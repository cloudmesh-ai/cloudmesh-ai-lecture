# Virtual Machine Management with virsh

!!! info "Learning Objectives"
    - Connect to a hypervisor using the `virsh` command-line interface.
    - Monitor the state and resource utilization of guest virtual machines.
    - Execute lifecycle management tasks including starting, stopping, and destroying VMs.
    - Modify virtual machine configurations using XML definitions.
    - Access the serial console of a guest machine for direct interaction.

In a Linux-based virtualization environment, managing virtual machines (VMs) often requires interacting with the hypervisor. While graphical tools exist, professional system administrators rely on the command line for automation, remote management, and precision.

`virsh` is the primary command-line interface (CLI) tool for managing guest virtual machines. It acts as a frontend for `libvirt`, an open-source API that provides a consistent way to manage different virtualization technologies, such as KVM (Kernel-based Virtual Machine), QEMU, and Xen. By using `libvirt`, `virsh` abstracts the underlying hypervisor complexities, allowing administrators to use the same set of commands regardless of the specific virtualization backend.

## Connecting to the Hypervisor

Before managing VMs, `virsh` must establish a connection to the `libvirtd` daemon. This connection is defined by a URI (Uniform Resource Identifier).

### Understanding Connection URIs

The URI tells `virsh` which hypervisor to talk to and what permission level to use:

- `qemu:///system`: Connects to the system-wide instance of QEMU/KVM. This is the most common URI, as it manages VMs that are available to all users and start automatically on boot.
- `qemu:///session`: Connects to a user-specific instance. VMs created here are only visible to the user who created them.
- `qemu+ssh://user@remote-host/system`: Connects to a remote hypervisor via SSH.

### Establishing a Connection

To connect to the local system hypervisor, use the `connect` command:

```bash
virsh connect qemu:///system
```

If you need to inspect a system without the risk of making accidental changes, you can initiate a read-only connection:

```bash
virsh connect qemu:///system -readonly
```

## Monitoring Guest Virtual Machines

Once connected, the first step is typically to identify which VMs are available and what their current status is.

### Listing Guest VMs

The `list` command provides a snapshot of the current domains (VMs) managed by the hypervisor.

```bash
# List only currently running VMs
virsh list

# List all VMs, including those that are shut down
virsh list --all
```

The output includes the VM ID, name, and state (e.g., `running`, `shut off`, or `paused`).

### Inspecting Detailed Domain Information

To get a comprehensive overview of a specific VM's configuration, such as its CPU allocation, memory usage, and UUID, use the `dominfo` command:

```bash
virsh dominfo <vm_name>
```

This command is essential for verifying if a VM has the correct resources allocated before performing heavy workloads.


## Lifecycle Orchestration

Managing the power state of a VM is a fundamental task. `virsh` provides several ways to change the state of a guest.

### Starting and Stopping VMs

To boot a VM that is currently defined but inactive:

```bash
virsh start <vm_name>
```

To stop a VM, there are two primary methods depending on the required urgency:

1. **Graceful Shutdown**: Sends an ACPI shutdown signal to the guest OS, allowing it to close applications and shut down cleanly.

```bash
virsh shutdown <vm_name>
```

2. **Forced Destruction**: Immediately stops the VM. This is equivalent to pulling the power plug from a physical server and can lead to data corruption if used improperly.

```bash
virsh destroy <vm_name>
```

### Rebooting and Pausing

To restart a guest machine:

```bash
virsh reboot <vm_name>
```

To freeze the execution of a VM (saving its state in memory), use `suspend`, and to wake it up, use `resume`:

```bash
virsh suspend <vm_name>
virsh resume <vm_name>
```

## Configuration Management

Every VM in `libvirt` is defined by an XML configuration file. This file specifies the hardware allocated to the VM, including the disk paths, network interfaces, and memory limits.

### Editing the VM Definition

Instead of manually editing XML files on the filesystem, `virsh` provides an `edit` command that opens the configuration in the system's default text editor (e.g., `vi` or `nano`) and validates the XML before saving.

```bash
virsh edit <vm_name>
```

Common changes made via `edit` include increasing the memory limit or adding a new virtual disk.

### Defining and Undefining VMs

A VM can exist in two states: **active** (running) and **defined** (the XML configuration exists on disk).

- **Define**: To create a VM from an existing XML file:

```bash
virsh define /path/to/vm_config.xml
```

- **Undefine**: To remove the VM's configuration from the hypervisor (this does not delete the virtual disk files):

```bash
virsh undefine <vm_name>
```

## Direct Guest Interaction

When network access to a VM is lost or the VM is failing to boot, you can use the serial console to interact with the guest.

### Accessing the Console

The `console` command connects your terminal directly to the VM's serial port:

```bash
virsh console <vm_name>
```

*Note: For this to work, the guest OS must be configured to send its output to the serial console (e.g., via GRUB configuration in Linux).*

To exit the console and return to the host terminal, press `Ctrl + ]`.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] Successfully connected to the hypervisor using a URI (e.g., `qemu:///system`).
    - [ ] Listed all guests and identified their current states using `virsh list --all`.
    - [ ] Retrieved detailed resource information for a specific VM using `dominfo`.
    - [ ] Performed a graceful `shutdown` and a forced `destroy` of a test VM.
    - [ ] Modified a VM's hardware configuration using `virsh edit`.
    - [ ] Accessed the guest serial console using `virsh console`.

## Practical Exercises

!!! note "Exercise 1: Basic Inspection"
    Connect to your local hypervisor. List all virtual machines, including inactive ones. Select one VM and display its detailed resource information. Note the amount of memory allocated and the current CPU state.

!!! note "Exercise 2: Lifecycle Management"
    Create a test VM (or use an existing one). Perform the following sequence:
    1. Start the VM.
    2. Verify it is running using `virsh list`.
    3. Reboot the VM.
    4. Forcefully stop the VM using `destroy`.
    5. Verify that the state has changed to `shut off`.

!!! note "Exercise 3: Configuration Modification"
    Use `virsh edit` to modify the memory allocation of a VM (e.g., increase it by 512MB). Save the changes and restart the VM. Use `virsh dominfo` to verify that the new memory limit has been applied.

