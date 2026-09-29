# Bridging Containers and CI/CD

!!! info "Learning Objectives"
    - Map the full lifecycle of a container from a Git commit to a running Kubernetes Pod.
    - Understand the role of the Container Registry as the "hand-off" point between CI and CD.
    - Implement a basic "Build $\rightarrow$ Push $\rightarrow$ Deploy" pipeline.
    - Analyze the benefits of GitOps (ArgoCD/Flux) over traditional push-based deployment.

Throughout this course, we have studied DevOps pipelines and Container orchestration as separate topics. In reality, they are two halves of the same system. A container is simply the "artifact" that the DevOps pipeline produces and the "unit of deployment" that the orchestrator manages.

The goal of a modern AI platform is to achieve **Continuous Deployment**: a developer pushes a change to a model's hyperparameters in Git, and minutes later, a new container is automatically built and rolled out to the GPU cluster.

!!! info "Why this matters"
    Manual deployments are the enemy of reproducibility. If you manually build an image on your laptop and push it to a server, you have introduced a "human-in-the-loop" variance. By automating the bridge between the container and the pipeline, you ensure that every single version of your AI model can be traced back to a specific Git commit and a specific build log.

## 1. The Automation Flow: Build $\rightarrow$ Ship $\rightarrow$ Run

A professional container pipeline consists of three distinct phases:

### Phase 1: Continuous Integration (The Build)
The CI server (GitHub Actions, Jenkins, GitLab CI) monitors the repository. When a change is pushed:
1.  **Linting/Testing**: The code is checked for errors.
2.  **Build**: The CI server runs `docker build` to create an image.
3.  **Security Scan**: The image is scanned for vulnerabilities (using the tools discussed in the Security chapter).
4.  **Tagging**: The image is tagged with the Git commit hash (e.g., `my-ai-model:a1b2c3d`) rather than just `latest`.

### Phase 2: The Hand-off (The Ship)
The CI server pushes the tagged image to the **Container Registry**. The registry acts as the single source of truth. Once the image is in the registry, the CI phase is complete.

### Phase 3: Continuous Deployment (The Run)
The CD system (e.g., ArgoCD, Flux, or a custom script) notices a new image is available and updates the Kubernetes manifest.
1.  **Update Manifest**: The `image: my-ai-model:old` is changed to `image: my-ai-model:a1b2c3d`.
2.  **Rolling Update**: Kubernetes performs a rolling update—starting new pods with the new image and slowly terminating the old ones to ensure zero downtime.

## 2. Push-based vs. Pull-based (GitOps)

There are two primary ways to trigger the "Run" phase:

| Approach | Mechanism | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Push-based** | The CI server calls `kubectl apply` to tell the cluster to update. | Simple to set up; fast feedback. | CI server needs admin access to the cluster (security risk). |
| **Pull-based (GitOps)** | An agent inside the cluster (ArgoCD) watches Git. When Git changes, the agent "pulls" the change. | Highly secure; the cluster is self-healing (reverts manual changes). | More complex setup; slightly slower update loop. |

### The GitOps Workflow for AI
For AI teams, GitOps is particularly powerful. You can maintain a separate "Environment Repository" that defines exactly which model version is running in `staging` vs `production`. Changing the model version is as simple as a Pull Request to update a version tag in a YAML file.

## 3. Example Pipeline Architecture

A typical AI deployment pipeline looks like this:
`Git Commit` $\rightarrow$ `GitHub Action (Build/Scan)` $\rightarrow$ `GitHub Container Registry` $\rightarrow$ `ArgoCD` $\rightarrow$ `Kubernetes GPU Cluster`

### Production Readiness Checklist
Before promoting a container image from `staging` to `production`, verify the following:

- [ ] **Immutable Tagging**: Is the image tagged with a specific Git commit hash or semantic version (e.g., `v1.2.3`) rather than `latest`?
- [ ] **Vulnerability Scan**: Has the image passed a CVE scan (e.g., Trivy) with zero "CRITICAL" vulnerabilities?
- [ ] **Rootless Execution**: Is the container configured to run as a non-root user?
- [ ] **Resource Limits**: Are CPU and Memory limits explicitly defined in the Kubernetes manifest to prevent OOM (Out of Memory) crashes?
- [ ] **Health Probes**: Are `livenessProbe` and `readinessProbe` configured to ensure traffic only hits healthy pods?
- [ ] **Secret Externalization**: Are all API keys and passwords stored in a Secret manager (Vault/K8s Secrets) rather than environment variables in the image?

---

## Self-Assessment

Test your knowledge by expanding the questions below.

??? question "Why is tagging images with a Git commit hash better than using the 'latest' tag?"
    The `latest` tag is ambiguous; it changes every time a new image is pushed. Using a commit hash provides an immutable link between the running container and the exact version of the code that created it, which is essential for auditing and rolling back failures.

??? question "What is the role of the Container Registry in a CI/CD pipeline?"
    The registry serves as the decoupled hand-off point. The CI system only needs permission to *write* to the registry, and the CD system (or Kubernetes) only needs permission to *read* from it. This limits the blast radius of security credentials.

??? question "How does GitOps improve the reliability of AI deployments?"
    GitOps ensures that the actual state of the cluster always matches the desired state defined in Git. If a pod is accidentally deleted or a configuration is changed manually, the GitOps controller will automatically detect the drift and "heal" the cluster by redeploying the correct version.

## Assignments

!!! note "Assignment 1: Designing a Pipeline"
    Draw a flow chart for an AI project. Include the following components: a Git repo, a CI tool, a Registry, and a K8s cluster. Label the "Build", "Ship", and "Run" boundaries.

!!! note "Assignment 2: Implementing a Simple Push Pipeline"
    Use a GitHub Action to:
    1. Build a small Docker image from a `Dockerfile` in your repo.
    2. Push that image to the GitHub Container Registry (GHCR).
    3. (Optional) Use a `kubectl` action to update a deployment in a local K8s cluster.

## References

- ArgoCD Documentation: [argoproj.github.io/cd/](https://argoproj.github.io/cd/)
- Flux CD Documentation: [fluxcd.io/](https://fluxcd.io/)
- Google Cloud: Continuous Delivery for Containerized Apps: [cloud.google.com/architecture/](https://cloud.google.com/architecture/)

---

## What's Next?

You have now completed the Containerization and Orchestration chapter! You have gone from the basic "Build $\rightarrow$ Ship $\rightarrow$ Run" lifecycle to managing complex, secure, GPU-accelerated clusters integrated into an automated pipeline. You are now ready to apply these skills to the broader **Cloud-Native** ecosystem.
