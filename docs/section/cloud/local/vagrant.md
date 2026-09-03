# Virtual Machine Orchestration with Vagrant

!!! info "Learning Outcomes"
    *   Experiment with virtual machines on your local computer before moving to a cloud environment.
    *   Learn to define and manage VM configurations as code.

---

[Vagrant](https://www.vagrantup.com/) is a tool for building and managing virtual machine environments in a single workflow. It provides a consistent way to create reproducible development environments, allowing you to define your VM configuration in a simple file (`Vagrantfile`).

Vagrant typically interfaces with a provider (like Oracle VirtualBox) to launch the VM, though it supports others such as VMware, Hyper-V, and Docker. One of its most useful features is the ability to automatically fetch "boxes" (pre-configured VM images) and start them with a single command.

## Installation

Detailed installation instructions for all platforms are available at the [official downloads page](https://www.vagrantup.com/downloads).

### macOS
Download the `.dmg` installer from the official website. After installation, Vagrant is typically located in `/usr/local/bin/vagrant`. Ensure this directory is in your `PATH` environment variable.

### Windows
Download and run the Windows installer. You will likely need to reboot your computer for the changes to take effect. Ensure you have a supported provider (like VirtualBox) installed.

### Linux
On Ubuntu and other Debian-based systems, you can install Vagrant via `apt`:

```bash
sudo apt update
sudo apt install vagrant
```

Alternatively, you can download the official `.deb` or `.rpm` package from the Vagrant website for the most recent version.

## Getting Started

Vagrant uses "boxes" as the base image for VMs. You can browse available boxes at [Vagrant Cloud](https://app.vagrantup.com/boxes/search). For this class, we recommend using a recent Ubuntu LTS image (e.g., Ubuntu 22.04).

### Launching Your First VM

To get a basic Ubuntu 22.04 instance running:

```bash
# Initialize a new Vagrant environment with the Ubuntu 22.04 box
vagrant init ubuntu/jammy64

# Start and provision the VM
vagrant up

# Securely shell into the VM
vagrant ssh
```

### Managing the VM Lifecycle

Once you have exited the VM using the `exit` command, you can manage it from your host terminal:

| Command | Description |
| :--- | :--- |
| `vagrant status` | Check the current state of the VM (running, powered off, etc.) |
| `vagrant halt` | Gracefully shut down the guest operating system. |
| `vagrant suspend` | Save the current state of the VM and stop it (similar to hibernate). |
| `vagrant resume` | Wake up a suspended VM. |
| `vagrant reload` | Restart the VM and apply any changes made to the `Vagrantfile`. |
| `vagrant destroy` | Completely remove the VM and its associated disks. |

## Exercises

!!! assignment "Exercise 1: Local Environment Setup"
    Install Vagrant and VirtualBox on your computer. Launch an Ubuntu 22.04 (`ubuntu/jammy64`) instance and verify that you can `ssh` into it.

!!! assignment "Exercise 2: VM Lifecycle"
    Experiment with the lifecycle commands. Start the VM, suspend it, resume it, and finally destroy it. Use `vagrant status` at each step to observe the change.

!!! assignment "Exercise 3: Software Installation"
    Inside your Vagrant VM, perform the following tasks:
    1. Update the package list: `sudo apt update`.
    2. Check the default Python 3 version: `python3 --version`.
    3. Install `pip` for Python 3: `sudo apt install python3-pip`.
    4. Install a simple tool like `htop` to monitor system resources.

!!! assignment "Exercise 4: Configuration as Code"
    Read the `Vagrantfile` created during `vagrant init`. Try to find where the box name is specified. Research how to change the amount of RAM allocated to the VM within the `Vagrantfile` and apply the change using `vagrant reload`.