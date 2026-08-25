---
title: "Python SSH"
---

!!! info "Learning Outcomes"
    - Understand the role of SSH (Secure Shell) in remote cloud resource management.
    - Implement programmatic SSH connections using the `paramiko` library.
    - Manage remote cloud instances by executing commands and handling remote streams.

Secure Shell (SSH) is the standard protocol for managing remote Linux servers. In a cloud environment, where your management script runs on one machine and your virtual machines (VMs) run on another, SSH is the primary mechanism for configuration and administration.

While you can use the `subprocess` module to call the system's `ssh` command, using a dedicated library like `paramiko` provides much finer control over authentication, channel management, and error handling.

## Programmatic Remote Management with Paramiko

To use `paramiko`, you first need to install it:

``` bash
$ pip install paramiko
```

The following example demonstrates how to connect to a remote cloud VM using an SSH private key and execute a command to check the system uptime.

``` python
import paramiko

# Connection details
hostname = 'vm-web-01.cloud.local'
username = 'cloud-user'
key_path = '/home/user/.ssh/id_rsa'

try:
    # Create an SSH client
    client = paramiko.SSHClient()
    
    # Automatically add the server's host key (only for trusted environments)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect using a private key
    print(f"Connecting to {hostname}...")
    client.connect(hostname, username=username, key_filename=key_path)
    
    # Execute a remote command
    command = 'uptime'
    stdin, stdout, stderr = client.exec_command(command)
    
    # Read the output
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    if output:
        print(f"Remote Output:\n{output}")
    if error:
        print(f"Remote Error:\n{error}")
        
    client.close()
    print("Connection closed.")

except Exception as e:
    print(f"SSH Connection failed: {e}")
```

### Key Concepts
- **`SSHClient`**: The primary interface for managing the SSH connection.
- **`set_missing_host_key_policy`**: Determines how the client handles unknown host keys. `AutoAddPolicy` is common for automated scripts but should be used cautiously in high-security environments.
- **`exec_command()`**: Sends a command to the remote server and returns three streams: `stdin` (to send data), `stdout` (to read output), and `stderr` (to read errors).

!!! assignment "Remote Cloud Auditor"
    Write a Python script that:
    1. Takes a list of three remote VM IP addresses.
    2. Connects to each VM using the same SSH key.
    3. Executes a command to check the available disk space (e.g., `df -h /`).
    4. Parses the output to find the percentage of disk used.
    5. Prints a warning if any VM has more than 80% disk utilization.