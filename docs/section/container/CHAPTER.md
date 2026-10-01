# Containerization and Orchestration

<!--start-->

Welcome to the Containers section of the course. This chapter explores the transition from traditional virtual machines to lightweight, portable containers, and the orchestration layers required to manage them at an enterprise and AI scale.

## Learning Objectives

By the end of this section, you will be able to:
- **Understand Container Fundamentals**: Distinguish between OS-level virtualization and hardware virtualization, and explain the role of namespaces and cgroups.
- **Master Container Tooling**: Build, ship, and run applications using [Docker](/section/container/foundations/docker.md), [Podman](/section/container/foundations/podman.md), and [Apptainer](/section/container/foundations/apptainer.md).
- **Orchestrate at Scale**: Deploy and manage distributed applications using [Kubernetes](/section/container/orchestration/kubernetes.md), including autoscaling and package management with [Helm](/section/container/specialized/helm.md).
- **Optimize for AI Workloads**: Configure GPU acceleration and high-performance storage for Deep Learning containers.
- **Secure the Pipeline**: Implement container hardening and integrate containerized workloads into a production-ready CI/CD pipeline.

## Overview

Containerization has revolutionized how AI models are deployed. By bundling the model, its dependencies, and the runtime environment into a single immutable image, researchers can ensure that "it works on my machine" translates to "it works in production."

This section is divided into four parts:

### Part I: Foundations of Containerization

* **[Introduction to Containers](/section/container/foundations/containers.md)**: The core concept of OS-level virtualization, Linux namespaces, cgroups, and the value proposition of containers.
* **[Docker: The Industry Standard](/section/container/foundations/docker.md)**: Understanding images, containers, the Docker CLI, and the build-ship-run workflow.
* **[Beyond Docker](/section/container/foundations/podman.md)**: Exploring daemonless and rootless container engines with Podman and the broader container ecosystem ([`foundations/podman-and-co.md`](/section/container/foundations/podman-and-co.md)).
* **[HPC & Research Containers](/section/container/foundations/apptainer.md)**: Using Apptainer (formerly Singularity) for High Performance Computing and shared-cluster environments.

### Part II: Orchestration at Scale

* **[Kubernetes Fundamentals](/section/container/orchestration/kubernetes.md)**: The K8s API, Pods, Deployments, Services, and the declarative state model.
* **[Local Kubernetes Development](/section/container/orchestration/kubernetes-local.md)**: Setting up local clusters with Kind, Minikube, and K3s for rapid prototyping.
* **[Kubernetes Autoscaling](/section/container/kubernetes-advanced/hpa-autoscaling.md)**: Understanding Horizontal Pod Autoscaler (HPA) and Request-based scaling ([`rps-autoscaling.md`](/section/container/kubernetes-advanced/rps-autoscaling.md)) for dynamic AI workloads.
* **[Enterprise Platforms](/section/container/orchestration/openshift.md)**: Red Hat OpenShift and the enterprise-grade wrapper around Kubernetes.
* **[Comparing Orchestrators](/section/container/orchestration/orchestration-comparison.md)**: Evaluating Kubernetes against simpler alternatives like Docker Swarm or Nomad.

### Part III: Specialized Container Operations

* **[GPU Acceleration for AI](/section/container/specialized/ai-containers.md)**: Managing CUDA, the NVIDIA Container Toolkit, and VRAM allocation for Deep Learning workloads.
* **[Storage & Networking](/section/container/specialized/container-storage-networking.md)**: Understanding the CNI and CSI abstraction layers, Persistent Volumes, and high-performance networking for AI.
* **[Package Management with Helm](/section/container/specialized/helm.md)**: Using Helm charts to template and version Kubernetes applications.

### Part IV: Security & Productionization

* **[Container Security & Hardening](/section/container/security/container-security.md)**: Implementing rootless mode, distroless images, and automated vulnerability scanning.
* **[The Deployment Pipeline](/section/container/security/containers-in-pipeline.md)**: Bridging the gap between container builds and CI/CD pipelines for a seamless "Code to Cluster" flow.

---

## Practical Lab

For hands-on experience with these tools, please refer to the **[Local Lab Guide](/section/devops/local-lab.md)** and the specific exercise files within each chapter.

## What's Next?
Start your journey into the world of virtualization by exploring the **[Introduction to Containers](/section/container/foundations/containers.md)**.

<!--end-->