# OpenShift for AI: Enterprise Kubernetes & Managed AI Workloads

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Define Red Hat OpenShift and explain its relationship to upstream Kubernetes.
    - Contrast core OpenShift concepts (Routes, ImageStreams, SCCs) with standard K8s equivalents.
    - Implement the Source-to-Image (S2I) workflow for deploying AI applications directly from source.
    - Configure Security Context Constraints (SCCs) to enable GPU-accelerated workloads.
    - Explore Red Hat OpenShift AI (RHOAI) for integrated model development and serving.

## Overview

OpenShift is an enterprise-grade distribution of Kubernetes. While Kubernetes provides the core orchestration engine, OpenShift provides a complete, opinionated platform that adds critical layers for security, developer experience, and operational stability.

Think of Kubernetes as the **engine** of a car—flexible and versatile, but requiring you to build the chassis, install the seats, and wire the dashboard yourself. OpenShift is the **complete vehicle**: it comes with the engine pre-installed, along with a built-in registry, integrated monitoring, a developer-centric console, and automated CI/CD pipelines.

Enterprises prefer OpenShift because it reduces the "day two" operational burden. Instead of spending months integrating different tools for logging, monitoring, and security, OpenShift provides a curated stack that is tested and supported by Red Hat, ensuring that security patches and updates are applied consistently across the cluster.

## Core Sections

### Architecture & Tooling

OpenShift maintains the same basic architecture as Kubernetes (Control Plane and Worker Nodes) but introduces several enhancements to simplify management.

#### The `oc` CLI

The primary tool for interacting with OpenShift is the `oc` command-line interface. It is important to understand that **`oc` is a superset of `kubectl`**. 

Almost every command you know from Kubernetes works in OpenShift. For example, `oc get pods` is functionally identical to `kubectl get pods`. However, `oc` adds specific commands for OpenShift-exclusive features, such as `oc new-app` for S2I deployments or `oc expose` for creating Routes.

#### The Web Console

While the CLI is effective, OpenShift's Web Console is a first-class citizen. It provides two distinct perspectives:

- **Administrator Perspective**: For managing cluster health, nodes, quotas, and Security Context Constraints (SCCs).
- **Developer Perspective**: A simplified view for deploying applications, managing builds, and monitoring pod logs without needing to write complex YAML manifests.

### The "Enterprise Gap": Kubernetes vs. OpenShift

To transition from vanilla Kubernetes to OpenShift, you must understand a few key architectural shifts.

| Feature | Vanilla Kubernetes | Red Hat OpenShift | AI Impact |
| :--- | :--- | :--- | :--- |
| **Networking** | Ingress (Generic) | Routes (Built-in/Simplified) | Easier external access to AI APIs and Dashboards |
| **Image Mgmt** | External Registry | Integrated ImageStreams | Automated triggers when model images are updated |
| **Security** | RBAC / Pod Security | Security Context Constraints (SCC) | Strict, granular control over GPU device access |
| **Isolation** | Namespaces | Projects (Namespace + Metadata) | Better multi-tenant research isolation and quotas |
| **Deployment** | YAML Manifests | S2I (Source-to-Image) | Deploy AI code from Git without writing Dockerfiles |

![Kubernetes vs OpenShift](images/openshift-comparison.png)

Figure 1: Comparison of the Kubernetes core and the OpenShift Enterprise wrap.

### Operational Workflows for AI

#### Source-to-Image (S2I)

One of OpenShift's most useful features is **Source-to-Image (S2I)**. In standard Kubernetes, a developer must write a Dockerfile, build the image, push it to a registry, and then update a YAML manifest. S2I automates this entire chain.

**The S2I Flow**: `Git Repository` $\rightarrow$ `Builder Image` $\rightarrow$ `Application Image` $\rightarrow$ `Deployment`.

Example: Deploying a FastAPI LLM wrapper:

```bash
# Create a new application directly from a GitHub repo using the python-3.9 builder
oc new-app python:3.9~https://github.com/user/llm-wrapper.git
```

##### Concrete Example: HuggingFace Sentiment Analysis

To make the S2I concept tangible, consider deploying a simple sentiment analysis API using a pre-trained HuggingFace model.

