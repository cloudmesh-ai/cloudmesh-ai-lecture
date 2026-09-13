# Running Large Language Models on CPU

!!! info "Learning Objectives"
    - Select an LLM based on available system RAM and quantization levels.
    - Deploy and manage models using Ollama for rapid prototyping.
    - Use `llama.cpp` for lightweight, embeddable CPU inference.
    - Implement programmatic LLM generation using Python's `transformers` library.
    - Optimize CPU inference performance via thread management and quantization.

Large Language Models (LLMs) are typically designed to run on powerful GPUs with high-bandwidth memory (VRAM). However, the high cost and availability of GPUs often make CPU-only execution a necessity for local development, edge computing, or resource-constrained environments. The primary challenge of CPU inference is the significant difference in memory bandwidth and compute throughput compared to GPUs.

To make LLMs viable on CPUs, two primary techniques are used: quantization and optimized inference engines. Quantization reduces the precision of model weights (e.g., from 16-bit floating point to 4-bit integers), which drastically lowers the RAM requirement and increases execution speed without a proportional loss in accuracy. By utilizing optimized engines like `llama.cpp` or `Ollama`, developers can run models with billions of parameters on standard consumer hardware.

## Model Selection and RAM Requirements

The feasibility of running an LLM on a CPU depends entirely on the model's parameter count and its quantization level. If a model exceeds the available system RAM, the operating system will use swap space on the disk, leading to a catastrophic drop in performance.

### RAM Estimation and Quantization

The following table illustrates the approximate RAM requirements for common model sizes in both full precision (FP16) and 4-bit quantization.

| Model Size | Approx. RAM (FP16) | Recommended Quant | Approx. RAM (4-bit) |
| :--- | :--- | :--- | :--- |
| TinyLlama (1.1B) | 2-3 GB | q4_0 | ~1 GB |
| Mistral (7B) | 14 GB | q4_0 | ~6 GB |
| Llama-2 (7B) | 14 GB | q4_0 | ~6 GB |
| DistilGPT-2 (124M) | 0.5 GB | N/A | ~0.5 GB |

### Selection Rule of Thumb

For a typical laptop or desktop with 8-16 GB of RAM, the recommended limit is models with 7 billion parameters or fewer, using 4-bit quantization. Models larger than 7B typically require 32 GB of RAM or more to avoid system instability and extreme latency.

## Rapid Deployment with Ollama

Ollama is a streamlined tool designed to simplify the deployment of LLMs on macOS, Linux, and Windows. It bundles the model weights, configuration, and a high-performance inference engine into a single service.

### Installation

Ollama can be installed using the following methods:

- **Linux and macOS**:
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```
- **Windows**: Download the installer from the official Ollama website.

### Model Management and Execution

Once installed, the `ollama` command-line tool is used to manage models.

```bash
# Pull a 7B LLaMA-2 model with 4-bit quantization
ollama pull llama2:7b-q4_0

# Pull a smaller 1B model for higher speed
ollama pull tinyllama:1b-q4_0

# Launch an interactive chat session
ollama run llama2:7b-q4_0
```

### Programmatic Access via REST API

Ollama runs as a background service that exposes a REST API, allowing other applications to generate text without managing the model weights manually.

```bash
curl -X POST http://localhost:11434/api/chat \
     -d '{"model":"llama2:7b-q4_0","messages":[{"role":"user","content":"Explain the difference between RAM and VRAM."}]}'
```

### Performance Tuning

To prevent the LLM from consuming all available CPU resources and making the host system unresponsive, you can limit the number of threads used by the inference engine:

```bash
export OLLAMA_NUM_THREADS=4
```

## High-Performance Inference with llama.cpp

For applications that require a lightweight, embeddable solution without a background service, `llama.cpp` is the industry standard. It is written in C++ and designed specifically for CPU inference.

### Architecture and GGUF Format

`llama.cpp` utilizes the GGUF (GPT-Generated Unified Format) file format, which stores both the model weights and the required metadata in a single binary. This allows for extremely fast loading and precise control over memory mapping.

### Running Inference

Once the `llama-cli` binary is obtained and a GGUF model is downloaded, inference can be started directly from the terminal:

```bash
./llama-cli -m tinyllama-q4_0.gguf -p "The capital of France is" -n 128
```

The `-m` flag specifies the model path, `-p` provides the prompt, and `-n` sets the number of tokens to generate.

## Programmatic Control with Python Transformers

For developers who need full control over the model's behavior or wish to integrate LLMs into a larger Python pipeline, the Hugging Face `transformers` library is the most flexible option.

### Installation

The following libraries are required for CPU-based generation:

```bash
pip install torch transformers
```

### Implementing a Generation Pipeline

The following script demonstrates how to load a small, CPU-compatible model and generate text.

```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import time

