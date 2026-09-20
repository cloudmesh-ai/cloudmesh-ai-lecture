# Other Architectures with VM on Apple Silicon

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:

    - **Differentiate** between software emulation (QEMU) and hardware-assisted virtualization (Parallels, VMware, Apple VF) on Apple Silicon.
    - **Identify** the only tool capable of cross-architecture (e.g., x86_64 to ARM) virtualization on macOS.
    - **Select** the appropriate hypervisor for running Raspberry Pi images and Android VMs.
    - **Compare** performance tradeoffs between TCG (Tiny Code Generator) and HVF (Hypervisor.framework).




QEMU (used directly or via front-ends such as UTM, Multipass, or the open-source “QEMU-VM” scripts) is the only hypervisor on Apple Silicon that can *truly* run guest machines of a different architecture – e.g., an x86_64 OS on an ARM-based Mac **and** also emulate the exact ARM hardware used by a Raspberry Pi.


Other macOS-native hypervisors (Parallels Desktop, VMware Fusion Tech-Preview, Apple’s own Virtualization Framework) are **hybrid/“type-2” hypervisors that rely on hardware-assisted virtualization**, so they can only run **ARM-64 guests** on an ARM Mac (or x86_64 guests on an Intel Mac). They cannot run an OS built for a different ISA.

Below is a comparison of the main options you’ll encounter on an ARM-based Mac, with a focus on cross-architecture support.

---

<a id="1-qemu-apple-silicon-native-or-via-front-ends"></a>
## 1. QEMU + Apple Silicon (native or via front-ends)

!!! info "Why this matters"
    Software emulation allows developers to maintain a single physical machine while testing software across multiple CPU architectures (x86, ARM, RISC-V, etc.). This is critical for cross-platform development and legacy system maintenance.


| Feature | Details |
|---|---|
| **CPU-architecture support** | Full system-level emulation: can run **x86-64, i386, PowerPC, MIPS, RISC-V**, etc. on Apple Silicon. It can also emulate **ARMv7/ARMv8** exactly as found on a Raspberry Pi (including the Broadcom BCM2837/BCM2711 SoC peripherals). |
| **Performance** | Because it is pure software emulation, raw CPU speed is roughly **5-20% of native** for x86-64 workloads (depends on workload and the use of TCG vs. Apple’s Hypervisor.framework assisted JIT). For ARM-to-ARM (e.g., running a Raspberry-Pi image) you can enable the **Hypervisor.framework acceleration** (`-accel hvf`) which gives near-native speeds. |
| **Ease of use** | Command-line heavy, but many GUI front-ends exist: <br>• **UTM** – a polished, sandboxed macOS app that ships QEMU under the hood. <br>• **Multipass** – uses QEMU for non-Intel Macs when you ask for a non-ARM image. <br>• **QEMU-GUI (QEMU-Manager, AQEMU, etc.)** – more developer-oriented. |
| **Raspberry Pi specific** | QEMU can emulate the **BCM2835/BCM2836/BCM2837** SoC (the “raspi” machine types). You can boot the official Raspberry Pi OS images as if they were running on a Pi. |
| **Licensing** | Open-source (GPL-2). Free to modify and redistribute. |
| **Typical use-cases** | • Running legacy Windows 7/10 (x86) on a Mac M1/M2.<br>• Testing Raspberry Pi images on a laptop without the board.<br>• Cross-platform CI that needs to spin up an ARM image on an ARM host. |

**Why QEMU is the only “true” cross-ISA hypervisor on macOS Arm:**
- It does **software translation** (TCG – Tiny Code Generator) of guest instructions to host instructions, so it is not limited by the host’s CPU ISA.
- Apple’s own `hvf` (Hypervisor.framework) can be layered on top to accelerate *ARM-to-ARM* virtualization, but the translation layer stays for *ARM-to-x86*.

!!! tip "Pro Tip: Choosing the Right Acceleration"
    When running an ARM64 guest on Apple Silicon, always use `-accel hvf` in your QEMU command line. Without it, QEMU will use TCG (emulation), and your VM will feel incredibly slow. With it, you are using hardware-assisted virtualization.


---

<a id="2-parallels-desktop-for-mac-apple-silicon-edition"></a>
## 2. Parallels Desktop for Mac (Apple Silicon edition)

!!! info "Why this matters"
    For developers who need to run Windows or Linux on their Mac for daily productivity, hardware-assisted virtualization provides the necessary performance to make the VM feel like a native application.


