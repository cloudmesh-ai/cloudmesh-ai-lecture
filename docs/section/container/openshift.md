---
title: "OpenShift for AI: Enterprise Kubernetes & Managed AI Workloads"
---

## Learning Objectives

!!! info "Learning Objectives"
    - Define Red Hat OpenShift and explain its relationship to upstream Kubernetes.
    - Contrast core OpenShift concepts (Routes, ImageStreams, SCCs) with standard K8s equivalents.
    - Implement the Source-to-Image (S2I) workflow for deploying AI applications directly from source.
    - Configure Security Context Constraints (SCCs) to enable GPU-accelerated workloads.
    - Explore Red Hat OpenShift AI (RHOAI) for integrated model development and serving.

## Overview

OpenShift is an enterprise-grade distribution of Kubernetes. While Kubernetes provides the core orchestration engine, OpenShift provides a complete, opinionated platform that adds critical layers for security, developer experience, and operational stability.

Think of Kubernetes as the **engine** of a car—powerful and flexible, but requiring you to build the chassis, install the seats, and wire the dashboard yourself. OpenShift is the **complete vehicle**: it comes with the engine pre-installed, along with a built-in registry, integrated monitoring, a developer-centric console, and automated CI/CD pipelines.

### Why "Opinionated" Kubernetes?

Enterprises prefer OpenShift because it reduces the "day two" operational burden. Instead of spending months integrating different tools for logging, monitoring, and security, OpenShift provides a curated stack that is tested and supported by Red Hat, ensuring that security patches and updates are applied consistently across the cluster.

## Core Sections

### 1. Architecture & Tooling

OpenShift maintains the same basic architecture as Kubernetes (Control Plane and Worker Nodes) but introduces several enhancements to simplify management.

#### The `oc` CLI

The primary tool for interacting with OpenShift is the `oc` command-line interface. It is important to understand that **`oc` is a superset of `kubectl`**. 

Almost every command you know from Kubernetes works in OpenShift. For example, `oc get pods` is functionally identical to `kubectl get pods`. However, `oc` adds specific commands for OpenShift-exclusive features, such as `oc new-app` for S2I deployments or `oc expose` for creating Routes.

#### The Web Console

While the CLI is powerful, OpenShift's Web Console is a first-class citizen. It provides two distinct perspectives:
- **Administrator Perspective**: For managing cluster health, nodes, quotas, and Security Context Constraints (SCCs).
- **Developer Perspective**: A simplified view for deploying applications, managing builds, and monitoring pod logs without needing to write complex YAML manifests.

### 2. The "Enterprise Gap": Kubernetes vs. OpenShift

To transition from vanilla Kubernetes to OpenShift, you must understand a few key architectural shifts.

| Feature | Vanilla Kubernetes | Red Hat OpenShift | AI Impact |
| :--- | :--- | :--- | :--- |
| **Networking** | Ingress (Generic) | Routes (Built-in/Simplified) | Easier external access to AI APIs and Dashboards |
| **Image Mgmt** | External Registry | Integrated ImageStreams | Automated triggers when model images are updated |
| **Security** | RBAC / Pod Security | Security Context Constraints (SCC) | Strict, granular control over GPU device access |
| **Isolation** | Namespaces | Projects (Namespace + Metadata) | Better multi-tenant research isolation and quotas |
| **Deployment** | YAML Manifests | S2I (Source-to-Image) | Deploy AI code from Git without writing Dockerfiles |

![K8s vs OpenShift](images/k8s-vs-openshift-chatgpt.png)

Figure 1: Comparison of the Kubernetes core and the OpenShift Enterprise wrap.

### 3. Operational Workflows for AI

#### Source-to-Image (S2I)

One of OpenShift's most useful features is **Source-to-Image (S2I)**. In standard Kubernetes, a developer must write a Dockerfile, build the image, push it to a registry, and then update a YAML manifest. S2I automates this entire chain.

**The S2I Flow**: `Git Repository` $\rightarrow$ `Builder Image` $\rightarrow$ `Application Image` $\rightarrow$ `Deployment`.

Example: Deploying a FastAPI LLM wrapper:

```bash
# Create a new application directly from a GitHub repo using the python-3.9 builder
oc new-app python:3.9~https://github.com/user/llm-wrapper.git
```

