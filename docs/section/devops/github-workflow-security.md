# Securing Your Automation: GitHub Actions Security

!!! info "Learning Objectives"
    - Identify the primary security vulnerabilities associated with CI/CD pipelines.
    - Implement best practices for managing GitHub Secrets to prevent leakage.
    - Understand the risks of third-party actions and how to mitigate supply chain attacks.
    - Distinguish between `pull_request` and `pull_request_target` triggers.
    - Apply the Principle of Least Privilege to the `GITHUB_TOKEN`.
    - Evaluate the security trade-offs of provisioning cloud VMs directly from GitHub Actions.

As organizations shift toward "everything as code," the CI/CD pipeline becomes the most critical piece of infrastructure. Because a GitHub Action often has the power to deploy code to production, access databases, and manage cloud resources, it is a **high-value target** for attackers. A single compromised workflow or a leaked secret can lead to a full-scale cloud breach.

## 1. Secrets Management and the Risk of Leakage

Secrets (API keys, SSH keys, passwords) are the keys to your kingdom. If they are leaked, your security is gone.

### Common Leakage Scenarios
- **Logging Secrets**: Using `echo` or printing a variable that contains a secret. While GitHub attempts to mask secrets in logs (replacing them with `***`), an attacker can bypass this by encoding the secret (e.g., Base64) or printing it character by character.
- **Insecure Variable Passing**: Passing secrets as environment variables to scripts that might log their environment or crash and dump a core file.
- **Commit History**: Accidentally committing a secret to the repository before moving it to GitHub Secrets.

### Best Practices for Secrets
- **Use GitHub Secrets**: Never hardcode credentials. Store them in **Settings $\rightarrow$ Secrets and variables $\rightarrow$ Actions**.
- **Avoid `echo`**: Never print secrets. If you must debug, use a tool that masks output or a dedicated secret-scanning tool.
- **Rotation**: Regularly rotate your secrets. If a developer leaves the team or a laptop is lost, change the keys immediately.

## 2. Supply Chain Security: Third-Party Actions

Most developers use community-made actions (e.g., `actions/checkout` or `docker/login-action`). This introduces a **supply chain risk**: if the maintainer of a popular action is compromised, they could push a malicious update that steals your secrets.

### The Danger of Version Tags
Most people use tags to version actions:
```yaml
- uses: actions/checkout@v4 # DANGEROUS
```
Tags are **mutable**. An attacker who gains access to the `actions/checkout` repository can move the `v4` tag to a malicious commit, and your pipeline will automatically pull the malicious code on the next run.

### The Solution: Commit SHA Pinning
The only way to guarantee that the code you are running is the code you reviewed is to pin the action to a specific **Commit SHA**.

```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477ut # Fixed SHA for v4.1.1
```
While SHAs are harder to read, they are **immutable**. To keep things maintainable, many teams use a dependency bot (like Dependabot) to automatically update these SHAs.

## 3. The `pull_request` vs. `pull_request_target` Trap

Understanding how GitHub handles permissions for different events is critical to preventing **Privilege Escalation**.

### `on: pull_request` (Safe)
When a workflow is triggered by a PR from a fork, it runs in the context of the **merge commit**. It has **read-only** access to the repository and **no access** to secrets. This is the safe default.

### `on: pull_request_target` (Dangerous)
This event triggers the workflow in the context of the **base branch** (usually `main`). It has **write access** and **access to secrets**.
**The Risk**: If your `pull_request_target` workflow checks out the code from the PR and then runs a script from that code, an attacker can submit a PR that modifies that script to steal your secrets and send them to a remote server.

**Rule of Thumb**: Never use `pull_request_target` to execute code provided by a contributor unless you have a very strict review process.

## 4. The Principle of Least Privilege: `GITHUB_TOKEN`

Every workflow is automatically provided with a `GITHUB_TOKEN`. By default, this token may have broad permissions.

### Hardening the Token
You should explicitly define the permissions your workflow needs at the top of your YAML file. If your workflow only needs to read the code and push to the `gh-pages` branch, do not give it full write access to the entire repository.

```yaml
permissions:
  contents: read   # Can read the repo
  pages: write     # Can update GitHub Pages
  id-token: write  # Required for OIDC cloud authentication
```

## 5. Runner Security: Hosted vs. Self-Hosted

### GitHub-Hosted Runners
These are clean, ephemeral VMs provided by GitHub. They are generally secure because they are destroyed after every job, preventing "persistence" by an attacker.

