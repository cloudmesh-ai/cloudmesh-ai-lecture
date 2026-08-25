# Virtualization {#sec:virtualization}


!!! note "Learning Outcome"
    * Gain a fundamental understanding of virtualization concepts.
    * Define and distinguish between different types of Virtual Machines (VMs).
    * Understand the role and types of Hypervisors.

---

Virtualization is a cornerstone technology that enabled the cloud revolution. It provides the underlying principles for the development and adoption of cloud computing by allowing physical hardware to be partitioned into multiple virtual resources. While the concept is not new, modern virtualization has led to significantly better utilization of server resources in data centers and on local desktops.

Virtualization enables the execution of multiple isolated environments on a single piece of physical hardware, making it appear as if each application or operating system is running on its own independent computer.

Examples of the usefulness of virtualization include testing applications and running experiments on an operating system different from the one on the host computer. To enable this, we use virtual machines.

## Virtual Machines

A **Virtual Machine (VM)** is a software-based emulation of a computer system. VMs allow for the execution of an entire operating system (including the kernel) on top of another operating system or directly on the hardware. Multiple VMs share the physical resources of the host system.

We distinguish between two primary types of virtual machines:

### 1. System Virtual Machines (Hardware VMs)

System VMs provide a complete emulation of the underlying hardware, allowing a full "guest" operating system to run. The hypervisor abstracts the physical CPU, memory, and I/O devices.

*   **Examples**: Oracle VirtualBox, VMware Workstation, Microsoft Hyper-V.

### 2. Process Virtual Machines (Application VMs)

Process VMs provide a platform-independent environment designed to execute a single program. They abstract the underlying hardware and OS to ensure the application runs identically regardless of the host platform.

*   **Examples**: Java Virtual Machine (JVM), .NET Common Language Runtime (CLR).

#### Contrast: Wine (Wine is not an emulator)

The next software that we introduce is not a hypervisor. However, it is very interesting as a contrast to the other approach.

The term Wine has been originally introduced as an acronym for *Wine Is Not an Emulator*. In contrast to the other approaches, Wine introduces a compatibility layer that allows running Windows applications on a number of POSIX-compliant operating systems. This includes Linux, macOS and BSD. In contrast to using a virtual machine or emulator, Wine translates Windows API calls into POSIX calls [@www-wine]. Hence, it allows us to pass the Windows API calls directly to operating system calls leading to good performance [@www-wine]. The disadvantage of this approach is that in the early days and still today, some of the underlying calls may not be ported yet and may lead to applications not running.

---

## System Virtualization and Hypervisors

System virtualization is the primary engine behind Infrastructure-as-a-Service (IaaS). The software layer that creates and runs virtual machines is called the **Virtual Machine Monitor (VMM)** or, more commonly, the **Hypervisor**.

!!! info "Virtual Machine Monitor (VMM)" 
    The **Virtual Machine Monitor (VMM)** is the software layer that abstracts physical hardware to create and manage virtual machines; this layer is more commonly referred to as the **Hypervisor**.

There are two primary architectures for hypervisors:

### Type 1: Bare-Metal Hypervisors

A Type 1 hypervisor is installed directly on the physical hardware. It has direct access to the CPU, memory, and I/O devices, which results in high performance and stability.

*   **Role**: It acts as the operating system for the hardware, managing the guest VMs.
*   **Examples**: 
    *   **VMware ESXi**: Widely used in enterprise data centers for server consolidation.
    *   **Microsoft Hyper-V**: Integrated into Windows Server and used extensively in Azure cloud.
    *   **Xen**: An open-source hypervisor used by many early cloud providers (including AWS in its early stages).

### Type 2: Hosted Hypervisors

A Type 2 hypervisor runs as an application on top of a conventional operating system (the "Host OS"). The host OS manages the hardware, and the hypervisor requests resources from the host OS.

*   **Role**: It is easier to install and use for development and testing on a personal computer.
*   **Examples**: 
    *   **Oracle VirtualBox**: A free and open-source hypervisor popular for local development and cross-platform testing.
    *   **VMware Workstation**: A professional-grade hosted hypervisor used by developers and IT professionals.
    *   **QEMU**: A generic and open-source machine emulator and virtualizer often used in combination with KVM.
