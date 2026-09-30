# OpenStack and Containers

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Explain the core OpenStack architecture, distinguishing between the control plane and the data plane.
    - Analyze the technical trade-offs between running containers on virtual machines versus using native OpenStack container services.
    - Differentiate between Container-as-a-Service (Zun) and Container-Orchestration-as-a-Service (Magnum).
    - Evaluate how Kuryr optimizes container networking by bypassing traditional overlays in favor of native Neutron ports.
    - Outline the workflow of provisioning a managed Kubernetes cluster via Magnum.
    - Execute basic container lifecycle operations using the Zun CLI.
    - Design a basic security and quota strategy for containerized workloads in a multi-tenant environment.

## Overview

OpenStack provides a unified control plane that allows operators to manage both virtual machines (VMs) and containers. While VMs offer strong isolation and full OS control, containers provide speed, density, and portability. By integrating container services like Magnum and Zun with the existing OpenStack networking (Neutron) and identity (Keystone) fabrics, organizations can achieve enterprise-grade governance for cloud-native workloads.

## Core Sections

### OpenStack Architecture Foundations

OpenStack is an open-source Infrastructure-as-a-Service (IaaS) that transforms physical hardware into programmable virtual resources. Its architecture is split into two primary components:

- **Control Plane**: APIs and managers (such as Keystone, Glance, and Nova-API) that orchestrate resource allocation and decide what happens in the cloud.
- **Data Plane**: The physical and virtual resources (KVM hypervisors, OVS switches, Cinder volumes) where the actual workloads reside and execute.

The core services include Nova (compute), Neutron (network), Cinder (block storage), Swift (object storage), Glance (image service), and Keystone (identity).

### Evolution of Workloads

The transition from monolithic applications to microservices has shifted infrastructure requirements:

- **Legacy Era**: Monolithic applications were typically deployed on bare metal or VMs, which are characterized by slower boot times and higher resource overhead.
- **Cloud-Native Era**: Microservices are deployed in containers, offering fast boot times, a shared kernel, and high portability.

The goal for many organizations is to maintain the isolation and governance of a cloud environment while leveraging the speed and density of containers, leading to hybrid environments where VMs and containers run side-by-side.

### Running Containers on OpenStack

Deploying containers on OpenStack offers several technical and business advantages:

- **Resource Density**: Sharing a kernel reduces RAM and CPU overhead compared to VMs, lowering infrastructure costs.
- **Rapid Scaling**: Containers start in seconds, improving responsiveness to traffic spikes.
- **Governance**: Existing Keystone RBAC and Neutron security groups provide consistent security policies.
- **Unified Fabric**: Kuryr allows containers to have first-class IP addresses, simplifying networking and auditing.
- **Infrastructure-as-Code**: Tools like Heat and Terraform can automate the provisioning of both the cluster and the application.

### Container Strategy Decision

When choosing a container strategy on OpenStack, there are three primary paths:

1. **The DIY Path**: Deploying a VM, installing an operating system, and manually installing Kubernetes or Docker. This offers total control but introduces high operational overhead.
2. **The Managed Path (OpenStack Magnum)**: Using Magnum for one-click clusters and integrated lifecycle management. This reduces overhead but offers less control over master node configuration.
3. **The Serverless Path (OpenStack Zun)**: Using Zun for "just run my image" functionality without managing VMs. This is ideal for simple apps but does not support complex orchestration.

### OpenStack Magnum: Container Orchestration as a Service (COaaS)

Magnum provides managed container orchestration. Instead of running the orchestration engine itself, Magnum provisions and manages the infrastructure required to run it.

#### Provisioning Workflow

1. **Cluster Template**: Define a blueprint including the OS image, flavor, Kubernetes version, and network.
2. **Cluster**: Instantiate the blueprint by specifying the number of nodes.
3. **Access**: Magnum generates a `kubeconfig` file for the user to interact with the cluster.

Under the hood, Magnum leverages **Heat** (OpenStack Orchestration) to launch VM instances, configure networking, and execute installation scripts.

#### Lifecycle and Management

