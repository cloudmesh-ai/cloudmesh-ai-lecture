# Getting Started with NVIDIA AI Pair

This guide covers the end-to-end process of setting up your first NVIDIA Personal AI Router (PAIR) cluster, managing the underlying inference engines, and operating the system via the terminal.

---

## 1. Installation and Initial Setup

### Installation
Download the appropriate asset from the [PAIR releases page](https://github.com/NVIDIA/Personal-AI-Router/releases).

- **Windows**: Run the Windows installer and launch from the Start menu.
- **Linux (Debian)**: Install via `sudo apt install ./NVPAIR-Setup-*.deb`.
- **macOS**: Drag the `.dmg` to Applications.
- **Headless/Source**: Extract the background services archive and run the binaries directly.

### The First-Run Workflow
Once installed, PAIR follows a five-step lifecycle to get you operational:

1. **Start**: Launch the application. This starts the **Broker**, which in turn supervises all background workers.
2. **Discover**: The nodes announce themselves on the local network and browse for peers.
3. **Pair**: Establish trust between nodes using a six-digit PIN. This bootstraps the mutual TLS (mTLS) certificates required for secure routing.
4. **Enable Engine**: Install or adopt an inference engine (Ollama or LM Studio) on the node.
5. **Prepare Model**: Download the specific LLM weights needed for your tasks.

---

## 2. Headless Operation: The Terminal Interface (TUI)

For servers, SSH sessions, or machines without a desktop environment, PAIR provides `nvpair-tui`.

### Starting the TUI
Ensure the desktop application is fully quit before starting the TUI to avoid port conflicts.
```bash
nvpair-tui
```

### Key Operations and Bindings
The TUI is a keyboard-driven interface. Navigate with `j` (down) and `k` (up).

#### Engine Management (Engines Tab)
Select an engine and use these keys:
- `i`: **Install** a new engine.
- `s`: **Start** the engine.
- `x`: **Stop** the engine.
- `r`: **Restart** the engine.
- `u`: **Uninstall** the engine.
- `p`: **Pull/Download** a model (opens a prompt for the model name, e.g., `llama3:8b`).

#### Routing and Health (Proxies & Workloads Tabs)
- **Proxies Tab**: View listening ports. Press `enter` to pin a proxy to a specific node, or `a` to return to **automatic routing**.
- **Workloads Tab**: Monitor live inference requests, seeing which model and engine are serving the job.
- **Logs Tab**: View real-time service logs. Use `d`, `i`, `w`, `e` to change the log level (Debug, Info, Warn, Error).

---

## 3. Engine and Model Lifecycle

It is critical to distinguish between the **Engine** (the software runtime) and the **Model** (the weight files).

### The Lifecycle Chain
| Action | Goal | Effect |
| :--- | :--- | :--- |
| **Install** | Get the runtime on the machine | Installs Ollama/LM Studio and starts the service. |
| **Start** | Make the runtime available | Marks the node as eligible to serve requests. |
| **Add Model** | Get weights onto the machine | Downloads the model files via the engine. |
| **Load** | Hold model in memory | Moves weights from disk to VRAM (required by some engines). |
| **Eject** | Free memory | Removes model from VRAM but keeps the files on disk. |
| **Delete** | Remove weights | Permanently deletes the model files from the machine. |

### Tips for Cluster Efficiency
- **Redundancy**: Put the same model on multiple nodes to make them interchangeable.
- **Optimization**: Use the TUI or Desktop app to "Eject" models not currently in use to free up VRAM for others.
- **Verification**: Always verify the **Endpoint URL** from the PAIR interface rather than assuming a default port.

---

## 4. Running Your First Inference

Once your cluster is paired and models are loaded, point your application to the PAIR local endpoint.

### Example: Using `curl` with an Ollama-compatible endpoint
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Why is NVIDIA PAIR useful for multi-agent systems?"
}'
```
PAIR will intercept this request, find the best node holding `llama3`, and stream the response back to you.

---

## 5. Maintenance and Updates

### Automatic Checks
PAIR checks for updates every six hours. It will notify you in the **Overview** tab when a new release is available.

### Update Procedure
1. **Download**: Click "Download update" in Settings $\rightarrow$ Service.
2. **Install**: Click "Restart & install".
3. **Consistency**: Update **every node** in the cluster to the same version to avoid unstable behavior.

### Troubleshooting common issues
- **No nodes appearing?** Check firewall rules for the discovery ports.
- **Pairing stalled?** Ensure both nodes are on the same subnet and can reach each other.
- **Model not found?** Check that the model was successfully pulled and the engine is currently **Running**.


https://build.nvidia.com/playbooks/pair


## spark

wget https://github.com/NVIDIA/Personal-AI-Router/releases/download/v0.1.1/NVPAIR-Setup-0.1.1-arm64.deb

sudo apt install ./NVPAIR-Setup-0.1.1-arm64.deb

ollama:
docker pull ghcr.io/open-webui/open-webui:ollama
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama


docker run -d --gpus all \
  -p 12000:8080 \
  -v ollama:/root/.ollama \
  -v open-webui:/app/backend/data \
  --name spark-ai \
  --restart always \
  ghcr.io/open-webui/open-webui:ollama


## white

wget https://github.com/NVIDIA/Personal-AI-Router/releases/download/v0.1.1/NVPAIR-Setup-0.1.1-amd64.deb
sudo apt install ./NVPAIR-Setup-0.1.1-amd64.deb


##test for install  

dpkg -l | grep nvpair
ii  nvpair                                        0.1.1-463                                        amd64        

## spark

On the **NVIDIA DGX Spark** (powered by the GB10 Grace Blackwell Superchip with **128 GB of unified memory**), your model choice depends on whether you want a fast general workhorse, a specialized coding/agent model, or a deep-reasoning heavyweight.

Because you have 128 GB of VRAM, you have a massive amount of headroom, allowing you to run multiple concurrent models or comfortably host larger 30B–70B parameter models.

The best models to pull into Ollama for deployment via NVIDIA PAIR include:

### 1. The Best All-Around Coding & Agent Workhorse

* **Model:** `qwen3-coder-next` (or `Qwen3-Coder`)
* **Quantization:** `q4_K_M`
* **VRAM footprint:** ~20 GB
* **Why it shines:** It hits an incredible sweet spot (~47 tokens/sec on the DGX Spark). It provides exceptional structured data output and robust tool-calling reliability, making it ideal if you are using AI coding assistants or automated agents.

### 2. The Best Multimodal / Vision Companion

* **Model:** `qwen3-vl:30b`
* **VRAM footprint:** ~19 GB
* **Why it shines:** Running alongside your primary coder model, this gives your setup native image understanding and vision capabilities while leaving plenty of VRAM headroom in reserve.

### 3. The Best Heavyweight General / Reasoning Option

* **Model:** `Llama 3.3 70B Instruct` or `DeepSeek-R1` (Distilled variants like 32B or full quantized 70B-class)
* **Quantization:** `Q4_K_M` or `FP4`
* **VRAM footprint:** ~43 GB to 60 GB
* **Why it shines:** Leverages the Blackwell architecture's native 4-bit precision performance to run massive reasoning models locally at very usable speeds (around 3 to 7+ tokens/sec for 70B+ classes).

---

### Quick Recommendation to Start

To get up and running immediately with great performance and low latency through your PAIR setup, pull a fast mid-sized model first:

```bash
ollama run qwen2.5:14b

