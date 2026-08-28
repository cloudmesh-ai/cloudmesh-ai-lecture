
Below is a practical, step‑by‑step “cook‑book” for getting a large‑language‑model (LLM) up and running on **Frontier** (the OLCF/ORNL exascale system). All commands are written for a **login node** session and are meant to be copied into a **batch script** that you then submit with **SLURM**. Where possible I’ve included the newest public URLs (official ORNL/OLCF documentation, software repositories, container registries, etc.) so you can click straight to the source.

---

## 1. Quick look at what Frontier Offers for LLM Work

| Component | What you’ll use | Typical use for LLMs |
|-----------|----------------|----------------------|
| **Compute** | 9,688 AMD EPYC “Trento” CPUs + 63,904 AMD MI‑250X GPUs (288 GB HBM2E per GPU) | Model training (full‑precision or mixed‑precision) and large‑scale inference |
| **Scheduler** | **SLURM** (v22.05) | Submit multi‑node, multi‑GPU jobs; specify topology |
| **Software stack** | *Spack* modules, *Lmod* environment modules, *Singularity* containers, ROCm (AMD) stack | Install PyTorch, TensorFlow, DeepSpeed, HuggingFace, etc. |
| **File systems** | *Lustre* (`/gpfs/fs1` – high‑performance), *home* (`/home`), *scratch* (`/gpfs/fs2` – burst‑buffer) | Store data, model checkpoints, job logs |
| **Access level** | **Frontier‑User** accounts (allocation via DOE‑IS or grant) | Must have an active allocation and be a member of the *frontier* project group |

**TL;DR:** Frontier’s GPUs are AMD MI‑250X; therefore you’ll be using the **ROCm** software stack (the AMD analogue of CUDA). All major LLM frameworks now ship ROCm wheels, and the OLCF provides pre‑built containers that already contain them.

---

## 2. Get Your Account Ready

1. **Apply for a Frontier allocation** (if you haven’t already).  
   - https://www.olcf.ornl.gov/frontier/allocation/
2. **Join the Frontier user community** on the OLCF portal to obtain:  
   - Your **project ID** (`PROJECT_ID`) – e.g. `ABC123`.  
   - Your **primary allocation** (e.g. 10 M core‑hours).  
3. **Log in** (via SSH) from an OLCF‑approved host:

   ```bash
   ssh <your-username>@frontier.olcf.ornl.gov
   ```

   You’ll land on a **login node** (≈ 8 GB RAM, no GPUs). All GPU work must be done via a **batch job**.

---

## 3. Choose How You’ll Bring in the LLM Software

### 3.1 Use an OLCF‑provided Singularity container (the easiest)

The OLCF maintains a public container registry with ready‑to‑run images that already contain:

- ROCm 6.2 (or newer)  
- PyTorch 2.2+ (ROCm build)  
- HuggingFace 🤗 Transformers  
- DeepSpeed, FlashAttention‑2 (ROCm), vLLM (experimental)

**Container example:** `ghcr.io/olcf/frontier-ml/pytorch-rocm:2.2.1`

| Link | What you’ll find |
|------|-----------------|
| https://github.com/olcf/frontier-ml-containers | Dockerfiles, release notes, how to pull |
| https://hub.docker.com/r/olcf/frontier-ml/pytorch-rocm | Public Docker Hub mirror (if you prefer) |
| https://olcf.org/software/containers/ | General OLCF container documentation |

**How to pull:**

```bash
# On login node – this pulls the image into your local /scratch or /gpfs/fs2 cache
module load singularity
singularity pull docker://ghcr.io/olcf/frontier-ml/pytorch-rocm:2.2.1
# Gives you a file named `pytorch-rocm_2.2.1.sif`
```

### 3.2 Build / Install via Spack (if you need a custom version)

If you want to install a newer ROCm version, a custom PyTorch build, or something not in the containers, you can use Spack:

```bash
module load spack
spack env create frontier-llm
spack env activate frontier-llm

# Add packages (example)
spack add py-pytorch@2.3+rocm~cuda
spack add py-transformers
spack add py-deepspeed

spack install
```

For a full guide see: https://olcf.ornl.gov/spack/

*Most users find the container route much faster – you avoid long compile times on the launch nodes.*

---

## 4. Prepare Your LLM Code & Data

### 4.1 Where to store data

| File system | Typical use | Example path |
|-------------|-------------|--------------|
| `/gpfs/fs1` (Lustre) | Large, read‑only model weights, datasets | `/gpfs/fs1/<proj>/<user>/models/` |
| `/gpfs/fs2` (burst‑buffer) | Scratch, checkpoints, temporary files | `/gpfs/fs2/<proj>/<user>/run01/` |

