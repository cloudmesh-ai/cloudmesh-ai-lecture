# LLM Infrastructure and Deployment

!!! info "Learning Objectives"
    By the end of this chapter, students will be able to:
    1. Compare enterprise and consumer GPU architectures for LLM inference.
    2. Explain the function of NVLink and InfiniBand in distributed serving.
    3. Deploy an LLM using the vLLM serving framework.
    4. Analyze the trade-offs between Model-as-a-Service (MaaS) and self-hosted Kubernetes deployments.

## Overview

Deploying Large Language Models (LLMs) requires a fundamental shift from traditional microservices architecture. While standard APIs are typically compute-bound or I/O-bound, LLM inference is primarily memory-bandwidth bound. The challenge of infrastructure is managing the massive memory requirements of model weights and the dynamic memory requirements of the Key-Value (KV) cache during token generation.

Effective deployment focuses on three primary metrics:
1. Time to First Token (TTFT): The latency before the user sees the first character of the response.
2. Inter-token Latency: The speed at which subsequent tokens are generated.
3. Throughput: The total number of tokens generated across all concurrent requests per second.

## Core Sections

### Hardware Selection

Hardware selection is the most critical decision in the LLM lifecycle because it defines the upper bound of model size and concurrency.

#### GPU Architectures

Enterprise GPUs, such as the NVIDIA H100 and A100, are designed for high-throughput data center workloads. They feature HBM (High Bandwidth Memory), which allows the GPU to move model weights from memory to the compute cores rapidly.

Consumer GPUs, like the RTX 4090 or L40S, offer significant compute power but are limited by slower GDDR6X memory and lower total VRAM.

Why this matters: Using a GPU with insufficient VRAM will force the model to offload weights to system RAM (via PCIe), which increases latency by orders of magnitude, making the model unusable for real-time applications.

#### Interconnects and Distributed Inference

When a model is too large for a single GPU (e.g., a 70B parameter model in FP16 requires ~140GB of VRAM), it must be split across multiple GPUs using Tensor Parallelism.

1. NVLink: A high-speed, point-to-point interconnect that allows GPUs within a single node to communicate without going through the PCIe bus.
2. InfiniBand: A low-latency networking standard used to connect multiple GPU nodes into a cluster for massive-scale inference.

Why this matters: Without high-speed interconnects, the synchronization overhead between GPUs becomes the primary bottleneck, negating the benefits of adding more hardware.

:::warning
Avoid mixing GPU architectures (e.g., combining A100s and H100s) in a single Tensor Parallel group. The system will default to the slowest common denominator, causing resource underutilization and unpredictable latency.
:::

### Serving Frameworks

Standard Python wrappers around model weights are insufficient for production. Specialized serving frameworks optimize how memory is allocated and how requests are batched.

#### vLLM and PagedAttention

vLLM is a high-throughput serving engine that introduces PagedAttention. Traditional serving allocates a contiguous block of memory for the KV cache of each request, leading to significant internal fragmentation. PagedAttention manages the KV cache as non-contiguous blocks (pages), similar to virtual memory in operating systems.

Why this matters: PagedAttention allows for much higher batch sizes by reducing memory waste, directly increasing the total throughput of the server.

#### NVIDIA Triton and TensorRT-LLM

For maximum performance on NVIDIA hardware, TensorRT-LLM compiles the model into a highly optimized engine. It uses kernel fusion and quantization to reduce the computational overhead of each token. NVIDIA Triton serves as the model orchestrator, managing multiple model instances and request queues.

#### Local Deployment with Ollama

Ollama provides a simplified abstraction for running LLMs locally. It bundles the model weights, configuration, and a serving engine into a single package, making it suitable for developer prototyping and internal tooling.

:::tip
Use Ollama for the initial prototyping phase to validate prompt engineering, then migrate to vLLM or TensorRT-LLM when transitioning to a production environment requiring high concurrency.
:::

Below is an example of a Kubernetes manifest for deploying a vLLM server using a GPU node.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm-serving
  labels:
    app: vllm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm
  template:
    metadata:
      labels:
        app: vllm
    spec:
      containers:
      - name: vllm-container
        image: vllm/vllm-openai:latest
        args:
        - "--model"
        - "facebook/opt-125m"
        - "--gpu-memory-utilization"
        - "0.9"
        - "--max-model-len"
        - "2048"
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
        env:
        - name: HUGGING_FACE_HUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: hf-token
              key: token