| Feature | Details |
|---|---|
| **CPU-architecture support** | **ARM-only** guests (macOS ARM, Linux ARM, Windows 10/11 ARM). No x86/x86-64 emulation. |
| **Performance** | Uses Apple’s Hypervisor.framework (hardware-assisted). Near-native speeds for ARM guests (≈ 90-100% of native). |
| **Raspberry Pi** | Cannot directly run a Pi-specific image because QEMU’s “raspi” board emulation is missing. You could run a generic ARM Linux distro, but not the exact Pi hardware peripherals. |
| **Ease of use** | Very polished GUI, one-click installation, seamless integration with macOS (shared folders, drag-and-drop, Coherence mode). |
| **Licensing / cost** | Commercial, paid per-machine (subscription or perpetual). |
| **Typical use-cases** | • Running ARM versions of Windows/macOS for development.<br>• Running Linux ARM distros for testing.<br>• Desktop virtualization with high-performance graphics (Apple-GPU passthrough). |

**Bottom line:** Great for high-performance ARM-on-ARM workflows where GUI convenience and native speed are more important than architecture flexibility.

---

<a id="3-vmware-fusion-tech-preview-apple-virtualization-framework"></a>
## 3. VMware Fusion Tech-Preview & Apple Virtualization Framework

:::info "Why this matters"
The Apple Virtualization Framework is the foundational API that many other tools use. Understanding it helps in understanding how macOS manages VMs at the kernel level.
:::

