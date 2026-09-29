# DevSecOps: Security in the Automation Pipeline

Integrating security into the DevOps lifecycle is known as **DevSecOps**. The core philosophy is to **"Shift Left"**—meaning security is no longer a final check performed by a separate team at the end of the project, but is integrated into every single step of the development process.

!!! info "The Shift Left Philosophy"
    In traditional DevOps, security happens *after* the build. In DevSecOps, security happens *during* the code write, the build, and the deployment. By finding a vulnerability in the HCL code before it is applied, you prevent a security hole from ever existing in the real world.

---

## 1. Infrastructure as Code (IaC) Security

When we manage infrastructure with Terraform, the code itself becomes the attack surface. A single line of HCL can accidentally expose an entire database to the public internet.

### Policy as Code (PaC)
To prevent these mistakes, we use **Policy as Code**. These are tools that scan your Terraform files for security misconfigurations *before* you run `terraform apply`.

**Common Industry Tools:**
- **Checkov**: A static analysis tool that checks for hundreds of common misconfigurations.
- **TFLint**: A linter that catches errors that `terraform validate` might miss.
- **Terrascan**: Scans IaC for security vulnerabilities and compliance violations.

### What do these tools look for?
A security scanner will flag your code if it finds:
- **Open Security Groups**: A rule allowing SSH (port 22) or HTTP (port 80) from `0.0.0.0/0` (the entire internet).
- **Public Storage**: An AWS S3 bucket created without "Public Access Block" enabled.
- **Unencrypted Disks**: An EBS volume or RDS database created without encryption enabled.
- **Missing Tags**: Resources without `Owner` or `Environment` tags, which makes auditing impossible.

---

## 2. Secrets Management

A common cause of major data breaches is **Secret Leakage**—when developers accidentally commit API keys, passwords, or SSH keys into a Git repository.

### The Problem with Static Secrets
Using `.env` files or hardcoded environment variables is a start, but it is not secure for production because:
1. The secrets are still stored in plain text on the disk.
2. Rotating a password requires updating every single server and restarting the app.

### The Solution: Dynamic Secrets Management
Professional organizations use a **Secrets Manager** (like HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault).

**How the Professional Workflow Works:**
1. **No Secrets in Git**: The code contains a *reference* to a secret (e.g., `secret/db_password`), not the password itself.
2. **Just-in-Time Retrieval**: When the application starts, it authenticates with the Secrets Manager and fetches the password into memory.
3. **Automatic Rotation**: The Secrets Manager can automatically change the database password every 30 days without the developer needing to update any code.

---

## 3. Pipeline Security & Governance

Security isn't just about the code; it's about *who* can change the infrastructure.

### Protected Branches & Gatekeeping
To prevent an unauthorized change from hitting production:
- **Protected Branches**: The `main` branch is locked. No one can push to it directly.
- **Mandatory Pull Requests**: All changes must be submitted via a PR.
- **Automated Gates**: The CI pipeline runs `Checkov` and `terraform plan`. If the security scan fails or the plan deletes a critical resource, the "Merge" button is disabled.
- **Peer Review**: At least one other engineer must approve the plan before it can be applied.

Refer to [github-workflow-security.md](github-workflow-security.md) for detailed instructions on implementing these protections in GitHub.

---

## Self-Assessment

## Self-Assessment

Test your knowledge of DevSecOps by expanding the questions below.

??? question "What does 'Shift Left' mean in the context of security?"
    **Shift Left** means moving security testing to the earliest possible stage of the software development lifecycle. Instead of testing for vulnerabilities after the app is deployed, you scan the code and the infrastructure definitions during the development phase.

??? question "What is 'Policy as Code' and how does it differ from a standard linter?"
    **Policy as Code** (using tools like Checkov) defines security and compliance rules as code. While a standard linter checks for *style* or *syntax* (e.g., "is this indented correctly?"), Policy as Code checks for *security risk* (e.g., "is this database exposed to the public internet?").

??? question "Why are Secrets Managers preferred over environment variables for production?"
    Secrets Managers provide **centralized control**, **audit logs** (you know exactly who accessed the password), and **automatic rotation**. Environment variables are static, often stored in plain text on the server, and are difficult to change across a large fleet of machines.

??? question "Describe the sequence of a secure Terraform deployment pipeline."
    1. Developer pushes HCL to a feature branch $\rightarrow$ 2. CI runs `terraform fmt`, `validate`, and `Checkov` $\rightarrow$ 3. CI runs `terraform plan` and posts the result to a PR $\rightarrow$ 4. A peer reviews the plan and security report $\rightarrow$ 5. The PR is merged to `main` $\rightarrow$ 6. The pipeline executes `terraform apply`.
