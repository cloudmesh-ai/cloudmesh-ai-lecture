# Modern DevOps and Cloud Automation

Welcome to the DevOps section of the course. This chapter explores how to bridge the gap between software development and IT operations to deliver high-quality software reliably and consistently.

## Chapter Map

### Part I: Foundations of DevOps

* **[Introduction to DevOps](devops.md)**: The core philosophy, the DevOps lifecycle, and the importance of feedback loops.
* **[DevOps and Organizational Culture](devops-team.md)**: Conway's Law, Team Topologies, and Collaborative Engineering.

### Part II: Infrastructure as Code (IaC)

* **[The Core of IaC](devops-iac.md)**: Declarative vs. Procedural approaches and the concept of idempotence.
* **[Server Provisioning with Terraform](terraform.md)**: Managing cloud resources with HCL and state files.
* **[Configuration Management with Ansible](ansible.md)**: Agentless automation and playbook-driven configuration.
* **[Enterprise Scale with Puppet](puppet.md)**: The pull-based model and state enforcement at scale.
* **[Dynamic Configuration with Jinja2](devops-jinja2.md)**: Using templates to make infrastructure DRY and dynamic.

### Part III: Continuous Integration and Delivery (CI/CD)

* **[The CI/CD/CM Framework](devop-ci.md)**: Understanding the integrated pipeline from Continuous Development to Continuous Improvement.
* **[Task Automation with Make](make.md)**: Using Makefiles as the "glue" for local and remote automation.
* **[CI/CD Tooling Landscape](ci-cd-comparison.md)**: A comparative look at modern orchestration tools.
    * **[GitHub Actions](github-workflows.md)**: Event-driven automation integrated into source control.
    * **[Jenkins](jenkins.md)**: The universal, extensible automation orchestrator.
    * **[CircleCI](circleci.md)**: Managed, container-first CI/CD.
    * **[Travis CI](travis.md)**: Configuration-as-code for open source.

### Part IV: Cloud-Native Implementation & Observability

* **[GitOps Fundamentals](gitops-fundamentals.md)**: The "single source of truth" model and pull-based synchronization.
* **[DevOps on AWS](devop-aws.md)**: Leveraging the AWS CodeSuite for a unified toolchain.
* **[Observability with Azure Monitor](devop-azure-monitor.md)**: Moving from reactive monitoring to proactive observability.

### Part V: DevSecOps and Hardening

* **[DevSecOps Fundamentals](devsecops.md)**: Policy as Code, secrets management, and the shift-left philosophy.
* **[Securing the Pipeline](github-workflow-security.md)**: Implementation details for GitHub Actions and supply chain security.

### Part VI: AI and the Future of DevOps

* **[AI-Augmented DevOps](ai-devops.md)**: From "Syntax Writer" to "Architectural Reviewer"—leveraging LLMs for IaC, AIOps, and automated pipelines.

---

## Practical Lab

For students wanting to try these tools locally, please refer to the **[Local Lab Guide](local-lab.md)**.
