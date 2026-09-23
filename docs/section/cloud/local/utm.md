# macOS Virtualization with UTM

!!! info "Learning Objectives"
    - Install and configure UTM on macOS.
    - Differentiate between "Virtualize" and "Emulate" modes.
    - Deploy and configure a Linux guest OS using UTM.
    - Manage hardware resources (CPU, RAM, Storage) within the UTM interface.
    - Configure basic networking and shared directories for guest-host integration.

For many users, the command-line interface of tools like QEMU or Lima is insufficient for tasks that require a full graphical desktop environment or complex manual installation processes. While headless VMs are ideal for servers, developers often need a "desktop-in-a-box" experience to test GUI applications, use a different OS for browsing, or run software that requires a visual installer.

UTM is a native macOS application that provides a graphical user interface for virtualization and emulation. It serves as a sophisticated wrapper around QEMU and Apple's Virtualization framework. By abstracting the complex command-line arguments of QEMU into a visual wizard, UTM makes it accessible to deploy a wide variety of operating systems on macOS, whether they share the host's architecture or require full system emulation.

## Core Concepts: Virtualization vs. Emulation

The most critical decision when creating a VM in UTM is choosing between the "Virtualize" and "Emulate" options. This choice determines the performance and compatibility of the guest OS.

### Virtualization

When you select "Virtualize", UTM uses Apple's Hypervisor framework. This allows the guest OS to execute instructions directly on the host CPU.

- **Requirement**: The guest OS architecture must match the host architecture (e.g., ARM64 Linux on Apple Silicon).
- **Performance**: Near-native speed.
- **Use Case**: Running a Linux server or desktop for development on the same architecture as the Mac.

### Emulation

When you select "Emulate", UTM uses QEMU to simulate a completely different CPU architecture.

- **Requirement**: None; it can run almost any architecture (e.g., x86_64 Windows on Apple Silicon).
- **Performance**: Significantly slower, as every guest instruction must be translated to the host architecture.
- **Use Case**: Running legacy software or testing binaries for a different processor architecture.

## Installation and Setup

UTM is distributed as a standalone application and can be installed through multiple channels.

### Installing UTM

The most direct method is downloading the `.dmg` file from the official UTM website. Alternatively, it can be installed via Homebrew Cask:

```bash
brew install --cask utm
```

Once installed, UTM can be launched from the Applications folder. No additional backend installation is required, as UTM bundles the necessary QEMU binaries.

## Creating a Virtual Machine

UTM uses a guided wizard to simplify the configuration of virtual hardware.

### The Configuration Wizard

1. Click the **Create a New Virtual Machine** button.
2. Choose between **Virtualize** (for native speed) or **Emulate** (for cross-platform compatibility).
3. Select the operating system. For Linux, choose the **Linux** option.
4. Provide the installation media. This typically involves selecting an ISO image (e.g., Ubuntu Server ARM64).
5. Configure the hardware resources:
    - **Memory**: Allocate RAM (e.g., 4096 MB for a smooth experience).
    - **CPU**: Define the number of cores.
6. Finalize the storage by specifying the disk size.

### Launching and Installation

After the wizard completes, click the **Play** button in the UTM sidebar to start the VM. The VM will boot from the mapped ISO, and the user must follow the standard installation prompts of the guest operating system to install it onto the virtual hard disk.


## Performance Tuning

To move beyond the basic configuration and achieve maximum efficiency, you should optimize the virtual hardware settings.

### VirtIO: The Gold Standard for I/O
By default, UTM may use generic emulated hardware for compatibility. However, for near-native performance, you should use **VirtIO** drivers for both networking and storage. VirtIO is a virtualization standard for network and disk device drivers that reduces the overhead of emulation.

- **Storage**: In the VM settings, ensure the disk interface is set to `VirtIO`.
- **Network**: Set the network interface to `VirtIO-net`.

### GPU Acceleration
For VMs requiring a graphical desktop, the default display can feel sluggish. Enabling **VirtIO-GPU** with OpenGL acceleration (where supported) significantly improves the smoothness of the guest UI.

### CPU Model Selection
When using "Emulate" mode, the choice of CPU model affects both compatibility and speed. While `qemu64` is the safest default, selecting a more modern CPU model (like `host` if virtualizing) can unlock advanced instruction sets (e.g., AVX) that speed up computational tasks in the guest.

