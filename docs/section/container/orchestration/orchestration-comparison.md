# Orchestration Comparison: Kubernetes, Docker Swarm, and OpenShift

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Understand the fundamental differences between a basic orchestrator (Swarm) and a full-scale platform (OpenShift).
    - Analyze the trade-offs between the flexibility of "vanilla" Kubernetes and the opinionated nature of OpenShift.
    - Identify the specific technical and organizational triggers that justify moving from Swarm to Kubernetes.
    - Apply a structured decision framework to select the right orchestration tool for a given business requirement.

## Overview

Running a single container is simple. Running a thousand containers across fifty servers, while ensuring they can communicate, recover from hardware failure, and scale automatically based on traffic, is a complex engineering problem.

Container orchestration solves four primary challenges:

- **Scheduling**: Deciding which server has enough resources to run a new container.
- **Self-Healing**: Detecting when a container crashes or a node dies and restarting the workload elsewhere.
- **Service Discovery & Load Balancing**: Ensuring that traffic reaches the correct container, even as containers are moved or scaled.
- **Declarative State**: Allowing developers to describe the *desired* state (e.g., "I want 5 replicas of the API") and letting the system work to maintain that state.

## Implementation

### Docker Swarm: The Path of Least Resistance

Docker Swarm is Docker's native orchestration tool. It is built into the Docker Engine, meaning if you have Docker installed, you already have Swarm.

#### Philosophy: Simplicity First

Swarm is designed for teams that want the benefits of orchestration without the "operational tax" of Kubernetes. It uses the same CLI and Compose file format that developers already use locally.

#### Analysis of Docker Swarm

- **Strengths**: Zero-config setup (`docker swarm init`), low cognitive load, fast deployment, and very low resource overhead on nodes.
- **Weaknesses**: Limited flexibility in scheduling, basic networking (lacks advanced Canary or Blue/Green patterns), and a smaller ecosystem of third-party plugins compared to K8s.

### Kubernetes (K8s): The Industry Standard

**[Kubernetes](/section/container/orchestration/kubernetes.md)** is a highly extensible, open-source system designed for massive scale and extreme flexibility. It acts as a framework for building platforms rather than a finished product.

#### Philosophy: Power and Extensibility

Kubernetes provides the core primitives (Pods, Services, ConfigMaps, Secrets), allowing operators to assemble a custom environment tailored to their specific needs.

#### Analysis of Kubernetes

- **Strengths**: Extreme scalability, a vast CNCF ecosystem (Prometheus, Istio, ArgoCD), advanced self-healing via Liveness/Readiness probes, and complete cloud agnosticism.
- **Weaknesses**: A steep learning curve (the "Complexity Tax"), high operational overhead for vanilla installations, and a tendency toward "YAML overload."

### Red Hat OpenShift: The Enterprise Platform

**[OpenShift](/section/container/orchestration/openshift.md)** is a distribution of Kubernetes. It is "Kubernetes with a battery-included enterprise wrapper," providing a complete vehicle rather than just the engine.

#### Philosophy: Developer Experience and Security

OpenShift adds an integrated developer console, built-in CI/CD pipelines (Tekton), an integrated image registry, and a strict security model to reduce the "day two" operational burden.

#### Analysis of OpenShift

- **Strengths**: Integrated developer workflows (Source-to-Image), hardened security by default (SCCs), unified management via a highly effective web console, and official Red Hat enterprise support.
- **Weaknesses**: Opinionated and restrictive security defaults, potential vendor lock-in due to OpenShift-specific features (e.g., Routes), and significant licensing costs.

### Feature Comparison Matrix

