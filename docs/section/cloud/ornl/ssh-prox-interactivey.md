# Gemma‑4 inference server on a Frontier compute (worker) node

Goal: **Access the server from your laptop** through an SSH tunnel that “proxies” the connection via the Frontier login node (and, if needed, a bastion node).  

The workflow is:

```
Laptop  <--SSH tunnel-->  frontier-login.olcf.ornl.gov  <--SSH tunnel-->  Worker‑node (allocated by SLURM)
```

The tunnel forwards a local port on your laptop (e.g., 8000) to the port on the worker node where the Gemma‑4 server is listening (e.g., 8000).  
All traffic is encrypted and passes through the OLCF network; you never expose a port on the public Internet.

---

## Prerequisites  

| Item | What you need | How to verify |
|------|---------------|---------------|
| **Frontier allocation** | Active project allocation (`PROJECT_ID`) and a Frontier user account. | `scontrol show partition` returns a list; `sacctmgr show assoc format=user,project,account` shows your allocation. |
| **SSH key** | Public key (`~/.ssh/id_rsa.pub` or `~/.ssh/id_ed25519.pub`) registered in the OLCF user portal. | Try `ssh -vv frontier.olcf.ornl.gov` – you should see “Offering public key …”. |
| **Singularity container** | `pytorch-rocm_2.2.1.sif` (or newer) with Gemma‑4 inside. | `singularity exec pytorch-rocm_2.2.1.sif python -c "import transformers"` should exit cleanly. |
| **Model files** | Gemma‑4 model cached under `/gpfs/fs1/LLM/models/gemma-4b-it`. | `ls /gpfs/fs1/LLM/models/gemma-4b-it` shows `config.json`, `pytorch_model‑*.bin`, etc. |
| **Python 3.10+** on the worker node (provided by the container). | Implicit with the container. | — |
| **Local tools** | `ssh`, `scp` (or `rsync`), optional `jq` for pretty‑printing JSON responses. | `ssh -V` and `jq --version`. |

---

## 1. Reserve an interactive worker node  

We need a node that stays alive while we develop locally. Use `salloc` (interactive SLURM allocation) and request a **single node** (or more, if you want multi‑node serving).

```bash
# Request 1 node with 8 MI‑250X GPUs, 2 h wall‑time
salloc \
  --partition=debug \          # or “primary” for longer jobs
  --nodes=1 \
  --ntasks-per-node=8 \
  --gpus-per-task=1 \
  --cpus-per-task=8 \
  --time=02:00:00 \
  --account=PROJECT_ID \
  --exclusive
```

If the allocation is granted, you will be dropped into a **Shell on the login node** *inside* the allocation. Any `srun` you launch from here will execute on the **worker node**.

---

## 2. Start the Gemma‑4 inference server on the worker node  

We will use the **vLLM** server (ROCm build) because it provides an OpenAI‑compatible REST API that is easy to call from a laptop.

### 2.1 Load modules & define paths  

```bash
module purge
module load singularity rocm/6.2.0   # provides ROCm libraries
SING_IMG="${HOME}/pytorch-rocm_2.2.1.sif"

MODEL_DIR="/gpfs/fs1/LLM/models/gemma-4b-it"
```

### 2.2 Launch the server with `srun`  

`vllm` must be started **inside the allocation** (so it runs on the worker node). The command below binds the model directory, runs the container, and starts the server listening on **all interfaces** (`0.0.0.0`) inside the node on port **8000**.

```bash
# Run on the *login node* of the allocation – srun will execute on the worker node
srun \
  --cpu-bind=mask_cpu \
  --gpu-bind=single:8 \
  singularity exec \
    --bind ${MODEL_DIR}:${MODEL_DIR} \
    ${SING_IMG} \
    vllm.entrypoints.openai.api_server \
      --model ${MODEL_DIR} \
      --dtype bfloat16 \
      --port 8000 \
      --tensor-parallel-size 8 \
      --disable-log-requests
```

**What happens**

| Piece | Explanation |
|-------|-------------|
| `srun` | Starts one process per GPU (8 tasks). The container runs **once per task**, but `vllm` internally does the necessary tensor‑parallel sharding. |
| `--cpu-bind=mask_cpu` / `--gpu-bind=single:8` | Guarantees each task gets a dedicated GPU and a set of CPU cores, matching the recommended Frontier GPU binding guide. |
| `--port 8000` | The server listens on port 8000 **inside the worker node**. Because we will forward this port later, the server must bind to `0.0.0.0` (default for vLLM). |
| `--tensor-parallel-size 8` | Distributes the Gemma‑4 model across the 8 GPUs on the node. |

You should see logs similar to:

```
INFO:     Using tensor parallel size: 8
INFO:     Started server process [pid=...] listening on http://0.0.0.0:8000
```

Leave this terminal **open**; the server will keep running until the allocation expires or you `Ctrl‑C` it.

---

## 3. Create an SSH tunnel from your laptop to the worker node  

Because the worker node has **no direct inbound network access**, we forward the port through the login node (the “jump host”).

### 3.1 Identify the worker node’s hostname  

While the server is running, run (in a separate shell *on the login node* of the allocation):

