# Example DevOps Project: From Code to Cloud

This project serves as a capstone integration for the DevOps chapter. It guides you through the end-to-end process of taking a simple application from a local git commit to a production-ready deployment on the cloud.

By completing this project, you will tie together the concepts of **Infrastructure as Code (IaC)**, **Configuration Management**, **CI/CD Pipelines**, **Container Orchestration**, and **Observability**.

## Project Overview

**Scenario**: You are deploying a lightweight "CloudMesh-AI" status API. 
**Goal**: Establish a fully automated pipeline where any change to the code is automatically tested, packaged, deployed to a Kubernetes cluster, and monitored for performance.

### The DevOps Toolchain
| Phase | Tool | Purpose | Reference |
| :--- | :--- | :--- | :--- |
| **Provisioning** | Terraform | AWS Infrastructure | [Terraform Guide](/section/devops/terraform.md) |
| **Configuration** | Ansible | OS Hardening & Tooling | [Ansible Guide](/section/devops/ansible.md) |
| **CI / Build** | GitHub Actions | Dockerization & Push | [GitHub Workflows](/section/devops/github-workflows.md) |
| **Orchestration** | Kubernetes | Deployment & Scaling | [CI/CD Framework](/section/devops/devop-ci.md) |
| **Observability** | CloudWatch / Azure Monitor | Health & Metrics | [Monitoring Guide](/section/devops/devop-azure-monitor.md) |
| **Security** | GitHub Secrets / OIDC | Pipeline Hardening | [Pipeline Security](/section/devops/github-workflow-security.md) |

---

## Step 1: Infrastructure Provisioning with Terraform

Before we can deploy code, we need a place for it to live. We use Terraform to ensure our infrastructure is versioned and reproducible.

### Task: Provision an AWS Environment
1. **Define the Provider**: Set up the AWS provider in your `main.tf`.
2. **Create Networking**: Define a VPC, public subnets, and an Internet Gateway.
3. **Provision Compute**: 
   - Create an EC2 instance (for the K8s control plane or a standalone node).
   - Configure Security Groups to allow traffic on ports 80 (HTTP), 443 (HTTPS), and 22 (SSH).
4. **Apply the Configuration**:
   ```bash
   terraform init
   terraform plan
   terraform apply -auto-approve
   ```

!!! tip "Concept Link"
    This process implements the **Declarative** approach discussed in [The Core of IaC](/section/devops/devops-iac.md).

---

## Step 2: OS Configuration with Ansible

Terraform gives us a "blank slate" VM. We use Ansible to transform that VM into a functional server.

### Task: Prepare the Node for Containers
1. **Inventory Management**: Add the IP address of your Terraform-provisioned instance to your Ansible `hosts` file.
2. **Write the Playbook**: Create a playbook to:
   - Update all system packages.
   - Install `docker.io` and `kubectl`.
   - Ensure the Docker service is started and enabled on boot.
   - Create a dedicated application user with limited privileges.
3. **Execute the Configuration**:
   ```bash
   ansible-playbook -i hosts setup-node.yml
   ```

!!! info "Why not Terraform?"
    While Terraform can run scripts via `remote-exec`, [Ansible](/section/devops/ansible.md) is used here because it is **idempotent**, ensuring the server stays in the desired state even if the playbook is run multiple times.

---

## Step 3: Continuous Integration with GitHub Actions

Now that the infrastructure is ready, we automate the "Build" phase. We want our application to be packaged as a Docker image every time we push to the `main` branch.

### Task: Build the Automation Pipeline
1. **Create the Workflow**: Define a file at `.github/workflows/pipeline.yml`.
2. **Define the Job**:
   - **Trigger**: `on: push: branches: [main]`
   - **Build**: Use a `docker/build-push-action` to build the image from the `Dockerfile`.
   - **Push**: Authenticate with AWS ECR (Elastic Container Registry) and push the tagged image.
3. **Secure the Pipeline**: Use [GitHub Secrets](/section/devops/github-workflow-security.md) to store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

```yaml
# Example snippet
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and Push Docker Image
        run: |
          docker build -t cloudmesh-api:latest .
          docker push ${{ secrets.ECR_REPOSITORY }}:latest
```

---

## Step 4: Deployment to Kubernetes (K8s)

With the image safely stored in the registry, we deploy it to our cluster using Kubernetes manifests.

### Task: Orchestrate the Application
1. **Define the Deployment**: Create a `deployment.yaml` specifying:
   - 3 replicas for high availability.
   - The image path from your ECR registry.
   - Resource limits (CPU/Memory) to prevent "noisy neighbor" issues.
2. **Expose the Service**: Create a `service.yaml` (type: LoadBalancer) to route external traffic to your pods.
3. **Deploy**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```

!!! tip "DevOps Flow"
    This step represents the **Orchestration** phase, moving from a single VM to a scalable, self-healing cluster as described in the [CI/CD/CM Framework](/section/devops/devop-ci.md).

---

## Step 5: Observability and Monitoring

A deployment is not complete until you can prove it is working and healthy.

### Task: Establish Telemetry
1. **Infrastructure Monitoring**: Enable AWS CloudWatch to monitor CPU and Disk usage of the nodes.
2. **Application Monitoring**: 
   - Integrate [Azure Monitor / Application Insights](/section/devops/devop-azure-monitor.md) (or CloudWatch Logs) to capture application exceptions and request latency.
3. **Configure Alerting**: Set up a threshold (e.g., "CPU > 80% for 5 minutes") to trigger a notification via Email or Slack.

---

## Step 6: Hardening and DevSecOps

Finally, we review the entire pipeline to eliminate security vulnerabilities.

### Task: Secure the Lifecycle
1. **Image Scanning**: Add a step in the GitHub Action to scan the Docker image for CVEs using `Trivy` or `Snyk`.
2. **Principle of Least Privilege**: Replace long-lived AWS IAM keys in GitHub Secrets with **OIDC (OpenID Connect)** to allow GitHub to assume a temporary AWS role.
3. **Network Hardening**: Update the Terraform Security Groups to restrict SSH access to only your corporate IP range.

Refer to [Securing the Pipeline](/section/devops/github-workflow-security.md) for detailed implementation patterns.

---

## Summary of the Project Flow

By following these steps, you have implemented a professional-grade DevOps lifecycle:
**Code** $\rightarrow$ **Git Push** $\rightarrow$ **GitHub Action (Build & Scan)** $\rightarrow$ **ECR (Registry)** $\rightarrow$ **K8s (Deploy)** $\rightarrow$ **CloudWatch (Monitor)**.

---

## What's Next?

This project demonstrates the integration of the entire DevOps toolchain. To dive deeper into any of the specific tools used here, return to the **[Master Index](/section/devops/devops.md)**.
