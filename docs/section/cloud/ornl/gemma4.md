
## Appendix B – Running **Gemma‑4** (the 4‑B‑parameter Gemma model) on Frontier 

we want the 31B
can we make it for both so we use an environment variable


The steps below extend the “cook‑book” from the main answer.  
They are written for the **same Singularity container** (`pytorch‑rocm:2.2.1`) that already contains ROCm‑enabled PyTorch, 🤗 Transformers, DeepSpeed, FlashAttention‑2 (ROCm) and vLLM.  If you prefer a different container, just replace the image name – the rest of the workflow stays identical.

---

### B‑1.  Locate a ROCm‑compatible Gemma‑4 build  

| Source | Direct link | Notes |
|--------|-------------|-------|
| 🤗 HuggingFace – `google/gemma-4b-it` (instruction‑tuned) | <https://huggingface.co/google/gemma-4b-it> | Model is provided in **PyTorch** format; the repo already ships a `config.json` that tells Transformers the architecture. |
| OLCF / Frontier‑ML container (pre‑installed) | The container already contains the **`transformers`** version that knows about Gemma, so you do **not** need to compile any custom ops. | |

> **Important:** Gemma‑4 is a **ROCm‑compatible** model because it uses only standard PyTorch ops.  No extra AMD extensions are required.

---

### B‑2.  Pull the model onto the Lustre file system  

Run **once** on a login node (or on a login‑node interactive session) to cache the weights in a location that all compute nodes can read:

```bash
# Load the same container we will use later
module load singularity
SING_IMG="${HOME}/pytorch-rocm_2.2.1.sif"   # adjust path if needed

# Destination on Lustre (read‑only, shared)
MODEL_ROOT="/gpfs/fs1/LLM/models"
MODEL_DIR="${MODEL_ROOT}/gemma-4b-it"

# If the model already exists, skip the download
if [ ! -d "${MODEL_DIR}" ]; then
    singularity exec \
        --bind ${MODEL_ROOT}:${MODEL_ROOT} \
        ${SING_IMG} \
        python - <<'PY'
import os
from transformers import AutoTokenizer, AutoModelForCausalLM

model_name = "google/gemma-4b-it"
dst = os.getenv("MODEL_DIR")
os.makedirs(dst, exist_ok=True)

print(f"Downloading {model_name} → {dst}")
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model    = AutoModelForCausalLM.from_pretrained(
             model_name,
             torch_dtype="bfloat16",      # fits comfortably in MI‑250X HBM2E
             device_map="cpu",            # keep on CPU while downloading
             trust_remote_code=True)

tokenizer.save_pretrained(dst)
model.save_pretrained(dst)
PY
else
    echo "Gemma‑4 already present at ${MODEL_DIR}"
fi
```

After this finishes you will have a directory layout similar to:

```
/gpfs/fs1/LLM/models/gemma-4b-it/
├─ config.json
├─ generation_config.json
├─ tokenizer_config.json
├─ special_tokens_map.json
├─ tokenizer.model
├─ pytorch_model-00001-of-00002.bin
├─ pytorch_model-00002-of-00002.bin
└─ … (other HF metadata)
```

---

### B‑3.  Minimal inference script for Gemma‑4  

Create (or edit) a Python file called **`gemma_inference.py`** in the same folder as your SLURM script:

```python
#!/usr/bin/env python
"""
Simple inference demo for Gemma‑4 (4‑B) using the ROCm‑enabled
transformers library inside the Frontier container.
"""

import argparse, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model_dir", required=True,
                   help="Path on Lustre where Gemma‑4 was cached")
    p.add_argument("--output_dir", required=True,
                   help="Where generated text & logs will be written")
    p.add_argument("--prompt", default="Write a short poem about sunrise.",
                   help="Prompt string")
    p.add_argument("--max_new_tokens", type=int, default=256)
    p.add_argument("--temperature", type=float, default=0.8)
    args = p.parse_args()

    # -------------------------------------------------
    # Load model & tokenizer – let transformers spread
    # the weights across *all* available GPUs automatically.
    # -------------------------------------------------
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_dir,
        use_fast=True,
        trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        args.model_dir,
        torch_dtype=torch.bfloat16,      # best perf on MI‑250X
        device_map="auto",               # auto‑shard across GPUs
        trust_remote_code=True)

    # -------------------------------------------------
    # Encode prompt, generate, decode
    # -------------------------------------------------
    inputs = tokenizer(args.prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            do_sample=True,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id,
        )
    text = tokenizer.decode(generated_ids[0],
                            skip_special_tokens=True,
                            clean_up_tokenization_spaces=True)

    # -------------------------------------------------
    # Write output
    # -------------------------------------------------
    os.makedirs(args.output_dir, exist_ok=True)
    out_file = os.path.join(args.output_dir, "gemma4_output.txt")
    with open(out_file, "w") as f:
        f.write(text)

    print(f"\n=== Generated text ===\n{text}\n")
    print(f"[+] Saved to {out_file}")

if __name__ == "__main__":
    main()
```

