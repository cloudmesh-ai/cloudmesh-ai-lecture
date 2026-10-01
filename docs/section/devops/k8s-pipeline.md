# Deploying Kubernetes Workloads via CI/CD Pipelines

## Learning Objectives

!!! info "Learning Objectives"
    - Distinguish between the "Push" and "Pull" models of Kubernetes deployment.
    - Implement the deployment of Kubernetes manifests using standard CI/CD tools.
    - Understand the role of Helm in packaging and versioning Kubernetes applications.
    - Analyze the security implications of providing CI/CD pipelines with cluster administrative access.
    - Evaluate the transition from traditional pipelines to GitOps workflows.

## Overview

In previous sections, we learned how to provision the underlying infrastructure (VMs, Networks, and Storage) using Terraform and configure the OS using Ansible. However, in a modern cloud-native environment, the "unit of deployment" is no longer the VM, but the container.

The final link in the DevOps chain is the automated deployment of these containers into a Kubernetes cluster. This process bridges the gap between the "Build" phase (creating a Docker image) and the "Run" phase (execuring that image in production). This chapter explores how to move from manual `kubectl apply` commands to a fully automated, audited, and secure CI/CD pipeline.

## Core Sections

### The Declarative Model: Kubernetes Manifests

Kubernetes operates on a declarative model. Instead of telling the cluster *how* to deploy an app (e.g., "start a container, then attach a volume"), you define *what* the desired state should be in a YAML manifest.

A standard deployment typically involves three core resources:
1. **Deployment**: Defines the desired number of replicas, the container image, and the update strategy (e.g., Rolling Update).
2. **Service**: Provides a stable network endpoint (IP and DNS name) to load balance traffic across the pods.
3. **Ingress**: Manages external access to the services, typically providing HTTP routing and SSL termination.

By storing these manifests in Git, the infrastructure becomes versioned and auditable—a core requirement of the "Everything as Code" philosophy.

### The "Push" Model: Deploying via CI/CD

The most common starting point for automation is the "Push" model. In this scenario, the CI/CD tool (e.g., GitHub Actions, Jenkins) acts as the orchestrator that pushes changes to the cluster.

#### The Workflow
1. **Build**: The pipeline builds a new Docker image and pushes it to a registry (e.g., Docker Hub, ECR).
2. **Authenticate**: The pipeline authenticates with the Kubernetes API using a ServiceAccount token or a cloud-provider identity (OIDC).
3. **Apply**: The pipeline executes `kubectl apply -f manifests/` to update the cluster state.

#### Implementation Example (GitHub Actions)
A typical step for deploying a manifest would look like this:

```yaml
- name: Deploy to Kubernetes
  run: |
    kubectl config use-context my-cluster-context
    kubectl apply -f k8s/deployment.yaml
    kubectl apply -f k8s/service.yaml
```

!!! warning "The Security Risk of Push Pipelines"
    The "Push" model requires the CI/CD tool to hold highly privileged credentials (often `cluster-admin`) to the Kubernetes API. If the CI/CD tool is compromised, the attacker gains full control over the entire cluster.

### Scaling Deployments with Helm

As applications grow, managing raw YAML manifests becomes cumbersome. Repeating the same Deployment and Service blocks for "Dev," "Staging," and "Prod" leads to massive duplication. **Helm** solves this by introducing the concept of a "Chart."

#### Helm as the "Package Manager" for K8s
Helm allows you to template your manifests using a `values.yaml` file. Instead of hardcoding the image tag or replica count, you use placeholders:

```yaml
# templates/deployment.yaml
kind: Deployment
metadata:
  name: {{ .Values.appName }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
        - image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
```

By using `helm upgrade --install`, you can deploy a complex application with a single command, managing versioning and rollbacks through Helm's internal release history.

### The Evolution to GitOps (The "Pull" Model)

To solve the security risks and configuration drift associated with the "Push" model, the industry has shifted toward **GitOps**.