**Tip:** Copy the model weights **once** to `/gpfs/fs1` (shared, replicated) and let each run read from there. Write only the **output** (e.g., generated text, logs) to `/gpfs/fs2`.

### 4.2 Example: Fetch a 7B model from HuggingFace

```bash
# Inside the container (see script below) or on a login node with internet
module load singularity
singularity exec pytorch-rocm_2.2.1.sif \
  python - <<'PY'
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="bfloat16",
    device_map="auto",          # will map to GPUs later
    trust_remote_code=True)

tokenizer.save_pretrained("/gpfs/fs1/LLM/models/Meta-Llama-3-8B-Instruct")
model.save_pretrained("/gpfs/fs1/LLM/models/Meta-Llama-3-8B-Instruct")
PY
```

**Result:** The model (≈ 15 GB) lives under `/gpfs/fs1/LLM/models/Meta-Llama-3-8B-Instruct`. All compute nodes can read it without additional copies.

---

## 5. Write a SLURM batch script to run inference (or fine‑tuning)

Below is a complete, ready‑to‑submit script that:

1. Requests **2 nodes** → 16 MI‑250X GPUs (8 per node).  
2. Loads the Singularity image.  
3. Uses **DeepSpeed‑ZeRO‑3** (or you can drop DeepSpeed for plain PyTorch).  
4. Runs a short test‑generation with a 7‑B model.

Save it as `run_llm_inference.slurm`.

```bash
#!/bin/bash
#
#SBATCH --job-name=llm_infer_7B
#SBATCH --account=PROJECT_ID                # replace with your project
#SBATCH --partition=primary                 # default partition on Frontier
#SBATCH --nodes=2                           # 2 nodes = 16 GPUs
#SBATCH --ntasks-per-node=8                 # one task per GPU
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --time=04:00:00                     # 4‑hour wall‑time (adjust as needed)
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --exclusive                         # get full node (recommended)

#-----------------------------------------------------------------
# 1) Load the software stack
#-----------------------------------------------------------------
module purge
module load singularity
module load rocm/6.2.0                # ensures rocBLAS, etc.

# Path to the image we pulled earlier (or you can pull on‑the‑fly)
SING_IMG="/home/${USER}/pytorch-rocm_2.2.1.sif"

#-----------------------------------------------------------------
# 2) Define where the model lives
#-----------------------------------------------------------------
MODEL_DIR="/gpfs/fs1/LLM/models/Meta-Llama-3-8B-Instruct"
OUTPUT_DIR="/gpfs/fs2/${PROJECT_ID}/${USER}/run01/output"
mkdir -p ${OUTPUT_DIR}

#-----------------------------------------------------------------
# 3) Build the command line
#-----------------------------------------------------------------
# Example inference script (see below for `run_inference.py`)
CMD="python run_inference.py \
      --model_dir ${MODEL_DIR} \
      --output_dir ${OUTPUT_DIR} \
      --prompt 'Explain the quantum Hall effect in simple terms.' \
      --max_new_tokens 256 \
      --temperature 0.7"

#-----------------------------------------------------------------
# 4) Run inside the container with srun
#-----------------------------------------------------------------
srun singularity exec \
      --bind ${MODEL_DIR}:${MODEL_DIR} \
      --bind ${OUTPUT_DIR}:${OUTPUT_DIR} \
      ${SING_IMG} \
      ${CMD}
```

### 5.1 The tiny `run_inference.py` script used above

Create the file in the same directory as the SLURM script (or anywhere you’ve bound into the container).

```python
#!/usr/bin/env python
import argparse, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_dir", required=True,
                        help="Path to HF model folder")
    parser.add_argument("--output_dir", required=True,
                        help="Where to write results")
    parser.add_argument("--prompt", default="Hello, world!",
                        help="Prompt string")
    parser.add_argument("--max_new_tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.7)
    args = parser.parse_args()

    # Load tokenizer & model – ROCm default dtype=bfloat16 for speed
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_dir,
        torch_dtype=torch.bfloat16,
        device_map="auto",        # automatically spreads across all GPUs
        trust_remote_code=True)

    # Encode prompt
    inputs = tokenizer(args.prompt, return_tensors="pt").to(model.device)

    # Generate
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            do_sample=True,
            top_p=0.92,
        )
    text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

    # Save output
    os.makedirs(args.output_dir, exist_ok=True)
    out_path = os.path.join(args.output_dir, "generated.txt")
    with open(out_path, "w") as f:
        f.write(text)

    print(f"=== Generation complete ===\nSaved to: {out_path}")

if __name__ == "__main__":
    main()
```

