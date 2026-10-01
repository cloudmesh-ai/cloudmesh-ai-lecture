# Container Storage & Networking

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Understand the ephemeral nature of container filesystems and the necessity of persistent storage.
    - Differentiate between Bind Mounts and Volumes for data persistence.
    - Explain the Container Network Interface (CNI) and how pods communicate across a cluster.
    - Understand the Container Storage Interface (CSI) and the lifecycle of Persistent Volumes (PV) and Claims (PVC) in [Kubernetes](../orchestration/kubernetes.md).

## Overview

Containers are designed to be **ephemeral**. This means that any data written to the container's own writable layer is deleted the moment the container is stopped or deleted. For AI workloads—where datasets can be terabytes in size and model weights are critical assets—this behavior is unacceptable. You cannot risk losing a trained model simply because a pod restarted.

To handle data and communication at scale, the industry relies on abstraction layers (CSI and CNI) that separate the application from the underlying physical hardware, allowing for portable and resilient infrastructure.

!!! info "Why this matters"
    In a distributed AI training setup, multiple containers across different physical nodes must access the same dataset. Storing data inside a container would require duplicating it on every node, wasting massive amounts of storage. By using shared storage and a standardized networking layer, you can mount a single high-performance network drive (like NFS or Lustre) into thousands of containers simultaneously, ensuring data consistency across the entire cluster.

## Implementation

### Container Storage: Beyond Ephemeral Layers

To persist data, it must be stored *outside* the container's writable layer.

#### Bind Mounts vs. Volumes

- **Bind Mounts**: Map a specific path on the host machine (e.g., `/home/user/data`) directly into the container. While fast and simple, bind mounts tie the container to a specific host's directory structure, reducing portability.
- **Volumes**: Managed by the container engine (Docker/Podman). The engine creates a directory on the host and manages its lifecycle. Volumes are more portable and are the preferred method for persisting data in production environments.

#### The [Kubernetes](../orchestration/kubernetes.md) Storage Stack (CSI)

In [Kubernetes](../orchestration/kubernetes.md), the **Container Storage Interface (CSI)** provides a universal API that allows K8s to interact with any storage provider (e.g., AWS EBS, Azure Disk, or local NFS) without needing to build a specific integration for every vendor.

![CSI Abstraction](images/csi-abstraction.png)

Figure 1: The CSI Abstraction. The CSI Driver ensures that the K8s API can request storage from any provider without knowing the provider's specific API.

**The PV/PVC Lifecycle:**

1. **Persistent Volume (PV)**: A piece of storage in the cluster provisioned by an administrator or a storage class. It represents the "physical" disk.
2. **Persistent Volume Claim (PVC)**: A request for storage by a user (e.g., "I need 50Gi of storage with ReadWriteOnce access"). It acts as a "ticket" to claim a PV.
3. **Binding**: [Kubernetes](../orchestration/kubernetes.md) matches the PVC to an available PV and mounts it into the Pod.

#### Enterprise Storage for AI: Scaling to Petabytes

For small projects, a local NFS or cloud disk is sufficient. However, production AI clusters handling petabytes of data require **Distributed Storage**.

- **Ceph**: A unified storage system that provides block, file, and object storage. Ceph is widely used in AI because it scales horizontally and provides high redundancy.
- **GlusterFS**: A scalable network filesystem that aggregates disk storage from multiple servers into a single global namespace. It is often used for storing massive datasets that must be accessible to thousands of GPU nodes simultaneously.
- **Lustre**: The "gold standard" for supercomputing. Lustre is designed for extreme I/O throughput, allowing thousands of nodes to read from the same dataset without bottlenecking the metadata server.

!!! info "Storage Strategy: Throughput vs. Latency"
    When designing an AI system, you must choose your storage based on the workload:
    - **Training**: Requires high **throughput** (sequential reads of large files). Use Lustre or CephFS.
    - **Inference**: Requires low **latency** (fast access to small model weights). Use local NVMe SSDs or a fast local-path provisioner.

### Container Networking: How Pods Talk

Networking in containers is complex because pods are ephemeral and frequently move between hosts. A stable discovery mechanism is required to maintain communication.

#### The Container Network Interface (CNI)

Similar to storage, networking is standardized via the **CNI**. This specification allows different networking plugins (such as Flannel, Calico, or Cilium) to be swapped in and out of a cluster without changing the application code.

**The AI Traffic Flow: From User to Model**

In a production AI deployment, a request travels through several layers of abstraction before it hits the GPU.

![Traffic Flow](images/traffic-flow.png)

Figure 2: The AI Traffic Flow.
`External User` $\rightarrow$ `Ingress (Routing)` $\rightarrow$ `Service (Load Balancing)` $\rightarrow$ `Pod (Application)` $\rightarrow$ `GPU (Inference)`.

1. **External User**: Sends an HTTP request (e.g., via a REST API) to the public IP.
2. **Ingress**: The Ingress Controller (e.g., NGINX) evaluates the host header (e.g., `api.ai-model.com`) and routes the traffic to the correct internal Service.
3. **Service**: The Service acts as a stable entry point. It load-balances the request across multiple identical Pods using a round-robin or least-connection strategy.
4. **Pod**: The request enters the Pod's network namespace. The application (e.g., FastAPI) processes the request and sends it to the model engine.
5. **GPU**: The model engine uses the NVIDIA driver to execute the inference on the GPU.

**Core Networking Concepts:**

