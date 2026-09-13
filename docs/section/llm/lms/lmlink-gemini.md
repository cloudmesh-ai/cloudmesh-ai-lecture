# Unified Multi-Tier LLM Cluster Architecture & Deployment Guide (`lms`-Native)

This guide provides a unified, up-to-date deployment blueprint for your **four-tier compute cluster**, fully transitioned to LM Studio's official CLI (`lms`) and modern networking standards.

---

## 1. System Architecture Overview

Your environment spans **four distinct compute tiers** controlled centrally from your M1 MacBook Pro, using native `lms` tools, secure SSH tunneling, and OpenAI-compatible endpoints.

```text
                                +-----------------------------------+
                                |          M1 MacBook Pro           |
                                |     (Client Control Machine)      |
                                +-----------------------------------+
                                   /       |              \           \      
         [LM Link Mesh]           /        | [Localhost]   \           \ [HTTPS API]
        +------------------------+         |                \           \
        v                                  v                 v           v
+------------------------+      +------------------------+  +------------------------+  +------------------------+
|   NVIDIA DGX Spark     |      |   Linux + RTX 3090     |  | Remote 2x/4x A100 Node |  |    Jetstream Cloud     |
|  (Llama 3.3 70B via    |      |   (Qwen3-Coder-30B)    |  | (Proxy via port 17704) |  | (llm.jetstream-cloud)  |
|      LM Studio)        |      |                        |  |                        |  |                        |
+------------------------+      +------------------------+  +------------------------+  +------------------------+
        \                                 /                         
         \                               / [Localhost Aggregator]   
          v                             v                           
        +---------------------------------------+                   
        |         LM Studio Local Router        |                   
        |              [port 1234]              |                   
        +---------------------------------------+                   

   Client Tools Integration:
   • Claude Code (CLI) ---> Points to your choice of active endpoint (`localhost:1234`, `17704`, or Jetstream)
   • VS Code (Cline/Continue) ---> Multi-profile settings routing across all nodes

```

---

## 2. Infrastructure Deployment & Setup

### Step 1: Initialize Remote Nodes (DGX Spark & RTX 3090)

Ensure the `lms` CLI is bootstrapped on your remote Linux/DGX nodes:

```bash
~/.lmstudio/bin/lms bootstrap

```

To run models without heavy background services blocking your shell, use the `lms` execution commands:

* **Option A (GUI Interop):** Launch the LM Studio desktop interface on the remote node's display; it hooks directly into the underlying `llmster` engine.
* **Option B (Headless CLI):** Load models and spin up the server explicitly in your active workflow:

```bash
# Load your hardware-optimized model with maximum GPU offloading
lms load <model_identifier> --gpu max

# Start the OpenAI-compatible server on the default port (1234)
lms server start

```

*(Stopping the process or exiting the shell cleanly tears down the runtime context).*

### Step 2: Establish LM Link Mesh on Your MacBook

1. Open the **LM Studio** desktop app on your M1 MacBook Pro.
2. Authenticate your CLI/App session if prompted:

```bash
lms login

```

3. Use the **LM Link** panel in the desktop application to pair your remote DGX Spark and RTX 3090 instances into your unified mesh network.

### Step 3: Secure the Remote A100 Cluster & Jetstream Connection

1. Launch a persistent background SSH tunnel to forward the multi-GPU A100 cluster proxy to port `17704` on your Mac:

```bash
ssh -N -L 17704:localhost:17704 user@your-a100-cluster-ip &

```

2. Verify connectivity:

```bash
curl http://localhost:17704/v1/models

```

3. Add your Jetstream Cloud credentials to your shell configuration (`~/.zshrc`):

```zsh
export JETSTREAM_API_KEY="your-jetstream-api-key"
export JETSTREAM_BASE_URL="https://llm.jetstream-cloud.org/v1"

```

---

## 3. Managing and Swapping Models on Local Nodes

Dynamically manage runtime memory using `lms` commands across your nodes:

```bash
# List available local models on disk
lms ls

# Check models currently active in memory
lms ps

# Unload current memory block
lms unload

# Load a new model with maximum GPU offload and context sizing
lms load <model_identifier> --gpu max --context-length 8192

```

