# Student Project: Multi-Cloud OpenStack Networking with a Site-to-Site VPN

!!! warning
    this is not the complete project, but an idea

    technically you could use AI services and clusters hosted in the cloud they are expensive however, so using openstack is a good abstration

    a related questions could this already be achieved with kubernetes where some stuff is on one cloud while other is on another.

## 1. Project Overview

This project explores how two independent OpenStack cloud environments can be connected using a secure, software-defined site-to-site VPN.

The goal is to create a small multi-cloud infrastructure in which virtual machines (VMs) running in two separate OpenStack clouds can communicate over private IP addresses, even though the clouds are located in different IP domains.

Each cloud will contain:

- A public/external network
- A private/internal network
- Multiple ordinary VMs and/or GPU VMs
- A dedicated VPN VM
- OpenStack networking components managed through Neutron
- An Ansible-based deployment and configuration process

The NVIDIA GPUs in the project are intentionally **independent**. The project does not attempt to combine GPUs using NVLink, NVSwitch, or another hardware interconnect. Instead, the purpose is to provide ordinary IP connectivity between independent GPU-enabled VMs.

---

## 2. Project Motivation

Modern computing environments increasingly use multiple cloud or data-center environments. Organizations may have separate OpenStack installations for different departments, locations, experiments, or infrastructure providers.

A challenge appears when workloads in one cloud need to communicate with workloads in another cloud.

For example:

- A GPU workload may run in Cloud A.
- Another GPU workload may run in Cloud B.
- Application services may exist in both environments.
- Databases or storage services may need controlled cross-site access.
- Administrators may need secure management connectivity.

One possible solution is to establish a site-to-site VPN between the two cloud environments.

This project demonstrates how that can be accomplished using:

- OpenStack
- OpenStack Neutron
- Linux virtual machines
- WireGuard
- Private IP routing
- Ansible

---

## 3. Project Scenario

The project assumes two separate OpenStack clouds.

### Cloud A

Cloud A has:

- A public/external network
- A private network such as `10.10.0.0/16`
- A public IP such as `147.126.224.94`
- A dedicated VPN VM
- Multiple workload VMs
- One or more NVIDIA GPU VMs

### Cloud B

Cloud B has:

- A public/external network
- A private network using `172.29.0.0/16`
- A public IP assigned to the VPN VM
- A dedicated VPN VM
- Multiple workload VMs
- One or more NVIDIA GPU VMs

The private networks are intentionally different:

```text
Cloud A: 10.10.0.0/16
Cloud B: 172.29.0.0/16
```

Using non-overlapping private address spaces allows the two environments to be routed together without address ambiguity.

> Note: `147.126.224.94` is treated in this project as an example public endpoint associated with Cloud A. A real deployment should verify ownership, routing, firewall policy, and authorization before using any public address.

---

## 4. High-Level Architecture

The resulting architecture is:

```text
                         INTERNET / WAN
                    │                   │
             Public IP A          Public IP B
                    │                   │
             ┌──────┴──────┐     ┌─────┴──────┐
             │   VPN VM A  │     │  VPN VM B  │
             │  WireGuard  │═════│  WireGuard │
             └──────┬──────┘     └─────┬──────┘
                    │                   │
              Cloud A LAN          Cloud B LAN
              10.10.0.0/16         172.29.0.0/16
                    │                   │
          ┌─────────┼────────┐   ┌──────┼─────────┐
          │         │        │   │      │         │
        VM-A1     VM-A2    GPU-A VM-B1 VM-B2    GPU-B
```

The VPN VMs provide the boundary between the public Internet and the private cloud networks.

The workload VMs do not need to run VPN software.

---

## 5. Core Design Principle

The most important design decision is that the VPN is implemented as a **site-to-site routed connection**, rather than as a separate VPN connection on every workload VM.

The intended traffic flow is:

