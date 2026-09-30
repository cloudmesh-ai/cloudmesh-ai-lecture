# Podman

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Install and configure Podman across various operating systems.
    - Execute container operations using the Docker-compatible CLI.
    - Implement secure, rootless containers to enhance host security and reduce attack surfaces.
    - Orchestrate groups of containers using Pods to mirror Kubernetes architecture.
    - Build OCI-compliant images using Dockerfiles and specialized tools like Buildah.
    - Use Skopeo for image inspection and registry management without pulling images.
    - Plan container-based architectures using visualization and mind-mapping techniques.

## Overview

Podman (Pod Manager) is an open-source, daemonless container engine for developing, managing, and running OCI-compliant containers. Unlike traditional container engines, Podman does not rely on a central background process (daemon) to manage containers, which fundamentally changes the security and operational model of the host.

The primary value proposition of Podman is its "rootless" nature. By allowing users to run containers as non-privileged users, Podman significantly reduces the attack surface of the host system. Furthermore, Podman introduces the concept of "Pods"—groups of containers that share a network namespace—bringing a Kubernetes-like orchestration model to the local development environment.

## Core Sections

### Understanding Podman's Architecture

Podman is designed to be a drop-in replacement for the Docker CLI, meaning most commands work identically. However, its internal architecture differs in several critical ways:

- **Daemonless**: There is no background service (`dockerd`) running as root. The `podman` command interacts directly with the container runtime (like `runc` or `crun`).
- **Rootless Execution**: Containers run under the user's own UID. User namespaces are used to map the internal container root user to a non-privileged user on the host.
- **Pod-Centric**: Podman can group containers into "Pods," allowing them to share the same IP address and ports, mirroring the fundamental unit of deployment in Kubernetes.
- **OCI Compliance**: Podman follows the Open Container Initiative (OCI) standards, ensuring that images built with Podman are compatible with other runtimes and registries.

!!! info "Why this matters"
    In a traditional daemon-based architecture, the daemon is a "god process" running as root. If an attacker finds a vulnerability in the daemon, they potentially gain full root access to the host machine. Podman's daemonless architecture removes this single point of failure and this high-value target, making it the preferred choice for high-security production environments.

### Installation and Setup

Podman is available across most major Linux distributions and can be run on macOS and Windows via virtualization layers (such as WSL2).

#### Installation Commands

| OS | Command |
|----|---------|
| **Fedora / RHEL 9** | `sudo dnf -y install podman` |
| **CentOS 8 / Rocky 9** | `sudo dnf -y module enable container-tools && sudo dnf -y install podman` |
| **Ubuntu 22.04+** | `sudo apt update && sudo apt -y install podman` |
| **macOS** (Homebrew) | `brew install podman` |
| **Windows** (WSL2) | Install a Linux distribution in WSL2, then follow the Linux installation steps. |

!!! tip "Verification"
    After installation, run `podman info`. Ensure that `rootless: true` appears in the host information to confirm you are running as a non-privileged user.

### Essential Podman CLI Operations

Because Podman is Docker-compatible, the learning curve for existing users is minimal.

#### Docker $\rightarrow$ Podman Migration Checklist
If you are moving from Docker to Podman, use this checklist to ensure a smooth transition:

- [ ] **CLI Aliasing**: Set up `alias docker=podman` in your `.bashrc` or `.zshrc` to reuse existing scripts.
- [ ] **Rootless Configuration**: Verify your user has entries in `/etc/subuid` and `/etc/subgid` to enable user namespaces.
- [ ] **Volume Permissions**: When mounting host directories, use the `:Z` (private) or `:z` (shared) flags to automatically handle SELinux relabeling.
- [ ] **Registry Search**: Configure `/etc/containers/registries.conf` to include your preferred registries (e.g., `docker.io`, `quay.io`) so you can pull images without the full URL.
- [ ] **Network Setup**: If using complex networking, install `slirp4netns` for rootless network namespace support.

#### Common Commands

| Goal | Podman Command |
|------|----------------|
| List images | `podman images` |
| Pull an image | `podman pull quay.io/centos/centos:stream8` |
| Run interactive | `podman run -it --rm quay.io/centos/centos:stream8 bash` |
| Run in background | `podman run -d --name web -p 8080:80 nginx:alpine` |
| View running | `podman ps` |
| Stop and remove | `podman stop web && podman rm web` |
| Execute inside | `podman exec -it web sh` |
| Copy files | `podman cp <src> <container>:/dest` |

#### Docker Compatibility Shim

If you have existing scripts that depend on the `docker` command, you can create a symbolic link to redirect those calls to Podman:

```bash
sudo ln -s $(which podman) /usr/local/bin/docker
```

