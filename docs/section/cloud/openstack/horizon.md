---
title: "Managing the Cloud: The OpenStack Horizon Dashboard"
---

# The OpenStack Horizon Dashboard

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this section, participants will be able to:

    - Navigate the Horizon dashboard interface.
    - Provision and manage virtual machines, networks, and storage volumes via the GUI.
    - Manage project-level identity, roles, and quotas.
    - Use Horizon to troubleshoot instance status and monitor resource utilization.

## Overview

The **Horizon Dashboard** is the web-based graphical user interface (GUI) for OpenStack. While power users and automation scripts rely on the CLI and APIs, Horizon provides a critical visual entry point for administrators and users to manage their cloud resources without needing to master complex command-line syntax. It serves as a central orchestration layer that abstracts the underlying complexity of the OpenStack ecosystem into a series of intuitive menus and forms.

## Core Sections

### Architecture and Interface Overview

Horizon does not manage cloud resources directly; instead, it acts as a sophisticated client for the OpenStack APIs. When a user performs an action in the dashboard, Horizon makes a series of authenticated requests to the corresponding service API.

#### The Role of Identity (Keystone)

Every interaction in Horizon begins with authentication via the **Keystone** identity service. Upon login, Horizon retrieves the user's available projects (tenants) and roles. Because OpenStack is designed for multi-tenancy, the dashboard dynamically adjusts its available options based on the active project context.

- **Project-Based Isolation**: Resources like virtual machines and networks are bound to a project. Horizon ensures that users only see and manage resources they have the authority to access.
- **Role-Based Access Control (RBAC)**: Depending on whether a user is assigned the `member` or `admin` role, Horizon unlocks different tabs, such as the global Administration panel.

#### Navigation and Layout

The Horizon interface is organized into functional areas that mirror the underlying service architecture.

- **Project Tab**: This is the operational heart of the dashboard. It provides a project-centric view where users can instantiate resources, manage network topology, and monitor volume health.
- **Administration Tab**: Accessible only to cloud operators, this area provides tools for managing the physical infrastructure, such as hypervisor status, global quota limits, and the creation of new projects and users.
- **Identity/Account**: A personal management area where users can rotate their API passwords, upload SSH public keys for VM access, and review their project memberships.

### Deep Dive: Resource Management

#### Compute Orchestration (Nova)

The **Compute** section is the primary interface for managing the lifecycle of virtual instances.

- **Instance Provisioning**: The "Launch Instance" wizard guides users through selecting a source image, a flavor, and a network. This process triggers Nova to coordinate with Neutron for networking and Cinder for boot volumes.
- **Flavor Management**: Flavors define the virtual hardware (vCPU, RAM, Disk). Horizon allows users to quickly compare flavors to match the resource requirements of their application.
- **Console Access**: Horizon provides integrated VNC and Spice consoles. This allows administrators to troubleshoot "boot-looping" instances or perform initial OS configuration when SSH access is not yet available.
- **Lifecycle Operations**: Beyond launching, Horizon simplifies complex operations such as resizing an instance (changing its flavor) or migrating a VM to a different physical compute node for maintenance.

#### Software-Defined Networking (Neutron)

The **Network** section provides a visual representation of the virtual data center's connectivity.

- **The Network Hierarchy**: Horizon helps users manage the relationship between virtual networks (the L2 broadcast domain) and subnets (the L3 IP address range).
- **Security Groups as Virtual Firewalls**: Security groups are stateful firewalls that operate at the port level. Horizon allows users to define ingress and egress rules, ensuring that only authorized traffic (e.g., TCP 80 for HTTP) reaches the instance.
- **Floating IPs and External Access**: Since instances typically live on private networks, Horizon provides the interface to allocate "Floating IPs" from a public pool and associate them with a private IP. This creates a 1:1 NAT mapping that allows the instance to be reachable from the internet.
- **Router Management**: Users can create virtual routers to connect different subnets or link a private network to the external "provider" network.

#### Storage and Image Services (Cinder & Glance)

Horizon integrates block storage and image management to ensure data persistence and rapid deployment.

- **Glance (Image Service)**: The Image section allows users to upload custom OS disk images or create snapshots of existing instances. These images act as the gold templates for all new VM deployments.
- **Cinder (Block Storage)**: Unlike the ephemeral disk that comes with a VM, Cinder volumes are persistent. Horizon allows users to create these volumes independently and attach them to one or more instances, ensuring data survives even if the instance is deleted.
- **Volume Snapshots**: Users can take point-in-time snapshots of their volumes via the GUI, providing a critical safety net for database updates or system changes.

### The Horizon Workflow: Deploying a Production-Ready VM

Launching a functional VM requires more than just clicking "Launch". A production-ready workflow in Horizon follows this logical sequence:

1. **Network Preparation**: Create a dedicated network and subnet. Define a Security Group that allows SSH (port 22) and the specific application ports required.
2. **Image Selection**: Choose a hardened OS image from the Glance catalog.
3. **Resource Sizing**: Select a flavor that provides sufficient vCPU and RAM for the intended workload.
4. **Secure Access Configuration**: Upload an SSH public key to the account. During launch, this key is injected into the instance's `authorized_keys` file, eliminating the need for insecure passwords.
5. **Provisioning**: Initiate the launch. Horizon monitors the status from `BUILD` to `ACTIVE`.
6. **External Connectivity**: Allocate a Floating IP from the pool and associate it with the new instance to enable remote management.

### Strategic Comparison: Horizon vs. CLI

Choosing between the GUI and the CLI depends on the scale and nature of the task.

| Feature | Horizon (GUI) | OpenStack CLI / SDK |
| :--- | :--- | :--- |
| **Learning Curve** | Low - Visual and intuitive | Higher - Requires syntax knowledge |
| **Speed of Single Action** | Fast for one-off tasks | Slower (typing commands) |
| **Repeatability** | Low - Manual clicking | High - Scripts and templates |
| **Scalability** | Limited to one-by-one | High - Bulk operations via loops |
| **Complex Layouts** | Difficult to visualize | Easy to define via Heat templates |
| **Auditability** | Low - Actions are not logged | High - Scripts can be version-controlled |

!!! tip "The Hybrid Approach"
    Most cloud operators use **Horizon** for quick sanity checks, monitoring, and initial exploration, but switch to the **CLI** or **Heat templates** for any task that needs to be repeated or documented as "Infrastructure as Code."

## Summary Checklist

- [ ] Navigate the Horizon dashboard interface.
- [ ] Provision a virtual machine using the GUI.
- [ ] Configure security groups to control network traffic.
- [ ] Allocate and associate a Floating IP with an instance.
- [ ] Create and attach a Cinder volume for persistent storage.

## Assignments

!!! note "Assignment.1: Launching your first instance"
    Using the Horizon dashboard, launch a small Linux instance. Ensure you select a valid image, flavor, and network, and inject a public SSH key for access.

??? tip "Solution: Launching your first instance"
    1. Navigate to **Compute $\rightarrow$ Instances** $\rightarrow$ **Launch Instance**.
    2. In the **Source** tab, select a trusted image (e.g., Cirros or Ubuntu).
    3. In the **Flavor** tab, select a small flavor (e.g., m1.tiny).
    4. In the **Networks** tab, select the default project network.
    5. In the **Key Pair** tab, select your uploaded key pair.
    6. Click **Launch Instance**.

!!! note "Assignment.2: Configuring Network Security"
    Create a new security group named `web-server` and add a rule to allow ingress traffic on TCP port 80 (HTTP) and port 22 (SSH) from any IP address.

??? tip "Solution: Configuring Network Security"
    1. Navigate to **Network $\rightarrow$ Security Groups**.
    2. Click **Create Security Group**, name it `web-server`, and save.
    3. Select the `web-server` group and click **Manage Rules**.
    4. Add a rule: Protocol `TCP`, Port `22`, Remote IP `0.0.0.0/0`.
    5. Add a rule: Protocol `TCP`, Port `80`, Remote IP `0.0.0.0/0`.

!!! note "Assignment.3: Managing Persistent Storage"
    Create a 1GB volume in Cinder and attach it to a running instance.

??? tip "Solution: Managing Persistent Storage"
    1. Navigate to **Volumes $\rightarrow$ Volumes**.
    2. Click **Create Volume**, set size to `1 GB`, and save.
    3. Once the volume status is `available`, click **Manage Volume** $\rightarrow$ **Attach to Server**.
    4. Select the target instance and click **Attach Volume**.

## References

- OpenStack Horizon User Guide: [docs.openstack.org/horizon](https://docs.openstack.org/horizon)
- OpenStack API Reference: [docs.openstack.org/api-ref](https://docs.openstack.org/api-ref)

## Self-Evaluation

??? note "What is the primary purpose of the Horizon dashboard?"
    Horizon provides a web-based graphical interface that simplifies the management of OpenStack resources by aggregating multiple API services (Nova, Neutron, etc.) into a single user-friendly portal.

??? note "How does Horizon handle security for instance access?"
    Horizon allows users to create and manage Security Groups (via Neutron) to define firewall rules and facilitates the injection of SSH keypairs during the instance launch process.

??? note "In which menu would you go to associate a public Floating IP with a private instance?"
    You would navigate to the **Network $\rightarrow$ Floating IPs** section to allocate an IP and then associate it with the desired instance.