- **Pod Networking**: Every Pod in [Kubernetes](../orchestration/kubernetes.md) receives its own unique IP address. All containers within a single Pod share that IP and can communicate via `localhost`.
- **Service (ClusterIP)**: Because Pod IPs are volatile, a **Service** provides a stable IP address and DNS name that load-balances traffic across a set of identical Pods.
- **Ingress**: The entry point for external traffic, routing requests from the outside world (e.g., `api.my-ai-model.com`) to the correct internal Service.

#### Networking for AI: High-Performance Requirements

Standard container networking introduces a small amount of latency due to virtualization. For distributed AI training (e.g., using PyTorch Distributed), this latency can become a primary bottleneck.

- **Host Networking**: Running a container with `--net=host` removes network isolation, allowing the container to use the host's network stack directly for maximum performance.
- **SR-IOV / RDMA**: Specialized CNI plugins allow AI containers to bypass the kernel entirely and communicate directly with the NIC, which is essential for multi-node GPU training and low-latency weight synchronization.

## Summary Checklist

- [ ] Explain why the container writable layer is unsuitable for AI model weights.
- [ ] Compare Bind Mounts and Volumes in terms of portability and management.
- [ ] Describe the relationship between a Persistent Volume (PV) and a Persistent Volume Claim (PVC).
- [ ] Explain the role of the CSI in abstracting storage providers.
- [ ] Identify the purpose of the CNI in standardized pod networking.
- [ ] Contrast standard bridge networking with Host Networking for high-performance AI workloads.

## Self-Evaluation

??? question "What happens to data in a container if you don't use a Volume or Bind Mount?"
    The data is stored in the container's writable layer. Because this layer is tied to the specific container instance, it is destroyed the moment the container is deleted, resulting in total data loss.

??? question "What is the difference between a PV and a PVC in [Kubernetes](../orchestration/kubernetes.md)?"
    A PV (Persistent Volume) is the actual storage resource (the physical disk) provisioned by an admin. A PVC (Persistent Volume Claim) is a request for storage by a user. The PVC abstracts the hardware, allowing a developer to request "50Gi of storage" without knowing whether it is backed by AWS EBS or a local NFS.

??? question "Why is CNI important for [Kubernetes](../orchestration/kubernetes.md)?"
    CNI provides a standardized way for [Kubernetes](../orchestration/kubernetes.md) to configure networking. It allows the cluster to remain agnostic of the underlying network provider, meaning an organization can migrate a cluster from one cloud provider to another by simply changing the CNI plugin.

## Assignments

!!! note "Assignment.1: Data Persistence Test"
    Start a container and create a writable file. Stop and delete the container, then verify the file is gone. Repeat the process using a **Docker Volume** and verify that the file persists after the container is deleted.
    
    ??? tip "Solution: Persistence Test"
        1. Run `docker run --name test-ephemeral alpine sh -c "echo 'hello' > /data/test.txt"`. Delete the container and try to find the file.
        2. Run `docker volume create my-vol` and `docker run -v my-vol:/data alpine sh -c "echo 'hello' > /data/test.txt"`. Delete the container, then start a new one mounting the same volume to verify the file is still there.

!!! note "Assignment.2: Exploring K8s Services"
    Deploy two pods in a local cluster (e.g., using Kind). Attempt to ping one from the other using its IP. Delete the pod and redeploy it; observe the IP change. Finally, create a **Service** and ping the service's stable DNS name to verify the solution to IP volatility.
    
    ??? tip "Solution: Service Discovery"
        Create a deployment for a simple web server. Use `kubectl get pods -o wide` to see the IP. Delete the pod and see the new IP. Create a Service with `kubectl expose deployment <name> --port=80` and then `kubectl exec` into a second pod to `curl <service-name>`.

!!! note "Assignment.3: Storage Strategy Design"
    You are designing a system to train a Large Language Model on a dataset of 50TB. The training will run across 64 GPU nodes.
    1. Which storage solution would you choose (Local Disk, NFS, or a Distributed Filesystem like Ceph/Lustre) and why?
    2. How would you configure the `PersistentVolumeClaim` to ensure all 64 nodes can read the dataset simultaneously?
    3. Explain the trade-off between using a "ReadWriteOnce" (RWO) vs. "ReadWriteMany" (RWX) access mode in this scenario.
    
    ??? tip "Solution: Storage Strategy"
        1. **Distributed Filesystem (Lustre/Ceph)**: Local disks are too small, and a single NFS server would become a bottleneck for 64 nodes. Lustre/Ceph provides the necessary aggregate throughput.
        2. Use a PVC with `accessModes: [ReadWriteMany]` and a StorageClass that supports shared filesystems.
        3. RWO allows only one node to mount the volume; RWX is required for distributed training where multiple pods must read the same weights and data.

## References

- [Kubernetes](../orchestration/kubernetes.md) Storage Documentation: [kubernetes.io/docs/concepts/storage/](https://kubernetes.io/docs/concepts/storage/)
- CNI Specification: [cncf.io/projects/cni/](https://cncf.io/projects/cni/)
- Docker Volumes Guide: [docs.docker.com/storage/volumes/](https://docs.docker.com/storage/volumes/)

## What's Next?

You now know how to build, secure, and connect containers. The final step is to automate this entire process. Head over to **[Bridging Containers and CI/CD](/section/container/security/containers-in-pipeline.md)** to see how to turn your Dockerfile into a production-ready pipeline.
