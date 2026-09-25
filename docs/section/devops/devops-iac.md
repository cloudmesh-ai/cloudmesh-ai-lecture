# Infrastructure as Code (IaC)

!!! info "Learning Objectives"
    - Define Infrastructure as Code (IaC) and identify its role in modern cloud architectures.
    - Contrast IaC with traditional configuration management.
    - Explain the concept of idempotence and how it prevents environment drift.
    - Evaluate different categories of IaC and provisioning tools.
    - Understand the relationship between IaC and the broader DevOps lifecycle.

In the early days of data centers, provisioning a server meant physically racking hardware and manually installing an operating system. In the cloud era, infrastructure is software. Infrastructure as Code (IaC) is the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools.

IaC allows you to generate, maintain, and destroy application infrastructure—such as servers, storage, and networking—without requiring manual changes. The state of the infrastructure is maintained in version-controlled files.

!!! info "Why this matters"
    Cloud architectures and containers have made IaC mandatory. The sheer volume of components (microservices, load balancers, VPCs, security groups) makes manual management impractical. Without IaC, scaling demands and elasticity (scaling up/down based on load) would be impossible to manage in real-time.

## The Value of a Declarative Approach

Using scripts or declarative descriptions for infrastructure provides several critical advantages over manual configuration:

- **Consistency**: Every environment (Dev, Staging, Production) is an identical replica.
- **Dependency Management**: Tools automatically handle the order of creation (e.g., creating a VPC before the subnet).
- **Replicability**: Entire environments can be spun up or torn down in minutes.
- **Testability**: Infrastructure changes can be tested in a sandbox before being applied to production.
- **Documentation**: The code serves as the living documentation of the infrastructure.
- **Risk Reduction**: Minimizes human error associated with manual "click-ops" in a cloud console.

!!! info "Why this matters"
    Manual changes lead to "snowflake servers"—unique configurations that no one remembers how to reproduce. When a snowflake server crashes, recovery is slow and painful. IaC ensures that servers are "cattle, not pets," meaning any instance can be destroyed and recreated from code instantly.

## IaC and the DevOps Lifecycle

IaC is the engine that powers the "Automated Infrastructure" pillar of DevOps. To achieve a full CI/CD pipeline, IaC must be integrated into the shared version control system alongside the application code.

Typical DevOps workflow:
1. **Provisioning**: Use an IaC tool (e.g., Terraform) to create the virtual network and servers.
2. **Configuration**: Use a Configuration Management tool (e.g., Ansible) to install software, set up users, and apply security patches.
3. **Deployment**: Use a CI/CD tool (e.g., GitHub Actions) to deploy the application code.

!!! info "Why this matters"
    By keeping infrastructure code in the same repository as application code, teams ensure that when a new feature requires a new database version, the infrastructure change and the code change are committed, reviewed, and deployed together as a single atomic unit.

## Comparing Tool Categories

Not all "automation" tools are the same. They generally fall into four categories:

| Category | Examples | Primary Purpose |
|----------|-----------|-----------------|
| **Ad hoc scripts** | Shell, Python, Lua | Simple, one-off tasks. |
| **Configuration Management** | Ansible, Chef, Puppet, SaltStack | Managing software state *inside* the OS. |
| **Server Templating** | Docker, Packer, Vagrant | Creating a frozen image of a server/container. |
| **Server Provisioning** | Terraform, CloudFormation, ARM | Creating the "virtual hardware" (VMs, Networks). |

### Procedural vs. Declarative

A key distinction in IaC is between procedural (imperative) and declarative approaches:

- **Procedural (How)**: You tell the tool the exact steps to take (e.g., "Create a VM, then install Nginx, then open port 80"). If you run this twice, it might fail because the VM already exists.
- **Declarative (What)**: You define the desired end-state (e.g., "I want one VM with Nginx and port 80 open"). The tool compares the current state with the desired state and makes only the necessary changes.

!!! info "Why this matters"
    Declarative tools are far more robust for scale. They handle the complex logic of "if it exists, update it; if it doesn't, create it," reducing the amount of brittle logic developers have to write in their scripts.

