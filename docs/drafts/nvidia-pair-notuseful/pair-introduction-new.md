# NVIDIA AI Pair: Comprehensive Architectural Overview

## 1. What is NVIDIA AI Pair?

**NVIDIA AI Pair (Personal AI Router)** is a decentralized control plane and workload traffic controller designed for multi-agent AI systems. It transforms a collection of independent machines on a local network into a unified inference resource.

Crucially, AI Pair is **not** a GPU-pooling technology. It does not merge VRAM or combine GPUs into a single larger logical device. Instead, it acts as an intelligent **Proxy** that intercepts requests from your applications and routes them to the most appropriate node in your network based on model availability and current hardware utilization.

To your applications, AI Pair presents a single local endpoint that looks exactly like the inference engine they already speak to (e.g., Ollama or LM Studio), allowing existing tools to work unchanged while gaining the power of a multi-node cluster.

---

## 2. Core Concepts and Vocabulary

To understand how AI Pair operates, it is essential to use the following standardized terminology:

| Term | Definition |
| :--- | :--- |
| **Node** | A single machine running PAIR. Every node runs the same software; there is no "master" or "primary" node. |
| **Cluster** | The set of nodes paired together. Membership is symmetric; a node belongs to at most one cluster. |
| **Engine** | The local inference server (e.g., Ollama, LM Studio) that actually runs the models. |
| **Model** | The specific LLM weights hosted on an engine. Models are not shared; a node must hold the model locally to serve it. |
| **Endpoint** | The local URL your apps use. It remains constant regardless of which node eventually serves the request. |
| **Proxy** | The component behind the endpoint that accepts requests, selects the best node, and streams the response back. |
| **Job (Workload)** | A single routed request. The system tracks these as "jobs" for monitoring and telemetry. |
| **Broker** | The parent service on each node (`nvpair-ui-broker`) that supervises all other workers and exposes the JSON-RPC API. |

---

## 3. Detailed Architecture

### The Symmetric Peer-to-Peer Model
Unlike traditional server-client architectures, PAIR uses a **Symmetric Clustering** approach. Every node is an equal peer. This removes the single point of failure and allows any node to act as the entry point for an application.

### Process Architecture
The system is split into a frontend (Desktop or TUI) and a backend of Go-based services. The **Broker** is the heart of the node, supervising a fleet of specialized workers:
- **Proxies (`ollama-proxy`, `lmstudio-proxy`)**: Handle the actual HTTP traffic and routing.
- **Scanner & Info (`node-scanner`, `node-info`)**: Handle LAN discovery and host telemetry.
- **Engine Manager**: Manages the installation and lifecycle of Ollama/LM Studio.
- **Cluster Manager**: Handles identity, pairing, and mutual TLS trust.
- **Job Scheduler**: Tracks pending work and priority snapshots across the node.

### The Routing Lifecycle
1. **Discovery**: Nodes announce themselves on the LAN.
2. **Pairing**: Users use a six-digit PIN to bootstrap trust and establish mutual TLS certificates.
3. **Interception**: PAIR intercepts the standard ports used by inference engines.
4. **Routing Decision**: When a request arrives, the Proxy checks:
   - Which nodes in the cluster are online?
   - Which nodes have the requested model loaded?
   - Which node has the lowest current GPU utilization?
5. **Dispatch**: The request is forwarded to the optimal node, and the result is streamed back to the user.

---

## 4. Hard Architectural Boundaries (What PAIR Does NOT Do)

Understanding the limits of PAIR is critical for proper infrastructure planning:

- **No VRAM Pooling**: If you have two nodes with 24GB VRAM, you **cannot** run a 40GB model. The model must fit entirely within one node's memory.
- **No Model Sharding**: PAIR does not split a single model's weights across the network.
- **No In-Flight Migration**: A request cannot be moved to a different node once it has started running.
- **No Model Storage**: PAIR does not store models; it only manages the engines that do.
- **No Latency Reduction**: Adding nodes increases **throughput** (how many requests you can handle at once) but does not make a single individual request process faster.

---

## 5. Strategic Application: When to Use and Avoid

### Use AI Pair when:
- **Powering Multi-Agent Systems**: When your application triggers multiple independent agents (coding, research, review) simultaneously.
- **Utilizing Heterogeneous Hardware**: When you want to leverage a mix of high-end (DGX Blackwell) and mid-range (RTX 3090) hardware in one cluster.
- **Scaling Inference Capacity**: When you need to increase the total tokens-per-second your local infrastructure can produce.

### Avoid AI Pair when:
- **Model Size exceeds Hardware**: When your target model is larger than your biggest single GPU's memory. (In this case, you need Tensor Parallelism/Sharding, not a router).
- **Extreme Low-Latency Requirements**: When you only ever send one prompt and the slight overhead of a proxy is unacceptable.

---

## 6. Networking and Hardware Integration

### Security and Trust
PAIR uses a **Zero-Trust-ish** approach for local networks. While discovery is open, the actual routing of inference traffic is restricted to paired nodes using **mutual TLS (mTLS)**. This ensures that only authorized machines in your cluster can exchange sensitive AI prompts.

### The Grace Blackwell (DGX Spark) Advantage
While PAIR manages the routing *between* nodes, the hardware *inside* the node determines the capacity.
- **Discrete GPU Nodes (RTX)**: Limited by VRAM and PCIe bandwidth.
- **Unified Memory Nodes (Grace Blackwell)**: Because the CPU and GPU share a massive, high-speed memory pool, a single DGX Spark node can host models with hundreds of billions of parameters. In a PAIR cluster, these nodes act as the "super-nodes," handling the most complex, memory-intensive requests while smaller RTX nodes handle the lighter, faster tasks.
