Here is the updated documentation including a section for Windows terminal recording options.

---

# Terminal Recordings and Screenshots

In Linux, macOS, and Windows, you can record and replay terminal sessions or capture your screen using several utilities.

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



> **Security Warning:** Before publishing recordings to public repositories (such as GitHub documentation), verify that you have not exposed sensitive information, including API keys, passwords, internal IP addresses, or usernames.

## Capturing Screenshots

* **macOS Interactive Area Capture (GUI):** Press `SHIFT + COMMAND + 4` and select the area you want to capture.
* **macOS Command Line Capture:** Use the native `screencapture` utility:
```bash
screencapture -i a.png

```

* **Windows Interactive Area Capture (GUI):** Press `WIN + SHIFT + S` to open the Snipping Tool and select the area you want to capture.

