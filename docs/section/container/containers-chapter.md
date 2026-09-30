# Containerization and Orchestration

Welcome to the Containers section of the course. This chapter explores the transition from traditional virtual machines to lightweight, portable containers, and the orchestration layers required to manage them at an enterprise and AI scale.

## Chapter Map

### Part I: Foundations of Containerization

* **[Introduction to Containers](/section/container/foundations/containers.md)**: The core concept of OS-level virtualization, Linux namespaces, cgroups, and the value proposition of containers.
* **[Docker: The Industry Standard](/section/container/foundations/docker.md)**: Understanding images, containers, the Docker CLI, and the build-ship-run workflow.
* **[Beyond Docker](/section/container/foundations/podman.md)**: Exploring daemonless and rootless container engines with Podman and the broader container ecosystem ([`foundations/podman-and-co.md`](/section/container/foundations/podman-and-co.md)).
* **[HPC & Research Containers](/section/container/foundations/apptainer.md)**: Using Apptainer (formerly Singularity) for High Performance Computing and shared-cluster environments.

### Part II: Orchestration at Scale

* **[Kubernetes Fundamentals](/section/container/orchestration/kubernetes.md)**: The K8s API, Pods, Deployments, Services, and the declarative state model.
* **[Local Kubernetes Development](/section/container/orchestration/kubernetes-local.md)**: Setting up local clusters with Kind, Minikube, and K3s for rapid prototyping.
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
