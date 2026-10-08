# Azure Containers

!!! info "Learning Objectives"
    - Architect and deploy an Azure Kubernetes Service (AKS) cluster.
    - Differentiate between Azure CNI and Kubenet networking models.
    - Deploy serverless containers using Azure Container Instances (ACI).
    - Implement a private image management strategy with Azure Container Registry (ACR).
    - Build event-driven microservices using Azure Container Apps with KEDA and Dapr.
    - Configure Azure container networking using Load Balancers and Application Gateways.

## Overview

Azure provides a tiered ecosystem of container services designed to balance operational control with developer velocity. At the highest level of control is Azure Kubernetes Service (AKS), a managed Kubernetes offering that abstracts the control plane while providing deep access to node configuration. For workloads requiring rapid deployment without cluster management, Azure Container Instances (ACI) provides a serverless container execution environment.

Bridging the gap between full orchestration and serverless is Azure Container Apps, which leverages KEDA for autoscaling and Dapr for microservice communication. Supporting these services is the Azure Container Registry (ACR), which provides a secure, geo-replicated storage mechanism for container images. Networking across these services is integrated into Azure Virtual Networks (VNets), utilizing Azure Load Balancers and Application Gateways to manage ingress and egress traffic.

## Azure Kubernetes Service (AKS)

Azure Kubernetes Service (AKS) is a managed Kubernetes offering that reduces the overhead of deploying and managing Kubernetes clusters. Azure manages the Kubernetes control plane (API server, etcd, scheduler, and controller manager) at no cost for the Free tier, while the user manages the agent nodes.

### Cluster Architecture

An AKS cluster consists of a managed control plane and one or more node pools. The control plane handles the orchestration of the cluster, while nodes run the actual application pods.

The control plane is hosted by Azure and is not directly accessible via SSH. It ensures that the desired state of the cluster is maintained. Nodes are Azure Virtual Machines configured with the kubelet, a container runtime (containerd), and a network proxy (kube-proxy or Cilium).

### Node Pools

Nodes in AKS are organized into node pools. A node pool is a group of VMs with the same configuration (VM size, OS image, etc.).

1. System Node Pools: Every cluster must have at least one system node pool. These pools host critical system pods such as CoreDNS and konnectivity.
2. User Node Pools: User node pools are used to run application workloads. They allow for heterogeneous compute resources, such as GPU-enabled VMs for machine learning workloads, separate from the system pods.

### Networking Models

AKS supports two primary network models that determine how pods receive IP addresses.

Azure CNI (Container Networking Interface): In this model, every pod receives a full IP address from the Azure Virtual Network subnet. This allows pods to be first-class citizens in the VNet, enabling direct connectivity to other Azure resources. However, it consumes a large number of IP addresses from the subnet.

Kubenet: This model uses a logically separate network for pods. Only the nodes receive IP addresses from the VNet. Pods are assigned IPs from a private CIDR range and use routing tables to communicate with the rest of the network. This is more IP-efficient but requires more complex routing configuration for external access.

### Azure AD Integration

AKS integrates with Azure Active Directory (Azure AD) to provide Role-Based Access Control (RBAC). By enabling Azure AD integration, cluster administrators can assign Kubernetes RBAC roles to Azure AD users or groups. This eliminates the need to manage separate Kubernetes certificates for authentication.

To create a basic AKS cluster using the Azure CLI:

```bash
az group create --name myResourceGroup --location eastus

az aks create \
    --resource-group myResourceGroup \
    --name myAKSCluster \
    --node-count 3 \
    --enable-addons monitoring \
    --generate-ssh-keys
```

## Azure Container Instances (ACI)

Azure Container Instances (ACI) is a serverless container offering that allows users to run a container in Azure without managing any virtual machines or orchestrators.

### Serverless Execution Model

ACI abstracts the underlying infrastructure entirely. When a container is deployed, Azure provisions the necessary compute and network resources on demand. This makes ACI ideal for burstable workloads, simple applications, and task automation.

### Deployment and Use Cases

ACI supports deployment via the Azure CLI, portal, or YAML templates. It is commonly used for:

- Simple applications that do not require the complexity of Kubernetes.
- Scheduled tasks and batch jobs.
- Bursting AKS workloads to ACI using the Virtual Kubelet.

Example ACI deployment YAML:

```yaml
apiVersion: container.azure.com/v1
kind: ContainerGroup
metadata:
  name: hello-world-aci
properties:
  containers:
  - name: hello-world
    properties:
      image: mcr.microsoft.com/azuredocs/aci-helloworld
      ports:
      - port: 80
        protocol: TCP
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 1.5
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - port: 80
      protocol: TCP
```

## Azure Container Registry (ACR)

Azure Container Registry (ACR) is a managed Docker registry service based on the Open Container Initiative (OCI) distribution specification.

### Image Management

ACR provides a centralized location to store and manage container images. It supports private registries, ensuring that images are only accessible to authorized users and services.

### Geo-replication

For globally distributed applications, ACR supports geo-replication. This feature replicates the registry to multiple Azure regions, allowing AKS clusters in different regions to pull images from a local registry, reducing latency and increasing reliability.

### Vulnerability Scanning

