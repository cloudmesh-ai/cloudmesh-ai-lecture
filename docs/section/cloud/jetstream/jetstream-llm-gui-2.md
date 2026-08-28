
**Setting Up LLM‑Powered Extensions in Visual Studio Code**  
*Continue (dev) + Cline (formerly Claude Dev)*  

Both extensions let you interact with a Large Language Model (LLM) from inside VS Code, but they store their configuration in different places.

| Extension | Where the configuration lives | Typical use‑cases |
|-----------|------------------------------|-------------------|
| Continue | `config.yaml` (core layout file) – can be opened and edited from the UI | Chat, code‑refactoring, agent‑style tasks, inline completions |
| Cline | Dedicated **Settings panel** in the Cline sidebar (no file editing) | Autonomous agent that can read/write files and run terminal commands |

---

## 1. Choosing a UI option

| Option | When to use it | How to enable |
|--------|----------------|---------------|
| AI Assistant (native to VS Code ≥ 1.87) | You have the latest VS Code and prefer a *no‑extension* solution. | Open Settings (`Ctrl+,`) → search **AI Assistant: Enabled** → tick the checkbox. |
| ChatGPT – EasyCode (or another OpenAI‑compatible extension) | You already use an extension for code‑completion or want extra features such as “Insert at cursor”. | Open the Extensions view (`Ctrl+Shift+X`), search **ChatGPT – EasyCode**, and click **Install**. |

---

## 2. Continue – GUI configuration (using `gpt-oss-120b`)

### 2.1 Open the `config.yaml` file (no terminal needed)

| Method | Steps |
|--------|-------|
| Command Palette | Press **Ctrl + Shift + P**, type **Continue: Open config.yaml**, press **Enter**. |
| Gear icon in the Continue sidebar | Click the **Continue** icon on the Activity Bar, scroll to the bottom of the sidebar, click the **gear/settings** icon. The file opens automatically. |

The file opens in an editor tab titled `config.yaml`. Most settings can also be changed through the UI (see the next subsection).

### 2.2 Core configuration UI (no manual YAML editing)

1. Open the **Continue** sidebar (click the “C” icon on the left).  
2. Click the **gear/settings** icon at the top of the sidebar.  
3. You will see three main sections:  
   * **Chat / Refactoring / Agent** – models used for conversational or multi‑file tasks.  
   * **Inline Completion** – models used for low‑latency code completions (autocomplete).  
   * **Advanced** – temperature, context‑window limits, key‑bindings, etc.  
4. **Select a provider** for each section (dropdown):  
   * **Ollama (local)** – free/offline.  
   * **OpenRouter (cloud)** – if you prefer a hosted endpoint.  
   * …or any other provider shown in the list.  
5. **Enter credentials**  
   * For cloud providers paste the API key **or** reference an environment variable using the syntax `${env:YOUR_VAR}`.  
   * For local providers the API‑key field can stay blank; just make sure the backend server is running (e.g., `ollama serve`).  
6. **Choose the model name** – type **`gpt-oss-120b`** (or select it from the dropdown if it appears).  
7. **Adjust optional numeric parameters** (plain numbers only):  
   * **Temperature** – typical range `0.0` – `1.0` (use `0.7` for chat, `0.2` for inline completions).  
   * **Max tokens** – e.g., `300` for chat, `150` for inline completions.  
   * **Context window** – set to the limit of your model, e.g., `4096`.  
8. Click **Save** (or simply close the panel). The UI writes the changes back to `config.yaml` automatically.

### 2.3 Example `config.yaml` block for `gpt-oss-120b`

Open the file via the method in 2.1, replace the existing `models:` section with the block below, then save the file and reload the extension (`Ctrl + Shift + R`).

```yaml
models:
  # Chat / Refactoring / Agent tasks
  chat:
    provider: ollama               # change to "openrouter" if you use the cloud endpoint
    model: gpt-oss-120b           # the 120‑billion‑parameter OSS model
    api_key: ${env:OLLAMA_API_KEY} # leave empty for local Ollama, or use ${env:OPENROUTER_API_KEY} for cloud
    temperature: 0.7
    max_tokens: 300

  # Inline code completions (autocomplete)
  completions:
    provider: ollama
    model: gpt-oss-120b
    temperature: 0.2
    max_tokens: 150

# Optional context providers
context_providers:
  - name: files
    tag: "@files"
    description: "All workspace files"
  - name: git
    tag: "@git"
    description: "Current Git diff"
  - name: search
    tag: "@search"
    description: "Workspace text search"

# Advanced settings
advanced:
  context_window: 4096
  stream: true                     # live‑token streaming
  inline_edit_shortcut: "Alt+Enter"
  chat_panel_shortcut: "Ctrl+Space"
```

*If you are using OpenRouter, replace the `provider` value with `openrouter` and set `api_key` to `${env:OPENROUTER_API_KEY}`.*

### 2.4 Adding context providers (Continue)

