# Inference and Performance Optimization

!!! info "Learning Objectives"
    By the end of this chapter, students will be able to:
    1. Calculate VRAM requirements for LLMs based on parameter count and precision.
    2. Distinguish between compute-bound and memory-bound operations in LLM inference.
    3. Explain the mechanism and memory trade-offs of KV caching.
    4. Compare different quantization levels (FP16, INT8, INT4) and their impact on performance.
    5. Describe how PagedAttention and Speculative Decoding optimize throughput.

## Overview

LLM inference is the process of using a trained model to generate text. Unlike training, which processes large batches of data in parallel, inference is typically autoregressive: the model generates one token at a time, and each new token depends on all previously generated tokens.

The primary challenge in production inference is not the raw number of floating-point operations (FLOPs) the hardware can perform, but the speed at which data can be moved from memory to the processor. This makes LLM inference predominantly memory-bound. Optimization techniques focus on reducing the memory footprint of the model and the overhead of managing the context window.

## Core Sections

### Memory vs Compute

LLM inference consists of two main phases: the prefill phase (processing the input prompt) and the decode phase (generating tokens one by one).

The prefill phase is typically compute-bound because the model processes all input tokens in parallel, maximizing the utilization of GPU tensor cores. However, the decode phase is memory-bound. To generate a single token, the GPU must read every single parameter of the model from VRAM into the compute cores.

Why this matters: If the memory bandwidth is 2 TB/s and the model is 140 GB (FP16), the maximum theoretical generation speed is limited by how fast those 140 GB can be read, regardless of how many TFLOPS the GPU possesses.

#### VRAM Calculation

The memory required to load a model is determined by the number of parameters and the precision (bits per parameter).

1. FP32 (Full Precision): 4 bytes per parameter.
2. FP16/BF16 (Half Precision): 2 bytes per parameter.
3. INT8 (Quantized): 1 byte per parameter.
4. INT4 (Quantized): 0.5 bytes per parameter.

The following Python script calculates the minimum VRAM required to load a model, including a buffer for the KV cache and system overhead.

```python
def calculate_vram(params_billions, precision_bytes=2, overhead_gb=2):
    """
    Calculates the estimated VRAM required to load an LLM.
    
    Args:
        params_billions (float): Model size in billions of parameters.
        precision_bytes (float): Bytes per parameter (e.g., 2 for FP16, 0.5 for INT4).
        overhead_gb (float): Additional VRAM for KV cache and OS (GB).
    """
    # Model weight memory = params * precision
    model_weight_gb = params_billions * precision_bytes
    total_vram_gb = model_weight_gb + overhead_gb
    
    return total_vram_gb

# Example: Llama-3 8B in FP16 (2 bytes)
model_size = 8
precision = 2
required = calculate_vram(model_size, precision)
print(f"Required VRAM for {model_size}B model in FP16: {required} GB")

# Example: Llama-3 70B in INT4 (0.5 bytes)
model_size_large = 70
precision_low = 0.5
required_large = calculate_vram(model_size_large, precision_low)
print(f"Required VRAM for {model_size_large}B model in INT4: {required_large} GB")
```

:::warning
Calculating only the model weight memory is a common mistake. In production, the KV cache grows with the sequence length and batch size, often requiring several additional gigabytes of VRAM.

## Acceleration Techniques

### KV Caching

In an autoregressive model, the hidden states (Keys and Values) for previous tokens are identical regardless of what the next token is. Without caching, the model would recompute the K and V vectors for every token in the prompt for every new token generated, resulting in $O(n^2)$ complexity.

KV caching stores these vectors in VRAM, allowing the model to only compute the K and V for the most recent token.

Why this matters: KV caching reduces the computational complexity of the decode phase from quadratic to linear, drastically increasing the tokens-per-second rate.

:::tip
To optimize KV cache memory, consider using Grouped-Query Attention (GQA), which shares key and value heads across multiple query heads, reducing the cache size without significant loss in quality.

### Quantization

Quantization reduces the precision of model weights from high-bit floats (FP16) to lower-bit integers (INT8, INT4). This reduces the memory footprint and increases the speed of memory transfers.

1. Post-Training Quantization (PTQ): Weights are quantized after the model is trained. This is faster but can lead to accuracy degradation.
2. Quantization-Aware Training (QAT): The model is trained to be resilient to quantization errors.

Common formats include:

- GGUF: Optimized for CPU/GPU hybrid inference (common in llama.cpp).
- AWQ (Activation-aware Weight Quantization): Protects important weights to maintain accuracy.
- GPTQ: A layer-wise quantization method that minimizes output error.

Why this matters: Quantization allows a 70B parameter model (which would normally require 140 GB of VRAM in FP16) to fit into 40 GB of VRAM in INT4, making it deployable on a single A100 or H100 GPU.

### Speculative Decoding

Speculative decoding uses two models: a small, fast "draft" model and a large, accurate "target" model.

1. The draft model predicts the next $k$ tokens quickly.
2. The target model verifies all $k$ tokens in a single parallel forward pass.
3. If the target model disagrees with a token, it rejects the subsequent tokens, and the process restarts from the point of failure.

Why this matters: Since the target model's verification pass is compute-bound (parallel) rather than memory-bound (sequential), speculative decoding can increase throughput by 2x-3x without changing the output distribution of the larger model.

### PagedAttention

Traditional KV caches allocate contiguous blocks of memory for the maximum possible sequence length. This leads to internal fragmentation (memory allocated but not used) and external fragmentation (memory available but not contiguous).

PagedAttention, introduced by vLLM, manages KV cache memory using a paging mechanism similar to virtual memory in operating systems. It divides the cache into small, non-contiguous blocks.

Why this matters: PagedAttention eliminates memory waste, allowing for significantly larger batch sizes and higher throughput in production environments.

## Summary Checklist

1. [ ] Calculated VRAM requirements for different precisions.
2. [ ] Explained why LLM decode is memory-bound.
3. [ ] Described the purpose and mechanism of KV caching.
4. [ ] Compared FP16, INT8, and INT4 quantization.
5. [ ] Explained the draft-and-verify cycle of Speculative Decoding.
6. [ ] Identified how PagedAttention reduces memory fragmentation.

## Assignments

!!! note "VRAM Capacity Planning"
    You are deploying a model with 30 billion parameters. You have a GPU with 48 GB of VRAM.
    
    Determine if the model will fit in FP16, INT8, and INT4 precision, assuming 4 GB of overhead for the system and KV cache.
    
    ??? question "Solution"
        1. FP16: $30 \times 2 + 4 = 64$ GB. (Does not fit)
        2. INT8: $30 \times 1 + 4 = 34$ GB. (Fits)
        3. INT4: $30 \times 0.5 + 4 = 19$ GB. (Fits)

!!! note "KV Cache Trade-offs"
    Explain why increasing the batch size in a production server increases the VRAM pressure even if the model weights remain the same.
    
    ??? question "Solution"
        The KV cache must be maintained for every request in the batch. If the batch size is 32 and the sequence length is 2048, the server must store 32 separate sets of Key and Value vectors. As batch size grows, the total VRAM consumed by the KV cache grows linearly, potentially leading to Out-of-Memory (OOM) errors.

## References

1. vLLM: PagedAttention for efficient LLM serving.
2. GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers.
3. Speculative Decoding: Fast Inference from Large Language Models.

## Self-Evaluation

??? note "What is the difference between the prefill and decode phases in terms of hardware utilization?"
    The prefill phase is compute-bound, utilizing GPU tensor cores to process the input prompt in parallel. The decode phase is memory-bound, limited by the bandwidth required to move model weights from VRAM to the cores for every single token generated.

??? note "Why is KV caching essential for LLM performance?"
    It prevents the redundant re-computation of hidden states for all previous tokens in the sequence, reducing the complexity of generating each new token from $O(n^2)$ to $O(n)$.

??? note "How does INT4 quantization impact a model compared to FP16?"
    It reduces the memory footprint by 4x (from 2 bytes to 0.5 bytes per parameter), allowing larger models to fit on smaller GPUs and increasing memory bandwidth efficiency, though it may introduce slight degradation in model perplexity.

??? note "In what scenario would Speculative Decoding be ineffective?"
    If the draft model is too inaccurate, the target model will frequently reject its predictions, causing the system to fall back to standard sequential decoding and adding the overhead of the draft model's computation.

??? note "How does PagedAttention solve the problem of memory fragmentation?"
    It treats the KV cache as a series of non-contiguous pages rather than a single contiguous block. This allows the system to allocate memory dynamically as needed, eliminating the need to reserve the maximum sequence length upfront.
