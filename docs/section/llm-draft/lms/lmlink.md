
---

# Unified Multi-Tier LLM Cluster Architecture & Deployment Guide (Daemon-Free)

Requirement: 

* deamon free
* running LM Studio in foreground or interactive mode rather than background system daemons across your four compute tiers.


## 1. System Architecture Overview

Your environment is structured into **four distinct compute tiers** controlled centrally from your M1 MacBook Pro, leveraging LM Link, secure SSH tunneling, and standard OpenAI-compatible endpoints without relying on background system daemons.

```text
                                +-----------------------------------+
                                |          M1 MacBook Pro           |
                                |     (Client Control Machine)      |
                                +-----------------------------------+
                                   /       |              \           \      
         [LM Link / Mesh]         /        | [Localhost]   \           \ [HTTPS API]
        +------------------------+         |                \           \
        v                                  v                 v           v
+------------------------+      +------------------------+  +------------------------+  +------------------------+
|   NVIDIA DGX Spark     |      |   Linux + RTX 3090     |  | Remote 2x/4x A100 Node |  |    Jetstream Cloud     |
| (LM Studio / Desktop)  |      | (LM Studio / Desktop)  |  | (Proxy via port 17704) |  | (llm.jetstream-cloud)  |
+------------------------+      +------------------------+  +------------------------+  +------------------------+
        \                                 /                         
         \                               / [Localhost Aggregator]   
          v                             v                           
        +---------------------------------------+                   
        |         LM Studio Unified Router      |                   
        |              [port 1234]              |                   
        +---------------------------------------+                   

   Client Tools Integration:
   • Claude Code (CLI) ---> Points to your choice of active endpoint (`localhost:1234`, `17704`, or Jetstream)
   • VS Code          ---> Multi-profile extension settings routing across all nodes

```

---

## 2. Infrastructure Deployment & Setup (Daemon-Free)

### Step 1: Initialize Remote Nodes (DGX Spark & RTX 3090)

Instead of running a background system daemon (`lms daemon up`), manage these nodes via active foreground processes or desktop apps:

* **Option A (GUI):** Launch the LM Studio desktop application directly on the physical display/desktop of the DGX Spark and RTX 3090 machines.
* **Option B (Foreground CLI):** If logged in via terminal, load your model and start the server process directly in an active, foreground shell window:
```bash

lms load <model_identifier> --gpu max
lms server start

```


*(Keeping this terminal window open keeps the service alive; closing it or hitting `Ctrl+C` cleanly shuts down the server).*

### Step 2: Establish LM Link on Your MacBook

1. Open the **LM Studio** desktop app on your M1 MacBook Pro.
2. Authenticate your session if prompted:
```bash
lms login

```


3. Use the LM Studio GUI dashboard to pair your active remote DGX Spark and RTX 3090 instances into your **LM Link** mesh network.

### Step 3: Secure the Remote A100 Cluster & Jetstream Connection

1. Launch a persistent background SSH tunnel to map the remote multi-GPU A100 cluster proxy forward to port `17704` on your Mac:

```bash
ssh -N -L 17704:localhost:17704 user@your-a100-cluster-ip &

```


2. Verify local proxy connectivity:

```bash
curl http://localhost:17704/v1/models

```


3. Add your Jetstream Cloud credentials to your shell configuration (`~/.zshrc`):

```zsh
export JETSTREAM_API_KEY="your-jetstream-api-key"
export JETSTREAM_BASE_URL="https://llm.jetstream-cloud.org/v1"

```



---

## 3. Managing and Swapping Models on Local Nodes (Spark & RTX 3090)

With the manual/foreground setup, you can dynamically change models using either interface method:

* **Method A (GUI):** Open LM Studio on your Mac, select your DGX Spark or RTX 3090 from the node menu, and load a different model directly into VRAM.
* **Method B (CLI):**

```bash
# List available local models
lms ls

# Unload current memory block
lms unload --host <node-ip-or-name>

# Load new model with maximum GPU offloading
lms load <model_identifier> --host <node-ip-or-name> --gpu max --context-length 8192

```

---

## 4. Client Tool Configuration (Claude Code & VS Code)

### A. Claude Code Configuration (`~/.zshrc`)

Set up base variables or alias shortcuts to swap your CLI focus between targets:

```zsh
# Default target pointing to A100 cluster proxy
export ANTHROPIC_BASE_URL="http://localhost:17704/v1"
export ANTHROPIC_MODEL="gemma-4"
export ANTHROPIC_API_KEY="not-needed"

```

