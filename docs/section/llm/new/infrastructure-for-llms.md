# Infrastructure for Large Language Models (LLMs)

## Learning Objectives

!!! info "Learning Objectives"
    * Design compute clusters utilizing GPU nodes and inference-optimized VMs.
    * Evaluate storage strategies for model artifacts, vector databases, and feature stores.
    * Configure secure networking using private endpoints, VPC peering, and service meshes.
    * Analyze the trade-offs between reserved, spot, and serverless compute provisioning.

## Overview

Deploying Large Language Models (LLMs) at scale requires a fundamental shift in how infrastructure is architected. Unlike traditional microservices that are primarily CPU-bound and have relatively small memory footprints, LLM workloads are characterized by extreme demands on compute (GPU/TPU), massive memory requirements (VRAM), and high-throughput, low-latency networking needs.

This chapter explores the architectural components required to support the entire LLM lifecycle: from training and fine-tuning to high-performance inference.

## Compute Infrastructure

Compute for LLMs is divided into two primary phases: Training/Fine-tuning (compute-intensive, long-running) and Inference (latency-sensitive, request-driven).

### GPU Architectures and Selection

The Graphics Processing Unit (GPU) is the cornerstone of LLM infrastructure due to its ability to perform massive parallel matrix multiplications.

#### NVIDIA GPUs (CUDA Ecosystem)
NVIDIA's strength lies in its **CUDA** (Compute Unified Device Architecture) platform, which provides a mature software stack for deep learning.

*   **NVIDIA H100 (Hopper):** Optimized for training and large-scale inference. It introduces the "Transformer Engine," which uses FP8 precision to accelerate training and inference without significant loss in accuracy. High HBM3 bandwidth makes it suitable for the largest models.
*   **NVIDIA A100 (Ampere):** A versatile GPU with Multi-Instance GPU (MIG) capabilities, allowing a single A100 to be partitioned into multiple smaller GPUs for lighter workloads.
*   **NVIDIA T4 / L4:** Optimized for inference. These are lower-power, lower-cost GPUs designed to handle smaller models or quantized versions of larger models.

#### Selection Criteria

When choosing a GPU, the primary constraint is often VRAM (Video RAM). An LLM's weights must reside in VRAM for fast access.

*   **Memory Calculation:** A model with 70 billion parameters in FP16 precision requires $70 \times 2$ bytes $\approx 140$ GB of VRAM just to load the weights. This necessitates multi-GPU setups (model parallelism).
*   **Compute Throughput:** Training requires high FLOPS (Floating Point Operations Per Second), whereas inference is often memory-bandwidth bound (the speed at which weights can be moved from VRAM to the compute cores).

### Provisioning Strategies

GPU resources are expensive and scarce, necessitating strategic procurement.

*   **Reserved Instances:** Essential for training clusters. Guaranteed availability over 1-3 years in exchange for a commitment. This prevents capacity errors during critical training runs.
*   **Spot Instances:** Ideal for non-critical batch processing or fault-tolerant fine-tuning. These offer significant discounts but can be reclaimed by the provider at any time.
*   **Node Pools:** In Kubernetes (K8s), LLM workloads should be isolated into dedicated GPU node pools using Taints and Tolerations. This ensures that non-GPU workloads do not occupy expensive GPU nodes.

### Serverless and Managed Inference

For many organizations, managing raw GPU clusters is too complex.

*   **Inference as a Service (IaaS):** Services like Cloud Run (with GPU support) or AWS SageMaker Inference. These abstract the underlying VM, allowing developers to deploy a container that scales to zero when not in use.
*   **AWS Lambda with SageMaker:** While Lambda itself cannot run large LLMs, it can act as the orchestration layer, calling SageMaker endpoints.
*   **The Trade-off:** Serverless reduces operational overhead but introduces "Cold Starts"—the delay when a new container must be spun up and the model weights must be loaded into VRAM.

## Storage Architecture

LLM storage is focused on the velocity of data movement.

### Model Artifact Storage

Model weights (checkpoints) are massive blobs.

*   **Object Storage (S3, GCS, Azure Blob):** The primary repository for model weights.
*   **The Bottleneck:** Loading a 100GB model from S3 to a GPU node over a standard network can take minutes.
*   **Optimization:** Use Regional Endpoints to keep storage and compute in the same zone and employ Parallel Downloads or specialized filesystems (like FSx for Lustre) to saturate the network interface.

### Vector Databases

Retrieval Augmented Generation (RAG) requires storing document embeddings in a way that allows for efficient similarity searches.

#### Popular Vector DBs

*   **Pinecone:** A managed, cloud-native vector database optimized for low-latency retrieval at scale.
*   **Milvus:** An open-source, highly scalable vector database designed for billion-scale vectors.
*   **Elasticsearch / OpenSearch (k-NN):** Leverages existing search infrastructure by adding k-Nearest Neighbor (k-NN) indexing. Ideal for hybrid search (combining keyword search with semantic vector search).