## Solving Environment Drift with Idempotence

One of the most dangerous problems in operations is **environment drift**, where servers that were originally identical gradually diverge due to manual hot-fixes and ad-hoc changes. This leads to the "it works on my machine" error.

IaC solves this through **Idempotence**.

An operation is idempotent if performing it multiple times has the same effect as performing it once. In IaC, this means that running the code against an existing environment will either do nothing (if the environment is already correct) or bring it back to the desired state.

!!! info "Why this matters"
    Idempotence guarantees a predictable end-state regardless of the starting state. This allows teams to run their IaC pipelines on a schedule (e.g., every hour) to automatically "heal" any drift and ensure the environment remains secure and compliant.

## IaC Tooling Landscape

### Cloud-Specific Tools
These tools are optimized for a single provider and often support new features the day they are released:
- **AWS**: CloudFormation
- **Google Cloud**: Cloud Deployment Manager
- **Azure**: Azure Resource Manager (ARM)
- **OpenStack**: Heat

### Cloud-Agnostic Tools
**Terraform** is the industry standard for multi-vendor infrastructure. While Terraform scripts are not always portable (the resource definitions for AWS differ from Azure), the *workflow* and *tooling* remain identical across all providers.

# Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is Infrastructure as Code (IaC) and why is it superior to manual provisioning?"
    **Infrastructure as Code (IaC)** is the practice of managing and provisioning computer data centers through machine-readable definition files rather than manual hardware configuration or interactive tools. It is superior because it ensures consistency across environments (Dev, Staging, Prod), enables rapid replicability, reduces human error, and provides a version-controlled history of infrastructure changes.

??? question "What is the difference between procedural (how) and declarative (what) approaches to IaC?"
    A **Procedural** approach requires specifying the exact steps to achieve a goal (e.g., \"Create a VM, then install Nginx, then open port 80\"). A **Declarative** approach defines the desired end-state (e.g., \"I want one VM with Nginx and port 80 open\"), and the tool automatically handles the logic to move the system from its current state to the desired state.

??? question "How do server provisioning (e.g., Terraform) and configuration management (e.g., Ansible) differ?"
    **Server Provisioning** focuses on creating the foundational infrastructure \"hardware\" layers, such as VPCs, subnets, and virtual machines. **Configuration Management** focuses on the \"software\" layer inside those machines, such as installing specific packages, managing user accounts, and implementing security policies.

??? question "What is idempotence and how does it prevent environment drift?"
    **Idempotence** is the property where an operation can be performed multiple times without changing the result beyond the initial application. In IaC, this means running the code against an environment will either do nothing (if the environment is already correct) or fix any deviations, thereby automatically \"healing\" environment drift and ensuring a predictable end-state.

??? question "How do I identify the appropriate IaC tool for a specific cloud provider?"
    Depending on the needs, you can choose **Cloud-Specific tools** (like AWS CloudFormation, Azure ARM, or Google Deployment Manager) for deep integration and immediate support for new provider features, or **Cloud-Agnostic tools** (like Terraform) to maintain a consistent workflow and toolset across multiple cloud vendors.

!!! note "Assignment 1: Procedural vs Declarative"
    Write a simple shell script (procedural) to create a directory and a file. Now, explain why this script is NOT idempotent (what happens if you run it a second time?). Propose how a declarative tool would handle the same task.

!!! note "Assignment 2: Designing a Multi-Cloud Strategy"
    You are tasked with deploying a web app to both AWS and Azure for high availability. List the components you would need to define in your IaC (e.g., VPC, VM, Load Balancer). Discuss whether you would use cloud-specific tools or a tool like Terraform, and justify your choice.

!!! note "Assignment 3: Audit for Environment Drift"
    Imagine you have a production server that was configured manually two years ago. Describe a strategy to bring this server under IaC management without causing downtime. (Hint: Think about "importing" existing state).

## Further Reading

- **Terraform Up and Running**: A practical guide to structuring Terraform code and deployment practices.
- **Infrastructure as Code (Book)**: A deep dive into the theory and application of IaC.
