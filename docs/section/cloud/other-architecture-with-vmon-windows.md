# Other Architectures with VM on Windows

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    - **Differentiate** between software emulation (QEMU) and hardware-assisted virtualization (Hyper-V, VMware, VirtualBox) on Windows x86_64.
    - **Identify** the primary tool capable of cross-architecture (e.g., ARM to x86_64) virtualization on Windows.
    - **Select** the appropriate hypervisor for running Raspberry Pi images and Android VMs on a Windows host.
    - **Compare** performance tradeoffs between TCG (Tiny Code Generator) and WHPX (Windows Hypervisor Platform).

QEMU (used directly or via various front-ends) is the primary tool on Windows x86_64 that can *truly* run guest machines of a different architecture – e.g., an ARM-based OS on an x86_64 Windows machine **and** also emulate the exact ARM hardware used by a Raspberry Pi.

Other Windows-native hypervisors (Hyper-V, VMware Workstation, Oracle VirtualBox) are **hybrid/“type-2” or “type-1” hypervisors that rely on hardware-assisted virtualization**, so they can only run **x86_64 guests** on an x86_64 Windows host. They cannot natively run an OS built for a different ISA (Instruction Set Architecture) like ARM or RISC-V.

Below is a comparison of the main options you’ll encounter on a Windows x86_64 machine, with a focus on cross-architecture support.

---

<a id="1-qemu-windows-native-or-via-front-ends"></a>
## 1. QEMU + Windows (native or via front-ends)

!!! info "Why this matters"
    Software emulation allows developers to maintain a single physical machine while testing software across multiple CPU architectures (ARM, RISC-V, PowerPC, etc.). This is critical for cross-platform development, embedded systems testing, and legacy maintenance.


| Feature | Details |
|---|---|
| **CPU-architecture support** | Full system-level emulation: can run **ARM64, ARMv7, RISC-V, PowerPC, MIPS**, etc. on Windows x86_64. It can also emulate **ARMv7/ARMv8** exactly as found on a Raspberry Pi (including the Broadcom BCM2837/BCM2711 SoC peripherals). |
| **Performance** | Because it is pure software emulation, raw CPU speed is significantly lower (often **5-20% of native**) for non-x86 workloads. For x86-on-x86 guests, you can enable the **Windows Hypervisor Platform (WHPX)** acceleration (`-accel whpx`) to achieve near-native speeds. |
| **Ease of use** | Command-line heavy by default. While there are fewer polished "all-in-one" GUIs like UTM (which is macOS only), users often use **QEMU** directly or integrate it with tools like **Vagrant** or custom scripts. |
| **Raspberry Pi specific** | QEMU can emulate the **BCM2835/BCM2836/BCM2837** SoC (the “raspi” machine types). You can boot official Raspberry Pi OS images on Windows as if they were running on a Pi. |
| **Licensing** | Open-source (GPL-2). Free to modify and redistribute. |
| **Typical use-cases** | • Testing ARM-based Linux distributions on a Windows laptop.<br>• Testing Raspberry Pi images without owning the physical board.<br>• Running legacy non-x86 software. |

**Why QEMU is the primary cross-ISA tool on Windows:**
- It uses **software translation** (TCG – Tiny Code Generator) to translate guest instructions (e.g., ARM) into host instructions (x86_64), meaning it is not limited by the host’s CPU ISA.
- Windows' `whpx` (Windows Hypervisor Platform) can be used to accelerate *x86-to-x86* virtualization, but the translation layer (TCG) must be used for *x86-to-ARM*.

!!! tip "Pro Tip: Choosing the Right Acceleration"
    When running an x86_64 guest on Windows via QEMU, always use `-accel whpx` (if Hyper-V/WHPX is enabled in Windows Features) or `-accel haxm` (for older Intel systems) to avoid the massive performance penalty of software emulation.


### Example: Launching an ARM64 Guest via QEMU CLI on Windows
```powershell
# Example command to emulate an ARM64 machine
qemu-system-aarch64 `
  -machine virt `
  -cpu cortex-a57 `
  -m 2048 `
  -kernel ubuntu-arm64-kernel `
  -append "root=/dev/vda console=ttyAMA0" `
  -drive file=ubuntu-arm64.qcow2,if=virtio `
  -netdev user,id=net0 -device virtio-net-device,netdev=net0 `
  -nographic
```

---

<a id="2-standard-hypervisors-hyper-v-vmware-virtualbox"></a>
## 2. Standard Hypervisors (Hyper-V, VMware, VirtualBox)

These tools are designed for **Virtualization**, not **Emulation**. They assume the Guest CPU is the same (or a subset) as the Host CPU.

| Tool | Primary Windows Use-case | Acceleration Method | Cross-ISA Support? |
|---|---|---|---|
| **Hyper-V** | Enterprise VMs, Docker Desktop, WSL2 | Native (Type-1) | No (x86 $\rightarrow$ x86 only) |
| **VMware Workstation** | High-performance Dev VMs | VMX / WHPX | No (x86 $\rightarrow$ x86 only) |
| **VirtualBox** | General purpose, Open Source | VT-x / AMD-V / WHPX | Very Limited/Experimental |

