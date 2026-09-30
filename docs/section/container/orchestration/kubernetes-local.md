# Local Kubernetes Development

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Evaluate and choose a local Kubernetes distribution (kind, minikube, k3d, or MicroK8s) based on OS and resource constraints.
    - Install the required prerequisite tools, including a container runtime and the `kubectl` CLI.
    - Provision a functional single-node or multi-node Kubernetes cluster on a local machine.
    - Verify cluster health and connectivity using standard Kubernetes CLI commands.
    - Deploy a basic application and expose it to a local browser using NodePort services.
    - Manage the cluster lifecycle (start, stop, and delete) across different local providers.

## Overview

Before deploying to a production GPU cluster or a cloud environment, developers need a safe, isolated sandbox for rapid prototyping. Local Kubernetes distributions allow you to run a fully functional cluster on a single laptop, enabling you to test manifests, verify networking, and debug deployments without incurring cloud costs or risking production stability.

Most local tools use a concept called **Containers-as-Nodes**. Instead of running four separate Virtual Machines to simulate a multi-node cluster, tools like `kind` start Docker containers and run the Kubernetes components (Kubelet, Kube-proxy, etc.) *inside* those containers. This significantly reduces memory overhead while providing a high-fidelity simulation of a real cluster.

## Core Sections

### Choosing a Local Cluster Tool

The right tool depends on your operating system, available RAM, and whether you need a simple single-node setup or a complex multi-node simulation.

| Tool | Implementation | Main Advantages | Ideal Use Case |
|------|----------------|------------------|----------------|
| **kind** (K8s IN Docker) | Nodes as Docker containers | Extremely fast; simulates multi-node clusters; high portability. | CI pipelines, rapid local development, multi-node testing. |
| **minikube** | Typically a VM (or Docker) | Full feature set; supports many drivers; easy addon management. | General development wanting a "real" VM node. |
| **k3d** (k3s in Docker) | Lightweight k3s in Docker | Lowest memory footprint; fastest startup; CNCF-conformant. | Low-resource laptops, ARM machines, edge-style demos. |
| **MicroK8s** | Native binary (Snap) | All-in-one installation; native performance on Ubuntu/WSL2. | Ubuntu users preferring a native, non-virtualized install. |

### Common Prerequisites

Before provisioning a cluster, ensure the following container runtime and command-line tools are installed.

| Operating System | Required Packages | Installation Command |
|------------------|-------------------|----------------------|
| **Ubuntu / Debian** | `docker.io`, `curl`, `git` | `sudo apt update && sudo apt install -y docker.io curl git` |
| **macOS** | Docker Desktop, `kubectl` | `brew install kubectl` |
| **Windows 10/11** | Docker Desktop or WSL2 | Install Docker Desktop or `winget install Kubernetes.kubectl` |

!!! tip "Verification"

    Verify that the container runtime is active before proceeding:

    ```bash
    docker run --rm hello-world
    ```

### Provisioning Your Cluster

Depending on your chosen tool, use the following commands to instantiate your local environment.

#### 1. Using kind (Docker-based)

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/download/v0.23.0/kind-$(uname -s)-$(uname -m)
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create a single-node cluster
kind create cluster --name local-kind

# Verify the cluster
kubectl cluster-info
kubectl get nodes
```

#### 2. Using minikube (VM/Docker-based)

```bash
# Install minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube /usr/local/bin/

# Start using the Docker driver (fastest)
minikube start --driver=docker

# Enable useful addons
minikube addons enable ingress
minikube addons enable metrics-server
```

#### 3. Using k3d (Lightweight k3s)

```bash
# Install k3d
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash

# Create a cluster
k3d cluster create local-k3d

# Verify
kubectl get nodes
```

#### 4. Using MicroK8s (Native Ubuntu)

```bash
# Install via snap
sudo snap install microk8s --classic
sudo usermod -a -G microk8s $USER
newgrp microk8s

# Enable core services
microk8s enable dns dashboard

