# Hardware Emulation and Virtualization with QEMU

!!! info "Learning Objectives"
    - Install and configure QEMU on Linux and macOS.
    - Create and manage virtual disk images using `qemu-img`.
    - Deploy a full Linux distribution using QEMU.
    - Emulate non-native architectures (e.g., ARM) for cross-platform development.
    - Understand the role of KVM and WHPX in hardware acceleration.

Virtualization allows a single physical machine to run multiple isolated operating systems, but not all virtualization is the same. Most modern tools provide virtualization, where the guest OS runs on the same CPU architecture as the host, leveraging a hypervisor to execute instructions at near-native speed. However, there are cases where a developer needs to run software designed for an entirely different processor, such as testing a binary for an ARM-based Raspberry Pi on an x86-64 workstation.

QEMU (Quick Emulator) is a versatile, open-source tool that provides both full system emulation and virtualized execution. Unlike specialized hypervisors that only support the host's native architecture, QEMU can emulate a wide array of CPUs, memory controllers, and peripherals. When paired with a hardware accelerator like KVM (Kernel-based Virtual Machine) on Linux or WHPX (Windows Hypervisor Platform) on Windows, QEMU transforms from a software emulator into a high-performance virtualization engine.

## Installation and Environment Setup

QEMU is available across most major operating systems, though the installation process and acceleration capabilities vary.

### Linux Installation

On Ubuntu or Debian-based systems, QEMU is typically installed alongside KVM to ensure optimal performance.

```bash
sudo apt update
sudo apt install qemu-system-x86 qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```

To run QEMU with KVM acceleration without requiring root privileges for every command, the user must be added to the `kvm` and `libvirt` groups:

```bash
sudo usermod -aG kvm,libvirt $USER
```

Note that a logout and login are required for these group membership changes to take effect.

### macOS Installation

On macOS, QEMU can be installed via Homebrew:

```bash
brew install qemu
```

While macOS does not use KVM, QEMU can leverage the native macOS Virtualization.framework or QEMU's own acceleration hooks to improve performance.

## Managing Virtual Storage

Before a virtual machine can be launched, it requires a virtual hard disk. QEMU uses the `qemu-img` utility to create and manipulate these disk images.

### The qcow2 Format

QEMU supports several disk formats, but `qcow2` (QEMU Copy-On-Write version 2) is the standard. The primary advantage of `qcow2` is that it is a sparse file. If you create a 20GB disk, the file on your physical host will initially be very small (a few kilobytes). It only grows as the guest OS actually writes data to the disk.

### Creating a Virtual Disk

To create a 20GB virtual disk in the `qcow2` format, use the following command:

```bash
qemu-img create -f qcow2 virtual-disk.qcow2 20G
```

This command creates `virtual-disk.qcow2`, which acts as the primary storage for the guest operating system.

## Deploying a Virtual Machine

Launching a VM in QEMU involves specifying the hardware resources, the storage, and the boot media.

### The Installation Process

To install a Linux distribution (e.g., Ubuntu 22.04 LTS), you must boot from an ISO image and install it onto the virtual disk created previously.

```bash
qemu-system-x86_64 \
    -m 2048 \
    -smp 2 \
    -boot d \
    -enable-kvm \
    -netdev user,id=net0 -device e1000,netdev=net0 \
    -hda virtual-disk.qcow2 \
    -cdrom ubuntu-22.04-live-server-amd64.iso
```

### Command Breakdown

- `-m 2048`: Allocates 2048MB (2GB) of RAM to the virtual machine.
- `-smp 2`: Allocates 2 CPU cores to the virtual machine.
- `-boot d`: Sets the boot order to boot from the CD-ROM first.
- `-enable-kvm`: Enables KVM hardware acceleration. Without this, QEMU uses software emulation, which is significantly slower.
- `-netdev user,id=net0 -device e1000,netdev=net0`: Configures a user-mode network stack, providing the VM with internet access.
- `-hda virtual-disk.qcow2`: Specifies the virtual hard disk image.
- `-cdrom ubuntu-22.04-live-server-amd64.iso`: Specifies the installation media.

