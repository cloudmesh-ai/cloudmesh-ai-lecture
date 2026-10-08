# AWS Containers

!!! info "Learning Objectives"
    - Explain the architectural differences between Amazon ECS and EKS.
    - Configure ECS Task Definitions and Services.
    - Deploy and manage EKS clusters using managed node groups and Fargate profiles.
    - Implement serverless container compute using AWS Fargate.
    - Manage container image lifecycles and security using Amazon ECR.
    - Configure VPC networking and load balancing for containerized workloads.

## Overview

AWS provides a tiered ecosystem for container orchestration and execution, allowing users to choose the level of control versus operational overhead. The primary orchestrators are Amazon Elastic Container Service (ECS), a proprietary AWS-native orchestrator, and Amazon Elastic Kubernetes Service (EKS), a managed Kubernetes offering. Both orchestrators can run on traditional EC2 instances or via AWS Fargate, a serverless compute engine. Image management is centralized in Amazon Elastic Container Registry (ECR), while networking is handled through the VPC CNI and integrated Elastic Load Balancing (ELB).

## Amazon Elastic Container Service (ECS)

ECS is a highly scalable, high-performance container orchestration service that integrates deeply with the AWS ecosystem. It eliminates the complexity of managing a Kubernetes control plane.

### Architecture

The ECS hierarchy consists of clusters, services, and tasks. A cluster is a logical grouping of resources. Within a cluster, services define the desired state of an application, while tasks represent the actual running containers.

### Task Definitions

A Task Definition is a JSON-formatted blueprint that describes one or more containers that form a single application unit. It specifies:

- Container image to use.
- CPU and memory limits.
- Port mappings.
- Environment variables.
- Logging configuration (typically CloudWatch Logs).
- IAM roles for the task and the execution agent.

Example Task Definition snippet:

```yaml
containerDefinitions:
  - name: "web-app"
    image: "123456789012.dkr.ecr.us-east-1.amazonaws.com/web-app:latest"
    cpu: 256
    memory: 512
    portMappings:
      - containerPort: 80
        hostPort: 80
        protocol: "tcp"
    logConfiguration:
      logDriver: "awslogs"
      options:
        awslogs-group: "/ecs/web-app"
        awslogs-region: "us-east-1"
        awslogs-stream-prefix: "ecs"
```

### Services and Tasks

A task is the instantiated version of a task definition. ECS services ensure that the specified number of tasks are running and healthy. If a task fails, the service scheduler automatically replaces it. Services integrate with Application Load Balancers to distribute traffic across tasks across multiple Availability Zones.

## Amazon Elastic Kubernetes Service (EKS)

EKS provides a managed Kubernetes environment, allowing users to run K8s without installing or operating their own control plane.

### Control Plane and Nodes

AWS manages the Kubernetes control plane, including the API server and etcd, across multiple Availability Zones for high availability. Users manage the data plane, which consists of the worker nodes where pods are scheduled.

Nodes can be managed in two ways:

1. Managed Node Groups: AWS automates the provisioning and lifecycle management of EC2 instances.
2. Self-Managed Nodes: Users have full control over the EC2 instances, including custom AMIs.

### Fargate Profiles

EKS supports AWS Fargate, allowing pods to run without managing EC2 instances. A Fargate profile defines which pods should run on Fargate based on Kubernetes namespaces and labels. When a pod matches a profile, EKS provisions the required compute on demand.

### Kubectl Integration

EKS integrates with standard Kubernetes tooling. Authentication is handled via the `aws eks` CLI, which updates the `kubeconfig` file.

```bash
aws eks update-kubeconfig --region us-east-1 --name my-eks-cluster

kubectl get pods -n my-namespace
```

## AWS Fargate

AWS Fargate is a serverless compute engine for containers that works with both ECS and EKS. It removes the need to provision, configure, and scale a cluster of virtual machines.

### Serverless Compute Model

In the Fargate model, the user specifies the CPU and memory requirements at the task or pod level. AWS manages the underlying infrastructure, patching, and scaling. This shifts the operational burden from cluster management to application management.

### Pricing and Use Cases

Fargate pricing is based on the amount of vCPU and memory requested from the time the container starts pulling the image until the task terminates.

Fargate is appropriate for:

- Bursty workloads where scaling EC2 clusters would be too slow.
- Applications where reducing operational overhead is prioritized over fine-grained OS tuning.
- Small-to-medium workloads that do not require the economies of scale provided by reserved EC2 instances.

## Amazon Elastic Container Registry (ECR)

ECR is a fully managed Docker container registry used to store, manage, and deploy container images. It integrates natively with ECS and EKS to provide secure, high-performance image pulls.

For a comprehensive guide on repository types, authentication, image scanning, and lifecycle policies, see the dedicated guide: **[Amazon ECR Detailed Guide](aws-ecr.md)**.

## Networking and Load Balancing

Container networking in AWS relies on the VPC CNI (Container Network Interface) to provide native VPC connectivity.