| Shortcut you type in chat | What it does |
|---------------------------|--------------|
| `@files` | Includes all files in the current workspace. |
| `@git` | Adds the latest Git diff. |
| `@search <term>` | Performs a workspace‑wide text search and includes the results. |

To add or edit these mappings:

1. In the Continue Settings UI, scroll to **Context Providers**.  
2. Click **Add Provider**, select the source (Files, Git, Search, etc.), and assign a tag (`@files`, `@git`, …).  
3. Click **Save**.

### 2.5 Keyboard shortcuts (Continue)

| Shortcut | Action |
|----------|--------|
| **Ctrl + Space** (default) | Opens the Continue chat panel **or** sends the highlighted code block to the chat. |
| **Alt + Enter** (default) | Opens the inline edit bar inside the current file for on‑the‑spot generation or refactoring. |
| **Ctrl + Shift + R** (default) | Reloads the extension – useful after editing `config.yaml` manually. |

You can change any of these in the **Keybindings** section of the Continue UI (gear → Keybindings).

---

## 3. Cline – GUI configuration (using `gpt-oss-120b`)

### 3.1 Open the Cline settings panel

1. Click the **Cline** icon (ant/robot) in the Activity Bar.  
2. At the top of the Cline sidebar, click the **gear (⚙️) Settings** icon.  

A form‑style UI will appear.

### 3.2 Choose your LLM provider

| Provider | How to set it in the UI |
|----------|------------------------|
| Ollama (local) | 1. In the *Provider* dropdown select **Ollama**. <br>2. Set **Base URL** to `http://localhost:11434` (default Ollama address). <br>3. In the *Model* field type **`gpt-oss-120b`**. |
| OpenRouter (cloud) | 1. In the *Provider* dropdown select **OpenRouter**. <br>2. Paste your OpenRouter API key (or `${env:OPENROUTER_API_KEY}`). <br>3. In the *Model* field type **`gpt-oss-120b`**. |

### 3.3 Optional tuning parameters (Advanced section)

| Setting | Recommended value for a 120 B model |
|---------|--------------------------------------|
| Context Window Limit | `8192` (most 120 B models expose at least an 8 k token window) |
| Temperature | `0.3` – balances creativity and reproducibility for code generation |
| Allowed Terminal Commands | `git, npm, yarn, pip, curl` (adjust to what you trust) |
| Use Compact Prompt (LM Studio & Ollama) | **Enabled** – reduces prompt size by ~90 % and prevents the context window from being exhausted on local back‑ends. |

After you have filled in the fields, click **Done** (or **Save**) to store the settings.

### 3.4 Keyboard shortcuts (Cline)

| Shortcut | Action |
|----------|--------|
| **Ctrl + Alt + C** (default) | Opens the Cline chat panel and automatically adds any selected code as context. |
| **Ctrl + Alt + I** (default) | Opens the inline edit bar inside the current file for on‑the‑spot generation or refactoring. |
| **Ctrl + Shift + R** (default) | Reloads the Cline extension – use after changing the provider or model. |

You can modify these shortcuts via the **Keybindings** button at the bottom of the Cline settings panel.

---

## 4. Quick‑access summary (one‑click view)

| Goal | Continue (GUI) | Cline (GUI) |
|------|----------------|-------------|
| Open the core config file | Command Palette → “Continue: Open config.yaml” or gear icon in Continue sidebar | Not applicable – configuration is UI‑only |
| Select LLM provider | Settings → **Chat / Inline** → **Provider** dropdown (choose **Ollama** or **OpenRouter**) | Settings → **Provider** dropdown in Cline sidebar |
| Enter API key securely | Use `${env:OLLAMA_API_KEY}` for local Ollama (optional) or `${env:OPENROUTER_API_KEY}` for cloud | Same – UI accepts `${env:…}` |
| Choose model | In the same section type **`gpt-oss-120b`** | In the model dropdown type **`gpt-oss-120b`** |
| Add a context keyword (Continue only) | Settings → **Context Providers** → **Add Provider** → set tag (`@files`, `@git`, …) | No built‑in tags – you can paste any text manually |
| Reload after editing | **Ctrl + Shift + R** or click **Reload** button in UI | **Ctrl + Shift + R** in Cline sidebar |
| Open inline edit bar | **Alt + Enter** (default) | **Ctrl + Alt + I** (default) |
| Open chat panel | **Ctrl + Space** (default) | **Ctrl + Alt + C** (default) |

---

## 5. Checklist – Are you ready?

1. **Install the extensions**  
   * Continue – search “Continue” in the Extensions view, click **Install**.  
   * Cline – search “Cline”, click **Install**.  
2. **Start any local servers** (if you chose Ollama)  
   ```bash
   ollama serve                      # starts the Ollama server
   ollama pull gpt-oss-120b          # downloads the model (may take a while)
   ```  
   For OpenRouter you only need the API key; no local server is required.  
