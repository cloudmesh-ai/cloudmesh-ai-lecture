# Virtual Machine Management with VirtualBox

!!! note "Learning Outcome"
    By the end of this section, you will be able to:
    * Install and configure Oracle VirtualBox and an Ubuntu LTS guest OS.
    * Understand the importance of LTS versions for stability and support.
    * Configure essential VM features like Guest Additions, shared clipboards, and shared folders.
    * Manage VM resource allocation (CPU, RAM, Disk) based on different use cases.

For development purposes, we recommend using an Ubuntu virtual machine set up with Oracle VirtualBox. It is crucial to use a current LTS (Long Term Support) version of Ubuntu (e.g., 22.04 or 24.04) rather than outdated versions.

## Installation

### VirtualBox

VirtualBox is free and open-source. Detailed installation instructions for your specific operating system can be found at:
* [VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads)

### Ubuntu ISO

Download the latest Ubuntu Desktop LTS image:
* [Ubuntu Desktop Download](http://www.ubuntu.com/download/desktop)

### Hardware Requirements

Depending on your host machine's specifications, you may find that some configurations are too resource-constrained. We recommend the following minimal host setup for a smooth experience:
*   **CPU**: Multi-core processor with virtualization extensions (VT-x or AMD-V) enabled in BIOS/UEFI.
*   **RAM**: At least 8 GB of system memory.
*   **Storage**: At least 50 GB of free hard drive space.

### Recommended VM Configurations

Depending on your task, you may want to adjust the resources allocated to the VM:

| Profile | CPU Cores | RAM | Disk Space | Use Case |
| :--- | :---: | :---: | :---: | :--- |
| **Minimal** | 1 | 2 GB | 10 GB | Basic Linux CLI tasks |
| **Development** | 2 | 4 GB | 25 GB | IDEs, Compiling, LaTeX |
| **Heavy** | 4 | 8 GB | 50 GB | Docker, Heavy Data Processing |

A tutorial video for the installation process is available here:
[![Video](images/video.png) Using Ubuntu in VirtualBox](https://youtu.be/NWibDntN2M4)

!!! warning "Version Note"
    Tutorial videos may show older versions of Ubuntu (e.g., 16.04 or 18.04). Always install the latest LTS version available at the time of your installation.

## Guest Additions

Installing **Guest Additions** is highly recommended as it enables essential features:
*   **Dynamic Window Resizing**: The VM resolution automatically adjusts to the window size.
*   **Shared Clipboard**: Allows copy-pasting text between the host and guest OS.
*   **Shared Folders**: Easy file transfer between host and guest.

A guide for installing Guest Additions can be found here:
[![Video](images/video.png) VirtualBox Guest Additions Guide](https://youtu.be/wdCoiNdn2jA)

**Important**: Please reboot the virtual machine after installing Guest Additions to apply the changes.

### Copy-Paste Configuration (macOS)

To enable the shared clipboard on macOS, go to **Devices** $\rightarrow$ **Shared Clipboard** $\rightarrow$ **Bidirectional**.

*   **Host (macOS) $\rightarrow$ Guest (Ubuntu)**: `Cmd + C` $\rightarrow$ `Ctrl + Shift + V` (in terminal)
*   **Guest (Ubuntu) $\rightarrow$ Host (macOS)**: `Ctrl + Shift + C` $\rightarrow$ `Cmd + V`

## Exercises

!!! assignment "Exercise 1: Installation"
    Install Ubuntu Desktop on your computer using VirtualBox and successfully install the Guest Additions.

!!! assignment "Exercise 2: Clipboard Integration"
    Configure bidirectional copy-paste and verify that you can move text between your host OS and the guest VM.

!!! assignment "Exercise 3: Environment Setup"
    Install the required development tools and programs as defined in the course configuration.

!!! assignment "Exercise 4: OS Knowledge"
    Identify and document the specific key combinations required to copy and paste between your specific host OS (Windows/macOS/Linux) and the VirtualBox guest.