# Running LLMs on Linux CPU: A Complete Guide

This tutorial provides a comprehensive guide to running Large Language Models (LLMs) locally on Linux using only the CPU. We explore three primary paths—from "plug-and-play" tools to raw C++ binaries and flexible Python implementations—culminating in a live demo that runs on any typical laptop.

!!! note "Learning Objectives"

    By the end of this guide, you will be able to:
    - **Evaluate and choose** between different CPU-based LLM runners (Ollama, llama.cpp, Transformers).
    - **Deploy a quantised model** to fit within limited system RAM.
    - **Execute inference** via CLI, REST API, or Python script.
    - **Analyze and optimize** CPU performance using thread limiting and 4-bit quantisation.
    - **Troubleshoot common CPU-inference errors** such as Out-of-Memory (OOM) and segmentation faults.

---

## Quick Start: Linux Step-by-Step Guide

If you are in a hurry, follow this high-level workflow. Detailed commands for each step are provided in the options below.

| Step | Action | Description | Reference |
| :--- | :--- | :--- | :--- |
| **1** | **Install Tool** | Choose a runner based on your needs (Ease of use vs. Control). | See Options A, B, C |
| **2** | **Fetch Model** | Pull or convert a model that fits in RAM ($\le$ 7B, preferably 4-bit). | See Options A, B, C |
| **3** | **Run Inference** | Interact with the model via CLI, REST, or Python. | See Options A, B, C |
| **4** | **Optimize** | Limit CPU threads and use quantisation for better stability. | Performance Tips |

---

## 1. Option A: Ollama (Plug-and-Play)

Ollama is the easiest way to get started. It bundles the model runner and a simple API into one package.

### Installation & Setup

```bash
# Install Ollama (works on Ubuntu/Debian, Fedora, and CentOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a 4-bit quantised 7B LLaMA-2 model (~6 GB RAM)
ollama pull llama2:7b-q4_0

# Or a lighter 1B model (~1 GB RAM) for slower CPUs
ollama pull tinyllama:1b-q4_0
```

### Running Inference

**Interactive Chat:**
```bash
ollama run llama2:7b-q4_0
```

**REST API Example:**
Any language can interact with Ollama via its HTTP API.
```bash
curl -X POST http://localhost:11434/api/chat \
     -H "Content-Type: application/json" \
     -d '{
           "model":"llama2:7b-q4_0",
           "messages":[{"role":"user","content":"What is the difference between RAM and VRAM?"}]
         }' | jq .
```

> **Performance Tip:** Limit the CPU threads to keep your desktop responsive:
> ```bash
> export OLLAMA_NUM_THREADS=4   # Add to ~/.bashrc or run before starting
> systemctl restart ollama.service
> ```

---

## 2. Option B: llama.cpp (Pure C++ Binary)

`llama.cpp` is the gold standard for CPU inference. It is a high-performance C++ implementation with minimal dependencies.

### Installation & Setup

```bash
# 1. Download the pre-built Linux binary
wget https://github.com/ggerganov/llama.cpp/releases/download/b1.7/llama.cpp-linux-x86_64.zip
unzip llama.cpp-linux-x86_64.zip
chmod +x llama-cli
```

### Model Conversion (GGML)

To use a Hugging Face model with `llama.cpp`, you must convert it to GGML format (typically 4-bit quantised) once.

```bash
# Example: TinyLlama-1.1B-Chat (~1 GB after q4_0)
git clone https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v0.1
cd TinyLlama-1.1B-Chat-v0.1

# Convert to GGML 4-bit
../llama-cli convert_hf_to_ggml.py --outtype q4_0 --outfile ../tinyllama-q4_0.ggmlv3.bin .
```

### Running Inference

```bash
../llama-cli -m tinyllama-q4_0.ggmlv3.bin \
             -p "Write a haiku about sunrise." \
             -n 48
```

`llama-cli` can be easily wrapped in a Python `subprocess` or a FastAPI wrapper for custom applications.

---

## 3. Option C: Python (Transformers + bitsandbytes)

Use this route if you need deep integration with the Hugging Face ecosystem or are building a complex AI pipeline.

### Installation

```bash
# Install CPU-only PyTorch
pip install torch==2.4.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install Transformers and quantisation libraries
pip install transformers bitsandbytes accelerate
```

### Loading a 4-bit Model

This example loads a Mistral-7B model using `bitsandbytes` for 4-bit quantisation to save RAM.

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, bitsandbytes as bnb

model_name = "mistralai/Mistral-7B-Instruct-v0.2"

# Configure 4-bit quantisation
quant_cfg = bnb.nn.Int8Params(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4"
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    quantization_config=quant_cfg,
    trust_remote_code=True
)

