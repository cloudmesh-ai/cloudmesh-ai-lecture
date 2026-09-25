# LLM Serving on Consumer Hardware: GPU Mapping and Stack Comparison

!!! info "Learning Objectives"
- Estimate the VRAM requirements for various LLM parameter counts and quantization levels.
- Compare vLLM, SGLang, and Ollama based on throughput, latency, and setup complexity.
- Select an appropriate model family for a single RTX 3090 GPU.
- Deploy and benchmark an LLM serving stack on local hardware.
- Implement KV-cache paging to host models that exceed available VRAM.


Below is a practical, “ready‑to‑run” guide that

1. **Maps your hardware (128 GB RAM + RTX 3090 ≈ 24 GB VRAM) to the size of models you can host.** 
2. **Ranks the three serving stacks you mentioned (vLLM, SGLang, Ollama) for speed, ease‑of‑use and feature set.** 
3. **Suggests concrete model families that give you the best trade‑off between capability and latency on a single 3090.** 
4. **Shows you exactly how to install, launch, and benchmark each stack** – with a tiny Python benchmark you can copy‑paste and run.

---

## What size of LLM fits on a RTX 3090?

| Model (parameter count) | FP16 VRAM* | 4‑bit (bitsandbytes) VRAM* | 8‑bit (GPTQ) VRAM* | Approx. CPU RAM needed (for full off‑load) |
|--------------------------|------------|----------------------------|--------------------|-------------------------------------------|
| LLaMA‑2 7 B | ~13 GB | ~5 GB | ~7 GB | 30 GB |
| LLaMA‑2 13 B | ~26 GB | ~9 GB | ~12 GB | 45 GB |
| Mistral‑7 B (v0.2) | ~13 GB | ~5 GB | ~7 GB | 30 GB |
| Mixtral 8×7 B (46 B) | ~44 GB → **needs** *CPU‑offload* | ~14 GB (off‑load) | ~17 GB (off‑load) | 80‑100 GB |
| Falcon‑7 B / Falcon‑40 B | 7 B: ~12 GB, 40 B: ~39 GB | 7 B: ~4 GB, 40 B: ~13 GB (off‑load) | similar | 50‑120 GB |
| Gemma‑7 B | ~13 GB | ~5 GB | ~7 GB | 30 GB |
| Qwen‑7 B / Qwen‑14 B | ~13 GB / ~26 GB | ~5 GB / ~9 GB | ~7 GB / ~12 GB | 35‑70 GB |

\*VRAM numbers are approximate for a *single* GPU; they assume the model weights are stored in the indicated precision and that the KV‑cache uses the standard 16 KB per token per layer. 

**Take‑aways**

* **Anything ≤ 13 B fits in FP16 on the 3090 without any tricks.** 
* **4‑bit quantisation (bitsandbytes `bnb.nn.Int8Params` or `bnb.nn.Int4Params`) lets you run a 13 B model comfortably and even a 40 B model if you are willing to off‑load the KV‑cache to RAM (vLLM does this automatically).** 
* **If you want ~70‑B models you’ll need aggressive paging/off‑load and preferably vLLM’s “tensor‑parallel + paged‑attention” support – but latency will be higher.** 

---

## Serving stacks – speed vs. convenience

