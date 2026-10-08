# Oct 15 Lecture: Containerization, Orchestration, and Cloud Integration

## Learning Objectives

!!! info "Learning Objectives"
    - Understand the transition from basic process isolation to large-scale cluster orchestration.
    - Compare container runtimes including Docker, Podman, and Apptainer, specifically for HPC and security contexts.
    - Implement and manage scalable clusters using Kubernetes and OpenShift.
    - Secure the container lifecycle from build to deployment using CI/CD pipelines.
    - Integrate containerized workloads with cloud infrastructure and specialized AI cloud services.

## Overview

Containers provide a pathway from basic process isolation to large-scale cluster orchestration and integration with cloud infrastructure. By isolating applications and dependencies, tools like Docker, Podman, and Apptainer ensure consistency across different environments. For larger scales, orchestration platforms like Kubernetes and OpenShift automate scheduling, scaling, and self-healing. To move these workloads into production, they must be secured within CI/CD pipelines and integrated with virtualized infrastructure, such as OpenStack and AI-specialized clouds.

## Core Sections

### Container Foundations

Containerization begins with the concept of isolating an application from its environment. Before selecting a runtime, it is critical to understand how image layers and namespaces create this isolation, ensuring that the software behaves identically regardless of where it is deployed.

- **[Core Container Philosophy](/section/container/foundations/containers.md)**: Introduction to the conceptual underpinnings of containerization and the role of the **Container Registry** as the source of truth for images.
- **[Docker](/section/container/foundations/docker.md)**: The industry standard for building and running containers, including the use of **Docker Compose** to manage multi-container applications on a single host.
- **[Podman](/section/container/foundations/podman.md)**: A daemonless alternative to Docker, focusing on security, rootless containers, and `podman-compose`.
- **[Podman vs Docker](/section/container/foundations/podman-and-co.md)**: A comparative analysis of the two most popular container engines.
- **[Apptainer](/section/container/foundations/apptainer.md)**: Containerization specifically designed for High-Performance Computing (HPC) and scientific workloads.
- **[Container Tool Comparison](/section/container/container-tool-comparison.md)**: A high-level overview of when to use which container technology.

!!! warning "The Privileged Mode Trap"
    Using `--privileged` in Docker or Podman grants the container near-complete access to the host kernel. While useful for debugging, this bypasses almost all security boundaries and should never be used in production.

### Container Security & Lifecycle

A running container is only as secure as the process that built it. Moving from a local prototype to a production deployment requires a shift toward "Shift-Left" security, where vulnerabilities are caught in the CI/CD pipeline before the image ever reaches a cluster.

- **[Container Security](/section/container/security/container-security.md)**: Hardening containers, preventing breakouts, and ensuring image authenticity via signing.
- **[CI/CD Security](/section/container/security/containers-in-pipeline.md)**: Integrating security scanning and hardening into the automated deployment pipeline.
- **[Kubernetes Deployment Pipelines](/section/devops/k8s-pipeline.md)**: Implementing the mechanics of automated delivery to Kubernetes clusters.
- **[AI Workloads in Containers](/section/container/specialized/ai-containers.md)**: Specialized configurations for GPU passthrough and CUDA in containerized environments.
- **[Container Storage and Networking](/section/container/specialized/container-storage-networking.md)**: Understanding CNI, CSI, and persistent volumes for stateful applications.

!!! warning "Root in Container"
    Running processes as `root` inside a container is a common mistake. Even with isolation, a breakout vulnerability can lead to host-level compromise. Always specify a non-root `USER` in your Dockerfile to follow the principle of least privilege.

### Cluster Orchestration

Managing a few containers is straightforward; managing thousands across a distributed cluster is an entirely different problem. Orchestration platforms solve this by automating the "Desired State"—ensuring that if a pod crashes, it is automatically rescheduled and healed.

- **[Kubernetes Introduction](/section/container/orchestration/kubernetes.md)**: Foundations of the most widely used orchestration platform, including the use of **Ingress Controllers** to manage external traffic.
- **[Kubernetes Local Deployment](/section/container/orchestration/kubernetes-local.md)**: Setting up a local cluster for development. This covers lightweight distributions like **k3s (via k3d)**, **Kind**, and **Minikube** for low-resource environments.
- **[HPA Autoscaling](/section/container/kubernetes-advanced/hpa-autoscaling.md)**: Dynamically scaling pods based on CPU and memory utilization.
- **[RPS Autoscaling](/section/container/kubernetes-advanced/rps-autoscaling.md)**: Advanced scaling based on requests per second.
- **[Helm](/section/container/specialized/helm.md)**: Using the "package manager for Kubernetes" to manage complex applications.
- **[OpenShift](/section/container/orchestration/openshift.md)**: Enterprise-grade Kubernetes with additional security and developer tooling.
- **[Orchestration Comparison](/section/container/orchestration/orchestration-comparison.md)**: Evaluating different orchestration strategies and platforms.

