# Container Security & Hardening

!!! info "Learning Objectives"
    - Identify common security vulnerabilities in container images and runtimes.
    - Implement the principle of "Least Privilege" using rootless containers.
    - Understand the role of image scanning and software bill of materials (SBOM).
    - Configure security contexts to restrict container capabilities in Kubernetes.

Containers are often perceived as secure because they provide isolation. However, this isolation is not a security boundary in the same way a VM hypervisor is. Containers share the host's kernel; if a process inside a container can exploit a kernel vulnerability, it can potentially "break out" and gain control of the host machine.

Securing a containerized environment requires a "Defense in Depth" strategy that covers the image, the runtime, and the orchestrator.

!!! info "Why this matters"
    In AI and Data Science, we often pull large, pre-built images from public registries (e.g., Docker Hub). These images frequently contain outdated system libraries with known vulnerabilities (CVEs). If an AI model is served via an API in an unhardened container, an attacker could use a vulnerability in a library like `numpy` or a system utility to execute arbitrary code on your compute cluster.

## 1. Image Security: The Supply Chain

The first line of defense is ensuring that the images you build and pull are trustworthy and minimal.

### Quick Start: Scanning a Local Image with Trivy
Before integrating scanning into a pipeline, you can manually audit any image on your machine. **Trivy** is the industry standard for this.

1. **Install Trivy** (on Ubuntu/Debian):
   ```bash
   sudo apt-get install wget gnupg
   wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
   echo "deb https://aquasecurity.github.io/trivy-repo/deb ubuntu focal main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
   sudo apt-get update
   sudo apt-get install trivy
   ```

2. **Scan a specific image**:
   ```bash
   trivy image python:3.11-slim
   ```

3. **Filter for only Critical vulnerabilities**:
   ```bash
   trivy image --severity CRITICAL python:3.11-slim
   ```

### Image Scanning and SBOM
An **Image Scanner** (e.g., Trivy, Grype, or Snyk) analyzes the layers of an image and compares the installed packages against databases of known vulnerabilities.
*   **SBOM (Software Bill of Materials)**: A formal record containing the details of all components and libraries used in building the image. An SBOM allows you to quickly identify if a new vulnerability (like Log4Shell) affects your deployed models.

### The Principle of Minimal Images
The more tools you have in your image, the larger the attack surface.
- **Avoid "Kitchen Sink" Images**: Don't use full OS images if you only need a runtime.
- **Distroless Images**: These images contain only your application and its runtime dependencies—no shell, no package manager, no `curl`. If an attacker gains entry, they have no tools to explore the system.

### AI-Specific Security Risks
AI and Machine Learning containers introduce unique attack vectors that generic security guides often miss:

- **The Deserialization Trap**: Loading a model using `pickle` or `joblib` from an untrusted source is an extreme security risk. These libraries can be manipulated to execute arbitrary code during the loading process. **Always use safe formats like Safetensors or ONNX for models from the web.**
- **Dependency Bloat**: AI frameworks (PyTorch, TensorFlow) are massive. To avoid inheriting hundreds of unnecessary vulnerabilities, use **Multi-stage Builds**. Build your dependencies in one stage and copy only the final compiled artifacts to a lean production image.

### Practical Hardening: Before vs. After
Comparing a typical "developer" Dockerfile with a "production-hardened" version:

**❌ Vulnerable Dockerfile**
```dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 git vim curl
COPY . /app
WORKDIR /app
ENV API_KEY="sk-123456789" # CRITICAL SECURITY FAILURE
CMD ["python3", "main.py"]
```

**✅ Hardened Dockerfile**
```dockerfile
# Stage 1: Build
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production
FROM python:3.11-slim
WORKDIR /app
# Copy only the installed packages from builder
COPY --from=builder /root/.local /root/.local
COPY src/ ./src
ENV PATH=/root/.local/bin:$PATH

# Run as non-root user
RUN useradd -m appuser
USER appuser

CMD ["python", "src/main.py"]
```

## 2. Runtime Security: Rootless Containers

By default, the Docker daemon runs as `root`. This means that if a process inside the container manages to break out, it arrives on the host machine with root privileges.

### Rootless Mode
**Rootless containers** (supported by Podman and now Docker) allow the container engine and the containers themselves to run as a non-privileged user. 
- **User Namespaces**: This technology maps the `root` user inside the container to a non-privileged user on the host. To the application, it looks like it's running as root; to the host OS, it's just another limited user.

### Secret Management: Avoid the "Image Leak"
A common mistake is embedding secrets (API keys, DB passwords) directly in the Dockerfile using `ENV` or `ARG`.
**Warning:** Any value set via `ENV` is baked into the image layers. Anyone with access to the image can run `docker inspect` and see your secrets in plain text.