| Feature | Details |
|---|---|
| **CPU-architecture support** | **ARM-only** (on Apple Silicon). |
| **Performance** | Near-native (uses Apple's Hypervisor.framework). |
| **Ease of use** | VMware Fusion is a traditional GUI; Apple's framework is an API for developers (though tools like UTM can use it). |
| **Key Limitation** | Like Parallels, it cannot translate x86 instructions to ARM. |

:::warning "Common Pitfall"
Do not confuse "Virtualization" with "Emulation". Virtualization (HVF) is fast but requires the guest and host to share the same CPU architecture. Emulation (TCG) is slow but can run any architecture.
:::

---

<a id="4-android-on-apple-silicon"></a>
## 4. Android on Apple Silicon

Running Android on Apple Silicon can be confusing because there are multiple ways to do it, and they differ wildly in architecture support.

### Android Emulator (Android Studio)
The official Android Emulator is actually a highly customized **QEMU front-end**. It uses Apple's `hvf` acceleration for ARM64 images.

### Architecture Comparison for Android

| Hypervisor / Tool | Can run **official Android ARM64 AVD**? | Can run **Android-x86 ISO**? | Can run **Raspberry-Pi Android builds**? | Approx. performance* |
|-------------------|-------------------------------------------|------------------------------|------------------------------------------|----------------------|
| Android Emulator (Studio) | ✔️ (native, hvf) | ✔️ (slow, translation) | ❌ (no Pi board emulation) | ARM64 ≈ 90-100% native; x86 ≈ 10-20% |
| UTM (QEMU) | ✔️ (via QEMU, hvf) | ✔️ (TCG) | ✔️ (raspi3/4 machine) | ARM64 ≈ 80-95%; x86 ≈ 5-15% |
| Parallels Desktop | ✔️ (import AVD image) | ❌ (no x86 support) | ❌ | ARM64 ≈ 95-100% |
| VMware Fusion (Tech-Preview) | ✔️ (import AVD) | ❌ | ❌ | ARM64 ≈ 90-100% |
| Apple Virtualization Framework (custom) | ✔️ (if you write a small boot loader) | ❌ | ❌ | ≈ 100% (native) |
| Docker Desktop (adb-only) | ❌ (no UI) | ❌ | ❌ | N/A (headless) |

\*Performance numbers are **relative to native hardware** and are based on typical workloads measured on an M1-Mac (4-core, 8 GB RAM). Real-world results can vary with the specific Android build, graphics settings, and allocated RAM/CPU.

---

<a id="5-practical-recommendations-for-different-use-cases"></a>
## 5. Practical recommendations for different use-cases

| Use-case | Best tool(s) | Why |
|----------|--------------|-----|
| **Developing Android apps in Android Studio** | **Android Emulator** (built-in) | Direct integration with Studio, ADB, and Play Store images. |
| **Testing an Android x86 custom ROM** | **QEMU** (or **UTM**) | Full-system x86 emulation; you can script the launch for CI. |
| **Running Android on a “desktop-style” VM with macOS window management** | **Parallels Desktop** (or **UTM** if you need x86) | Seamless windowing, snapshots, drag-and-drop files. |
| **Validating a Raspberry-Pi-targeted Android build without a Pi board** | **QEMU** via `raspi4` machine (UTM GUI makes this painless). |
| **CI/CD pipeline that needs to spin up Android for UI tests** | **Android Emulator** + **headless mode** (`-no-window`) or **Docker-based ADB-only containers**. |
| **Maximum native speed (e.g., GPU-intensive games or AR experiments)** | **Parallels Desktop** or **Android Emulator** (both use Metal for graphics via hvf). |

---


## 6. One-line cheat-sheet

Below are example commands for common virtualization tasks on Apple Silicon.

### Example: Launching an ARM64 AVD
```bash
# Launch an official Android Virtual Device (AVD) from the command line
~/Library/Android/sdk/emulator/emulator -avd <name>
```

### Example: Running Android-x86 ISO in QEMU
```bash
# This command uses QEMU to emulate x86_64 hardware on ARM. 
# Note: This will be slow due to software translation (TCG).
qemu-system-x86_64 \
  -machine q35,accel=hvf \
  -cpu host \
  -smp 4 \
  -m 4G \
  -drive file=android.qcow2,if=virtio \
  -cdrom android-x86.iso \
  -boot d \
  -display cocoa
```

### Example: Emulating a Raspberry-Pi Android image
```bash
# Emulating specific Raspberry Pi 4 hardware
qemu-system-aarch64 \
  -M raspi4 \
  -cpu cortex-a72 \
  -m 4096 \
  -accel hvf \
  -kernel .../raspi4-boot.bin \
  -sd lineages-pi4.img \
  -append "root=/dev/mmcblk0p2 rw console=tty1" \
  -serial stdio \
  -display cocoa
```

### Example: Running Android in Parallels
*Create a Custom VM → Import the AVD .img → Start* (no CLI needed).

---

### Summary

- QEMU (directly or via UTM) is the only hypervisor on Apple Silicon that can truly run *any* Android image, including x86 and Raspberry-Pi-specific builds.
- If you only need the official ARM64 Android images that Android Studio provides, the built-in Android Emulator (which itself is a thin QEMU front-end) gives you the best performance and the smoothest developer experience.
- Parallels Desktop (and the VMware Tech-Preview) give you a polished macOS-style UI for ARM64 Android but cannot handle x86 or Pi-specific images.

---

## Assignments

!!! note "Assignment 1: Emulation vs. Virtualization"
    Install **UTM** (free). Attempt to boot a lightweight **x86_64 Linux ISO** (e.g., Alpine Linux). Once booted, install a native **ARM64 ISO** of the same distribution. Compare the boot speed and responsiveness. Note how the "Emulation" setting in UTM corresponds to QEMU's TCG.

!!! note "Assignment 2: Raspberry Pi Emulation"
    Using UTM or the QEMU CLI, configure a VM with the `raspi4` machine type. Attempt to boot a Raspberry Pi OS image. Verify that you can access the shell and run a basic `uname -a` command to confirm the architecture.

!!! note "Assignment 3: Android Architecture Audit"
    Create an Android Virtual Device (AVD) in Android Studio. Use the `adb shell getprop ro.product.cpu.abi` command to verify if the running device is `arm64-v8a` or `x86_64`. Based on the result, determine if your emulator is using HVF or TCG.

---

!!! info "Self-Assessment"
    Test your knowledge by expanding the questions below.

    ??? question "Which hypervisor is the only one capable of running x86_64 guests on an ARM-based Mac?"
        **QEMU** (and its front-ends like UTM). It uses software translation (TCG) to emulate the x86_64 instruction set on ARM hardware.

    ??? question "What is the primary difference between TCG and HVF in QEMU?"
        **TCG (Tiny Code Generator)** is a software emulator that translates instructions from one architecture to another (slow). **HVF (Hypervisor.framework)** is a hardware-assisted virtualization layer that allows a guest of the same architecture to run at near-native speed (fast).

    ??? question "Why can't Parallels Desktop run an official Raspberry Pi image?"
        Parallels relies on hardware-assisted virtualization, which requires the guest to be a generic ARM64 architecture. Raspberry Pi images rely on specific **Broadcom SoC peripherals** (board emulation), which Parallels does not provide. QEMU provides this specific board emulation.

    ??? question "If you need maximum performance for an ARM64 Linux VM on an M2 Mac, which tool should you choose?"
        **Parallels Desktop** or **VMware Fusion**, as they are highly optimized for the Apple Hypervisor.framework and offer near-native performance.

    ??? question "What is the performance penalty for running x86_64 workloads on Apple Silicon via QEMU?"
        Raw CPU speed is typically only **5-20% of native** performance because every x86 instruction must be translated to an ARM instruction via software.

    ??? question "How do you launch an Android Virtual Device (AVD) from the command line?"
        You use the emulator tool located in the Android SDK:
        `~/Library/Android/sdk/emulator/emulator -avd <name>`