## Managing the Guest Environment

UTM provides several tools to manage the VM once it is running.

### Installing Guest Tools

Many advanced features, such as shared directories, dynamic resolution, and the `utmctl` command-line interface, require a guest agent to be installed inside the virtual machine. Without these tools, the host cannot communicate deeply with the guest OS.

For Linux guests (Ubuntu/Debian), install the agents by running:

```bash
sudo apt update
sudo apt install spice-vdagent qemu-guest-agent
```

After installation, restart the VM to ensure the services are active.

### Console and Headless Mode

By default, UTM opens a graphical window showing the VM's screen. For server-based VMs, this is often unnecessary. Users can configure the VM to start in "headless" mode and connect via SSH using the macOS terminal:

```bash
ssh username@guest-ip-address
```

### Networking and Integration

UTM supports different networking modes to control how the VM communicates with the host and the external network:

- **Shared Network**: The VM is behind a virtual NAT, allowing it to access the internet but remaining invisible to the external network.
- **Bridged Network**: The VM appears as a separate device on the physical network, receiving its own IP address from the router.

### Shared Directories

To move files between macOS and the guest OS without using network transfers, UTM supports shared directories. By adding a folder in the VM settings under the "Sharing" tab, UTM uses the VirtFS (9p) protocol to map a macOS folder into the guest's filesystem.

## Snapshotting and State Management

Virtualization allows you to save the exact state of a machine, providing a safety net for experimentation.

### Suspending vs. Snapshotting
It is important to distinguish between these two concepts:

- **Suspending (Save State)**: This is like putting a laptop to sleep. UTM saves the current RAM state to disk and stops the CPU. When you resume, you are exactly where you left off.
- **Snapshotting**: This is a permanent point-in-time recovery image. A snapshot records the state of the virtual disk and configuration. You can return to a snapshot multiple times, even after you have continued working and made further changes.

### Creating and Restoring Snapshots
In the UTM sidebar, you can right-click a VM and select **Snapshots**. From here, you can create a named snapshot (e.g., "Before System Update") and restore the VM to that state if something goes wrong.

## Portability and Backup

UTM makes it easy to move virtual machines between different macOS devices or share them with collaborators.

### Exporting VMs
You can export a VM as a `.utm` package. This package contains the virtual disk images and the configuration file. To export, right-click the VM in the sidebar and select **Export**.

### Importing and Sharing
A `.utm` file can be imported into any UTM installation. This is the ideal way to distribute "pre-baked" development environments to a team, ensuring everyone is working on the exact same OS version and configuration.

## Command-Line Interface (utmctl)

For users who prefer the terminal or need to automate VM management, UTM provides a powerful command-line utility called `utmctl`. This tool allows you to perform most of the actions available in the GUI directly from the macOS terminal.

### Accessing utmctl

The `utmctl` binary is bundled within the UTM application package. You can run it using its absolute path:

```bash
/Applications/UTM.app/Contents/MacOS/utmctl --help
```

To make it easier to use, you can add an alias to your shell configuration (e.g., `.zshrc`):

```bash
alias utmctl='/Applications/UTM.app/Contents/MacOS/utmctl'
```

### Common Commands

Here are the most useful `utmctl` commands for daily management:

| Command | Description | Example |
| :--- | :--- | :--- |
| `list` | Lists all configured virtual machines | `utmctl list` |
| `start` | Starts or resumes a specific VM | `utmctl start "Ubuntu"` |
| `stop` | Requests a graceful shutdown | `utmctl stop "Ubuntu" --request` |
| `status` | Displays the current state of a VM | `utmctl status "Ubuntu"` |
| `ip-address` | Retrieves the guest OS IP address | `utmctl ip-address "Ubuntu"` |
| `exec` | Executes a command inside the guest | `utmctl exec "Ubuntu" -- uptime` |
| `suspend` | Suspends the VM state | `utmctl suspend "Ubuntu"` |
| `dict` | Displays detailed VM configuration | `utmctl dict "Ubuntu"` |

## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "In UTM, when should you use 'Virtualize' instead of 'Emulate'?"
    You should use "Virtualize" when the guest OS architecture matches the host architecture (e.g., ARM64 Linux on Apple Silicon) to achieve near-native performance.