*Make the script executable*:

```bash
chmod +x gemma_inference.py
```

---

### B‑4.  SLURM batch job for **Gemma‑4 inference** (2 nodes = 16 GPUs)

Save the following as **`run_gemma4.slurm`**.  It mirrors the generic script from the main answer, but points at the Gemma‑4 model and the new Python script.

```bash
#!/bin/bash
#
#SBATCH --job-name=gemma4_infer
#SBATCH --account=PROJECT_ID                     # <-- replace with your project
#SBATCH --partition=primary
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --exclusive

# -------------------------------------------------
# 1. Environment
# -------------------------------------------------
module purge
module load singularity rocm/6.2.0

# Path to the pre‑pulled container
SING_IMG="${HOME}/pytorch-rocm_2.2.1.sif"

# -------------------------------------------------
# 2. Directories
# -------------------------------------------------
MODEL_DIR="/gpfs/fs1/LLM/models/gemma-4b-it"
OUTPUT_DIR="/gpfs/fs2/${PROJECT_ID}/${USER}/gemma4/run01"

mkdir -p "${OUTPUT_DIR}"

# -------------------------------------------------
# 3. Command to run inside the container
# -------------------------------------------------
CMD="python gemma_inference.py \
      --model_dir ${MODEL_DIR} \
      --output_dir ${OUTPUT_DIR} \
      --prompt 'Explain why the sky appears blue in simple terms.' \
      --max_new_tokens 200 \
      --temperature 0.7"

# -------------------------------------------------
# 4. Launch with srun + singularity
# -------------------------------------------------
srun singularity exec \
     --bind ${MODEL_DIR}:${MODEL_DIR} \
     --bind ${OUTPUT_DIR}:${OUTPUT_DIR} \
     ${SING_IMG} \
     ${CMD}
```

**Submit the job**

```bash
sbatch run_gemma4.slurm
```

When the job finishes, the generated answer will be in:

```
/gpfs/fs2/<PROJECT_ID>/<USER>/gemma4/run01/gemma4_output.txt
```

---

### B‑5.  Optional: Faster generation with **vLLM (ROCm)**  

If you need **throughput‑oriented** inference (e.g., serving many requests or generating long passages), the container also ships a ROCm‑compatible build of **vLLM**.  The workflow is almost identical; you only replace the Python script with a tiny wrapper that launches `vllm.entrypoints.openai.api_server` and then `curl` the local endpoint.

#### Quick vLLM launch (single‑node, 8 GPUs)

```bash
#!/bin/bash
#SBATCH --job-name=gemma4_vllm
#SBATCH --account=PROJECT_ID
#SBATCH --partition=primary
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --gpus-per-task=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --output=%x-%j.out
#SBATCH --error=%x-%j.err
#SBATCH --exclusive

module purge
module load singularity rocm/6.2.0
SING_IMG="${HOME}/pytorch-rocm_2.2.1.sif"

MODEL_DIR="/gpfs/fs1/LLM/models/gemma-4b-it"
OUTPUT_DIR="/gpfs/fs2/${PROJECT_ID}/${USER}/gemma4/vllm"

mkdir -p "${OUTPUT_DIR}"

# vLLM command – note the `--tensor-parallel-size=8` to spread across the 8 GPUs
VLLM_CMD="vllm.entrypoints.openai.api_server \
          --model ${MODEL_DIR} \
          --tensor-parallel-size 8 \
          --port 8000 \
          --dtype bfloat16 \
          --disable-log-requests"

srun singularity exec \
     --bind ${MODEL_DIR}:${MODEL_DIR} \
     --bind ${OUTPUT_DIR}:${OUTPUT_DIR} \
     ${SING_IMG} \
     ${VLLM_CMD}
```

After the job starts, you can **curl** the server from the compute node (or from a login node via `ssh -L` port‑forwarding) to generate text:

```bash
# From a login node (after allocating the job, e.g. via salloc)
ssh -L 8000:$(hostname):8000 <your_user>@frontier.olcf.ornl.gov   # port‑forward
curl http://127.0.0.1:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model":"gemma-4b-it",
        "prompt":"Summarize the plot of Shakespeare''s Hamlet in 3 sentences.",
        "max_tokens":150,
        "temperature":0.7
      }' | jq .
```

vLLM automatically handles **tensor‑parallel sharding**, so you get the same latency as a single‑GPU model while using the full 8‑GPU node.

---

### B‑6.  Performance tips for Gemma‑4 on Frontier  