*(To route Claude Code through your DGX Spark or RTX 3090 instead, swap the base URL to `http://localhost:1234/v1`).*

### B. VS Code Extension Configuration (`~/.continue/config.json`)

Configure multi-profile backends for extensions like **Continue**, **Cline**, or **Roo Code**:

```json
{
  "models": [
    {
      "title": "Gemma 4 (A100 Cluster)",
      "provider": "openai",
      "apiBase": "http://localhost:17704/v1",
      "model": "gemma-4"
    },
    {
      "title": "DGX Spark / RTX 3090 (LM Link)",
      "provider": "openai",
      "apiBase": "http://localhost:1234/v1",
      "model": "your-linked-local-model"
    },
    {
      "title": "Jetstream Cloud",
      "provider": "openai",
      "apiBase": "https://llm.jetstream-cloud.org/v1",
      "apiKey": "your-jetstream-api-key",
      "model": "jetstream-model-name"
    }
  ]
}

```


Cline

To configure the **Cline** extension in VS Code on your M1 MacBook Pro so it can talk to your multi-tier backends (such as your local LM Studio router, your remote A100 cluster proxy, or Jetstream Cloud), follow these steps:

### Step 1: Install Cline

1. Open **VS Code** on your Mac.
2. Go to the Extensions marketplace (`Cmd+Shift+X` or click the Extensions icon on the left sidebar).
3. Search for **Cline** (by Saoud Rizwan) and click **Install**.

### Step 2: Open Cline Settings

1. Click the **Cline icon** in your left activity bar to open the Cline panel.
2. Click the **Settings gear icon (⚙️)** at the top of the Cline panel.

### Step 3: Configure Provider & Endpoints

Because Cline supports OpenAI-compatible APIs, you can point it directly to any of your local or remote routing layers.

In the **API Provider** dropdown, select **OpenAI Compatible**, then fill out the fields depending on which tier you want Cline to target:

#### Option A: Routing via LM Studio (DGX Spark / RTX 3090 / Local Router)

* **Base URL:** `http://localhost:1234/v1`
* **API Key:** `not-needed` (or any dummy string like `lm-studio`)
* **Model ID:** Enter the exact model name currently loaded in your LM Studio network (e.g., matching what is active on your Spark or 3090).

#### Option B: Routing via the Remote A100 Cluster Proxy (`17704`)

* **Base URL:** `http://localhost:17704/v1`
* **API Key:** `not-needed`
* **Model ID:** `gemma-4` (or the specific model identifier mapped on your A100 backend)

#### Option C: Routing via Jetstream Cloud

* **Base URL:** `[https://llm.jetstream-cloud.org/v1](https://llm.jetstream-cloud.org/v1)`
* **API Key:** Your personal Jetstream API key (`sk-...`)
* **Model ID:** Your target Jetstream model name

---

### Step 4: Advanced Model Parameters (Recommended for Local Models)

Scroll down inside the Cline settings to fine-tune context behavior for coding:

* **Context Window:** Match this to your model's capabilities (e.g., `8192`, `16384`, or higher depending on the model you are running on your A100s or workstations).
* **Max Output Tokens:** Set a comfortable ceiling for code generation blocks (e.g., `4096` or `8192`).

Click **Save** at the bottom of the provider settings panel, and Cline is ready to interact with your chosen backend directly inside your workspace.


With your mix of hardware—**RTX 3090 (24GB VRAM)**, **NVIDIA DGX Spark** (cohesive multi-GPU / high-memory accelerator setup), **M1 MacBook Pro Max 64GB**, and your **remote A100 cluster**—you can distribute your models based on their strengths: code execution, heavy logic reasoning, or fast local agent tasks.

Here is a breakdown of what models you should run on each machine to get the absolute most out of your setup:

---

### 1. The RTX 3090 Rig (24GB VRAM)

* **Best Choice:** **Qwen3-Coder (30B-A3B)** or **DeepSeek-R1-Distill-32B** (at a 4-bit/Q4 or IQ4 quant).
* **Why:** A single 24GB VRAM card hits the sweet spot for 27B–32B parameter models. Qwen3-Coder models excel at local agentic tool use (crucial for Cline and VS Code), while a DeepSeek-R1 distilled model gives you powerful logic and math reasoning right on your local hardware without hitting the cloud.

### 2. The NVIDIA DGX Spark