*Note: Only use this shim if Docker is not installed on the system.*

### Rootless Containers and Security

Rootless containers are Podman's most significant security feature. By using **User Namespaces**, Podman maps the internal root user of a container to a non-privileged user on the host.

#### How it Works: User Namespaces

When you run a rootless container, the Linux kernel creates a new user namespace. Inside this namespace, the process believes it is running as `UID 0` (root). However, on the host machine, that same process is actually running as your normal user (e.g., `UID 1000`).

!!! info "Why this matters"
    If a process escapes a rootless container, the attacker only gains the permissions of the non-privileged user who started the container. They cannot modify system files, install root-level software, or access other users' data. This effectively isolates the compromise to a single user account rather than the entire physical machine.

```bash
# Verify rootless mode
podman info | grep rootless
# Expected output: rootless: true
```

### Working with Pods

A **Pod** is a group of one or more containers that share the same network namespace. This allows containers within the same pod to communicate via `localhost`.

!!! info "Why this matters"
    In Kubernetes, the smallest deployable unit is a Pod, not a container. By using Pods locally, you can test the exact networking behavior your app will experience in production. For example, a sidecar container (like a log shipper or a proxy) can access the primary application's port without needing complex networking rules.

#### Complex AI Pod Example: API + Monitoring

Imagine an AI inference service that requires a primary API and a sidecar that monitors GPU health.

1. **Create a Pod**:
    ```bash
    podman pod create --name ai-stack -p 8000:8000
    ```

2. **Add the Inference API**:
    ```bash
    podman run -d --pod ai-stack --name inference-api pytorch-api:latest
    ```

3. **Add the Monitoring Sidecar**:
    ```bash
    podman run -d --pod ai-stack --name gpu-monitor nvidia-smi-exporter:latest
    ```

4. **Verification**:
    The `inference-api` can now communicate with the `gpu-monitor` simply by calling `http://localhost:9100`.

### Image Construction and the Podman Ecosystem

Podman supports standard `Dockerfile` syntax but integrates with specialized tools for more advanced image creation.

#### Exporting to Kubernetes: `generate kube`
One of Podman's most powerful features is its ability to serve as a local "prototype" for Kubernetes deployments.

- **`podman generate kube`**: This command analyzes a running pod (and its containers) and generates a Kubernetes-compatible YAML manifest. This allows you to develop your stack locally and then move it to a real cluster with zero changes to the YAML.
- **`podman play kube`**: The reverse operation. You can take a Kubernetes manifest (YAML) and run it locally using Podman. This is an essential tool for testing K8s deployments before pushing them to a cluster.

**Example: Exporting a local AI stack**
```bash
# Create a pod with an API and a Monitor
podman pod create --name ai-stack -p 8000:8000
podman run -d --pod ai-stack --name api my-model-api
podman run -d --pod ai-stack --name monitor gpu-exporter

# Generate the K8s YAML
podman generate kube ai-stack > ai-stack-k8s.yaml
```

#### Specialized Tools: Buildah and Skopeo

While `podman build` is great for simple cases, professional container engineers often use specialized tools:

- **Buildah**: A tool for building OCI images without requiring a daemon. Buildah allows for more granular control. For example, you can mount a container's filesystem to your host and use standard shell commands to modify it without needing a `Dockerfile` for every single change.
  - *Use Case*: Creating a minimal "scratch" image where you only copy in a single binary.

- **Skopeo**: A utility for inspecting, copying, and managing images between different registries.
  - *Use Case*: Copying an image from a private corporate registry to a public one without needing to `pull` it to your local machine first.
  - *Example*: `skopeo copy docker://registry.internal/my-app:v1 docker://quay.io/my-user/my-app:v1`

### Architecture Planning with Visualization

Before implementing a containerized system, it is best practice to map the architecture. Mind-mapping helps distill complex systems into a clear hierarchy of services and dependencies.

#### Recommended Planning Tools
| Tool | Use Case |
|------|-----------|
| **XMind / FreeMind** | Polished layouts for radial architecture maps. |
| **MindMeister** | Collaborative, web-based planning. |
| **Obsidian** | Markdown-based knowledge graphs for technical documentation. |

#### Best Practices for Architecture Mapping
- **Distillation**: Use one word per branch to force clarity.
- **Layering**: Use color coding to distinguish between Frontend, Backend, and Data layers.
- **Iteration**: Start with a brainstorm, then group related services into Pods or clusters.

::: tip "From Map to Manifest"
    Once your mind-map is complete, each "leaf" node becomes a service in your `podman-compose.yml` or a container in a Pod. The links between nodes define your `depends_on` relationships and network requirements.
:::

