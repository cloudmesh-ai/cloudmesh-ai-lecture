
**# Tutorial: Run Local or Remote LLM Models and Access Them from VS Code (macOS / Linux / Windows)**  

*This guide reflects the **latest releases** (LM Studio ≥ 0.2.14 and `lm‑proxy` ≥ 0.3.0).  The old `lm‑link` binary has been replaced, and LM Studio now ships a native OpenAI‑compatible API, so the proxy is **optional**.  All commands run in the foreground; closing the terminal (or pressing **Ctrl‑C**) stops everything – no background daemons, no system‑service managers, and **no tmux** required.*  

---  

## 1️⃣  Why “no daemons”?  

Launching the services directly in a terminal makes them ordinary foreground processes. When the terminal is closed or you hit **Ctrl‑C**, the processes exit automatically. This keeps the workflow simple, reproducible, and easy to debug.

---  

## 2️⃣  Prerequisites  

| Requirement | Details |
|------------|----------|
| **OS** | macOS (Homebrew recommended), Linux (Ubuntu/Debian/Arch), or Windows (WSL2 works as well) |
| **Python** | 3.9 + (for the optional `lm-proxy` package) |
| **Git** | Optional – for cloning example repos |
| **Internet** | Needed the first time to download model files |
| **GPU (optional)** | If you have an NVIDIA GPU, LM Studio will use it automatically when you pass `--device cuda` (or `--device auto`). Otherwise it falls back to CPU. |

---  

## 3️⃣  Install the three components  

### 3.1 LM Studio (the inference engine)  

