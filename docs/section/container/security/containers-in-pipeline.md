# Bridging Containers and CI/CD

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Map the full lifecycle of a container from a Git commit to a running Kubernetes Pod.
    - Understand the role of the Container Registry as the "hand-off" point between CI and CD.
    - Implement a basic "Build $\rightarrow$ Push $\rightarrow$ Deploy" pipeline.
    - Analyze the benefits of GitOps (ArgoCD/Flux) over traditional push-based deployment.
    - Implement advanced rollout strategies (Canary and Blue-Green) for AI models.
    - Integrate observability-driven rollbacks into the MLOps feedback loop.
    - Understand the relationship between Infrastructure as Code (IaC) and container pipelines.
    - Distinguish between traditional CI/CD and Continuous Training (CT).

## Concepts

### Overview

Throughout this course, we have studied DevOps pipelines and container orchestration as separate topics. In reality, they are two halves of the same system. A container is simply the "artifact" that the DevOps pipeline produces and the "unit of deployment" that the orchestrator manages.

The goal of a modern AI platform is to achieve **Continuous Deployment**: a developer pushes a change to a model's hyperparameters in Git, and minutes later, a new container is automatically built and rolled out to the GPU cluster.

!!! info "Why this matters"
    Manual deployments are the enemy of reproducibility. If you manually build an image on your laptop and push it to a server, you have introduced "human-in-the-loop" variance. By automating the bridge between the container and the pipeline, you ensure that every single version of your AI model can be traced back to a specific Git commit and a specific build log.

### The Automation Flow: Build $\rightarrow$ Ship $\rightarrow$ Run

A standardized container pipeline consists of three distinct phases:

#### Phase 1: Continuous Integration (The Build)

The CI server (e.g., GitHub Actions, Jenkins, GitLab CI) monitors the repository. When a change is pushed, it triggers the following sequence:

1. **Linting/Testing**: The code is checked for syntax errors and unit tests are executed.
2. **Build**: The CI server runs `docker build` to create a container image.
3. **Security Scan**: The image is scanned for vulnerabilities (using tools like [Trivy](/section/container/security/container-security.md#vulnerability-scanning-and-sbom)).
4. **Tagging**: The image is tagged with the Git commit hash (e.g., `my-ai-model:a1b2c3d`) rather than just `latest` to ensure immutability.

#### Phase 2: The Hand-off (The Ship)

The CI server pushes the tagged image to the **Container Registry**. The registry acts as the single source of truth and the decoupled hand-off point between the build and deployment phases. Once the image is in the registry, the CI phase is complete.

#### Phase 3: Continuous Deployment (The Run)

The CD system (e.g., ArgoCD, Flux, or a custom script) notices a new image is available and updates the Kubernetes manifest.

1. **Update Manifest**: The image reference is updated from the old hash to the new hash.
2. **Rolling Update**: Kubernetes performs a rolling update—starting new pods with the new image and slowly terminating the old ones to ensure zero downtime.

### Push-based vs. Pull-based (GitOps)

There are two primary ways to trigger the "Run" phase of a pipeline.

| Approach | Mechanism | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Push-based** | The CI server calls `kubectl apply` to tell the cluster to update. | Simple to set up; fast feedback. | CI server needs admin access to the cluster (security risk). |
| **Pull-based (GitOps)** | An agent inside the cluster (ArgoCD) watches Git. When Git changes, the agent "pulls" the change. | Highly secure; the cluster is self-healing (reverts manual changes). | More complex setup; slightly slower update loop. |

#### The GitOps Workflow for AI

For AI teams, GitOps is particularly effective. You can maintain a separate "Environment Repository" that defines exactly which model version is running in `staging` vs `production`. Changing the model version is as simple as a Pull Request to update a version tag in a YAML file, providing a clear audit trail of every model change.

### Advanced Deployment Strategies

For high-stakes AI models, a simple rolling update may be too risky. Instead, teams use advanced patterns to verify model performance on live traffic.

#### Canary Releases
A **Canary Release** routes a small percentage of traffic (e.g., 5%) to the new model version while the majority remains on the stable version.
- **Verification**: Data scientists monitor the "canary" for accuracy drops, latency spikes, or unexpected predictions.
- **Promotion**: If the canary performs well, traffic is incrementally shifted (10% $\rightarrow$ 25% $\rightarrow$ 100%).
- **Implementation**: Typically achieved using a Service Mesh (e.g., Istio) or an Advanced Ingress Controller.

#### Blue-Green Deployments
In a **Blue-Green** setup, two identical environments exist: "Blue" (current production) and "Green" (new version).
- **Switch**: Once the Green environment is fully tested, the load balancer "flips" all traffic from Blue to Green.
- **Instant Rollback**: If a critical bug is found, the flip is reversed instantly, returning all traffic to the Blue environment.

### The MLOps Feedback Loop: Observability and Rollbacks

A production pipeline is not a one-way street; it requires a feedback loop to ensure model quality.

#### Observability Integration
By integrating tools like **Prometheus** and **Grafana**, the CD system can monitor the health of a new deployment in real-time. For AI models, this includes monitoring "Model Drift" or "Prediction Confidence" scores.

#### Automated Rollbacks
When using GitOps (e.g., ArgoCD), you can configure **Automated Rollbacks**. 

**The Observability Feedback Loop**:
1. **Monitor**: Prometheus collects real-time metrics (e.g., 5xx error rates or P99 latency).
2. **Alert**: Alertmanager detects that a new deployment has exceeded a predefined error threshold.
3. **Trigger**: A webhook is sent to the GitOps controller (ArgoCD) or a custom bot.
4. **Revert**: The system automatically triggers a Git revert of the deployment commit in the environment repository.
5. **Heal**: ArgoCD detects the Git change and immediately rolls back the cluster to the previous stable image.

This ensures that a "bad" model version is removed from production in seconds, without requiring a human engineer to wake up and manually trigger a rollback.

### Infrastructure as Code (IaC) and the Pipeline

Containers do not run in a vacuum; they require a cluster. To ensure the entire environment is reproducible, the cluster itself must be managed as code.

- **Provisioning**: Tools like **Terraform** or **Pulumi** define the GPU nodes, VPCs, and Kubernetes clusters.
- **Layered Pipeline**: The full flow becomes: `IaC (Cluster Setup)` $\rightarrow$ `CI/CD (Container Deployment)`. This prevents "configuration drift" where different clusters have different settings.

### Continuous Training (CT)

While standard CI/CD handles *code* changes, AI requires **Continuous Training (CT)** to handle *data* changes.

- **The CT Trigger**: A monitoring system detects "Data Drift" (the incoming real-world data no longer matches the training data).
- **The Loop**: This triggers an automated retraining pipeline $\rightarrow$ a new model is saved $\rightarrow$ a new container image is built $\rightarrow$ the GitOps repo is updated.
- **Result**: The model evolves automatically as the world changes, without a developer needing to push a manual Git commit.

## Implementation

In this section, we move from theory to practice. We will implement a production-grade GitHub Actions pipeline tailored for an AI workload. 

### Production-Grade AI Pipeline

AI containers are uniquely challenging because they often rely on massive base images (e.g., NVIDIA CUDA) and require specialized hardware (GPUs). A naive pipeline will be slow and insecure.

!!! info "Why this matters"
    AI base images can easily exceed 5GB. Without advanced caching and security gates, your pipeline will become a bottleneck, and you risk deploying bloated images with hundreds of critical vulnerabilities inherent in complex ML libraries.

Below is a complete `.github/workflows/main.yml` implementation.

```yaml
name: Production AI Model Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  # Use a specific CUDA version to ensure consistency across GPU nodes
  BASE_IMAGE: nvidia/cuda:12.2.0-base-ubuntu22.04

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      security-events: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Export for Scan
        uses: docker/build-push-action@v5
        with:
          context: .
          # Use GHA cache to avoid re-downloading 5GB+ AI base images
          cache-from: type=gha
          cache-to: type=gha,mode=max
          push: false
          load: true 
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}

      - name: Security Scan (Trivy)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: 'table'
          exit-code: '1' # Block the pipeline on CRITICAL vulnerabilities
          ignore-unfixed: true
          severity: 'CRITICAL'

      - name: Push Verified Image
        if: success()
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:cuda-12.2

  deploy:
    needs: build-and-scan
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set Kubernetes Context
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG }}

      - name: Deploy to K8s Cluster
        run: |
          # Update the deployment to use the newly scanned and pushed image
          kubectl set image deployment/ai-model-api \
            ai-container=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} \
            --record
          
          # Verify the rollout
          kubectl rollout status deployment/ai-model-api --timeout=300s

      - name: Post-Deployment Smoke Test
        run: |
          # Simple curl to verify the AI model endpoint is responding
          curl -f http://ai-model-api.svc.cluster.local/health
```

### Pipeline Logic Breakdown

1. **Optimized Caching**: We use `cache-from: type=gha` and `cache-to: type=gha`. For AI workloads, this is the difference between a 2-minute build and a 20-minute build, as it avoids re-pulling heavy CUDA layers.
2. **The Security Gate**: The `trivy-action` is configured with `exit-code: '1'`. This transforms the scan from a "report" into a "gate." If a CRITICAL vulnerability is found, the pipeline fails immediately, and the `Push Verified Image` step is skipped.
3. **GPU-Aware Tagging**: We tag the image with both the Git SHA (for immutability) and a CUDA version (e.g., `cuda-12.2`). This allows the K8s scheduler to ensure the image is compatible with the physical GPU drivers on the worker nodes.
4. **Atomic Deployment**: By using `kubectl rollout status`, we ensure the pipeline doesn't report success until the pods are actually healthy and running.

### Production Readiness Checklist

Before promoting a container image from `staging` to `production`, verify the following:

- [ ] **Immutable Tagging**: Is the image tagged with a specific Git commit hash or semantic version instead of `latest`?
- [ ] **Vulnerability Scan**: Has the image passed a CVE scan with zero "CRITICAL" vulnerabilities?
- [ ] **[Rootless Execution](/section/container/foundations/podman.md)**: Is the container configured to run as a non-root user?
- [ ] **Resource Limits**: Are CPU and Memory limits explicitly defined in the Kubernetes manifest to prevent OOM crashes?
- [ ] **Health Probes**: Are `livenessProbe` and `readinessProbe` configured to ensure traffic only hits healthy pods?
- [ ] **Secret Externalization**: Are all API keys and passwords stored in a Secret manager (Vault/K8s Secrets) rather than baked into the image?

## Self-Evaluation

### Summary Checklist

- [ ] Map the lifecycle of a container from Git commit to a running Pod.
- [ ] Explain why using a Git commit hash for tagging is better than using `latest`.
- [ ] Contrast push-based deployment with pull-based GitOps.
- [ ] Identify the three phases of a standardized pipeline: Build, Ship, and Run.
- [ ] Explain the difference between Canary and Blue-Green deployment strategies.
- [ ] Describe how automated rollbacks are triggered via observability.
- [ ] Contrast standard CI/CD with Continuous Training (CT).
- [ ] Apply the production readiness checklist to an AI model deployment.

??? question "Why is tagging images with a Git commit hash better than using the 'latest' tag?"
    The `latest` tag is ambiguous; it changes every time a new image is pushed. Using a commit hash provides an immutable link between the running container and the exact version of the code that created it, which is essential for auditing and rolling back failures.

??? question "What is the role of the Container Registry in a CI/CD pipeline?"
    The registry serves as the decoupled hand-off point. The CI system only needs permission to *write* to the registry, and the CD system (or Kubernetes) only needs permission to *read* from it. This limits the blast radius of security credentials.

??? question "How does GitOps improve the reliability of AI deployments?"
    GitOps ensures that the actual state of the cluster always matches the desired state defined in Git. If a pod is accidentally deleted or a configuration is changed manually, the GitOps controller will automatically detect the drift and "heal" the cluster by redeploying the correct version.

??? question "What is the difference between a Canary and a Blue-Green deployment?"
    A Blue-Green deployment is an "all-or-nothing" flip between two identical environments. A Canary release is a gradual shift, routing a small percentage of traffic to the new version to test it in production before a full rollout.

??? question "How does Continuous Training (CT) differ from standard CI/CD?"
    Standard CI/CD is triggered by changes to *code* or *configuration*. Continuous Training is triggered by changes in *data* (e.g., data drift), automating the retraining, packaging, and deployment of a model without requiring a manual code push.

## Assignments

!!! note "Assignment.1: Designing a Pipeline"
    Draw a flow chart for an AI project. Include the following components: a Git repo, a CI tool, a Registry, and a K8s cluster. Label the "Build", "Ship", and "Run" boundaries.
    
    ??? tip "Solution: Pipeline Design"
        The flow should be: Git $\rightarrow$ (Build Phase: Lint/Build/Scan) $\rightarrow$ Registry (Ship Phase) $\rightarrow$ K8s Cluster (Run Phase via ArgoCD/Flux).

!!! note "Assignment.2: Implementing a Simple Push Pipeline"
    Use a GitHub Action to:
    1. Build a small Docker image from a `Dockerfile` in your repo.
    2. Push that image to the GitHub Container Registry (GHCR).
    3. (Optional) Use a `kubectl` action to update a deployment in a local K8s cluster.
    
    ??? tip "Solution: Push Pipeline"
        Use the `docker/build-push-action` in GitHub Actions, providing the `secrets.GITHUB_TOKEN` for registry authentication.

!!! note "Assignment.3: Designing a Canary Rollout"
    You are deploying a new version of a Large Language Model (LLM) that is suspected to be more accurate but might be slower. Design a Canary release strategy.
    1. What percentage of traffic will you start with?
    2. Which metrics (KPIs) will you monitor to decide if the model should be promoted?
    3. How will you handle a scenario where the model's accuracy is higher, but the latency exceeds the SLA?
    
    ??? tip "Solution: Canary Design"
        Start with 1-5% of traffic. Monitor P99 latency and prediction confidence scores. If latency exceeds SLA, the model should be rolled back, even if accuracy is higher, unless the latency can be optimized.

## References

- ArgoCD Documentation: [argoproj.github.io/cd/](https://argoproj.github.io/cd/)
- Flux CD Documentation: [fluxcd.io/](https://fluxcd.io/)
- Google Cloud: Continuous Delivery for Containerized Apps: [cloud.google.com/architecture/](https://cloud.google.com/architecture/)

## What's Next?

You have now completed the Containerization and Orchestration chapter! You have gone from the basic "Build $\rightarrow$ Ship $\rightarrow$ Run" lifecycle to managing complex, secure, GPU-accelerated clusters integrated into an automated pipeline. You are now ready to apply these skills to the broader **Cloud-Native** ecosystem.
