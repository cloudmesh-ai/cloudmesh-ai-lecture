
## SSH Proxy via Batch Job

Running a Gemma‑4 (or any LLM) on a Frontier compute node from a batch job and exposing a local port on your laptop via an SSH tunnel.

The workflow is:

1. **Submit a SLURM batch script** that  
   * allocates a worker node,  
   * starts the LLM inference server (vLLM) on that node, and  
   * writes the node’s hostname to a small “heartbeat” file that the login node can read.  

2. **On your laptop** poll the batch system for the job’s node name, then open a two‑hop SSH tunnel  
   `laptop ←→ login‑node ←→ worker‑node`.  

3. Verify the server is up by querying the local forwarded port.  

All commands are written for a typical Frontier user (ROCm‑enabled `pytorch‑rocm` container).  Adjust paths, project IDs and ports to suit your own environment.

---  

## 1.  Batch script that launches the LLM and records the worker node name  

Save the following as **`run_gemma4_batch.slurm`** (you can rename it, just keep the `.slurm` suffix).

```bash
#!/bin/bash
#
#------------------- SLURM JOB SETTINGS -------------------
#SBATCH --job-name=gemma4_batch
#SBATCH --account=PROJECT_ID                # <‑‑ replace with your project
#SBATCH --partition=primary                 # or debug for short tests
#SBATCH --nodes=1                           # single worker node
#SBATCH --ntasks-per-node=8                 # one task per GPU
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00                     # wall‑time you need
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --exclusive                         # whole node for best bandwidth

#------------------- ENVIRONMENT -------------------------
module purge
module load singularity rocm/6.2.0
SING_IMG="${HOME}/pytorch-rocm_2.2.1.sif"    # path to the OLCF container
MODEL_DIR="/gpfs/fs1/LLM/models/gemma-4b-it"

# File that will be visible on the login node (shared Lustre)
HEARTBEAT="/gpfs/fs2/${PROJECT_ID}/${USER}/gemma4_node_${SLURM_JOB_ID}.txt"

#------------------- START SERVER ------------------------
# The server will listen on all interfaces (0.0.0.0) port $SERVER_PORT
SERVER_PORT=8000

# Record the node name *as soon as the allocation starts*.
# $SLURM_JOB_NODELIST expands to the allocated node list (a single name here).
echo "$(date)   node=$(scontrol show hostnames $SLURM_JOB_NODELIST)" > "$HEARTBEAT"

# Run vLLM under srun so that each task gets a GPU.
# vLLM internally handles tensor‑parallel sharding across the 8 GPUs.
srun \
  --cpu-bind=mask_cpu \
  --gpu-bind=single:8 \
  singularity exec \
    --bind ${MODEL_DIR}:${MODEL_DIR} \
    ${SING_IMG} \
    vllm.entrypoints.openai.api_server \
      --model ${MODEL_DIR} \
      --dtype bfloat16 \
      --port ${SERVER_PORT} \
      --tensor-parallel-size 8 \
      --disable-log-requests

# When the server exits (job ends or you cancel), clean up the heartbeat file.
rm -f "$HEARTBEAT"
```

### What the script does

| Step | Reason |
|------|--------|
| `#SBATCH …` block | Requests a **single** compute node with 8 MI‑250X GPUs. |
| `module load …` | Loads ROCm libraries required by the container. |
| `HEARTBEAT` file | Placed on the Lustre burst‑buffer (`/gpfs/fs2`). The login node (and you, from the laptop) can read the file to discover the node’s hostname. |
| `echo … > $HEARTBEAT` | Writes the node name *immediately* after the allocation starts. |
| `srun … vllm.entrypoints.openai.api_server` | Starts the Gemma‑4 inference server inside the container. The server binds to `0.0.0.0:8000` **on the worker node**. |
| `rm -f $HEARTBEAT` | Removes the heartbeat file when the job finishes, preventing stale data. |

Submit the job from the Frontier login node:

```bash
sbatch run_gemma4_batch.slurm
```

Take note of the **SLURM job id** that `sbatch` prints (e.g. `12345678`). You will need it for the next step.

---  

## 2.  Helper script on the laptop – discover the node and open the tunnel  