### VPC CNI

The VPC CNI allows each pod (in EKS) or task (in ECS) to receive a private IP address directly from the VPC subnet. This eliminates the need for overlay networks and allows containers to communicate with other VPC resources (like RDS) using standard security groups.

### Load Balancing

AWS uses Elastic Load Balancing to route external traffic to containers:

- Application Load Balancer (ALB): Operates at Layer 7. It supports path-based and host-based routing, making it ideal for microservices.
- Network Load Balancer (NLB): Operates at Layer 4. It provides ultra-low latency and handles millions of requests per second, suitable for TCP/UDP traffic.

## Summary Checklist

- [ ] Determine orchestrator: ECS for simplicity/AWS-native, EKS for Kubernetes ecosystem.
- [ ] Create ECR repository and push container images.
- [ ] Define resource requirements (CPU/Memory) in Task Definitions or Pod specs.
- [ ] Configure VPC networking: define subnets and security groups for container access.
- [ ] Select compute type: EC2 for control/cost-optimization, Fargate for serverless.
- [ ] Configure Load Balancer: ALB for HTTP/S, NLB for TCP/UDP.
- [ ] Set up health checks and auto-scaling policies.

## Assignments

!!! note "Assignment.1: Serverless Deployment with ECS Fargate"
    Deploy a single-container application to ECS using the Fargate launch type. The application should be accessible via a public IP or Load Balancer.

    ??? tip "Solution: Serverless Deployment with ECS Fargate"
        1. Create an ECS Cluster.
        2. Create a Task Definition selecting "Fargate" as the launch type, specifying CPU (0.25 vCPU) and Memory (0.5 GB).
        3. Create a Service using the Task Definition, selecting Fargate, and configuring the network to use a public subnet with "Auto-assign public IP" enabled.
        4. Deploy the service and retrieve the public IP of the running task.

!!! note "Assignment.2: EKS Cluster Setup"
    Provision an EKS cluster with a managed node group and deploy a sample Nginx deployment using kubectl.

    ??? tip "Solution: EKS Cluster Setup"
        1. Create cluster:
           ```bash
           eksctl create cluster --name my-cluster --region us-east-1 --nodegroup-name standard-nodes --node-type t3.medium --nodes 2
           ```
        2. Create deployment:
           ```bash
           kubectl create deployment nginx-demo --image=nginx
           ```
        3. Expose as LoadBalancer:
           ```bash
           kubectl expose deployment nginx-demo --port=80 --target-port=80 --type=LoadBalancer
           ```

## References

- AWS ECS Documentation: https://docs.aws.amazon.com/ecs/
- AWS EKS Documentation: https://docs.aws.amazon.com/eks/
- AWS Fargate Documentation: https://aws.amazon.com/fargate/
- AWS ECR Documentation: https://docs.aws.amazon.com/ecr/

## Self-Evaluation

??? note "Contrast the operational model of Amazon ECS and Amazon EKS."
    ECS is an AWS-native orchestrator that reduces complexity by removing the need to manage a Kubernetes control plane. It uses Task Definitions and Services to manage containers. EKS is a managed Kubernetes service that provides a standard K8s API, allowing users to leverage the broader Kubernetes ecosystem and tools while AWS manages the control plane availability.

??? note "How does the AWS Fargate pricing model differ from the EC2 launch type?"
    In the EC2 launch type, users pay for the EC2 instances provisioned in the cluster, regardless of how many containers are running on them. In the Fargate model, users pay only for the vCPU and memory resources requested at the task or pod level, billed per second from the time the image pull starts until the container terminates.

??? note "Explain the advantage of the VPC CNI over a traditional container overlay network."
    The VPC CNI assigns actual VPC IP addresses to pods or tasks. This allows containers to be first-class citizens in the VPC, enabling direct communication with other VPC resources using standard AWS Security Groups and avoiding the performance overhead and complexity of encapsulation associated with overlay networks.

## Appendix: Related Resources

The following documents provide additional context and specialized use cases for AWS Kubernetes (EKS) within this course:

- **AI/LLM Infrastructure**:
    - [Hands-on Lab Blueprint](../../llm/new/hands-on-lab-blueprint.md) - Details on provisioning GPU-enabled EKS clusters and using EKS-optimized GPU AMIs.
    - [LLMs as Cloud Native Services](../../llm/new/llms-as-cloud-native-services.md) - Discusses EKS as a platform for self-hosting Large Language Models.
    - [Summary & Quick Start Checklist](../../llm/new/summary-&-quick-start-checklist.md) - Includes EKS GPU node pools as a key infrastructure deliverable.
- **DevOps & Automation**:
    - [Ansible](../../devops/ansible.md) - Discusses EKS in the context of managed service benefits and infrastructure automation.
- **Student Projects**:
    - [Assignment Ideas](../../../../lecture/assignments/ideas.md) - Suggestions for deploying RAG applications and Chat-bots to EKS.