---

## 4. Hardware Workload Mapping Strategy

* **RTX 3090 Rig (24GB VRAM):** Run **Qwen3-Coder (30B)** at Q4/IQ4 quant. Perfect for rapid local agent loops, code auto-completions, and low-latency syntax evaluations.
* **NVIDIA DGX Spark (128GB Unified Memory):** Run **Llama 3.3 (70B Instruct)** at Q4_K_M. This acts as your heavy local reasoning engine, handling multi-file repository indexing and complex architectural analysis.
* **Remote A100 Cluster (Port `17704`):** Run **Gemma 4** or massive MoE systems. Reserved for extreme-scale context ingestion and heavy multi-GPU inference.
* **M1 MacBook Pro Max (64GB Unified Memory):** Run **Qwen3.8-27B (Q4)** locally for mobile and offline fallback operations.

---

## 5. Client Tool Configuration (Claude Code & VS Code)

### A. Claude Code Configuration (`~/.zshrc`)

Add target shortcuts to your shell profile to switch your CLI target instantly:

```zsh
# Default target pointing to A100 cluster proxy
export ANTHROPIC_BASE_URL="http://localhost:17704/v1"
export ANTHROPIC_MODEL="gemma-4"
export ANTHROPIC_API_KEY="not-needed"

```

*(To pivot Claude Code to your DGX Spark or RTX 3090 network, change the base URL to `http://localhost:1234/v1`).*

### B. VS Code Extension Configuration (Cline / Continue)

Configure multi-profile backends for extensions like **Cline** or **Continue** via OpenAI-compatible endpoints:

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
      "title": "DGX Spark - Llama 3.3 70B (LM Link)",
      "provider": "openai",
      "apiBase": "http://localhost:1234/v1",
      "model": "llama-3.3-70b-instruct"
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

---

## 6. Quick Reference: Essential `lms` Commands

| Command | Action |
| --- | --- |
| `lms status` | Check if the core runtime daemon is active |
| `lms ls` | List all models available in your local repository |
| `lms ps` | Inspect models currently loaded into VRAM/RAM |
| `lms server start --port 1234` | Launch the OpenAI-compatible server endpoint |
| `lms server stop` | Terminate the active API server |



## OSX

```
lms get --mlx Qwen3.8-27B
```

```
 lms get --mlx Qwen3.8-27B
Searching staff picks with the term Qwen3.8-27B

   ↓ To download: model qwen/qwen3.8-27b - 171.39 KB
   └─ ✓ Satisfied Qwen3.8 27B 8bit [MLX]

About to download 171.39 KB.

? Start download?
❯ Yes
  No
  Change variant selection
```


```
lms ls
```

```
You have 5 models, taking up 64.69 GB of disk space.

LLM                               PARAMS    ARCH       SIZE        DEVICE    
google/gemma-4-31b (1 variant)    31B       gemma4     18.44 GB    Local     
llama-3-8b-instruct-1048k         8B        Llama      4.53 GB     Local     
openai/gpt-oss-20b (1 variant)    20B       gpt_oss    12.10 GB    Local     
qwen/qwen3.8-27b (1 variant)      27B       qwen3_5    29.53 GB    Local     

EMBEDDING                               PARAMS    ARCH          SIZE        DEVICE    
text-embedding-nomic-embed-text-v1.5              Nomic BERT    84.11 MB    Local    
```


```
lms ps
```
```
No models are currently loaded.

To load a model, run:

    lms load <model path>
```

```
lms load qwen/qwen3.8-27b
```
```
Loading qwen/qwen3.8-27b 65% ⠦
...
```

When its loaded we see

```
Model loaded successfully in 22.12s.
(27.50 GiB)
To use the model in the API/SDK, use the identifier "qwen/qwen3.8-27b".
```

```
lms ps                   
```

```
IDENTIFIER          MODEL               STATUS    SIZE        CONTEXT    PARALLEL    DEVICE    TTL
qwen/qwen3.8-27b    qwen/qwen3.8-27b    IDLE      29.53 GB    131072     4           Local        
```


