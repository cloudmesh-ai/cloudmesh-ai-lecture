# Provisioning Infrastructure with Terraform

!!! info "Learning Objectives"
    - Define Infrastructure as Code (IaC) and the role of Terraform in the DevOps ecosystem.
    - Master the Terraform lifecycle: `init`, `plan`, `apply`, and `destroy`.
    - Write HCL (HashiCorp Configuration Language) to provision cloud resources.
    - Implement infrastructure using multiple providers, including AWS, Docker, and Multipass.
    - Understand the importance of the Terraform state file.

In a modern cloud environment, manually creating servers, databases, and networks through a web console is inefficient and impossible to audit. Terraform, created by HashiCorp, solves this by allowing you to define your entire infrastructure as code. 

Written in Go, Terraform uses a declarative language called HCL (HashiCorp Configuration Language). Unlike procedural scripts that list a sequence of steps, HCL allows you to describe the *desired end-state* of your infrastructure, and Terraform figures out the most efficient way to achieve that state.

!!! info "Why this matters"
    The most critical feature of Terraform is the **State File** (`.tfstate`). Terraform keeps track of every resource it creates. When you change your code, Terraform compares the code against the state file and the actual cloud environment to determine exactly what needs to be added, modified, or deleted. This prevents the accidental duplication of resources and allows for precise infrastructure management.

## The Terraform Workflow

Terraform operates on a consistent four-step lifecycle that ensures changes are predictable and safe.

### 1. Initialization (`terraform init`)
Before running any scripts, you must initialize the project directory. This command downloads the necessary **Providers** (the plugins that allow Terraform to talk to AWS, Azure, etc.) and sets up the backend for the state file.

### 2. Planning (`terraform plan`)
The plan command is a "dry run." It compares your current code against the real-world infrastructure and generates an execution plan.
```bash
terraform plan -out project.tfplan
```
The output shows exactly what will happen (e.g., `+ create`, `~ update`, `- destroy`). Saving the plan to a file ensures that the exact same changes are applied in the next step.

### 3. Application (`terraform apply`)
The apply command executes the plan and makes the changes in the cloud.
```bash
terraform apply project.tfplan
```
Terraform spawns multiple background jobs to create resources in parallel, significantly speeding up the provisioning process.

### 4. Destruction (`terraform destroy`)
When resources are no longer needed, Terraform can tear them down cleanly.
```bash
terraform plan -destroy -out destroy.tfplan
terraform apply destroy.tfplan
```

!!! info "Why this matters"
    The `plan` $\rightarrow$ `apply` workflow is a safety mechanism. In professional environments, the `plan` output is often attached to a Pull Request and reviewed by another engineer before the `apply` command is ever run, preventing costly or catastrophic infrastructure mistakes.

## Practical Example: AWS EC2 Provisioning

To provision a basic virtual machine on AWS, create a file named `main.tf` with the following configuration:

```hcl
provider "aws" {
  access_key = "ACCESS_KEY_HERE"
  secret_key = "SECRET_KEY_HERE"
  region     = "us-east-1"
}

resource "aws_instance" "myec2instance" {
  ami           = "ami-2757f631"
  instance_type = "t2.micro"
}
```

**Key Concepts:**
- **Provider**: The plugin that connects Terraform to the AWS API.
- **Resource**: The specific object you want to create (in this case, an `aws_instance`).
- **Arguments**: Parameters like `ami` and `instance_type` that define the resource's properties.

## Alternative Providers: Docker and Multipass

Terraform is not limited to the cloud; it can manage any resource with an API, including local containers and virtual machines.

### Local Docker Provisioning
You can use Terraform to manage local Docker containers, which is excellent for testing infrastructure code locally.

```hcl
provider "docker" {}

resource "docker_image" "nginx" {
  name = "nginx:latest"
}

resource "docker_container" "nginx" {
  image = docker_image.nginx.image_id
  name  = "tutorial-nginx"
  ports {
    internal = 80
    external = 80
  }
}
```

### Local VM Provisioning with Multipass
Canonical Multipass allows you to spin up Ubuntu VMs on your local machine. Using the `larstobi/multipass` provider, you can manage these VMs declaratively.

```hcl
terraform {
  required_providers {
    multipass = {
      source  = "larstobi/multipass"
      version = "~> 1.4.0"
    }
  }
}

provider "multipass" {}

resource "multipass_instance" "ubuntu_vm" {
  name   = "dev-vm"
  cpus   = 2
  memory = "2GiB"
  disk   = "10GiB"
  image  = "lts"
}

output "vm_ip" {
  value = multipass_instance.ubuntu_vm.ipv4
}
```

