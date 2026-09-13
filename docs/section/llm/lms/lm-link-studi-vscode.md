
# Tutorial: Run Local or Remote LLM Models to access in VSCode

We describe how we use  **LM Studio**, **LM Link**, and **VS Code** together from a single terminal while we do not use background daemons.

This guide shows you how to:

1. **Install** the three tools.
2. **Start** LM Studio and LM Link **in the foreground** from a terminal window.
3. **Configure** VS Code to talk to the locally‑running LM Studio server via LM Link.
4. **Stop** everything simply by closing the terminal (or pressing `Ctrl‑C`).

> **Why “no daemons”?**  
> By launching the services in the same terminal session, they run as regular foreground processes. When you kill the terminal, the processes terminate automatically—no extra service managers or background tasks are needed.

---

## 1. Prerequisites

| What you need | Details |
|---------------|---------|
| **Operating System** | Linux, macOS, or Windows (WSL2 works too) |
| **Python** | ≥ 3.9 (for LM Link) |
| **Git** | Optional – for cloning example repos |
| **Internet** | To download model files the first time |
| **GPU (optional)** | If you want hardware‑accelerated inference. LM Studio will fall back to CPU if no GPU is detected. |

---

## 2. Install the three components

### 2.1 LM Studio (the inference engine)

| Platform | Command |
|----------|---------|
| **macOS (Homebrew)** | `brew install --cask lm-studio` |
| **Ubuntu/Debian** | ```bash<br>curl -L -o lm-studio.deb https://github.com/lmstudio-ai/lm-studio/releases/latest/download/lm-studio_ubuntu_amd64.deb<br>sudo dpkg -i lm-studio.deb<br>``` |
| **Windows** | Download the installer from the [LM Studio releases page](https://github.com/lmstudio-ai/lm-studio/releases) and run it. The installer also puts a `lm-studio.exe` binary in `C:\Program Files\LM Studio\` which is added to your `PATH`. |

> **Tip** – After installation, you can check the binary is reachable:  
> ```lm-studio --help```


### 2.2 LM Link (OpenAI‑compatible proxy)

LM Link is a tiny Python package that forwards `POST /v1/chat/completions` (and other endpoints) to the LM Studio server.

```bash
python -m pip install --upgrade lm-link
```

> **Verification**: `lm-link --version` should print something like `0.2.0`.

### 2.3 VS Code + LM Studio extension

1. **Install VS Code** – if you haven’t already: <https://code.visualstudio.com/>
2. **Open VS Code → Extensions** (⇧⌘X on macOS, Ctrl‑Shift‑X on Windows/Linux).
3. **Search for “LM Studio”** and install the official extension (or any “OpenAI‑compatible” client you prefer, e.g., “ChatGPT‑Assistant”).

> The extension only needs an **API base URL** and **API key**. We’ll use a dummy key because LM Link does **not** validate it.

---

## 3️⃣ Run the services from a terminal (foreground)

Open a **single** terminal window (or a multiplexer like `tmux`/`screen` if you like).

### 3.1 Start LM Studio in head‑less mode

```bash
# Replace <model> with the model you want to use.
# Example: The default “tiny-llama-1.1b-chat-v1.0.Q4_K_S.gguf”
# You can also specify a full path to a local model file.

lm-studio \
  --model <model> \
  --host 127.0.0.1 \
  --port 12345 \
  --no-gui   # <-- forces head‑less (no window) mode
```

**Explanation of flags**

| Flag | Meaning |
|------|---------|
| `--model` | Path/identifier of the GGUF model you wish to run. |
| `--host` | Bind address – `127.0.0.1` is enough for local use. |
| `--port` | Port used by LM Studio’s OpenAI‑compatible endpoint. |
| `--no-gui` | Prevents the desktop UI from opening; the process stays in the terminal. |

> **When you see** `[*] Running on http://127.0.0.1:12345/v1`, LM Studio is ready.

> **Tip** – Add `--max-gpu-batch-size 32` or other performance flags if you have a GPU. Run `lm-studio --help` for the full list.

### 3.2 Start LM Link (the proxy)

Open a **second** terminal tab **or** keep the current one and launch LM Link in the *background* of the same shell (still foreground overall). I recommend a separate tab so you can see its logs.

```bash
lm-link \
  --host 127.0.0.1 \
  --port 5678 \
  --backend http://127.0.0.1:12345/v1
```

**What this does**

| Flag | Meaning |
|------|---------|
| `--host` | Where LM Link itself listens (normally localhost). |
| `--port` | Port you’ll point VS Code at (e.g., 5678). |
| `--backend` | The URL of the LM Studio server started above. |

You should now see a line like:

```
[INFO] Proxy listening on http://127.0.0.1:5678/v1 → http://127.0.0.1:12345/v1
```

### 3.3 Verify the chain works (optional)

```bash
curl http://127.0.0.1:5678/v1/models
```

Expected JSON (truncated) shows the model name:

```json
{
  "object": "list",
  "data": [
    {
      "id": "llama-3-8b-instruct-q4_k_m",
      "object": "model",
      "owned_by": "local"
    }
  ]
}
```

If you get a JSON response, the pipeline is healthy.

---

## 4️⃣ Wire VS Code to the local endpoint

1. **Open VS Code → Settings** (`Ctrl+,`).
2. Search for **“OpenAI API Base URL”** (the exact name depends on the extension; for the official LM Studio extension it’s *LM Studio: API Base URL*).
3. **Set it to** `http://127.0.0.1:5678/v1`.
4. **Set the API key** to any non‑empty string, e.g., `lmstudio-local`. LM Link ignores the key but the extension requires something.
5. (Optional) Adjust **model name** in the extension UI to match the model you launched, e.g., `llama-3-8b-instruct-q4_k_m`.

### 4.1 Test inside VS Code

*Open any file (e.g., `example.py`).*  
Select a few lines of code, then run the extension’s **“Ask LM Studio”** command (usually `Ctrl+Shift+P → “LM Studio: Ask”`).

You should see a response pop‑up generated by the model you started earlier. If it works, everything is correctly wired.

---

## 5️⃣ One‑terminal “kill‑everything” workflow (no daemons)

Because **both LM Studio** and **LM Link** are foreground processes, you can keep them in the **same terminal session** using a simple process manager like `&` (background) **or** a multiplexer. The *simplest* way:

```bash
# 1️⃣ Start LM Studio (foreground)
lm-studio --model <model> --host 127.0.0.1 --port 12345 --no-gui
```

Leave that terminal open. In a **second tab** (or split pane) start LM Link:

```bash
lm-link --host 127.0.0.1 --port 5678 --backend http://127.0.0.1:12345/v1
```

Now you have two tabs, each showing logs. When you’re done:

* **Press `Ctrl‑C`** in **both** tabs (or close the terminal window).  
* The processes exit, and there are no lingering background services.

### Alternative: single‑command start with `tmux` (one window, two panes)

If you prefer a single terminal window:

```bash
# Start a new tmux session called "lm"
tmux new-session -s lm -d "lm-studio --model <model> --host 127.0.0.1 --port 12345 --no-gui"
tmux split-window -h "lm-link --host 127.0.0.1 --port 5678 --backend http://127.0.0.1:12345/v1"
tmux attach -t lm
```

Now you have two panes side‑by‑side. **Detach** with `Ctrl‑b d` and **kill the whole session** with `tmux kill-session -t lm`. All child processes stop automatically.

---

## 6️⃣ Troubleshooting Cheat‑Sheet

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `curl …/v1/models` returns *connection refused* | LM Studio not running on the expected port | Verify the `--port` you passed to LM Studio and that the process is still alive (`ps aux | grep lm-studio`). |
| LM Link logs “Backend unreachable” | Wrong backend URL or LM Studio crashed | Ensure the `--backend` URL matches LM Studio’s host/port. Restart LM Studio if it exited. |
| VS Code says “Invalid API key” | Extension insists on a non‑empty key, but LM Link ignores it | Put any dummy string, e.g., `lmstudio-local`. |
| Model never loads (stuck on “Loading …”) | Not enough RAM/VRAM for the model size | Choose a smaller GGUF file (`tiny-…`), or use `--cpu` flag to force CPU. |
| `lm-link` says “Port already in use” | Something else already listening on 5678 | Pick a free port, e.g., `--port 7777`, and update VS Code accordingly. |
| GPU not used (performance is very slow) | LM Studio started in CPU‑only mode or CUDA drivers missing | Install proper NVIDIA drivers + `torch` with CUDA, then start LM Studio with `--device cuda`. |

---

## 7️⃣ Summary of Commands (copy‑paste friendly)

```bash
# 1️⃣ Install (run once)
# macOS
brew install --cask lm-studio
# Linux (Ubuntu/Debian)
curl -L -o lm-studio.deb https://github.com/lmstudio-ai/lm-studio/releases/latest/download/lm-studio_ubuntu_amd64.deb
sudo dpkg -i lm-studio.deb
# Python tool (cross‑platform)
python -m pip install --upgrade lm-link

# 2️⃣ Start LM Studio (foreground)
lm-studio \
  --model /path/to/your/model.gguf \
  --host 127.0.0.1 \
  --port 12345 \
  --no-gui

# 3️⃣ In another terminal tab, start LM Link
lm-link \
  --host 127.0.0.1 \
  --port 5678 \
  --backend http://127.0.0.1:12345/v1

# 4️⃣ Quick health‑check
curl http://127.0.0.1:5678/v1/models
```

When you close *both* terminal tabs (or press `Ctrl‑C`), **everything stops**—no daemon, no lingering background service.

---

## 8️⃣ Bonus: Quick “Ask‑the‑model” from the command line

If you want to test the whole stack without VS Code, you can use `curl` directly:

```bash
curl http://127.0.0.1:5678/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "llama-3-8b-instruct-q4_k_m",
        "messages": [{"role":"user","content":"Tell me a short joke about AI."}],
        "max_tokens": 64,
        "temperature": 0.7
      }' | jq .choices[0].message.content
```

You should see a short joke printed to the console—proving that LM Studio → LM Link → client works end‑to‑end.

---

### 🎉 You’re all set!

* **One terminal** starts LM Studio (headless).  
* **A second terminal** runs LM Link (proxy).  
* **VS Code** talks to `http://127.0.0.1:5678/v1`.  
* **Close the terminals** → everything terminates automatically.


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the function of `lm-link` in the connection chain between VS Code and LM Studio?"
    `lm-link` acts as an OpenAI-compatible proxy that forwards API requests from clients (like the VS Code extension) to the underlying LM Studio server.

??? question "How do you stop the `lm-studio` and `lm-link` services when they are run in the foreground?"
    Since they are run as foreground processes, you can stop them by simply closing the terminal window or pressing `Ctrl-C` in the active terminal.

??? question "If VS Code shows \"Invalid API key\" when connecting to LM Link, how should you resolve it?"
    Because LM Link ignores the API key but the VS Code extension requires a non-empty string, you should enter any dummy text (e.g., `local-key`) into the API Key field.