OpenShift detects the language, pulls the appropriate builder image, injects your code, and deploys the pod—all in one step.

![S2I Workflow](images/s2i-workflow-chatgpt.png)

Figure 2: The Source-to-Image (S2I) process.

#### Managing External Access with Routes

In Kubernetes, you define an Ingress object. In OpenShift, you use **Routes**. A Route is essentially a managed Ingress that automatically integrates with the OpenShift built-in HAProxy router to provide a DNS-addressable URL.

```bash
# Expose a service as a route
oc expose svc llm-wrapper-service
```

#### Security Context Constraints (SCC)

OpenShift is secure by default. By default, pods cannot run as the root user or access host devices. This is a challenge for AI workloads that need direct access to NVIDIA GPUs.

To resolve this, you must assign a specific **Security Context Constraint (SCC)** to the ServiceAccount running the AI pod. For GPU workloads, the `privileged` or `anyuid` SCC is often required:

```bash
# Allow the 'default' service account in the 'ai-project' to run as any user
oc adm policy add-scc-to-user anyuid -z default -n ai-project
```

!!! warning "Security Risk"
    Assigning the `privileged` SCC grants the pod nearly full access to the host node. This should only be used for trusted GPU operators and strictly managed workloads.

### 4. AI Integration: Red Hat OpenShift AI (RHOAI)

For data scientists, OpenShift provides a specialized layer called **Red Hat OpenShift AI (RHOAI)**. This transforms the cluster from a general-purpose orchestrator into a full-stack AI platform.

#### Integrated Environments

RHOAI provides a managed **JupyterHub** experience. Instead of manually deploying notebooks, users can launch "Workbench" instances with pre-installed PyTorch, TensorFlow, and Scikit-learn images, mapped to persistent storage.

#### The GPU Operator

Installing NVIDIA drivers on a Kubernetes cluster is often difficult. OpenShift uses the **NVIDIA GPU Operator**, which automates the entire lifecycle:
1. Detecting the GPU hardware on the node.
2. Installing the correct NVIDIA drivers.
3. Deploying the NVIDIA Container Toolkit.
4. Exposing the GPUs as schedulable resources for pods.

#### Model Serving

RHOAI integrates with **KServe** and **vLLM**, allowing users to deploy large language models as scalable services with built-in canary deployments and auto-scaling.

## Summary Checklist

- [ ] Define the difference between Kubernetes and OpenShift.
- [ ] Use the `oc` CLI to manage resources.
- [ ] Deploy an application using the S2I workflow.
- [ ] Create an OpenShift Route for external access.
- [ ] Configure an SCC to allow GPU access for a pod.
- [ ] Understand the role of RHOAI and the GPU Operator in AI workflows.

## Assignments

!!! note "Assignment 1: The S2I Challenge"
    Deploy a simple Python AI-greeting app using a Git URL and the official Python S2I builder. Verify the app is running in the developer console.

!!! note "Assignment 2: The Route Mission"
    Expose your application to the internet using an OpenShift Route (`oc expose`). Share the generated URL and verify connectivity.

!!! note "Assignment 3: The Security Puzzle"
    Attempt to launch a pod that requires root privileges (or GPU access). Observe the `CrashLoopBackOff` or permission error, then fix it by assigning the `anyuid` SCC to the ServiceAccount.

## References

- [Red Hat OpenShift Documentation](https://docs.openshift.com/)
- [OpenShift AI (RHOAI) Documentation](https://docs.openshift.com/container-platform/latest/openai/index.html)

## Self-Assessment
Test your knowledge by expanding the questions below.
??? note "If I am already familiar with `kubectl`, do I need to learn a new tool for OpenShift?"
    No. The `oc` CLI is a superset of `kubectl`. Almost every `kubectl` command works exactly the same way when typed as `oc`.

??? note "What is the primary advantage of an ImageStream over a standard Docker image reference?"
    ImageStreams allow for "triggers." When a new image is pushed to a stream, OpenShift can automatically trigger a new build or a redeployment of the application, enabling a true GitOps workflow.

??? note "Why would an AI researcher prefer 'Projects' over standard Kubernetes 'Namespaces'?"
    While a Project is technically a Namespace, it adds a layer of administrative metadata, including integrated quotas, user access control, and a simplified view in the Web Console, making it easier to manage multi-tenant research environments.