!!! info "Why this matters"
    Using local providers like Docker and Multipass allows developers to "shift-left" their infrastructure testing. You can verify that your HCL logic is correct on your laptop before applying it to a production cloud environment, reducing the risk of deployment failures.

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the difference between declarative (Terraform) and procedural (Scripts) IaC?"
    **Declarative IaC** (Terraform) describes the *desired end-state* of the infrastructure (e.g., \"I want 3 web servers and 1 database\"), and the tool automatically determines the most efficient way to reach that state. **Procedural IaC** (Scripts) specifies a precise sequence of steps to perform (e.g., \"Create VM 1, then create VM 2, then install Nginx\"), which can be brittle and prone to errors if run multiple times.

??? question "Can you explain the `init` $\rightarrow$ `plan` $\rightarrow$ `apply` workflow?"
    The workflow ensures changes are safe and predictable: `init` downloads the necessary provider plugins and initializes the state backend; `plan` performs a \"dry run\" by comparing the code to the existing state and printing the exact changes to be made; and `apply` executes those changes in the real-world environment.

??? question "What is the role of the `.tfstate` file in tracking infrastructure?"
    The **`.tfstate` file** acts as Terraform's memory. It maps the resources defined in your HCL code to the actual IDs of the resources created in the cloud. This allows Terraform to determine if a resource needs to be created, updated, or destroyed without having to query the entire cloud API on every run.

??? question "How do you distinguish between a Provider and a Resource in Terraform?"
    A **Provider** is a plugin that allows Terraform to communicate with a specific API (e.g., the `aws` provider for Amazon Web Services or the `docker` provider for Docker). A **Resource** is the specific object managed by that provider (e.g., an `aws_instance` represents a virtual machine, while a `docker_container` represents a container).

??? question "How can Terraform be used to provision both cloud and local resources?"
    Terraform is provider-agnostic, meaning it can use different providers in the same configuration. You can use an AWS provider to provision a cloud-based VPC and EC2 instance, while simultaneously using a Docker or Multipass provider to provision local containers or VMs on your own machine, all using the same HCL language and workflow.

!!! note "Exercise 1: The Lifecycle Challenge"
    Create a Terraform script to provision a local Docker container. Run the `init`, `plan`, and `apply` commands. Once verified, use `terraform destroy` to remove the container and explain what happens to the `.tfstate` file after destruction.

!!! note "Exercise 2: Multi-Provider Architecture"
    Design a Terraform configuration that uses two different providers simultaneously (e.g., one to create a local Multipass VM and another to create a Docker container inside that VM). Describe how Terraform handles the dependencies between these two providers.

!!! note "Exercise 3: State Recovery"
    Imagine your `.tfstate` file was accidentally deleted, but your resources still exist in AWS. Research the `terraform import` command and describe the steps you would take to recover the state file without destroying the existing infrastructure.


!!! note "Exercise 4: Using Terraform on your local computer"

    * Create s terraform local installation script and instructions are provided.
    * Verify if it works on your computer.
    * Contrast your experience with the docker based terraform.
    * Enhance the multipass script with the same services exposed to in the docker example.


# Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the role of the Terraform state file (.tfstate)?"
    The state file acts as a source of truth, mapping your HCL code to the real-world resources created in the cloud. It allows Terraform to track resource IDs, metadata, and dependencies, ensuring that subsequent `plan` and `apply` commands only modify what is necessary and avoid duplicating resources.

??? question "Explain the difference between 'terraform plan' and 'terraform apply'."
    `terraform plan` is a dry run that compares the current state with the desired configuration and outputs the changes that *would* be made without actually executing them. `terraform apply` executes those changes in the cloud to reach the desired state. Using `plan` first allows for verification and review before making actual infrastructure changes.

??? question "Why is a declarative language (HCL) preferred over procedural scripts for infrastructure?"
    A declarative language allows you to describe *what* the infrastructure should look like (the end-state), whereas procedural scripts describe *how* to build it (step-by-step). Declarative tools are inherently more robust because they automatically handle dependencies and can correct \"drift\" by comparing the current state to the desired state.

??? question "How does 'terraform destroy' ensure a clean teardown of resources?"
    `terraform destroy` uses the state file to identify all resources created by the configuration and deletes them in the reverse order of their dependencies. This ensures that components like VMs are removed before the networks they depend on are deleted, preventing orphaned resources and costs.

??? question "What is the benefit of using the 'plan' -> 'apply' workflow in a team environment?"
    In teams, the output of `terraform plan` can be attached to a Pull Request for peer review. This ensures that another engineer validates the intended changes before they are applied to production, reducing the risk of catastrophic mistakes and providing an audit trail of intended infrastructure modifications.


## Further Reading

- **Terraform Up and Running**: A comprehensive guide to professional Terraform patterns.
- **HashiCorp Learn**: Official tutorials and certification paths for Terraform.


---

## Appendix: Local Deployment with Terraform (Docker)

### 0. Clone the Repository
Before running the automation, clone the course repository to your local machine:

```bash
git clone https://github.com/cloudmesh-ai/cloudmesh-ai-lecture.git
cd cloudmesh-ai-lecture
```


While Terraform is typically used for cloud infrastructure, you can use the **Docker Provider** to automate the deployment of this site locally. This ensures that every student is running the site in the exact same containerized environment.

### 1. Local Configuration
Create a file named `local_site.tf` with the following configuration:

```hcl
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "python_site" {
  name = "python:3.11-slim"
}

resource "docker_container" "site_server" {
  image = docker_image.python_site.image_id
  name  = "cloudmesh-ai-site"
  
  ports {
    internal = 8000
    external = 8000
  }

  # We simulate the deployment by running the install and serve commands
  command = [
    "sh", "-c", 
    "pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions && mkdocs serve -a 0.0.0.0:8000"
  ]
  
  # Mount the current directory as a volume so changes are reflected in real-time
  volumes {
    host_path      = "."
    container_path = "/app"
  }
  
  working_dir = "/app"
}

output "site_url" {
  value = "http://localhost:8000"
}
```

### 2. Execution
Run the following commands to launch the site:

```bash
terraform init
terraform apply -auto-approve
```

Once the apply is complete, Terraform will output the URL. You can then open your browser and visit `http://localhost:8000`.

### 3. Destruction
To stop the server and remove the container:

```bash
terraform destroy -auto-approve
```

### Why use Terraform for this?
Unlike a simple shell script, Terraform tracks the **state** of the container. If you change the port mapping in the `.tf` file and run `apply` again, Terraform will intelligently destroy and recreate the container to match the new configuration, ensuring your environment never drifts from the definition.