| Goal | Recommended setting | Why |
|------|---------------------|-----|
| **Maximum throughput** | Use **vLLM** with `--tensor-parallel-size=8` (or 16 if you span two nodes) | vLLM implements optimized kernel fusion and a custom request queue. |
| **Lowest latency for short prompts** | Keep **`max_new_tokens ≤ 128`** and enable **FlashAttention‑2** (`--flash-attn`) – already baked into the container. |
| **Fit larger context (≥ 4096 tokens)** | Switch to **`torch_dtype=torch.float16`** (instead of `bfloat16`) – it uses ~20 % less memory on MI‑250X. |
| **Avoid I/O stalls** | **Striped** the model directory on Lustre: `lfs setstripe -c 32 -S 1M /gpfs/fs1/LLM/models/gemma-4b-it` (run once before the first download). |
| **Checkpoint‑driven fine‑tuning** | Use **DeepSpeed ZeRO‑3** with the same `ds_cfg.json` shown in the main answer; set `train_batch_size` to 64‑128 per node for a 4 B model. |
| **Mixed‑precision training** | Add `--bf16` flag to `deepspeed run_train.py` – ROCm 6.2 has full bfloat16 support on MI‑250X. |

---

### B‑7.  Common error‑messages & fixes  

| Symptom | Typical root cause | Fix |
|---------|--------------------|-----|
| `RuntimeError: ROCm error: invalid device ordinal` | The job did not actually allocate GPUs (e.g., forgot `--gpus-per-task=1`). | Verify `scontrol show job $SLURM_JOB_ID` shows `NumNodes`, `NumGPUs`. |
| `ImportError: cannot import name 'flash_attn'` | The container image is older than v2.1 of FlashAttention‑ROCm. | Pull the latest container: `singularity pull docker://ghcr.io/olcf/frontier-ml/pytorch-rocm:2.3.0` (or newer). |
| `torch.cuda.is_available() returns False` | ROCm environment not loaded (missing `module load rocm`). | Ensure the `rocm` module is loaded **before** `singularity exec`. |
| `OSError: [Errno 28] No space left on device` | Writing checkpoints to `/gpfs/fs2` while the allocation’s quota is exhausted. | Clean old checkpoint directories or request a larger quota from OLCF. |
| `PermissionError: [Errno 13] Permission denied` | Trying to write to `/gpfs/fs1` (read‑only for users). | Write all runtime output to `/gpfs/fs2` (burst‑buffer) instead. |
| `Segmentation fault` during generation (large `max_new_tokens`) | The model exceeds HBM2E capacity (e.g., trying to run 27B on a single GPU). | Reduce `max_new_tokens` or run with **tensor‑parallel** across more GPUs; for >7 B you must spread the model. |

If you encounter an error not on this list, capture:

```bash
scontrol show job $SLURM_JOB_ID
cat *.out *.err
```

and open a ticket on the OLCF Helpdesk (see Appendix A).

---

### B‑8.  One‑liner quick test (single node, 8 GPUs, no batch script)

For a *very fast sanity check* you can use `salloc` to get an interactive allocation and run the inference directly:

```bash
# Request an interactive 8‑GPU allocation (debug partition, 30 min)
salloc --partition=debug --nodes=1 --ntasks-per-node=8 \
       --gpus-per-task=1 --cpus-per-task=8 --time=00:30:00 --exclusive

# Inside the allocation:
module load singularity rocm/6.2.0
singularity exec \
   --bind /gpfs/fs1/LLM/models/gemma-4b-it:/model \
   ${HOME}/pytorch-rocm_2.2.1.sif \
   python - <<'PY'
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
model_dir = "/model"

tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
mdl = AutoModelForCausalLM.from_pretrained(
        model_dir,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True)

prompt = "What are the health benefits of drinking green tea?"
inp = tok(prompt, return_tensors="pt").to(mdl.device)
out = mdl.generate(**inp, max_new_tokens=120, temperature=0.8)
print(tok.decode(out[0], skip_special_tokens=True))
PY
```

If you see a coherent answer printed, the entire stack (ROCm, container, Gemma‑4 model, multi‑GPU sharding) is working correctly.

---

## Run Gemma‑4 on Frontier in 5 Commands  

```bash
# 1. Pull container (once)
module load singularity
singularity pull docker://ghcr.io/olcf/frontier-ml/pytorch-rocm:2.2.1

# 2. Download the model to Lustre (once)
singularity exec pytorch-rocm_2.2.1.sif \
   python - <<'PY'
from transformers import AutoTokenizer, AutoModelForCausalLM
model = "google/gemma-4b-it"
tok   = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
mdl   = AutoModelForCausalLM.from_pretrained(
          model,
          torch_dtype="bfloat16",
          device_map="cpu",
          trust_remote_code=True)
tok.save_pretrained("/gpfs/fs1/LLM/models/gemma-4b-it")
mdl.save_pretrained("/gpfs/fs1/LLM/models/gemma-4b-it")
PY

# 3. Create `gemma_inference.py` (see script above)

# 4. Submit the SLURM script (`run_gemma4.slurm`) that binds the model and output dirs.

# 5. Retrieve result:
cat /gpfs/fs2/<PROJECT_ID>/<USER>/gemma4/run01/gemma4_output.txt
```

That’s it – you now have a reproducible, scalable workflow for **Gemma‑4** on the OLCF **Frontier** system.  Happy language‑modeling!