```

### Cloud Strategies

The choice of deployment strategy is a trade-off between operational overhead, data privacy, and cost.

#### Model-as-a-Service (MaaS)

MaaS providers (e.g., OpenAI, Anthropic, Azure AI) provide access to models via a managed API. The provider handles all infrastructure, scaling, and hardware optimization.

Why this matters: MaaS allows teams to iterate quickly without managing GPU clusters, shifting the cost from Capital Expenditure (CapEx) to Operational Expenditure (OpEx).

#### Self-hosting on Kubernetes

Self-hosting involves deploying models on your own GPU nodes using frameworks like KServe or Ray Serve. These tools provide the necessary abstractions for autoscaling, canary deployments, and resource quotas.

1. KServe: A serverless inferencing platform that integrates with Knative for scale-to-zero capabilities.
2. Ray Serve: A scalable model serving library that allows for complex inference pipelines (e.g., combining an embedding model with a generative model).

Why this matters: Self-hosting is necessary for organizations with strict data sovereignty requirements or those using highly customized fine-tuned models that cannot be uploaded to a third-party provider.

:::warning
Self-hosting introduces significant "hidden" costs, including the need for specialized DevOps engineers to manage GPU drivers, CUDA versions, and Kubernetes device plugins.
:::

## Summary Checklist

1. Hardware: Have the VRAM requirements for the model weights and expected KV cache been calculated?
2. Interconnects: If using multiple GPUs, is NVLink configured and verified?
3. Framework: Has a serving framework (vLLM, Triton) been selected based on the throughput requirements?
4. Cloud Strategy: Has the decision between MaaS and self-hosting been justified by privacy and cost analysis?
5. Observability: Are metrics for TTFT and inter-token latency being tracked?

## Assignments

!!! note "VRAM Calculation"
    Given a model with 70 billion parameters stored in FP16 (2 bytes per parameter), calculate the minimum VRAM required just to load the model weights. How does this change if the model is quantized to INT4 (0.5 bytes per parameter)?

    ??? question "Solution"
        1. FP16: 70 billion parameters * 2 bytes/param = 140 GB.
        2. INT4: 70 billion parameters * 0.5 bytes/param = 35 GB.
        Note: This does not include the VRAM needed for the KV cache or activation tensors.

!!! note "vLLM Deployment"
    Write a bash command to launch a vLLM server using the `meta-llama/Llama-2-7b-hf` model, limiting the GPU memory utilization to 80% and setting the maximum sequence length to 4096.

    ??? question "Solution"
        ```bash
        python -m vllm.entrypoints.openai.api_server \
            --model meta-llama/Llama-2-7b-hf \
            --gpu-memory-utilization 0.8 \
            --max-model-len 4096
        ```

## References

1. vLLM Documentation: https://docs.vllm.ai/
2. NVIDIA TensorRT-LLM Guide: https://nvidia.github.io/TensorRT-LLM/
3. KServe Documentation: https://kserve.github.io/website/
4. Ray Serve Documentation: https://docs.ray.io/en/latest/serve/index.html

## Self-Evaluation

??? note "What is the primary difference between HBM and GDDR6X in the context of LLMs?"
    HBM (High Bandwidth Memory) provides significantly higher memory bandwidth than GDDR6X, which is critical for LLM inference because the process is memory-bandwidth bound.

??? note "Why is PagedAttention more efficient than contiguous memory allocation for the KV cache?"
    PagedAttention allows the KV cache to be stored in non-contiguous blocks, eliminating internal fragmentation and allowing for higher batch sizes and better GPU utilization.

??? note "When should a team choose self-hosting over a MaaS provider?"
    Self-hosting should be chosen when there are strict data privacy requirements (data cannot leave the VPC), a need for deep control over the model version/weights, or when the scale of requests makes a fixed-cost GPU cluster cheaper than per-token pricing.

??? note "What is the role of NVLink in a multi-GPU setup?"
    NVLink provides a high-speed communication path between GPUs, allowing them to synchronize weights and activations during Tensor Parallelism without the bottleneck of the PCIe bus.

??? note "How does quantization affect the hardware requirements for LLM deployment?"
    Quantization reduces the precision of model weights (e.g., from FP16 to INT4), which proportionally reduces the VRAM required to load the model, allowing larger models to fit on smaller or fewer GPUs.