ACR integrates with Microsoft Defender for Cloud to provide vulnerability scanning. When an image is pushed to the registry, it is automatically scanned for known security vulnerabilities (CVEs), and the results are reported in the Azure portal.

To create a registry and push an image:

```bash
az acr create --resource-group myResourceGroup --name myRegistry --sku Basic

az acr login --name myRegistry

docker tag my-image:latest myRegistry.azurecr.io/my-image:latest

docker push myRegistry.azurecr.io/my-image:latest
```

## Azure Container Apps

Azure Container Apps is a serverless platform designed for microservices, built on top of Kubernetes but abstracting the complexity of cluster management.

### Architecture and Serverless Nature

Container Apps allows developers to deploy containers without managing the underlying Kubernetes cluster. It handles the scaling, ingress, and environment configuration automatically.

### Autoscaling with KEDA

Azure Container Apps uses KEDA (Kubernetes Event-driven Autoscaling) to scale applications based on events. Unlike standard Kubernetes Horizontal Pod Autoscalers (HPA) that rely on CPU/Memory, KEDA allows scaling based on:

- HTTP traffic volume.
- Message queue depth (e.g., Azure Service Bus).
- Database changes.
- Cron schedules.

### Microservices with Dapr

Integration with Dapr (Distributed Application Runtime) provides a set of building blocks for microservices. Dapr simplifies common distributed system challenges such as:

- State management: Providing a consistent API for key-value stores.
- Service-to-service invocation: Handling service discovery and retries.
- Pub/Sub: Implementing asynchronous messaging between services.

## Networking

Container networking in Azure ensures that workloads are reachable and secure.

### Virtual Networks (VNet)

All container services can be integrated into an Azure VNet. This allows containers to communicate with other Azure resources (like SQL databases) using private IP addresses, reducing exposure to the public internet.

### Azure Load Balancer

The Azure Load Balancer operates at Layer 4 (TCP/UDP). In AKS, creating a Service of type `LoadBalancer` automatically provisions an Azure Load Balancer that distributes incoming traffic across the nodes in the cluster.

### Application Gateway

For Layer 7 (HTTP/HTTPS) routing, the Azure Application Gateway is used. It provides advanced features such as:

- URL-based routing.
- SSL termination.
- Web Application Firewall (WAF) for protection against common web attacks.

The Application Gateway Ingress Controller (AGIC) allows AKS to manage the Application Gateway configuration directly via Kubernetes Ingress resources.

## Summary Checklist

- [ ] Resource group created and region selected.
- [ ] ACR created and integrated with the AKS cluster.
- [ ] AKS cluster deployed with appropriate node pool sizes.
- [ ] Network model (Azure CNI or Kubenet) selected based on IP availability.
- [ ] Azure AD RBAC roles assigned to cluster users.
- [ ] Ingress controller (AGIC or NGINX) configured for external traffic.
- [ ] KEDA scalers defined for Azure Container Apps.
- [ ] VNet integration configured for private resource access.

## Assignments

!!! note "Assignment.1: Deploy a Multi-Container App to AKS"
    Create an AKS cluster and deploy a simple two-tier application (frontend and backend) using Kubernetes manifests. Ensure the frontend can communicate with the backend using a Kubernetes Service.

    ??? tip "Solution: Deploy a Multi-Container App to AKS"
        1. Create a deployment for the backend: `kubectl apply -f backend-deployment.yaml`
        2. Create a service for the backend: `kubectl apply -f backend-service.yaml`
        3. Create a deployment for the frontend that references the backend service name (e.g., `http://backend-service`).
        4. Expose the frontend via a LoadBalancer: `kubectl expose deployment frontend --type=LoadBalancer --port=80`.

!!! note "Assignment.2: Serverless Scaling with Container Apps"
    Deploy a container app that scales to zero when there is no traffic and scales up based on HTTP request volume using a KEDA scaler.

    ??? tip "Solution: Serverless Scaling with Container Apps"
        1. Create a Container App environment.
        2. Deploy the app using `az containerapp create`.
        3. Set the min-replicas to 0 and max-replicas to 10.
        4. Configure the HTTP scaler to trigger based on concurrent requests.

## References

- [Azure Kubernetes Service Documentation](https://learn.microsoft.com/en-us/azure/aks/)
- [Azure Container Instances Documentation](https://learn.microsoft.com/en-us/azure/container-instances/)
- [Azure Container Registry Documentation](https://learn.microsoft.com/en-us/azure/container-registry/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)

## Self-Evaluation

??? note "What is the primary difference between Azure CNI and Kubenet?"
    Azure CNI assigns every pod an IP address from the Azure Virtual Network subnet, enabling direct VNet connectivity but consuming more IPs. Kubenet assigns pods IPs from a private range, conserving VNet IPs but requiring routing configuration for external communication.

??? note "When should a developer choose Azure Container Apps over AKS?"
    Azure Container Apps should be chosen for microservices that require serverless scaling (via KEDA), built-in Dapr integration, and minimal operational overhead, whereas AKS is appropriate for workloads requiring full Kubernetes API access and custom cluster configuration.

??? note "How does ACR geo-replication improve application performance?"
    Geo-replication copies container images to multiple Azure regions. This allows AKS clusters to pull images from the nearest regional registry, reducing image pull latency and ensuring availability if a specific region experiences an outage.