### The Role of WSL2 (Windows Subsystem for Linux)
WSL2 is a unique hybrid. It uses a highly optimized lightweight utility VM managed by Hyper-V. While it primarily runs x86_64 Linux, it can be configured to run ARM64 binaries via **binfmt_misc** and **QEMU-user emulation** internally, allowing you to run ARM64 containers on Windows x86_64 with surprising efficiency.

---

<a id="3-android-virtualization-on-windows"></a>
## 3. Android Virtualization on Windows

Running Android on Windows x86_64 usually takes one of three paths:

### A. Android Studio Emulator (The Standard)
The official Android Emulator is actually a **specialized QEMU front-end**. 
- **Architecture**: It can run both `x86_64` and `arm64-v8a` images.
- **Acceleration**: On Windows, it uses **WHPX (Windows Hypervisor Platform)** to accelerate `x86_64` images.
- **Performance**: `x86_64` images are extremely fast (near-native). `arm64` images are emulated via TCG and are significantly slower.

### B. BlueStacks / LDPlayer / Nox
These are "Android Players" optimized for gaming. They typically use a modified version of VirtualBox or a proprietary hypervisor to run x86-translated Android images, focusing on GPU acceleration for Windows.

### C. QEMU (Manual/Advanced)
For researchers needing to boot a raw Android system image (like a LineageOS build for a specific Pi device) on Windows, QEMU is the only choice.

**Example: Launching an Android-Pi image via QEMU on Windows**
```powershell
qemu-system-aarch64 `
  -M raspi3b `
  -cpu cortex-a53 `
  -m 1024 `
  -kernel kernel-android-pi.bin `
  -sd lineage-pi.img `
  -append "root=/dev/mmcblk0p2 rw console=ttyAMA0" `
  -serial stdio `
  -display sdl
```

---

### Summary

- **QEMU** is the only tool on Windows x86_64 that can truly run *any* architecture, including ARM64 and Raspberry-Pi-specific builds.
- **Hyper-V, VMware, and VirtualBox** provide high performance but are limited to the host's architecture (x86_64).
- **Android Emulator** (via Android Studio) is the best balance for developers, leveraging WHPX for x86_64 images while providing QEMU-based emulation for ARM64 images.

---

## Assignments

!!! note "Assignment 1: Emulation vs. Virtualization"
    Install **Oracle VirtualBox** or enable **Hyper-V**. Create a standard **x86_64 Ubuntu VM**. Then, install **QEMU for Windows**. Attempt to boot an **ARM64 Linux image** (or a small RISC-V image). Compare the boot speed and UI responsiveness. Note the difference between hardware-assisted virtualization (VirtualBox/Hyper-V) and software emulation (QEMU TCG).

!!! note "Assignment 2: Raspberry Pi Emulation"
    Using the QEMU CLI on Windows, configure a VM with the `raspi3b` or `raspi4` machine type. Attempt to boot a Raspberry Pi OS image. Verify that you can access the shell and run `uname -a` to confirm the guest is running an ARM architecture on your x86 host.

!!! note "Assignment 3: Android Architecture Audit"
    Create an Android Virtual Device (AVD) in Android Studio. Use the `adb shell getprop ro.product.cpu.abi` command to verify if the running device is `arm64-v8a` or `x86_64`. Based on the result, determine if your emulator is using WHPX acceleration or TCG emulation.

---

!!! info "Self-Assessment"
    Test your knowledge by expanding the questions below.

    ??? question "Which tool is the only one capable of running ARM64 guests on an x86_64 Windows machine?"
        **QEMU**. It uses software translation (TCG) to emulate the ARM64 instruction set on x86_64 hardware.

    ??? question "What is the primary difference between TCG and WHPX in QEMU on Windows?"
        **TCG (Tiny Code Generator)** is a software emulator that translates instructions from one architecture to another (slow). **WHPX (Windows Hypervisor Platform)** is a hardware-assisted virtualization layer that allows a guest of the *same* architecture (x86_64) to run at near-native speed (fast).

    ??? question "Why can't Hyper-V run an official Raspberry Pi image?"
        Hyper-V relies on hardware-assisted virtualization, which requires the guest to share the host's ISA (x86_64). Raspberry Pi images are built for **ARM** and rely on specific **Broadcom SoC peripherals** (board emulation), which Hyper-V does not provide. QEMU provides this specific board emulation.

    ??? question "If you need maximum performance for an x86_64 Linux VM on Windows, which tool should you choose?"
        **Hyper-V** or **VMware Workstation**, as they are highly optimized for the Windows kernel and offer near-native performance.

    ??? question "What is the performance penalty for running ARM64 workloads on Windows x86_64 via QEMU?"
        Raw CPU speed is typically only **5-20% of native** performance because every ARM instruction must be translated to an x86 instruction via software.

    ??? question "How do you launch an Android Virtual Device (AVD) from the command line on Windows?"
        You use the emulator tool located in the Android SDK:
        `%LOCALAPPDATA%\Android\Sdk\emulator\emulator.exe -avd <name>`