### Booting the Installed System

Once the installation is complete, you can boot directly from the hard drive by removing the `-cdrom` option and changing the boot order:

```bash
qemu-system-x86_64 \
    -m 2048 \
    -smp 2 \
    -enable-kvm \
    -netdev user,id=net0 -device e1000,netdev=net0 \
    -hda virtual-disk.qcow2
```

## Hardware Acceleration

The performance of a QEMU VM depends entirely on whether it is emulated or virtualized.

### KVM (Kernel-based Virtual Machine)

KVM is a Linux kernel module that turns the kernel into a Type-1 hypervisor. When QEMU uses `-enable-kvm`, it offloads the execution of guest instructions directly to the host CPU, provided the CPU supports virtualization extensions (Intel VT-x or AMD-V).

### WHPX (Windows Hypervisor Platform)

On Windows, QEMU can use the Windows Hypervisor Platform (WHPX). This allows QEMU to leverage Microsoft's hypervisor layer, providing similar performance gains as KVM on Linux.

!!! warning "Acceleration Requirements"
    Hardware acceleration requires that virtualization is enabled in the host's BIOS/UEFI settings. If disabled, QEMU will default to software emulation, resulting in extreme performance degradation.

## Cross-Architecture Emulation

One of QEMU's most distinct features is its ability to run code for different CPU architectures.

### Emulating ARM (Raspberry Pi)

To run a Raspberry Pi image on an x86-64 host, QEMU must emulate the ARM CPU. This process is slower than native virtualization because every ARM instruction must be translated to an x86-64 instruction.

### Launching an ARM VM

Emulating ARM often requires an external kernel file that QEMU can use to boot the image.

```bash
qemu-system-arm -kernel ./kernel-qemu-4.4.34-jessie \
    -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" \
    -hda raspberrypi-os.img \
    -cpu arm1176 -m 256 -machine versatilepb \
    -no-reboot -serial stdio
```

### Command Breakdown

- `-cpu arm1176`: Emulates the specific ARM CPU used in early Raspberry Pi models.
- `-machine versatilepb`: Specifies the machine type to be emulated.
- `-kernel`: Points to the pre-built Linux kernel required for booting the ARM image.
- `-append`: Passes boot arguments to the kernel.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] QEMU and KVM are installed and configured.
    - [ ] User is added to the `kvm` and `libvirt` groups.
    - [ ] A `qcow2` virtual disk has been created using `qemu-img`.
    - [ ] A Linux distribution has been installed using an ISO.
    - [ ] The VM boots successfully from the virtual disk with acceleration.
    - [ ] A non-native architecture (ARM) has been successfully emulated.

## Practical Exercises

!!! note "Exercise 1: Basic Virtualization"
    Install QEMU on your system. Create a 10GB `qcow2` disk image. Download a lightweight Linux ISO (such as Alpine Linux) and boot it using QEMU. Verify that you can reach the shell.

!!! note "Exercise 2: Full System Deployment"
    Deploy a full Ubuntu Server installation. Allocate 4GB of RAM and 4 CPU cores. Ensure that KVM acceleration is enabled and verify that the VM has internet access by pinging a public DNS server (e.g., 8.8.8.8).

!!! note "Exercise 3: Cross-Platform Testing"
    Obtain a Raspberry Pi OS image and a compatible QEMU ARM kernel. Emulate the ARM architecture and boot the image. Run `uname -m` inside the VM to verify that the system reports an ARM architecture despite running on an x86 host.

## Further Reading

- QEMU Official Documentation: https://www.qemu.org/documentation/
- KVM Project: https://www.linux-kvm.org/
- Libvirt Project: https://libvirt.org/
