# Hands-On Lab Blueprint: Deploying an LLM Inference Service

This lab provides a step-by-step blueprint for architecting, deploying, and monitoring a Large Language Model (LLM) inference service on a managed Kubernetes cluster. The goal is to move from a raw model weight file to a scalable, observable, and secure production endpoint.

## Learning Objectives

!!! info "Learning Objectives"

    - Provision a GPU-enabled managed Kubernetes cluster (EKS, AKS, or GKE).
    - Optimize a HuggingFace transformer model using ONNX for efficient inference.
    - Containerize an LLM using FastAPI and Docker, ensuring GPU acceleration via CUDA.
    - Automate the lifecycle using a GitHub Actions CI/CD pipeline.
    - Orchestrate the deployment with Helm, configuring Horizontal Pod Autoscaling (HPA) for GPU workloads.
    - Secure the service using internal Application Load Balancers (ALB) and IAM-based identity.
    - Instrument the application with OpenTelemetry (OTEL) and Prometheus for real-time observability.
    - Implement AI safety guardrails using a regex-based blacklist.

## Overview

The architecture follows a cloud-native pattern:
`User Request` $\rightarrow$ `ALB` $\rightarrow$ `K8s Service` $\rightarrow$ `FastAPI Pod (GPU)` $\rightarrow$ `ONNX Runtime` $\rightarrow$ `LLM Model`

Telemetry is streamed to a Prometheus/Grafana stack, and the deployment is managed via GitOps principles.

## Lab Implementation Steps

### Step 1: Environment Preparation

Before deploying the model, the underlying infrastructure must be established.

1. **Cloud Account & Quotas**: 
   - Ensure you have an active AWS/Azure/GCP account.
   - Request a quota increase for GPU instances (e.g., `p3.2xlarge` on AWS or `Standard_NC` on Azure). Most default accounts have a quota of 0 for GPUs.

2. **Cluster Provisioning**:
   - Provision a managed Kubernetes cluster.
   - Create a dedicated **GPU Node Pool**. Ensure the nodes have the necessary NVIDIA drivers installed (e.g., using the Amazon EKS optimized GPU AMI).

3. **Tooling Installation**:
   - `kubectl`: For cluster interaction.
   - `helm`: For package management.
   - `cloud-cli`: (aws, az, or gcloud) for authentication and registry management.

### Step 2: Model Selection and Optimization (OPT-125m & ONNX)

For educational purposes, this lab uses **Facebook's OPT-125m**. It is small enough to run on modest hardware but shares the architecture of larger LLMs.

1. **Model Selection**: Download the `facebook/opt-125m` model from HuggingFace.

2. **ONNX Conversion**: 
   - Raw PyTorch models are often inefficient for inference. We convert the model to **ONNX (Open Neural Network Exchange)** format.
   - Use the `optimum` library from HuggingFace:

   ```bash
   pip install optimum[onnxruntime-gpu]
   optimum-cli export onnx --model facebook/opt-125m opt_onnx/
   ```

3. **Why ONNX?**: This step introduces graph optimizations, constant folding, and the ability to run inference across different hardware backends without changing the model code.

### Step 3: Containerization with FastAPI

The model is wrapped in an asynchronous API.

1. **API Implementation**: Create a `main.py` using FastAPI.

   ```python
   from fastapi import FastAPI
   from optimum.onnxruntime import ORTModelForCausalLM
   from transformers import AutoTokenizer

   app = FastAPI()
   tokenizer = AutoTokenizer.from_pretrained("facebook/opt-125m")
   model = ORTModelForCausalLM.from_pretrained("opt_onnx/", provider="CUDAExecutionProvider")

   @app.post("/generate")
   async def generate(prompt: str):
       inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
       outputs = model.generate(**inputs, max_new_tokens=50)
       return {"text": tokenizer.decode(outputs[0], skip_special_tokens=True)}
   ```

2. **Dockerfile Optimization**:
   - Use a CUDA-enabled base image: `nvidia/cuda:12.1.0-base-ubuntu22.04`.
   - Implement multi-stage builds to keep the final image lean.
   - Install `onnxruntime-gpu` to ensure the API leverages the GPU.

### Step 4: CI Pipeline (GitHub Actions)

Automate the build, test, and push cycle.

1. **Workflow Trigger**: Configure `.github/workflows/pipeline.yml` to trigger on pushes to the `main` branch.

2. **Build & Push**:
   - Use `docker build` to create the image.
   - Authenticate with the cloud registry (e.g., Amazon ECR).
   - Tag the image with the Git commit SHA for traceability.

3. **Automated Testing**: Run a lightweight test suite (using a CPU-only version of the model) to verify that the FastAPI endpoints are responding correctly before pushing.

### Step 5: Deployment (Helm & HPA)

Manage the application lifecycle with Kubernetes primitives.

1. **Helm Charting**: Create a chart defining the `Deployment`, `Service`, and `HPA`.

2. **GPU Resource Requests**: 
   - Define the GPU limit in the deployment spec:

   ```yaml
   resources:
     limits:
       nvidia.com/gpu: 1 
   ```

3. **Autoscaling (HPA)**:
   - Configure the Horizontal Pod Autoscaler. Since CPU/Memory are often misleading for LLMs, explore custom metrics (e.g., GPU Duty Cycle) via the Prometheus Adapter to trigger scaling.

### Step 6: Ingress and Identity (ALB & IAM)

Expose the service securely.

1. **ALB Controller**: Deploy the AWS Load Balancer Controller to automatically provision an ALB based on Kubernetes Ingress resources.

2. **Internal Exposure**: Set the ALB to `internal` to ensure the LLM is not exposed to the public internet, simulating a corporate internal API.