??? question "How does UTM's 'Emulate' mode enable running x86_64 Windows on Apple Silicon?"
    The "Emulate" mode uses QEMU to simulate an x86_64 CPU, translating its instructions to ARM64 instructions that the Apple Silicon chip can execute, albeit at a significantly lower speed.

??? question "What is the benefit of 'headless' mode in UTM?"
    Headless mode allows the VM to run in the background without a graphical window, which is ideal for server-based VMs that are managed via SSH.

??? question "How can you share files between macOS and a UTM guest VM?"
    By configuring a "Shared Directory" in the VM settings, UTM uses the VirtFS (9p) protocol to map a macOS folder into the guest's filesystem.

??? question "What is the relationship between UTM and QEMU?"
    UTM is a graphical user interface (GUI) wrapper around QEMU and Apple's Virtualization framework, making the power of QEMU accessible through a visual wizard.

??? question "How can you manage UTM virtual machines from the command line?"
    You can use the `utmctl` utility, located at `/Applications/UTM.app/Contents/MacOS/utmctl`, to perform tasks like starting, stopping, and listing VMs without using the GUI.

## Practical Exercises

!!! note "Exercise 1: Basic Native Virtualization"
    Install UTM and create a new virtual machine using the "Virtualize" option. Use a native ARM64 Linux ISO (such as Ubuntu Server) to install the OS. Boot the VM and verify that it runs with native performance.

!!! note "Exercise 2: Cross-Architecture Emulation"
    Create a second virtual machine using the "Emulate" option. Choose an x86_64 architecture and boot a lightweight Linux distribution. Compare the boot time and general responsiveness of this VM against the virtualized VM from Exercise 1.

!!! note "Exercise 3: Host-Guest Integration"
    In the settings of your Linux VM, configure a shared directory that points to a folder on your macOS desktop. Inside the Linux guest, mount the shared folder and create a text file. Verify that the file appears instantly on your macOS desktop.

!!! note "Assignment: Hosting a Web Service"
    This assignment synthesizes all the concepts covered in this chapter. You will move from a GUI installation to a fully automated, headless web server.

    **Objective.** Deploy a Linux server that hosts a public-facing web page, managed entirely via the command line.

    **Task Sequence**

    1. **Provisioning**: 
       - Create a new Ubuntu Server VM using the "Virtualize" option.
       - Configure it to start in **headless mode**.

    2. **Environment Setup**:
       - Boot the VM and install the **Guest Tools** (`spice-vdagent` and `qemu-guest-agent`).
       - Reboot the VM.

    3. **Infrastructure Discovery**:
       - Use the macOS terminal and `utmctl ip-address "Your-VM-Name"` to find the internal IP address of the server.

    4. **Service Deployment**:
       - SSH into the VM: `ssh username@guest-ip`.
       - Install a web server: `sudo apt install nginx -y`.
       - Create a simple HTML page in `/var/www/html/index.html` that says "Hello from UTM Virtualized Server!".

    5. **Verification**:
       - Open a web browser on your macOS host and navigate to the VM's IP address. Verify that your web page is visible.

    6. **Automation Integration**:
       - Add your VM's name to the `Makefile` provided in the previous appendix.
       - Verify that you can start, stop, and check the status of your web server using `make start`, `make stop`, and `make status`.

    **Submission Criteria**

    - A screenshot of the web page being accessed from the macOS browser.
    - A terminal log showing the successful output of `make status` and `utmctl ip-address`.

## Appendix: Guest Tools Automation

Since `utmctl` and shared directories rely on the guest agent being installed inside the VM, you can automate this process using a `Makefile` and SSH.

### Guest Tools Bootstrap Makefile

Create a file named `Makefile.guest` in your project directory:

```makefile
# Guest Tools Installation Makefile
# 

# Configuration variables
VM_USER ?= ubuntu
VM_IP   ?= 192.168.64.x  # Replace with your VM's current IP
SSH_CMD = ssh -o StrictHostKeyChecking=no $(VM_USER)@$(VM_IP)

.PHONY: help install verify clean

help:
	@echo "Guest Tools Automation"
	@echo "======================="
	@echo "Target: $(VM_USER)@$(VM_IP)"
	@echo ""
	@echo "Available Commands:"
	@echo "  make install   - Install spice-vdagent and qemu-guest-agent"
	@echo "  make verify    - Verify agent installation via utmctl"
	@echo ""

install:
	@echo "Installing guest tools on $(VM_IP)..."
	@$(SSH_CMD) "sudo apt update && sudo apt install -y spice-vdagent qemu-guest-agent"
	@echo "Installation complete. Please reboot the VM for changes to take effect."

verify:
	@echo "Verifying guest tools for VM..."
	@/Applications/UTM.app/Contents/MacOS/utmctl ip-address
	@echo "If the IP address was returned successfully, the agent is running."

clean:
	@echo "Nothing to clean."
```