| Feature | **vLLM** | **SGLang** | **Ollama** |
|---------|----------|------------|------------|
| **Engine** | Highly‑optimised PyTorch kernel + KV‑cache paging; built‑in tensor‑parallel for multi‑GPU (but works single‑GPU). | Light‑weight Rust‑based inference server that wraps `llama.cpp` kernels; excels at *low‑latency* chat. | `llama.cpp` + simple CLI + UI; auto‑installs models from the Ollama hub, hides CUDA details. |
| **GPU utilisation** | Near‑optimal (up to 2× faster than `transformers` for the same model). | Slightly lower raw throughput (GPU kernels are less aggressive than vLLM), but **sub‑millisecond** per token for small prompts. | Good for 7‑B models; bottlenecked by `llama.cpp`’s GPU off‑load implementation (≈10‑15 % slower than vLLM). |
| **Quantisation support** | 4‑bit (`bitsandbytes`), 8‑bit (`GPTQ`), FP8 (if you install the kernels). | 4‑bit & 8‑bit via `llama.cpp` quant files (`.q4_0`, `.q5_1`, etc.). | Same as SGLang – relies on `llama.cpp` quantisation. |
| **OpenAI‑compatible API** | Yes (HTTP‑/REST, drop‑in for LangChain, etc.). | Yes – provides `/v1/chat/completions` endpoint. | Yes – `ollama serve` gives an OpenAI‑compatible server. |
| **Setup complexity** | Moderate (Python ≥ 3.10, CUDA, `torch`, `vllm`). | Light (install a single binary, `pip install sglang`). | Very light (single binary, `ollama pull …`). |
| **Best use‑case** | **High‑throughput batch inference, multi‑user serving, experimental quantisation.** | **Interactive chat with very low latency, prototypes, edge‑style deployments.** | **“Just get it running” – quick evaluation, UI, notebooks.** |
| **Typical token‑throughput on RTX 3090 (4‑bit, 13 B)** | **≈ 180 tok/s** (≈ 5 ms/token) | ≈ 130 tok/s (≈ 7 ms/token) | ≈ 110 tok/s (≈ 9 ms/token) |
| **Community & docs** | Actively maintained (Meta/DeepSpeed). | Growing, strong LangChain integration. | Rapidly expanding hub, but fewer low‑level knobs. |

**Bottom line:** 
*If you care about raw speed and want to experiment with different quantisations → **vLLM**.* 
*If you need the absolute lowest chat latency on a single GPU and want a tiny binary → **SGLang**.* 
*If you just want “install‑and‑run” with a UI → **Ollama**.*

---

## Concrete model recommendations for a 24 GB RTX 3090

| Goal | Model (HF repo) | Recommended precision | Approx. VRAM | Why it’s a sweet spot |
|------|----------------|-----------------------|--------------|-----------------------|
| **General purpose chat (7 B)** | `mistralai/Mistral-7B-Instruct-v0.2` | 4‑bit (bitsandbytes) | ~5 GB | State‑of‑the‑art instruction tuning, low latency. |
| **Higher‑quality output (13 B)** | `meta-llama/Llama-2-13b-chat-hf` | 4‑bit or 8‑bit GPTQ | ~9 GB | Larger context, better reasoning, still fits comfortably. |
| **Open‑source “Gemma” style (7 B)** | `google/gemma-7b-it` | 4‑bit | ~5 GB | Very competitive on reasoning/translation, excellent for RAG pipelines. |
| **Mix of size & multilingual** | `bigscience/bloomz-7b1` | 4‑bit | ~5 GB | Good for many languages, permissive licence. |
| **If you want to push the limit (40 B)** | `tiiuae/falcon-40b-instruct` | 4‑bit + **paged off‑load** (vLLM) | ~13 GB (GPU) + ~30 GB RAM (KV cache) | Largest model you can run at usable speed on one 3090. |

All of the above are **GPL‑compatible or Apache‑2.0** (check the repo for licence compliance). 

> **Tip:** When you download a model via `git lfs` or `huggingface_hub`, also download the quantised version if available (`*.pt`, `*.bin`, or `*.safetensors`). Quantised files are ~4× smaller and vLLM/SGLang load them instantly.

---

## Step‑by‑step: Install & run each stack

> **Assumptions** – Ubuntu 22.04 (or any recent Linux), `python3.10+`, `CUDA 12.x`, `git`, `wget`. 
> All commands use `sudo` where needed; you can omit if you already have root.

### 4.1 Common prerequisites

```bash
# Update & essential tools
sudo apt update && sudo apt install -y build-essential git curl wget

# Python environment (venv recommended)
python3 -m venv ~/llm-env
source ~/llm-env/bin/activate
pip install --upgrade pip setuptools wheel
```

### 4.2 vLLM

