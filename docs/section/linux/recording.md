# Terminal Recordings and Screenshots

!!! info "Learning Objectives"

    By the end of this section, you will be able to:
    * **Understand** the value of terminal recordings versus static screenshots for technical documentation and debugging.
    * **Compare and contrast** various recording tools (`script`, `asciinema`, `TermRecord`) based on output format and use case.
    * **Demonstrate** the ability to record, replay, and share terminal sessions across Linux, macOS, and Windows.
    * **Apply** security best practices to identify and redact sensitive information (secrets, keys, IPs) from recordings before publication.

## Introduction
When creating technical documentation, tutorials, or bug reports, static screenshots often fall short because they cannot capture the timing, pacing, and flow of a command-line interaction. Terminal recordings allow you to share a "living" document that others can watch as if they were sitting at your console, making them far more effective for demonstrating complex workflows.

## Comparison of Recording Tools

| Tool | Platform | Output Format | Best Use Case |
| :--- | :--- | :--- | :--- |
| `script` | Linux/macOS | `.typescript` (Text) | Quick local captures, system auditing |
| `asciinema` | All | `.cast` (JSON) | High-quality web embedding, professional sharing |
| `TermRecord` | Linux/macOS | `.html` | Standalone portable documentation |
| `Start-Transcript`| Windows | `.txt` | Simple audit logs, text-based records |

---

## Terminal Recording Tools

### 1. Built-in: `script` (Linux / macOS)
The `script` utility is preinstalled on almost all Unix-like systems, meaning it is immediately available without installing extra packages.

To record a session with timing data:
```bash
script -t 2> timing.file output.typescript
```

To stop recording, type `exit`. To replay the session:
```bash
scriptreplay timing.file output.typescript
```

### 2. `asciinema` (Linux / macOS / Windows)
`asciinema` records text-based terminal sessions into lightweight files that can be embedded in web pages or shared online. It is cross-platform and works on Windows via the Windows Subsystem for Linux (WSL) or native package managers.

```bash
# macOS Installation via Homebrew
brew install asciinema

# Windows Installation via winget (in PowerShell or Command Prompt)
winget install asciinema.asciinema

# Record your session
asciinema rec recording.cast

# Play back your session locally
asciinema play recording.cast
```

### 3. `TermRecord` (Linux / macOS)
If you need a standalone HTML file that can be opened in a browser:

**macOS Installation:**
```bash
brew install ttyrec
pip install TermRecord
```

**Usage:**
```bash
TermRecord -o recording.html
```

You can preview it from the command line using a browser such as Google Chrome:
```bash
google-chrome recording.html
```

### 4. Windows Native Alternatives
For Windows (PowerShell or Command Prompt), native terminal recording can be handled through built-in tools or utilities:

* **Windows Terminal Command Palette / Screen Capture:** If you use Windows Terminal, you can use built-in broadcasting or external screen recording tools (such as Windows Game Bar via `WIN + G`) to capture your console window.
* **PowerShell Transcript Logging:** You can natively record all PowerShell input and output to a text file for documentation purposes:
```powershell
# Start recording
Start-Transcript -Path "C:\path\to\recording.txt"

# Stop recording
Stop-Transcript
```

---

## Capturing Screenshots
Sometimes a single image is more efficient than a recording.

### macOS
* **Interactive Area Capture (GUI):** Press `SHIFT + COMMAND + 4` and select the area you want to capture.
* **Command Line Capture:** Use the native `screencapture` utility:
```bash
screencapture -i a.png
```

### Windows
* **Interactive Area Capture (GUI):** Press `WIN + SHIFT + S` to open the Snipping Tool and select the area you want to capture.
* **Full Screen Capture:** Press the `Print Screen` (PrtSc) key to copy the entire screen to the clipboard.

### Linux
Depending on your desktop environment (GNOME, KDE, XFCE), the tools may vary:
* **GUI Capture:** Press the `Print Screen` key to capture the whole screen, or `ALT + Print Screen` to capture the currently active window.
* **GNOME Screenshot:** Use the built-in screenshot utility or run `gnome-screenshot -i` from the terminal for an interactive selector.
* **Command Line (scrot):** If installed, you can use `scrot` for quick captures:
```bash
# Install scrot
sudo apt install scrot

# Capture the current screen
scrot screenshot.png
```

---

## Security: Avoiding Recording Secret Information

> **CRITICAL WARNING:** Before publishing recordings to public repositories (such as GitHub), you must verify that you have not exposed sensitive information, including API keys, passwords, internal IP addresses, or usernames.

### 1. Pre-Recording Prevention: Environment Isolation
The safest approach is to avoid exposing secrets in the terminal environment entirely:
* **Use Dummy Credentials:** Use placeholder values (e.g., `API_KEY=your_key_here`) instead of real production keys.
* **Source Environment Variables from Files:** Load sensitive configuration from a separate `.env` file that is not echoed to the screen, or export them before starting the recording session.

### 2. Post-Recording Editing (`asciinema`)
Since `asciinema` records as plain-text JSON, you can edit the `.cast` file manually:
1. Open the `.cast` file in a text editor.
2. Locate lines containing sensitive text in the output frames `[timestamp, event_type, text]`.
3. Replace the sensitive string with asterisks or dummy text.

### 3. Dedicated Redaction Tools
For automated scrubbing:
* **Scrubbing scripts:** Write a short Python or `sed` script to parse your output logs and regex-replace known patterns (e.g., AWS keys, Bearer tokens) before rendering or publishing.

---

## AI-Enhanced Documentation
Since you are working with AI tools, you can leverage LLMs to transform raw recordings into professional documentation:

1. **Transcript to Tutorial:** Copy the text output of a `script` or `Start-Transcript` session and provide it to an LLM. Ask it to: *"Convert this terminal transcript into a structured Markdown tutorial with step-by-step explanations and formatted code blocks."*
2. **AI-Powered Redaction:** Use an LLM to identify potentially sensitive patterns in a transcript that you might have missed manually.

---

## Assignments

!!! note "Assignment 1: Basic Capture & Playback"
    **Task:** Use `script` or `asciinema` to record a session where you:
    1. Create a new directory called `lecture-test`.
    2. Create a file inside it using `echo "Hello World" > test.txt`.
    3. List the directory contents.
    **Deliverable:** Submit the recording file and a screenshot of the playback.

!!! note "Assignment 2: The Documentation Workflow"
    **Task:** Record a short tutorial (3-5 commands) using `asciinema`. Embed the link (via asciinema.org) or the local file into a small Markdown file that explains what the recording demonstrates.
    **Deliverable:** A Markdown file containing the recording link/file and a brief description.

!!! note "Assignment 3: The Redaction Challenge"
    **Task:** 
    1. Record a session where you "accidentally" export a fake secret: `export API_KEY=sk-1234567890abcdef`.
    2. Use the manual editing technique or a `sed` script to redact that key from the recording file.
    **Deliverable:** Both the original (unredacted) and the final (redacted) files, with a brief explanation of the method used.

!!! note "Assignment 4: Cross-Platform Screen Captures"
    **Task:** Capture a screenshot of your terminal window on the following platforms:
    1. **macOS**: Use either the GUI shortcut (`SHIFT + COMMAND + 4`) or the `screencapture` command.
    2. **Windows**: Use the Snipping Tool (`WIN + SHIFT + S`).
    3. **Linux**: Use the `Print Screen` key or a tool like `gnome-screenshot`.
    *(Note: If you do not have access to all three, use Virtual Machines or Cloud-based desktops to complete this).*
    **Deliverable:** Three screenshot files, clearly labeled by the operating system used.