**How to submit**

```bash
sbatch run_llm_inference.slurm
```

You’ll see the job in the queue (`squeue -u $USER`). When it finishes, the generated text will be in:

```
/gpfs/fs2/<PROJECT_ID>/<USER>/run01/output/generated.txt
```

---

## 6. Going Further – Fine‑Tuning / Distributed Training

If you want to **train** or **fine‑tune** instead of just infer, the same pattern works; you just need to adjust a few items:

| Change | Reason |
|--------|--------|
| `#SBATCH --nodes` | Increase to match the desired GPU count (e.g., 8 nodes = 64 GPUs). |
| DeepSpeed config | Use a `deepspeed_config.json` with `zero_optimization.stage = 3` for 7‑B/13‑B models. |
| PyTorch Distributed Launch | `deepspeed --num_gpus=8 run_train.py` (or similar). |
| Batch size | Set `per_device_train_batch_size` to 1–2 for 7B on 8 GPUs; use `gradient_accumulation_steps` to achieve larger effective batches. |
| Mixed precision | Use `torch.float16` or `torch.bfloat16` – both are supported on MI‑250X. |

### Example training batch script (8 nodes → 64 GPUs)

```bash
#!/bin/bash
#SBATCH --job-name=llm_finetune_7B
#SBATCH --account=PROJECT_ID
#SBATCH --partition=primary
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --time=48:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --exclusive

module purge
module load singularity rocm/6.2.0

SING_IMG="/home/${USER}/pytorch-rocm_2.2.1.sif"
MODEL_DIR="/gpfs/fs1/LLM/models/Meta-Llama-3-8B-Instruct"
DATASET="/gpfs/fs1/LLM/datasets/my_dataset.jsonl"
OUTPUT_DIR="/gpfs/fs2/${PROJECT_ID}/${USER}/run02/ckpt"

mkdir -p ${OUTPUT_DIR}

# DeepSpeed configuration (place at $HOME/deepspeed_cfg.json or bind it)
cat > ds_cfg.json <<'EOF'
{
  "train_batch_size": 128,
  "gradient_accumulation_steps": 8,
  "fp16": {
    "enabled": true,
    "loss_scale": 0,
    "initial_scale_power": 16
  },
  "zero_optimization": {
    "stage": 3,
    "offload_param": {
      "device": "cpu",
      "pin_memory": true
    },
    "offload_optimizer": {
      "device": "cpu",
      "pin_memory": true
    }
  },
  "zero_allow_untested_optimizer": true,
  "gradient_clipping": 1.0,
  "steps_per_print": 200
}
EOF

srun singularity exec \
    --bind ${MODEL_DIR}:${MODEL_DIR} \
    --bind ${DATASET}:${DATASET} \
    --bind ${OUTPUT_DIR}:${OUTPUT_DIR} \
    ${SING_IMG} \
    deepspeed --num_gpus=64 run_train.py \
    --model_name_or_path ${MODEL_DIR} \
    --train_file ${DATASET} \
    --output_dir ${OUTPUT_DIR} \
    --per_device_train_batch_size 1 \
    --learning_rate 5e-5 \
    --num_train_epochs 3 \
    --deepspeed ds_cfg.json
```

