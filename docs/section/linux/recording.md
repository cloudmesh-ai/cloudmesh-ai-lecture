# Terminal Captures and Recordings

!!! note "Learning Objectives"

    * **Understand** the a-priori decision process of when to use screenshots, ASCII text, or terminal recordings.
    * **Demonstrate** the ability to capture screens and terminal sessions across Linux, macOS, and Windows.
    * **Compare and contrast** various recording tools (`script`, `asciinema`, `TermRecord`) based on output format and use case.
    * **Apply** security best practices to identify and redact sensitive information (secrets, keys, IPs) from recordings before publication.

## Introduction

When documenting technical workflows, choosing the right medium for your evidence is critical. 

**Screenshots** are sufficient when you need to show a final state, a specific error message, or the visual layout of a tool. They are the fastest to produce and consume for a single "point in time."

**ASCII copy-pasting** is best when the content is the priority. It makes your documentation searchable, accessible to screen readers, and allows users to copy commands directly.

**Terminal recordings** are necessary when the *process* is as important as the result. Use them to demonstrate a sequence of commands, show the timing of a process, or guide a user through a live interaction.

## Comparison of Capture Methods

| Method | Format | Searchable | Interactive | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Screenshot** | Image (`.png`, `.jpg`) | No | No | Static states, UI layout, quick proofs |
| **ASCII Text** | Markdown (```` ``` ````) | Yes | No | Reference guides, searchable logs, API outputs |
| **Recording** | Video/Cast (`.cast`, `.html`) | Partial | Yes | Tutorials, timing demos, complex workflows |

---

## Screenshots

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

## Alternative: Copy-Pasting ASCII Output
In many cases, the most effective way to document terminal output is not by recording a video or taking a screenshot, but by simply copying and pasting the text output directly into your documentation using Markdown code blocks (```` ``` ````).

### Example
Instead of a screenshot of `ls -la`, you provide:

```bash
$ ls -la
total 12
drwxr-xr-x  2 user user 4096 Oct 10 10:00 .
drwxr-xr-x 20 user user 4096 Oct 10 09:00 ..
-rw-r--r--  1 user user  123 Oct 10 10:00 test.txt
```

### Advantages
* **Searchability**: Text inside code blocks is indexed and searchable by browsers and documentation tools.
* **Copy-Paste Friendly**: Users can copy commands or specific output values (like a generated ID) directly from your documentation.
* **Accessibility**: Screen readers can process text, whereas they cannot read content inside images or recorded videos.
* **Maintenance**: If a command or output changes slightly, you can edit the text in seconds without having to re-record a session or retake a screenshot.
* **Performance**: Text blocks load instantly and do not require external players or large image files.

### Disadvantages
* **Loss of Timing**: You cannot convey how long a process takes or the pacing of the interaction.
* **Loss of "Live" Feel**: The interactive nature of a terminal (cursor movement, typing speed) is lost.
* **Length**: For extremely long outputs, text blocks can make the page cumbersome (though this can be mitigated using `<details>` tags).

---

## Terminal Recordings

| Tool | Platform | Output Format | Playback | Best Use Case |
| :--- | :--- | :--- | :--- | :--- |
| `script` | Linux/macOS | `.typescript` (Text) | `scriptreplay` | Local auditing, quick captures |
| `asciinema` | All | `.cast` (JSON) | Web/CLI (`play`) | Professional tutorials, web embedding |
| `TermRecord` | Linux/macOS | `.html` | Web Browser | Portable, standalone documentation |
| `Start-Transcript` | Windows | `.txt` | Text Editor | Simple PowerShell audit logs |

---


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

!!! note "Assignment 5: The Markdown Documentation Challenge"
    **Task:** 
    1. Run a command that produces a multi-line output (e.g., `df -h` or `ip addr`).
    2. Copy the output and paste it into a Markdown file using a bash code block.
    3. Add a brief explanation above the block describing what the command does and a brief analysis of one line of the output.
    **Deliverable:** A Markdown file containing the formatted output and your explanation.
