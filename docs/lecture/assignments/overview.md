---
title: "Assignments and Project Guidelines"
---

## Learning Objectives

!!! info "Learning Objectives"
    - Understand the technical and academic requirements for course assignments and the final project.
    - Apply DevOps principles (automation, reproducibility, and version control) to all submissions.
    - Manage cloud resources responsibly to avoid costs and resource exhaustion.
    - Implement security best practices for credential management in public repositories.

## Overview

To ensure a high standard of technical rigor and innovation, all students must adhere to the following requirements for course assignments and the final project. These guidelines are designed to foster professional development in cloud computing, AI, and DevOps.

## Core Sections

### 1. Project Scope and Innovation

The final project is a cornerstone of the course and must demonstrate a non-trivial application of the concepts learned.

- **Project Approval**: Students must work with the instructor throughout the semester to obtain formal project approval.
- **Prohibited Topics**: Projects centered on *recommender system analysis* are strictly disallowed. Students are expected to pursue more original and technically challenging research directions.
- **Novelty**: Projects must address a specific, non-trivial problem. Examples include benchmarking AI models across different cloud architectures, implementing custom distributed systems, or optimizing high-performance computing (HPC) workflows. Simple website deployments are not sufficient.
- **Academic Integrity**: In accordance with University Policies, the same project cannot be submitted in multiple classes. Significant extensions are required if building upon previous work.
- **Automation Requirement**: Regardless of the cloud provider used, the deployment and management of containers or Virtual Machines (VMs) must be **fully automated**.
- **Interface Requirement**: All interactions must be possible via Command Line Interface (CLI) or API. Use of a Graphical User Interface (GUI) requires a technical justification within the project documentation.
- **Reproducibility**: Projects must include a `README.md` and automation scripts (e.g., Terraform, Ansible, or Shell scripts) that allow a grader to recreate the entire environment and results through a clearly defined sequence of non-interactive steps.
- **Version Control**: Git must be used for every assignment. Frequent, atomic commits are required to provide a "paper trail" of progress.

!!! note "Repository"
    Students will be provided with an open-source git repository set up by the instructor for their work.

### 2. Resource Management and Liability

Students are encouraged to use a variety of environments, but must do so responsibly.

- **Local Simulation**: The use of a local computer to simulate a cloud environment is permitted.
- **Employer Equipment**: Using employer-provided equipment for coursework may violate corporate IT policies. The university and the instructor are not responsible for any disciplinary actions resulting from the use of company hardware.
- **Hardware Recommendations**: While Raspberry Pis are useful, "Mini PCs" (refurbished enterprise small-form-factor PCs) are recommended for local cloud simulation due to superior compute power, RAM, and virtualization support (VT-x/AMD-V).
- **Cost Responsibility**: Students are solely responsible for all costs incurred through the use of remote or commercial cloud resources.
- **Resource Abuse**: Careless resource management that exhausts class-assigned resources on ACCESS CI or Chameleon Cloud—thereby impacting other students—will result in a failing grade ("F"). 

!!! warning "Resource Management Incident"
    In previous iterations of this course, a student abused the system by starting thousands of unused VMs, consuming 20,000 hours of compute time in a few days. This resulted in all students losing access to the cloud resources. This policy exists to protect the shared resource pool for the entire class.

- **Data Management**: Do not upload raw data, container images, or VM disks to GitHub. Upload only the scripts required to create and manage them. Utilize a `.gitignore` file to prevent accidental uploads.

### 3. Security and Ethics

- **Security Protocols**: Students must implement best practices for identity protection, including the use of IAM roles and billing alerts. Storing passwords or sensitive credentials in public repositories (GitHub, DockerHub) will result in a grade reduction.
- **Data Privacy**: Datasets used in projects must be in the public domain or used with explicit rights. Sensitive personal data or proprietary company information must never be uploaded to public cloud buckets or repositories.

### 4. Collaboration

Collaboration is encouraged, provided the scale and complexity of the project match the group size. The current limit for project groups is two students.

### 5. General Tips

- **Backup Strategy**: Regularly back up all work to a combination of local storage and cloud services (e.g., GitHub).
- **LLMs as Assistants**: Large Language Models (LLMs) may be used for debugging or clarifying concepts. However, they frequently hallucinate technical specifications or use outdated API syntax. Students are responsible for the correctness of all submitted code. Unverified LLM-generated security configurations are high-risk and may lead to system failure.
- **Credit Monitoring**: For those using "Free Tiers" (AWS, Azure, GCP), set up **Billing Alarms** immediately. These tiers have strict limits and expiration dates.

## Summary Checklist

- [ ] Obtain formal project approval from the instructor.
- [ ] Ensure the project topic is not a prohibited recommender system.
- [ ] Implement full automation for all VM/container deployments.
- [ ] Verify that all project interactions are possible via CLI or API.
- [ ] Provide a `README.md` that enables a single-command environment recreation.
- [ ] Set up billing alarms for all commercial cloud accounts.
- [ ] Confirm that no sensitive credentials are stored in the git repository.

## Assignments

!!! note "Assignment 1: Environment Setup"
    Set up your local development environment, including Git, a chosen hypervisor, and the necessary CLI tools for your target cloud providers.

!!! note "Assignment 2: Project Proposal"
    Draft a project proposal including a title, architectural diagram, and a description of the non-trivial problem you intend to solve.

## References

- [University Academic Integrity Policy](https://example.edu/policy)
- [GitHub Documentation](https://docs.github.com/)
- [Terraform Documentation](https://developer.hashicorp.com/terraform)

## Self-Evaluation

??? note "What is the 'Automation Requirement' for the final project?"
    All deployments and management of containers or Virtual Machines must be fully automated using scripts (e.g., Terraform, Ansible, Shell), meaning a grader can recreate the environment without manual GUI intervention.

??? note "What happens if a student exhausts shared cloud resources through negligence?"
    Due to the shared nature of the allocations on ACCESS CI and Chameleon Cloud, resource abuse that impacts other students' ability to work will result in a failing grade ("F").

??? note "How should sensitive credentials like API keys be handled in a public GitHub repository?"
    Sensitive credentials must never be stored in the repository. Instead, use environment variables, secret management tools, or IAM roles, and ensure a `.gitignore` file is used to prevent accidental commits.
