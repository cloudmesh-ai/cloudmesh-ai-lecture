# Ansible in the Age of Kubernetes and Docker

!!! info "Learning Objectives"
    - Compare the roles of Ansible, Docker, and Kubernetes in a modern DevOps stack.
    - Identify specific scenarios where Ansible is essential even in containerized environments.
    - Understand the concept of "bootstrapping" infrastructure.
    - Determine when to use a managed cloud service versus self-managed infrastructure.

A common question for developers moving to the cloud is: *"If I'm using Docker and Kubernetes, do I still need a configuration management tool like Ansible?"*

The answer depends on which layer of your infrastructure you are managing. While these tools are often discussed together, they solve fundamentally different problems and are complementary rather than interchangeable.

### The DevOps Trinity

To understand why you might need all three, consider their primary roles:

| Tool | Primary Role | Analogy |
| :--- | :--- | :--- |
| **Docker** | **Packaging**: Wraps an application and its dependencies into a portable container. | The "shipping container" that holds the goods. |
| **Kubernetes** | **Orchestration**: Manages the deployment, scaling, and networking of those containers across a cluster. | The "crane and ship captain" managing the containers. |
| **Ansible** | **Provisioning**: Sets up the underlying servers, OS, and network settings that allow Kubernetes to run. | The "dockyard" building the pier and installing the electricity. |

!!! info "Why this matters"
    Containers abstract the application from the OS, but they do not abstract the *hardware or the VM* from the cloud provider. Someone still has to install the OS, configure the firewall, set up the container runtime (like containerd), and join the node to the Kubernetes cluster. This "bootstrapping" phase is where Ansible excels.

## When Ansible is Essential

Even in a "Kubernetes-first" world, Ansible is critical for the following tasks:

- **Provisioning and Bootstrapping Nodes**: Setting up raw virtual machines on AWS, GCP, or Azure. This includes installing OS dependencies, security hardening, and preparing the machine to join a K8s cluster.
- **Managing Non-Containerized Infrastructure**: Not everything can be a container. You still need to configure physical load balancers, external database clusters, storage arrays, or corporate monitoring agents that must run directly on the host OS.
- **Day-2 Infrastructure Operations**: Automating critical OS-level tasks such as kernel updates, disk partitioning, or managing SSH access and user accounts across your cluster nodes.
- **Cluster Bootstrapping (GitOps)**: Using tools like **Kubespray** (which is built on Ansible) to provision the Kubernetes cluster itself from scratch.

## When You Can Skip Ansible

You may find that you don't need Ansible if your environment fits these criteria:

1.  **Fully Managed Kubernetes**: If you use AWS EKS, Google GKE, or Azure AKS, the cloud provider manages the underlying worker nodes for you. You interact with the API, and the provider handles the OS and runtime.
2.  **Pure Immutable Infrastructure**: If you use Terraform to create "Golden Images" (via Packer) that already have everything installed, and you replace the entire VM whenever a change is needed rather than updating it in place.
3.  **Pure GitOps**: If you use ArgoCD or Flux to manage everything *inside* the cluster, and your cluster was provisioned via a managed service.

# Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "How do I distinguish between packaging (Docker), orchestration (Kubernetes), and provisioning (Ansible)?"
    **Packaging** (Docker) focuses on bundling an application and its dependencies into a portable container. **Orchestration** (Kubernetes) manages the deployment, scaling, and networking of those containers across a cluster. **Provisioning** (Ansible) handles the setup of the underlying servers, operating systems, and network settings that allow the orchestration layer to run.

??? question "What does 'bootstrapping a node' mean in a DevOps context?"
    Bootstrapping a node is the process of taking a "vanilla" or raw virtual machine and installing the necessary OS dependencies, performing security hardening, and setting up the container runtime (like containerd) so that the node can successfully join a Kubernetes cluster.

??? question "What are three tasks that still require Ansible even if the application is containerized?"
    1. **Provisioning raw VMs**: Setting up the base OS on AWS, GCP, or Azure.
    2. **Managing non-containerized infrastructure**: Configuring physical load balancers, external databases, or storage arrays.
    3. **Day-2 Operations**: Performing OS-level maintenance like kernel updates, disk partitioning, or managing SSH access.

??? question "When does a managed service (like EKS, GKE, or AKS) remove the need for manual provisioning?"
    Managed services remove the need for manual provisioning because the cloud provider manages the underlying worker nodes' operating system, security patches, and container runtime. The user interacts with the Kubernetes API, and the provider handles the "bootstrapping" and maintenance of the nodes.

!!! note "Assignment 1: Infrastructure Audit"
    Look at a hypothetical architecture consisting of: an AWS VPC, three EC2 instances running a K8s cluster, an external RDS database, and an S3 bucket. Identify which parts of this architecture would be managed by Terraform, which by Ansible, and which by Kubernetes.

!!! note "Assignment 2: Bootstrapping Workflow"
    Describe the sequence of events required to take a "vanilla" Ubuntu VM and turn it into a Kubernetes worker node. Which of these steps are "provisioning" (Ansible) and which are "orchestration" (Kubernetes)?

!!! note "Assignment 3: Managed vs. Self-Managed"
    Compare the operational overhead of managing a K8s cluster via Kubespray (Ansible) versus using Google GKE. List two advantages and two disadvantages of each approach.