Create a small Bash helper on your laptop called **`ssh-gemma4-tunnel.sh`**.  It takes the SLURM job id as an argument, waits for the heartbeat file to appear, extracts the worker‑node name, and spawns an SSH tunnel that forwards the remote port (`8000`) to a local port of your choice.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# ssh-gemma4-tunnel.sh
# -------------------------------------------------
# Usage:  ./ssh-gemma4-tunnel.sh <SLURM_JOB_ID> [local_port]
# -------------------------------------------------

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <SLURM_JOB_ID> [local_port]"
  exit 1
fi

JOB_ID=$1
LOCAL_PORT=${2:-8000}          # default: forward to localhost:8000
REMOTE_PORT=8000               # port used inside the worker node
PROJECT_ID="PROJECT_ID"        # <‑‑ replace with your project id
USER_NAME="your_user"          # <‑‑ replace with your Frontier username

# Path where the batch script writes the heartbeat file (must match $HEARTBEAT above)
HEARTBEAT="/gpfs/fs2/${PROJECT_ID}/${USER_NAME}/gemma4_node_${JOB_ID}.txt"

# ----------------------------------------------------------------
# 1) Wait until the heartbeat file exists and contains a node name.
# ----------------------------------------------------------------
echo "Waiting for the batch job ($JOB_ID) to start..."
while true; do
  # Use ssh to cat the file on the login node.
  # The `-q` flag suppresses warnings if the file does not yet exist.
  NODE=$(ssh -q ${USER_NAME}@frontier.olcf.ornl.gov \
          "cat ${HEARTBEAT} 2>/dev/null || true")
  if [[ -n "$NODE" ]]; then
    # The file format is: "<date>   node=<hostname>"
    WORKER=$(echo "$NODE" | awk -F'node=' '{print $2}' | tr -d '[:space:]')
    if [[ -n "$WORKER" ]]; then
      echo "Found worker node: $WORKER"
      break
    fi
  fi
  sleep 3
done

# ----------------------------------------------------------------
# 2) Open the two‑hop SSH tunnel.
#    -J : jump through the Frontier login node (bastion)
#    -L : local_port:target_node:remote_port
# ----------------------------------------------------------------
echo "Opening SSH tunnel: localhost:${LOCAL_PORT} → ${WORKER}:${REMOTE_PORT}"
ssh -N -L ${LOCAL_PORT}:${WORKER}:${REMOTE_PORT} \
    -J frontier-login.olcf.ornl.gov \
    ${USER_NAME}@frontier.olcf.ornl.gov &
TUNNEL_PID=$!
echo "Tunnel PID: $TUNNEL_PID"
echo "Press ENTER to terminate the tunnel and exit."
read   # wait for user to press ENTER

# Clean up
kill $TUNNEL_PID 2>/dev/null || true
echo "Tunnel closed."
```

### How to use the helper

```bash
# 1) Submit the batch job (if you haven’t already)
sbatch run_gemma4_batch.slurm   # note the job id printed, e.g. 12345678

# 2) From your laptop, start the tunnel
./ssh-gemma4-tunnel.sh 12345678 8000   # 8000 is the local port you want
```

The script will:

1. **Poll** the heartbeat file on the Frontier login node until it appears.  
2. **Extract** the worker‑node hostname (`nidXXXXX`).  
3. **Create** a tunnel: `localhost:8000 → nidXXXXX:8000` via the login node (`frontier-login.olcf.ornl.gov`).  

The tunnel runs in the background; when you press **Enter** the script kills the SSH process and exits.

---  

## 3.  Verify that the LLM server is reachable  

While the tunnel is active, run any OpenAI‑compatible client against `http://127.0.0.1:8000`.  Example using `curl`:

```bash
curl -s http://127.0.0.1:8000/v1/models | jq .
```

Expected output (JSON) :

```json
{
  "data": [
    {
      "id": "gemma-4b-it",
      "object": "model"
    }
  ]
}
```

A quick completion request:

```bash
curl -s http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model":"gemma-4b-it",
        "prompt":"Explain why the sky appears blue in simple terms.",
        "max_tokens":150,
        "temperature":0.7
      }' | jq .
```

If you see a populated `choices[0].text` field, the server is up and the tunnel works.

---  

## 4.  Clean‑up  

When you are finished:

1. **Terminate the tunnel** – press **Enter** in the helper script (or `kill` the PID shown).  
2. **Cancel the SLURM job** (if it has not already finished):

   ```bash
   scancel 12345678
   ```

   The batch script’s `rm -f $HEARTBEAT` will delete the heartbeat file, so future runs will not pick up a stale node name.