```

*(or your preferred variant depending on your exact workflow needs)*

---

## white

With an Ubuntu desktop featuring an **RTX 3090 (24 GB VRAM)** and **128 GB of system RAM**, your setup hits a fantastic sweet spot.

Because your VRAM is restricted to 24 GB, but your system RAM is massive (128 GB), you have two distinct paths: **Maximum Speed** (keeping the model 100% inside the RTX 3090's VRAM) or **Maximum Capability** (spilling over into system RAM or running larger quantized models).

The ideal model choices for your hardware split cleanly into these categories:

---

### Tier 1: The Absolute Sweet Spot (100% in VRAM, Maximum Speed)

*If you want blazing-fast inference (25–35+ tokens/second) without any CPU offloading bottlenecks, keep your models under ~18–20 GB.*

* **The Best All-Around / Coding Model:** **`qwen3.6:27b`** or **`qwen2.5-coder:32b`** (at `Q4_K_M` quantization, taking ~17–20 GB).
* *Why:* This is widely considered the ultimate daily driver for a single 24 GB card. It handles complex coding, logic, and multi-file workflows natively in VRAM.


* **The Best Reasoning Model:** **`deepseek-r1:32b`** (at `Q4_K_M`, taking ~20 GB).
* *Why:* Gives you top-tier step-by-step logic and mathematical reasoning entirely on the GPU.



---

### Tier 2: The Capacity Stretch (Using System RAM for 70B+ Models)

*Because you have 128 GB of system RAM, you are not strictly capped at 32B models. You can load larger models using partial GPU offloading (or via llama.cpp/Ollama splitting layers between your RTX 3090 and system RAM).*

* **The Best Heavyweight General Model:** **`llama3.3:70b`** or **`deepseek-r1:70b`** (at `Q4_K_M` quantization, taking ~43–48 GB total).
* *Why:* Since a 70B 4-bit model requires ~45 GB, it won't fit entirely inside your 24 GB VRAM. However, your 128 GB system RAM easily holds the rest. Ollama will offload as many layers as possible to the RTX 3090 and run the remaining layers on your system RAM.
* *The Tradeoff:* It will be noticeably slower than Tier 1 (dropping down to roughly 5–12 tokens/sec depending on your system RAM bandwidth), but it grants you access to full 70B-class intelligence locally.



---

### Recommendation on How to Run Them via Ollama

To test the blazing-fast VRAM sweet spot first, pull the top-tier 27B/32B class:

```bash
ollama run qwen3.6:27b

