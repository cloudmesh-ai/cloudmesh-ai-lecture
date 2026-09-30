# Kubernetes (K8s) for AI: Production-Grade Orchestration

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Explain the core architecture of Kubernetes and its role in the AI lifecycle.
    - Distinguish between key K8s objects: Pods, Deployments, Services, and ConfigMaps.
    - Design a production-ready architecture for an AI application.
    - Implement GPU-aware scheduling using resource limits, taints, and tolerations.
    - Deploy a multi-tier AI application using Kubernetes manifests.

## Overview

While Docker provides the "container" (the package), **Kubernetes (K8s)** provides the "orchestra" (the management). In an AI context, workloads are rarely limited to a single container; they typically form a pipeline consisting of data ingestion, preprocessing, inference, and a frontend. Kubernetes orchestrates these disparate components into a unified, scalable system.

AI development is iterative and resource-intensive. Without an orchestrator, moving a model from a researcher's notebook to a GPU cluster involves manual image builds and SSH-based deployments. Kubernetes transforms this into a repeatable process, ensuring that the exact same environment used for training is used for inference, thereby eliminating "environment drift."

!!! info "Why this matters"
    Kubernetes is the industry standard for AI because it handles the unique requirements of deep learning workloads: GPU orchestration to prevent resource contention, elasticity to handle spiky inference demand, and self-healing to automatically restart LLM processes that crash due to Out-of-Memory (OOM) errors.

## Core Sections

### The AI Lifecycle and Kubernetes

Kubernetes provides the underlying infrastructure for each stage of the AI lifecycle:

- **Data Engineering**: Orchestrating Spark or Ray clusters to clean and preprocess massive datasets.
- **Training**: Managing distributed training jobs (often via operators like Kubeflow) that synchronize weights across dozens of GPUs.
- **Inference (Deployment)**: Wrapping trained models in high-performance containers (e.g., vLLM) and scaling them based on real-time traffic.
- **Monitoring**: Tracking "model drift" and GPU health to determine when a model needs to be re-trained.

### Kubernetes Core Architecture

Kubernetes operates on a **Cluster** model consisting of a **Control Plane** (the brain) and one or more **Worker Nodes** (the muscle). This decoupled architecture ensures that the management of the cluster is separated from the execution of workloads.

#### The Control Plane

The Control Plane makes global decisions about the cluster and responds to events:

- **kube-apiserver**: The central gateway for all communication.
- **etcd**: A distributed key-value store that acts as the cluster's "source of truth," ensuring state is preserved even if the API server crashes.
- **kube-scheduler**: Critical for AI; it performs **Bin-Packing** to maximize GPU utilization or **Spreading** to ensure high availability.
- **kube-controller-manager**: Handles cluster-level functions, such as replacing pods when a node fails.

#### Worker Nodes

Worker nodes are the physical or virtual machines where workloads run. Each node hosts three essential components:

- **Kubelet**: The node agent that ensures containers are running and healthy according to the pod specification.
- **kube-proxy**: Manages network rules on the host to enable communication between pods and external clients.
- **Container Runtime**: The execution engine (e.g., `containerd` or `CRI-O`) that pulls images and manages namespaces/cgroups.

### Key Kubernetes Objects

| Object | Description | AI Use Case |
|----------|-------------|----------------|
| **Pod** | The smallest deployable unit; contains one or more containers. | A single LLM instance. |
| **Deployment** | Manages identical pods, handling updates and scaling. | Scaling a FastAPI backend to 5 replicas. |
| **Service** | A stable network endpoint for a set of pods. | A stable IP address to call the LLM API. |
| **ConfigMap** | Stores non-confidential configuration data. | Model names, temperature, API endpoints. |
| **Secret** | Stores sensitive data (passwords, tokens). | HuggingFace API keys. |
| **Ingress** | Manages external HTTP/S access to services. | The public URL for the AI Frontend. |

### Packaging and Deployment Patterns

In a production environment, managing raw YAML manifests for every environment (Dev, Staging, Prod) leads to "YAML sprawl"—a state where small differences in resource limits or environment variables result in dozens of nearly identical files. To solve this, AI engineers use templating and overlay tools.

#### Helm: The Package Manager for Kubernetes
**Helm** introduces the concept of a **Chart**. Instead of hard-coding values, you use placeholders (e.g., `{{ .Values.gpuLimit }}`). This allows you to maintain one chart and multiple `values.yaml` files for different environments.

