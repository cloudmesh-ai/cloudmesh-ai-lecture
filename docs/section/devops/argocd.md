# ArgoCD: Declarative GitOps for Kubernetes

## Learning Objectives

By the end of this chapter, participants will be able to:
- Explain the difference between "Push-based" and "Pull-based" CD.
- Describe the ArgoCD architecture and its role in a GitOps pipeline.
- Configure ArgoCD Applications to synchronize Kubernetes clusters with Git repositories.
- Implement automated synchronization and self-healing strategies.
- Manage multi-cluster and multi-tenant deployments using ArgoCD Projects and ApplicationSets.

## Overview

While traditional CI/CD tools (like Jenkins or GitHub Actions) typically **push** changes to a cluster via `kubectl apply` or Helm, ArgoCD implements a **pull-based** model. 

In a pull-based GitOps workflow, a controller runs *inside* the Kubernetes cluster. It continuously monitors a Git repository (the "Source of Truth") and compares the desired state defined there with the live state of the cluster. If a discrepancy (drift) is detected, ArgoCD can automatically synchronize the cluster to match the Git repository.

!!! info "Why ArgoCD?"
    ArgoCD eliminates the need to store cluster credentials (Kubeconfig) in external CI tools, reducing the security attack surface. It also ensures that the cluster state never drifts from the version-controlled definition, providing an audit trail for every change.

## Core Concepts

### 1. The GitOps Control Loop
ArgoCD operates on a continuous reconciliation loop:
1. **Monitor**: Watch the Git repository for commits.
2. **Compare**: Diff the desired state (Git) against the live state (K8s).
3. **Sync**: Update the cluster to match Git (either manually or automatically).

### 2. Applications
The `Application` is the primary resource in ArgoCD. It defines:
- **Source**: The Git repository, path, and target revision (branch/tag).
- **Destination**: The target Kubernetes cluster and namespace.
- **Sync Policy**: How the application should be updated (Manual vs. Automatic).

### 3. Sync Policies
- **Automated Sync**: ArgoCD automatically applies changes as soon as they land in Git.
- **Prune**: If a resource is deleted from Git, ArgoCD removes it from the cluster.
- **Self-Heal**: If a user manually edits a resource in the cluster (drift), ArgoCD immediately reverts it to the state defined in Git.

### 4. Projects and Multi-tenancy
ArgoCD **Projects** (`AppProject`) provide a logical grouping of applications. They allow administrators to:
- Restrict which Git repositories can be used.
- Limit which clusters and namespaces an application can deploy to.
- Define RBAC roles for different teams.

### 5. ApplicationSets
For managing dozens or hundreds of clusters, **ApplicationSets** allow you to template applications. For example, you can define one ApplicationSet that automatically deploys a "Monitoring" stack to every cluster registered in your inventory.

## Implementation Workflow

### Step 1: Define the Desired State
Place your Kubernetes manifests (YAML), Helm charts, or Kustomize overlays in a Git repository.
Example structure:
```text
infra-repo/
  ├── clusters/
  │   ├── production/
  │   │   └── guestbook-app.yaml
  │   └── staging/
  │       └── guestbook-app.yaml
  └── base/
      └── deployment.yaml
```

### Step 2: Create the ArgoCD Application
You can create an application via the UI, CLI, or as a YAML manifest:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: 'https://github.com/example/infra-repo.git'
    targetRevision: HEAD
    path: clusters/production
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: guestbook-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Step 3: Observe the Sync
Once applied, the ArgoCD UI provides a visual representation of all resources in the application, showing their health status (Healthy, Progressing, Degraded) and sync status (Synced, OutOfSync).

## Summary: Push vs. Pull CD

| Feature | Push-based (Jenkins/GH Actions) | Pull-based (ArgoCD) |
| :--- | :--- | :--- |
| **Mechanism** | CI Tool $\rightarrow$ Cluster | Cluster $\leftarrow$ Git |
| **Credentials** | CI Tool needs Kubeconfig | Cluster pulls from Git |
| **Drift Detection** | Only at deploy time | Continuous |
| **Recovery** | Manual redeploy | Automatic Self-healing |
