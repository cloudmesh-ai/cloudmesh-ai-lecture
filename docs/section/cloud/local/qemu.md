# Virtual Machine Management with QEMU

!!! note "Learning Outcome"
    By the end of this section, you will be able to:
    * Install and configure QEMU on different operating systems.
    * Create virtual hard disks and install a Linux distribution.
    * Use QEMU to emulate different architectures, such as the Raspberry Pi.
    * Understand the differences between QEMU's behavior on Linux and Windows.


In this section, we provide a short example of how to use QEMU. We
will start with the installation, create a virtual hard
disk, install Ubuntu on the disk, and start the virtual machine. Next,
we will demonstrate how to emulate a Raspberry Pi with QEMU.

## Install QEMU

To install QEMU+KVM on Ubuntu/Linux Mint, please use:

```bash
sudo apt update
sudo apt install qemu-system-x86 qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
```

**Important:** To run QEMU with KVM acceleration without using `sudo`, you must add your user to the `kvm` and `libvirt` groups:

```bash
sudo usermod -aG kvm,libvirt $USER
```
*Note: You will need to log out and log back in for these changes to take effect.*

On macOS, QEMU can be installed with Homebrew:

```bash
brew install qemu
```

## Create a Virtual Hard Disk with QEMU

To create an image file with the size of 10GB and `qcow2` format
(the default format for QEMU images), run:

    $ qemu-img create -f qcow2 testing-image.img 10G

Note that a new file called `testing-image.img` is now created at your
home folder (or the place where you run the terminal). Note also that
the size of this file is not 10 Gigabytes, it is around 150KB only; QEMU
will not use any space unless needed by the virtual operating system, but
it will set the maximum allowed space for that image to 10 Gigabytes
only.

## Install Ubuntu on the Virtual Hard Disk

Now that we have created our image file, if we have an ISO file for a
Linux distribution (e.g., Ubuntu 22.04 LTS) and we want to test it
using QEMU with the image file as a hard drive, we can run:

```bash
qemu-system-x86_64 \
    -m 2048 \
    -boot d \
    -enable-kvm \
    -smp 2 \
    -netdev user,id=net0 -device e1000,netdev=net0 \
    -hda testing-image.img \
    -cdrom ubuntu-22.04-live-server-amd64.iso
```

!!! warning
    please adjust the network settings to match your environment. Read up on the internet how to do it and document.

### Command Breakdown:

*   `-m 2048`: Allocates 2048MB (2GB) of RAM to the virtual machine.
*   `-boot d`: Specifies the boot order. `d` tells QEMU to boot from the CD-ROM first.
*   `-enable-kvm`: Enables KVM (Kernel-based Virtual Machine) for hardware acceleration. This is critical for performance; without it, QEMU uses software emulation which is significantly slower. Ensure virtualization is enabled in your BIOS/UEFI.
*   `-smp 2`: Allocates 2 CPU cores to the virtual machine.
*   `-netdev user,id=net0 -device e1000,netdev=net0`: Configures a modern user-mode network stack, providing the VM with internet access.
*   `-hda testing-image.img`: Specifies the virtual hard disk image created in the previous step.
*   `-cdrom ubuntu-22.04-live-server-amd64.iso`: Specifies the ISO image to be used as the installation media.

## Booting the Installed System

Once the installation is complete, you can boot directly from the hard drive image by removing the `-cdrom` option:

```bash
qemu-system-x86_64 -m 2048 -enable-kvm -smp 2 -netdev user,id=net0 -device e1000,netdev=net0 -hda testing-image.img
```

*Note: `qemu-system-x86_64` is used to emulate a 64-bit x86 architecture.*

## Emulating a Raspberry Pi

To emulate a Raspberry Pi, you need a compatible kernel and a disk image. Because the Raspberry Pi uses an ARM architecture, we use `qemu-system-arm` instead of the x86 emulator.