## remotes

Your `lms ps` output shows that **`qwen/qwen3.8-27b`** is successfully loaded into memory on your local machine, idling with a `131072` context window, 4 parallel slots, and ready to accept API requests.

Because you have your multi-tier environment set up, you can also check the status of your **remote linked nodes** (like your DGX Spark or RTX 3090 rig) directly from your terminal by appending the `--host` flag to `lms ps`:

```bash
# Check loaded models on a specific remote node in your LM Link network
lms ps --host <remote-node-ip-or-name>

```

### Next Steps with Your Running Model:

1. **Test a quick prompt right from your terminal:**
```bash
lms chat qwen/qwen3.8-27b

```


2. **Point your tools to it:** Since it's active locally on port `1234`, your running instance matches the `localhost:1234/v1` base URL configured for Claude Code and Cline.


```
lms chat qwen/qwen3.8-27b
```

```
✔ Always fetch the model catalog ? (requires internet connection) Yes
Setting the preference to always fetch the model catalog.

 ╭──────────────────────────────────────────────────────────────────────╮
 │ 👾 lms chat                                                          │
 │ Type exit or Ctrl+C to quit                                          │
 │                                                                      │
 │ Chatting with qwen/qwen3.8-27b                                       │
 │                                                                      │
 │ Try one of the following commands:                                   │
 │ /model - Load a model (type /model to see list)                      │
 │ /download - Download a model                                         │
 │ /clear - Clear the chat history                                      │
 │ /help - Show help information                                        │
 ╰──────────────────────────────────────────────────────────────────────╯

› Type a message or use / to use commands
```

## How do i configure now cline


1. Open **VS Code**
2. Install/open the **Cline** extension
3. Click the **Cline icon** in the sidebar
4. Click the **gear/settings** icon
5. Choose your **API provider**, e.g. **Anthropic**, **OpenAI**, **Google**, **OpenRouter**, **Ollama**, **LM Studio**
6. Enter your **API key**
7. Pick a **model**
8. Test with a simple prompt in the Cline chat

For project-specific behavior, create a file:

- `.clinerules` in your project root


## Claude Code


## 1. Install it

If you use Node.js:

```bash
npm install -g @anthropic-ai/claude-code
```

Then in your project folder:

```bash
cd your-project
claude
```

## 2. Authenticate

You can authenticate in two common ways.

### Option A: Claude subscription login

Start Claude Code:

```bash
claude
```

Then use:

```text
/login
```

Sign in with your Claude account, e.g. Claude Pro/Max, if available.

### Option B: API key

Set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Then run:

```bash
claude
```

Do **not** commit your API key to your repo.

## 3. Basic slash commands

Inside Claude Code, useful commands include:

```text
/login
/model
/config
/permissions
/mcp
/compact
/clear
```

Common ones:

- `/login` — sign in or change account
- `/model` — choose the model
- `/permissions` — manage what Claude Code is allowed to do
- `/mcp` — manage MCP servers
- `/config` — general settings
- `/compact` — compress conversation context

## 4. Add project instructions

Claude Code reads a file called:

```text
CLAUDE.md
```

Put it in your project root.

Example:

```md
# Project rules

- Use pnpm, not npm.
- Run tests with: pnpm test
- Keep changes small and focused.
- Do not modify generated files.
- Do not commit secrets.
- Prefer TypeScript over JavaScript.
```

You can also have global notes in:

```text
~/.claude/CLAUDE.md
```

## 5. Configure permissions

Claude Code can read/write files and run shell commands. You should control what it can do automatically.

Settings files:

Global:

```text
~/.claude/settings.json
```

Project shared:

```text
.claude/settings.json
```

Project local/private:

```text
.claude/settings.local.json
```

The local one is usually the best place for personal permissions.

Example idea:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff)",
      "Bash(pnpm test)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(.env*)",
      "Read(.git/**)"
    ]
  }
}
```

The exact permission syntax may vary, so use:

```text
/permissions
```

to inspect and adjust it interactively.

## 6. Configure a model

Use:

```text
/model
```

inside Claude Code.

If you are using a specific org setup, custom endpoint, Bedrock, or Vertex, your team may have a different required configuration.

Common provider-related env vars:

```bash
# Standard Anthropic API
export ANTHROPIC_API_KEY="..."