### Comparison of Hypervisor Types

The following table summarizes the key differences, advantages, and disadvantages of Type 1 and Type 2 hypervisors.

| Feature | Type 1 (Bare-Metal) | Type 2 (Hosted) |
| :--- | :--- | :--- |
| **Installation** | Directly on hardware | On top of a Host OS |
| **Performance** | High (near-native) | Lower (overhead from Host OS) |
| **Efficiency** | Very high (direct resource access) | Moderate (resources managed by Host OS) |
| **Stability** | Higher (less software layers) | Lower (depends on Host OS stability) |
| **Ease of Setup** | Complex (requires dedicated hardware) | Simple (installed like any application) |
| **Typical Use Case** | Production servers, Enterprise Cloud | Development, Testing, Personal use |
| **Advantages** | $\bullet$ Maximum performance $\bullet$ Scalability $\bullet$ Robust security | $\bullet$ Easy installation $\bullet$ Better hardware compatibility $\bullet$ Familiar interface |
| **Disadvantages** | $\bullet$ Steeper learning curve $\bullet$ Restricted hardware support | $\bullet$ Performance overhead $\bullet$ Dependence on Host OS |


### Virtualization Architecture

The following diagram illustrates the architecture of a hosted hypervisor (Type 2), where multiple virtual machines run on top of a hypervisor, which in turn runs on a host operating system.


#### Type 2 (Hosted) Virtualization

<div style="font-family: sans-serif; border: 2px solid #333; border-radius: 6px; padding: 15px; width: 550px; background: #fff; margin: auto;">
  <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 12px;">Virtual machines</div>
  
  <!-- VMs Row -->
  <div style="display: flex; justify-content: space-between; border: 2px solid #333; border-radius: 4px; padding: 10px; margin-bottom: 10px;">
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">VM1</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Guest OS</div>
    </div>
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">VM2</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Guest OS</div>
    </div>
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">VM3</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Guest OS</div>
    </div>
  </div>

  <!-- Hypervisor -->
  <div style="background: #d5e8d4; border: 2px solid #82b366; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
    Hypervisor
  </div>

  <!-- Host OS -->
  <div style="background: #dae8fc; border: 2px solid #6c8ebf; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
    Host operating system
  </div>

  <!-- Host Hardware -->
  <div style="background: #ffe6cc; border: 2px solid #d79b00; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; font-size: 14px;">
    Host hardware
  </div>
</div>

</br>
Figure: Type 2 (Hosted) Virtualization
</br>

#### Type 1 (Bare-metal) Virtualization


<div style="font-family: sans-serif; border: 2px solid #333; border-radius: 6px; padding: 15px; width: 550px; background: #fff; margin: auto;">
  <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 12px;">Virtual machines</div>
  
  <!-- VMs Row -->
  <div style="display: flex; justify-content: space-between; border: 2px solid #333; border-radius: 4px; padding: 10px; margin-bottom: 10px;">
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">VM1</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Guest OS</div>
    </div>
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">VM2</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Guest OS</div>
    </div>
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">VM3</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Guest OS</div>
    </div>
  </div>

  <!-- Hypervisor -->
  <div style="background: #d5e8d4; border: 2px solid #82b366; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
    Hypervisor
  </div>


  <!-- Host Hardware -->
  <div style="background: #ffe6cc; border: 2px solid #d79b00; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; font-size: 14px;">
    Host hardware
  </div>
</div>
</br>

Figure: Type 1 (Bare-metal) Virtualization


In either case, the functionality a virtual machine is supported
through configuration files, specifications, and access to the
physical resources either directly or indirectly through the host
OS. A virtual machine provides the same functionality as a physical
computer, but with the advantage that through virtualization they are
portable, can be managed, and provide increased security while
shielding the underlying OS from harmful actions. As a virtual
machine is in principle a program, it consists of several files
, including a configuration file, virtual disk files, virtual RAM, and a
log file. Virtual machines are configured to run a virtual operating
system that allows applications to run on them. Each virtual machine
has its own copy of the OS, making it independent and more secure.