- **Provisioning**: Automated installation of the Container Orchestration Engine (COE).
- **Scaling**: Worker nodes can be added or removed via API calls.
- **Updating**: Rolling updates are used to manage cluster versions.
- **Integration**: **Octavia** (OpenStack Load Balancer) is used to expose Kubernetes services to external networks.

### OpenStack Zun: Container as a Service (CaaS)

Zun provides a serverless container experience, removing the need for users to manage VMs, SSH keys, or kubeconfigs.

#### Architecture and Features

Zun treats containers as first-class resources. The architecture follows this flow:

1. The user interacts with the Zun API (which is Docker-compatible).
2. Zun API authenticates via Keystone.
3. Zun Conductor schedules containers onto Nova compute nodes.
4. The container runtime (Docker, containerd, or CRI-O) runs the image, using Glance as the registry.
5. Neutron provides networking, including ports, security groups, and floating IPs.

#### Use Cases for Zun

- **CI/CD Pipelines**: Spinning up a container for a test suite and destroying it immediately after.
- **Quick Prototyping**: Testing a new image without the overhead of a full cluster.
- **Edge Computing**: Deploying lightweight containers to edge nodes.
- **Task Offloading**: Running heavy data-processing scripts as one-off containers.

#### Zun CLI Example

```bash
# Pull an image into Glance
openstack image create cirros --file cirros-0.5.2-x86_64-disk.img --disk-format qcow2 --container-format bare

# Create and start a container
openstack container create mycirros \
    --image cirros \
    --flavor m1.tiny \
    --net private

openstack container start mycirros

# Exec into container
openstack container exec mycirros hostname
```

### Networking with Kuryr

Standard Kubernetes networking often relies on "overlays" (e.g., VXLAN), which create a network-within-a-network, leading to double-encapsulation and performance degradation.

**Kuryr-Kubernetes** solves this by implementing the Kubernetes CNI plugin using native Neutron ports.

- **Mechanism**: Kuryr maps Kubernetes pods directly to Neutron ports, giving each container a "real" IP from the OpenStack network.
- **Visibility**: Container traffic is visible directly in the Neutron dashboard.
- **Security**: Neutron Security Groups can be applied directly to pods.
- **Performance**: Latency is reduced by removing the overlay layer.

### Security, Isolation, and Operations

Containers in OpenStack inherit the same tenant-level quotas and security frameworks as VMs.

#### Isolation Layers

| Layer | Mechanism |
|-------|-----------|
| **Identity** | Keystone tokens for API calls (Magnum, Zun, Kuryr). |
| **Compute** | Nova flavors, CPU pinning, and PCI-passthrough. |
| **Network** | Neutron security groups and network policies. |
| **Image** | Glance image signatures and Trusted-Registries. |
| **Runtime** | SELinux/AppArmor profiles, or gVisor/Kata for enhanced isolation. |
| **Encryption** | Cinder encrypted volumes and Barbican secrets. |

#### Operational Considerations

- **Quota & Billing**: Limits are set on containers, pods, CPUs, RAM, and volumes.
- **Monitoring**: Implemented via Monasca, Ceilometer, or Prometheus.
- **Logging**: Centralized via ELK or OpenSearch.
- **Backup**: Cinder volume snapshots and etcd exports for Kubernetes.
- **Upgrades**: Magnum supports version upgrades via Heat; Zun upgrades are runtime-based.

### Comparison and Selection

The following table summarizes when to use each service:

| Scenario | Recommended Component |
|----------|----------------------|
| Fully-fledged microservices app (auto-scale, multiple services) | Magnum + Kubernetes |
| Batch job or CI step (run script, then exit) | Zun |
| Per-pod network policies and Neutron security groups | Magnum + Kuryr |
| Legacy app requiring a single container | Zun |
| Exposing containers via floating IP | Zun or Magnum (via LoadBalancer) |

### Future Roadmap

Recent and upcoming developments (2024-2026) focus on:

- **Magnum**: Integration with Cluster-API and GPU-operator support.
- **Zun**: Transitioning to containerd/CRI-O as default runtimes and experimental pod APIs.
- **Kuryr**: Full support for Kubernetes NetworkPolicy and tighter Octavia integration.
- **OpenStack-CNCF Bridge**: Aodh-based autoscaling for Magnum and Barbican-backed secrets for pods.

## Summary Checklist

- [ ] Understand the difference between the OpenStack Control Plane and Data Plane.
- [ ] Compare the resource overhead of VMs versus containers.
- [ ] Identify when to use Magnum (orchestration) versus Zun (individual containers).
- [ ] Explain how Kuryr eliminates network overlays using Neutron ports.
- [ ] Describe the Magnum provisioning workflow: Template $\rightarrow$ Cluster $\rightarrow$ Kubeconfig.
- [ ] Identify the isolation mechanisms provided by Keystone, Neutron, and Nova.

## Assignments

!!! note "Assignment.1: Provision a Kubernetes Cluster"
    Use the OpenStack CLI to create a 2-node Kubernetes cluster using Magnum.
    1. Create a cluster template.
    2. Instantiate a cluster from that template.
    3. Use the generated `kubeconfig` to run `kubectl get nodes`.
    
    ??? tip "Solution: Provisioning"
        Use `openstack coe cluster template create` followed by `openstack coe cluster create`. Once the status is `CREATE_COMPLETE`, run `openstack coe cluster config <cluster_name> > kubeconfig.yaml` and set `export KUBECONFIG=kubeconfig.yaml`.

!!! note "Assignment.2: Serverless Container Execution"
    Deploy a container from the `alpine` image using Zun and execute a simple command to verify it is running.
    
    ??? tip "Solution: Zun Execution"
        Run `openstack container create my-alpine --image alpine` and `openstack container start my-alpine`. Verify with `openstack container exec my-alpine echo "Hello from Zun"`.

!!! note "Assignment.3: Secure Credential Management"
    Create a Zun container that retrieves a secret from Barbican during its execution.
    
    ??? tip "Solution: Barbican Integration"
        Store a secret in Barbican using `openstack secret create`. When creating the Zun container, map the secret to an environment variable or a file within the container.

!!! note "Assignment.4: Infrastructure Automation"
    Write a Heat template that provisions both a Magnum cluster and an Octavia load balancer in a single transaction.
    
    ??? tip "Solution: Heat Orchestration"
        Define an `OS::Magnum::Cluster` resource and an `OS::Octavia::LoadBalancer` resource within the same Heat YAML file, ensuring the load balancer references the cluster's network.

## References

| Resource | Link |
|----------|------|
| OpenStack Magnum Docs | https://docs.openstack.org/magnum/latest/ |
| OpenStack Zun Docs | https://docs.openstack.org/zun/latest/ |
| Kuryr-Kubernetes GitHub | https://github.com/openstack/kuryr-kubernetes |
| Magnum Quick-Start Tutorial | https://docs.openstack.org/magnum/latest/user/quickstart.html |
| Zun CLI Reference | https://docs.openstack.org/python-zunclient/latest/ |
| OpenStack Containers Lab | https://github.com/openstack/openstack-helm/tree/master/containers |

## Self-Evaluation

??? note "Distinguish between the OpenStack Control Plane and the Data Plane."
    The Control Plane consists of APIs and management services (e.g., Keystone, Nova-API) that orchestrate resource allocation. The Data Plane consists of the actual physical and virtual resources (e.g., KVM hypervisors, OVS switches) where workloads execute.

??? note "What is the main difference between OpenStack Zun and OpenStack Magnum?"
    Zun is a Container-as-a-Service (CaaS) that allows users to launch individual containers without managing a cluster. Magnum is a Container-Orchestration-as-a-Service (COaaS) that deploys and manages full orchestration clusters, such as Kubernetes.

??? note "How does Kuryr optimize container networking in an OpenStack environment?"
    Kuryr bridges the gap between the container CNI and OpenStack Neutron. It allows containers to connect directly to Neutron ports, bypassing the traditional overlay networks (like Flannel) to reduce latency and improve visibility.