## Summary Checklist

- [ ] Install Podman and verify rootless mode with `podman info`.
- [ ] Execute a basic container using the Docker-compatible CLI.
- [ ] Explain how User Namespaces enable rootless containers.
- [ ] Create a Pod and deploy multiple containers into it.
- [ ] Communicate between two containers in the same Pod via `localhost`.
- [ ] Build an OCI-compliant image using a `Dockerfile`.
- [ ] Distinguish between the roles of Podman, Buildah, and Skopeo.
- [ ] Map a multi-tier application architecture using a mind-map.

## Assignments

!!! note "Assignment.1: Rootless Verification"
    Install Podman on your system and verify that it is running in rootless mode. Explain the security benefit of this configuration.
    
    ??? tip "Solution: Rootless Verification"
        Run `podman info | grep rootless`. The output should be `rootless: true`. The benefit is that a container escape does not grant root access to the host machine.

!!! note "Assignment.2: Pod Deployment"
    Create a Pod named `web-stack`. Deploy an NGINX container and a Redis container into the same Pod. Verify that the NGINX container can reach Redis via `localhost`.
    
    ??? tip "Solution: Pod Deployment"
        1. `podman pod create --name web-stack -p 8080:80`
        2. `podman run -d --pod web-stack --name nginx nginx:alpine`
        3. `podman run -d --pod web-stack --name redis redis:alpine`
        4. `podman exec -it nginx curl localhost:6379` (or use `redis-cli`).

!!! note "Assignment.3: Custom Image Build"
    Write a simple `Dockerfile` for a Python script, build it using `podman build`, and run the container to verify the output.
    
    ??? tip "Solution: Custom Image"
        Create a `Dockerfile` with `FROM python:slim`, `COPY` the script, and `CMD ["python", "script.py"]`. Build with `podman build -t my-py-app .`.

!!! note "Assignment.4: Implementing an AI Monitoring Sidecar"
    Deploy a local AI stack using Podman Pods to implement the "Sidecar Pattern".
    1. Create a pod named `ai-monitoring-pod` and expose port 8000.
    2. Deploy a "Model API" container (e.g., using a simple FastAPI image) into the pod.
    3. Deploy a "GPU Health" sidecar container (e.g., `nvidia-smi-exporter`) into the same pod.
    4. Verify that the Model API can reach the monitor via `http://localhost:<port>`.
    
    ??? tip "Solution: Sidecar Pattern"
        Use `podman pod create --name ai-monitoring-pod -p 8000:8000`. Then use `podman run --pod ai-monitoring-pod ...` for both containers. The shared network namespace allows communication via `localhost`.

## References

- Podman Official Documentation: [docs.podman.io](https://docs.podman.io)
- OCI Specification: [opencontainers.org](https://opencontainers.org)
- Podman-Compose GitHub: [github.com/containers/podman-compose](https://github.com/containers/podman-compose)

## Self-Evaluation

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What does it mean for Podman to be 'rootless by default' and why is this important?"
    Rootless means Podman runs containers as a non-privileged user without requiring a root-privileged daemon. This is critical for security because it prevents a "container escape" from granting the attacker root access to the physical host machine.

??? question "How does Podman's concept of a 'Pod' align with Kubernetes architecture?"
    A Pod in Podman is a group of one or more containers that share the same network namespace and IP address. This mirrors the fundamental unit of deployment in Kubernetes, allowing developers to test multi-container pods locally before deploying to a cluster.

??? question "How can you use Podman as a drop-in replacement for Docker?"
    Since Podman provides near 1:1 CLI compatibility, you can often simply alias the `docker` command to `podman` (`alias docker=podman`) to run existing scripts without modification.

??? question "What is the purpose of `buildah` and `skopeo`?"
    `buildah` is a specialized tool for building OCI-compliant images without a daemon, while `skopeo` is used for inspecting and copying images between different registries and formats.

??? question "How does mind-mapping assist in planning a container architecture?"
    Mind-mapping allows developers to visually distill complex systems into a hierarchy of services and dependencies, which can then be directly translated into a `podman-compose.yml` file or a Kubernetes manifest.

??? question "Explain the role of User Namespaces in rootless containers."
    User namespaces allow the kernel to map a UID inside a container (e.g., UID 0 / root) to a different UID on the host (e.g., UID 1000). This means the process can act as root inside the container to install packages or manage services, but remains a non-privileged user on the host.

??? question "Why would you use a Pod instead of just running multiple separate containers?"
    Pods allow containers to share a network namespace, meaning they can communicate via `localhost` with very low latency. This is ideal for "sidecar" patterns, such as having a monitoring agent or a log forwarder running alongside a primary application.