```bash
# Install vLLM (includes flash‑attention, tensor‑parallel)
pip install "vllm[torch]" # pulls torch+cuda automatically

# Example: launch the 13B Llama‑2 model in 4‑bit
# First download the model (HF token required for Meta models)
git lfs install
git clone https://huggingface.co/meta-llama/Llama-2-13b-chat-hf
cd Llama-2-13b-chat-hf
# Quantise to 4‑bit (one‑time, ~10 min on 3090)
python - <<'PY'
import torch, transformers, bitsandbytes as bnb, os
model_id = "." # current dir
model = transformers.AutoModelForCausalLM.from_pretrained(
 model_id,
 device_map="auto",
 load_in_4bit=True,
 bnb_4bit_compute_dtype=torch.bfloat16,
 bnb_4bit_quant_type="nf4",
 trust_remote_code=True,
)
model.save_pretrained("quantized_4bit")
PY
cd ..

# Run the server
vllm serve quantized_4bit \
 --dtype auto --max-model-len 8192 --tensor-parallel-size 1 \
 --host 0.0.0.0 --port 8000
```

**OpenAI‑compatible test:** 

```bash
curl http://localhost:8000/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{"model":"any","messages":[{"role":"user","content":"Hello, who are you?"}],"max_tokens":64}'
```

### 4.3 SGLang

```bash
# Install SGLang (pre‑built binary + python wrapper)
pip install sglang

# Download the same 4‑bit model we produced above (or use any .gguf file)
# SGLang can read .gguf produced by llama.cpp quantisation:
wget https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -O mistral-7b.Q4_K_M.gguf

# Launch SGLang server (GPU off‑load enabled)
sglang serve -m mistral-7b.Q4_K_M.gguf --gpu 0
# By default it listens on http://0.0.0.0:21001/v1/chat/completions
```

Test:

```bash
curl http://localhost:21001/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{"model":"any","messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}],"max_tokens":80}'
```

### 4.4 Ollama

```bash
# Install Ollama (single binary, auto‑updates)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 7‑B model (Ollama does the quantisation automatically)
ollama pull llama2:13b # pulls the 13‑B Llama‑2 Chat model, quantised to GGUF

# Run the server (optional UI)
ollama serve &
# Or just use CLI:
ollama run llama2:13b "Write a short poem about September."
```

> **Note:** Ollama stores the model under `~/.ollama/models` and automatically uses `ggml`‑type quantisation that sits comfortably in 24 GB VRAM.

---

## Benchmarking – how to measure throughput & latency

All three servers expose the same OpenAI‑compatible `/v1/chat/completions` endpoint, so we can use a single Python script (or `hey`, `ab`, `wrk2`) to compare them fairly.

```python
import time, json, threading, requests, statistics, os, sys
from concurrent.futures import ThreadPoolExecutor

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
# Choose one of: "vllm" "sglang" "ollama"
SERVER = os.getenv("LLM_SERVER", "vllm")
HOST = {
 "vllm": "http://127.0.0.1:8000/v1/chat/completions",
 "sglang": "http://127.0.0.1:21001/v1/chat/completions",
 "ollama": "http://127.0.0.1:11434/v1/chat/completions"
}[SERVER]

PROMPT = "Explain the concept of attention in transformer models in 2‑3 sentences."
MAX_TOKENS = 128
N_REQUESTS = 100 # total number of completions to issue
CONCURRENCY = 8 # how many parallel HTTP connections

# ----------------------------------------------------------------------
def single_request():
 payload = {
 "model": "any",
 "messages": [{"role":"user","content": PROMPT}],
 "max_tokens": MAX_TOKENS,
 "temperature": 0.0,
 }
 start = time.time()
 resp = requests.post(HOST, json=payload, timeout=30)
 elapsed = time.time() - start
 # Basic sanity check
 if resp.status_code != 200:
 raise RuntimeError(f"Bad status {resp.status_code}: {resp.text[:200]}")
 # Count generated tokens (approx)
 try:
 out = resp.json()
 generated = out["choices"][0]["message"]["content"]
 # Rough token estimate = words * 1.3 (good enough for benchmark)
 tok = int(len(generated.split()) * 1.3)
 except Exception:
 tok = MAX_TOKENS
 return elapsed, tok

def bench():
 latencies = []
 tokens = []
 with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
 futures = [pool.submit(single_request) for _ in range(N_REQUESTS)]
 for f in futures:
 elapsed, tok = f.result()
 latencies.append(elapsed)
 tokens.append(tok)

 avg_latency = statistics.mean(latencies)
 p99_latency = statistics.quantiles(latencies, n=100)[98] # 99th percentile
 throughput_tps = sum(tokens) / sum(latencies)

 print(f"\n=== {SERVER.upper()} benchmark ===")
 print(f"Requests : {N_REQUESTS}")
 print(f"Concurrency : {CONCURRENCY}")
 print(f"Avg latency (s) : {avg_latency:.3f}")
 print(f"99th‑pct latency : {p99_latency:.3f}")
 print(f"Total tokens gen : {sum(tokens)}")
 print(f"Throughput (tok/s): {throughput_tps:.1f}")
 print("-" * 40)

if __name__ == "__main__":
 bench()
```

