# Virtual Machine Management with VirtualBox

!!! info "Learning Objectives"
    After completing this chapter, you will be able to:
    - Install and configure Oracle VirtualBox and an Ubuntu LTS guest OS.
    - Manage VM resource allocation (CPU, RAM, disk) based on different use cases.
    - Configure essential VM features like Guest Additions, shared clipboards, and shared folders.
    - Control the full VM lifecycle using both the VirtualBox GUI and the `VBoxManage` command-line interface.
    - Automate VM deployment and management using shell scripts.

VirtualBox provides an environment for running multiple operating systems on a single physical machine. For most users, the Graphical User Interface (GUI) is the primary point of interaction, offering an intuitive way to create and manage VMs. However, for developers and system administrators, the GUI is often insufficient. When you need to deploy dozens of VMs, integrate VM creation into a CI/CD pipeline, or manage VMs on a remote server without a display, the command line is essential.

The primary tool for this is `VBoxManage`, a CLI utility that provides full control over the VirtualBox engine. Almost every action performed in the GUI is a wrapper around a `VBoxManage` command.

## Getting Started: Installation & Setup

### VirtualBox and OS Installation

VirtualBox is free and open-source. Detailed installation instructions for your specific operating system can be found at:

* [VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads)

For the guest OS, we recommend using a current LTS (Long Term Support) version of Ubuntu (e.g., 22.04 or 24.04) to ensure stability and long-term support.