model_name = "distilgpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_text(prompt, max_new=80):
    inputs = tokenizer(prompt, return_tensors="pt")
    start_time = time.time()
    
    output = model.generate(
        **inputs,
        max_new_tokens=max_new,
        do_sample=True,
        temperature=0.9
    )
    
    elapsed = time.time() - start_time
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Calculate tokens per second (tps)
    token_count = output.shape[1] - inputs["input_ids"].shape[1]
    tps = token_count / elapsed
    
    return generated_text, tps

prompt = "The future of artificial intelligence is"
text, tps = generate_text(prompt)

print(f"Prompt: {prompt}")
print(f"Generated: {text}")
print(f"Performance: {tps:.2f} tokens per second")
```

## Optimization and Troubleshooting

Running LLMs on CPUs often requires specific tuning to balance speed and stability.

### Common Issues and Solutions

| Issue | Cause | Resolution |
| :--- | :--- | :--- |
| **Out-of-Memory (OOM)** | Model too large for RAM | Use 4-bit quantization or a smaller parameter model (e.g., 1B instead of 7B). |
| **High Latency** | CPU bottleneck | Set `OMP_NUM_THREADS` or `OLLAMA_NUM_THREADS` to match physical cores. |
| **System Lag** | Resource exhaustion | Limit thread count to leave cores available for the OS. |

!!! warning "CPU vs GPU Transition"
    While the logic remains the same, moving from CPU to GPU requires updating the `torch` installation to a CUDA-enabled version and changing the model device to `cuda` or using `device_map="auto"`.

## Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "Why is RAM the primary constraint when running LLMs on a CPU?"
    If the model's weights exceed available system RAM, the OS uses disk swap, which causes a catastrophic drop in inference performance.

??? question "What is quantization, and how does it help CPU-based LLM execution?"
    Quantization reduces the precision of model weights (e.g., from FP16 to 4-bit integers), drastically lowering RAM requirements and increasing speed.

??? question "When should you use Ollama versus `llama.cpp`?"
    Use Ollama for rapid prototyping and ease of deployment (bundled service); use `llama.cpp` for lightweight, embeddable, or highly customizable inference.

??? question "How do you programmatically implement LLM generation in Python for CPU use?"
    Use the `transformers` library to load a CPU-compatible model (e.g., `distilgpt2`) and a tokenizer to create a generation pipeline.

??? question "How can you prevent an LLM process from making your entire system laggy?"
    Limit the number of CPU threads used by the inference engine (e.g., via `OMP_NUM_THREADS` or `OLLAMA_NUM_THREADS`) to leave cores available for the OS.

## Practical Exercises

!!! note "Exercise 1: Rapid Deployment"
    Install Ollama and pull a model with fewer than 2 billion parameters (e.g., `tinyllama`). Run an interactive session and verify that the response time is acceptable for your hardware.

!!! note "Exercise 2: Performance Benchmarking"
    Use `llama.cpp` to run two different models: a 1B model and a 7B quantized model. Record the tokens per second (tps) for each and document the performance degradation as model size increases.

!!! note "Exercise 3: Custom Python Pipeline"
    Implement a Python script using the `transformers` library that takes a prompt from the user, generates a response, and prints the total time elapsed and the tokens per second. Test the script with `distilgpt2` and observe the impact of changing the `temperature` parameter.

## Further Reading

- Ollama Documentation: https://ollama.com/library
- llama.cpp GitHub: https://github.com/ggerganov/llama.cpp
- Hugging Face Transformers Guide: https://huggingface.co/docs/transformers/index
