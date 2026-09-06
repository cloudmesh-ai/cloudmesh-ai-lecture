# Tutorial: Getting Started with the Zed Editor (`zed.dev`)

!!! info "Learning Objectives"
    By the end of this tutorial, you will be able to:
    * Understand the hardware requirements for Zed, including GPU availability and CPU fallback options.
    * Install and launch Zed on macOS, Linux, or Windows from the command line or desktop installer.
    * Navigate the interface using essential keyboard shortcuts and the command palette.
    * Configure user settings, themes, and optional keymap bindings using JSON files.
    * Extend the editor by installing language support and custom extensions.
    * Utilize integrated AI features such as the inline assistant and agent panel.

---

## 1. Setup & Installation

### Installation
Zed is available for macOS, Linux, and Windows. 

* **Direct Download:** Head over to [zed.dev](https://zed.dev) to download the installer for your platform.
* **Command Line Launch:** Once installed, you can open any project directory directly from your terminal using:
```bash
zed ~/projects/my-app
```

### System Requirements & GPU Acceleration
Zed is designed for high performance and utilizes the GPU for rendering the interface.

* **GPU Acceleration:** For the best experience, a compatible GPU is recommended.
* **CPU Fallback:** If you are on a machine without a dedicated GPU (e.g., a headless server, an older laptop, or a VM), Zed can still run using software-based OpenGL/Vulkan implementations. Note that you may experience higher CPU usage or lower frame rates during heavy UI interactions.

---

## 2. Getting Oriented: The "Zed Way"

Zed relies heavily on a **Command Palette** workflow, reducing the need to hunt through menus.

### The Command Palette
The Command Palette is the heart of Zed. If you don't know the shortcut for an action, you can find it here:
* **macOS:** `Cmd + Shift + P`
* **Linux / Windows:** `Ctrl + Shift + P`

### Essential Navigation Shortcuts
Once you are comfortable with the palette, these shortcuts will significantly speed up your workflow:

| Action | macOS | Linux / Windows |
| :--- | :--- | :--- |
| **Go to File** | `Cmd + P` | `Ctrl + P` |
| **Find in Project** | `Cmd + Shift + F` | `Ctrl + Shift + F` |
| **Go to Symbol** | `Cmd + Shift + O` | `Ctrl + Shift + O` |
| **Toggle Terminal** | `Ctrl + ` ` | `Ctrl + ` ` |
| **Open Settings** | `Cmd + ,` | `Ctrl + ,` |

---

## 3. Personalizing Your Editor

Zed uses a JSON-based configuration model, allowing for precise control over the editor's behavior.

### User Settings
You can access your settings via `Cmd/Ctrl + ,`. Here is an example of a common starting configuration:

```json
{
  "theme": "One Dark",
  "buffer_font_family": "JetBrains Mono",
  "buffer_font_size": 14,
  "format_on_save": "on",
  "vim_mode": false
}
```

* **Themes:** Quickly switch themes using `Cmd/Ctrl + K, Cmd/Ctrl + T`.
* **Vim Mode:** To enable modal editing, set `"vim_mode": true` in your settings.

### Extending Zed
While Zed comes with built-in support for many languages (Rust, JS/TS, Python), you can add more via extensions:

1. Open the **Extensions View**: `Cmd/Ctrl + Shift + X`.
2. Search for a language (e.g., Go, PHP) or a theme/icon pack.
3. Click **Install**.

---

## 4. Leveraging Built-In AI Features

One of Zed's most powerful aspects is its deep integration of AI directly into the coding flow.

### Inline Assistant
For quick refactors, bug fixes, or code generation:
* **Shortcut:** `Cmd + Enter` (macOS) or `Ctrl + Enter` (Linux/Windows).
* **Use Case:** Highlight a block of code and ask the AI to "optimize this loop" or "add error handling."

### The Agent Panel
For project-wide context and complex architectural questions:
* **Shortcut:** `Cmd + Shift + A` (macOS) or `Ctrl + Shift + A` (Linux/Windows).
* **Capability:** The Agent can read, search, and edit multiple files across your project to implement features or find bugs.

### Configuring AI Providers
You can choose your preferred AI backend in the **Agent Settings**:
* **Zed-hosted models**: Quick start with Zed's default offerings.
* **Custom API Keys**: Connect your own Anthropic or OpenAI keys.
* **Gateways**: Route requests through services like OpenRouter.

---

## Hands-on Exercise

!!! note "Zed Quick-Start Challenge"
    **Task:** Perform the following sequence to familiarize yourself with the editor:
    1. **Launch**: Open a project folder from your terminal using the `zed` command.
    2. **Configure**: Open settings and change your `buffer_font_size` to `16` and set `format_on_save` to `"on"`.
    3. **Navigate**: Use `Cmd/Ctrl + P` to find a file and `Cmd/Ctrl + Shift + O` to jump to a specific function/symbol within that file.
    4. **Extend**: Install one new language extension or theme from the Extensions view.
    5. **AI**: Use the **Inline Assistant** to add a docstring or comment to a function in your code.
    **Deliverable:** A screenshot of your modified settings file and the result of the AI-generated comment.