#### Why Vector DBs?

Traditional SQL databases are designed for exact matches. Vector DBs use algorithms like HNSW (Hierarchical Navigable Small World) to perform Approximate Nearest Neighbor (ANN) searches, finding the closest meaning in a high-dimensional space in milliseconds.

### Feature Stores

For LLMs integrated into production ML pipelines, Feature Stores (e.g., Feast, Tecton) ensure that the data used during training (offline) is the exact same data used during inference (online), preventing training-serving skew.

## Networking and Security

Networking for LLMs must balance the need for massive data throughput with strict security boundaries.

### Secure Connectivity

LLMs often handle sensitive corporate data, making public internet exposure unacceptable.

*   **Private Endpoints (AWS PrivateLink / Azure Private Link):** Allows the application to communicate with the LLM API over the provider's private backbone, never leaving the internal network.
*   **VPC Peering:** Used to connect the compute VPC (where GPUs live) with the data VPC (where vector DBs and object storage live) with minimal latency.
*   **Firewalls and Security Groups:** Strict egress filtering is required to prevent data exfiltration where a compromised model or prompt-injection attack attempts to send data to an external server.

### Service Mesh and Traffic Management

As LLM architectures evolve into Agentic workflows (multiple models calling each other), networking complexity increases.

*   **Istio / Linkerd (Service Mesh):**
    *   **mTLS:** Ensures all communication between the application, the orchestrator, and the model is encrypted.
    *   **Observability:** Provides detailed telemetry on request latency and error rates for specific model versions.
*   **Rate-Limiting Gateways:**
    *   **Why:** LLM APIs are expensive and have strict token limits (TPM - Tokens Per Minute).
    *   **Mechanism:** A gateway (e.g., Kong, Apigee) implements leaky bucket or token bucket algorithms to prevent a single user from exhausting the organization's entire quota.

## Summary Checklist

*   [ ] GPU selection based on VRAM requirements and model precision.
*   [ ] Provisioning strategy aligned with workload (Reserved for training, Spot for batch).
*   [ ] GPU node isolation in Kubernetes using Taints and Tolerations.
*   [ ] Model artifact loading optimized via Regional Endpoints.
*   [ ] Vector database selected based on scale and search type (ANN vs. Exact).
*   [ ] Private connectivity established via PrivateLink or VPC Peering.
*   [ ] Rate-limiting implemented at the gateway to manage token quotas.

## Assignments

!!! note "Assignment.1: Compute Sizing"
    Calculate the minimum VRAM required to load a 175B parameter model using FP16 precision. Determine how many NVIDIA A100 (80GB) GPUs are required for the weights alone, ignoring KV cache and activation memory.

    ??? tip "Solution: Compute Sizing"
        A 175B model in FP16 (2 bytes per parameter) requires $175 \times 2 = 350$ GB. 
        $350 / 80 = 4.375$. 
        Minimum 5 A100 (80GB) GPUs are required.

!!! note "Assignment.2: RAG Storage Design"
    Design a storage architecture for a corporate knowledge base containing 10 million documents. Specify the choice of Vector DB and the method for updating embeddings when documents change.

    ??? tip "Solution: RAG Storage Design"
        For 10 million documents, a scalable solution like Milvus or Pinecone is recommended. 
        Architecture:
        1. Object Storage (S3) for raw documents.
        2. Embedding Pipeline (Lambda + LLM) to convert text to vectors.
        3. Vector DB (Milvus) for ANN search.
        4. Update mechanism: Implement a versioning system in the metadata. When a document is updated in S3, trigger a webhook to re-embed the document and perform an `upsert` operation in the Vector DB using the document ID.

## References

*   NVIDIA Hopper Architecture Whitepaper.
*   AWS SageMaker Inference Documentation.
*   Pinecone Vector Database Documentation.
*   Milvus Documentation.
*   Istio Service Mesh Documentation.

## Self-Evaluation

??? note "Why is VRAM the primary constraint when selecting GPUs for LLMs?"
    LLM weights must be loaded into VRAM to achieve the memory bandwidth necessary for fast inference and training. If the model weights exceed the available VRAM, the system must either use model parallelism across multiple GPUs or swap to system RAM (CPU), which causes a massive drop in performance.

??? note "What is the difference between a standard SQL database and a Vector Database in the context of LLMs?"
    SQL databases perform exact match or range queries. Vector databases store embeddings (high-dimensional vectors) and use Approximate Nearest Neighbor (ANN) algorithms, such as HNSW, to find documents with the most similar semantic meaning, even if they share no exact keywords.

??? note "How does a Rate-Limiting Gateway protect LLM infrastructure?"
    LLM APIs often have strict Tokens Per Minute (TPM) and Requests Per Minute (RPM) limits. A gateway prevents a single user or service from consuming the entire quota through techniques like token bucket algorithms, ensuring fair usage and preventing service outages.
