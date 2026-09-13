# Leveraging AWS for DevOps

!!! info "Learning Objectives"
    - Identify the key AWS services that support CI/CD workflows.
    - Understand the role of the AWS CodeSuite in automating application delivery.
    - Distinguish between different AWS infrastructure automation tools.
    - Learn how to implement monitoring and observability using AWS native tools.

Amazon Web Services (AWS) provides a comprehensive, end-to-end ecosystem for DevOps. Instead of stitching together multiple third-party tools, teams can use AWS native services to automate everything from the initial code commit to the final production monitoring.

!!! info "Why this matters"
    Using a unified cloud-native toolchain reduces "integration friction." When your CI/CD pipeline, your container registry, and your deployment target all live within the same cloud identity and access management (IAM) system, security is tighter, latency is lower, and troubleshooting is simplified.

## Integrated CI/CD with AWS CodeSuite

AWS provides a family of tools known as the "CodeSuite" to handle the software delivery lifecycle:

| Tool | Purpose | Description |
| :--- | :--- | :--- |
| **AWS CodeStar** | **Unified Orchestration** | Provides a single dashboard to set up your project, integrating source control, CI/CD, and deployment in one UI. |
| **AWS CodePipeline** | **Workflow Automation** | The "glue" that connects the stages. It triggers the build when code is pushed and coordinates the move from test to production. |
| **AWS CodeBuild** | **Managed Compilation** | A fully managed build service that compiles code, runs tests, and creates deployable artifacts (like Docker images) without needing to manage build servers. |
| **AWS CodeDeploy** | **Deployment Automation** | Handles the actual rollout of the application to EC2, Lambda, or ECS, supporting strategies like "Blue/Green" to ensure zero downtime. |

## Infrastructure Automation and Serverless

Beyond the application code, AWS provides tools to manage the environment the code runs in.

### Container and Serverless Platforms
- **Elastic Container Service (ECS)**: A highly scalable container management service that allows you to run Docker containers without managing a full Kubernetes cluster.
- **AWS Lambda**: The pinnacle of "NoOps." Lambda allows you to deploy code as functions (FaaS), where AWS handles all infrastructure, scaling, and availability.

### Infrastructure as Code (IaC)
- **AWS CloudFormation**: The native AWS tool for defining infrastructure as code. You describe your resources (VPCs, S3 buckets, EC2) in a JSON or YAML template, and CloudFormation provisions them as a single "stack."
- **AWS OpsWorks**: A configuration management service that uses Chef or Puppet to automate how servers are configured, deployed, and managed.

## Observability: Monitoring and Logging on AWS

A DevOps pipeline is incomplete without a feedback loop. AWS provides tools to ensure your application is healthy and performing as expected.

### Amazon CloudWatch
CloudWatch is the central nervous system for monitoring. It:
- **Collects Metrics**: Tracks CPU usage, disk I/O, and custom application metrics.
- **Centralizes Logs**: Gathers logs from all EC2 instances and Lambda functions into one searchable place.
- **Sets Alarms**: Triggers notifications or automatic scaling actions when a threshold is met (e.g., "Scale up if CPU > 70%").

### AWS X-Ray
While CloudWatch tells you *that* a system is slow, X-Ray tells you *where* it is slow. X-Ray provides distributed tracing, allowing you to follow a single request as it travels through multiple microservices, helping you pinpoint the exact bottleneck in a complex architecture.

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the difference between CodeBuild and CodeDeploy?"
    **CodeBuild** is a managed build service that compiles source code, runs tests, and produces deployable artifacts (like Docker images) without the need to manage build servers. **CodeDeploy** is a deployment service that automates the rollout of those artifacts to compute services like EC2, AWS Lambda, or Amazon ECS, supporting strategies like Blue/Green deployments to ensure zero downtime.

??? question "How does CodePipeline orchestrate a CI/CD workflow?"
    **CodePipeline** acts as the orchestration \"glue\" that connects the various stages of the software delivery lifecycle. It monitors the source control for changes, triggers the build process in CodeBuild, and coordinates the movement of verified artifacts through testing and eventually into production via CodeDeploy.

??? question "What is the difference between CloudFormation (provisioning) and OpsWorks (configuration)?"
    **CloudFormation** is used for *provisioning* infrastructure; it uses templates to create and manage a stack of AWS resources (e.g., VPCs, S3 buckets, EC2 instances). **OpsWorks** is used for *configuration management*; it uses Chef or Puppet to manage the internal state of those servers, such as installing software packages and configuring OS settings.

??? question "When should I use CloudWatch versus AWS X-Ray?"
    Use **CloudWatch** for general monitoring and alerting; it collects metrics (CPU, memory), centralizes logs, and triggers alarms when thresholds are exceeded. Use **AWS X-Ray** for distributed tracing; it allows you to follow a single request across multiple microservices to pinpoint the exact location of a performance bottleneck or failure.

??? question "What is the 'NoOps' benefit of AWS Lambda?"
    AWS Lambda enables a \"NoOps\" (No Operations) model because it is a serverless platform. AWS handles all the underlying infrastructure management, including server provisioning, patching, scaling, and high availability. Developers only need to upload their code as functions, removing the operational burden of managing servers.

!!! note "Exercise 1: Pipeline Design"
    Design a CI/CD pipeline for a Flask application. Specify which AWS CodeSuite tools you would use for:
    1. Triggering the build from GitHub.
    2. Running the unit tests.
    3. Deploying the app to an ECS cluster.
    4. Notifying the team via email if the deployment fails.

!!! note "Exercise 2: Monitoring Strategy"
    You have a microservice architecture with five different services. One of your users reports that "the app feels slow." Describe how you would use Amazon CloudWatch and AWS X-Ray together to find the root cause.

!!! note "Exercise 3: IaC Comparison"
    Compare AWS CloudFormation with HashiCorp Terraform. What are the pros and cons of using a cloud-specific tool (CloudFormation) versus a cloud-agnostic tool (Terraform)?