In a GitOps workflow, a controller (like **ArgoCD** or **Flux**) is installed *inside* the Kubernetes cluster. This controller constantly monitors a Git repository and "pulls" the desired state into the cluster.

| Feature | Push Model (CI/CD) | Pull Model (GitOps) |
| :--- | :--- | :--- |
| **Agent Location** | Outside the cluster (CI Tool) | Inside the cluster (GitOps Operator) |
| **Credentials** | CI Tool holds cluster secrets | Cluster holds Git read-only secrets |
| **Drift Detection** | Only detected during next run | Continuous real-time detection |
| **State Authority** | The CI Pipeline | The Git Repository |

By moving the authority to the cluster itself, you eliminate the need to expose your API server to the internet or store sensitive admin tokens in a third-party CI tool.

## Summary Checklist

- [ ] Differentiate between a declarative manifest and a procedural script.
- [ ] Implement a basic `kubectl apply` step within a CI/CD pipeline.
- [ ] Use Helm to template Kubernetes manifests for different environments.
- [ ] Identify the security risks associated with the "Push" model of deployment.
- [ ] Explain the core mechanism of a GitOps "Pull" loop.
- [ ] Compare the blast radius of a compromised CI tool versus a compromised GitOps operator.

## Assignments

!!! note "Assignment.1: Manifest Parameterization"
    Take a standard Kubernetes Deployment YAML and identify three values that change between "Development" and "Production" (e.g., replicas, resource limits, image tags). Rewrite these as a Helm `values.yaml` file.

    ??? tip "Solution: Manifest Parameterization"
        Create a `values.yaml` with keys like `replicaCount`, `cpuLimit`, and `imageTag`. In the template, replace the hardcoded values with `{{ .Values.replicaCount }}`, etc.

!!! note "Assignment.2: The Pipeline Audit"
    Analyze a hypothetical GitHub Action that uses `kubectl apply`. Identify two ways an attacker could exploit this pipeline to gain unauthorized access to the cluster.

    ??? tip "Solution: The Pipeline Audit"
        1. **Secret Leakage**: If the `KUBE_CONFIG` is printed in logs. 2. **Malicious PR**: If the pipeline runs on `pull_request` from a fork and executes a script from the PR that calls `kubectl`.

!!! note "Assignment.3: GitOps Migration Plan"
    Describe the steps required to move an existing "Push-based" Jenkins pipeline to an "ArgoCD Pull-based" workflow. What happens to the Jenkins job? Where does the "deployment" action now occur?

    ??? tip "Solution: GitOps Migration Plan"
        The Jenkins job is reduced to "Build & Push Image" and "Update Git Manifest." The actual deployment is now handled by ArgoCD, which detects the Git change and synchronizes the cluster state.

## References

- Kubernetes Official Documentation: [kubernetes.io/docs](https://kubernetes.io/docs)
- Helm Documentation: [helm.sh/docs](https://helm.sh/docs)
- ArgoCD Documentation: [argoproj.github.io/cd](https://argoproj.github.io/cd/)

## Self-Evaluation

??? note "What is the primary advantage of a declarative manifest over a sequence of CLI commands?"
    A declarative manifest defines the desired end-state. If a resource is accidentally deleted or modified (drift), the system can automatically detect the difference and restore the resource to the defined state, whereas a sequence of commands would either fail or create duplicates.

??? note "How does Helm simplify the management of multiple environments (Dev, Stage, Prod)?"
    Helm uses a templating engine and `values.yaml` files. Instead of maintaining three separate copies of every YAML file, you maintain one template and three small values files, ensuring that the architectural structure remains identical while only the environment-specific parameters change.

??? note "Why is the 'Pull' model (GitOps) considered more secure than the 'Push' model?"
    In the "Push" model, the external CI tool requires administrative credentials to the cluster. In the "Pull" model, the operator lives inside the cluster and only needs read-only access to Git. This eliminates the need to store sensitive cluster-admin tokens in an external third-party system.