# AWS Bedrock
export CLAUDE_CODE_USE_BEDROCK=1

# Google Vertex
export CLAUDE_CODE_USE_VERTEX=1
```

For Bedrock/Vertex, you also need the corresponding AWS or GCP credentials configured.

## 7. Add MCP servers

MCP servers let Claude Code connect to external tools, databases, docs, APIs, etc.

Inside Claude Code:

```text
/mcp
```

You can also add them from the CLI, for example:

```bash
claude mcp add <name> -- <command>
```

Example pattern:

```bash
claude mcp add filesystem -- npx @modelcontextprotocol/server-filesystem /path/to/project
```

Check the MCP server documentation for the exact command.

## 8. Recommended starter configuration

For a normal app repo, I’d start with:

1. `CLAUDE.md` at project root
2. `.claude/settings.local.json` for local permissions
3. API key or subscription login configured
4. Dangerous shell commands denied or required to ask
5. Secrets excluded from Claude’s access

Minimal `CLAUDE.md`:

```md
# Rules

- Do not modify environment files.
- Do not run destructive commands without asking.
- Run the project’s linter/tests before finishing.
- Prefer minimal diffs.
```

Minimal `.claude/settings.local.json`:

```json
{
  "permissions": {
    "deny": [
      "Read(.env*)",
      "Bash(rm -rf *)"
    ]
  }
}
```

## Quick checklist

```bash
claude
```

Then verify:

```text
/login
/model
/permissions
/mcp
/config
```

If you tell me what you want to configure — **API key, Claude subscription, model, permissions, MCP, Bedrock, Vertex, or enterprise endpoint**
— I can give you the exact setup.


## adding the spark

To add your **NVIDIA Spark** to the LM Studio instance running on your M1 MacBook Pro **without using background daemons**, and to have it instantly available so you can switch models seamlessly inside **Cline**, follow this streamlined workflow.

---

### Step 1: Connect the NVIDIA Spark via LM Link (Daemon-Free)

Because you are avoiding system daemons, you will run LM Studio in an active foreground session on the Spark:

1. **On the NVIDIA Spark:**
Open LM Studio as a standard foreground/desktop app (or run your manual foreground server setup).
2. **Authenticate both machines:**
Open a terminal on your Mac (and on the Spark if needed) and run:
```bash
lms login

```


3. **Enable LM Link on the Spark:**
In the Spark's local terminal or app, enable the link:
```bash
lms link enable

```


4. **Link to your Mac:**
Open LM Studio on your M1 MacBook Pro, click on the **LM Link** tab in the sidebar, and pair the Spark.

Once paired, **any model loaded on the Spark will automatically surface inside your Mac's LM Studio model selector** as if it were running locally, completely backed by the end-to-end encrypted mesh.

---

### Step 2: Verify the Spark is Connected via CLI

On your Mac terminal, check your linked nodes and active models:

```bash
lms link status

```

When you run `lms ps` on your Mac, your local models (like the Qwen 27B currently active) and your Spark's remote resources will now be visible through a unified local proxy router on your Mac at port `1234`.

---

### Step 3: Seamless Model Switching inside Cline

Because LM Link routes everything through your Mac's local API aggregator (`http://localhost:1234/v1`), **you do not need to change your Cline base URL** when switching between your Mac and your NVIDIA Spark.

To switch models seamlessly:

1. **Change the model in LM Studio (GUI or CLI):**

* *Via GUI:* On your Mac's LM Studio window, open the model dropdown, select your **NVIDIA Spark** node, and load your heavy model (e.g., Llama 3.3 70B).
* *Via CLI from your Mac:*
```bash
lms load <spark_model_identifier> --host <spark-device-name>

```

2. **Update Cline's Model ID:**
Open your Cline settings sidebar in VS Code. Since the Base URL stays anchored to `http://localhost:1234/v1`, you only need to update the **Model ID** text field to match whatever model you just loaded onto the Spark.

