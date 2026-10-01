# Modern DevOps and Cloud Automation

<!--start-->
This chapter explores how to bridge the gap between software development and IT operations to deliver high-quality software reliably and consistently.

### Part I: Foundations of DevOps

* **[🔴 Introduction to DevOps](/section/devops/devops.md)**: The core philosophy, the DevOps lifecycle, and the importance of feedback loops.
* **[🔴 DevOps and Organizational Culture](/section/devops/devops-team.md)**: Conway's Law, Team Topologies, and Collaborative Engineering.

### Part II: Infrastructure as Code (IaC)

* **[🔴 The Core of IaC](/section/devops/devops-iac.md)**: Declarative vs. Procedural approaches and the concept of idempotence.
* **[🔴 Server Provisioning with Terraform](/section/devops/terraform.md)**: Managing cloud resources with HCL and state files.
* **[🔴 Configuration Management with Ansible](/section/devops/ansible.md)**: Agentless automation and playbook-driven configuration.
* **[🔴 Enterprise Scale with Puppet](/section/devops/puppet.md)**: The pull-based model and state enforcement at scale.
* **[🔴 Dynamic Configuration with Jinja2](/section/devops/devops-jinja2.md)**: Using templates to make infrastructure DRY and dynamic.

### Part III: Continuous Integration and Delivery (CI/CD)

* **[🔴 The CI/CD/CM Framework](/section/devops/devop-ci.md)**: Understanding the integrated pipeline from Continuous Development to Continuous Improvement.

#### From Local Automation to Global Orchestration
* **[🟢 Task Automation with Make](/section/devops/make.md)**: Using Makefiles as the "glue" for local automation, providing a consistent interface before moving to the cloud.
* **[🔴 CI/CD Tooling Landscape](/section/devops/ci-cd-comparison.md)**: A comparative look at modern orchestrators that scale local automation to the entire organization.
    * **[🔴 GitHub Actions](/section/devops/github-workflows.md)**: Event-driven automation integrated into source control.
    * **[🔴 Jenkins](/section/devops/jenkins.md)**: The universal, extensible automation orchestrator.
    * **[🔴 CircleCI](/section/devops/circleci.md)**: Managed, container-first CI/CD.
    * **[🔴 Travis CI](/section/devops/travis.md)**: Configuration-as-code for open source.

### Part IV: Cloud-Native Implementation & Observability

* **[🔵 GitOps Fundamentals](/section/devops/gitops-fundamentals.md)**: The "single source of truth" model and pull-based synchronization.
* **[🔵 ArgoCD](/section/devops/argocd.md)**: Implementing declarative continuous delivery for Kubernetes clusters.
* **[🔵 DevOps on AWS](/section/devops/devop-aws.md)**: Leveraging the AWS CodeSuite for a unified toolchain.
* **[🔵 Observability with Azure Monitor](/section/devops/devop-azure-monitor.md)**: Moving from reactive monitoring to proactive observability.

### Part V: DevSecOps and Hardening

* **[🔵 DevSecOps Fundamentals](/section/devops/devsecops.md)**: Policy as Code, secrets management, and the shift-left philosophy.
* **[🔵 Securing the Pipeline](/section/devops/github-workflow-security.md)**: Implementation details for GitHub Actions and supply chain security.

### Part VI: AI and the Future of DevOps

* **[🔵 AI-Augmented DevOps](/section/devops/ai-devops.md)**: From "Syntax Writer" to "Architectural Reviewer"—leveraging LLMs for IaC, AIOps, and automated pipelines.

---

### Practical Application

* **[🔵 Example DevOps Project](/section/devops/example-devops-project.md)**: A comprehensive capstone project showing the integration of various DevOps tools from provisioning to monitoring.
* **[🔵 Local Lab Guide](/section/devops/local-lab.md)**: Instructions for students wanting to try these tools locally.

<!--end-->