1. **Download a pre-built kernel**:

   !!! warning
       the kernal is from the internet and has not be tested. 
       
   ```bash
   wget https://raw.githubusercontent.com/dhruvvyas90/qemu-rpi-kernel/master/kernel-qemu-4.4.34-jessie
   ```

2. **Download a Raspberry Pi OS image**:
   Download a `.img` file (Note: Ensure the filename in the launch command below matches the filename of the image you downloaded, e.g., rename it to `raspberrypi-os.img`) from the official [Raspberry Pi downloas page](https://www.raspberrypi.org/software/operating-systems/).

3. **Launch the Emulator**:
   Use the following command to emulate the ARM architecture:

   ```bash
   qemu-system-arm -kernel ./kernel-qemu-4.4.34-jessie \
       -append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" \
       -hda raspberrypi-os.img \
       -cpu arm1176 -m 256 -machine versatilepb \
       -no-reboot -serial stdio
   ```

**Note:**
* `kernel-qemu-4.4.34-jessie` is the pre-built kernel required for QEMU to boot the ARM image.
* `raspberrypi-os.img` should be the path to the image file you downloaded.


## QEMU on Windows

Because QEMU is fundamentally a Linux-native technology (leveraging KVM for hardware acceleration), running it on Windows differs slightly from Linux:

### How QEMU Runs on Windows

Acceleration (WHPX): On Windows, QEMU uses the Windows Hypervisor Platform (WHPX) or WinHv APIs under the hood. This allows QEMU to leverage Microsoft's hypervisor layer for hardware-accelerated virtualization, meaning your VMs run at near-native speed instead of crawling through pure software emulation.

* Binaries & Installation: You can download official or pre-compiled Windows binaries for QEMU (often provided via projects like QEMU for Windows or bundled with other tools).

* Command Line Interface: Like on Linux, QEMU on Windows is primarily a command-line tool. Spun up manually, it requires long chains of arguments to define disk images, RAM, ISOs, and networking.

QEMU is typically not used standalone on Windows. While it can be run directly via the command line on Windows, most Windows users avoid managing raw QEMU commands because native alternatives like Hyper-V, VMware Workstation Pro (which is now free for personal use), or VirtualBox offer much easier graphical interfaces.

However, QEMU is heavily used behind the scenes on Windows:

Android Studio Emulator: The official Android emulator for Windows uses QEMU under the hood to run ARM/x86 virtual devices.

WSL2 (Windows Subsystem for Linux): While WSL2 uses lightweight Hyper-V utility VMs, Microsoft's underlying architecture heavily borrows from virtualization concepts closely tied to QEMU/KVM ecosystem tooling.

Platform Backends: Tools like Vagrant or various container/cluster testing setups on Windows can sometimes utilize QEMU via alternative providers.

If you are on Windows, you can run QEMU, but unless you need a specific architecture emulation or are building a custom tooling pipeline, you will usually find a much smoother experience using Hyper-V (built into Windows Pro), VMware Workstation, or VirtualBox.

## Resources

### General

* Official website for `libvirt` is here: <https://libvirt.org/>
* Home page of KVM is here: <https://www.linux-kvm.org/page/Main_Page>
* QEMU home page: <https://www.qemu.org/>
* QEMU User Documentation: <https://qemu.weilnetz.de/doc/qemu-doc.html>
* Wikipedia page for QEMU: <https://en.wikipedia.org/wiki/QEMU>

### Comparison

* <http://opensourceforu.com/2012/05/virtualisation-faceoff-qemu-virtualbox-vmware-player-parallels-workstation/>
* <https://stackoverflow.com/questions/43704856/what-is-the-difference-qemu-vs-virtualbox>
* Wikipedia page for QEMU: <https://en.wikipedia.org/wiki/QEMU>

### Comparison

* <http://opensourceforu.com/2012/05/virtualisation-faceoff-qemu-virtualbox-vmware-player-parallels-workstation/>
* <https://stackoverflow.com/questions/43704856/what-is-the-difference-qemu-vs-virtualbox>