* **Best Choice:** **Mistral Small / Devstral (24B–48B)** or **Llama 3.3 (70B quantized)**.
* **Why:** The DGX Spark handles heavy enterprise and deep system orchestration workloads. Use it for a larger frontier-class open model (like a 70B parameter model at Q4 quantization) or specialized multi-step code generation models that require robust VRAM bandwidth to maintain low latency during agentic loops.

### 3. The Remote A100 Cluster (via Port `17704`)

* **Best Choice:** **Gemma 4** or **Qwen-Max / Large MoE architectures** (fully resident in high-speed multi-GPU VRAM).
* **Why:** Since you have a multi-A100 backend proxy mapped here, reserve this tier for your heaviest, highest-context frontier tasks. Run large-context models (e.g., 32K–128K+ windows) here so Claude Code can ingest massive repositories or documentation sets without choking local VRAM.

### 4. M1 MacBook Pro Max (64GB Unified Memory)

* **Best Choice:** **Qwen3.8-27B (Q4 or Q8)** or **Gemma 4 (26B)**.
* **Why:** Your Mac's 64GB of unified memory allows you to comfortably run dense 27B models locally via MLX or llama.cpp. This acts as your mobile/local offline fallback when you aren't routing tasks out to your DGX Spark or RTX 3090 via LM Link.

---

### Recommended Workflow Mapping for Cline & Claude Code

* **For everyday coding & fast edits:** Route Cline/Claude Code to your **RTX 3090 running Qwen3-Coder-30B** for instant generation speed.
* **For deep architectural refactoring & complex debugging:** Shift your tool target to your **A100 Cluster (Gemma 4)** or **DGX Spark (70B)** to leverage maximum reasoning capacity.


## MAC OS

Use **Qwen3.8-27B**.

### Why Choose Qwen3.8-27B over Gemma 4 for Local Mac Usage:

1. **Superior Coding & Agentic Performance:** Qwen models (specifically the Qwen dense/coder line) consistently rank at the top for local coding assistants like Cline, Claude Code, and VS Code integrations. It handles tool-calling loops and multi-step code generation natively with exceptional precision.
2. **Flexible Thinking Control:** Qwen3.8-27B features adjustable reasoning effort flags (`xhigh`, `medium`, `low`), letting you dynamically scale its logic depth depending on whether you need a fast completion or deep architecture debugging.
3. **Massive Context & Native Multimodality:** It ships with a native 262K context window (extensible up to 1M tokens) and strong vision capabilities, making it far more versatile for analyzing local file trees or UI screenshots on your Mac.

### Which Quantization to Pick (Q4 vs. Q8)?

* **Go with Q4 (or IQ4_NL / Q4_K_M)** if you want lightning-fast token generation speeds on your M1 Mac's unified memory. It leaves plenty of breathing room for macOS system memory and other background tools.
* **Go with Q8** only if your workflow demands maximum code-accuracy logic and you don't mind a slightly lower generation tokens-per-second rate.

*(If you are setting it up via llama.cpp or MLX on your Mac, pull `Qwen/Qwen3.8-27B-Instruct` quantized to Q4_K_M for the best balance of speed and coding intelligence).*

### Spark

On your **NVIDIA DGX Spark**, you should run a **larger frontier-class open weight model or Mixture-of-Experts (MoE)** that exceeds the 24GB VRAM ceiling of your RTX 3090, but fully leverages the Spark's **128 GB of unified system memory (Grace Blackwell architecture)**.

The best choices to load onto your DGX Spark include:

### 1. Llama 3.3 (70B Instruct) or Qwen3.8 (Large Variant / MoE)

* **Why:** With 128GB of high-speed unified memory, the DGX Spark can comfortably fit a fully unquantized or lightly quantized (Q4/Q5) 70B+ parameter model.
* **Role in your cluster:** Keep this as your **heavy local reasoning and orchestration engine**. When Cline or Claude Code faces a complex software architecture refactoring task that requires looking deep into a codebase, route it to the 70B model running on the Spark. It bridges the gap between your local Mac/3090 setup and your remote A100 cluster.

### 2. DeepSeek or Mixture-of-Experts (MoE) Architectures

* **Why:** The Spark's Grace Blackwell unified design excels at handling memory-bound MoE models efficiently. Running a model like a DeepSeek distilled variant or specialized MoE allows you to utilize massive parameter counts while maintaining fast token throughput.

## what is best for spark

### How to manage it via LM Link:

Leave the Spark loaded with your heavy **70B/MoE model**, use your **RTX 3090** for fast 32B coding loops (Qwen3-Coder), and use your **Mac** for mobile/offline fallback. This gives you a tiered performance hierarchy across all your local hardware before ever needing to tap your remote A100 cluster or Jetstream Cloud.

Load **Llama 3.3 (70B Instruct)** (quantized to Q4_K_M or IQ4_NL) onto your **NVIDIA DGX Spark**.

### Why Llama 3.3 70B for the Spark?

* **Perfect Memory Fit:** The DGX Spark features **128 GB of coherent unified system memory** (Grace Blackwell architecture). A 70B model at a 4-bit quantization takes up roughly 40GB–45GB of space, fitting comfortably into the Spark's massive memory footprint with plenty of headroom left over for long context windows and fast token caching.
* **The "Goldilocks" Tier:** Your RTX 3090 handles the snappy 30B coding tasks, your Mac handles mobile/local fallback, and your remote A100 cluster handles hyper-scale tasks. Putting a heavy 70B reasoning model on the Spark creates a seamless mid-to-high bridge for deep code analysis, multi-file architectural reasoning, and complex agentic workflows when Cline or Claude Code needs broad context comprehension.

To install and configure **Claude Code** on your macOS system, follow the native command-line installation path recommended by Anthropic.

---

### Step 1: Install Claude Code

Open your terminal on your M1 MacBook Pro and run the native installer script:

```zsh
curl -fsSL https://claude.ai/install.sh | bash

```

*(Alternatively, if you prefer using Homebrew: `brew install --cask claude-code`)*

Verify that the installation completed successfully by checking the version:

```zsh
claude --version

```

---

### Step 2: Authenticate Your Account

Claude Code requires an active account (such as Claude Pro, Max, Team, Enterprise, or a Claude Console API account).

1. Navigate to any of your code project directories in your terminal:
```zsh
cd /path/to/your/project

```


2. Launch the CLI tool for the first time:
```zsh
claude

```


3. Follow the automated browser prompts to log in and authorize your session. Once authenticated, credentials are saved locally so you won't need to log in repeatedly.

---

### Step 3: Configure Claude Code to Route Through Your Local/Remote Backends

By default, Claude Code communicates with Anthropic's cloud infrastructure. However, because you are building a custom multi-tier cluster infrastructure (using your local Mac, DGX Spark, RTX 3090, A100 cluster proxy, or Jetstream), you can redirect Claude Code's backend target using standard OpenAI-compatible environment variables.

To point Claude Code to a specific backend, define the routing variables in your `~/.zshrc` file:

#### Option A: Target your Remote A100 Cluster Proxy (`17704`)

```zsh
export ANTHROPIC_BASE_URL="http://localhost:17704/v1"
export ANTHROPIC_MODEL="gemma-4"
export ANTHROPIC_API_KEY="not-needed"

```

#### Option B: Target your Local LM Studio Router (DGX Spark / RTX 3090 on Port `1234`)

```zsh
export ANTHROPIC_BASE_URL="http://localhost:1234/v1"
export ANTHROPIC_MODEL="your-linked-local-model"
export ANTHROPIC_API_KEY="not-needed"

```

After modifying your `~/.zshrc`, reload your shell:

```zsh
source ~/.zshrc

```

---

### Step 4: Essential Claude Code Commands & Shortcuts

Once inside an active `claude` session in your project directory:

* Type `/` inside the prompt to view available workspace commands and tools.
* Press **Shift + Tab** to cycle through different permission modes (e.g., auto-approval vs. guarded interactive turns).
* Type `/config` to open settings (such as theme and preferences).


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What does it mean to run an LLM service \"daemon-free\"?"
    It means running the service as a foreground process in a terminal window. This ensures that the process terminates automatically when the terminal is closed or `Ctrl-C` is pressed, avoiding lingering background services.

??? question "Why is the Llama 3.3 70B model a good fit for the NVIDIA DGX Spark node?"
    The DGX Spark features 128GB of unified memory, which is more than enough to host a 70B model at 4-bit quantization (approx. 40-45GB) while leaving significant headroom for large context windows.

??? question "How can Claude Code be configured to route through a local LM Studio router?"
    By setting the `ANTHROPIC_BASE_URL` environment variable to `http://localhost:1234/v1` (or the appropriate local router URL) in the shell configuration (e.g., `.zshrc`).

* Use `claude -c` to instantly continue your most recent conversation thread in that project.