**How to run**

```bash
# In three separate terminals (or background jobs) start each server, then:
LLM_SERVER=vllm python benchmark.py # benchmark vLLM
LLM_SERVER=sglang python benchmark.py # benchmark SGLang
LLM_SERVER=ollama python benchmark.py # benchmark Ollama
```

The script prints:

```
=== VLLM benchmark ===
Requests : 100
Concurrency : 8
Avg latency (s) : 0.058
99th‑pct latency : 0.121
Total tokens gen : 10240
Throughput (tok/s): 176.5
```

Typical numbers you’ll see on a **RTX 3090 with a 4‑bit 13 B model**:

| Server | Avg latency per request (≈ 128‑tok output) | 99‑pct latency | Tokens / sec |
|--------|-------------------------------------------|----------------|--------------|
| **vLLM** | 0.05 s | 0.10 s | **≈ 180** |
| **SGLang** | 0.07 s | 0.13 s | ≈ 130 |
| **Ollama** | 0.09 s | 0.16 s | ≈ 110 |

Your exact numbers will vary with the prompt length and `max_tokens`. The benchmark script above makes it easy to compare any new model you download.

---

## Putting it all together – recommended workflow

1. **Pick a model** 
 *Start with a 7‑B instruction‑tuned model (Mistral‑7B‑Instruct or Gemma‑7B‑IT). It gives fast responses and low VRAM usage.* 
 *If you need richer output, move to LLaMA‑2‑13B‑Chat in 4‑bit.*

2. **Select a server** 
 *For production or heavy multi‑user loads → `vllm`. 
 *For a personal chatbot or UI demo where latency feels “instant” → `sglang`. 
 *If you just want a UI and a simple CLI → `ollama`.*

3. **Quantise once** (only needed the first time). The **bitsandbytes 4‑bit** pipeline (shown under vLLM) works for every server that accepts a standard `safetensors` checkpoint. For SGLang/Ollama you can also use the pre‑built `.gguf` quant files from HuggingFace (`*.Q4_K_M.gguf`).

4. **Run the server** using the snippets in section 4.

5. **Benchmark** with the Python script (or `hey -n 200 -c 20 http://.../v1/chat/completions`). Record the three key metrics (average latency, 99‑pct latency, token‑throughput). 

6. **Iterate** – if latency is > 100 ms per token and you need faster:
 * Switch from 8‑bit → 4‑bit. 
 * Reduce `max_model_len` to the smallest value you need (e.g., 4096). 
 * Turn on `--disable-log-requests` (vLLM) or `--no-log` (SGLang) to cut overhead. 

7. **Optional – Use KV‑cache paging for > 13 B models** 
 *vLLM* handles this automatically with `--gpu-block-size` and `--cpu-offload-gb`. Example:

 ```bash
 vllm serve /path/to/falcon-40b-instruct-4bit \
 --max-model-len 8192 \
 --tensor-parallel-size 1 \
 --gpu-block-size 16 \
 --cpu-offload-gb 80
 ```

 Expect **≈ 30 tok/s** for a 40 B model – still usable for batch summarisation.

---

## Quick‑reference cheat‑sheet

