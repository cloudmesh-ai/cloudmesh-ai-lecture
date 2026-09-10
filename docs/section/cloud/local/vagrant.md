# Virtual Machine Orchestration with Vagrant

!!! info "Learning Objectives"
    - Set up a local virtualization environment using Vagrant and a hypervisor.
    - Define and manage virtual machine (VM) configurations as code using a `Vagrantfile`.
    - Execute and manage the full VM lifecycle, including creation, suspension, and destruction.
    - Provision basic software and tools within a guest operating system.

The gap between a developer's local environment and a production server is a common source of software failures—the "it works on my machine" problem. To solve this, engineers use virtualization to create environments that exactly mimic the target server.

Vagrant is an orchestration tool that simplifies this process. It does not provide the virtualization itself; instead, it acts as a wrapper around a **provider** (such as Oracle VirtualBox, VMware, or Hyper-V). By using a simple configuration file, Vagrant allows you to create reproducible, disposable development environments that can be shared across a team, ensuring everyone is working on the same OS version and configuration.

## Infrastructure as Code for Local VMs

The core of Vagrant is the concept of **Infrastructure as Code (IaC)**. Rather than manually installing an OS and configuring settings through a GUI, you define the desired state of the machine in a `Vagrantfile`.

### The Vagrant Box

Vagrant uses "boxes" as the base image for VMs. A box is a pre-packaged VM image that includes the operating system and a minimal set of configurations. Instead of downloading a massive ISO file and going through a manual installation process, Vagrant fetches a box from [Vagrant Cloud](https://app.vagrantup.com/boxes/search) and clones it locally.

### Understanding the Vagrantfile

The `Vagrantfile` is a Ruby-based configuration file that describes the desired state of the virtual machine. You do not need to know Ruby to use it, as the syntax is designed to be declarative.

A typical `Vagrantfile` looks like this:

```ruby
Vagrant.configure("2") do |config|
  # 1. Define the base image
  config.vm.box = "ubuntu/jammy64"

  # 2. Configure Networking
  # Assigns a static IP to the VM, allowing you to access it from the host browser
  config.vm.network "private_network", ip: "192.168.56.10"

  # 3. Set up Synced Folders
  # Maps a folder on your host machine to a folder in the guest VM
  # config.vm.synced_folder "src/", "/var/www/html"

  # 4. Provider-specific configuration (VirtualBox)
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 2
    vb.name = "cloudmesh-ubuntu-vm"
  end
end
```

#### Key Configuration Options:

- **`config.vm.box`**: Specifies which image to download from Vagrant Cloud.
- **`config.vm.network`**: Defines how the VM communicates. A `private_network` is ideal for creating a host-only network where the VM is reachable via a specific IP.
- **`config.vm.synced_folder`**: One of Vagrant's most powerful features. It allows you to edit code on your host machine using your favorite IDE, and have the changes immediately reflected inside the VM.
- **`vb.memory` / `vb.cpus`**: Allows you to tune the hardware resources based on the requirements of your application.

### The Provider Model

Vagrant is provider-agnostic. While VirtualBox is the most common provider for local development, Vagrant can also manage:

- **VMware**: For enterprise-grade performance.
- **Hyper-V**: For native Windows virtualization.
- **Docker**: To manage containers as if they were VMs.

## Installation and Environment Setup

To use Vagrant, you must install both the Vagrant software and a compatible provider.

### macOS and Windows

Download the official installers from the [Vagrant downloads page](https://www.vagrantup.com/downloads). For Windows users, a system reboot is typically required after installation to finalize the network drivers.

### Linux

On Ubuntu and other Debian-based systems, Vagrant can be installed via the package manager:

```bash
sudo apt update
sudo apt install vagrant
```

## Orchestrating Your First Machine

Once installed, you can launch a VM using a few standardized commands. For this guide, we will use the `ubuntu/jammy64` box (Ubuntu 22.04 LTS).

### Initialization and Launch

To create a new environment, run the following commands in your terminal:

```bash
# Initialize a new Vagrant environment with the Ubuntu 22.04 box
vagrant init ubuntu/jammy64

# Start and provision the VM
vagrant up

# Access the VM via a secure shell
vagrant ssh
```

When you run `vagrant up`, Vagrant performs several steps: it downloads the box if it is not already present, creates a new VM instance based on that box, configures the network, and boots the guest OS.

### Managing the Guest Lifecycle

After exiting the VM (`exit`), you can manage the state of the machine from your host terminal.

| Command | Description |
| :--- | :--- |
| `vagrant status` | Displays the current state of the VM (e.g., running, powered off). |
| `vagrant halt` | Performs a graceful shutdown of the guest OS. |
| `vagrant suspend` | Saves the VM state to disk and pauses execution. |
| `vagrant resume` | Wakes a suspended VM from its saved state. |
| `vagrant reload` | Restarts the VM and applies changes made to the `Vagrantfile`. |
| `vagrant destroy` | Completely removes the VM and all associated virtual disks. |

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] Vagrant and a provider (e.g., VirtualBox) are installed and verified.
    - [ ] A `Vagrantfile` has been initialized using `vagrant init`.
    - [ ] The VM has been successfully launched using `vagrant up`.
    - [ ] The guest OS has been accessed via `vagrant ssh`.
    - [ ] The VM lifecycle commands (`halt`, `suspend`, `destroy`) have been tested.

## Practical Exercises

!!! note "Exercise 1: Environment Verification"
    Install Vagrant and VirtualBox. Initialize an Ubuntu 22.04 (`ubuntu/jammy64`) instance. Use `vagrant ssh` to enter the machine and run `lsb_release -a` to verify the OS version.

!!! note "Exercise 2: Lifecycle and Provisioning"
    Perform the following sequence of operations:
    1. Use `vagrant halt` to shut down the machine, then `vagrant status` to verify.
    2. Use `vagrant up` to restart it.
    3. SSH into the VM and install the `htop` system monitor using `sudo apt update && sudo apt install htop -y`.
    4. Use `vagrant suspend` and then `vagrant resume` to verify the state is preserved.

!!! note "Exercise 3: Configuration as Code"
    Open the `Vagrantfile` in a text editor. Find the provider configuration section for VirtualBox. Modify the configuration to increase the VM's RAM to 2048MB. Save the file and run `vagrant reload` to apply the changes. Verify the new memory limit inside the VM using the `free -m` command.
