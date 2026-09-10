# Remote Server Management in Python

!!! info "Learning Objectives"
    - Understand the role of Secure Shell (SSH) in remote cloud resource management.
    - Implement remote execution using various abstraction levels: `subprocess`, `paramiko`, `fabric`, and `RemoteExecutor`.
    - Manage remote files using SFTP.
    - Select the appropriate remote management tool based on task complexity and dependency requirements.
    - Apply security best practices for SSH authentication and host verification.

Secure Shell (SSH) is the industry-standard protocol for managing remote Linux servers. In cloud environments, where management scripts typically run on a control node and target multiple virtual machines (VMs), SSH provides the encrypted channel necessary for configuration, administration, and monitoring.

Python offers multiple ways to interact with remote servers, ranging from simple system calls to high-level orchestration frameworks. Choosing the right tool depends on the required level of control, the need for portability, and the scale of the infrastructure being managed.

## Fundamental SSH Concepts

Before implementing programmatic access, it is important to understand the underlying SSH mechanism. SSH uses a client-server architecture where the client authenticates itself to the server to establish a secure, encrypted tunnel.

### Authentication Mechanisms

SSH supports several methods of authentication:

- **Password Authentication**: The user provides a password. This is generally discouraged for automation due to security risks and the difficulty of managing secrets.
- **Public Key Authentication**: The user provides a private key that matches a public key stored on the server in the `authorized_keys` file. This is the standard for cloud automation.
- **Agent Forwarding**: Using an SSH agent to manage keys, allowing the client to authenticate to multiple servers without storing private keys on intermediate jump hosts.

### Host Key Verification

When a client connects to a server for the first time, the server presents a host key. The client must verify this key to prevent Man-in-the-Middle (MITM) attacks. In automated scripts, developers often use policies to handle unknown host keys, though these must be chosen based on the security requirements of the environment.

## Low-Level Execution with subprocess

For simple, one-off commands where the local system's SSH configuration (such as `~/.ssh/config`) is already correctly set up, the `subprocess` module is the most direct approach. It invokes the system's own SSH binary, leveraging all local configurations and agents.

### Implementation

The `subprocess.run` function is used to execute the command and capture the output.

Example: Running a basic command via system SSH.

```python
import subprocess

# Command to run on the remote server
# The syntax follows the standard shell: ssh user@host command
cmd = ["ssh", "cloud-user@vm-web-01.cloud.local", "uptime"]

# Execute and capture output
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print(f"System Uptime:\n{result.stdout}")
else:
    print(f"SSH Error:\n{result.stderr}")
```

### Trade-offs

- **Pros**: No external dependencies, uses existing system SSH configs.
- **Cons**: Limited control over the SSH session, difficult to handle interactive prompts, and requires the SSH binary to be installed on the host.

## Fine-Grained Control with Paramiko

`paramiko` is a native Python implementation of the SSHv2 protocol. It provides complete control over the SSH connection, including channel management and SFTP.

### Establishing a Connection

The `paramiko.SSHClient` class handles the connection lifecycle.

Example: Connecting using a private key.

```python
import paramiko

hostname = "vm-web-01.cloud.local"
username = "cloud-user"
key_path = "/home/user/.ssh/id_rsa"

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, key_filename=key_path)
    print("Connection established.")
    client.close()
except Exception as e:
    print(f"SSH Connection failed: {e}")
```

### Executing Commands and Handling Streams

The `exec_command` method returns three streams: `stdin` for input, `stdout` for output, and `stderr` for errors.

Example: Capturing remote output and handling errors.

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("vm-web-01.cloud.local", username="cloud-user", key_filename="/home/user/.ssh/id_rsa")

stdin, stdout, stderr = client.exec_command("uptime")
output = stdout.read().decode("utf-8")
error = stderr.read().decode("utf-8")

if output:
    print(f"Output: {output}")
if error:
    print(f"Error: {error}")

client.close()
```

### Remote File Management via SFTP

Paramiko integrates SFTP for file transfers, allowing for `put` and `get` operations.

Example: Uploading and downloading files.

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("vm-web-01.cloud.local", username="cloud-user", key_filename="/home/user/.ssh/id_rsa")

sftp = client.open_sftp()
sftp.put("local_config.conf", "/tmp/remote_config.conf")
sftp.get("/var/log/syslog", "local_syslog.log")
sftp.close()
client.close()
```

