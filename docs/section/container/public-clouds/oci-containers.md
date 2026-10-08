# OCI Containers

!!! info "Learning Objectives"
    - Deploy an Oracle Container Engine for Kubernetes (OKE) cluster.
    - Compare and implement Virtual Nodes and Managed Nodes within OKE.
    - Configure and manage container images using the Oracle Cloud Infrastructure Registry (OCIR).
    - Deploy serverless containers using OCI Container Instances.
    - Implement network security and load balancing for containerized workloads in OCI.
    - **Integrate OKE with auto-scaling (HPA) and Infrastructure as Code (Terraform).**
    - **Optimize OKE deployments for the OCI Always Free tier.**

## Overview

Oracle Cloud Infrastructure (OCI) provides a set of container services designed to manage the lifecycle of containerized applications. The primary offerings include Oracle Container Engine for Kubernetes (OKE) for orchestrated clusters, OCI Container Instances for serverless container execution, and the Oracle Cloud Infrastructure Registry (OCIR) for private image management. These services integrate with OCI Identity and Access Management (IAM) and Virtual Cloud Network (VCN) to provide security and networking isolation.

## Core Sections

### Oracle Container Engine for Kubernetes (OKE)

OKE is a managed Kubernetes service that simplifies the deployment and operation of Kubernetes clusters. It manages the Kubernetes control plane, providing high availability and automated updates.

The OKE architecture consists of a managed control plane and worker nodes. The control plane is hosted and managed by Oracle, which reduces the operational overhead of managing etcd and the Kubernetes API server.

OKE offers two types of node pools:

1. Managed Nodes: The user is responsible for the worker node lifecycle, including OS patching and scaling. The nodes are standard OCI Compute instances.
2. Virtual Nodes: A serverless Kubernetes experience where Oracle manages the underlying compute infrastructure. Users manage only the pods and the cluster configuration. This removes the need to manage node pools or patch the operating system.

#### Always Free Optimization
For students and developers, OCI provides an **Always Free** tier. To stay within these limits when using OKE:
- Use **Virtual Nodes** where possible to minimize management overhead.
- Leverage **ARM Ampere A1 shapes** for worker nodes, which offer significantly more resources (up to 4 OCPUs and 24 GB of RAM) for free compared to AMD shapes.
- Monitor your **Block Volume** usage, as OCI provides a generous total quota (usually 200 GB) shared across all boot and data volumes.

#### Scaling and Elasticity
To achieve true cloud-native elasticity on OKE, you must combine Kubernetes-level scaling with OCI-level infrastructure scaling:
- **Pod Scaling**: Implement the **Horizontal Pod Autoscaler (HPA)** to increase pod replicas based on CPU/Memory utilization (refer to `docs/section/container/kubernetes-advanced/hpa-autoscaling.md`).
- **Node Scaling**: For Managed Nodes, enable the **Cluster Autoscaler**. This allows OKE to automatically add or remove worker nodes from the node pool when pods cannot be scheduled due to insufficient resources.
- **Virtual Node Scaling**: Since Virtual Nodes are serverless, scaling is handled automatically by Oracle, removing the need for a Cluster Autoscaler.

Creating a cluster involves defining the VCN, choosing the node pool type, and configuring the API endpoint access. The endpoint can be set to Public, allowing access from the internet, or Private, restricting access to the VCN or connected networks.

OKE integrates with OCI IAM via the OCI Kubernetes Service. Role-based access control (RBAC) within Kubernetes is mapped to OCI IAM groups to control cluster management and resource deployment permissions.

### OCI Container Instances

OCI Container Instances provide a serverless method to run containers without the overhead of managing Kubernetes clusters. They are suitable for lightweight workloads, CI/CD runners, or short-lived tasks.

To deploy a container instance, the user specifies the container image, resource requirements (CPU and RAM), and networking configuration. OCI provisions the necessary compute resources and executes the container.

This service eliminates the need to manage worker nodes or clusters, making it a viable option for applications that do not require the complex orchestration features provided by Kubernetes.

### Oracle Cloud Infrastructure Registry (OCIR)

OCIR is a managed Docker registry that allows users to store, manage, and distribute container images.

#### Serverless Comparison Matrix
To understand where OKE fits in the broader cloud landscape, compare OCI's serverless container offerings with other major providers:

| Feature | OKE Virtual Nodes | AWS Fargate | GKE Autopilot |
| :--- | :--- | :--- | :--- |
| **Management** | Oracle managed | AWS managed | Google managed |
| **Pricing** | Per Pod resource | Per Pod resource | Per Pod resource |
| **Control** | High (Standard K8s) | Moderate | Moderate/Low |
| **Ideal Use** | Enterprise K8s without VM overhead | AWS-native serverless K8s | Fully managed "Hands-off" K8s |

Authentication for OCIR is handled through OCI IAM. Users must create an Auth Token in their user profile. This token serves as the password when logging in via the Docker CLI, while the username follows the format `<tenancy-namespace>/<username>`.

The process for pushing and pulling images requires tagging images with the region-specific registry endpoint.

```bash
docker login <region-key>.ocir.io
# Username: <tenancy-namespace>/<username>
# Password: <auth-token>

docker tag my-image:latest <region-key>.ocir.io/<tenancy-namespace>/my-repo:latest
docker push <region-key>.ocir.io/<tenancy-namespace>/my-repo:latest
```

### Networking & Load Balancing