```bash
# This prints the allocated node name, e.g. nid001234
scontrol show hostnames $SLURM_JOB_NODELIST
```

Save the result; we’ll call it `WORKER_NODE`.

### 3.2 Build a two‑hop tunnel  

**Option A – Single‑hop (most common)**  
If your allocation was granted **on a single node**, the login node you’re currently on is the same host that will forward traffic to the worker node. You can tunnel directly:

```bash
# On your laptop
ssh -L 8000:$(scontrol show hostnames $SLURM_JOB_NODELIST):8000 \
    -J frontier-login.olcf.ornl.gov \
    your_user@frontier.olcf.ornl.gov \
    -N
```

Explanation:

| Flag | Meaning |
|------|----------|
| `-L 8000:WORKER:8000` | Forward local port 8000 → port 8000 on the worker node. |
| `-J frontier-login.olcf.ornl.gov` | “Jump” through the login node (acts as a bastion). |
| `-N` | Do not execute a remote command; just keep the tunnel open. |
| `your_user@frontier.olcf.ornl.gov` | Your Frontier account. |

**Option B – Explicit two‑hop** (if you need to SSH to a *separate* login node first):

```bash
# 1. Open a tunnel from laptop -> login node
ssh -L 9000:$(scontrol show hostnames $SLURM_JOB_NODELIST):8000 \
    your_user@frontier-login.olcf.ornl.gov -N &
#   ^ local port 9000 will forward to the worker node’s port 8000

# 2. (Optional) keep the above process in background; you can now use
#    localhost:9000 on your laptop as the endpoint.
```

*Note*: Replace `9000` with any free local port if 8000 is already in use on your laptop.

### 3.3 Verify the tunnel  

On your laptop (while the tunnel is active):

```bash
curl -s http://127.0.0.1:8000/v1/models  # vLLM endpoint for model list
```

You should receive a JSON response like:

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

If you get `Connection refused` or a timeout, double‑check:

1. The tunnel command is still running.  
2. The worker node name (`$SLURM_JOB_NODELIST`) is correct.  
3. The server on the worker node is still alive (`squeue` still shows your allocation).  

---

## 4. Call Gemma‑4 from your laptop  

Now you can treat the forwarded port as a local OpenAI‑compatible API. Example using `curl`:

```bash
curl -s http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model":"gemma-4b-it",
        "prompt":"Explain why the sky appears blue in simple terms.",
        "max_tokens":150,
        "temperature":0.7,
        "stream":false
      }' | jq .
```

Or, from Python (requires `openai` package, version ≥ 1.0):

```python
import openai

client = openai.OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="irrelevant"  # vLLM does not check the key
)

resp = client.completions.create(
    model="gemma-4b-it",
    prompt="Explain why the sky appears blue in simple terms.",
    max_tokens=150,
    temperature=0.7,
)

print(resp.choices[0].text)
```

All traffic travels through the encrypted SSH tunnel, keeping the model and data inside the OLCF network.

---

## 5. Clean‑up  

When you are finished:

1. **Stop the server** – go to the terminal on the login node where `srun` launched vLLM and press `Ctrl‑C`.  
2. **Cancel the allocation** (if it hasn’t timed out automatically):  

   ```bash
   scancel $SLURM_JOB_ID
   ```

3. **Terminate the tunnel** – simply kill the `ssh` process on your laptop (e.g., `pkill -f "ssh -L 8000"` or close the terminal window).  

---

## 6. Full example – copy‑paste script workflow  

Below is a **single‑file script** you can paste into a terminal on your laptop.  
It automates the allocation, starts the server, opens the tunnel, and leaves you with a ready‑to‑use endpoint. Adjust the variables (`PROJECT_ID`, `LOCAL_PORT`, `REMOTE_PORT`) as needed.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# USER‑CONFIGURABLE
# -------------------------------------------------
PROJECT_ID="ABC123"          # <-- replace with your Frontier project
LOCAL_PORT=8000             # port on your laptop
REMOTE_PORT=8000            # port the vLLM server will listen on
TIME_LIMIT="02:00:00"       # wall‑time for the interactive allocation
CONTAINER="${HOME}/pytorch-rocm_2.2.1.sif"
MODEL_DIR="/gpfs/fs1/LLM/models/gemma-4b-it"
# -------------------------------------------------
# 1) Request interactive allocation (SLURM)
# -------------------------------------------------
ALLOC=$(salloc \
  --partition=debug \
  --nodes=1 \
  --ntasks-per-node=8 \
  --gpus-per-task=1 \
  --cpus-per-task=8 \
  --time=${TIME_LIMIT} \
  --account=${PROJECT_ID} \
  --exclusive \
  --no-shell)   # we will attach later

# Grab the allocation ID (SLURM_JOB_ID) from environment of salloc
JOB_ID=$SLURM_JOB_ID
echo "Allocation ${JOB_ID} granted."

# -------------------------------------------------
# 2) Get the worker node name
# -------------------------------------------------
WORKER=$(scontrol show hostnames $SLURM_JOB_NODELIST)
echo "Worker node: $WORKER"