Your local Mac client handles the proxying automatically, meaning Cline sends requests to `localhost:1234`, and LM Studio transparently shuttles the heavy compute over to your NVIDIA Spark over the encrypted link.


Here is the updated master document integrating your NVIDIA Spark configuration (**Llama 3.3 70B** model choice), the **daemon-free workflow** for the Spark and RTX 3090 nodes, **LM Link** pairing, and your updated **Cline & Claude Code** configurations.

---

# Unified Multi-Tier LLM Cluster Architecture & Deployment Guide

## 1. System Architecture Overview

Your environment spans **four distinct compute tiers** controlled centrally from your M1 MacBook Pro, leveraging LM Link, secure SSH tunneling, and standard OpenAI-compatible endpoints.

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
| (Llama 3.3 70B via     |      | (Qwen3-Coder 32B via   |  | (Proxy via port 17704) |  | (llm.jetstream-cloud)  |
|  LM Studio Desktop)    |      |  LM Studio Desktop)    |  |                        |  |                        |
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
   • VS Code (Cline)  ---> Multi-profile extension settings routing across all nodes

```

---

## 2. Infrastructure Setup & LM Link Pairing (Daemon-Free)

### Step 1: Initialize Workstation Nodes (DGX Spark & RTX 3090)

To avoid background system daemons, run LM Studio as an active foreground/desktop application on your DGX Spark and RTX 3090 rig:

1. Open LM Studio on the physical desktop or interactive workspace of each node.
2. Authenticate the CLI tools:
```bash
lms login

```


3. Enable LM Link on the node via terminal:
```bash
lms link enable

```



### Step 2: Establish LM Link on Your MacBook

1. Open LM Studio on your M1 MacBook Pro.
2. Log in with your account (`lms login`).
3. Navigate to the **LM Link** panel in the sidebar and accept/pair your NVIDIA DGX Spark and RTX 3090 nodes.
4. Verify the mesh status from your Mac terminal:
```bash
lms link status

```



### Step 3: Secure the Remote A100 Cluster & Jetstream Connection

1. Launch your persistent background SSH tunnel for the A100 cluster proxy on port `17704`:
```bash
ssh -N -L 17704:localhost:17704 user@your-a100-cluster-ip &

```


2. Configure your Jetstream Cloud environment variables in your Mac's `~/.zshrc`:
```zsh
export JETSTREAM_API_KEY="your-jetstream-api-key"
export JETSTREAM_BASE_URL="https://llm.jetstream-cloud.org/v1"

```



---

## 3. Workload & Model Distribution Strategy

* **NVIDIA DGX Spark (128GB Unified Memory):**
* **Assigned Model:** **Llama 3.3 (70B Instruct)** (Quantized to Q4_K_M or IQ4_NL)
* **Purpose:** Heavy local reasoning, architectural design, and multi-file code refactoring.


* **Linux RTX 3090 Rig (24GB VRAM):**
* **Assigned Model:** **Qwen3-Coder (30B-A3B)** (Quantized to Q4)
* **Purpose:** Fast, snappy local agentic loops and routine script generation.


* **M1 MacBook Pro Max (64GB Unified Memory):**
* **Assigned Model:** **Qwen3.8-27B** (MLX format, Q4_K_M)
* **Purpose:** Local mobile/offline fallback and fast local workspace evaluation.


* **Remote A100 Cluster Proxy (`17704`):**
* **Assigned Model:** **Gemma 4**
* **Purpose:** Ultra-high-context, hyper-scale repository ingestion and complex logic processing.



To load or change the model on your Spark or RTX 3090 from your Mac via LM Link:

```bash
lms load <model_identifier> --host <spark-or-3090-device-name> --gpu max

```

---

## 4. Client Tool Configurations (Claude Code & Cline)

### A. Claude Code Configuration (`~/.zshrc`)

Set target endpoints in your shell configuration:

```zsh
# Default target pointing to A100 cluster proxy (or change base_url to localhost:1234 for LM Link router)
export ANTHROPIC_BASE_URL="http://localhost:17704/v1"
export ANTHROPIC_MODEL="gemma-4"
export ANTHROPIC_API_KEY="not-needed"