| Feature | Docker Swarm | Kubernetes (Vanilla) | Red Hat OpenShift |
| :--- | :--- | :--- | :--- |
| **Installation** | Trivial (`swarm init`) | Complex (on-prem) / Easy (managed) | Managed / Complex (on-prem) |
| **Learning Curve** | Low | High | Medium (Console) / High (CLI) |
| **Scaling** | Fast, but basic | Advanced, Policy-driven | Advanced, Policy-driven |
| **Security** | Basic (Docker Secrets) | Strong (RBAC, NetworkPolicies) | Extremely Strong (SCCs, RBAC) |
| **CI/CD** | External | External / GitOps | Integrated (Tekton) |
| **Image Registry** | External | External | Integrated |
| **Networking** | Overlay / Ingress | CNI (Calico, Flannel, etc.) | Integrated (OVN-Kubernetes) |
| **Developer UX** | CLI-centric | CLI-centric | Console + CLI |
| **Target Audience** | Small teams, simple apps | DevOps teams, large scale | Enterprises, regulated industries |

### The Decision Framework: An Engineering Approach

Choosing an orchestrator is a balance between **Operational Effort** and **Required Capability**. Instead of a simple flowchart, production teams use a weighted decision matrix to quantify the trade-offs.

#### Weighted Decision Matrix
Assign a weight (1-5) to each criteria based on your project's priority, then score each tool (1-10).

| Criteria | Weight | Docker Swarm | K8s (Vanilla) | OpenShift |
| :--- | :---: | :---: | :---: | :---: |
| **Time to First Deploy** | 5 | 10 | 4 | 6 |
| **Resource Efficiency** | 3 | 9 | 7 | 5 |
| **Security Compliance** | 4 | 3 | 7 | 10 |
| **Ecosystem/Plugins** | 4 | 4 | 10 | 8 |
| **Operational Overhead** | 5 | 10 | 3 | 6 |
| **Weighted Total** | -- | **High** | **Medium** | **Medium-High** |

#### Decision Workflow
1. **Is this a small project, a prototype, or a set of internal tools?**
   - $\rightarrow$ **Choose Docker Swarm**. The speed of deployment outweighs the need for advanced scaling.
2. **Do you need to run at a massive scale (100+ nodes) or require extreme cloud-portability?**
   - $\rightarrow$ **Choose Kubernetes**. It is the only tool with the ecosystem to support this scale.
3. **Are you in a highly regulated industry with strict security compliance requirements?**
   - $\rightarrow$ **Choose OpenShift**. The built-in security constraints and enterprise support provide the necessary auditability.
4. **Do you have a large team of developers who need a "Push-to-Deploy" experience without K8s expertise?**
   - $\rightarrow$ **Choose OpenShift**. The S2I and Developer Console drastically reduce onboarding friction.

!!! info "Automating the Transition"
    Regardless of the orchestrator you choose, the goal is to remove manual intervention. To learn how to bridge the gap between your container images and these orchestration platforms using automated pipelines, refer to **[Bridging Containers and CI/CD](../security/containers-in-pipeline.md)**.

### Emerging Trends in AI Orchestration

As AI models grow and the need for efficient inference increases, the orchestration landscape is evolving beyond the "Always-On" pod model.

#### Serverless AI and Knative
**Knative** is a Kubernetes-based platform that brings serverless capabilities to containerized workloads. For AI, this enables **Scale-to-Zero**:
- When no inference requests are coming in, the LLM pod is terminated to save expensive GPU resources.
- When a request arrives, Knative rapidly spins up a pod to handle the request.
- This is critical for "bursty" AI workloads where GPUs would otherwise sit idle 90% of the time.

#### Edge Orchestration with K3s
Deploying LLMs on the edge (e.g., in a factory or on a mobile gateway) requires a smaller footprint than standard K8s. **K3s** is a lightweight, certified Kubernetes distribution optimized for ARM and low-resource environments.
- **Edge AI**: K3s allows you to deploy "small" LLMs (e.g., Phi-3 or Llama-3-8B) directly on edge hardware, reducing latency and ensuring privacy by keeping data on-site.

---

#### Summary Matrix