```text
GPU-A
10.10.3.10
    |
    v
Cloud A routing
    |
    v
VPN VM A
10.10.0.5
    |
    | WireGuard tunnel
    |
VPN VM B
172.29.0.5
    |
    v
Cloud B routing
    |
    v
GPU-B
172.29.3.10
```

This allows many VMs to use the same VPN.

For example:

```text
Cloud A                         Cloud B

10.10.1.0/24  <==============>  172.29.1.0/24
10.10.2.0/24  <==============>  172.29.2.0/24
10.10.3.0/24  <==============>  172.29.3.0/24
```

The exact subnets can be adjusted for the laboratory environment.

---

## 6. Why Use Dedicated VPN VMs?

The VPN endpoints will run on dedicated virtual machines.

Each VPN VM will have at least two network interfaces.

### VPN VM A

```text
NIC 1:
  External/public network
  Public IP: 147.126.224.94

NIC 2:
  Internal network
  Private IP: 10.10.0.5
```

### VPN VM B

```text
NIC 1:
  External/public network
  Public IP: <Cloud B public IP>

NIC 2:
  Internal network
  Private IP: 172.29.0.5
```

The VPN VMs will run WireGuard.

This design has several advantages:

1. Workload VMs do not need VPN configuration.
2. GPU VMs remain focused on compute workloads.
3. Routing is centralized.
4. Security rules are easier to manage.
5. Additional VMs can use the VPN without installing VPN software.
6. The architecture resembles a real site-to-site cloud network.

---

## 7. WireGuard

WireGuard will be used as the VPN technology.

WireGuard provides an encrypted Layer-3 tunnel between the two VPN VMs.

Conceptually:

```text
Cloud A VPN VM
10.10.0.5
      |
      | encrypted WireGuard tunnel
      |
Cloud B VPN VM
172.29.0.5
```

The public interfaces establish the tunnel, while the private interfaces provide access to the internal OpenStack networks.

Example WireGuard addressing could be:

```text
WireGuard network:
10.255.0.0/30

VPN A:
10.255.0.1

VPN B:
10.255.0.2
```

The WireGuard peers would advertise the opposite private cloud network.

Conceptually:

```text
VPN A:
AllowedIPs = 172.29.0.0/16

VPN B:
AllowedIPs = 10.10.0.0/16
```

The exact configuration should be generated by Ansible rather than manually maintained.

---

## 8. Routing

Routing is the key part of the project.

Cloud A must know that the Cloud B private network is reachable through VPN VM A:

```text
172.29.0.0/16
       |
       v
10.10.0.5
```

Cloud B must know that the Cloud A private network is reachable through VPN VM B:

```text
10.10.0.0/16
       |
       v
172.29.0.5
```

The VPN VMs must also enable IPv4 forwarding.

Conceptually:

```text
Cloud A:

10.10.0.0/16
      |
      | route
      v
VPN-A
      |
      | WireGuard
      v
VPN-B
      |
      | route
      v
172.29.0.0/16
```

---

## 9. OpenStack Networking

The project uses OpenStack Neutron for networking.

Each cloud should have an external network and one or more private networks.

A simplified Cloud A topology is:

```text
External Network
       |
       |
   Neutron Router
       |
       |
Private Network
10.10.0.0/16
       |
  ┌────┼───────────────┐
  |    |               |
 VM-A1 VM-A2          VPN-A
```

Cloud B is similar:

```text
External Network
       |
       |
   Neutron Router
       |
       |
Private Network
172.29.0.0/16
       |
  ┌────┼───────────────┐
  |    |               |
 VM-B1 VM-B2          VPN-B
```

Depending on the OpenStack environment, routing can be implemented using Neutron routers, subnet host routes, or another supported routing design.

---

## 10. Security Groups

Security groups should restrict access to the minimum required traffic.

The VPN VMs need to accept WireGuard traffic on their public interfaces.

For example:

```text
UDP 51820
Source: VPN peer public IP
Destination: VPN VM
```