**The Correct Approach**: Inject secrets at **runtime** using:
- **Kubernetes Secrets**: Mounted as files or environment variables.
- **Vaults**: Fetching secrets from HashiCorp Vault or AWS Secrets Manager at startup.
- **Environment Files**: Passing a `.env` file at runtime via `docker run --env-file`.

## 3. Automating Security in the CI/CD Pipeline

Security should not be a manual check at the end of the project; it must be "shifted left" into the build pipeline.

### Integrated Vulnerability Scanning
Instead of scanning images manually, you can integrate tools like **Trivy** directly into your GitHub Actions workflow. This allows you to fail the build automatically if a "CRITICAL" vulnerability is detected.

**Example GitHub Action Snippet:**
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: 'my-ai-app:${{ github.sha }}'
    format: 'table'
    exit-code: '1' # Fail the build if vulnerabilities are found
    ignore-unfixed: true
    severity: 'CRITICAL,HIGH'
```

By adding this step, you ensure that no image with a critical security hole ever reaches your container registry.

## 4. Orchestrator Security: Kubernetes Hardening

Once containers are moved to Kubernetes, the security focus shifts to how they are managed.

### Security Contexts
A **Security Context** defines the privilege and access control settings for a Pod or Container. Key settings include:
- `runAsNonRoot: true`: Forces the container to run as a non-root user.
- `readOnlyRootFilesystem: true`: Prevents the container from writing to its own filesystem, stopping attackers from installing malware or modifying configuration files.
- `allowPrivilegeEscalation: false`: Prevents a process from gaining more privileges than its parent.

### Network Policies
By default, all pods in a Kubernetes cluster can talk to all other pods. **Network Policies** act as a firewall for pods, allowing you to restrict traffic so that, for example, your frontend pod can talk to your AI model pod, but your model pod cannot talk to your internal database.

---

## Container Security Checklist

Before deploying a container to production, verify the following:

- [ ] **Image Minimalist**: Is the image based on a slim or distroless variant?
- [ ] **No Root**: Does the Dockerfile use a non-privileged `USER`?
- [ ] **Scanned**: Has the image been scanned for CVEs in the CI pipeline?
- [ ] **Secret-Free**: Are there no `ENV` or `ARG` secrets baked into the image layers?
- [ ] **Safe Loading**: Are AI models loaded using safe formats (e.g., Safetensors) instead of `pickle`?
- [ ] **ReadOnly**: Is the `readOnlyRootFilesystem` enabled in the Kubernetes security context?
- [ ] **Network Isolated**: Is there a NetworkPolicy restricting traffic to only necessary peers?

## Self-Assessment

Test your knowledge by expanding the questions below.

??? question "Why is a container not as secure as a Virtual Machine?"
    VMs have their own kernel and are isolated by a hypervisor. Containers share the host's kernel. If the kernel is compromised via a vulnerability, all containers sharing that kernel are potentially at risk.

??? question "What is a 'Distroless' image and why is it secure?"
    A distroless image contains only the application and its minimal runtime dependencies. It removes the shell (`/bin/sh`, `/bin/bash`) and package managers (`apt`, `yum`), meaning an attacker who gains execution has no built-in tools to move laterally through the system.

??? question "How does a User Namespace prevent host compromise?"
    It maps the container's internal root user (UID 0) to a high-numbered, non-privileged UID on the host. Even if an attacker breaks out of the container, they land on the host as a user with almost no permissions.

## Assignments

!!! note "Assignment 1: Scanning Your Images"
    Install a scanner like **Trivy**. Run a scan on a common AI image (e.g., `pytorch/pytorch:latest`). Identify the number of 'Critical' and 'High' vulnerabilities. Research one of the CVEs and explain how it could be exploited.

!!! note "Assignment 2: Hardening a Dockerfile"
    Take a standard Dockerfile and apply three hardening techniques:
    1. Switch to a smaller base image.
    2. Create a non-root user and use the `USER` instruction.
    3. Remove unnecessary tools (like `git` or `vim`) after the build phase.

## References

- CIS Benchmarks for Docker and Kubernetes: [cisecurity.org](https://www.cisecurity.org/)
- OWASP Docker Security Cheat Sheet: [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- Trivy Documentation: [aquasecurity.github.io/trivy/](https://aquasecurity.github.io/trivy/)

---

## What's Next?

Security is critical, but a secure container is useless if it can't store data or talk to other services. Head over to **Container Storage & Networking** to learn about CNI, CSI, and Persistent Volumes.
