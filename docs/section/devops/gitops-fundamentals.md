# GitOps Fundamentals

GitOps is an operational framework that takes DevOps best practices—such as version control, collaboration, compliance, and CI/CD—and applies them to infrastructure automation.

## What is GitOps?

At its core, GitOps uses a Git repository as the "single source of truth" for the desired state of your infrastructure. Instead of manually executing commands to change the state of a cluster, you describe the desired state in a Git repository (typically using declarative manifests), and a controller ensures that the actual state of the environment matches the desired state.

!!! info "Why this matters"
    For AI teams, GitOps provides a rigorous audit trail for model deployments. If a new model version causes a regression in prediction accuracy or triggers a memory leak on a GPU node, GitOps allows the team to perform a "one-click rollback" by reverting a single commit in Git. This eliminates the panic of manual rollbacks in production and ensures that the state of the cluster is always reproducible.

### Key Principles
- **Declarative**: The entire system is described declaratively (e.g., YAML manifests). For more on the foundations of this approach, see [[devops-iac]].
- **Declarative**: The entire system is described declaratively (e.g., YAML manifests). For more on the foundations of this approach, see [[devops-iac]].
- **Versioned and Immutable**: The desired state is stored in Git, providing a complete audit trail and the ability to roll back instantly.
- **Pulled Automatically**: Software agents automatically pull the desired state from the source.
- **Continuously Reconciled**: Software agents continuously observe the actual state and correct any drift from the desired state.

## Push vs. Pull Deployments

There are two primary patterns for implementing the synchronization between Git and the environment.

### Push-based Deployment (e.g., [[jenkins]], [[github-workflows]])
In a push-based model, the CI/CD pipeline is responsible for pushing the changes to the target environment.
- **Mechanism**: When a change is merged into Git, the CI tool triggers a script (e.g., `kubectl apply -f manifest.yaml`) to update the cluster.
- **Pros**: Simpler to set up the first steps; familiar to those used to traditional CI/CD.
- **Cons**: Requires the CI tool to have administrative access to the cluster (security risk); does not automatically detect or fix "configuration drift" (manual changes made to the cluster).

### Pull-based Deployment (e.g., ArgoCD, Flux)
In a pull-based model, an agent (operator) runs inside the cluster and "pulls" the configuration from Git.
- **Mechanism**: The operator continuously monitors the Git repository. When it detects a difference between the Git state and the cluster state, it pulls the changes and applies them locally.
- **Pros**: More secure (no external credentials needed for the cluster); automatically corrects drift; provides better visibility into the synchronization status.
- **Cons**: More complex to set up initially; requires installing operators in the cluster.

### Comparison Summary

| Feature | Push-based | Pull-based |
| :--- | :--- | :--- |
| **Agent Location** | External (CI Server) | Internal (Cluster) |
| **Credentials** | Stored in CI Tool | Stored in Cluster |
| **Drift Detection** | None (usually) | Continuous |
| **Security** | Higher Risk (Wide Access) | Lower Risk (Least Privilege) |
| **Setup Complexity** | Low | Medium |

## Practical Examples

To illustrate the difference, consider how a deployment is triggered in each model:

### The "Push" Approach (CI Script)
In a push-based system, your CI configuration (like a GitHub Action) contains the logic to apply the change:
```yaml
# .github/workflows/deploy.yml
- name: Deploy to Production
  run: |
    kubectl config use-context prod-cluster
    kubectl apply -f k8s/deployment.yaml
```

### The "Pull" Approach (Declarative Application)
In a pull-based system, you define an "Application" resource inside the cluster. The controller then handles the rest:
```yaml
# argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-web-app
spec:
  source:
    repoURL: https://github.com/org/my-repo.git
    targetRevision: main
    path: k8s/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
```

## Understanding Configuration Drift

**Configuration Drift** occurs when the actual state of the infrastructure deviates from the desired state defined in Git. This often happens when someone manually edits a resource (e.g., using `kubectl edit` to quickly increase replicas during a production incident) without updating the source code.

In a traditional push-based system, this drift remains until the next deployment. In a GitOps (pull-based) system, the controller detects the drift immediately and automatically reverts the environment to match the "truth" in Git, ensuring environment consistency and preventing "snowflake" servers.

## The GitOps Developer Workflow

The power of GitOps lies in turning infrastructure changes into a standard software development process:

1. **Propose**: A developer creates a new branch and modifies the declarative manifests (e.g., updating an image tag or changing a service port).
2. **Review**: A Pull Request (PR) is opened. Teammates review the infrastructure change just as they would review application code.
3. **Approve**: The PR is merged into the main branch after passing automated tests and manual review.
4. **Synchronize**: The GitOps controller (e.g., ArgoCD) detects the commit on the main branch and triggers a synchronization.
5. **Verify**: The controller applies the changes to the cluster and monitors the health of the resources until the actual state matches the desired state.

## Handling Secrets in GitOps

One of the primary challenges of GitOps is the **Secrets Paradox**: Git is meant to be a transparent, versioned history, but secrets (API keys, database passwords) must remain private. Storing plain-text secrets in Git is a critical security failure.

To solve this, GitOps practitioners use one of these three common patterns:

1. **Sealed Secrets**: Tools like *Bitnami Sealed Secrets* allow you to encrypt a secret using a public key. The resulting "SealedSecret" is safe to store in Git; only the controller running inside the cluster holds the private key needed to decrypt it.
2. **External Secrets Operator (ESO)**: Instead of storing the secret in Git, you store a *reference* to a secret located in a professional vault (e.g., AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault). The ESO fetches the actual value at runtime and injects it into the cluster.
3. **Sops (Secrets Operations)**: An editor that encrypts specific values within a YAML file using KMS or PGP, allowing the file to be committed to Git while keeping the sensitive data encrypted.

## The Role of Kubernetes in GitOps

Kubernetes is the ideal platform for GitOps because it is natively declarative. 

1. **Declarative API**: Kubernetes uses manifests (YAML/JSON) to describe the desired state of pods, services, and deployments.
2. **Control Loop**: The Kubernetes architecture is built around the concept of a "control loop" (reconciliation), which is exactly what GitOps tools like ArgoCD and Flux leverage to maintain state.
3. **Custom Resource Definitions (CRDs)**: GitOps tools extend the Kubernetes API using CRDs, allowing you to define "Application" resources that link a Git repo to a specific namespace in the cluster.

By combining Kubernetes with GitOps, organizations can achieve higher reliability, faster recovery from failures, and a more secure deployment pipeline.

## GitOps Readiness Checklist

Is your organization actually practicing GitOps? Check your process against these requirements:

- [ ] **Declarative**: Is the entire system described as a target state (what it should be) rather than a list of instructions (how to do it)?
- [ ] **Versioned**: Is the complete desired state stored in a Git repository?
- [ ] **Automated**: Is the deployment triggered by a Git event (merge/commit) rather than a manual command?
- [ ] **Reconciled**: Does the system automatically detect and correct manual changes (drift) in the environment?
- [ ] **Secure**: Are secrets handled via encryption or external vaults rather than plain-text in the repository?