3. **Configure the provider and model** as described in sections 2.1 / 2.2 (Continue) and 3.1 / 3.2 (Cline).  
4. **Save** the settings (Continue writes automatically; Cline requires clicking **Done**).  
5. **Reload** the extension (`Ctrl + Shift + R`).  
6. **Test a simple prompt**  
   * Continue – open the chat panel, type “What is the capital of Canada?” → should reply “Ottawa”.  
   * Cline – open its chat panel, type the same prompt → should reply “Ottawa”.  
7. **Add context providers** in Continue if you want `@files`, `@git`, or `@search`.  
8. **Adjust shortcuts** if the defaults clash with other extensions.  
9. **Save** – both extensions persist settings automatically; you can also click **Save** in each panel for certainty.  

---

## 6. Frequently asked questions (model‑specific)

| Question | Answer |
|----------|--------|
| *The model does not appear in the dropdown* | Make sure the model has been pulled for Ollama (`ollama pull gpt-oss-120b`). For OpenRouter verify that your plan includes the model and that the name is typed exactly (`gpt-oss-120b`). |
| *I get “context window exceeded”* | Increase the **Context Window Limit** in Cline’s advanced settings (e.g., to `8192`). In Continue you may lower **max_tokens** or reduce **temperature** to keep prompts smaller. |
| *Performance feels slow* | `gpt-oss-120b` is a very large model. If you run it locally, ensure you have enough RAM/VRAM or enable low‑VRAM mode in Ollama (`ollama run gpt-oss-120b --low-vram`). For cloud usage, consider a smaller model for quick edits and reserve `gpt-oss-120b` for heavyweight reasoning tasks. |
| *Can I use the same model for both chat and autocomplete?* | Yes. In Continue set **Provider** to the same value in both the **Chat** and **Completions** sections and use `gpt-oss-120b` for both. In Cline the single provider applies to all interactions. |
| *Can I store my keys in the VS Code settings file instead of the UI?* | It is possible, but not recommended because the settings file may be committed to source control. Prefer using environment variables (`${env:…}`) in the UI. |
| *How do I see raw request/response for debugging?* | Both extensions have a debug console in their sidebar. In Continue click **Logs → Show raw API**. In Cline click **Debug → Network** to view HTTP payloads. |

---

## 7. Tailored configuration examples (copy‑paste)

### 7.1 Continue – local Ollama for chat **and** inline completions

```yaml
models:
  chat:
    provider: ollama
    model: gpt-oss-120b
    temperature: 0.7
    max_tokens: 300
  completions:
    provider: ollama
    model: gpt-oss-120b
    temperature: 0.2
    max_tokens: 150
context_providers:
  - name: files
    tag: "@files"
    description: "All workspace files"
  - name: git
    tag: "@git"
    description: "Current Git diff"
advanced:
  context_window: 4096
  stream: true
  inline_edit_shortcut: "Alt+Enter"
  chat_panel_shortcut: "Ctrl+Space"
```

1. Open the file via **Command Palette → Continue: Open config.yaml**.  
2. Paste the block, save, then reload the extension (`Ctrl + Shift + R`).

### 7.2 Cline – cloud OpenRouter using `gpt-oss-120b`

1. Open the **Cline Settings** panel (gear icon in the Cline sidebar).  
2. **Provider** → **OpenRouter**.  
3. **API Key** → `${env:OPENROUTER_API_KEY}`.  
4. **Model** → type `gpt-oss-120b`.  
5. **Temperature** → `0.3`.  
6. **Context Window** → `8192`.  
7. Enable **Use compact prompt** (checkbox).  
8. Click **Done**.

Cline will now send all requests to OpenRouter using the selected `gpt-oss-120b` model with a low temperature for reliable code generation.

---

## 8. Where to find more information

| Resource | What you’ll find |
|----------|-------------------|
| Continue documentation – *Configuration* | Full reference for every `config.yaml` field and UI screenshots. |
| Continue YouTube channel | Video walkthroughs of the gear‑icon settings, context providers, and shortcuts. |
| Cline official docs – *Settings* | Step‑by‑step screenshots of the settings panel and advanced options. |
| Ollama docs | Instructions for pulling large models, low‑VRAM mode, and GPU/CPU offloading. |
| OpenRouter model catalogue | List of available models (including `gpt‑oss‑120b`) and pricing. |
| VS Code Keybindings reference | How to edit or override the default shortcuts shown above. |

---

## 9. Next steps

1. **Decide on a deployment** – local Ollama for privacy/offline, or OpenRouter for cloud access.  
2. **Follow the UI steps** in sections 2.1 / 2.2 (Continue) and 3.1 / 3.2 (Cline) to point the extensions at `gpt-oss-120b`.  
3. **Run a quick test** to verify the connection.  
4. **Fine‑tune** the advanced parameters (temperature, context window, allowed commands) to match your workflow.  
5. **Start using the AI** – ask for whole‑file refactors, generate new functions inline, or let Cline execute safe terminal commands without leaving VS Code.  

If you encounter any specific error messages or need a configuration that matches a particular operating system (Windows, macOS, Linux), let me know and I’ll provide a ready‑to‑copy snippet tailored to that environment.