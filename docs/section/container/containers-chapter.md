# Containerization and Orchestration

Welcome to the Containerization section of the course. This chapter explores the shift from traditional virtual machines to lightweight, portable containers, and how to manage them at scale using orchestration platforms.

## Chapter Map

### Part I: Foundations of Containerization

* **[Introduction to Containers](containers.md)**: The core concepts of containerization, the image-container relationship, and the "build once, run anywhere" philosophy.
* **[Container Tool Comparison](container-tool-comparison.md)**: A comparative look at the landscape of container engines.
* **[Docker: The Industry Standard](docker.md)**: Working with Dockerfiles, images, and the Docker runtime.
* **[Podman and the Daemonless Approach](podman.md)**: Exploring rootless containers and the alternative to the Docker daemon.
* **[Apptainer for HPC](apptainer.md)**: Using specialized containers for High-Performance Computing and scientific research.

### Part II: Container Orchestration

* **[Orchestration Landscape](orchestration-comparison.md)**: Why single containers aren't enough and how orchestrators solve the problem of scale.
* **[Kubernetes: The Gold Standard](kubernetes.md)**: Deep dive into K8s architecture, Pods, Services, and Deployments.
* **[Local Kubernetes Development](kubernetes-local.md)**: Setting up development environments with Minikube, Kind, and K3s.
* **[Advanced Kubernetes Scaling](kubernetes-advanced/hpa-autoscaling.md)**: Managing workload demand with HPA and RPS autoscaling.
* **[Package Management with Helm](helm.md)**: Templating and managing complex Kubernetes applications as charts.

### Part III: Enterprise Platforms & Cloud Integration

* **[OpenShift: Enterprise Kubernetes](openshift.md)**: Red Hat's enterprise-grade Kubernetes platform.
* **[Containers on OpenStack](openstack/openstack.md)**: Integrating container workloads within an OpenStack cloud environment.

### Part IV: Advanced Container Operations

* **[Container Security & Hardening](container-security.md)**: Image scanning, rootless containers, and security contexts.
* **[AI Workloads in Containers](ai-containers.md)**: GPU passthrough, NVIDIA Container Toolkit, and optimizing AI images.
* **[Container Storage & Networking](container-storage-networking.md)**: Understanding CNI, CSI, and persistent volume management.
* **[Bridging Containers and CI/CD](containers-in-pipeline.md)**: The path from source code to a running cluster in a production pipeline.

---

## Practical Lab

For hands-on experience with Docker, Podman, and Kubernetes, please refer to the **[Local Lab Guide](../devops/local-lab.md)**.
