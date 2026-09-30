# Container Security & Hardening

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Identify common security vulnerabilities in container images and runtimes.
    - Implement the principle of "Least Privilege" using rootless containers and non-root users.
    - Understand the role of image scanning and the Software Bill of Materials (SBOM).
    - Configure security contexts and network policies to restrict container capabilities in Kubernetes.
    - Apply AI-specific hardening techniques to mitigate risks like unsafe model deserialization and resource exhaustion.
    - Implement advanced runtime hardening using Seccomp and MAC (AppArmor/SELinux).
    - Verify image integrity and provenance using digital signatures.
    - Identify and mitigate common container breakout vectors.

## Overview

Containers are often perceived as secure because they provide isolation. However, this isolation is not a security boundary in the same way a VM hypervisor is. Containers share the host's kernel; if a process inside a container can exploit a kernel vulnerability, it can potentially "break out" and gain control of the host machine.

Securing a containerized environment requires a "Defense in Depth" strategy that covers the image, the runtime, and the orchestrator.

!!! info "Why this matters"
    In AI and Data Science, we often pull large, pre-built images from public registries (e.g., Docker Hub). These images frequently contain outdated system libraries with known vulnerabilities (CVEs). If an AI model is served via an API in an unhardened container, an attacker could use a vulnerability in a library like `numpy` or a system utility to execute arbitrary code on your compute cluster.

## Core Sections

### Image Security: The Supply Chain

The first line of defense is ensuring that the images you build and pull are trustworthy and minimal.

#### Vulnerability Scanning and SBOM

An **Image Scanner** (e.g., Trivy, Grype, or Snyk) analyzes the layers of an image and compares the installed packages against databases of known vulnerabilities.

- **SBOM (Software Bill of Materials)**: A formal record containing the details of all components and libraries used in building the image. An SBOM allows you to quickly identify if a new vulnerability (like Log4Shell) affects your deployed models.

**Example: Scanning a Local Image with Trivy**

```bash
# Scan a specific image
trivy image python:3.11-slim

# Filter for only Critical vulnerabilities
trivy image --severity CRITICAL python:3.11-slim
```

#### Image Integrity & Provenance: Signing your Images

Scanning an image tells you it's *safe*, but it doesn't tell you it's *authentic*. A sophisticated attacker could replace your scanned image in the registry with a malicious one that has the same tag.

- **Image Signing**: Using tools like **Cosign (Sigstore)**, you can digitally sign your images after they pass the CI pipeline. 
- **Verification**: The deployment target (e.g., a Kubernetes Admission Controller) can be configured to **refuse** any image that does not have a valid signature from your trusted build pipeline. This ensures that only images you explicitly approved can run in production.

#### The Principle of Minimal Images

The more tools you have in your image, the larger the attack surface. 

- **Avoid "Kitchen Sink" Images**: Do not use full OS images if you only need a runtime.
- **Distroless Images**: These images contain only your application and its runtime dependencies—no shell, no package manager, and no `curl`. If an attacker gains entry, they have no tools to explore the system.

### AI-Specific Security Risks

AI and Machine Learning containers introduce unique attack vectors that generic security guides often miss.

- **The AI Attack Chain (Prompt Injection $\rightarrow$ Escape)**: In LLM-powered applications, a "Prompt Injection" attack can trick the model into executing an unintended command. If the application has a vulnerability (like an unsafe `eval()` call or a shell execution), the attacker can move from the prompt to **Remote Code Execution (RCE)**. From there, they will attempt to escalate privileges and execute a **Container Escape** to take over the host. This illustrates why "Defense in Depth" is critical: a secure prompt doesn't stop a kernel bug, and a rootless container stops a prompt injection from becoming a host takeover.
- **The Deserialization Trap**: Loading a model using `pickle` or `joblib` from an untrusted source is an extreme security risk. These libraries can be manipulated to execute arbitrary code during the loading process. **Always use safe formats like Safetensors or ONNX for models sourced from the web.**
- **Adversarial Resource Exhaustion**: AI models often use high-performance C++/CUDA runtimes. Attackers can send specially crafted inputs (e.g., a tensor with an absurdly large dimension or a recursive prompt) that triggers an Out-of-Memory (OOM) crash or a CPU spike. If not managed by strict resource limits (CPU/Memory quotas), a single malicious request can crash the entire container or starve other models on the same GPU.
- **Dependency Bloat**: AI frameworks (PyTorch, TensorFlow) are massive. To avoid inheriting hundreds of unnecessary vulnerabilities, use **Multi-stage Builds** to separate the build-time dependencies from the final runtime artifacts.
- **Prompt Injection as an Entry Point**: For AI agents equipped with tool-access (e.g., a "Python Interpreter" or "Bash Shell" tool), a prompt injection attack can serve as the initial breach. An attacker can trick the LLM into executing a malicious payload via its tools, leading to Remote Code Execution (RCE) within the container. Once RCE is achieved, the attacker can attempt a container breakout using the vectors described below, escalating from a simple prompt to host-level control.

