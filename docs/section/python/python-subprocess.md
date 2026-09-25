# Subprocess: Orchestrating External Tools

!!! info "Learning Outcomes"
    - Understand the conceptual difference between a parent process and a subprocess.
    - Manage the "Three Standard Streams" (stdin, stdout, stderr) to control process I/O.
    - Execute system commands using the modern `subprocess.run()` for most automation tasks.
    - Implement complex, non-blocking process interactions using the `Popen` class.
    - Apply security best practices to prevent shell injection attacks.

## Introduction: Why Subprocesses?

Python is a remarkably powerful language with a vast ecosystem of libraries. However, in the real world of system administration and DevOps, you will frequently encounter tools that are simply better suited for specific tasks than any Python library.

Whether it is the speed of `grep`, the robustness of `git`, the processing power of `ffmpeg`, or the system-level access of `ipconfig`, the ability to "shell out" from Python allows you to leverage the entire history of Unix and Windows utilities.

### What is a Process?

In computing, a **process** is an independent instance of a program in execution. Each process has its own:

- **Memory Space**: It cannot access another process's memory directly.
- **Process ID (PID)**: A unique identifier assigned by the operating system.
- **Execution State**: It can be running, sleeping, or terminated.

When you use the `subprocess` module, your Python script becomes the **parent process**, and it spawns a **child process**. The parent can control the child, feed it data, read its output, and eventually wait for it to terminate.

### The Three Standard Streams

Every process created by the operating system is automatically given three communication channels, known as **standard streams**:

1. **`stdin` (Standard Input)**: The channel through which the process receives data (typically from the keyboard or a file).
2. **`stdout` (Standard Output)**: The channel through which the process sends its successful results (typically the terminal screen).
3. **`stderr` (Standard Error)**: A separate channel dedicated to error messages. This ensures that errors don't get mixed in with valid data output.

Understanding these streams is the key to mastering the `subprocess` module.

---

## Simple Execution: `os.system`

For years, `os.system()` was the go-to method for running shell commands. It is simple: you pass a string, and the system executes it.

### Basic Syntax

```python
import os

# Example: Clear the terminal screen
exit_code = os.system("cls" if os.name == "nt" else "clear")
print(f"Command finished with exit code: {exit_code}")
```

### Why is it considered legacy?

While convenient, `os.system()` has several major drawbacks:

- **No Output Capture**: You cannot easily capture the text the command prints to the screen; you only get the exit code.
- **Shell Dependency**: It spawns a full system shell (like `/bin/sh` or `cmd.exe`) to run the command. This is slower and introduces security risks.
- **Blocking**: Your Python script completely pauses until the command finishes.

!!! tip "Best Practice"
    Use `os.system()` only for trivial tasks like clearing the screen or running a command where you don't care about the output. For everything else, use `subprocess`.

---

## The Cloudmesh Wrapper: `Shell.run`

In the Cloudmesh ecosystem, we often prioritize development speed. The `Shell` wrapper provides a high-level abstraction that handles the most common frustration of subprocesses: converting raw bytes into usable Python strings.

```python
from cloudmesh.ai.common.Shell import Shell

# Executes the command and returns the output as a string automatically
result = Shell.run("ls -lisa")
print(result)

# Since the result is a string, you can process it immediately
lines = result.split("\n")
for line in lines:
    if line:
        print(f"Processing: {line}")
```

This wrapper is ideal for rapid prototyping. `Shell.run` was invented before `subprocess.run()` existed and remains useful for simple string-based output.

---

## The new `subprocess.run()` in Python

Introduced in Python 3.5, `subprocess.run()` is the recommended function for most automation tasks. It is a synchronous function that wraps the more complex `Popen` class into a single, easy-to-use call.

### Basic Usage

By default, `subprocess.run()` sends the command's output directly to your terminal.

```python
import subprocess

# We pass the command as a list to avoid the shell
subprocess.run(["ls", "-l"])
```

### Capturing Output with `CompletedProcess`

When you need to use the command's output in your Python logic, use `capture_output=True`. This returns a `CompletedProcess` object.

```python
import subprocess

# text=True converts the output from bytes to a string
result = subprocess.run(["ls", "-l"], capture_output=True, text=True)

print(f"Standard Output: {result.stdout}")
print(f"Standard Error: {result.stderr}")
print(f"Exit Code: {result.returncode}")
```