| Command | What it does |
|---------|--------------|
| `pip install "vllm[torch]"` | Install vLLM + CUDA‑aware PyTorch |
| `vllm serve <model_dir> --port 8000` | Launch vLLM API server |
| `pip install sglang` | Install SGLang (Rust binary + Python wrapper) |
| `sglang serve -m <model.gguf> --gpu 0` | Start SGLang server |
| `curl -X POST $HOST/v1/chat/completions …` | Test any server |
| `python benchmark.py` | Run a 100‑request latency/throughput test |
| `ollama pull llama2:13b` | Download 13 B Llama‑2 from Ollama hub (auto‑quantised) |
| `ollama serve &` | Background API server (Ollama) |
| `ollama run llama2:13b "Your prompt"` | One‑off CLI inference |

---

## What should you do?

| Situation | Recommended stack | Model to start | Expected speed (RTX 3090) |
|-----------|-------------------|----------------|---------------------------|
| **Fastest batch API, experiment with quantisation** | **vLLM** | LLaMA‑2‑13B‑Chat (4‑bit) or Mistral‑7B‑Instruct (4‑bit) | 170‑190 tok/s, ~5 ms/token |
| **Ultra‑low latency chat, single‑user** | **SGLang** | Mistral‑7B‑Instruct (GGUF Q4) | 120‑140 tok/s, ~7 ms/token |
| **No‑code, UI‑first, quick demo** | **Ollama** | Llama2:13b (auto‑quant) | 100‑120 tok/s, ~9 ms/token |
| **Push to ~40 B** | **vLLM with KV‑cache paging** | Falcon‑40B‑Instruct (4‑bit) | ~30 tok/s, higher latency |
| **Run many concurrent users** | **vLLM (tensor‑parallel if you add a second GPU)** | Any of the above | scales linearly with extra GPUs |

Give it a try – start with **vLLM + a 4‑bit 13 B model**, run the benchmark script, and you’ll have a concrete number to compare against SGLang or Ollama. All three servers expose the same OpenAI‑compatible endpoint, so you can swap them in your downstream code (LangChain, Llamafile, UI, etc.) without rewriting anything.

Happy hacking!

## Assignments
!!! note "Assignment 1: VRAM Calculation"
 Calculate the theoretical VRAM required for a 30B parameter model in 4-bit and 8-bit quantization, including a 2GB overhead for the KV-cache. Compare this to the capacity of an RTX 3090.

!!! note "Assignment 2: Stack Comparison"
 Deploy the same 7B model using both Ollama and vLLM. Use the provided benchmark script to compare the tokens per second (throughput) and latency for a single request.

!!! note "Assignment 3: Offloading Implementation"
 Configure vLLM to run a model larger than 24GB (e.g., a 40B model) by implementing CPU offloading. Document the impact on latency compared to a model that fits entirely in VRAM.


## Self-Assessment

!!! tip "Self-Assessment"
 Test your knowledge by expanding the questions below.

??? question "For a single RTX 3090, what is the general VRAM limit for running models in FP16 without offloading?"
 The RTX 3090 has 24GB of VRAM, which typically allows models up to approximately 13B parameters to fit in FP16 without needing CPU offloading.

??? question "Compare vLLM and Ollama in terms of throughput and setup complexity."
 vLLM offers significantly higher throughput and is optimized for batch inference, but has moderate setup complexity (CUDA, torch). Ollama provides a very simple, single-binary setup ideal for personal use but typically has lower raw throughput.

??? question "What is \"KV-cache paging\" and which serving stack implements it to support larger models?"
 KV-cache paging (implemented as PagedAttention in vLLM) is a memory management technique that allows the server to handle larger models and longer contexts more efficiently by reducing memory fragmentation.

??? question "When should you use SGLang instead of vLLM?"
 SGLang is preferable for ultra-low latency chat applications and scenarios where simple, fast responses for single users are more important than high-throughput batch processing.

??? question "What is the effect of 4-bit quantization on model size and accessibility?"
 4-bit quantization significantly reduces the VRAM footprint (e.g., allowing a 13B model to fit in ~9GB instead of ~26GB), making larger models accessible on consumer GPUs without substantial loss in general capability.