**Project Structure**
The Git repository (`hf-sentiment-app`) should be organized as follows:
```text
/hf-sentiment-app
├── app.py
└── requirements.txt
```

**Sample Code**
`app.py` implements a FastAPI endpoint that leverages the `transformers` pipeline:

```python
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()
# Load the sentiment-analysis pipeline (defaults to distilbert-base-uncased-finetuned-sst-2-english)
classifier = pipeline("sentiment-analysis")

@app.get("/predict")
async def predict(text: str):
    result = classifier(text)[0]
    return {"text": text, "label": result['label'], "score": result['score']}
```

`requirements.txt` specifies the necessary AI libraries:
```text
transformers
torch
fastapi
uvicorn
```

**Deployment Command**
You can deploy this entire stack from source with a single command:
```bash
oc new-app python:3.11~https://github.com/your-username/hf-sentiment-app.git
```

**Workflow Breakdown**
When this command is executed, OpenShift performs the following steps:
1. **Builder Image**: OpenShift pulls the official `python:3.11` S2I builder image.
2. **Source Code**: It clones the `hf-sentiment-app` repository into a temporary volume.
3. **Assemble**: The builder image runs a script that installs the dependencies from `requirements.txt` and copies the `app.py` into the final image.
4. **Application Image**: A new, immutable container image is pushed to the internal OpenShift registry.
5. **Pod**: OpenShift creates a Deployment and a Pod based on this new image.

OpenShift detects the language, pulls the appropriate builder image, injects your code, and deploys the pod—all in one step.

![S2I Process](images/s2i-process.png)

Figure 2: The Source-to-Image (S2I) process.

#### Managing External Access with Routes

In Kubernetes, you define an Ingress object. In OpenShift, you use **Routes**. A Route is essentially a managed Ingress that automatically integrates with the OpenShift built-in HAProxy router to provide a DNS-addressable URL.

```bash
# Expose a service as a route
oc expose svc llm-wrapper-service
```

#### Security Context Constraints (SCC)

OpenShift is secure by default. By default, pods cannot run as the root user or access host devices. This is a challenge for AI workloads that need direct access to NVIDIA GPUs.

To resolve this, you must assign a specific **Security Context Constraints (SCC)** to the ServiceAccount running the AI pod. For GPU workloads, the `privileged` or `anyuid` SCC is often required:

```bash
# Allow the 'default' service account in the 'ai-project' to run as any user
oc adm policy add-scc-to-user anyuid -z default -n ai-project
```

!!! warning "Security Risk"
    Assigning the `privileged` SCC grants the pod nearly full access to the host node. This should only be used for trusted GPU operators and strictly managed workloads.

### Enterprise AI Architecture: RHOAI and the GPU Stack

For data scientists, OpenShift provides a specialized layer called **Red Hat OpenShift AI (RHOAI)**. This transforms the cluster from a general-purpose orchestrator into a full-stack AI platform.