#### Practical Hardening Comparison

**Vulnerable Approach**

```dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y python3 git vim curl
COPY . /app
WORKDIR /app
ENV API_KEY="sk-123456789" # CRITICAL SECURITY FAILURE
CMD ["python3", "main.py"]
```

**Hardened Approach**

```dockerfile
# Stage 1: Build
# Use a full image to get build tools (gcc, make, etc.)
FROM python:3.11-slim AS builder
WORKDIR /app
# Install build-essential for packages that need compilation (e.g., some ML libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production
# Start from a clean slim image - NO build tools are carried over
FROM python:3.11-slim
WORKDIR /app

# Copy only the installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY src/ ./src
ENV PATH=/root/.local/bin:$PATH

# Run as non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "src/main.py"]
```

### Understanding Container Breakouts

Containers are designed for isolation, but they are not "strong" boundaries like Virtual Machines. A **Container Breakout** occurs when a process inside a container manages to execute code on the host operating system.

#### Real-World Case Study: CVE-2024-21626 (runc Breakout)
A critical vulnerability was discovered in `runc` (the low-level runtime used by Docker and Podman) that allowed an attacker to escape the container.
- **The Flaw**: An attacker could create a malicious image that, when run, leaked a file descriptor pointing to the host's `/sys/fs/cgroup` directory.
- **The Breakout**: By utilizing this leaked descriptor, the attacker could traverse the filesystem and gain access to the host's root filesystem, effectively breaking out of the container.
- **The Lesson**: This highlights that security depends not just on the high-level engine (Docker/Podman) but on the **low-level runtime** (`runc`). Keeping the host OS and its container runtimes patched is the only defense against these "zero-day" escapes.

#### Common Breakout Vectors
- **Privileged Containers**: Running a container with the `--privileged` flag is a **CRITICAL SECURITY FAILURE**. It gives the container almost all the capabilities of the host root user, making it trivial to mount the host's hard drive and modify the host's `/etc/shadow` or `/etc/sudoers`.
- **Capability Leaks**: Linux "Capabilities" break down the power of root into smaller pieces. If a container is granted `CAP_SYS_ADMIN` or `CAP_NET_ADMIN`, an attacker can often use these to exploit kernel vulnerabilities and escape.
- **Mount Leaks**: Mounting sensitive host paths (like `/var/run/docker.sock` or `/etc`) into a container allows the container to control the host's Docker daemon or modify system configs.
- **Kernel Vulnerabilities**: Since all containers share the same host kernel, a "zero-day" vulnerability in the kernel's memory management or network stack can be used to trigger a breakout.

!!! info "Case Study: Container Breakout in the Wild (CVE-2019-5736)"
    One of the most famous breakout vulnerabilities was found in `runc`, the low-level runtime used by Docker and Kubernetes.
    
    **The Vulnerability**: An attacker with root access inside a container could overwrite the `runc` binary on the host machine.
    **The Attack Vector**: When a host administrator runs `docker exec` to enter a malicious container, the process inside the container could trick the host's `runc` process into opening a handle to its own binary (`/proc/self/exe`) and then overwriting it with malicious code.
    **The Mitigation**: The fix involved `runc` creating a temporary, sealed copy of itself in memory before execution, ensuring that the binary on disk could not be overwritten during an `exec` operation. This highlights why "Defense in Depth" is critical—even if you trust your images, the runtime itself must be hardened.

**Prevention Strategy**: Always follow the principle of **Least Privilege**. Use rootless containers, avoid `--privileged` at all costs, and keep your host OS kernel patched.

### Runtime Security: Rootless Containers

By default, the Docker daemon runs as `root`. If a process inside the container breaks out, it potentially arrives on the host machine with root privileges.

#### Rootless Mode

**Rootless containers** (supported by Podman and Docker) allow the container engine and the containers themselves to run as a non-privileged user. 

- **User Namespaces**: This technology maps the `root` user inside the container to a non-privileged user on the host. To the application, it looks like it's running as root; to the host OS, it's just another limited user.