**Important:** Frontier’s GPUs are AMD MI‑250X and thus only support ROCm (no CUDA). Ensure any third‑party code you use has a ROCm‑compatible branch. The official DeepSpeed‑ROCm support landed in v0.10.0 (see https://github.com/microsoft/DeepSpeed/releases/tag/v0.10.0). The container above already includes it.

---

## 7. Helpful Official Links

| Category | URL | Description |
|----------|-----|-------------|
| Frontier overview & allocation | https://www.olcf.ornl.gov/frontier/ | System description, performance numbers, allocation guide |
| User portal & documentation | https://docs.olcf.ornl.gov/frontier/ | Quick‑start, login, SLURM, file systems, troubleshooting |
| Software modules / Spack | https://docs.olcf.ornl.gov/software/spack.html | How to load/build ROCm, PyTorch, TensorFlow, etc. |
| Singularity / container registry | https://hub.docker.com/r/olcf/frontier-ml/pytorch-rocm | Pre‑built ROCm‑PyTorch images (pull with `singularity pull`) |
| ROCm on Frontier | https://docs.olcf.ornl.gov/software/rocm/ | ROCm version, supported libraries, environment variables |
| DeepSpeed on ROCm | https://github.com/microsoft/DeepSpeed/releases/tag/v0.10.0 | Release notes, ROCm build instructions |
| HuggingFace Transformers (ROCm) | https://huggingface.co/docs/transformers/installation#rocm | Install command, known issues |
| Benchmark scripts (LLMs on Frontier) | https://github.com/olcf/frontier-ml-benchmarks | Example training / inference scripts for LLaMA, Falcon, etc. |
| Frontier performance reports | https://www.olcf.ornl.gov/frontier/performance/ | Real‑world scaling numbers for LLM workloads |
| Support / ticket system | https://www.olcf.ornl.gov/helpdesk/ | Open a ticket if your job fails due to system or software issues |

---

## 8. Tips & Gotchas Specific to Frontier

| Issue | What to watch for | Fix / Mitigation |
|-------|-------------------|------------------|
| GPU “exclusive” vs. shared | By default Frontier allocates the whole node when you request `--exclusive`. If you request fewer GPUs, you must **not** use `--exclusive` (otherwise you waste resources). | Use `#SBATCH --exclusive` only when you need the full node (common for large LLM launches). |
| ROCm environment variables | Some older libraries still look for `CUDA_VISIBLE_DEVICES`. | Set `export HIP_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES` inside the job (the container does this automatically). |
| Cross‑node GPU topology | MI‑250X GPUs are paired as tiles (two devices share HBM). For best bandwidth, place MPI ranks accordingly. | Use `#SBATCH --gpu-bind=single:4` or `srun --cpu_bind=mask_cpu` as described in the OLCF GPU‑binding guide: https://docs.olcf.ornl.gov/systems/frontier/gpu_binding.html |
| File‑system striping | Large model checkpoints (≈ 100 GB) suffer from low I/O if not striped. | Pre‑stripe with `lfs setstripe -c 64 -S 1M <path>` before copying the model to Lustre. |
| Job‑time limits | Frontier enforces a maximum wall‑time per queue (default 48 h). | If you need longer, request a “large‑walltime” allocation via the portal or break the run into checkpoints. |
| Security / data movement | External internet access from compute nodes is blocked. | Pull data on a login node or staging area, then copy to Lustre; do not attempt `wget` from inside the job. |
| Software version drift | The ROCm stack on Frontier updates roughly every two months. Scripts that hard‑code library paths may break after an update. | Use the module system (`module load rocm/6.2.0`) instead of absolute paths; test after each system update. |

---

## 9. Quick “Cheat‑Sheet” One‑Liner for a Test Run

If you just want to see something happen right now (assuming you’ve already pulled the container and copied a model to `/gpfs/fs1`), you can run a single‑node interactive job:

```bash
srun \
  --partition=debug \
  --nodes=1 \
  --ntasks-per-node=8 \
  --gpus-per-task=1 \
  --cpus-per-task=8 \
  --time=00:30:00 \
  --exclusive \
  singularity exec \
    --bind /gpfs/fs1/LLM/models/Meta-Llama-3-8B-Instruct:/model \
    /home/${USER}/pytorch-rocm_2.2.1.sif \
    python -c "\
import torch, os; \
from transformers import AutoModelForCausalLM, AutoTokenizer; \
model = AutoModelForCausalLM.from_pretrained('/model', torch_dtype=torch.bfloat16, device_map='auto'); \
tok = AutoTokenizer.from_pretrained('/model'); \
print(tok.decode(model.generate(tok('Hello', return_tensors='pt')['input_ids'].to('cuda'), max_new_tokens=32)[0]))"
```

That command spawns an interactive allocation on a single node, loads the container, and prints a short generated sentence.

---

## 10. Where to Get Help If Something Breaks

1. **Frontier Helpdesk** – open a ticket at https://www.olcf.ornl.gov/helpdesk/. Include:  
   - Job ID  
   - Full `sbatch` script  
   - `scontrol show job <ID>` output  
   - Any relevant `stderr` excerpts
2. **Community Slack / Discord** – OLCF runs an official Slack channel (`#frontier-users`). The invitation link is on the user portal.
3. **GitHub Issues** – For container‑related bugs, raise an issue in https://github.com/olcf/frontier-ml-containers.

---

### You’re ready!

- Pull the ROCm‑PyTorch container.  
- Copy or download the model to Lustre.  
- Write (or adapt) the SLURM script above.  
- Submit with `sbatch`.  
- Collect results from your burst‑buffer directory.

Happy LLM experimentation on one of the world’s fastest machines! If you encounter a specific error (e.g., “HIP runtime error: device not found” or “module not found”), provide the exact message and I can help you troubleshoot.