### Self-Hosted Runners
When you run an agent on your own server, you gain control but lose isolation:
- **Persistence**: A malicious PR could modify a file on the self-hosted runner's disk, affecting all subsequent jobs.
- **Network Access**: A self-hosted runner often has access to your internal corporate network, making it a prime target for lateral movement.

**Recommendation**: If using self-hosted runners, use **ephemeral runners** (e.g., using the Action Runner Controller on Kubernetes) that are destroyed after a single job.

## 6. Provisioning Cloud VMs via GitHub Actions: The "Should You?" Discussion

A common question in DevOps is: *"Should I use my GitHub Action to spin up a VM in AWS/Azure/GCP for testing or deployment?"*

### The Arguments

| Approach | Pros | Cons |
| :--- | :--- | :--- |
| **Yes, do it** | Fully automated environment; no "snowflake" servers; exact parity between test and prod. | Complexity in lifecycle management; risk of "zombie" VMs that cost money. |
| **No, avoid it** | Simpler pipelines; faster execution (no VM boot time); less secret exposure. | Dependence on static "staging" servers that drift over time. |

### The Verdict: Do it, but do it Right

Provisioning VMs via GitHub Actions is a powerful pattern, but it must follow these three security mandates:

1. **No Static Keys (Use OIDC)**: Never store `AWS_ACCESS_KEY_ID` in GitHub Secrets. Use **OpenID Connect (OIDC)** to allow GitHub to authenticate directly with the cloud provider using a short-lived token.
2. **Use IaC, Not Scripts**: Do not use `curl` or `aws cli` to create VMs. Use **Terraform** or **Ansible**. This ensures that the environment is defined as code and can be destroyed reliably.
3. **Automated Cleanup**: Always implement a "Destroy" step in your workflow. Use a `post` block or a separate "cleanup" job to ensure that no matter if the test fails or passes, the VM is terminated.

```yaml
# Example of the "Correct" way to handle Cloud VMs
jobs:
  test-on-vm:
    runs-on: ubuntu-latest
    permissions:
      id-token: write # Required for OIDC
      contents: read
    steps:
      - uses: actions/checkout@v4
      - name: Provision VM with Terraform
        run: terraform apply -auto-approve
      - name: Run Tests
        run: ./run-tests.sh
      - name: Destroy VM
        if: always() # Ensure cleanup happens even if tests fail
        run: terraform destroy -auto-approve
```

---

## 🎓 Learning Wrap-up

# Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "Why should I pin third-party actions to a specific Commit SHA instead of a version tag?"
    Version tags (like `@v4`) are **mutable**, meaning a maintainer or an attacker who compromises the repository can move the tag to a different, potentially malicious commit. **Commit SHAs** are immutable; pinning to a SHA guarantees that the exact code you reviewed and approved is what actually runs in your pipeline.

??? question "What is the benefit of defining explicit permissions for the GITHUB_TOKEN?"
    Applying the **Principle of Least Privilege** by defining explicit permissions (e.g., `contents: read`) ensures that the `GITHUB_TOKEN` only has the access it absolutely needs. This significantly reduces the blast radius if a third-party action is compromised or if the token is accidentally leaked.

??? question "When should I use pull_request instead of pull_request_target?"
    You should use `on: pull_request` for any workflow that processes untrusted code from a fork. It runs in the context of a merge commit with read-only access and no access to secrets. `on: pull_request_target` is dangerous because it runs in the context of the base branch and has access to secrets, which can be exploited by a malicious contributor to steal credentials.

??? question "How can I prevent secrets from leaking into GitHub Action logs?"
    Secrets should be stored in **GitHub Secrets** and never hardcoded. To prevent leakage, avoid using `echo` or printing variables containing secrets. While GitHub masks secrets with `***`, attackers can bypass this using encoding. The best practice is to use dedicated secret-scanning tools and regularly rotate credentials.

??? question "How does OIDC improve the security of provisioning cloud VMs?"
    **OpenID Connect (OIDC)** eliminates the need to store long-lived, static cloud credentials (like `AWS_ACCESS_KEY_ID`) in GitHub Secrets. Instead, it allows GitHub Actions to authenticate directly with the cloud provider using a short-lived, dynamically generated token, significantly reducing the risk of credential theft.

!!! note "Assignment: The Security Audit"
    Review a public open-source project's `.github/workflows` directory. Identify at least two security weaknesses (e.g., mutable tags, over-privileged tokens, or insecure event triggers) and write a short proposal on how to fix them.