#### Advanced Runtime Hardening: Seccomp and MAC

Beyond user namespaces, we can further restrict what a process is allowed to do via kernel-level filters.

- **Seccomp (Secure Computing Mode)**: Seccomp filters the **system calls** (syscalls) a container can make to the host kernel. For example, if your AI model only needs to read files and perform calculations, Seccomp can block the `mount()` or `reboot()` syscalls. If an attacker finds a vulnerability in the application, they cannot use these forbidden syscalls to attack the host.
- **MAC (Mandatory Access Control)**: Tools like **AppArmor** and **SELinux** define a strict security profile for the container. Unlike standard Linux permissions (DAC), MAC can prevent a process from accessing a specific folder or network socket even if that process is running as `root`. 

#### Runtime Security Monitoring: Falco and Tetragon
While Seccomp and MAC provide static boundaries, modern environments use active runtime security tools to detect and block threats in real-time.

- **Falco**: Acts as a "security camera" for your cluster. It uses eBPF to monitor system calls and generates alerts based on behavioral anomalies. It is primarily used for **detection and alerting**.
- **Tetragon**: Built on the same eBPF foundation but focuses on **enforcement**. Unlike Falco, which alerts after an event occurs, Tetragon can block the system call in real-time, preventing the action from completing.

**Example: Detecting a Shell in a Pod (Falco Rule)**
```yaml
- rule: Shell spawned in pod
  desc: Detects when a shell is started inside a container, which is rare for production AI services.
  condition: proc.name = sh or proc.name = bash
  output: "Shell spawned in pod (user=%user.name container_id=%container.id image=%container.image)"
  priority: WARNING
```

**The Hardening Hierarchy**:
`Non-Root User` $\rightarrow$ `User Namespaces` $\rightarrow$ `Seccomp Profiles` $\rightarrow$ `MAC Profiles (AppArmor/SELinux)` $\rightarrow$ `eBPF Monitoring (Falco/Tetragon)`

#### Secret Management

Embedding secrets (API keys, DB passwords) directly in the Dockerfile using `ENV` or `ARG` is a critical failure. Values set via `ENV` are baked into the image layers and can be seen via `docker inspect`.

**The Correct Approach**: Inject secrets at **runtime** using:

- **Kubernetes Secrets**: Mounted as files or environment variables.
- **Vaults**: Fetching secrets from HashiCorp Vault or cloud-native secret managers at startup.
- **Environment Files**: Passing a `.env` file at runtime via `docker run --env-file`.

### Orchestrator Security: Kubernetes Hardening

Once containers are moved to Kubernetes, the security focus shifts to the management of those pods.

#### Security Contexts

A **Security Context** defines the privilege and access control settings for a Pod or Container. Key settings include:

- `runAsNonRoot: true`: Forces the container to run as a non-root user.
- `readOnlyRootFilesystem: true`: Prevents the container from writing to its own filesystem, stopping attackers from installing malware.
- `allowPrivilegeEscalation: false`: Prevents a process from gaining more privileges than its parent.

#### Network Policies

By default, all pods in a Kubernetes cluster can communicate. **Network Policies** act as a firewall for pods, allowing you to restrict traffic. For example, you can configure a policy so that your frontend pod can talk to your AI model pod, but the model pod cannot talk to your internal database.

### Automating Security in the CI/CD Pipeline

Security must be "shifted left" into the build pipeline to prevent vulnerabilities from reaching production.

**Example GitHub Action Snippet for Trivy:**

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

## Summary Checklist

- [ ] **Image Minimalist**: Is the image based on a slim or distroless variant?
- [ ] **No Root**: Does the Dockerfile use a non-privileged `USER`?
- [ ] **Scanned & Signed**: Has the image passed a CVE scan and been digitally signed (e.g., using Cosign)?
- [ ] **Secret-Free**: Are there no `ENV` or `ARG` secrets baked into the image layers?
- [ ] **Safe Loading**: Are AI models loaded using safe formats (e.g., Safetensors) instead of `pickle`?
- [ ] **Resource Quotas**: Are CPU and Memory limits set to prevent adversarial resource exhaustion?
- [ ] **Runtime Hardened**: Are Seccomp profiles or MAC (AppArmor/SELinux) enabled?
- [ ] **ReadOnly**: Is the `readOnlyRootFilesystem` enabled in the Kubernetes security context?
- [ ] **Network Isolated**: Is there a NetworkPolicy restricting traffic to only necessary peers?

## Assignments