!!! warning "The Noisy Neighbor Problem"
    Pods without defined CPU and memory `limits` can consume all available resources on a node, starving other critical services. Always define resource requests and limits in your manifest to ensure cluster stability.

### Cloud & AI Integration

Cloud platforms provide the raw compute and storage (VMs) that support container clusters. Integrating containers with cloud-native services, such as managed databases or AI-specialized GPU instances, allows applications to scale beyond the limits of a single cluster.

- **[OpenStack Foundations](/section/cloud/openstack/openstack.md)**: Understanding the underlying cloud infrastructure.
- **[OpenStack and Containers](/section/container/openstack/openstack-containers.md)**: How to run containerized workloads on OpenStack.
- **[Containers on Chameleon](/section/container/openstack/openstack-chameleon-containers.md)**: Practical implementation on the Chameleon cloud.
- **[Containers on Jetstream](/section/container/openstack/openstack-jetstream-container.md)**: Practical implementation on the Jetstream cloud.
- **[AI in Cloud](/section/cloud/topics/ai.md)**: Utilizing cloud-native services for AI and machine learning workloads.

!!! warning "The Firewall Wall"
    A common point of failure in cloud deployments is the Security Group. Even if your container is running correctly, it will be unreachable if the cloud infrastructure firewall is not explicitly configured to allow traffic on the required ports.

## Summary Checklist

- [ ] Can successfully run a rootless container in Podman without using `sudo`.
- [ ] Can define a multi-container application using Docker Compose or Podman Compose.
- [ ] Can identify and fix a security vulnerability in a Dockerfile using a scanning tool.
- [ ] Can deploy a multi-container application using a Helm chart.
- [ ] Can implement a Horizontal Pod Autoscaler (HPA) that responds to a simulated load.
- [ ] Can deploy a container to an OpenStack-based cloud and verify external connectivity.
- [ ] Can configure a container to utilize cloud-native AI infrastructure (e.g., GPU passthrough).

## Assignments

!!! note "Practical Exercises"
    - **Assignment 1: Rootless Comparison**. Install both Docker and Podman. Demonstrate the ability to run a container as a non-root user in Podman and contrast it with the Docker daemon requirement.
    - **Assignment 2: Dynamic Scaling**. Deploy a sample application to a local Kubernetes cluster. Implement a Horizontal Pod Autoscaler (HPA) and use a load-testing tool to trigger a scaling event.
    - **Assignment 3: Cloud Deployment**. Deploy a containerized application to an OpenStack-based cloud (e.g., Chameleon or Jetstream) and verify connectivity.
    - **Capstone Project: [Kubernetes Grid](/lecture/assignments/project/kubernetes-grid.md)**: Implement a high-availability grid of services across a Kubernetes cluster.

    ??? tip "Solution: Assignment 2"
        To implement HPA, ensure your deployment has resource requests defined in the YAML. Use `kubectl autoscale deployment <name> --cpu-percent=50 --min=1 --max=10`. Use `fortio` or `hey` to generate HTTP traffic and monitor pods via `kubectl get pods -w`.

## References

- Internal documentation links are integrated into the Core Sections.

## Self-Evaluation

??? note "What is the main difference between Docker and Podman?"
Podman is daemonless and supports rootless containers by default, whereas Docker relies on a central daemon process that typically requires root privileges.

??? note "Why is Apptainer preferred over Docker in HPC environments?"
Apptainer is designed for scientific workloads and HPC, focusing on security (avoiding root privileges) and better integration with shared file systems and job schedulers like Slurm.

??? note "What is the role of a Kubernetes HPA?"
The Horizontal Pod Autoscaler (HPA) automatically increases or decreases the number of pods in a deployment based on observed CPU utilization or other specified metrics to maintain application performance during traffic spikes.

??? note "Scenario: You are deploying a scientific workload on a shared HPC cluster where you have no root access and must use a shared filesystem. Which runtime do you choose and why?"
Apptainer (formerly Singularity). Unlike Docker, it does not require a root daemon, is designed to run as an unprivileged user, and integrates natively with shared HPC filesystems and job schedulers like Slurm.