End-users and developers will benefit from using virtual machines in
the case they need to operate or support on different hardware or porting
software on it.


### Container

<div style="font-family: sans-serif; border: 2px solid #333; border-radius: 6px; padding: 15px; width: 550px; background: #fff; margin: auto;">
  <div style="text-align: center; font-weight: bold; font-size: 16px; margin-bottom: 12px;">Containers</div>
  
  <!-- Containers Row -->
  <div style="display: flex; justify-content: space-between; border: 2px solid #333; border-radius: 4px; padding: 10px; margin-bottom: 10px;">
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">Container 1</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Bins/Libs</div>
    </div>
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">Container 2</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Bins/Libs</div>
    </div>
    <div style="border: 1px solid #333; padding: 8px; width: 30%; text-align: center; border-radius: 4px;">
      <div style="font-weight: bold; font-size: 12px; margin-bottom: 4px;">Container 3</div>
      <div style="background: #d5e8d4; border: 1px solid #82b366; padding: 6px; margin-bottom: 4px; border-radius: 3px; font-size: 13px;">App</div>
      <div style="background: #dae8fc; border: 1px solid #6c8ebf; padding: 6px; border-radius: 3px; font-size: 13px;">Bins/Libs</div>
    </div>
  </div>

  <!-- Docker Engine -->
  <div style="background: #d5e8d4; border: 2px solid #82b366; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
    Docker Engine
  </div>

  <!-- Host OS -->
  <div style="background: #dae8fc; border: 2px solid #6c8ebf; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; margin-bottom: 10px; font-size: 14px;">
    Host OS
  </div>

  <!-- Host Hardware -->
  <div style="background: #ffe6cc; border: 2px solid #d79b00; padding: 10px; text-align: center; font-weight: bold; border-radius: 4px; font-size: 14px;">
    Host hardware
  </div>
</div>


## Hosted Virtualization

In hosted virtualization, the guest operating system accesses the underlying hardware through the host OS; consequently, it usually has limited access to the hardware as defined by the host OS. This allows the host
OS to impose policies that govern the operation of multiple guest OS
concurrently. This includes management and scheduling of processes,
memory, I/O operations to assign them appropriately to the guest
OS. Through this mechanism, the hypervisor provides an emulation of
available hardware to each Virtual Machine running on top of it in
time-sharing fashion for resource-constrained or resource shared
activities.

For example, the hypervisor can present generic I/O devices but may not have access to non-generic I/O devices. Generic I/O devices include network interface cards and CD-ROMs. Examples of non-generic I/O devices include PCI data acquisition cards. However,
with appropriate driver support, even such devices could be made
accessible to the VMs.

Often we also find that hosted virtualization supports connected USB
drives in the VMs which become very practical for USB attached
devices needed in storage, or even edge computing applications.


Advantages of Hosted Virtualization include

* Multiple Operating systems run on separate virtual machines on a VMM.
* Different Operating systems run on separate virtual machines on a VMM.
* Hardware-level driver support is controlled by VMM, allowing an
  isolation of certain security aspects for accessing the hardware.
* Installation of software can be done by the owner of the virtual
  machine and does not have to be conducted by the provider of the
  hypervisor.

Disadvantages of Hosted Virtualization include


* Increased resource requirements as the Guest OS is running a full
  copy of the OS. In its worst case, this will lead to a significant performance reduction while using resources that are in contention.
* The user of hypervisors must be familiar with the operating system
   management and security to ensure it is safe to use.

## Summary

To showcase how these technologies relate to each other you may
review @fig:vm-taxonomy