!!! note "Assignment.1: Scanning Your Images"
    Install a scanner like **Trivy**. Run a scan on a common AI image (e.g., `pytorch/pytorch:latest`). Identify the number of 'Critical' and 'High' vulnerabilities. Research one of the CVEs and explain how it could be exploited.
    
    ??? tip "Solution: Image Scanning"
        Run `trivy image pytorch/pytorch:latest`. Look for the CVE ID (e.g., CVE-2023-XXXX). Search for the ID on the NVD (National Vulnerability Database) to understand the attack vector.

!!! note "Assignment.2: Hardening a Dockerfile"
    Take a standard Dockerfile and apply four hardening techniques:
    1. Switch to a smaller base image.
    2. Create a non-root user and use the `USER` instruction.
    3. Implement a multi-stage build to ensure build tools (`gcc`, `make`) are not in the final image.
    4. Use `readOnlyRootFilesystem: true` in a mock Kubernetes manifest.
    
    ??? tip "Solution: Hardening"
        Use `python:3.11-slim`, add `RUN useradd -m appuser && USER appuser`, and use a multi-stage build. For Kubernetes, add `securityContext: { readOnlyRootFilesystem: true }` to the container spec.

!!! note "Assignment.3: Image Signing"
    Research the **Cosign** tool from the Sigstore project. Describe the workflow required to sign a container image in a GitHub Action and how a Kubernetes cluster can verify that signature before allowing the pod to start.

!!! note "Assignment.4: The Vulnerable Dockerfile Audit"
    Below is a "Bad Dockerfile" used for an AI inference service. Your task is to identify the **5 critical security failures** in this file and rewrite it as a hardened production image.

    ```dockerfile
    FROM ubuntu:latest
    RUN apt-get update && apt-get install -y python3 git vim gcc make curl
    COPY . /app
    WORKDIR /app
    ENV API_KEY="sk-prod-5566778899" 
    RUN pip3 install torch transformers flask
    CMD ["python3", "app.py"]
    ```
    
    ??? tip "Solution: Security Audit"
        The failures are:
        1. **Base Image**: `ubuntu:latest` is too large and non-deterministic. Use a `-slim` variant.
        2. **Build Tools**: `gcc` and `make` are left in the final image, providing an attacker with compilers. Use a multi-stage build.
        3. **Secrets**: `API_KEY` is baked into the image layers. Use a secret manager or environment variable at runtime.
        4. **Root User**: No `USER` directive is present, meaning the app runs as root.
        5. **Lack of Limits**: No resource constraints are mentioned (though this is usually in the K8s manifest, the image should be optimized for them).

## References

- CIS Benchmarks for Docker and Kubernetes: [cisecurity.org](https://www.cisecurity.org/)
- OWASP Docker Security Cheat Sheet: [cheatsheetseries.owasp.org](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- Trivy Documentation: [aquasecurity.github.io/trivy/](https://aquasecurity.github.io/trivy/)

## Self-Evaluation

??? note "Why is a container not as secure as a Virtual Machine?"
    VMs have their own kernel and are isolated by a hypervisor. Containers share the host's kernel. If the kernel is compromised via a vulnerability, all containers sharing that kernel are potentially at risk.

??? note "What is a 'Distroless' image and why is it secure?"
    A distroless image contains only the application and its minimal runtime dependencies. It removes the shell (`/bin/sh`, `/bin/bash`) and package managers (`apt`, `yum`), meaning an attacker who gains execution has no built-in tools to move laterally through the system.

??? note "How does a User Namespace prevent host compromise?"
    It maps the container's internal root user (UID 0) to a high-numbered, non-privileged UID on the host. Even if an attacker breaks out of the container, they land on the host as a user with almost no permissions.

??? note "What is Seccomp and how does it protect the host?"
    Seccomp (Secure Computing Mode) allows you to restrict the system calls a container can make to the host kernel. By blocking dangerous syscalls (like `mount` or `reboot`), you reduce the attack surface available to a compromised process, making it harder to exploit kernel vulnerabilities.

??? note "Why is image signing critical for production AI pipelines?"
    Scanning ensures an image is safe, but signing ensures it is authentic. Digital signatures (e.g., using Cosign) prevent "registry poisoning" where a malicious actor replaces a trusted image with a compromised one using the same tag. Verification at deployment ensures only approved images run.

## What's Next?

Security is critical, but a secure container is useless if it can't store data or talk to other services. Head over to **[Container Storage & Networking](/section/container/specialized/container-storage-networking.md)** to learn about CNI, CSI, and Persistent Volumes.