```

If you want to test a massive model and let your 128 GB system RAM absorb the spillover:

```bash
ollama run llama3.3:70b

```

---

# mac

. The Sweet Spot (Best Balance of Intelligence & Speed)Models: qwen2.5:32b or deepseek-r1:32b (DeepSeek-R1-Distill-Qwen-32B)RAM Footprint: ~20GB – 22GB (Q4)Why: These run at blazing-fast token rates on Apple Silicon while offering reasoning and coding capabilities that punch way above their weight class. They leave plenty of memory free for background services like NVIDIA PAIR or IDE coding assistants.Command:Bashollama run qwen2.5:32b
# or
ollama run deepseek-r1:32b
2. The Heavyweights (Pushing 64GB to the Limit)Models: llama3.1:70b or deepseek-r1:70b (DeepSeek-R1-Distill-Llama-70B)RAM Footprint: ~40GB – 43GB (Q4_K_M)Why: A 70B model at 4-bit quantization will fit inside your 64GB Mac, leaving around 10–15GB for the OS. You get near-GPT-4 level reasoning locally, though token generation speeds will be noticeably slower than the 32B tier.Command:Bashollama run llama3.1:70b
# or
ollama run deepseek-r1:70b
3. The Speed Demons (Coding & Fast Agents)Models: qwen2.5-coder:7b or llama3.1:8bRAM Footprint: ~5GB – 6GBWhy: Perfect if you are pairing Ollama with IDE extensions or CLI tools where response latency needs to be instant.Command:Bashollama run qwen2.5-coder:7b

Here is a quick-reference summary table outlining the recommended Ollama models tailored for your M1 Max 64GB setup, factoring in memory footprint and expected token generation throughput based on the M1 Max's ~400 GB/s unified memory bandwidth.

| Model / Tag | Quantization | RAM Footprint | Expected Speed (Tokens/sec) | Best Use Case |
| --- | --- | --- | --- | --- |
| **`qwen2.5-coder:7b`** | Q4_K_M | ~5 GB | **80 – 100+ t/s** | Instant-response coding assistants, CLI tools, and background agent hooks. |
| **`qwen2.5:32b`** / **`deepseek-r1:32b`** | Q4_K_M | ~20 – 22 GB | **30 – 40 t/s** | **The Sweet Spot:** Excellent reasoning and coding capabilities with snappy output. |
| **`llama3.1:70b`** / **`deepseek-r1:70b`** | Q4_K_M | ~40 – 43 GB | **10 – 15 t/s** | **Heavyweight Reasoning:** Near-GPT-4 tier logic; maxes out the safe operational window inside your 64GB limit. |

---

### Quick Deployment Commands

To pull and run any of these directly in your terminal, use:

```bash
ollama run qwen2.5-coder:7b
ollama run qwen2.5:32b
ollama run deepseek-r1:70b