Containers in OCI run within a Virtual Cloud Network (VCN). Proper network design is required to ensure security and availability.

#### Infrastructure as Code (IaC) with Terraform
In production environments, OKE clusters and their networking are rarely created manually. The **OCI Terraform Provider** is the industry standard for automating these deployments. Using Terraform allows you to:
- Define your VCN, Subnets, and OKE Cluster as a version-controlled configuration.
- Ensure consistency across Development, Staging, and Production environments.
- Quickly tear down and rebuild test clusters for cost optimization.

A typical Terraform workflow for OKE involves using a module that handles the complex networking requirements (Public/Private subnets) before calling the `oci_containerengine_cluster` resource.

A typical OKE deployment requires a public subnet for the load balancer and private subnets for worker nodes. This architecture ensures that application workloads are not directly exposed to the public internet.

OKE integrates with the OCI Load Balancer service. When a Kubernetes Service of type `LoadBalancer` is created, OKE automatically provisions an OCI Load Balancer and configures the listener and backend sets.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

Security Lists and Network Security Groups (NSGs) control the traffic allowed into the worker nodes. Essential ports include 6443 for the Kubernetes API and the specific ports used by the application.

## Summary Checklist

- [ ] VCN and subnets configured for OKE deployment.
- [ ] OKE cluster created with a selected node pool (Managed or Virtual).
- [ ] IAM policies configured for cluster and node access.
- [ ] OCIR repository created and container image pushed.
- [ ] Container Instances deployed for serverless workloads.
- [ ] OCI Load Balancer configured and connectivity verified.
- [ ] Security Lists updated to allow application traffic.

## Assignments

!!! note "Assignment.1: Deploy a Basic OKE Cluster"
    Create a VCN with a public and private subnet. Deploy an OKE cluster using Virtual Nodes and deploy a simple Nginx pod. Verify the application is reachable via the OCI Load Balancer.

    ??? tip "Solution: Deploy a Basic OKE Cluster"
        1. Use the OCI Console or CLI to create a VCN with two subnets.
        2. Navigate to Developer Services > Kubernetes Clusters (OKE) and create a cluster.
        3. Select "Virtual Nodes" during the node pool configuration.
        4. Configure `kubectl` using the OCI CLI command: `oci ce cluster create-kubeconfig --cluster-id <cluster-ocid>`.
        5. Apply the Nginx deployment and a Service of type `LoadBalancer`.
        6. Find the external IP of the Load Balancer and test via a browser.

!!! note "Assignment.2: Manage Images with OCIR"
    Create a private repository in OCIR, push a custom application image, and configure an OKE pod to pull the image from the registry.

    ??? tip "Solution: Manage Images with OCIR"
        1. Generate an Auth Token in OCI User Settings.
        2. Run `docker login <region-key>.ocir.io` using the `<tenancy-namespace>/<username>` format.
        3. Build a local image: `docker build -t my-app .`.
        4. Tag the image: `docker tag my-app <region-key>.ocir.io/<tenancy-namespace>/my-app:v1`.
        5. Push the image: `docker push <region-key>.ocir.io/<tenancy-namespace>/my-app:v1`.
        6. In the Kubernetes deployment YAML, specify the image path: `image: <region-key>.ocir.io/<tenancy-namespace>/my-app:v1`.
        7. Create a Kubernetes secret of type `docker-registry` to allow OKE to authenticate with OCIR.

!!! note "Capstone Project: Cloud-Native CI/CD Pipeline on OCI"
    **Goal**: Implement a fully automated pipeline from code to production using OCI services.
    1. **Infrastructure**: Provision an OKE cluster (Virtual Nodes) and a VCN using a Terraform script.
    2. **CI/CD**: Set up a pipeline (e.g., GitHub Actions or OCI DevOps) that:
        - Triggers on a `git push`.
        - Builds a Docker image from the source code.
        - Pushes the image to **OCIR**.
        - Updates the OKE deployment using `kubectl set image`.
    3. **Elasticity**: Configure an **HPA** (Horizontal Pod Autoscaler) to scale your pods based on CPU usage.
    4. **Verification**: Use a load-testing tool (like `hey` or `ab`) to trigger a scaling event and verify that new pods are created automatically.

## References

- OCI OKE Documentation: https://docs.oracle.com/en-us/iaas/Content/ContainerEngine/Concepts/containerengineoverview.htm
- OCI Container Registry Documentation: https://docs.oracle.com/en-us/iaas/Content/Containers/Concepts/containerregistry.htm
- OCI Container Instances Documentation: https://docs.oracle.com/en-us/iaas/Content/Containers/Concepts/containerinstances.htm

## Self-Evaluation

??? note "What is the difference between Managed Nodes and Virtual Nodes in OKE?"
    Managed Nodes are OCI Compute instances where the user is responsible for the OS lifecycle and patching. Virtual Nodes provide a serverless experience where Oracle manages the underlying infrastructure and OS, allowing the user to focus only on the pods.

??? note "How does OCIR authentication work?"
    OCIR uses OCI IAM for authentication. Users log in using the Docker CLI with a username in the format `<tenancy-namespace>/<username>` and an OCI Auth Token as the password.

??? note "When should OCI Container Instances be used instead of OKE?"
    OCI Container Instances should be used for lightweight, standalone workloads, short-lived tasks, or CI/CD runners that do not require the complex orchestration, auto-scaling, and service discovery features provided by a full Kubernetes cluster.