| Platform | Installation command |
|----------|----------------------|
| **macOS (Homebrew)** | `brew install --cask lm-studio` |
| **Ubuntu/Debian** | ```bash<br>curl -L -o lm-studio.deb https://github.com/lmstudio-ai/lm-studio/releases/latest/download/lm-studio_ubuntu_amd64.deb<br>sudo dpkg -i lm-studio.deb<br>``` |
| **Windows** | Download the installer from the [LM Studio releases page](https://github.com/lmstudio-ai/lm-studio/releases) and run it. The installer adds `lm-studio.exe` to your `PATH`. |

> **Verify** the binary is reachable:  

```bash
lm-studio --help          # should show usage information
lm-studio --version       # e.g. 0.2.20
```

### 3.2 `lm-proxy` (the new optional proxy)  

```bash
python3 -m pip install --upgrade lm-proxy
```

> **Verify** it installed correctly:  

```bash
lm-proxy --version        # e.g. 0.3.2
```

### 3.3 VS Code + LM Studio extension  

1. Install **VS Code** from <https://code.visualstudio.com/> if you don’t have it.  
2. Inside VS Code → **Extensions** (⇧⌘X on macOS, Ctrl‑Shift‑X on Windows/Linux).  
3. Search for **“LM Studio”** (official) and click **Install**.  
   *If you prefer another OpenAI‑compatible client (e.g., “ChatGPT‑Assistant”), that works as well – you just need to supply an API base URL and a dummy key.*  

---  

## 4️⃣  Run the services (foreground, no daemons)  

> **You only need two terminal tabs (or two split panes).** No `tmux` is required, but you can still use it if you like – the steps below work without it.

### 4.1 Start LM Studio in head‑less mode  

```bash
# Pick a model you have already downloaded (or let LM Studio download one for you)
MODEL_PATH="$HOME/.cache/lm-studio/models/tiny-llama-1.1b-chat-v1.0.Q4_K_S.gguf"

lm-studio \
  --model "$MODEL_PATH" \
  --host 127.0.0.1 \
  --port 12345 \          # ← LM Studio will listen here
  --no-gui                # ← keeps the process in the terminal, no GUI window
```

**Important flags**

| Flag | Meaning |
|------|---------|
| `--model` | Path or identifier of the GGUF model you want to run. |
| `--host`  | Bind address (use `127.0.0.1` for local‑only access). |
| `--port`  | Port number for LM Studio’s OpenAI‑compatible endpoint (`/v1`). |
| `--no-gui`| Prevents the desktop UI from opening; the process stays in the terminal. |
| `--device cuda` / `--device auto` | (optional) Enable GPU inference if you have CUDA installed. |

When the server is ready you’ll see something like:

```
[*] Running on http://127.0.0.1:12345/v1
```

### 4.2 (Optional) Start the proxy in a second tab  

If you want to expose a **different** public port, add logging, or enforce a simple token, launch `lm-proxy`:

```bash
lm-proxy \
  --host 127.0.0.1 \
  --port 5678 \                         # ← VS Code will call this URL
  --backend http://127.0.0.1:12345/v1   # ← forwards to LM Studio
```

You’ll see:

```
[INFO] Proxy listening on http://127.0.0.1:5678/v1 → http://127.0.0.1:12345/v1
```

> **Why use the proxy?**  
> * Change the public port without restarting LM Studio.  
> * Insert a cheap “auth token” (`--auth-token <secret>`).  
> * Run several independent proxies for different projects.  

If you **don’t need a proxy**, skip this step and point VS Code directly at `http://127.0.0.1:12345/v1`.

### 4.3 Quick health‑check (any configuration)

```bash
# With proxy
curl http://127.0.0.1:5678/v1/models | head -n 20

# Without proxy (direct LM Studio)
curl http://127.0.0.1:12345/v1/models | head -n 20
```

You should receive JSON similar to:

```json
{
  "object": "list",
  "data": [
    {
      "id": "tiny-llama-1.1b-chat-v1.0.Q4_K_S",
      "object": "model",
      "owned_by": "local"
    }
  ]
}
```

If you get a proper JSON response, the chain is alive.

---  

## 5️⃣  Configure VS Code to talk to the local endpoint  

1. **Open Settings** (`⌘+,` on macOS, `Ctrl+,` on Windows/Linux).  
2. Search for **“LM Studio: API Base URL”** (or the generic *OpenAI API Base URL* if you use another extension).  
3. **Enter the correct URL**:  

| Situation | Value to paste |
|-----------|----------------|
| **Direct LM Studio** (no proxy) | `http://127.0.0.1:12345/v1` |
| **Via `lm-proxy`** | `http://127.0.0.1:5678/v1` |

4. **API Key** – LM Studio does **not** validate any key, but the extension requires a non‑empty string. Put anything, e.g., `local-key`.  
5. (Optional) In the extension UI, set **Model** to the exact ID you saw from the `curl …/models` call (e.g., `tiny-llama-1.1b-chat-v1.0.Q4_K_S`).  

### 5.1 Test inside VS Code  

*Open any source file (e.g., `example.py`).*  
Select a few lines, then run the extension’s **“Ask LM Studio”** command (usually `Ctrl+Shift+P → “LM Studio: Ask”`).  

You should see a generated response appear – that means VS Code is successfully talking to your locally‑running model.

---  

## 6️⃣  One‑terminal “kill‑everything” workflow (no daemons, no tmux)  

Because **both** LM Studio and `lm-proxy` run as **foreground** processes, simply closing the terminal (or pressing **Ctrl‑C**) terminates them. No extra cleanup is needed.

### Option A – Two separate tabs (most readable)

1. **Tab 1** – run LM Studio (as shown in **4.1**).  
2. **Tab 2** – run `lm-proxy` (as shown in **4.2**) *or* skip it.  
3. When done, press **Ctrl‑C** in each tab **or** close the tabs.

### Option B – One‑window split panes (built‑in VS Code terminal)

1. Open a VS Code terminal (`Ctrl+` `).  
2. Click the **Split Terminal** button to get two panes.  
3. Run LM Studio in the **left pane**, `lm-proxy` (or nothing) in the **right pane**.  
4. Shut down with **Ctrl‑C** in each pane.

### Option C – `tmux` (if you already love it)

> *You *can* still use `tmux`; the steps are the same, just replace the two tabs with two panes inside a tmux session.*

```bash
tmux new-session -s lm -d "lm-studio --model $MODEL_PATH --host 127.0.0.1 --port 12345 --no-gui"
tmux split-window -h "lm-proxy --host 127.0.0.1 --port 5678 --backend http://127.0.0.1:12345/v1"
tmux attach -t lm
```

Detach with `Ctrl‑b d` and later kill everything with `tmux kill-session -t lm`.

---  

## 7️⃣  Troubleshooting Cheat‑Sheet  

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `curl …/v1/models` → **connection refused** | LM Studio not running or wrong port | Verify LM Studio is still alive (`ps aux | grep lm-studio`). Restart with the correct `--port`. |
| `lm-proxy` logs **“Backend unreachable”** | LM Studio didn’t start, or wrong backend URL | Ensure `--backend http://127.0.0.1:12345/v1` matches the LM Studio port. |
| VS Code shows **“Invalid API key”** | Extension requires a non‑empty key | Enter any string (e.g., `local‑key`). |
| Model never loads (stuck on “Loading …”) | Not enough RAM/VRAM for model size | Choose a smaller GGUF, or add `--cpu` to force CPU inference. |
| **Port already in use** (e.g., 12345) | Another process already bound it | Kill the old process (`kill <pid>`) or pick a free port (e.g., `--port 12456`). |
| GPU not used (slow inference) | CUDA drivers missing or `--device` not set | Install NVIDIA driver + CUDA toolkit, then launch LM Studio with `--device cuda` (or `--device auto`). |
| Want a simple auth token for the proxy | `lm-proxy` can enforce a bearer token | Start it with `--auth-token mySecret`. Then put `mySecret` into the VS Code *API Key* field. |
| Running on Apple Silicon (M1/M2) | Need a model compiled for `apple`/`cpu` | Use a model such as `gemma-2b-it-q4_k_m.gguf` that is arm‑compatible. No extra flags needed. |

---  

## 8️⃣  Full‑copy‑paste “cheat‑sheet” (no tmux)  

```bash
# ── 1️⃣ Install / upgrade ────────────────────────────────────────
brew install --cask lm-studio               # macOS (or upgrade with `brew upgrade --cask lm-studio`)
python3 -m pip install --upgrade lm-proxy   # optional proxy, skip if you don't need it

# ── 2️⃣ Start LM Studio (head‑less) ─────────────────────────────────
MODEL="$HOME/.cache/lm-studio/models/tiny-llama-1.1b-chat-v1.0.Q4_K_S.gguf"
lm-studio \
  --model "$MODEL" \
  --host 127.0.0.1 \
  --port 12345 \
  --no-gui                                   # stays in this terminal tab

# (Leave this tab open)

# ── 3️⃣ (Optional) Start lm‑proxy in a second tab ─────────────────────
lm-proxy \
  --host 127.0.0.1 \
  --port 5678 \
  --backend http://127.0.0.1:12345/v1

# ── 4️⃣ Verify the chain works ───────────────────────────────────────
curl http://127.0.0.1:5678/v1/models   # if you used the proxy
#   or
curl http://127.0.0.1:12345/v1/models # direct LM Studio

# ── 5️⃣ Configure VS Code
#   • Settings → “LM Studio: API Base URL” → http://127.0.0.1:5678/v1  (proxy)  
#   • or → http://127.0.0.1:12345/v1 (direct)  
#   • API Key → any non‑empty string (e.g., “local-key”)  
#   • Model name → whatever you saw in the JSON response
```

When you’re done, simply close the two terminal tabs (or hit **Ctrl‑C** in each). All processes exit cleanly.

---  

## 9️⃣  Quick “Ask the model” from the command line (no VS Code needed)  

```bash
curl -X POST http://127.0.0.1:5678/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "tiny-llama-1.1b-chat-v1.0.Q4_K_S",
        "messages": [{"role":"user","content":"Tell me a short joke about AI"}],
        "max_tokens": 64,
        "temperature": 0.7
      }' | python3 - <<'PY'
import sys, json, textwrap
data = json.load(sys.stdin)
print("\n--- Model answer ---\n")
print(textwrap.fill(data["choices"][0]["message"]["content"], width=80))
PY
```

You should see a short joke printed, confirming the full pipeline works end‑to‑end.

---  

## 🎉  You’re all set!  

* One terminal tab runs **LM Studio** in headless mode.  
* (Optional) a second tab runs **`lm-proxy`** to expose a different port or add a simple token.  
* VS Code is configured to talk to the chosen URL with a dummy API key.  
* Closing the terminals (or pressing **Ctrl‑C**) stops everything – **no daemons, no background services, no tmux required**.  



## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the purpose of `lm-proxy` and is it required for modern LM Studio versions?"
    `lm-proxy` is an optional proxy that can add features like authentication tokens. It is not required for modern LM Studio versions as they now ship with a native OpenAI-compatible API.

??? question "Which flag is used to run LM Studio in headless mode (no GUI)?"
    The `--no-gui` flag is used to start LM Studio as a foreground process in the terminal without launching the graphical user interface.

??? question "How do you verify that the LM Studio server is responding via the command line?"
    You can use a `curl` command to request the list of models: `curl http://127.0.0.1:12345/v1/models`.

Happy coding and happy prompting with your locally‑run LLM! 🚀