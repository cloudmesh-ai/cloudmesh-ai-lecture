# Oct 15 Lecture: Containerization, Orchestration, and Cloud Integration

## Learning Objectives

!!! info "Learning Objectives"
    - Understand the difference between basic process isolation and cluster orchestration.
    - Compare container runtimes including Docker, Podman, and Apptainer.
    - Explain the core tenets of Kubernetes and OpenShift for managing scalable clusters.
    - Identify how containerized workloads are integrated with OpenStack and academic clouds like Chameleon and Jetstream.

## Overview

Containers provide a pathway from basic process isolation to large-scale cluster orchestration and integration with cloud infrastructure. By isolating applications and dependencies, tools like Docker, Podman, and Apptainer ensure consistency across different environments. For larger scales, orchestration platforms like Kubernetes and OpenShift automate scheduling, scaling, and self-healing. Finally, integrating these containers with virtualized infrastructure, such as OpenStack, bridges the gap between VMs and containerized workloads.

## Core Sections

### Container Foundations

Container foundations focus on isolation, image layers, and various container runtimes.

- **[Core Container Philosophy](/section/container/foundations/containers.md)**: Introduction to the conceptual underpinnings of containerization.
- **[Docker](/section/container/foundations/docker.md)**: The industry standard for building and running containers.
- **[Podman](/section/container/foundations/podman.md)**: A daemonless alternative to Docker, focusing on security and rootless containers.
- **[Podman vs Docker](/section/container/foundations/podman-and-co.md)**: A comparative analysis of the two most popular container engines.
- **[Apptainer](/section/container/foundations/apptainer.md)**: Containerization specifically designed for High-Performance Computing (HPC) and scientific workloads.
- **[Container Tool Comparison](/section/container/container-tool-comparison.md)**: A high-level overview of when to use which container technology.
- **[Container Security](/section/container/security/container-security.md)**: Hardening containers and preventing breakouts.
- **[AI Workloads in Containers](/section/container/specialized/ai-containers.md)**: Handling GPU passthrough and CUDA in containerized environments.
- **[Container Storage and Networking](/section/container/specialized/container-storage-networking.md)**: Understanding CNI, CSI, and persistent volumes.

### Container Orchestration

Moving from single containers to scalable, resilient clusters requires orchestration.

- **[Kubernetes Introduction](/section/container/orchestration/kubernetes.md)**: Foundations of the most widely used orchestration platform.
- **[Kubernetes Local Deployment](/section/container/orchestration/kubernetes-local.md)**: Setting up a local cluster for development and testing.
- **[HPA Autoscaling](/section/container/kubernetes-advanced/hpa-autoscaling.md)**: Dynamically scaling pods based on CPU and memory utilization.
- **[RPS Autoscaling](/section/container/kubernetes-advanced/rps-autoscaling.md)**: Advanced scaling based on requests per second.
- **[Helm](/section/container/specialized/helm.md)**: Using the "package manager for Kubernetes" to manage complex applications.
- **[OpenShift](/section/container/orchestration/openshift.md)**: Enterprise-grade Kubernetes with additional security and developer tooling.
- **[Orchestration Comparison](/section/container/orchestration/orchestration-comparison.md)**: Evaluating different orchestration strategies and platforms.

### Cloud Integration

Containers are often deployed on top of cloud platforms.

- **[OpenStack Foundations](/section/cloud/openstack/openstack.md)**: Understanding the underlying cloud infrastructure.
- **[OpenStack and Containers](/section/container/openstack/openstack-containers.md)**: How to run containerized workloads on OpenStack.
- **[Containers on Chameleon](/section/container/openstack/openstack-chameleon-containers.md)**: Practical implementation on the Chameleon cloud.
- **[Containers on Jetstream](/section/container/openstack/openstack-jetstream-container.md)**: Practical implementation on the Jetstream cloud.

## Summary Checklist

- [ ] Difference between Docker and Podman understood.
- [ ] Purpose of Apptainer in HPC identified.
- [ ] Core functions of Kubernetes (scheduling, scaling, self-healing) explained.
- [ ] Role of Helm in Kubernetes application management described.
- [ ] Integration points between containers and OpenStack identified.

## Assignments

!!! note "Practical Exercises"
    - Compare the installation and initial setup of Docker and Podman on a local machine.
    - Deploy a simple application to a local Kubernetes cluster and implement a basic HPA policy.
    - Research and document the process of deploying a container on an OpenStack-based cloud.

## References

- Internal documentation links are integrated into the Core Sections.

## Self-Evaluation

??? note "What is the main difference between Docker and Podman?"
Podman is daemonless and supports rootless containers by default, whereas Docker relies on a central daemon process.

??? note "Why is Apptainer preferred over Docker in HPC environments?"
Apptainer is designed for scientific workloads and HPC, focusing on security and better integration with shared file systems and job schedulers.

??? note "What is the role of a Kubernetes HPA?"
The Horizontal Pod Autoscaler (HPA) automatically increases or decreases the number of pods in a deployment based on observed CPU utilization or other specified metrics.
