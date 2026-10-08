# GCP Containers

!!! info "Learning Objectives"
    - Configure Google Kubernetes Engine (GKE) Standard and Autopilot clusters.
    - Deploy containerized applications to Cloud Run.
    - Manage container images and packages using Artifact Registry.
    - Implement networking and load balancing for GKE and Cloud Run workloads.
    - Evaluate the trade-offs between GKE, Cloud Run, and Compute Engine for containers.

## Overview

Google Cloud Platform (GCP) provides a tiered ecosystem for running containerized workloads, ranging from high-control infrastructure to fully managed serverless environments. The primary services include Google Kubernetes Engine (GKE) for complex orchestration, Cloud Run for request-driven serverless containers, and Artifact Registry for image lifecycle management.

| Service | Control | Operational Effort | Scaling | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **GKE Standard** | Maximum | High | Cluster-based | Complex AI clusters, Custom GPUs |
| **GKE Autopilot** | High | Low | Pod-based | Production K8s, Managed AI |
| **Cloud Run** | Low | Minimum | Request-based | LLM APIs, Orchestration |
| **Compute Engine** | Absolute | Maximum | Manual/MIG | Specialized hardware, Legacy AI |

The choice between these services depends on the required level of control over the underlying nodes, the scaling characteristics of the application, and the operational overhead the organization is willing to manage.

## Core Sections

### Google Kubernetes Engine (GKE)

GKE is a managed Kubernetes service that simplifies the deployment, management, and scaling of containerized applications. It offers two primary operational modes: Standard and Autopilot.

#### GKE Standard vs Autopilot

GKE Standard provides full control over the cluster infrastructure. Users manage the node pools, choose the machine types, and configure the node auto-scaling parameters. This mode is suitable for workloads requiring custom kernel modules, specific GPU configurations, or fine-grained control over node taints and tolerations.

GKE Autopilot is a fully managed experience where Google manages the entire cluster infrastructure, including the nodes. In Autopilot, the unit of billing is the pod (CPU, memory, and ephemeral storage) rather than the node. Autopilot automatically optimizes node provisioning and management, reducing operational overhead.

#### Regional vs Zonal Clusters

Zonal clusters distribute nodes across a single zone within a region. While they offer lower latency within that zone, they are susceptible to zonal outages.

Regional clusters distribute the control plane and nodes across multiple zones within a region. This architecture ensures high availability; if a single zone fails, the cluster continues to operate. Regional clusters are recommended for production workloads.

#### Node Auto-provisioning

Node auto-provisioning (NAP) extends the Cluster Autoscaler by automatically creating new node pools with the optimal machine type based on the resource requirements of pending pods. NAP analyzes the pods that cannot be scheduled and provisions nodes that fit those specific requirements, minimizing wasted resources.

Example command to create a GKE Autopilot cluster:

```bash
gcloud container clusters create-auto a-cluster \
    --region us-central1 \
    --project my-project-id
```

### Cloud Run

Cloud Run is a managed compute platform that enables the deployment of highly scalable containerized applications in a serverless environment. It is built on the Knative open-source standard, ensuring portability.

#### Request-Based Scaling

Cloud Run scales automatically based on the number of incoming requests. It can scale down to zero when no traffic is present, eliminating costs for idle resources. When requests arrive, Cloud Run rapidly provisions container instances to handle the load.

#### Configuration and Deployment

Cloud Run services are defined by the container image and the resource limits (CPU and memory). Traffic splitting allows for canary deployments by routing a percentage of traffic to a new revision.

Example command to deploy a container to Cloud Run:

```bash
gcloud run deploy my-service \
    --image gcr.io/my-project/my-app:v1 \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Artifact Registry

Artifact Registry is the evolution of Container Registry (GCR) and provides a centralized repository for managing container images and language packages (e.g., Maven, npm, Python).

#### Image Management and Versioning

Artifact Registry supports Docker V2 images and provides granular IAM permissions at the repository level. Versioning is handled through tags and digests, allowing teams to promote images through different environments (e.g., dev, staging, prod).

#### Vulnerability Scanning

Artifact Registry integrates with the Container Analysis API to provide automatic vulnerability scanning. When an image is pushed, GCP scans the OS packages for known vulnerabilities (CVEs) and provides a detailed report.

Example command to create an Artifact Registry repository:

```bash
gcloud artifacts repositories create my-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for my-app"
```

### Compute Engine for Containers

While GKE and Cloud Run are the primary container services, GCP allows running containers directly on Compute Engine (GCE) virtual machines. This is achieved by specifying a container image during VM creation.

This approach is suitable for:
- Applications that require a single, large VM with specialized hardware.
- Legacy applications that cannot be easily orchestrated by Kubernetes.
- Scenarios where the overhead of a container orchestrator is unnecessary.

Example command to launch a VM with a container:

```bash
gcloud compute instances create container-vm \
    --container-image gcr.io/google-samples/hello-app:1.0 \
    --zone us-central1-a
