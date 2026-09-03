# Virtual Machine Management with virsh

!!! note "Learning Outcome"
    By the end of this section, you will be able to:
    * Use the `virsh` command-line tool to connect to a hypervisor.
    * Monitor the state of guest virtual machines.
    * Perform essential management tasks such as starting, stopping, and editing VM configurations.


`virsh` is the command-line interface tool for managing guest virtual machines and the hypervisor. It acts as a frontend for `libvirt`, which is the API that manages the virtualization platform (such as KVM, QEMU, or Xen).

## Connecting to a Hypervisor

To initiate a session with a hypervisor, use the `connect` command:

```bash
virsh connect <name>
```

Where `<name>` is the machine name or URI of the hypervisor. For example, to connect to the local hypervisor, you can use `qemu:///system`.

If you want to initiate a read-only connection to avoid making accidental changes, add the `-readonly` flag:

```bash
virsh connect <name> -readonly
```

## Monitoring Guests

To display a list of guest virtual machines and their current states:

```bash
virsh list [ --inactive | --all ]
```

*   **`--inactive`**: Lists only the domains that have been defined but are not currently running.
*   **`--all`**: Lists all domains, regardless of whether they are active or inactive.

## Common Management Commands

Here are the most frequently used `virsh` commands for managing the lifecycle of a VM:

| Action | Command | Description |
| :--- | :--- | :--- |
| **Start** | `virsh start <vm_name>` | Boots a defined but inactive guest. |
| **Shutdown** | `virsh shutdown <vm_name>` | Sends a graceful shutdown signal to the guest OS. |
| **Destroy** | `virsh destroy <vm_name>` | Forcefully stops a guest (equivalent to pulling the power plug). |
| **Edit** | `virsh edit <vm_name>` | Opens the VM configuration XML in the default text editor. |
| **Info** | `virsh dominfo <vm_name>` | Displays detailed information about the guest. |
| **Console** | `virsh console <vm_name>` | Connects to the guest's serial console. |

## Resources

*   **Manual Page**: The official `virsh` man page provides a comprehensive list of all available options: [man virsh](https://linux.die.net/man/1/virsh)
*   **Libvirt Documentation**: For a deeper understanding of how the hypervisor is managed: [libvirt.org](https://libvirt.org/)
