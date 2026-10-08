# Lecture: DevOps, Infrastructure as Code, and CI/CD Pipelines

## Introduction: The DevOps Imperative
DevOps is not just a set of tools, but a cultural shift that bridges the gap between software development and IT operations. In the context of AI and Cloud infrastructure, DevOps allows us to treat infrastructure as software—versioned, tested, and deployed automatically. This ensures that our environments are reproducible, scalable, and resilient, eliminating the "it works on my machine" problem.

1. We begin with **Foundations**, understanding the collaborative nature of DevOps and the importance of local experimentation.
2. We then move to **Infrastructure as Code (IaC)**, learning how to define servers, networks, and services in declarative files rather than manual clicks.
3. We explore **CI/CD Pipelines**, the engine that automates the building, testing, and deployment of our applications.
4. Finally, we look at **GitOps and DevSecOps**, moving toward a state where the Git repository is the single source of truth for the entire system, with security integrated at every step.

---

## DevOps Foundations
*Focus: Establishing the mindset and environment for automation.*

*   **[DevOps Overview](/section/devops/devops.md)**: Introduction to the DevOps lifecycle, culture, and its role in modern software engineering.
*   **[DevOps Team Dynamics](/section/devops/devops-team.md)**: Understanding the organizational shifts required for effective collaboration between dev and ops.
*   **[Local Lab Setup](/section/devops/local-lab.md)**: Building a safe, local environment to test automation scripts before deploying to production.

## Infrastructure as Code (IaC) & Configuration Management
*Focus: Moving from manual configuration to programmable infrastructure.*

*   **[IaC Fundamentals](/section/devops/devops-iac.md)**: The core concepts of declarative vs. imperative infrastructure and the benefits of version-controlled environments.
*   **[Terraform](/section/devops/terraform.md)**: Using HashiCorp Terraform to provision cloud resources across multiple providers using a consistent language.
*   **[Ansible](/section/devops/ansible.md)**: Learning agentless configuration management to automate the setup of OS-level dependencies and services.
*   **[Jinja2 Templating](/section/devops/devops-jinja2.md)**: Utilizing Jinja2 to create dynamic, parameterized configuration files for Ansible and other tools.
*   **[Puppet](/section/devops/puppet.md)**: Exploring model-driven configuration management for maintaining system state at scale.
*   **[GNU Make](/section/devops/make.md)**: Using `make` to orchestrate local build tasks and simplify complex command-line workflows.

## CI/CD: Continuous Integration & Continuous Deployment
*Focus: Automating the path from code commit to production.*

*   **[CI/CD Fundamentals](/section/devops/devop-ci.md)**: Understanding the pipeline: Build $\rightarrow$ Test $\rightarrow$ Deploy.
*   **[CI/CD Tool Comparison](/section/devops/ci-cd-comparison.md)**: Evaluating the trade-offs between different pipeline orchestrators.
*   **[GitHub Actions](/section/devops/github-workflows.md)**: Implementing native automation within GitHub to trigger workflows on push, pull request, or schedule.
*   **[GitHub Workflow Security](/section/devops/github-workflow-security.md)**: Best practices for securing secrets and preventing malicious code injection in pipelines.
*   **[Jenkins](/section/devops/jenkins.md)**: Setting up and managing the industry-standard, highly extensible automation server.
*   **[Cloud-Native Pipelines](/section/devops/k8s-pipeline.md)**: Integrating CI/CD directly with Kubernetes for automated container deployment.
*   **[Other CI Tools](/section/devops/circleci.md) & [/section/devops/travis.md)**: Brief overview of CircleCI and Travis CI as alternatives for diverse project needs.

## GitOps, DevSecOps, and Observability
*Focus: Ensuring the system is secure, visible, and self-healing.*

*   **[GitOps Fundamentals](/section/devops/gitops-fundamentals.md)**: The evolution of IaC where the Git repository is the desired state of the live system.
*   **[ArgoCD](/section/devops/argocd.md)**: Implementing a declarative GitOps CD tool for Kubernetes to automate synchronization.
*   **[DevSecOps](/section/devops/devsecops.md)**: Shifting security "left" by integrating vulnerability scanning and compliance checks into the pipeline.
*   **[Azure Monitor](/section/devops/devop-azure-monitor.md)**: Implementing observability to track system health and performance in real-time.
*   **[Cloud-Specific DevOps](/section/devops/devop-aws.md)**: Applying DevOps patterns specifically within the AWS ecosystem.

## AI-Powered DevOps
*Focus: The intersection of LLMs and automation.*

*   **[AI for DevOps](/section/devops/ai-devops.md)**: Exploring how Large Language Models (LLMs) can assist in writing IaC, debugging pipelines, and generating documentation.

---

## Appendix: Additional Resources
*These documents provide practical examples, templates, and working notes that complement the main lecture topics.*

*   **[Example DevOps Project](/section/devops/example-devops-project.md)**: A comprehensive walkthrough of a real-world DevOps implementation.
*   **[DevOps TODO List](/section/devops/DEV-OPS-TODO.md)**: A living document of planned improvements and missing components in the DevOps section.
*   **[Configuration Snippets](/section/devops/snippet.j2)**: Practical Jinja2 examples for common configuration tasks.