### Using the Bootstrap Makefile

Because you cannot use `utmctl` to install the agent (as the agent is required for `utmctl` to work), this Makefile uses SSH to bootstrap the VM.

1.  **Find the IP**: Use the UTM GUI to find the IP address of your running VM.
2.  **Run Installation**:
    ```bash
    make -f Makefile.guest install VM_IP="192.168.64.5"
    ```
3.  **Reboot**: Reboot the VM via the UTM GUI.
4.  **Verify**:
    ```bash
    make -f Makefile.guest verify
    ```

## Appendix: VM Automation

To simplify the management of virtual machines, you can use a `Makefile`. This allows you to create shorthand commands for frequently used `utmctl` operations.

### UTM Management Makefile

Create a file named `Makefile` in your project directory and paste the following content:

```makefile
# UTM Virtual Machine Management Makefile
# 

# Configuration variables (override via command line: make start VM_NAME="Ubuntu")

VM_NAME ?= Ubuntu 24.04
UTMCTL  ?= /Applications/UTM.app/Contents/MacOS/utmctl

.PHONY: help list status start stop suspend-disk suspend-mem ip-address exec-demo info

# Default target
help:
	@echo 
	@echo " UTM Virtual Machine CLI Automation (utmctl)"
	@echo "==================================="
	@echo "Target VM Configuration: '$(VM_NAME)'"
	@echo ""
	@echo "Available Commands:"
	@echo "  make list            - List all available virtual machines"
	@echo "  make status          - Check the status of the target VM"
	@echo "  make start           - Start or resume the target VM (GUI/Headless)"
	@echo "  make stop            - Gracefully stop/request shutdown via guest agent"
	@echo "  make suspend-disk    - Suspend VM and save state to disk"
	@echo "  make suspend-mem     - Suspend VM to memory only"
	@echo "  make ip-address      - Retrieve the guest IP address"
	@echo "  make exec-demo       - Run a test command inside the guest OS"
	@echo "  make info            - Show detailed configuration info for the VM"
	@echo ""

list:
	@echo "Listing all configured UTM virtual machines..."
	@$(UTMCTL) list

status:
	@echo "Checking status of '$(VM_NAME)'..."
	@$(UTMCTL) status "$(VM_NAME)"

start:
	@echo "Starting '$(VM_NAME)'..."
	@$(UTMCTL) start "$(VM_NAME)"

stop:
	@echo "Sending graceful shutdown request to '$(VM_NAME)'..."
	@$(UTMCTL) stop "$(VM_NAME)" --request

suspend-disk:
	@echo "Suspending '$(VM_NAME)' and saving state to disk..."
	@$(UTMCTL) suspend "$(VM_NAME)" --force

suspend-mem:
	@echo "Suspending '$(VM_NAME)' to memory..."
	@$(UTMCTL) suspend "$(VM_NAME)"

ip-address:
	@echo "Fetching IP address for '$(VM_NAME)'..."
	@$(UTMCTL) ip-address "$(VM_NAME)"

exec-demo:
	@echo "Executing command inside '$(VM_NAME)' via guest agent..."
	@$(UTMCTL) exec "$(VM_NAME)" -- uname -a
	@$(UTMCTL) exec "$(VM_NAME)" -- uptime

info:
	@echo "Displaying configuration details for '$(VM_NAME)'..."
	@$(UTMCTL) dict "$(VM_NAME)"
```

Using this Makefile, you can start your VM with a simple command:
```bash
make start
```
Or target a different VM:
```bash
make start VM_NAME="Debian"
```

## Further Reading

- UTM Official Website: https://mac.getutm.app/
- UTM Official Documentation: https://getutm.app/support/
- Apple Virtualization Framework: https://developer.apple.com/documentation/virtualization
- QEMU Project: https://www.qemu.org/