```

### B. Cline Configuration (VS Code Extension)

Open Cline's settings panel in VS Code, choose **OpenAI Compatible** as the API Provider, and configure your targets:

* **For Local Workstations & Spark (via LM Link Router):**
* **Base URL:** `http://localhost:1234/v1`
* **API Key:** `not-needed`
* **Model ID:** Match whichever model is currently active (e.g., your Spark's Llama 3.3 70B or your Mac's Qwen 27B).


* **For Remote A100 Cluster Proxy:**
* **Base URL:** `http://localhost:17704/v1`
* **API Key:** `not-needed`
* **Model ID:** `gemma-4`


* **For Jetstream Cloud:**
* **Base URL:** `[https://llm.jetstream-cloud.org/v1](https://llm.jetstream-cloud.org/v1)`
* **API Key:** Your Jetstream API key
* **Model ID:** Your preferred cloud model identifier

## switch behind a  single url

**Yes, absolutely.** You can keep **one single, permanent URL in Cline** (`http://localhost:1234/v1`) and dynamically switch which model or machine is handling the request directly through LM Studio without ever changing your IDE settings.

Because LM Studio acts as an intelligent local router/aggregator via **LM Link**, it handles the network abstraction layer for you.

Here is how the single-URL switching mechanism works in practice:

---

### How the Single-URL Workflow Works

1. **Cline's Configuration Never Changes:**
In your Cline settings, you permanently lock in:
* **Base URL:** `http://localhost:1234/v1`
* **API Key:** `not-needed`
* **Model ID:** Whatever identifier corresponds to your currently active node model.


2. **LM Studio Manages the Routing Backend:**
When Cline sends a request to `localhost:1234`, it hits your Mac's local LM Studio instance.
* If you have a model loaded locally on your Mac, LM Studio answers it locally.
* If you load a model on your **NVIDIA Spark** or **RTX 3090** via LM Link, LM Studio automatically transparently proxies and routes the incoming request from `localhost:1234` over the encrypted mesh to that specific machine and streams the response back.



---

### How to Switch Between Models/Nodes Seamlessly

To change whether Cline is talking to your Mac, your RTX 3090, or your NVIDIA Spark:

* **Method A (The GUI Way):**
Open your Mac's LM Studio interface, click the model selection dropdown, and choose a model hosted on a different node (e.g., swapping from your Mac's Qwen 27B to your Spark's Llama 3.3 70B). LM Studio re-routes the endpoint target instantly.
* **Method B (The CLI Way):**
Run a single command from your Mac terminal to swap the active runtime target across your mesh:
```bash
# Unload current context and load a model residing on your Spark/3090 node
lms unload --all
lms load <model_name> --host <node_name> --gpu max

```



### The One Thing to Keep in Sync

Because Cline requires an explicit string in the **Model ID** field to match what the server expects, when you switch models via LM Studio, you just need to update Cline's Model ID text box to match the new model's tag (e.g., changing it from `qwen3.8-27b` to `llama-3.3-70b`). The Base URL (`http://localhost:1234/v1`) remains completely untouched.



## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the primary purpose of the `lms bootstrap` command on remote nodes?"
    The `lms bootstrap` command is used to initialize the LM Studio CLI tool on remote Linux/DGX nodes, making the `lms` binary globally accessible in the system path.

??? question "How does the \"LM Link\" mesh network simplify access to remote models on a MacBook?"
    LM Link allows the user to pair remote nodes (like a DGX Spark or RTX 3090) into a mesh network. This enables the local LM Studio instance to act as a router, allowing clients to use a single local endpoint (`localhost:1234`) while the requests are transparently proxied to the remote hardware.

??? question "In the context of Cline/VS Code, what is the advantage of using a single permanent Base URL?"
    By using a single Base URL (e.g., `http://localhost:1234/v1`), you can dynamically switch the active backend model or node via the LM Studio interface without needing to modify the IDE's configuration settings every time you change machines.
