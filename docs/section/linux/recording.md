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

## Avoiding to record secret information

You can prevent sensitive information from being recorded, though most standard terminal recorders capture raw text input and output streams indiscriminately.

Here are the primary ways to handle or remove secret information:

### 1. Pre-Recording Prevention: Environment Isolation

The safest approach is to avoid exposing secrets in the terminal environment entirely during the recording session:

* **Use Dummy Credentials:** Use placeholder values (e.g., `API_KEY=your_key_here`, `password123`) instead of real production keys or passwords.
* **Source Environment Variables from Files:** Load sensitive configuration from a separate, unrecorded file or `.env` file that is ignored by your commands, or export them before starting the recording session so they do not appear in command history or output text.

### 2. Post-Recording Editing (`asciinema`)

If you use `asciinema` to record `.cast` files, the recording is stored as plain-text JSON. You can edit the file manually before sharing it:

1. Open the `.cast` file in a text editor.
2. Locate the lines containing the sensitive text in the output frames (each frame is structured as `[timestamp, event_type, text]`).
3. Replace the sensitive string with asterisks or dummy text (ensure you do not alter the length of the string if it shifts column coordinates, or simply substitute characters 1-to-1).

### 3. Dedicated Redaction Tools

For automated scrubbing, tools like `asciinema` or third-party wrappers do not typically feature live optical "blending" since terminals render text rather than pixels, but you can pipe output through text filters or sanitize transcripts.

* **Scrubbing scripts:** You can write a short Python or `sed` script to parse your output logs and regex-replace known patterns (such as AWS keys, Bearer tokens, or IP addresses) before rendering or publishing them.

!!! Warning "Security Warning"" 
    Always review your raw typescript, cast file, or HTML output in a text editor before publishing it to a public repository. Terminal histories often capture unexpected environment variables, prompt strings showing hostnames, or configuration file contents.