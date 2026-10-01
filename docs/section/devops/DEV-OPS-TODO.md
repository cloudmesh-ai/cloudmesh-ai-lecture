# DevOps Section: Graduate-Level Gap Analysis & TODO

This document outlines the remaining gaps in the DevOps section from the perspective of a graduate-level engineering course. While the "tooling" is largely covered, a graduate course requires a shift from "how to use a tool" to "why this architectural choice was made" and "how to analyze the trade-offs."

## 1. Theoretical & Architectural Gaps

### A. Theoretical Foundations of Reliability
The current content focuses on *how* to deploy. A graduate student needs to understand the *metrics* of reliability.
- [ ] **SLIs, SLOs, and SLAs**: Create a dedicated guide or expand `devop-azure-monitor.md` to cover Service Level Indicators, Objectives, and Agreements.
- [ ] **Error Budgets**: Explain how SLOs create "Error Budgets" that balance the tension between feature velocity (Dev) and stability (Ops).
- [ ] **The SRE Handbook**: Introduce the concepts of "Toil" and "Automation" from the Google SRE perspective.

### B. Advanced Deployment Strategies
We cover "Push" vs "Pull," but lack a deep dive into risk-mitigation strategies.
- [ ] **Canary vs. Blue-Green vs. Shadow**: Expand `ci-cd-comparison.md` or a new guide to detail the mathematical and operational difference between these three.
- [ ] **Progressive Delivery**: Introduce the concept of "Feature Flags" and "Percentage-based Rollouts" (e.g., using Flagger or Argo Rollouts).

### C. The "State" Problem in IaC
We cover Terraform state, but not the complex "Day 2" operational challenges of state.
- [ ] **State Drift & Remediation**: A deeper dive into how to handle manual changes in production (drift) without destroying resources.
- [ ] **State Locking & Remote Backends**: More detailed guidance on managing state in large teams (S3 + DynamoDB locks).

## 2. Content Coverage Gaps

### A. The "Missing Link" in the Toolchain
- [ ] **Container Registry & Image Lifecycle**: We jump from "Building a Docker Image" to "Deploying to K8s." We need content on **Container Registries** (ECR/GHCR), **Image Scanning** (Trivy/Snyk), and **Image Versioning** (Semantic Versioning vs. Commit SHAs).
- [ ] **Secrets Management (Deep Dive)**: `github-workflow-security.md` covers the *risk*, but we need a guide on *solutions* like **HashiCorp Vault** or **AWS Secrets Manager**.

### B. Tool-Specific Depth
- [ ] **Terraform Modules**: While mentioned, we lack a "Best Practices" guide for structuring modules (Input validation, Output standardization).
- [ ] **Ansible Roles**: Similarly, we need a guide on creating "Enterprise-grade" roles that are portable across different OS distributions.

## 3. Pedagogy & Application Gaps

### A. The "Capstone" Integration
- [ ] **Guided Example Project**: `example-devops-project.md` exists, but it needs to be woven into the chapters. Each chapter should have a "Project Task" that contributes to the final example project.
- [ ] **Case Study Analysis**: Add a real-world "failure" analysis (e.g., a famous cloud outage) and ask students to identify which DevOps principle (Monitoring, IaC, etc.) would have prevented it.

### B. Rigor in Self-Evaluation
- [ ] **Analysis-Based Questions**: Upgrade some "What is X?" questions to "Given scenario Y, why is tool X better than tool Z?"

## 4. Immediate Action Items (Quick Wins)

- [ ] **Update `CHAPTER.md`**: Integrate the new `k8s-pipeline.md` and ensure the flow leads logically to the `example-devops-project.md`.
- [ ] **Fix `make.md`**: Address the `TODO: use clouds.yaml` mentioned in the file.
- [ ] **Standardize remaining files**: Run `/do-chapter` on `jenkins.md`, `circleci.md`, `travis.md`, and `devops.md` to ensure the "Definition of Done" is met for the whole section.
