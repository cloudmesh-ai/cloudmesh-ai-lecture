# GPU-Accelerated LLM Deployment

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Configure the NVIDIA GPU software stack, including drivers, CUDA Toolkit, and PyTorch.
    - Deploy Large Language Models (LLMs) using multiple inference engines: Ollama, vLLM, and Slang.
    - Evaluate the trade-offs between different GPU serving frameworks based on throughput and ease of deployment.
    - Manage GPU VRAM allocation and optimize model loading for hardware constraints.

The execution of Large Language Models (LLMs) is computationally intensive, requiring massive parallelization of matrix multiplications. While CPUs can run these models, Graphics Processing Units (GPUs) are specifically designed for this type of workload, offering orders-of-magnitude increases in tokens-per-second (tps).

The primary bottleneck in GPU deployment is Video RAM (VRAM). The model weights must be loaded into VRAM to achieve high performance. If a model exceeds the available VRAM, the system must either offload parts of the model to system RAM (drastically reducing speed) or fail with an Out-of-Memory (OOM) error. Choosing the right inference engine depends on whether the priority is rapid prototyping, low-latency single-user interaction, or high-throughput production serving.

## The GPU Infrastructure Stack

Before deploying a model, the host system must be configured with the correct hardware drivers and software libraries to allow the operating system and Python to communicate with the GPU.

### Hardware and Driver Requirements

The system requires an NVIDIA GPU with CUDA Compute Capability 6.0 or higher. The following components must be verified:

1. NVIDIA Driver: The kernel-level driver that allows the OS to interface with the GPU.
2. CUDA Toolkit: A parallel computing platform and API model that allows software to use the GPU for general-purpose processing.
3. cuDNN: A GPU-accelerated library for deep neural networks.

Verification of the driver and GPU status is performed using the `nvidia-smi` utility:

```bash
nvidia-smi
```

This command outputs the driver version, CUDA version, and current VRAM utilization.

### PyTorch and CUDA Integration

Most LLM frameworks use PyTorch as their underlying tensor library. PyTorch must be installed with a version that matches the installed CUDA Toolkit.

To isolate dependencies, a Python virtual environment is required:

```bash
mkdir -p ~/llm-gpu-demo && cd ~/llm-gpu-demo
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
```

Installation of the CUDA-enabled PyTorch build:

```bash
# Example for CUDA 12.4
pip install torch==2.3.0+cu124 torchvision==0.18.0+cu124 torchaudio==2.3.0+cu124 -f https://download.pytorch.org/whl/torch_stable.html
```

Verification of the installation is performed via a Python script:

```python
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    print(f"VRAM Total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

## Model Acquisition and Management

Model weights are typically stored in the Hugging Face Hub. Because model files are large (often exceeding 10 GB), Git Large File Storage (LFS) is used for cloning.

### Cloning Model Repositories

To clone a model repository, `git-lfs` must be installed on the system:

```bash
sudo apt-get install git-lfs
git lfs install
```

Cloning a specific model, such as Llama-2-7B-Chat:

```bash
git lfs clone https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
```

This creates a local directory containing the model weights, tokenizer configuration, and metadata.

## Inference Engine Implementation

Different engines offer different balances of performance, memory efficiency, and ease of use.

### Ollama: Rapid Prototyping

Ollama is an all-in-one tool that bundles the model runner and a REST API. It is designed for ease of deployment and local development.

Installation on Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Running a model:

```bash
ollama run llama2
```

Ollama manages model quantization and VRAM loading automatically, making it suitable for developers who require a functional API without manual memory tuning.

### vLLM: High-Throughput Production

vLLM is designed for production environments where high throughput and low latency are critical. Its primary innovation is PagedAttention, which optimizes the KV (Key-Value) cache to reduce memory fragmentation.

Installation:

```bash
pip install "vllm[all]"
```

Deploying an OpenAI-compatible API server:

```bash
python -m vllm.entrypoints.openai.api_server \
    --model ./Llama-2-7b-chat-hf \
    --tensor-parallel-size 1 \
    --port 8000 \
    --gpu-memory-utilization 0.9
```

Key parameters in vLLM:
- `--tensor-parallel-size`: Number of GPUs to split the model across.
- `--gpu-memory-utilization`: The fraction of GPU memory to reserve for the model and KV cache (default is 0.9).

### Slang: Lightweight Execution

Slang is a Rust-based inference engine focused on minimalism and performance. It often uses GGUF formats to allow for efficient loading.

Basic deployment flow:

```bash
# Convert HF model to GGUF
slang convert ./Llama-2-7b-chat-hf llama2-7b-chat.gguf

# Serve the model on GPU
slang serve --model llama2-7b-chat.gguf --device cuda
```

## Performance Comparison and Selection

The choice of engine is determined by the operational requirements of the application.

| Feature | Ollama | Slang | vLLM |
| :--- | :--- | :--- | :--- |
| **Primary Use Case** | Local Dev / Hobbyist | Lightweight / Embeddable | Production / API Service |
| **Architecture** | Wrapper / Go / C++ | Rust | Python / CUDA Kernels |
| **Memory Mgmt** | Automatic | Efficient (GGUF) | PagedAttention (Advanced) |
| **Throughput** | Moderate | Moderate | High |
| **API Style** | Custom / OpenAI | Custom | OpenAI Compatible |

### VRAM Calculation

To estimate the VRAM required for a model:
- FP16 (Full Precision): $\text{Parameters} \times 2 \text{ bytes}$
- INT4 (Quantized): $\text{Parameters} \times 0.5 \text{ bytes}$ (approximately)

For a 7B parameter model:
- FP16: $7 \times 10^9 \times 2 \approx 14 \text{ GB}$
- INT4: $7 \times 10^9 \times 0.5 \approx 3.5 \text{ GB}$

Additional VRAM is required for the KV cache, which grows with the context length.

!!! tip "Summary Checklist"

    - [ ] Verified NVIDIA drivers and CUDA Toolkit installation via `nvidia-smi`.
    - [ ] Installed PyTorch with the correct CUDA build and verified GPU access.
    - [ ] Installed `git-lfs` and cloned model weights from Hugging Face.
    - [ ] Evaluated and selected an inference engine (Ollama for ease, vLLM for throughput).
    - [ ] Calculated VRAM requirements to prevent Out-of-Memory (OOM) errors.

!!! note "Assignment 1: Environment Validation"

    **Task**: Install the CUDA-enabled version of PyTorch in a virtual environment. Write a Python script that prints the total VRAM of the first available GPU and its compute capability.
    **Goal**: Ensure the software stack is correctly linked to the hardware.

!!! note "Assignment 2: vLLM Deployment"

    **Task**: Deploy a 7B model using vLLM. Use a `curl` command to send a request to the `/v1/completions` endpoint and measure the time taken for the first token to appear (Time to First Token - TTFT).
    **Goal**: Implement a production-grade serving endpoint and measure latency.

!!! note "Assignment 3: VRAM Benchmarking"

    **Task**: Load the same model using Ollama and vLLM. Use `nvidia-smi -l 1` to monitor VRAM usage during inference. Compare how each engine handles memory allocation.
    **Goal**: Understand the difference between static memory allocation (vLLM) and dynamic loading (Ollama).