!!! warning "Security Note on AutoAddPolicy"
    `paramiko.AutoAddPolicy()` accepts any host key, exposing the connection to MITM attacks. In production, use `RejectPolicy` and maintain a known hosts file.

## High-Level Orchestration with Fabric

Fabric is a high-level library built on top of Paramiko. It is designed for application deployment and systems administration, providing a more intuitive API for executing tasks across multiple hosts.

### Connection and Execution

Fabric simplifies the connection process using a `Connection` object.

Example: Executing a command with Fabric.

```python
from fabric import Connection

# The Connection object handles authentication and session management
with Connection(host="vm-web-01.cloud.local", user="cloud-user") as c:
    # run() executes a command and returns a result object
    result = c.run("uptime", hide=True)
    print(f"Remote Output: {result.stdout.strip()}")
```

### Task-Based Orchestration

Fabric is particularly useful for running the same sequence of commands across a fleet of servers, as it abstracts the underlying SSH channel management.

## Standardized Execution with Cloudmesh RemoteExecutor

The `cloudmesh.ai.common.remote.RemoteExecutor` provides a standardized wrapper for SSH and SFTP operations within the Cloudmesh AI ecosystem. It integrates with global configuration settings for host key trust and output monitoring.

### Unified Remote Interface

`RemoteExecutor` simplifies the API by combining connection management and execution into a single object.

Example: Using RemoteExecutor for commands and file transfers.

```python
from cloudmesh.ai.common.remote import RemoteExecutor

# Initialize the executor
remote = RemoteExecutor(
    host="vm-web-01.cloud.local", 
    username="cloud-user", 
    key_filename="/home/user/.ssh/id_rsa"
)

# Execute a command and get a structured ExecResult
result = remote.execute("uptime")
print(f"Exit Code: {result.exit_code}")
print(f"Output: {result.stdout}")

# Upload a file using the helper method
remote.upload("local_script.py", "/tmp/remote_script.py")
```

## Comparison of Remote Management Methods

Choosing the right tool depends on the abstraction level and the specific requirements of the project.

| Method | Abstraction Level | Dependency | Best Use Case |
| :--- | :--- | :--- | :--- |
| `subprocess` | Low | System SSH | Simple scripts using existing system SSH configs. |
| `paramiko` | Medium | `paramiko` | Fine-grained control over SSH channels and SFTP. |
| `fabric` | High | `fabric` | Deployment workflows and multi-host orchestration. |
| `RemoteExecutor`| High | `cloudmesh-ai-common` | Standardized tasks within Cloudmesh AI projects. |

## Security Best Practices

When automating SSH, security must be the priority to prevent unauthorized access to cloud infrastructure.

- **Avoid Hardcoding Credentials**: Use environment variables or secret management services (e.g., HashiCorp Vault) instead of plain text keys.
- **Use SSH Agents**: Use the local SSH agent to avoid storing private keys on the disk of the machine running the script.
- **Principle of Least Privilege**: Use dedicated SSH users with restricted permissions via `sudoers` instead of the root account.

!!! tip "Summary Checklist"
    - Selected the appropriate tool based on abstraction needs (`subprocess`, `paramiko`, `fabric`, or `RemoteExecutor`).
    - Implemented secure authentication using private keys.
    - Handled remote output streams (`stdout`, `stderr`) and exit codes.
    - Performed remote file operations using SFTP.
    - Applied host key verification policies.
    - Followed the principle of least privilege for remote user accounts.

!!! note "Exercise 1: Basic Connectivity"
    Write a Python script that connects to a remote server and prints the current system kernel version using the `uname -a` command. Handle the connection using a try-except block to catch authentication errors.

!!! note "Exercise 2: Remote Cloud Auditor"
    Develop a script that performs the following tasks:
    1. Accepts a list of three remote VM IP addresses.
    2. Connects to each VM using a shared SSH private key.
    3. Executes a command to check available disk space (e.g., `df -h /`).
    4. Parses the output to determine the disk utilization percentage.
    5. Prints a warning message if any VM exceeds 80% disk usage.

!!! note "Exercise 3: Automated Deployment Pipeline"
    Implement a mini-deployment pipeline that:
    1. Connects to a remote server via SSH.
    2. Uses SFTP to upload a Python script named `app.py` to the `/tmp` directory.
    3. Executes the uploaded script using `python3 /tmp/app.py`.
    4. Captures the output and logs it to a local file named `deployment.log`.