```

## Containers for AI Workloads

In the context of AI and Machine Learning, containers provide the necessary isolation for complex dependency stacks (CUDA, PyTorch, TensorFlow).

### Accelerated Computing (GPUs & TPUs)
For AI training and high-performance inference, GKE supports accelerated node pools. Users can provision nodes with NVIDIA GPUs or Google TPUs. GKE Autopilot now simplifies this by allowing GPU requests directly in the pod specification, eliminating the need to manage the underlying GPU node pool manually.

### Integration with Vertex AI
Vertex AI, GCP's unified AI platform, leverages containers for its **Prediction** service. When deploying a custom model, Vertex AI requires a Docker image containing the model server (e.g., FastAPI, NVIDIA Triton). This allows data scientists to package their specific model version and environment into a container that Vertex AI then manages, scales, and endpoints.

### Serverless AI Orchestration
Cloud Run is an ideal choice for "LLM Orchestrators"—applications that use frameworks like LangChain or LlamaIndex to coordinate calls between multiple LLM APIs. Because these orchestrators are often I/O bound (waiting for API responses), the request-based scaling of Cloud Run is highly cost-effective.

## AI Container Lifecycle

The path from model development to production follows a structured CI/CD pipeline:

1.  **Development**: Model and API code are developed in a containerized environment (e.g., Dev Container).
2.  **Build**: **Cloud Build** triggers on a git commit, building the Docker image.
3.  **Store**: The image is pushed to **Artifact Registry**, where it is scanned for vulnerabilities.
4.  **Deploy**: The image is pulled into **GKE** (for heavy workloads) or **Cloud Run** (for APIs) via a deployment pipeline.

*Tip: For AI workloads, use "Slim" base images to reduce the image size, which significantly decreases the "cold start" time for Cloud Run services.*

## Networking

Networking for containers in GCP revolves around the Virtual Private Cloud (VPC) and Cloud Load Balancing.

#### VPC-Native Clusters

GKE clusters are recommended to be VPC-native. This uses Alias IP ranges to assign IP addresses to pods from the VPC subnet, allowing pods to be natively routable within the VPC without requiring a separate route table for each node.

#### Cloud Load Balancing and Ingress

For GKE, the GKE Ingress controller integrates with Google Cloud Load Balancing (GCLB). It creates a Global External HTTP(S) Load Balancer that routes traffic to Kubernetes services.

For Cloud Run, a built-in load balancer is provided automatically, though users can configure a Global External HTTP(S) Load Balancer for custom domains and advanced routing.

Example YAML for a GKE Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    kubernetes.io/ingress.class: "gce"
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

## Summary Checklist

- [ ] Enable GKE VPC-native clusters for improved networking and scalability.
- [ ] Select GKE Autopilot for reduced operational overhead or GKE Standard for full node control.
- [ ] Configure regional clusters for production high availability.
- [ ] Use Artifact Registry instead of GCR for granular IAM and multi-format support.
- [ ] Enable automatic vulnerability scanning in Artifact Registry.
- [ ] Configure Cloud Run concurrency settings to optimize resource utilization.
- [ ] Implement L7 Cloud Load Balancing for complex routing and SSL termination.
- [ ] Provision GPU/TPU node pools in GKE for accelerated AI workloads.
- [ ] Integrate Cloud Build for automated container pipelines from Git to Artifact Registry.

## Assignments

!!! note "Assignment.1: Deploy to Cloud Run"
    Deploy a simple Nginx container to Cloud Run and make it publicly accessible.

    ??? tip "Solution: Deploy to Cloud Run"
        1. Pull and tag a public image or use a pre-existing one.
        2. Run the following command:
        ```bash
        gcloud run deploy nginx-app --image nginx --platform managed --region us-central1 --allow-unauthenticated
        ```
        3. Verify the deployment using the provided URL.

!!! note "Assignment.2: GKE Autopilot Deployment"
    Create a GKE Autopilot cluster and deploy a sample pod using a YAML manifest.

    ??? tip "Solution: GKE Autopilot Deployment"
        1. Create the cluster:
        ```bash
        gcloud container clusters create-auto autopilot-cluster --region us-central1
        ```
        2. Get credentials:
        ```bash
        gcloud container clusters get-credentials autopilot-cluster --region us-central1
        ```
        3. Apply a manifest:
        ```yaml
        apiVersion: v1
        kind: Pod
        metadata:
          name: hello-pod
        spec:
          containers:
          - name: hello-app
            image: us-docker.pkg.dev/google-samples/containers/gke/hello-app:1.0
        ```
        ```bash
        kubectl apply -f pod.yaml
        ```

!!! note "Assignment.3: Artifact Registry Lifecycle"
    Create a Docker repository in Artifact Registry, push a local image, and verify the vulnerability scan.

    ??? tip "Solution: Artifact Registry Lifecycle"
        1. Create the repo:
        ```bash
        gcloud artifacts repositories create my-images --repository-format=docker --location=us-central1
        ```
        2. Configure Docker:
        ```bash
        gcloud auth configure-docker us-central1-docker.pkg.dev
        ```
        3. Tag and push:
        ```bash
        docker tag my-app:latest us-central1-docker.pkg.dev/my-project/my-images/my-app:v1
        docker push us-central1-docker.pkg.dev/my-project/my-images/my-app:v1
        ```
        4. Check the GCP Console under Artifact Registry -> my-images -> my-app:v1 to view the vulnerability report.

## References

- [Google Kubernetes Engine Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [VPC Networking for GKE](https://cloud.google.com/kubernetes-engine/docs/concepts/vpc-native-clusters)

## Self-Evaluation

??? note "What are the primary differences between GKE Standard and GKE Autopilot?"
    GKE Standard provides full control over the nodes, including machine type and node pool configuration, and bills based on the nodes provisioned. GKE Autopilot manages the entire infrastructure, including node provisioning and scaling, and bills based on the resource requests of the pods.

??? note "How does Cloud Run handle scaling and cost for infrequent workloads?"
    Cloud Run uses request-based scaling, which allows it to scale down to zero instances when there is no incoming traffic. This eliminates costs during idle periods, as users only pay for the resources consumed while processing requests.

??? note "Why is it recommended to use VPC-native clusters in GKE?"
    VPC-native clusters use Alias IP ranges, which make pod IPs natively routable within the VPC. This eliminates the need for complex route table management, improves scalability, and allows for easier integration with other VPC resources.

??? note "When should you use GKE instead of Cloud Run for an AI application?"
    GKE is preferred for long-running training jobs, complex inference pipelines requiring specialized GPU/TPU configurations, or applications needing low-latency inter-pod communication. Cloud Run is ideal for request-driven AI APIs or lightweight LLM orchestration (e.g., LangChain wrappers).

??? note "How does Vertex AI leverage containers for model serving?"
    Vertex AI Prediction allows users to deploy custom Docker images that contain the model and a serving engine (like FastAPI or Triton). Vertex AI then manages the container's deployment, scaling, and endpoint creation, providing a managed way to serve custom models.