The private interfaces should allow the required traffic between the workload networks.

During initial testing, ICMP can be allowed:

```text
ICMP
Cloud A private network <-> Cloud B private network
```

SSH should not automatically be opened to the entire Internet.

A better design is:

```text
SSH:
  management network only

WireGuard:
  UDP 51820
  peer public IP only

Application traffic:
  explicitly permitted ports

GPU/workload traffic:
  only between required hosts or subnets
```

---

## 11. Independent NVIDIA GPUs

The GPUs in this project are independent.

For example:

```text
GPU VM A
----------------
NVIDIA GPU
CUDA
10.10.3.10


GPU VM B
----------------
NVIDIA GPU
CUDA
172.29.3.10
```

The project does **not** attempt to create:

```text
GPU A <---- NVLink ----> GPU B
```

because a conventional IP VPN does not extend NVLink or NVSwitch.

Instead, the architecture provides:

```text
GPU VM A
     |
     | normal IP networking
     |
  WireGuard
     |
     | normal IP networking
     |
GPU VM B
```

This allows software that supports distributed execution over IP networking to communicate between the machines.

Performance will depend on:

- WAN bandwidth
- latency
- packet loss
- MTU
- CPU overhead
- VPN overhead
- OpenStack networking
- GPU workload characteristics

The VPN should therefore be considered a connectivity mechanism, not a replacement for local high-performance GPU interconnects.

---

## 12. Example Multi-VM Environment

A more realistic student laboratory could contain:

### Cloud A

```text
VPN-A       10.10.0.5
App-A1      10.10.1.10
App-A2      10.10.1.11
DB-A        10.10.2.10
GPU-A1      10.10.3.10
GPU-A2      10.10.3.11
```

### Cloud B

```text
VPN-B       172.29.0.5
App-B1      172.29.1.10
App-B2      172.29.1.11
DB-B        172.29.2.10
GPU-B1      172.29.3.10
GPU-B2      172.29.3.11
```

The desired connectivity could be:

```text
App-A1  <-> App-B1
DB-A    <-> DB-B
GPU-A1  <-> GPU-B1
GPU-A2  <-> GPU-B2
```

while management networks remain isolated.

---

## 13. Ansible Automation

A major objective of the project is to make the entire environment reproducible with Ansible.

Instead of manually creating VMs, networks, routes, security groups, and WireGuard configuration, Ansible should perform the deployment.

A proposed repository structure is:

```text
openstack-multicloud-vpn/
|
├── ansible.cfg
├── requirements.yml
├── README.md
|
├── inventory/
│   └── hosts.yml
|
├── group_vars/
│   ├── all.yml
│   ├── cloud_a.yml
│   └── cloud_b.yml
|
├── playbooks/
│   ├── site.yml
│   ├── network.yml
│   ├── vpn_vms.yml
│   ├── wireguard.yml
│   └── test.yml
|
└── roles/
    ├── openstack_network/
    ├── vpn_vm/
    └── wireguard/
```

The final project should be deployable with a command similar to:

```bash
ansible-playbook playbooks/site.yml
```

---

## 14. OpenStack Credentials

The Ansible deployment should use OpenStack authentication information through a secure mechanism such as `clouds.yaml`, environment variables, or Ansible Vault.

Credentials must not be committed to Git.

For example:

```text
Cloud A:
  cloud name = cloud_a

Cloud B:
  cloud name = cloud_b
```

The project should use placeholder values in documentation and source control.

Secrets should be represented as:

```text
REDACTED
```

rather than stored in the repository.

---

## 15. Suggested Ansible Workflow

The deployment can be divided into several stages.

### Stage 1: Requirements

Install the required Ansible collections.

For example:

```text
openstack.cloud
```

and any Linux/WireGuard-related collections required by the implementation.

### Stage 2: OpenStack Networks

Create or verify:

- External network
- Private network
- Subnets
- Neutron routers
- Router interfaces
- Security groups

### Stage 3: VPN VMs

Create:

```text
VPN-A
VPN-B
```

Each VM receives:

- Public interface
- Private interface
- Appropriate security groups
- Static/private addressing where appropriate

### Stage 4: Operating System Configuration

Configure:

- IP forwarding
- Firewall
- WireGuard package
- WireGuard interface
- Persistent configuration

### Stage 5: VPN Configuration

Generate WireGuard keys and peer configuration.

The public keys can be exchanged through Ansible variables.

Private keys should be protected using Ansible Vault or another secret-management mechanism.

### Stage 6: Routing

Configure:

```text
Cloud A -> 172.29.0.0/16 -> VPN-A
Cloud B -> 10.10.0.0/16 -> VPN-B
```

### Stage 7: Testing

Verify connectivity between selected VMs.

For example:

```bash
ping 172.29.3.10
```

from GPU-A, and:

```bash
ping 10.10.3.10
```

from GPU-B.

---

## 16. Testing Plan

The project should have measurable tests.

### Test 1: VPN Reachability

Verify that the two WireGuard endpoints can communicate.

Expected result:

```text
VPN-A <-> VPN-B
```

### Test 2: Private Network Routing

From a VM in Cloud A:

```bash
ping 172.29.1.10
```

Expected result:

```text
successful
```

### Test 3: Reverse Routing

From Cloud B:

```bash
ping 10.10.1.10
```

Expected result:

```text
successful
```

### Test 4: SSH

Verify that authorized VMs can connect using their private IP addresses.

Example:

```bash
ssh user@172.29.1.10
```

### Test 5: GPU Connectivity

Verify that the GPU VMs can communicate:

```bash
ping 172.29.3.10
```

Then test the actual distributed software selected for the project.

### Test 6: Isolation

Verify that blocked networks remain inaccessible.

For example:

```text
Cloud A management network
        X
Cloud B management network
```

---

## 17. Performance Measurements

Because the VPN adds an additional networking layer, the project should measure its impact.

Useful measurements include:

### Latency

```bash
ping <remote-private-ip>
```

Compare:

```text
local VM-to-VM latency
```

against:

```text
cross-cloud VPN latency
```

### Bandwidth

Use a controlled test tool such as `iperf3`.

Measure:

```text
VM-A -> VM-B
VM-B -> VM-A
```

### Packet Loss

Measure packet loss under normal and high traffic conditions.

### GPU Workload Performance

If a distributed GPU application is used, compare:

```text
single-GPU performance
```

with:

```text
multi-VM distributed performance
```

The objective is not necessarily to achieve local-NVLink performance, but to understand the cost of cross-cloud networking.

---

## 18. Security Considerations

This project intentionally places VPN endpoints on public networks.

Therefore:

1. Only the required WireGuard UDP port should be exposed.
2. SSH should be restricted.
3. VPN private keys must remain secret.
4. OpenStack credentials must not be committed to Git.
5. Ansible Vault should be considered for secrets.
6. Security groups should implement least privilege.
7. Internal services should not be exposed directly to the Internet.
8. Public IP addresses should only be used for the VPN tunnel and approved management functions.

The public address `147.126.224.94` should only be used if the student has authorization to operate infrastructure using that address.

---

## 19. Learning Objectives

By completing this project, a student should gain practical experience with:

### OpenStack

- Projects
- Networks
- Subnets
- Neutron routers
- Security groups
- Floating/public IPs
- VM provisioning

### Linux Networking

- Routing
- IP forwarding
- Firewalling
- Network interfaces
- Private versus public addressing

### VPN Technology

- WireGuard
- Public/private keys
- Site-to-site VPNs
- Encrypted tunnels
- Allowed IPs
- Routing through VPN interfaces

### Automation

- Ansible
- Ansible roles
- Inventory
- Variables
- Idempotent infrastructure deployment
- OpenStack automation