def generate(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    out = model.generate(**inputs,
                         max_new_tokens=max_new,
                         temperature=0.8,
                         do_sample=True)
    return tokenizer.decode(out[0], skip_special_tokens=True)

print(generate("Summarise the plot of *The Little Prince* in three sentences."))
```

> **Performance Tip:** Manually set the thread count to avoid CPU contention:
> ```python
> torch.set_num_threads(4)
> ```

---

## 4. Live Python Demo

<a name="demo"></a>

For those who want to see an LLM run immediately without downloading multi-gigabyte models, we use **DistilGPT-2**. It is a tiny model (124M parameters, ~0.5 GB RAM) that runs comfortably on any modern CPU.

### Demo Code

```python
# -------------------------------------------------
# Tiny CPU Demo: DistilGPT-2
# -------------------------------------------------
import time, os, platform, sys
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {platform.platform()}")
print(f"CPU count: {os.cpu_count()}")

model_name = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate(prompt: str, max_new: int = 80):
    inputs = tokenizer(prompt, return_tensors="pt")
    start = time.time()
    output = model.generate(**inputs,
                            max_new_tokens=max_new,
                            do_sample=True,
                            temperature=0.9)
    secs = time.time() - start
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    gen_tokens = output.shape[1] - inputs["input_ids"].shape[1]
    tps = gen_tokens / secs if secs > 0 else float("inf")
    return text, gen_tokens, secs, tps

prompt = "Write a short story about a robot that learns to paint."
generated, tokens, elapsed, tps = generate(prompt)

print("\n=== Prompt ===\n", prompt)
print("\n=== Generated text ===\n", generated)
print("\n=== Stats ===\n", f"Tokens generated : {tokens}")
print(f"Time elapsed      : {elapsed:.2f}s")
print(f"Tokens per second : {tps:.2f} tps")
```

### Expected Output (Example)

```text
Python: 3.12.7
Platform: Linux-5.15.0-1045-azure-x86_64-with-glibc2.35
CPU count: 12

=== Prompt ===
Write a short story about a robot that learns to paint.

=== Generated text ===
In a quiet workshop tucked away from the bustle of the city, a small robot named Arti was built by a curious inventor who loved both machinery and art...

=== Stats ===
Tokens generated : 84
Time elapsed      : 1.84s
Tokens per second : 45.65 tps
```

---

## 5. Performance Expectations

<a name="perf"></a>

Performance varies based on your CPU clock speed and available RAM. Below are typical metrics for a modern laptop CPU (e.g., Intel i7 / AMD Ryzen 7).

| Model (quant) | Approx. RAM | Tokens/s (tps) | Typical Latency (50 tokens) |
| :--- | :--- | :--- | :--- |
| **TinyLlama 1B (q4_0)** | ~1 GB | 30–40 tps | ~1.3s |
| **DistilGPT-2 (no quant)** | ~0.5 GB | ~45 tps | ~1.1s |
| **Mistral 7B (q4_0)** | ~6 GB | 5–10 tps | 5–10s |
| **Llama-2 7B (q4_0)** | ~6 GB | 8–12 tps | 4–6s |

*Note: For sub-second responses with 7B+ models, a dedicated GPU or a hosted inference service is required.*

---

## 6. Troubleshooting & Next Steps

<a name="next"></a>

| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| **`MemoryError` or OOM** | Model too large for RAM. | Use a 4-bit quantised version or a smaller model ($\le$ 7B). |
| **Very slow generation (< 2 tps)** | Running full-precision FP16 on CPU. | Switch to a quantised model or limit `torch.set_num_threads`. |
| **`ImportError: transformers`** | Missing dependencies. | Re-run the installation commands in Section 3. |
| **Ollama service unreachable** | Service not running or port 11434 blocked. | `systemctl start ollama.service`. |
| **`Segmentation fault` (llama-cli)** | CPU lacks AVX2/AVX512 support. | Build `llama.cpp` from source with `-mcpu=native`. |
| **Want to move to GPU?** | Hardware available but not used. | Install CUDA, use `device_map="auto"` in Transformers, or `GGML_CUDA=1` in llama.cpp. |

---

## Quick Start

- **Quickest Chat:** `curl ... | sh && ollama run llama2:7b-q4_0`
- **Embeddable/Lean:** `llama-cli` $\rightarrow$ Convert to GGML $\rightarrow$ Execute.
- **Developer Flexibility:** `torch` + `transformers` + `bitsandbytes` $\rightarrow$ `model.generate()`.

All methods run **entirely on the CPU**. Choose the one that best fits your development workflow!

---

## Appendix

### Assignments

!!! assignment "The Plug-and-Play Experience"
    **Task:** Install Ollama and run the `tinyllama` model.
    **Goal:** Verify that your Linux environment is correctly configured for LLM runners and that you can pull/execute a model via CLI.

!!! assignment "Binary Optimization"
    **Task:** Set up `llama.cpp` and run inference using a GGML quantised model.
    **Goal:** Understand the performance difference between a high-level wrapper (Ollama) and a raw C++ binary.

!!! assignment "Programmable Inference"
    **Task:** Write a custom Python script using the `transformers` library that takes a user prompt as input and prints both the generated text and the total execution time.
    **Goal:** Learn how to integrate LLM inference into a larger Python application.

!!! assignment "Performance Benchmarking"
    **Task:** Use `torch.set_num_threads()` to run the same prompt with 1, 2, 4, and 8 threads. Record the tokens per second (tps) for each.
    **Goal:** Analyze the relationship between CPU core allocation and inference throughput.