* [Ubuntu Desktop Download](http://www.ubuntu.com/download/desktop)

### Hardware Requirements

Depending on your host machine's specifications, some configurations may be too resource-constrained. The following minimal host setup is recommended:

* **CPU**: Multi-core processor with virtualization extensions (VT-x or AMD-V) enabled in BIOS/UEFI.
* **RAM**: At least 8 GB of system memory.
* **Storage**: At least 50 GB of free hard drive space.

### Recommended VM Configurations

Depending on the task, you should adjust the resources allocated to the VM:

| Profile | CPU Cores | RAM | Disk Space | Use Case |
| :--- | :---: | :---: | :---: | :--- |
| **Minimal** | 1 | 2 GB | 10 GB | Basic Linux CLI tasks |
| **Development** | 2 | 4 GB | 25 GB | IDEs, Compiling, LaTeX |
| **Heavy** | 4 | 8 GB | 50 GB | Docker, Heavy Data Processing |

!!! warning "Version Note"
    Tutorial videos may show older versions of Ubuntu (e.g., 16.04 or 18.04). Always install the latest LTS version available at the time of your installation.

## VM Lifecycle Management

Managing a VM involves creation, configuration, registration, and execution. This can be done through the GUI or the CLI.

### The GUI Approach

The GUI allows you to create a VM by clicking "New", selecting the ISO image, and following the wizard to allocate RAM and disk space. It is the best way for beginners to explore available settings.


#### Guest Additions and Integration

Installing **Guest Additions** is highly recommended to enable:

* **Dynamic Window Resizing**: The VM resolution automatically adjusts.
* **Shared Clipboard**: Copy-pasting between host and guest.
* **Shared Folders**: Easy file transfer.

After installation, reboot the VM. To enable the shared clipboard on macOS, go to **Devices** $\rightarrow$ **Shared Clipboard** $\rightarrow$ **Bidirectional**.

Key combinations for macOS $\leftrightarrow$ Ubuntu:

* **Host (macOS) $\rightarrow$ Guest (Ubuntu)**: `Cmd + C` $\rightarrow$ `Ctrl + Shift + V` (in terminal)
* **Guest (Ubuntu) $\rightarrow$ Host (macOS)**: `Ctrl + Shift + C` $\rightarrow$ `Cmd + V`


<div class="video-aspect" style="width:50%;">
  <iframe src="https://www.youtube.com/embed/NWibDntN2M4"
          allowfullscreen frameborder="0"></iframe>
</div>

<style>
.video-aspect {
  aspect-ratio: 16 / 9;      /* 16:9 */
  max-width: 100%;
}
.video-aspect iframe {
  width: 100%;
  height: 100%;
  border: 0;
}
</style>



### The CLI Approach (`VBoxManage`)

`VBoxManage` is the core command-line tool. The general syntax is:

```bash
VBoxManage [command] [sub-command] [options]
```

To create and register a new VM:

```bash
VBoxManage createvm --name "Ubuntu-Server" --ostype "Ubuntu_64" --register
```

To configure properties like RAM and CPU:

```bash
VBoxManage modifyvm "Ubuntu-Server" --memory 2048 --cpus 2 --vram 128
```

### Execution and Control

You can start a VM through the GUI "Start" button or via the CLI. The CLI is particularly useful for starting VMs in `headless` mode, which runs the VM in the background without a GUI window.

To start a VM headlessly:

```bash
VBoxManage startvm "Ubuntu-Server" --type headless
```

To gracefully shut down a VM:

```bash
VBoxManage controlvm "Ubuntu-Server" acpipowerbutton
```

To force a hard power-off:

```bash
VBoxManage controlvm "Ubuntu-Server" poweroff
```


## Advanced VM Configuration

### Storage Management

In the GUI, storage is managed under the "Storage" tab of the VM settings. In the CLI, you must first create the medium and then attach it to a controller.

To create a 20GB VDI disk:

```bash
VBoxManage createmedium disk --filename "Ubuntu-Server.vdi" --size 20000 --format VDI
```

To create a SATA controller and attach the disk:

```bash
VBoxManage storagectl "Ubuntu-Server" --name "SATA Controller" --add sata --controller ahci
VBoxManage storageattach "Ubuntu-Server" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "Ubuntu-Server.vdi"
```

### Networking

By default, VirtualBox uses NAT. You can change this to a Bridged adapter in the "Network" tab of the GUI, or via the CLI:

```bash
VBoxManage modifyvm "Ubuntu-Server" --nic1 bridged --bridgeadapter1 en0
```

## Automation and Scripting

Because `VBoxManage` is a standard CLI tool, it can be wrapped in scripts to automate the deployment of complex environments.

Example deployment script (`deploy_vm.sh`):


```bash
#!/bin/bash
VM_NAME=$1
VM_RAM=${2:-1024}

echo "Creating VM: $VM_NAME..."
VBoxManage createvm --name "$VM_NAME" --ostype "Ubuntu_64" --register
VBoxManage modifyvm "$VM_NAME" --memory $VM_RAM --cpus 1
VBoxManage createmedium disk --filename "${VM_NAME}.vdi" --size 10000
VBoxManage storagectl "$VM_NAME" --name "SATA" --add sata
VBoxManage storageattach "$VM_NAME" \
           --storagectl "SATA" \
           --port 0 \
           --device 0 \
           --type hdd --medium "${VM_NAME}.vdi"
VBoxManage startvm "$VM_NAME" --type headless
echo "VM $VM_NAME is now running headlessly."
```


!!! note "Summary Checklist"
    - [ ] VirtualBox and Ubuntu LTS installed.
    - [ ] Hardware requirements met and VM profile selected.
    - [ ] VM created and configured using both GUI and `VBoxManage`.
    - [ ] VM started in headless mode via CLI.
    - [ ] Virtual disk created and attached via CLI.
    - [ ] Network adapter configured (NAT or Bridged).
    - [ ] Guest Additions installed and clipboard integration verified.
    - [ ] Basic automation script tested for VM deployment.

!!! note "Exercise 1: Basic Setup"
    Install Ubuntu Desktop on your computer using VirtualBox (GUI). Install Guest Additions and configure bidirectional copy-paste. Verify that you can move text between your host OS and the guest VM.

!!! note "Exercise 2: CLI Configuration"
    Using `VBoxManage`, create a new VM named "Study-VM" with 2GB of RAM. Create a 10GB VDI disk, attach it to a SATA controller, and start the VM in headless mode.
    Verify it is registered using `VBoxManage list vms`.

!!! note "Exercise 3: Infrastructure Automation"
    Write a bash script that creates and starts two identical VMs ("Node-1" and "Node-2") headlessly, each with 512MB of RAM. Ensure the script cleans up any existing VMs with those names before starting to avoid registration errors.