# -------------------------------------------------
# 3) Launch vLLM on the worker via srun (runs in background)
# -------------------------------------------------
srun \
  --cpu-bind=mask_cpu \
  --gpu-bind=single:8 \
  singularity exec \
    --bind ${MODEL_DIR}:${MODEL_DIR} \
    ${CONTAINER} \
    vllm.entrypoints.openai.api_server \
      --model ${MODEL_DIR} \
      --dtype bfloat16 \
      --port ${REMOTE_PORT} \
      --tensor-parallel-size 8 \
      --disable-log-requests \
  &   # background it; output will appear on your terminal

# -------------------------------------------------
# 4) Create SSH tunnel (login node -> worker)
# -------------------------------------------------
# Note: the login node you are currently on is the same as the one
# you used for the allocation, so we can forward directly.
ssh -L ${LOCAL_PORT}:${WORKER}:${REMOTE_PORT} \
    -J frontier-login.olcf.ornl.gov \
    ${USER}@frontier.olcf.ornl.gov \
    -N &
TUNNEL_PID=$!
echo "Tunnel PID $TUNNEL_PID listening on localhost:${LOCAL_PORT}"

# -------------------------------------------------
# 5) Wait for the server to become reachable
# -------------------------------------------------
until curl -s http://127.0.0.1:${LOCAL_PORT}/v1/models >/dev/null; do
  echo "Waiting for vLLM to start..."
  sleep 3
done
echo "Gemma‑4 is ready! Call it with:"
echo "  curl http://127.0.0.1:${LOCAL_PORT}/v1/completions ..."
echo "When done, press ENTER to clean up."
read   # pause

# -------------------------------------------------
# 6) Clean up
# -------------------------------------------------
kill $TUNNEL_PID
scancel $JOB_ID
echo "All done."
```

Run the script with `bash launch_gemma4.sh`. It will:

1. Allocate a node.  
2. Start the Gemma‑4 server.  
3. Open a tunnel so you can call `http://127.0.0.1:8000` on your laptop.  
4. Clean everything up when you press **Enter**.

---

## 7. Common pitfalls & troubleshooting  

| Symptom | Likely cause | Fix |
|---------|---------------|-----|
| `curl: (7) Failed to connect to 127.0.0.1 port 8000` after starting the tunnel | Tunnel process died or never started. | Verify the `ssh -L … -N` command is still running (`ps -ef | grep ssh`). Re‑run the tunnel command. |
| Server logs show “Address already in use” | Another process is already listening on port 8000 on the worker node (e.g., a previous run). | Cancel the old allocation or change `REMOTE_PORT` to an unused value. |
| `torch.cuda.is_available()` returns **False** inside the container | ROCm module not loaded or container launched without GPU access. | Load `rocm/6.2.0` **before** `singularity exec`. Ensure `srun` requests one GPU per task (`--gpus-per-task=1`). |
| Model loading hangs for > 5 min | Model files not reachable (wrong path or Lustre striping). | Confirm `MODEL_DIR` exists on the worker: `ls $MODEL_DIR`. If you copied the model to a different location, update the bind path. |
| `vllm` crashes with “RuntimeError: Unexpected MPS device” | Accidentally used a CUDA‑only build of vLLM. | Use the OLCF‑provided image (`pytorch-rocm_2.2.1.sif`) which contains the ROCm vLLM binary. |
| Tunnel works but responses are **empty** | The request payload is malformed (e.g., missing `model` name). | Use the exact payload from the “Verify the tunnel” step; note that the model name is the folder name (`gemma-4b-it`). |
| Allocation expires while you’re still using the server | Wall‑time too short. | Request a longer `--time` or submit a batch script that runs the server for the required duration instead of an interactive allocation. |

---

## 8. Security note  

- **Never open the worker‑node port to the public Internet.** The tunnel ensures the port is only reachable from your laptop via authenticated SSH.  
- The OLCF login node enforces two‑factor authentication for SSH; keep your private key protected with a passphrase.  
- The vLLM server does **not** enforce API‑key authentication. If you need stricter access control, wrap the endpoint in a lightweight reverse‑proxy (e.g., `nginx` with basic auth) on the login node, then forward the tunnel to that proxy instead.

---

## 9. References  

| Resource | URL |
|----------|-----|
| Frontier allocation guide | <https://www.olcf.ornl.gov/frontier/allocation/> |
| OLCF SSH access & bastion host documentation | <https://docs.olcf.ornl.gov/frontier/access.html#ssh-access> |
| vLLM ROCm build (included in the OLCF container) | <https://github.com/vllm-project/vllm/tree/rocm> |
| Gemma‑4 model on HuggingFace | <https://huggingface.co/google/gemma-4b-it> |
| SLURM `salloc` / `srun` manual | <https://slurm.schedmd.com/salloc.html> |
| GPU binding guide for Frontier | <https://docs.olcf.ornl.gov/systems/frontier/gpu_binding.html> |
| OpenAI‑compatible API spec (used by vLLM) | <https://platform.openai.com/docs/api-reference/completions/create> |

---  

You are now ready to run Gemma‑4 on a Frontier worker node and interact with it from your laptop via a secure SSH tunnel. Happy inference!