### GPU Computing

- NVIDIA GPU VMs
- CUDA environments
- Independent GPU workloads
- Distributed application networking
- Limitations of IP networking compared with NVLink

---

## 20. Proposed Deliverables

The completed student project should produce:

1. **Architecture diagram**
2. **Ansible repository**
3. **OpenStack network configuration**
4. **Two VPN VM configurations**
5. **WireGuard configuration**
6. **Security-group configuration**
7. **Routing configuration**
8. **Automated deployment playbook**
9. **Automated connectivity tests**
10. **Performance measurements**
11. **Security analysis**
12. **Final project report**

The final repository should allow another student to reproduce the environment with their own authorized OpenStack credentials.

---

## 21. Possible Extensions

Once the basic system works, several extensions could be explored.

### Extension A: More Than Two Clouds

Add a third OpenStack environment:

```text
             Cloud A
                |
                |
             Cloud B
                |
                |
             Cloud C
```

This could become a small multi-site network.

### Extension B: Selective Routing

!!! warning
    this is a mus
Instead of connecting every subnet:

```text
10.10.0.0/16 <-> 172.29.0.0/16
```

allow only:

```text
10.10.3.0/24 <-> 172.29.3.0/24
```

This demonstrates network segmentation.

### Extension C: High Availability

Deploy two VPN VMs per cloud:

```text
Cloud A                  Cloud B

VPN-A1 ═══════════════ VPN-B1
VPN-A2 ═══════════════ VPN-B2
```

This introduces redundancy and failover.

### Extension D: Monitoring

Add monitoring for:

- VPN status
- VM availability
- bandwidth
- latency
- packet loss
- CPU utilization
- GPU utilization

### Extension E: Distributed GPU Applications

Run a distributed application across independent GPU VMs and investigate how latency and bandwidth affect performance.

---

## 22. Expected Final Architecture

The final architecture should resemble:

```text
                              PUBLIC INTERNET
                         │                     │
                  147.126.224.94          Public IP B
                         │                     │
                  ┌──────┴──────┐       ┌──────┴──────┐
                  │   VPN VM A  │       │   VPN VM B  │
                  │  WireGuard  │═══════│  WireGuard  │
                  │ 10.10.0.5   │       │ 172.29.0.5  │
                  └──────┬──────┘       └──────┬──────┘
                         │                     │
                ┌────────┴────────┐   ┌────────┴────────┐
                │  Cloud A LAN    │   │  Cloud B LAN    │
                │ 10.10.0.0/16   │   │ 172.29.0.0/16  │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
              ┌──────────┼─────────┐   ┌───────┼──────────┐
              │          │         │   │       │          │
            VM-A1      VM-A2    GPU-A VM-B1   VM-B2     GPU-B
```

The central idea is:

> **Use dedicated VPN VMs to create a secure routed connection between two independent OpenStack private networks, while allowing multiple ordinary and GPU-enabled VMs to communicate across the clouds without installing VPN software on every workload VM.**

---

## 23. Conclusion

This project demonstrates a practical multi-cloud networking architecture using two independent OpenStack environments.

The project separates responsibilities into three layers:

```text
OpenStack
    ↓
Provides VMs and networks

WireGuard VPN
    ↓
Connects the private networks securely

Applications / GPU workloads
    ↓
Use normal private IP connectivity
```

The NVIDIA GPUs remain independent compute resources. The VPN does not attempt to combine them into a single GPU or emulate an NVLink connection.

The main engineering challenge is instead **secure, automated, routed connectivity between the two OpenStack environments**.

Ansible provides the automation layer that makes the infrastructure reproducible, testable, and suitable for a student project.

A successful implementation should demonstrate that a VM in Cloud A can communicate with an authorized VM in Cloud B using private IP addresses, while public IP addresses are used only for establishing the encrypted VPN connection and approved management access.