# Alias kubectl for convenience
alias kubectl='microk8s kubectl'
```

### Testing the Cluster: "Hello World" AI API

The following manifest deploys a simple Flask-based AI API and exposes it via a `NodePort` service, which maps a port on your local machine directly to the service in the cluster.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-hello-world
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-hello-world
  template:
    metadata:
      labels:
        app: ai-hello-world
    spec:
      containers:
      - name: flask-api
        image: cloudmesh/flask-ai-demo:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: ai-hello-world
spec:
  type: NodePort
  selector:
    app: ai-hello-world
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30007
```

**Deployment Steps**:

1. Save the above as `ai-hello-world.yaml`.
2. Apply the manifest: `kubectl apply -f ai-hello-world.yaml`.
3. Verify status: `kubectl get pods,svc ai-hello-world`.
4. Access in browser: `http://localhost:30007`.

### Local Storage for AI: Managing Model Weights

When running AI workloads locally, you cannot bake 20GB of model weights into a container image without making your build pipeline unusable. You must use external storage.

#### `hostPath` vs. Local-Path Provisioners
- **`hostPath`**: Maps a specific directory from your laptop (e.g., `/Users/grey/models`) into the pod. While simple, it is fragile because it relies on the absolute path existing on the node.
- **Local-Path Provisioner**: A more robust approach used by tools like `kind`. It dynamically creates a directory on the host and manages it as a `PersistentVolume`, providing a better simulation of cloud storage.

#### Simulating Network Storage (NFS) locally
To test production-grade weight loading, you can run a lightweight NFS server in a separate container. This allows you to test `ReadWriteMany` (RWX) access, where multiple LLM pods read the same weights simultaneously—a requirement for scaling inference.

---

### The Local-to-Cloud Workflow: The Validation Loop

Local Kubernetes is not just for "running the app"; it is for **validating the infrastructure**. The professional AI engineering workflow follows a strict validation loop:

1. **Local Prototyping**: Use `kind` or `k3d` to verify that the `Deployment` and `Service` manifests are syntactically correct.
2. **Resource Validation**: Test if the pod can start with the requested memory limits without hitting an `OOMKilled` state locally.
3. **Staging**: Deploy to a managed cluster (e.g., EKS/GKE) with similar (but smaller) GPU resources.
4. **Production**: Deploy to the full-scale GPU cluster using Helm/Kustomize.

By catching manifest errors locally, you avoid the "commit-push-wait-fail" cycle that slows down AI development.

---

### Troubleshooting Common Local Issues

| Symptom | Likely Cause | Resolution |
|---------|--------------|------------|
| `kubectl: command not found` | CLI not installed or not in PATH. | Install `kubectl` via brew, apt, or the provider's bundle. |
| `Cannot connect to Docker daemon` | Docker service is stopped. | Start Docker Desktop or run `sudo systemctl start docker`. |
| `Nodes show NotReady` | Insufficient system RAM. | Increase allocated memory (e.g., `minikube start --memory=4096`). |
| `Port already allocated` | Host port is bound by another app. | Change the `nodePort` to a different value in the 30000-32767 range. |
| `Permission denied` (Linux) | User not in `docker` group. | `sudo usermod -aG docker $USER && newgrp docker`. |

### Alternative Runtime: Podman

For security-focused environments, **Podman** is a daemonless, rootless alternative to Docker. Since `kind` and `k3d` require a socket to manage node containers, you must enable the Podman socket:

```bash
systemctl --user enable --now podman.socket
```

Using Podman removes the need for a privileged root daemon, reducing the attack surface of your local machine while maintaining OCI compatibility.

## Summary Checklist

- [ ] Select a local cluster tool based on OS and available RAM.
- [ ] Install the container runtime (Docker or Podman) and `kubectl`.
- [ ] Provision a cluster using `kind`, `minikube`, `k3d`, or `MicroK8s`.
- [ ] Verify node status using `kubectl get nodes`.
- [ ] Deploy a sample application using a YAML manifest.
- [ ] Access the application via a `NodePort` service on `localhost`.
- [ ] Practice cluster lifecycle management (start/stop/delete).

## Assignments