```

Yes! The **Qwen3** generation (and its subsequent iterations like **Qwen3.5** and **Qwen3.8**) represents a massive leap forward from the older 2.5 variants.

The newer models introduce **native reasoning modes** (built-in step-by-step "thinking" capabilities comparable to reasoning models like DeepSeek-R1), much wider context windows (up to 256K), and highly efficient Mixture-of-Experts (MoE) architectures.

Here is how the modern **Qwen3** lineup maps out for your 64GB M1 Max setup:

### How to Run Them with Ollama

Ollama supports Qwen3 out of the box. You can pull and run the models directly:

```bash
# Pull and run the efficient MoE 30B variant (great balance of speed and intelligence)
ollama run qwen3:30b-a3b

# Or run the standard 32B dense model
ollama run qwen3:32b

```

*Note on Reasoning:* Qwen3 models run in a **thinking mode** by default, letting you see their step-by-step logic. If you want faster, direct responses without the inner monologue stream, you can toggle it off or use specific flags depending on your wrapper.

Here is the updated table for the modern **Qwen3** lineup, incorporating estimated token generation throughput explicitly calibrated for your **M1 Max 64GB** (which delivers roughly **400 GB/s** of unified memory bandwidth):

| Model Tag | Type | RAM Footprint (Q4) | Expected Speed on M1 Max (Tokens/sec) | Best Use Case |
| --- | --- | --- | --- | --- |
| **`qwen3:8b`** | Dense | ~5.2 GB | **75 – 90 t/s** | Daily driver, instant-response coding assistants, and rapid text generation. |
| **`qwen3:30b-a3b`** | MoE (Mixture of Experts) | ~19 GB | **45 – 60 t/s** | **The Speed/Intelligence Sweet Spot:** Because it only activates a fraction of its parameters per token, it runs much faster than a standard 30B dense model. |
| **`qwen3:32b`** | Dense | ~20 GB | **22 – 30 t/s** | Heavy-duty reasoning, complex logic, and deep analytical coding. |

# spark

Here is a comparable Ollama model performance and footprint table calibrated for the **NVIDIA DGX Spark** (Grace Blackwell architecture equipped with ultra-fast HBM3e VRAM, such as 192GB+ per GPU and massive memory bandwidth).

Unlike a consumer Mac, the DGX Spark can run multi-tens-of-billions parameter models at **native FP8 or unquantized precision** (or handle gigantic 120B+ models entirely in high-bandwidth VRAM) with blistering execution speeds.

| Model Tag | Type & Precision | VRAM Footprint | Expected Speed on Spark (Tokens/sec) | Best Use Case |
| --- | --- | --- | --- | --- |
| **`qwen3:32b`** | Dense (FP16 / Native) | ~64 GB | **150 – 200+ t/s** | Blazing-fast, uncompressed dense reasoning and coding with zero quantization loss. |
| **`deepseek-r1:70b`** / **`qwen3:70b`** | Dense (FP8 / Quantized) | ~75 – 80 GB | **90 – 130 t/s** | Enterprise-grade multi-step logic, complex research synthesis, and advanced agentic workflows. |
| **`llama3.1:70b`** | Dense (FP16 / Native) | ~140 GB | **60 – 85 t/s** | Full-precision 70B model execution entirely in HBM3e VRAM for maximum fidelity. |
| **Large MoE / 120B+ Models** | Mixture of Experts / Large Scale | ~150 – 180 GB | **40 – 60 t/s** | Pushing the 192GB VRAM boundary for near-frontier intelligence across massive multi-domain tasks. |

Here is the performance and footprint table calibrated for a powerful AI workstation featuring an **NVIDIA RTX 3090 (24GB VRAM)** paired with **128GB System RAM**.

On this setup, model execution speed is largely determined by whether the model fits entirely within the RTX 3090's ultra-fast 24GB VRAM or whether it overflows into the 128GB system RAM via PCIe offloading.

| Model Tag | Type & Quantization | Memory Footprint (VRAM / RAM Split) | Expected Speed on RTX 3090 (Tokens/sec) | Best Use Case |
| --- | --- | --- | --- | --- |
| **`qwen3:8b`** | Dense (FP16 or Q4) | ~5 GB to 16 GB (VRAM only) | **80 – 110+ t/s** | Blazing-fast daily coding assistants, agent loops, and instant responses. |
| **`qwen3:30b-a3b`** / **`qwen3:32b`** | MoE / Dense (Q4_K_M) | ~17 GB to 20 GB (VRAM only) | **35 – 50 t/s** | **The VRAM Sweet Spot:** Fits entirely inside the 24GB VRAM boundary, delivering high intelligence without PCIe bottleneck penalties. |
| **`llama3.1:70b`** / **`deepseek-r1:70b`** | Dense (Q4_K_M) | ~43 GB (24GB VRAM + 19GB Sys RAM) | **12 – 18 t/s** | Advanced multi-step reasoning where system RAM handles overflow, trading top speed for massive model capability. |

---

### Key Workstation Architecture Note:

* **The 24GB VRAM Wall:** Any model totaling under 24GB (like the 30B/32B Q4 models) runs at maximum GPU speeds because all weights stay locked inside the RTX 3090's GDDR6X memory (~936 GB/s bandwidth).
* **The PCIe Threshold:** Once a model exceeds 24GB (like a 70B model), Ollama splits the layers between the GPU and your 128GB system RAM. While your 128GB RAM ensures the model easily fits, token generation speeds will drop because data must cross the PCIe bus.

### COMBINED



With the **NVIDIA DGX Spark** (featuring the GB10 Grace Blackwell superchip and **128GB of coherent unified memory**), your hardware profile changes dramatically. Because it relies on a unified memory architecture over LPDDR5X, it functions similarly to a massive Mac Studio/MacBook Pro on steroids—allowing you to comfortably fit and run massive models that would normally require a multi-GPU data center node locally on your desk.

Here is how the optimal model selection shapes up across all three of your environments:

| Hardware Platform | Core Architecture & Memory | Recommended Optimal Model | Expected Performance | Strategic Role in Your Workflow |
| --- | --- | --- | --- | --- |
| **MacBook Pro M1 Max** | 64GB Unified Memory 

 (~400 GB/s Bandwidth) | `qwen3:30b-a3b-instruct-2507` | **50 – 65 t/s** | **Portable Daily Driver:** Lightning-fast local coding loops, quick scripts, and field testing with ample Mac memory headroom. |
| **Workstation** | 128GB RAM + RTX 3090 

 (24GB VRAM + PCIe RAM) | `qwen3:32b` (VRAM-only) 

 *or* `deepseek-r1:70b` (Hybrid) | **35 – 50 t/s** (32B) 

 **12 – 18 t/s** (70B) | **Stationary Compute Node:** Blazing VRAM speed for dense 32B models, or background overflow handling for 70B reasoning. |
| **NVIDIA DGX Spark** | GB10 Grace Blackwell 

 128GB Unified Memory | **`deepseek-r1:70b`** 

 *(or large 100B+ MoE variants)* | **25 – 40 t/s** *(Native / FP4-optimized)* | **The Frontier Desktop Supercomputer:** Easily houses heavy 70B+ enterprise reasoning and multi-hundred-billion parameter models locally in unified memory without data-center footprint constraints. |

---

### Summary Workflow Recommendation

* Use your **M1 Max Mac** for agile, high-speed coding and mobile tasks (`30b-a3b`).
* Use your **RTX 3090 Workstation** for local server workloads and VRAM-bound 32B execution.
* Use the **DGX Spark** when you need to push into massive **70B+ frontier models** that require deep, complex logic execution entirely inside a dedicated, compact desktop AI powerhouse.



With the **NVIDIA DGX Spark** (featuring the GB10 Grace Blackwell superchip and **128GB of coherent unified memory**), your hardware profile changes dramatically. Because it relies on a unified memory architecture over LPDDR5X, it functions similarly to a massive Mac Studio/MacBook Pro on steroids—allowing you to comfortably fit and run massive models that would normally require a multi-GPU data center node locally on your desk.

Here is how the optimal model selection shapes up across all three of your environments:

| Hardware Platform | Core Architecture & Memory | Recommended Optimal Model | Expected Performance | Strategic Role in Your Workflow |
| --- | --- | --- | --- | --- |
| **MacBook Pro M1 Max** | 64GB Unified Memory 

 (~400 GB/s Bandwidth) | `qwen3:30b-a3b-instruct-2507` | **50 – 65 t/s** | **Portable Daily Driver:** Lightning-fast local coding loops, quick scripts, and field testing with ample Mac memory headroom. |
| **Workstation** | 128GB RAM + RTX 3090 

 (24GB VRAM + PCIe RAM) | `qwen3:32b` (VRAM-only) 

 *or* `deepseek-r1:70b` (Hybrid) | **35 – 50 t/s** (32B) 

 **12 – 18 t/s** (70B) | **Stationary Compute Node:** Blazing VRAM speed for dense 32B models, or background overflow handling for 70B reasoning. |
| **NVIDIA DGX Spark** | GB10 Grace Blackwell 

 128GB Unified Memory | **`deepseek-r1:70b`** 

 *(or large 100B+ MoE variants)* | **25 – 40 t/s** *(Native / FP4-optimized)* | **The Frontier Desktop Supercomputer:** Easily houses heavy 70B+ enterprise reasoning and multi-hundred-billion parameter models locally in unified memory without data-center footprint constraints. |

---

### Summary Workflow Recommendation

* Use your **M1 Max Mac** for agile, high-speed coding and mobile tasks (`30b-a3b`).
* Use your **RTX 3090 Workstation** for local server workloads and VRAM-bound 32B execution.
* Use the **DGX Spark** when you need to push into massive **70B+ frontier models** that require deep, complex logic execution entirely inside a dedicated, compact desktop AI powerhouse.


| Hardware Platform | Core Architecture & Memory | Recommended Optimal Model | Expected Performance | Strategic Role in Your Workflow |
| --- | --- | --- | --- | --- |
| **MacBook Pro M1 Max** | 64GB Unified Memory | Hardware Platform | Core Architecture & Memory | Recommended Optimal Model | Expected Performance | Strategic Role in Your Workflow |
| --- | --- | --- | --- | --- |
| **MacBook Pro M1 Max** | 64GB Unified Memory  (~400 GB/s Bandwidth) | `qwen3:30b-a3b-instruct-2507` | **50 – 65 t/s** | **Portable Daily Driver:** Lightning-fast local coding loops, quick scripts, and field testing with ample Mac memory headroom. |
| **Workstation** | 128GB RAM + RTX 3090 (24GB VRAM + PCIe RAM) | `qwen3:32b`(VRAM-only)  *or* `deepseek-r1:70b` (Hybrid) | **35 – 50 t/s** (32B) **12 – 18 t/s** (70B) | **Stationary Compute Node:** Blazing VRAM speed for dense 32B models, or background overflow handling for 70B reasoning. |
| **NVIDIA DGX Spark** | GB10 Grace Blackwell  128GB Unified Memory | `deepseek-r1:70b`  *(or large MoE variants)* | **25 – 40 t/s** *(FP4 / Native optimized)* | **The Frontier Desktop Supercomputer:** Easily houses heavy 70B+ enterprise reasoning and multi-hundred-billion parameter models locally in unified memory. | (~400 GB/s Bandwidth) | `qwen3:30b-a3b-instruct-2507` | **50 – 65 t/s** | **Portable Daily Driver:** Lightning-fast local coding loops, quick scripts, and field testing with ample Mac memory headroom. |
| **Workstation** | 128GB RAM + RTX 3090 (24GB VRAM + PCIe RAM) | `qwen3:32b` (VRAM-only) *or* `deepseek-r1:70b` (Hybrid) | **35 – 50 t/s** (32B)  **12 – 18 t/s** (70B) | **Stationary Compute Node:** Blazing VRAM speed for dense 32B models, or background overflow handling for 70B reasoning. |
| **NVIDIA DGX Spark** | GB10 Grace Blackwell  128GB Unified Memory | `deepseek-r1:70b`  *(or large MoE variants)* | **25 – 40 t/s** *(FP4 / Native optimized)* | **The Frontier Desktop Supercomputer:** Easily houses heavy 70B+ enterprise reasoning and multi-hundred-billion parameter models locally in unified memory. |