- **Why AI needs Helm**: Model weights and GPU requirements vary wildly between a researcher's "sandbox" and a production "serving" cluster. Helm allows you to switch from 1 GPU in Dev to 8 GPUs in Prod by changing a single value in a YAML file.

#### Kustomize: Template-less Overlays
Unlike Helm, **Kustomize** does not use templates. Instead, it uses **overlays**. You define a "Base" manifest and then "patches" that modify specific fields for a particular environment.

- **The "AI Overlay" Pattern**: You might have a base deployment for your LLM engine, but a "Production Overlay" that adds a `PriorityClass` (to ensure the LLM isn't evicted) and a `PodDisruptionBudget` (to ensure minimum availability during node upgrades).

---

### The Operator Pattern: Extending the K8s API

While Pods and Deployments handle generic containers, AI infrastructure often requires complex, stateful lifecycle management (e.g., "Don't start the LLM pod until the GPU driver is verified and the model weights are fully synced from S3"). This is where **Operators** come in.

An Operator is a method of packaging, deploying, and managing a Kubernetes application. It combines a **Custom Resource Definition (CRD)**—which adds a new "type" of object to the K8s API (e.g., a `GPUCluster` object)—with a **Custom Controller** that runs in a continuous reconciliation loop.

#### The Reconciliation Loop
The Operator's core logic is: `Observe` $\rightarrow$ `Diff` $\rightarrow$ `Act`.
1. **Observe**: The Operator watches the current state of the cluster.
2. **Diff**: It compares the current state to the "Desired State" defined in the CRD.
3. **Act**: It performs the necessary actions to align the two.

#### Critical AI Operators
- **NVIDIA GPU Operator**: Instead of manually installing drivers on every node, the Operator detects the hardware, deploys the NVIDIA driver container, installs the Container Toolkit, and configures the device plugin—all automatically.
- **Kubeflow**: Provides a suite of Operators for ML workflows, including the `TFJob` and `PyTorchJob` CRDs, which handle the complex networking required for distributed training (e.g., setting up the `MASTER_ADDR` and `WORLD_SIZE` environment variables across multiple pods).

---

### Production Architecture Guide: AI-Powered Document Intelligence

To move from a prototype to a production-grade system, an AI application must account for high availability, resource isolation, and the massive size of model weights. Consider a system that indexes PDFs into a vector database and enables RAG (Retrieval-Augmented Generation) via an LLM.

#### The Production Inference Pipeline

In production, the pipeline is decoupled into a series of asynchronous services to prevent a slow LLM response from blocking the entire system:

1. **Ingress & Frontend**: A **Streamlit Frontend** receives the PDF.
2. **Async Queue**: The frontend pushes the file to a message queue (e.g., RabbitMQ) to decouple upload from processing.
3. **Worker Nodes**: A **FastAPI Worker** pulls the file, chunks the PDF, and interacts with the embedding model.
4. **Vector Storage**: Embeddings are stored in a **Vector Database** (e.g., Milvus or Weaviate) deployed as a **StatefulSet** to ensure stable network IDs and persistent storage.
5. **Inference Engine**: Relevant chunks are sent to an **LLM Engine** (e.g., vLLM) running on GPU nodes.
6. **Response**: The generated answer is returned to the user via a WebSocket or long-polling.

#### Data Persistence for Model Weights

Model weights (e.g., `.safetensors` files) are too large to be baked into container images. In production, these are managed as follows:

- **Cold Storage**: Weights are stored in an S3-compatible object store.
- **Warm Cache**: A **PersistentVolume (PV)** backed by a high-performance NVMe SSD is used to cache the weights on the worker node.
- **Mounting**: The LLM pod uses a **PersistentVolumeClaim (PVC)** to mount this cache, ensuring that pod restarts don't require a multi-gigabyte re-download of the model.

For a detailed explanation of the CSI (Container Storage Interface) and storage abstraction, refer to **[Container Storage & Networking](/section/container/specialized/container-storage-networking.md)**.

#### Manifest Design for AI: Production Hardening

**LLM Engine (GPU-Dependent):**
Requires explicit resource limits, a `PriorityClass` to prevent eviction, and a `Toleration` for GPU nodes.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-engine
spec:
  replicas: 2
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  template:
    spec:
      priorityClassName: system-cluster-critical
      tolerations:
      - key: "ai-gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      containers:
      - name: vllm-container
        image: vllm/vllm-openai:latest
        resources:
          limits:
            nvidia.com/gpu: 1
            memory: "32Gi"
            cpu: "4"
        volumeMounts:
        - name: model-storage
          mountPath: /models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-weights-pvc
```

**Orchestration API (CPU-Based):**
Lightweight and horizontally scalable with a `PodDisruptionBudget` to ensure 1 replica is always available during maintenance.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-api-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: ai-api
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: fastapi-container
        image: my-ai-api:v1.0
        env:
        - name: LLM_ENDPOINT
          value: "http://llm-service:8000"
```

#### AI Failure Modes & Troubleshooting

| Symptom | K8s Event / Status | Likely Root Cause | Resolution |
|:---|:---|:---|:---|
| **Pod stuck in `Pending`** | `Insufficient nvidia.com/gpu` | No nodes with available GPUs or mismatched Taints/Tolerations. | Check node taints; increase cluster size or check for "zombie" pods holding GPU resources. |
| **Pod crashes immediately** | `OOMKilled` | Model weights exceeded the `resources.limits.memory` setting. | Increase memory limit or use a quantized model (e.g., 4-bit instead of 16-bit). |
| **Slow Startup** | `ContainerCreating` | Large image pull (10GB+) from a remote registry. | Use a local registry mirror or "pre-pull" images using a DaemonSet. |
| **Intermittent 503s** | `ReadinessProbe` failed | LLM engine is still loading weights into VRAM. | Increase `initialDelaySeconds` in the readiness probe to account for model loading time. |
| **CUDA Out of Memory** | `CrashLoopBackOff` (Application Error) | Batch size too large for the allocated GPU VRAM. | Reduce `max_model_len` or `max_num_seqs` in the vLLM configuration. |

---

### Advanced Scheduling for AI Stability

#### Taints and Tolerations

To prevent general-purpose workloads (like web servers) from occupying expensive GPU nodes, we use taints and tolerations:

- **Taint**: Marks a node to repel pods unless they have a matching toleration.
  `kubectl taint nodes gpu-node-1 ai-gpu=true:NoSchedule`

- **Toleration**: Added to the pod spec to allow it to land on a tainted node.

#### Resource Governance

In shared research environments, governance prevents resource starvation:

- **ResourceQuotas**: Sets hard limits on total resources (e.g., max 2 GPUs) per namespace.
- **LimitRanges**: Defines default and maximum constraints for individual pods.

#### Scaling and Observability

- **Horizontal Pod Autoscaling (HPA)**: Automatically adjusts pod counts based on CPU or custom metrics (e.g., GPU VRAM usage via KEDA).
- **Monitoring**: Using **Prometheus** and **Grafana** with the **NVIDIA Device Plugin** to track GPU utilization, VRAM usage, and thermal throttling.
- **Log Aggregation**: Using the **EFK/Loki stack** to capture CUDA errors and Python tracebacks across multiple pods.

### The Academic Perspective: SLURM vs. Kubernetes

In research centers, a fundamental divide exists between **Batch HPC (SLURM)** and **Cloud-native Orchestration (Kubernetes)**.

- **SLURM (Batch Queue)**: Designed for massive, tightly coupled numerical simulations. It uses a strict queueing model with wall-time limits and is optimized for bare-metal InfiniBand performance.
- **Kubernetes (Stateful Services)**: Designed for long-running APIs and microservices. While it can run batch jobs, its primary strength is maintaining a desired state for services.

Many modern labs adopt a **hybrid approach**: using SLURM for heavy training and Kubernetes for model serving and interactive AI development.

## Summary Checklist

- [ ] Distinguish between the Control Plane and Worker Nodes.
- [ ] Explain the la-layer architecture of a Pod, Deployment, and Service.
- [ ] Describe how `nvidia.com/gpu` resource limits trigger GPU-aware scheduling.
- [ ] Implement a PVC to mount model weights from shared storage.
- [ ] Apply a Taint to a node and a corresponding Toleration to an AI pod.
- [ ] Contrast the batch-oriented model of SLURM with the service-oriented model of Kubernetes.

## Assignments

!!! note "Assignment.1: Resource Requesting"
    Write a Kubernetes manifest for a pod that requests 1 GPU and 16Gi of memory. Explain what happens if no nodes with available GPUs exist in the cluster.
    
    ??? tip "Solution: Resource Requesting"
        In the `spec.containers[].resources.limits` section, add `nvidia.com/gpu: 1` and `memory: "16Gi"`. If no GPUs are available, the pod will remain in a `Pending` state, and the scheduler will log an "Insufficient nvidia.com/gpu" event.

!!! note "Assignment.2: Designing a Stable AI Service"
    Design a deployment for an LLM engine that uses a Taint to stay on a GPU node and a PVC to load model weights from a shared NFS.
    
    ??? tip "Solution: Stable AI Service"
        Combine a `PersistentVolumeClaim` for the weights, a `Deployment` with `resources.limits` for the GPU, and a `tolerations` block matching the node's taint (e.g., `key: "ai-gpu", operator: "Equal", value: "true"`).

!!! note "Assignment.3: Scaling for Traffic"
    Implement a Horizontal Pod Autoscaler (HPA) for an AI API that scales from 2 to 10 replicas when CPU utilization exceeds 70%.
    
    ??? tip "Solution: Scaling"
        Run `kubectl autoscale deployment ai-api --cpu-percent=70 --min=2 --max=10`.

!!! note "Assignment.4: Templating with Helm"
    Create a simple Helm chart for the `ai-api` deployment. Parametrize the number of replicas and the `LLM_ENDPOINT` environment variable. Demonstrate how to deploy it to "Dev" (1 replica) and "Prod" (5 replicas) using two different `values.yaml` files.
    
    ??? tip "Solution: Helm Templating"
        Create a `Chart.yaml` and a `templates/deployment.yaml`. Use `{{ .Values.replicaCount }}` and `{{ .Values.llmEndpoint }}` in the manifest. Use `helm install dev ./my-chart -f values-dev.yaml` and `helm install prod ./my-chart -f values-prod.yaml`.

!!! note "Assignment.5: Production Hardening"
    Apply a `PodDisruptionBudget` to the `ai-api` deployment to ensure that at least one replica is always available during node maintenance. Additionally, assign a `PriorityClass` to the `llm-engine` pod to ensure it is the last to be evicted if the node runs out of resources.
    
    ??? tip "Solution: Hardening"
        Create a `PodDisruptionBudget` with `minAvailable: 1` and a `PriorityClass` object. Add `priorityClassName: high-priority` to the `llm-engine` pod spec.

## References

- Kubernetes Documentation: [kubernetes.io/docs](https://kubernetes.io/docs/)
- NVIDIA Device Plugin for K8s: [github.com/NVIDIA/k8s-device-plugin](https://github.com/NVIDIA/k8s-device-plugin)
- Kubeflow Documentation: [kubeflow.org/docs](https://kubeflow.org/docs/)

## Self-Evaluation

??? note "What is the primary difference between a Pod and a Deployment?"
    A Pod is a single instance of a running container (or small group of containers), whereas a Deployment is a controller that manages a set of identical pods, ensuring a desired number of replicas are always running and handling rolling updates.

??? note "How does Kubernetes handle GPU requests for AI models?"
    Kubernetes uses resource limits (`resources.limits`) for `nvidia.com/gpu`. The scheduler identifies nodes with available GPUs and places the pod there, ensuring that hardware is not over-subscribed.

??? note "What is the purpose of a Kubernetes Service in an AI pipeline?"
    A Service provides a stable DNS name (e.g., `http://llm-service`) that allows different components (like an API and an LLM engine) to find and communicate with each other, regardless of pod restarts or IP changes.

??? note "Why are Taints and Tolerations critical in mixed-resource clusters?"
    They reserve expensive GPU nodes exclusively for AI workloads by preventing standard, non-GPU pods from being scheduled on them, which would otherwise waste specialized hardware.

??? note "How would you handle a secret HuggingFace token in a production cluster?"
    Create a Kubernetes Secret using `kubectl create secret generic hf-token --from-literal=token=xxx` and inject it into the container as an environment variable using the `secretKeyRef` field in the pod specification.

??? note "When should you use Helm instead of raw YAML manifests for AI deployments?"
    When you need to manage multiple environments (Dev, Staging, Prod) with different resource constraints (e.g., 1 GPU vs 8 GPUs) without duplicating manifests. Helm allows you to template these values in a `values.yaml` file.

??? note "What is the 'Reconciliation Loop' in the context of a Kubernetes Operator?"
    It is the continuous process where the Operator observes the current state of the cluster, compares it to the desired state defined in a Custom Resource (CR), and performs actions to align the two (Observe $\rightarrow$ Diff $\rightarrow$ Act).

??? note "What is the most likely cause of an `OOMKilled` status for an LLM pod, and how is it fixed?"
    It usually means the model weights or the KV cache exceeded the pod's memory limit. This is fixed by increasing the `resources.limits.memory` in the manifest or using a more heavily quantized version of the model.