---  

## 5.  Full picture – what happens behind the scenes  

```
Laptop (localport 8000)  <--SSH tunnel-->  frontier-login.olcf.ornl.gov
                               |
                               |--- SSH forward --->  nid0XXXXX (worker node) :8000
```

* The **batch script** runs entirely on the compute node; it cannot be accessed directly from outside the OLCF network.  
* The **heartbeat file** is the only piece of information the login node needs to tell the outside world which compute node is hosting the server.  
* The **two‑hop tunnel** (`ssh -J`) uses the login node as a jump host; the final destination (`nid0XXXXX`) is resolved by the login node’s internal DNS, which knows the compute‑node hostnames.  

---  

## 6.  Optional: Automated one‑liner (if you prefer a single command)  

If you want to avoid a separate helper script, you can combine the steps in a one‑liner on the laptop (replace placeholders accordingly):

```bash
JOBID=$(sbatch run_gemma4_batch.slurm | awk '{print $4}')   # capture job id
HEARTBEAT="/gpfs/fs2/PROJECT_ID/your_user/gemma4_node_${JOBID}.txt"

# Wait for the node name
while :; do
  NODE=$(ssh your_user@frontier.olcf.ornl.gov "cat ${HEARTBEAT}" 2>/dev/null || true)
  [[ $NODE =~ node=([a-z0-9]+) ]] && WORKER=${BASH_REMATCH[1]} && break
  sleep 3
done

# Open tunnel (background)
ssh -N -L 8000:${WORKER}:8000 -J frontier-login.olcf.ornl.gov \
    your_user@frontier.olcf.ornl.gov &
echo "Tunnel PID $!  →  http://127.0.0.1:8000"
```

Press `Ctrl‑C` (or `kill %1`) to stop the tunnel and the job will end automatically when the wall‑time expires or when you `scancel $JOBID`.

---  

## 7.  Things to watch out for  

| Issue | Symptom | Remedy |
|-------|---------|--------|
| Heartbeat file never appears | `ssh-gemma4-tunnel.sh` hangs forever | Verify the batch job actually started (`squeue -j <JOBID>`). If the job is still pending due to lack of resources, wait or request a different partition. |
| Tunnel fails with “Permission denied (publickey)” | SSH key not registered on OLCF portal | Add your public key (`~/.ssh/id_rsa.pub` or `id_ed25519.pub`) via the OLCF user portal, then reload your ssh‑agent (`ssh-add`). |
| `curl` returns 404 or empty JSON | vLLM server not bound to `0.0.0.0` or wrong model name | Ensure `vllm.entrypoints.openai.api_server` is started with `--port 8000` (default binds to all interfaces) and that `MODEL_DIR` points to the Gemma‑4 folder (`gemma-4b-it`). |
| Port conflict on the worker node | “Address already in use” in the batch log | Change `SERVER_PORT` (and consequently `REMOTE_PORT`) to an unused value (e.g., 8010). |
| Job expires while you are still testing | Tunnel disconnects, server stops | Request a longer `--time` in the batch script, or submit a *repeating* job (e.g., a `sbatch` that launches another `sbatch`). |

---  

## 8.  References  

| Topic | URL |
|-------|-----|
| Frontier allocation guide | <https://www.olcf.ornl.gov/frontier/allocation/> |
| SSH access & bastion host (Frontier) | <https://docs.olcf.ornl.gov/frontier/access.html#ssh-access> |
| SLURM `srun` and GPU binding on Frontier | <https://docs.olcf.ornl.gov/systems/frontier/gpu_binding.html> |
| vLLM ROCm build (included in OLCF container) | <https://github.com/vllm-project/vllm/tree/rocm> |
| Gemma‑4 model on HuggingFace | <https://huggingface.co/google/gemma-4b-it> |
| OpenAI‑compatible API (used by vLLM) | <https://platform.openai.com/docs/api-reference/completions/create> |

---  

**You now have a complete, reproducible recipe** for:

* launching a Gemma‑4 (or any other LLM) inside a Frontier batch job,  
* exposing the worker‑node hostname via a shared heartbeat file, and  
* creating a secure SSH tunnel from your laptop that lets you interact with the model as if it were running locally.  