| If you value... | Use... | Why? |
| :--- | :--- | :--- |
| **Speed of Setup** | **Docker Swarm** | Get running in minutes. |
| **Flexibility & Ecosystem** | **Kubernetes** | Every cloud tool is built for K8s. |
| **Security & Support** | **OpenShift** | Enterprise hardening and official support. |
| **Lowest Overhead** | **Docker Swarm** | Minimum CPU/RAM wasted on the orchestrator. |
| **Developer Velocity** | **OpenShift** | Integrated tools from code to cluster. |

### References

- Kubernetes Documentation: [kubernetes.io/docs](https://kubernetes.io/docs/)
- Docker Swarm Documentation: [docs.docker.com/engine/swarm/](https://docs.docker.com/engine/swarm/)
- Red Hat OpenShift Documentation: [docs.openshift.com](https://docs.openshift.com/)

## Self-Evaluation

??? question "Why is OpenShift described as a 'distribution' of Kubernetes rather than an alternative?"
    Because OpenShift uses the Kubernetes API and core components as its engine. Everything you can do in Kubernetes, you can do in OpenShift. OpenShift simply adds additional layers—such as a web console, an integrated registry, and security policies—on top of that core.

??? question "What is the 'Complexity Tax' associated with Kubernetes?"
    The complexity tax refers to the significant amount of time and expertise required to set up and maintain a Kubernetes cluster. This includes managing the control plane, configuring the CNI, and handling storage via CSI. For small projects, this effort can exceed the value provided by the orchestrator.

??? question "In what specific scenario would Docker Swarm be a better choice than Kubernetes?"
    For a small team deploying a few microservices to a small number of nodes where the primary goal is simplicity and rapid iteration. If the team does not need advanced autoscaling or a massive ecosystem of plugins, Swarm is more efficient.

??? question "How does OpenShift's approach to security differ from vanilla Kubernetes?"
    Vanilla Kubernetes allows containers to run as root by default. OpenShift implements **Security Context Constraints (SCCs)**, which forbid containers from running as root by default and enforce strict rules on host system access.

## Assignments

!!! note "Assignment.1: The Orchestration Audit"
    Review a hypothetical project: A small team of 3 developers building a internal tool for 50 users. They have limited DevOps experience. Which orchestrator do you recommend and why?
    
    ??? tip "Solution: Orchestration Audit"
        **Recommendation: Docker Swarm**. Given the small team size, low user count, and limited DevOps expertise, the operational simplicity of Swarm outweighs the advanced features of K8s. It allows them to focus on the application rather than the infrastructure.

!!! note "Assignment.2: Migration Mapping"
    Map out the steps required to move a service from Docker Swarm to Kubernetes. What new objects (e.g., Pods, Services) would replace the Swarm services?
    
    ??? tip "Solution: Migration Mapping"
        1. Convert the `docker-compose.yml` to a K8s `Deployment` (defining replicas and pod specs).
        2. Replace the Swarm internal network with a K8s `Service` for stable discovery.
        3. Define a `ConfigMap` or `Secret` for environment variables.
        4. Implement an `Ingress` object to replace the Swarm routing mesh.

!!! note "Assignment.3: Enterprise Security Analysis"
    Compare the default security posture of vanilla Kubernetes versus OpenShift. Why would a bank prefer OpenShift for deploying an AI model?
    
    ??? tip "Solution: Security Analysis"
        Vanilla K8s allows containers to run as root by default. OpenShift implements **Security Context Constraints (SCCs)**, which forbid containers from running as root by default and enforce strict rules on host system access. A bank would prefer this "secure by default" approach to meet regulatory compliance and reduce the risk of container-escape attacks.

## What's Next?

Now that you can choose the right tool for the job, let's dive deep into the enterprise-grade option. Head over to **[OpenShift for AI: Enterprise Kubernetes & Managed AI Workloads](/section/container/orchestration/openshift.md)**.