![Virtualization Taxonomy [@paravsfull-virt]](images/vm.png){#fig:vm-taxonomy}

We summarize the following *hypervisor* types:

* Type-1 hypervisors supporting native or bare-metal. They run
  directly on the host's hardware to control the hardware and to
  manage guest operating systems.

* Type-2 hypervisors supporting hosted virtualization. They run on a
  conventional operating system (OS), just as other computer programs
  do. A guest operating system runs as a process on the host.

## Virtualization Approaches

Next, we look at different virtualization approaches that relate to
resource utilization.

### Full virtualization

When looking at virtualization, we often identify it with being full
virtualization. The hypervisor provides a full abstraction of the
hardware exposed to the guest OSs. In this case, the guest OSs the
virtual machine just run without any special modification on the host
OS. It just looks like an independent running computer
[@paravsfull-virt].

### Paravirtualization

Para -- alongside/partial -- virtualization is developed to improve
performance by interacting between the OS and the hypervisor. This is
done for complex and time-consuming tasks that otherwise could not be
managed by the VMM manager. Commands sent from the OS to the
hypervisor are called *hypercalls* [@paravsfull-virt].

## Virtualization Technologies

In this section, we cover an introduction to the underlying virtualization
technologies used on some mainstream platforms.

Cloud providers, such as AWS, Azure, and Google, and OpenStack use for
example, QEMU and KVM technologies for compute instance virtualization.

### Selected Hardware Virtualization Technologies

### AMD-V and Intel-VT

The hardware virtualization support enabled by AMD-V and Intel VT
technologies introduces virtualization in the x86 processor
architecture. According to Intel, Intel Hyper-Threading Technology
allows a single processor to execute two or more separate threads
concurrently. When it is enabled, multi-threaded software applications
can execute their threads in parallel, thereby improving their
performance.

### I/O MMU virtualization (AMD-Vi and Intel VT-d)

The term IOMMU is an abbreviation for input-output memory management
unit. An IOMMU allows through virtual addresses to interface with
physical addresses, allowing external direct-memory-access–capable IO
devices to interface with the main memory [@iommu-1]. AMD's I/O
Virtualization Technology (AMD-Vi) was originally called *IOMMU*.

To use Intel's *Virtualization Technology for Directed I/O* (VT-d),
both the motherboard chipset and system firmware (BIOS or UEFI) need
to fully support the IOMMU I/O virtualization functionality for it to
be usable [@iommu-2].



### Selected VM Virtualization Software and Tools

A number of noteworthy virtualization software and tools exist which
make the development and use of virtualization on the hardware
possible. They include

* Libvirt
* KVM
* Xen
* Hyper-V
* QEMU
* VMWare
* VirtualBox

We will be discussing them next.


#### Libvirt

[Libvirt](<https://libvirt.org/api.html>) is a library with an API
for managing virtualization solutions such as provided by KVM and
Xen. It provides a common management API for them, allowing uniform,
cross-hypervisor interfaces for higher-level management
tools. `Libvirt` provides a toolkit to manage virtualization hosts and
supports a wide set of languages, such as C, Python, Perl, and Java.
Drivers are the basic building block for libvirt functionality to
support the capability to handle specific hypervisor driver
calls. Drivers are discovered and registered during connection
processing as part of the `virInitializeAPI`.  Each driver has a
registration API that loads up the driver-specific function
references for the libvirt APIs to call.  The following is a
simplistic view of the hypervisor driver mechanism.  Furthermore, it
provides APIs for management of virtual networks and storage on the VM
Host Server. The configuration of each VM Guest is stored in an XML
file [@libvirt]. The official website for `libvirt` is located at

* <https://libvirt.org/>



#### QEMU

QEMU is a virtualization technology emulator that allows you to run
operating systems and Linux distributions on your current system
without installing them or burn their ISO files.  When used as a
machine emulator, QEMU can run OSs and programs made for one machine
(e.g., an ARM board) on a different machine (e.g., your own PC). By
using dynamic translation, it achieves very good performance.  QEMU
provides two generic functions.  One of them is an open-source machine
emulator, and the other is a virtualizer.

* *Machine emulation:* using it as a machine emulator it runs the OSs
  and programs designed for one machine on a different machine of potentially different architecture. It uses dynamic translation
  through which it achieves very good performance.

* *Virtualizer:* Using is as a virtualizer it executes the guest code
  directly on the host CPU. This enables QEMU to achieve near-native
  performance.

Once QEMU has been installed, it should be ready to run a guest OS
from a disk image. This image is a file that represents the filesystem
and OS on a hard disk. From the perspective of the guest OS, it
actually is a file on harddisk, and it can create its own filesystem
on the virtual disk.

QEMU supports either XEN or KVM to enable virtualization. With the
help of KVM, QEMU can virtualize x86, server, and embedded PowerPC,
64-bit POWER, S390, 32-bit and 64-bit ARM, and MIPS guests according
to the [QEMU Wiki](https://wiki.qemu.org/Main_Page).

Useful links include the following:

* An extensive manual is provided at
  <https://qemu.weilnetz.de/doc/qemu-doc.html>.

* QEMU can be downloaded from <http://www.qemu.org/download/>.

* A collection of images for testing purposes is provided at
  <https://wiki.qemu.org/Testing/System_Images>

An example of using QEMU is provided in Section
[Virtual Machine Management with QEMU]{@s-qemu-kvm}


#### KVM

KVM, or Kernel-based Virtual Machine is a popular open-source
hypervisor solution. It was released as a virtualization solution
for Linux based systems and later was merged into Linux Kernel
since version 2.6.20. It was originally supporting x86 hardware
with virtualization extensions (Intel VT or AMD-V), but later
supporting of PowerPC and ARM were added. It supports a variety
of different guest OSs, e.g., Windows family, Darwin (the core
of MacOS), in addition to the different distros from various Linux
operating systems. The full supported guest list can be found at:
<http://www.linux-kvm.org/page/Guest_Support_Status>

The full list of KVM features can be found here:
<http://www.linux-kvm.org/page/KVM_Features>.
Among them, some cool features include hot-plugging of hardware
, even CPU and PCI devices. It supports live migration of VMs too.

##### KVM vs QEMU

KVM includes a fork of the QEMU executable. The QEMU project focuses
on hardware emulation and portability. KVM focus on the kernel module
and interfacing with the rest of the userspace code.  KVM comes with a
`kvm-qemu` executable that just like QEMU manages the resources while
allocating RAM, loading the code. However, instead of recompiling the
code, it spawns a thread which calls the KVM kernel module to switch to
guest mode.  It then proceeds to execute the VM code. When privileged
instructions are found, it switches back to the KVM kernel module, and
if necessary, signals the QEMU thread to handle most of the hardware
emulation. This means that the guest code is emulated in a POSIX
thread, which can be managed with common Linux tools [@kvmvsqemu].

#### Xen

Xen is one of the most widely adopted hypervisors by IaaS cloud. It is
supported by the earliest and still the most popular public cloud
offering, i.e., Amazon Web Service (AWS). Eucalyptus, one open-source
effort to replicate what AWS had to offer, and the then most popular
private cloud software, supported Xen from the start. And later, Openstack,
the most popular open-source IaaS cloud software at present, also
supports Xen.

Some notable features of Xen include:

* Supporting x86-64 and ARM for host architecture.

* Supporting live migration of VMs between different physical hosts
without losing availability.

A more detailed list can be found at
<https://wiki.xenproject.org/wiki/Xen_Project_Release_Features>.


#### Hyper-V

Hyper-V is a product from Microsoft to support virtualization on
systems running Windows. Hyper-V was originally released along with
Windows Server 2008, with a separate free version with limited
functionality. In later releases, it adds more features, e.g., better
support of Linux guest OS, live migration of VMs, etc.

Hyper-V is still getting a lot of popularity comparing to XEN and KVM
which we attribute to the increasing presence of Microsoft's Azure cloud
offering.

![Popularity of KVM, Xen, and Hyper-V according to Google Trends [Source](https://trends.google.com/trends/?geo=US)](images/kvm-xen-hyperv-gtrends.png){#fig:hypervisor-gtrends}

However, overall, the search popularity of hypervisors have been
decreasing, as other lightweight virtualization solutions, i.e.,
container technologies become more main stream. We will cover them
in a later chapter.

More detailed information about Hyper-V can be found at
<https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/reference/hyper-v-architecture>

#### VMWare

VMware is well known for the company bringing hypervisors to the mass
market. The company is now owned by Dell. It has developed the first
type 2 hypervisor. Today VMWare offer type 1 hypervisors and type 2
hypervisors [@wikipedia-vmware].

Because the initial software virtualized "hardware for a video
adapter, a network adapter, and hard disk adapters" as well as
"pass-through drivers for guest USB, serial, and parallel devices"
[@wikipedia-vmware] it provided an attractive solution for many to use
it to run different OSs on their host computers.  One important
advantage is that it does not rely on virtualization extensions to the
x86 instruction set as it was developed before they became
available. This means it can run on many other platforms. However this
advantage is diminished with the ubiquitous availability of these
features in the hardware.

### Parallels

Another interesting company offering hypervisors is Parallels. This
company has two main products in that regards:

* Parallels Desktop for Mac, which for x86 machines allows users to
  run virtual machines independently using Windows, Linux, Solaris.

* Parallels Workstation for Microsoft Windows and Linux users which
  for x86 machines allows user to run virtual machines independently
  on the Windows host.

#### VirtualBox

VirtualBox is a free, open-source hypervisor for x86 architectures. It
is now owned by Oracle while transitioning from SUN which in turn
acquired the original technology from Innotek.

One of the nice features for us is that VirtualBox is able to create
and manage guest virtual machines such as Windows, Linux, BSD, OSx86
and even in part also macOS (on Apple hardware). Hence it makes it for
us a very valuable tool while being able to run virtual machines on a
local desktop or computer to simulate cloud resources without
charging cost. In addition, we find command-line tools such as Vagrant
 that make the use convenient while not having to
utilize the GUI or the more complex virtual box command interfaces. A
guest additions package allows compatibility with the host OS, to, for
example, allow window management between host and guest OS.

In Section [VirtualBox](../local/virtualbox.md) we have provided a practical
introduction to VirtualBox.

## Practical Virtualization

In practice, we often use hosted hypervisors to simulate cloud resources on a local desktop without incurring costs. 

### VirtualBox and Automation
One of the most common tools for this is **Oracle VirtualBox**. To make the use of VirtualBox more convenient and reproducible, we find command-line tools such as **Vagrant**, which allow us to define and launch virtual machines using a simple configuration configuration file instead of utilizing the GUI or complex command interfaces.

To improve the interaction between the host and the guest, a **guest additions package** is typically installed. This allows for features like shared folders, shared clipboards, and better window management between the host and guest OS.

In Section [VirtualBox](../local/virtualbox.md) we have provided a practical introduction to VirtualBox.

---

## Technical Nuances and Advanced Comparisons

### QEMU, KVM, and Xen
Beyond the basic types, there are specialized implementations. **QEMU** and **KVM** are better integrated into Linux and have a smaller footprint, which may result in better performance. **VirtualBox** is targeted as general virtualization software and is limited to x86 and amd64 architectures. 

**Xen** uses QEMU to allow hardware virtualization; however, Xen can also use paravirtualization [@diff-qemu]. 

### Full vs. Paravirtualization
In the following table, we summarize support for full- and paravirtualization across popular technologies.

|     | XEN | KVM | VirtualBox | VMware |
| --- | ---: | ---: | ---: | ---: |
| Paravirtualization | Yes | Yes (via virtio) | Yes | Yes |
| Full virtualization | Yes | Yes | Yes | Yes |

---

## Beyond Compute Virtualization

Virtualization is not limited to the CPU and Operating System. The same principle of abstracting physical hardware into logical resources applies to other infrastructure components.

### Storage Virtualization
Storage virtualization allows the system to integrate the logical view of the physical storage resources into a single pool of storage. Users are unaware that their data is not hosted on a single physical disk. This is achieved across various layers: Storage devices, the Block aggregation layer, the File/record layer, and the Application layer. 

A good example of cloud-based virtual storage is **Google Drive**, as well as services like **Dropbox, AWS S3, and Azure Blob Storage**.

### Network Virtualization
Network virtualization combines hardware and software network resources into a single, software-defined administrative unit called a **virtual network**. 

We distinguish between:
*   **External network virtualization**: Combines many physical networks into a unifying logical network.
*   **Internal network virtualization**: Provides network functionality to the processes and containers running on a single server.

Note that we will not cover this topic in this introductory class. However, students can contribute a section or chapter.
