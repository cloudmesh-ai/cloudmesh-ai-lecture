---
title: "Managing the Cloud: The OpenStack Horizon Dashboard"
---

# The OpenStack Horizon Dashboard

The **Horizon Dashboard** is the web-based graphical user interface (GUI) for OpenStack. While power users and automation scripts rely on the CLI and APIs, Horizon provides a critical visual entry point for administrators and users to manage their cloud resources without needing to master complex command-line syntax.

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this section, participants will be able to:
    - Navigate the Horizon dashboard interface.
    - Provision and manage virtual machines, networks, and storage volumes via the GUI.
    - Manage project-level identity, roles, and quotas.
    - Use Horizon to troubleshoot instance status and monitor resource utilization.

## 1. Overview of the Horizon Interface

Horizon acts as a unified front-end that communicates with the various OpenStack APIs (Nova, Neutron, Cinder, Glance, etc.). Instead of making separate API calls to different services, Horizon aggregates this data into a single, cohesive web experience.

### Key Navigation Areas

*   **Project Tab**: The primary workspace for users. This is where you create instances, manage security groups, and configure networks.
*   **Administration Tab**: Reserved for cloud operators. It allows for the management of hypervisors, global quotas, and identity providers.
*   **Identity/Account**: Where users manage their own passwords, keys, and project memberships.

## 2. Core Resource Management

### Managing Compute Instances (Nova)
Through the **Compute $\rightarrow$ Instances** menu, users can:
- **Launch Instance**: Select an image from Glance, a flavor (size) from Nova, and a network from Neutron.
- **Console Access**: Access the VNC or Spice console to interact with the VM's operating system directly from the browser.
- **Lifecycle Actions**: Start, stop, reboot, or migrate instances across physical hosts.

### Networking and Security (Neutron)
The **Network** section allows for the visual design of the virtual data center:
- **Networks & Subnets**: Create isolated virtual networks and define IP address ranges.
- **Security Groups**: Define firewall rules (ingress/egress) to control traffic to and from instances.
- **Floating IPs**: Associate a public-facing IP address with a private instance to enable external access.

### Volume and Image Management (Cinder & Glance)
- **Volumes**: Create persistent block storage and attach/detach them to running instances.
- **Images**: Upload custom OS images or manage snapshots of existing instances for rapid cloning.

## 3. The Horizon Workflow: Launching a VM

The typical workflow in Horizon follows a specific sequence to ensure the instance has all necessary dependencies:

1.  **Network Selection**: Ensure a network exists (or create one) and define a security group.
2.  **Image Selection**: Choose a pre-configured image (e.g., Ubuntu 22.04).
3.  **Flavor Selection**: Choose the amount of vCPU and RAM required.
4.  **Keypair Injection**: Upload an SSH public key to ensure secure access after boot.
5.  **Launch**: Initiate the request; Nova coordinates with Neutron and Cinder to provision the resources.

## 4. Horizon vs. CLI: When to use which?

| Feature | Horizon (GUI) | OpenStack CLI / SDK |
| :--- | :--- | :--- |
| **Learning Curve** | Low - Visual and intuitive | Higher - Requires syntax knowledge |
| **Speed of Single Action** | Fast for one-off tasks | Slower (typing commands) |
| **Repeatability** | Low - Manual clicking | High - Scripts and templates |
| **Scalability** | Limited to one-by-one | High - Bulk operations via loops |
| **Complex Layouts** | Difficult to visualize | Easy to define via Heat templates |

!!! tip "The Hybrid Approach"
    Most professional cloud operators use **Horizon** for quick sanity checks, monitoring, and initial exploration, but switch to the **CLI** or **Heat templates** for any task that needs to be repeated or documented as "Infrastructure as Code."

## Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

    ??? question "What is the primary purpose of the Horizon dashboard?"
        Horizon provides a web-based graphical interface that simplifies the management of OpenStack resources by aggregating multiple API services (Nova, Neutron, etc.) into a single user-friendly portal.

    ??? question "How does Horizon handle security for instance access?"
        Horizon allows users to create and manage Security Groups (via Neutron) to define firewall rules and facilitates the injection of SSH keypairs during the instance launch process.

    ??? question "In which menu would you go to associate a public Floating IP with a private instance?"
        You would navigate to the **Network $\rightarrow$ Floating IPs** section to allocate an IP and then associate it with the desired instance.
