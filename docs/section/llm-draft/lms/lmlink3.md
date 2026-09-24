Here is the up-to-date guide reflecting the modern native `lms` utility. LM Studio integrates a lightweight background engine (`llmster`) managed through `lms`, allowing you to switch seamlessly between terminal usage and the desktop GUI without conflicting flags or broken Electron window hacks.

---

# Tutorial: Run Local Models via Terminal or GUI and Access Them from VS Code (macOS / Linux / Windows)

*This guide uses **`lms`**, LM Studio's official companion CLI tool. It allows you to run models headless via the command line or use the desktop GUI app interchangeably.*

---

## 1️⃣ Prerequisites & Installation

| Requirement | Details |
| --- | --- |
| **OS** | macOS (Sonoma or newer), Linux (AppImage/Debian), or Windows 10/11 |
| **LM Studio** | Download and install the desktop application from the [official site](https://lmstudio.ai/). |
| **VS Code** | With the official **LM Studio** extension installed from the marketplace. |

### 1.1 Bootstrap the CLI Tool

The command-line tool `lms` ships inside your LM Studio installation. Open your terminal and run the bootstrap command once to make it globally accessible:

```zsh
~/.lmstudio/bin/lms bootstrap

```

> **Verify it works:**
> ```zsh
> lms --version
> 
> ```
> 
> 

---

## 2️⃣ Managing Models from the Terminal

You can list, download, and check running models straight from your shell:

* **List downloaded models available on disk:**
```zsh
lms ls

```


* **Search and download a model:**
```zsh
lms get <model-identifier-or-huggingface-url>

```


* **Check what models are currently active in memory:**
```zsh
lms ps

```



---

## 3️⃣ Running Headless via CLI (Alternative to the GUI)

If you want to run inference entirely in the terminal without launching the desktop window, use the built-in daemon and server commands:

1. **Start the Daemon:** Background Engine.
Boot up the background inference service:

```zsh
lms daemon up

```


2. **Start the Server:** OpenAI-Compatible Endpoint.
Launch the server on your preferred port (e.g., `12345`):

```zsh
lms server start --port 12345

```


3. **Load a Model and Test:** Load and Query.
Load one of your downloaded models into memory:

```zsh
lms load <your-model-name>

```

Verify the server is responding:

```zsh
curl http://127.0.0.1:12345/v1/models

```


When you are finished with the terminal session, you can stop the server or spin down the daemon completely:

```zsh
lms server stop
lms daemon down

```

---

## 4️⃣ Using the Desktop GUI When Preferred

Because `lms` talks to the same underlying daemon layer that the desktop app uses, **you can open the normal LM Studio desktop application at any time**.

* **To use the GUI:** Simply launch **LM Studio** from your Applications folder or desktop shortcut like normal. It will automatically detect models, allow you to use the visual chat interface, or let you click the **Local Server** tab to toggle the server visually.
* **To return to CLI/Headless use:** Just close the desktop application window. If you want the API server active without the window, use `lms server start`.

---

## 5️⃣ Configure VS Code to Talk to LM Studio

1. Open VS Code Settings (`⌘+,` on macOS, `Ctrl+,` on Windows/Linux).
2. Search for **“LM Studio: API Base URL”**.
3. Set the URL to your active server endpoint:
* **`[http://127.0.0.1:12345/v1](http://127.0.0.1:12345/v1)`** (or whatever port you designated via `lms server start`).


4. Set the **API Key** field to any non-empty string (e.g., `local-key`).
5. Open any code file, highlight text, and run the command palette (`Ctrl+Shift+P` / `⇧⌘P`) to select **“LM Studio: Ask”**.



## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What does the `lms daemon up` command do?"
    It starts the background inference engine, which manages the loading and unloading of models across the system.

??? question "How do you start an OpenAI-compatible server on a specific port using `lms`?"
    You use the command `lms server start --port <port>`, where `<port>` is your desired port number (e.g., 12345).

??? question "What is the benefit of using `lms` CLI over the GUI for model management?"
    The CLI allows for headless operation, enabling automation via scripts and easier management of models on remote servers without needing a graphical interface.

---