### Robust Error Handling

In a script, you usually don't want to ignore errors. By setting `check=True`, Python will automatically raise a `CalledProcessError` if the command fails (returns a non-zero exit code).

```python
import subprocess

try:
    subprocess.run(["ls", "/root/secret"], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"The command failed with code {e.returncode}")
    print(f"System Error: {e.stderr}")
```

---

## The Advanced Process Control: `Popen`

`subprocess.run()` is **blocking**—your script stops until the command is done. If you need to run a long-running process in the background or read output line-by-line, use the `Popen` class.

`Popen` is **asynchronous**; it starts the process and immediately returns control to your Python script.

### Managing Streams and Deadlocks

When using `Popen`, you often set `stdout=subprocess.PIPE`. This creates a "pipe"—a small memory buffer in the OS.

**The Deadlock Trap:** If the child process writes a huge amount of data to the pipe and the parent process doesn't read it, the pipe fills up. The child process then "blocks" (pauses). If the parent is simultaneously waiting for the child to finish (`process.wait()`), neither will ever move. This is a **deadlock**.

### The Solution: `communicate()`

The `communicate()` method prevents deadlocks by reading all data from `stdout` and `stderr` into memory and then waiting for the process to terminate.

```python
from subprocess import Popen, PIPE

# Start the process without blocking the main script
process = Popen(['ls', '-lisa'], stdout=PIPE, stderr=PIPE, text=True)

# Safely read the output and wait for the process to end
stdout, stderr = process.communicate()

print(f"Process finished. Output:\n{stdout}")
```

---

## Security: The Danger of `shell=True`

Setting `shell=True` tells Python to run the command through the system shell. While this allows shell features like wildcards (`*`) and pipes (`|`), it introduces a critical security vulnerability: **Shell Injection**.

### The Attack Vector

Imagine a script that lets a user list a directory:

```python
# DANGEROUS CODE
import subprocess
user_input = "my_folder; rm -rf /" 
subprocess.run(f"ls {user_input}", shell=True)
```

Because `shell=True` is used, the shell executes two separate commands: `ls my_folder` followed by `rm -rf /`.

### The Defense: Use Lists

The secure way is to pass the command as a **list** and leave `shell=False` (the default).

```python
# SECURE CODE
import subprocess
user_input = "my_folder; rm -rf /"
subprocess.run(["ls", user_input]) 
```

In this case, Python tells the OS to execute the `ls` program and pass the entire string `my_folder; rm -rf /` as a single literal argument.

---

## Assignments

!!! note "Assignment: Subprocess Automation"
    1. **System Auditor**: Write a script that runs `df -h` (disk usage) and `free -m` (memory usage). Parse the output to identify if any partition is over 80% full or if available memory is below 500MB. If so, print a warning to `stderr`.
    2. **Log Processor**: Use `Popen` to run a command that generates a continuous stream of output (e.g., `ping google.com` or `tail -f /var/log/syslog`). Read the output line-by-line in real-time and print only the lines that contain the word "ERROR" or "timeout".
    3. **Secure Wrapper**: Create a function `safe_execute(cmd_list)` that wraps `subprocess.run`. It should implement a timeout of 10 seconds, capture all output, and return a custom dictionary containing the status, stdout, and stderr.

---

## Self-Evaluation

??? note "What happens if a subprocess fills its output pipe buffer and the parent isn't reading?"
    The child process will block (pause) and wait for the OS pipe buffer to be cleared. If the parent is waiting for the child to finish without reading the buffer, the system enters a deadlock.

??? note "When is `subprocess.run()` a better choice than `Popen`?"
    When the task is short-lived, and you only need the final result after the command has finished. It is simpler, safer, and less prone to deadlocks.

??? note "Why is passing a list to `subprocess.run` safer than passing a string with `shell=True`?"
    Passing a list bypasses the system shell entirely. The arguments are passed directly to the OS exec call, meaning special shell characters (like `;`, `&`, `|`) are treated as literal text rather than command separators.

??? note "What is the difference between `stdout` and `stderr`?"
    `stdout` is for the successful output of a program, while `stderr` is reserved for error messages and diagnostics. This allows users to redirect errors to a log file while keeping the main output on the screen.