!!! note "Assignment.1: Multi-Node Simulation"
    Use `kind` to create a cluster with one control-plane node and two worker nodes. Verify that all three nodes are active and healthy.
    
    ??? tip "Solution: Multi-Node Kind"
        Create a `kind-config.yaml` with `kind: Cluster`, `apiVersion: kind.x-k8s.io/v1alpha4`, and a `nodes` list containing one `role: control-plane` and two `role: worker` entries. Run `kind create cluster --config kind-config.yaml`.

!!! note "Assignment.2: Application Exposure"
    Deploy a simple Nginx pod and create a Service of type `NodePort`. Determine the assigned port using `kubectl get svc` and access the Nginx welcome page in your browser.
    
    ??? tip "Solution: NodePort Exposure"
        Create a deployment for `nginx:alpine`, then create a service with `type: NodePort`. Use `kubectl get svc <service-name>` to find the port mapping (e.g., `80:31234/TCP`), then visit `http://localhost:31234`.

!!! note "Assignment.3: Lifecycle Management"
    Provision a cluster using `minikube`, enable the `ingress` addon, deploy a sample app, and then completely delete the cluster to ensure a clean state.
    
    ??? tip "Solution: Lifecycle"
        Use `minikube start`, `minikube addons enable ingress`, `kubectl apply -f <manifest>`, and finally `minikube delete`.

!!! note "Assignment.4: Local Storage Implementation"
    Deploy a pod that mounts a local directory from your host using a `hostPath` volume. Create a file on your laptop in that directory and verify that the pod can read it. Then, attempt to do the same using a `PersistentVolumeClaim` with a local-path provisioner.
    
    ??? tip "Solution: Local Storage"
        For `hostPath`, use `volumes: [{name: data, hostPath: {path: /tmp/models}}]`. For PVC, create a `PersistentVolumeClaim` and let the local-path-provisioner automatically create the PV on the host.

!!! note "Assignment.5: The Validation Loop"
    Write a bash script that performs a "Local CI Check":
    1. Deletes any existing `kind` cluster.
    2. Creates a new `kind` cluster.
    3. Applies a set of AI service manifests.
    4. Waits for pods to be `Ready`.
    5. Runs a `curl` command to verify the API is responding.
    6. Deletes the cluster.
    
    ??? tip "Solution: Validation Script"
        Use `kind create cluster`, `kubectl apply -f manifests/`, and a `while` loop with `kubectl get pods` to check status before running the `curl` test.

## References

- Kind Documentation: [kind.sigs.k8s.io](https://kind.sigs.k8s.io/)
- Minikube Documentation: [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/)
- k3d Documentation: [k3d.io](https://k3d.io/)
- MicroK8s Documentation: [microk8s.io](https://microk8s.io/)

## Self-Evaluation

??? note "Compare `kind` and `minikube` in terms of how they host the Kubernetes nodes."
    `kind` runs Kubernetes nodes as Docker containers on the host, making it very fast and portable. `minikube` typically runs a single node inside a virtual machine (though it supports a Docker driver), providing a more isolated environment that closely mimics a real VM node.

??? note "Which local Kubernetes tool is best suited for low-resource environments or ARM machines?"
    `k3d` (k3s in Docker) is the best choice for low-resource environments because it runs k3s, a lightweight, certified Kubernetes distribution, inside Docker containers.

??? note "What is the role of `kubectl` in managing a local Kubernetes cluster?"
    `kubectl` is the standard CLI tool used to communicate with the Kubernetes API server. Regardless of the local provider (`kind`, `minikube`, etc.), `kubectl` is the primary interface for deploying pods, managing services, and inspecting cluster health.

??? note "Why is a container runtime a prerequisite for tools like `kind` or `k3d`?"
    Because `kind` and `k3d` use containers to simulate the nodes of a Kubernetes cluster, they require a running runtime (like Docker or Podman) on the host to provision and manage those node-containers.

??? note "What are the advantages of using Podman as the runtime for a local Kubernetes cluster?"
    Using Podman allows for a daemonless and rootless experience, improving security by removing the need for a privileged root daemon and reducing system overhead.

## What's Next?

Now that you have a functional local sandbox, it's time to learn how to scale these workloads for production. Head over to **[Kubernetes (K8s) for AI: Production-Grade Orchestration](/section/container/orchestration/kubernetes.md)** to learn about GPU scheduling, Taints, and Tolerations.
