# Amazon Elastic Container Registry (ECR)

!!! info "Learning Objectives"
    - Compare the use cases for Public vs. Private ECR repositories.
    - Authenticate the Docker CLI with Amazon ECR.
    - Implement image lifecycle policies to manage storage costs.
    - Configure and interpret vulnerability scanning results.
    - Integrate ECR images into ECS and EKS orchestration.

## Overview

Amazon Elastic Container Registry (ECR) is a fully managed Docker container registry that makes it easy for developers to store, manage, and deploy Docker container images. In a typical CI/CD pipeline, ECR acts as the central source of truth between the build phase (where images are created and scanned) and the deployment phase (where orchestrators like ECS or EKS pull the images to run).

## Repository Types

AWS provides two types of registries to balance security and accessibility:

| Feature | Private Repository | Public Repository |
| :--- | :--- | :--- |
| **Visibility** | Only authenticated IAM users/roles | Anyone on the internet |
| **Access Control** | Fine-grained IAM policies | No access control for pulling |
| **Primary Use Case** | Internal enterprise apps, proprietary code | Open source projects, public base images |
| **Cost** | Paid per GB stored/data transfer | Free (within certain limits) |

## Practical Guide: Getting Started

### 1. Create a Repository
You can create a repository using the AWS Management Console or the CLI:

```bash
aws ecr create-repository --repository-name my-web-app --region us-east-1
```

### 2. Authenticate Docker CLI
Because ECR is integrated with AWS IAM, you cannot use a simple username/password. You must retrieve a temporary authentication token:

```bash
# Retrieve token and pipe it directly into docker login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
```

### 3. Push an Image
Follow the standard Docker workflow, ensuring the tag matches the ECR repository URI:

```bash
# Build the image
docker build -t my-web-app .

# Tag the image for ECR
docker tag my-web-app:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/my-web-app:latest

# Push to the cloud
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/my-web-app:latest
```

## Image Management

### Tagging Strategies
Using `:latest` is convenient for development but dangerous for production. Recommended strategies include:
- **Semantic Versioning**: `my-app:1.2.3`
- **Git Commit Hash**: `my-app:sha-a1b2c3d` (Ensures exact traceability to code)
- **Build ID**: `my-app:build-456`

### Lifecycle Policies
To prevent storage costs from ballooning due to old images, ECR Lifecycle Policies automate the cleanup of unused images.

**Example Policy**: Keep only the last 10 images tagged as `dev`, and delete any untagged images older than 14 days.

```json
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep last 10 dev images",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["dev"],
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": { "type": "expire" }
        },
        {
            "rulePriority": 2,
            "description": "Expire untagged images after 14 days",
            "selection": {
                "tagStatus": "untagged",
                "countType": "sinceImagePushed",
                "countUnit": "days",
                "countNumber": 14
            },
            "action": { "type": "expire" }
        }
    ]
}
```

## Security & Governance

### Vulnerability Scanning
ECR identifies software vulnerabilities (CVEs) within your images.
- **Basic Scanning**: Scans images on push using the Common Vulnerabilities and Exposures (CVE) database.
- **Enhanced Scanning**: Integrated with Amazon Inspector; provides continuous scanning and automatic re-scanning when new CVEs are discovered.

### IAM Permissions
Access to ECR is managed via IAM. Common permissions include:
- `ecr:GetAuthorizationToken`: Required for the `get-login-password` command.
- `ecr:BatchCheckLayerAvailability`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`: Required for pulling images.
- `ecr:PutImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`: Required for pushing images.

## Cloud Integration

### ECS Integration
In an ECS Task Definition, the image is referenced by its ECR URI:
```yaml
containerDefinitions:
  - name: "app-container"
    image: "123456789012.dkr.ecr.us-east-1.amazonaws.com/my-web-app:v1.0.0"
```
The ECS agent uses the Task Execution IAM Role to authenticate with ECR and pull the image.

### EKS Integration
Kubernetes pods pull from ECR similarly. While EKS nodes usually have the necessary IAM permissions via the Node Instance Role, you can also use `imagePullSecrets` if pulling from a cross-account registry.

## Assignments

!!! note "Assignment.1: ECR Lifecycle Management"
    1. Create a private ECR repository named `lifecycle-demo`.
    2. Push 15 different versions of a small image (e.g., `alpine`) tagged as `test-1`, `test-2`, etc.
    3. Create a lifecycle policy to keep only the 5 most recent images.
    4. Verify via the AWS Console that the oldest 10 images were automatically deleted.

!!! note "Assignment.2: Vulnerability Audit"
    1. Build an image using an intentionally outdated base image (e.g., `node:10`).
    2. Push the image to ECR.
    3. Trigger a scan and navigate to the "Vulnerabilities" tab in the console.
    4. Identify one "High" or "Critical" CVE and research the required version update to fix it.

## References

- AWS ECR Documentation: https://docs.aws.amazon.com/ecr/
- AWS IAM for ECR: https://docs.aws.amazon.com/ecr/latest/userguide/security-iam.html
- ECR Lifecycle Policies: https://docs.aws.amazon.com/ecr/latest/userguide/lifecycle-policies.html
