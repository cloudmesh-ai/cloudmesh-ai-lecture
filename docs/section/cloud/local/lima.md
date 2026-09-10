# Linux Virtualization with Lima

!!! info "Learning Objectives"
    - Install and configure Lima on macOS.
    - Launch and manage Linux instances using the `limactl` command-line tool.
    - Understand and customize Lima configuration YAML files.
    - Leverage automatic file sharing and port forwarding for seamless development.
    - Deploy Linux-only software, such as Apptainer, within a Lima VM.

The gap between a developer's local environment and a production server is a common source of software failures—the "it works on my machine" problem. This occurs when the local OS, library versions, or system configurations differ from the target environment. To solve this, engineers use virtualization to create environments that exactly mimic the target server.

Lima (Linux Machines) is a lightweight virtualization tool designed to provide Linux VMs on macOS with a focus on the command-line experience. Unlike traditional VM managers that prioritize a graphical interface, Lima focuses on automation and integration. It leverages QEMU (or the native macOS Virtualization.framework) to launch Linux instances and automatically handles the most tedious parts of VM management: file sharing and port forwarding. This allows a developer to feel as if they are working in a native Linux shell while maintaining the convenience of the macOS host.

## Installation and Setup

Lima requires a virtualization backend to run the Linux kernel. On macOS, QEMU is the most common provider.

### Installing Lima and QEMU

The simplest way to install Lima on macOS is via Homebrew:

```bash
brew install lima qemu
```

Once installed, the `limactl` (Lima Control) command becomes the primary interface for managing your Linux instances.


## Managing Lima Instances

Lima uses a template-based approach to create VMs. A template defines the operating system, the resources allocated, and the initial configuration.

### Launching Your First Instance

To start a new Linux VM using the default configuration, run:

```bash
limactl start
```

During the first run, Lima will prompt you to choose a template. The default Ubuntu template is recommended for most users. If you wish to start an instance with a specific name (e.g., "dev-box"), use:

```bash
limactl start dev-box
```

### Interacting with the VM

Once the instance is running, you can enter the Linux environment via a secure shell:

```bash
limactl shell default
```

This command handles the SSH keys and connection details automatically, dropping you directly into the guest OS terminal.

### Instance Lifecycle Management

You can manage multiple instances using the following `limactl` commands:

| Command | Description |
| :--- | :--- |
| `limactl list` | Shows all managed instances and their current status. |
| `limactl stop <name>` | Gracefully shuts down the VM. |
| `limactl start <name>` | Boots a stopped VM. |
| `limactl delete <name>` | Completely removes the VM and its configuration. |

## Configuring the Environment

One of Lima's most powerful features is its use of YAML configuration files. Every instance has a corresponding YAML file that defines its identity and resources.

### Automatic File Sharing and Port Forwarding

Lima eliminates the need for manual NFS or SMB mounts. By default, it maps the user's home directory on macOS to the same path inside the Linux VM.

For example, if you create a file at `/Users/grey/project/app.py` on your Mac, it is immediately available at `/Users/grey/project/app.py` inside the Lima shell.

Port forwarding is handled similarly. If a service inside the VM listens on port 8080, Lima automatically maps that port to the macOS host, allowing you to access the service at `http://localhost:8080`.

### Customizing the Configuration

To change the resources allocated to a VM (such as CPU or RAM), you can edit the instance configuration. You can do this during the `start` process by specifying a custom YAML file:

```bash
limactl start --with-config my-config.yaml
```

A sample configuration block for resources looks like this:

```yaml
cpus: 4
memory: "4GiB"
disk: "50GiB"
```


## Deploying Linux Software

Because Lima provides a full Linux kernel, it is an ideal environment for installing tools that require a Linux environment, such as Apptainer (formerly Singularity).

### Installing Apptainer in Lima

Once inside the Lima shell, you can follow standard Linux installation procedures. For Ubuntu, this involves updating the package manager and installing the required dependencies:

```bash
sudo apt update
sudo apt install -y apptainer
```

By combining Lima with Apptainer, macOS developers can build and test high-performance computing (HPC) containers locally before deploying them to a remote cluster.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] Lima and QEMU are installed via Homebrew.
    - [ ] A Linux instance has been successfully launched using `limactl start`.
    - [ ] Shell access has been verified using `limactl shell`.
    - [ ] Automatic file sharing between macOS and Linux has been confirmed.
    - [ ] Instance lifecycle commands (`list`, `stop`, `delete`) have been tested.
    - [ ] Linux-specific software has been installed within the guest environment.

## Practical Exercises

!!! note "Exercise 1: Basic Instance Setup"
    Install Lima and QEMU. Launch a default Ubuntu instance. Use `limactl shell` to enter the VM and run `uname -a` to verify that you are running a Linux kernel on your Mac.

!!! note "Exercise 2: Resource and Lifecycle Management"
    Create a new instance named "test-vm". Use `limactl list` to verify its status. Stop the instance, then restart it. Finally, delete the instance to clean up your environment.

!!! note "Exercise 3: Development Workflow Simulation"
    1. Create a directory on your macOS desktop called `lima-test`.
    2. Create a simple text file inside that directory.
    3. Launch a Lima instance and enter the shell.
    4. Navigate to the same directory within the VM and read the file to verify automatic file sharing.
    5. Install `curl` inside the VM and use it to fetch a webpage, verifying the VM's network connectivity.