3. **IAM Roles for Service Accounts (IRSA)**: 
   - Use IRSA to give the Pod a temporary IAM role. This allows the Pod to securely pull models from S3 or write logs to CloudWatch without embedded keys.

### Step 7: Observability (OTEL & Prometheus)

1. **OpenTelemetry Integration**: 
   - Add the OTEL Python SDK to the FastAPI app.
   - Instrument the `/generate` endpoint to track **Inference Latency** and **Token Throughput**.

2. **Prometheus Monitoring**:
   - Deploy Prometheus to scrape the OTEL collector.
   - Create a Grafana dashboard visualizing GPU temperature, memory usage, and request volume.

3. **The Hallucination Monitor**:
   - Implement a basic "hallucination-rate" monitor. 
   - Compare the model's output confidence scores (log-probs) against a threshold. If the average confidence for a response is below a specific percentage, flag it as a potential hallucination in the telemetry.

### Step 8: AI Safety (Regex Blacklist)

Implement a first-line defense against prohibited content.

1. **Guardrail Layer**: Create a middleware in FastAPI that intercepts requests and responses.

2. **Blacklist Implementation**: 
   - Maintain a list of regex patterns for prohibited topics.
   - If a match is found in the prompt, return a `403 Forbidden` with a safety warning.
   - If a match is found in the model output, redact the response before it reaches the user.

### Step 9: Demonstration and Validation

Final verification of the system.

1. **Functional Test**: Send a prompt to the ALB DNS and receive a generated response.

2. **Scaling Test**: Use a tool like `locust` or `hey` to flood the API with requests. Observe the HPA spinning up new GPU pods.

3. **Safety Test**: Input a blacklisted phrase and verify the guardrail blocks the request.

4. **Telemetry Review**: Open Grafana and observe the latency spikes and the hallucination-rate monitor in real-time.

## Architectural Trade-off: Raw GPU vs. Managed Services

Students must evaluate the choice between building a custom stack and using a managed provider.

| Feature | Raw GPU (EKS/AKS/GKE) | Managed (Bedrock / Azure OpenAI) |
| :--- | :--- | :--- |
| **Control** | Full control over model weights, quantization, and runtime. | Limited to provider-supported models and versions. |
| **Cost Model** | Hourly instance rate (Provisioned). | Pay-per-token (Serverless). |
| **Operational Effort** | High (Drivers, K8s, Scaling, Monitoring). | Low (API call only). |
| **Privacy** | Maximum (Data stays within your VPC). | High (depends on provider's data policy). |
| **Optimization** | Can use ONNX, TensorRT, vLLM for max perf. | Bound by provider's underlying optimization. |

## Summary Checklist

- [ ] GPU Quotas increased in Cloud Console.
- [ ] GPU Node Pool provisioned with NVIDIA drivers.
- [ ] Model converted to ONNX format.
- [ ] FastAPI container built and pushed to ECR.
- [ ] Helm chart deployed with `nvidia.com/gpu` limits.
- [ ] Internal ALB configured and IRSA roles attached.
- [ ] Prometheus scraping OTEL metrics.
- [ ] Safety regex middleware active.

## Assignments

!!! note "Assignment.1: Performance Comparison"

    Convert the OPT-125m model to ONNX and compare the inference latency (tokens per second) against the raw PyTorch implementation. Document the delta.

    ??? tip "Solution: Performance Comparison"

        Students should use `time.time()` or the OTEL latency metrics. Typically, ONNX Runtime with CUDA provides a 20-40% reduction in latency due to graph optimizations.

!!! note "Assignment.2: Custom Scaling Metric"

    Configure the Prometheus Adapter to trigger the HPA based on `gpu_utilization` rather than CPU usage.

    ??? tip "Solution: Custom Scaling Metric"

        This requires installing the `prometheus-adapter` and configuring a `CustomMetric` resource that maps the `dcgm_gpu_utilization` metric to the `pods` resource.

!!! note "Assignment.3: Enhanced Guardrails"

    Expand the regex blacklist to include a "jailbreak" detection pattern (e.g., detecting "Ignore all previous instructions").

    ??? tip "Solution: Enhanced Guardrails"

        Implement a regex pattern like `(?i)(ignore|disregard).*previous.*instructions` in the FastAPI middleware.

## References

- HuggingFace Optimum Documentation: [https://huggingface.co/docs/optimum/](https://huggingface.co/docs/optimum/)
- ONNX Runtime GPU Guide: [https://onnxruntime.ai/docs/](https://onnxruntime.ai/docs/)
- OpenTelemetry Python SDK: [https://opentelemetry.io/docs/instrumentation/python/](https://opentelemetry.io/docs/instrumentation/python/)
- Kubernetes GPU Documentation: [https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#gpu-resources](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#gpu-resources)

## Self-Evaluation

??? note "Why is ONNX preferred over raw PyTorch for production LLM inference?"

    ONNX provides a standardized representation of the model graph, allowing for hardware-specific optimizations (like constant folding and kernel fusion) that can significantly reduce latency and memory overhead.

??? note "How does IRSA improve the security of an LLM pod compared to using static secrets?"

    IRSA (IAM Roles for Service Accounts) provides the pod with temporary, short-lived AWS credentials via an OIDC provider. This eliminates the need to store long-lived access keys in Kubernetes secrets, reducing the risk of credential leakage.

??? note "What is the purpose of the 'hallucination monitor' in this architecture?"

    The hallucination monitor tracks the model's output confidence (log-probs). By alerting when confidence drops below a threshold, operators can identify when the model is likely guessing or fabricating information, providing a signal for human review or fallback mechanisms.