#### The RHOAI Ecosystem
RHOAI integrates several industry-standard tools into a unified control plane:
- **Integrated Workbench**: A managed **JupyterHub** experience. Instead of manually deploying notebooks, users can launch "Workbench" instances with pre-installed PyTorch or TensorFlow images, mapped to persistent storage via PVCs.
- **KServe (Model Serving)**: Provides a standardized way to deploy models as serverless inference services. KServe handles "Scale-to-Zero" (reducing costs when the model isn't used) and Canary rollouts (sending 10% of traffic to a new model version).
- **vLLM Integration**: RHOAI leverages vLLM for high-throughput LLM serving, integrating it directly into the KServe pipeline for optimized PagedAttention memory management.

#### The GPU Operator: Automating the Hardware Layer
Installing NVIDIA drivers on a Kubernetes cluster is often difficult. OpenShift uses the **NVIDIA GPU Operator**, which automates the entire lifecycle via a reconciliation loop:
1. **Detection**: Identifies the GPU hardware on the node.
2. **Driver Installation**: Deploys the correct NVIDIA drivers as a container.
3. **Toolkit Setup**: Installs the NVIDIA Container Toolkit to allow containers to "see" the GPU.
4. **Resource Exposure**: Configures the device plugin so that `nvidia.com/gpu` becomes a schedulable resource for pods.

---

### Governance & Multi-tenancy in AI Clusters

In academic or corporate research environments, GPU clusters are shared assets. Without strict governance, a single "greedy" training job can starve all other researchers of resources.

#### ResourceQuotas and LimitRanges
OpenShift uses these two primitives to enforce fairness:
- **ResourceQuotas**: Set a hard limit on the *total* resources a project can consume (e.g., "Project-A can use a maximum of 4 GPUs and 128Gi of RAM"). If a user tries to launch a 5th GPU pod, OpenShift will reject the request.
- **LimitRanges**: Set constraints on *individual* pods (e.g., "No single pod may request more than 2 GPUs"). This prevents a single user from claiming all the quota for one massive pod.

#### Project Isolation vs. Namespace Isolation
While a **Project** is technically a Kubernetes Namespace, it adds critical enterprise metadata:
- **Self-Service Provisioning**: Users can request a Project via the console, which triggers an approval workflow.
- **Auditability**: Every action within a Project is logged with the user's identity, which is essential for compliance in regulated industries (e.g., healthcare AI).
- **Integrated Quotas**: Quotas are tied to the Project, not the user, allowing a team to share a pool of GPUs.

---

- [ ] Define the difference between Kubernetes and OpenShift.
- [ ] Use the `oc` CLI to manage resources.
- [ ] Deploy an application using the S2I workflow.
- [ ] Create an OpenShift Route for external access.
- [ ] Configure an SCC to allow GPU access for a pod.
- [ ] Understand the role of RHOAI and the GPU Operator in AI workflows.

## Assignments

!!! note "Assignment.1: The S2I Challenge"
    Deploy a simple Python AI-greeting app using a Git URL and the official Python S2I builder. Verify the app is running in the developer console.
    
    ??? tip "Solution: S2I Deployment"
        Use `oc new-app python:3.9~<your-git-url>`. Check the build status with `oc get builds` and the deployment status with `oc get pods`.

!!! note "Assignment.2: The Route Mission"
    Expose your application to the internet using an OpenShift Route (`oc expose`). Share the generated URL and verify connectivity.
    
    ??? tip "Solution: Route Exposure"
        Run `oc expose svc <service-name>`. Use `oc get routes` to find the generated external URL.

!!! note "Assignment.3: The Security Puzzle"
    Attempt to launch a pod that requires root privileges (or GPU access). Observe the `CrashLoopBackOff` or permission error, then fix it by assigning the `anyuid` SCC to the ServiceAccount.
    
    ??? tip "Solution: SCC Configuration"
        Run `oc adm policy add-scc-to-user anyuid -z default -n <your-project>`. Redeploy the pod and verify it now starts successfully.

!!! note "Assignment.4: Governance Implementation"
    Create a new OpenShift Project. Apply a `ResourceQuota` that limits the project to a maximum of 2 GPUs. Attempt to deploy 3 GPU-enabled pods and observe the API error. Then, implement a `LimitRange` to ensure no single pod requests more than 1 GPU.
    
    ??? tip "Solution: Governance"
        Use `oc create quota gpu-quota --limits.nvidia.com/gpu=2`. Use `oc create limitrange gpu-limit --limits.nvidia.com/gpu=1`.

## References

- Red Hat OpenShift Documentation: [docs.openshift.com](https://docs.openshift.com/)
- OpenShift AI (RHOAI) Documentation: [docs.openshift.com/container-platform/latest/openai/index.html](https://docs.openshift.com/container-platform/latest/openai/index.html)

## Self-Evaluation

??? note "If I am already familiar with `kubectl`, do I need to learn a new tool for OpenShift?"
    No. The `oc` CLI is a superset of `kubectl`. Almost every `kubectl` command works exactly the same way when typed as `oc`.

??? note "What is the primary advantage of an ImageStream over a standard Docker image reference?"
    ImageStreams allow for "triggers." When a new image is pushed to a stream, OpenShift can automatically trigger a new build or a redeployment of the application, enabling a true GitOps workflow.

??? note "Why would an AI researcher prefer 'Projects' over standard Kubernetes 'Namespaces'?"
    While a Project is technically a Namespace, it adds a layer of administrative metadata, including integrated quotas, user access control, and a simplified view in the Web Console, making it easier to manage multi-tenant research environments.
