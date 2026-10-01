# Docker: The Industry Standard

## Learning Objectives

!!! info "Why this matters"
    By the end of this chapter, participants will be able to:
    - Install and configure the Docker Engine across various operating systems.
    - Build optimized Docker images using a Dockerfile and industry best-practice patterns.
    - Manage container lifecycles (create, start, stop, remove) using the Docker CLI.
    - Orchestrate multi-container applications using Docker Compose.
    - Implement persistent storage using volumes and bind mounts for large AI datasets.
    - Configure container networking for communication between containers and the host.
    - Troubleshoot common Docker runtime and build errors.
    - Implement multi-stage builds to reduce attack surface and image size.

## Implementation

Docker is a platform that allows developers to package applications and all their dependencies into a portable, reproducible unit called a container. Unlike Virtual Machines (VMs), which require a full guest operating system for every instance, containers share the host's Linux kernel. This makes them significantly lighter, allowing containers to start in milliseconds and enabling higher density on the same hardware.

Docker follows a client-server architecture. The Docker client (`docker` CLI) sends commands to the Docker daemon (`dockerd`), which manages the building of images and the execution of containers. The core workflow is summarized as **Build, Ship, and Run**:

1. **Build**: Use a `Dockerfile` to create an immutable **Image**.
2. **Ship**: Push that image to a **Registry** (e.g., Docker Hub).
3. **Run**: Pull the image and instantiate it as a **Container**.

### Docker Architecture and Terminology

Docker leverages Linux kernel primitives—specifically **Namespaces** and **Control Groups (cgroups)**—to provide isolation. Namespaces ensure a container cannot see processes or networks of other containers, while cgroups prevent a single container from consuming all host resources.

| Term | Meaning |
|------|---------|
| **Docker Engine** | A daemon (`dockerd`) and client (`docker`) that builds and manages containers. |
| **Image** | A read-only template consisting of stacked layers and metadata. |
| **Container** | A runtime instance of an image with an added writable layer. |
| **Registry** | A centralized service for storing and distributing images. |
| **Dockerfile** | A declarative script defining the instructions to build an image. |
| **Docker Compose** | A YAML-based tool for defining and running multi-container applications. |

The **Image Layer** system is based on a Union File System. Each instruction in a Dockerfile creates a new read-only layer. If multiple images share the same base layer (e.g., `ubuntu:22.04`), Docker stores that layer only once, significantly reducing disk usage.

### Installation and Setup

Docker installation varies by operating system. On Linux, the Docker daemon typically requires root privileges; adding the user to the `docker` group allows interaction without `sudo`.

#### Installation Commands

| OS | Commands |
|----|----------|
| **Ubuntu 22.04+** | `sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg lsb-release && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null && sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io && sudo usermod -aG docker $USER && newgrp docker` |
| **Fedora 38+** | `sudo dnf -y install dnf-plugins-core && sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo && sudo dnf install -y docker-ce docker-ce-cli containerd.io && sudo systemctl enable --now docker && sudo usermod -aG docker $USER && newgrp docker` |
| **CentOS 8 / Rocky 9** | `sudo dnf -y install dnf-plugins-core && sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo && sudo dnf install -y docker-ce docker-ce-cli containerd.io && sudo systemctl enable --now docker && sudo usermod -aG docker $USER && newgrp docker` |
| **macOS/Windows** | Install **Docker Desktop** from the official Docker website. |

!!! tip "Verify Installation"
    Run the following commands to confirm the engine is active:
    ```bash
    docker version
    docker info
    ```

### Essential Docker CLI Operations

The general lifecycle of a container involves provisioning, interaction, monitoring, and teardown.

#### Common Commands

| Action | Command | Common Options |
|--------|---------|----------------|
| **List images** | `docker images` | `-a` (show intermediate layers) |
| **Pull an image** | `docker pull nginx:alpine` | |
| **Run (interactive)** | `docker run -it --rm ubuntu bash` | `--name myctn`, `-p 8080:80` |
| **Run (background)** | `docker run -d --name web -p 80:80 nginx:alpine` | |
| **List running** | `docker ps` | `-a` (show stopped) |
| **Stop / Remove** | `docker stop web && docker rm web` | |
| **Execute inside** | `docker exec -it web sh` | |
| **Build an image** | `docker build -t myapp:1.0 .` | `--no-cache` |
| **Push to registry** | `docker push username/myapp:1.0` | |
| **System Cleanup** | `docker system prune -a` | *Removes all unused data* |

### Building Images

A Docker image is created from a `Dockerfile`. The build process creates a series of layered snapshots; Docker caches these layers to make subsequent builds nearly instantaneous if only the final layers have changed.

!!! info "Why this matters"
    Manual environment setup (e.g., a 10-page PDF of installation steps) is prone to human error. A `Dockerfile` transforms environment setup into **Code**. This means your environment can be version-controlled in Git, peer-reviewed in Pull Requests, and reproduced exactly by any teammate or CI/CD pipeline.

#### Example: "Hello World" Web App

1. **Create `app.py`**:
    ```python
    from flask import Flask
    app = Flask(__name__)

    @app.route("/")
    def hello():
        return "Hello from Docker!"

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    ```

2. **Create `Dockerfile`**:
    ```Dockerfile
    FROM python:3.12-slim
    WORKDIR /app
    COPY app.py .
    EXPOSE 5000
    CMD ["python", "app.py"]
    ```

3. **Build and Run**:
    ```bash
    docker build -t hello-app:0.1 .
    docker run -d -p 5000:5000 --name hello hello-app:0.1
    curl http://localhost:5000
    ```

#### Advanced: Multi-Stage Builds for AI Libraries

In AI, we often need to compile C++ or CUDA extensions (e.g., for custom PyTorch kernels), but we don't want the bulky compilers (GCC, NVCC) in our final production image.

!!! tip "The Multi-Stage Pattern"
    Use a `builder` stage to compile and a `runtime` stage to execute.

```Dockerfile
# Stage 1: Builder
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04 AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y python3-dev build-essential
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
WORKDIR /app
# Copy only the installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python3", "train.py"]
```

!!! info "Impact of Multi-Stage Builds"
    By separating the build environment from the runtime environment, you can reduce an image from **4GB (devel)** down to **1.2GB (runtime)**. This leads to faster pulls in production and a significantly smaller attack surface for security vulnerabilities.

### Data Persistence and Networking

#### Storage

Containers are ephemeral by default. To persist data, Docker provides:

- **Named Volumes**: Managed by Docker, stored in `/var/lib/docker/volumes/`. Preferred for production databases.
- **Bind Mounts**: Map a host directory (e.g., `/home/user/datasets`) to the container. Ideal for development live-reloads and mounting massive AI datasets.

!!! info "Why this matters for AI"
    AI datasets are often too large (TB+) to be baked into a container image. Using a **Bind Mount** allows the container to access the data directly from the host's high-performance NVMe or parallel filesystem (like Lustre) without duplicating the data into the container's writable layer.

::: warning "Volume Performance"
    On macOS and Windows, bind mounts are significantly slower than on Linux because they must go through a virtualization layer (gRPC-FUSE/VirtioFS). For high-I/O AI training, Linux is strongly recommended.
:::

#### Networking

Docker creates a virtual bridge network by default. Use port mapping (`-p host_port:container_port`) to expose services to the host.

| Network Driver | Description | Typical Use |
|----------------|-------------|-------------|
| **bridge** | Isolated private network on a single host. | Standard single-host apps. |
| **host** | Shares the host's network namespace. | Performance-critical apps, low-latency AI APIs. |
| **overlay** | Multi-host network. | Swarm or Kubernetes clusters. |

### Multi-Container Orchestration with Docker Compose

Docker Compose allows you to define a multi-container application in a single YAML file, ensuring environment parity across a team.

!!! info "Why this matters"
    Modern AI systems are rarely a single script. They typically involve a **Frontend** (React), an **API** (FastAPI), a **Task Queue** (Celery), and a **Database** (PostgreSQL/Redis). Docker Compose allows a researcher to launch the entire stack with one command, ensuring the API can always find the database at the hostname `db`.

#### Example `docker-compose.yml`

```yaml
version: "3.9"
services:
  web:
    build: ./web
    ports:
      - "8080:80"
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db-data:/var/lib/postgresql/data
volumes:
  db-data:
```

**Management Commands**:
- `docker compose up -d`: Build, create, and start containers in the background.
- `docker compose down -v`: Stop containers and remove named volumes.
- `docker compose logs -f`: Stream logs from all services.

### Security and Productionization

Running containers as `root` is a significant security risk. If a process escapes a container, it may gain root access to the host. For a more secure, rootless alternative, see [Podman](/section/container/foundations/podman.md).

#### Production Best Practices

- **Pin Base Images**: Use `python:3.12.3-slim` instead of `python:latest`.
- **Least Privilege**: Always include a `USER` directive in the Dockerfile to run the app as a non-root user.
- **Image Scanning**: Integrate tools like **Trivy** into CI/CD pipelines to detect CVEs in your layers.

::: warning "The :latest Tag Trap"
    Never use `:latest` in production. If the image provider updates the "latest" version and your container restarts, you may inadvertently deploy a breaking change without any code changes of your own. Always pin a specific version tag.
:::

For comprehensive security strategies, including rootless mode and image hardening, refer to **[Container Security & Hardening](/section/container/security/container-security.md)**.

## Summary Checklist

- [ ] Install the Docker Engine and verify with `docker version`.
- [ ] Create a `Dockerfile` and build a versioned image.
- [ ] Run a container with port mapping and a custom name.
- [ ] Distinguish between a named volume and a bind mount.
- [ ] Deploy a multi-container stack using `docker compose up`.
- [ ] Push a tagged image to a remote registry.
- [ ] Implement a multi-stage build to reduce image size.
- [ ] Explain the security risk of running as the root user inside a container.

## Assignments

!!! note "Assignment.1: Image Optimization"
    Take an existing Dockerfile and reduce its final image size by at least 50% using a multi-stage build and a smaller base image (e.g., `alpine` or `slim`).
    
    ??? tip "Solution: Optimization"
        Use a `build` stage (e.g., `FROM gcc as builder`) to compile binaries or install dependencies, then use a second `FROM alpine` stage to `COPY --from=builder` only the necessary artifacts.

!!! note "Assignment.2: Persistent Database"
    Launch a PostgreSQL container using a named volume to ensure that data survives after the container is deleted and recreated.
    
    ??? tip "Solution: Persistence"
        Run `docker volume create pg_data` and launch the container with `-v pg_data:/var/lib/postgresql/data`. Verify persistence by inserting a row, deleting the container, and restarting a new one with the same volume.

!!! note "Assignment.3: Multi-Service Stack"
    Create a `docker-compose.yml` that launches a web application and a Redis cache, ensuring the web app can resolve the Redis service by its name.
    
    ??? tip "Solution: Orchestration"
        Define two services (`web` and `redis`) in the YAML. In the web application code, connect to the database using the hostname `redis` rather than an IP address.

## What's Next?

Now that you have mastered Docker, we will explore a daemonless and rootless alternative that is increasingly popular in security-conscious environments: [Podman](/section/container/foundations/podman.md).

## References

- Docker Documentation: [docs.docker.com](https://docs.docker.com/)
- Dockerfile Best Practices: [docs.docker.com/develop/develop-images/dockerfile_best-practices/](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- Trivy Vulnerability Scanner: [github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy)

## Self-Evaluation

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "Explain the 'Build, Ship, Run' workflow."
    **Build**: A `Dockerfile` is used to create a read-only image. **Ship**: The image is pushed to a registry. **Run**: The image is pulled from the registry and instantiated as a running container.

??? question "What is the difference between a Docker Image and a Docker Container?"
    An image is a static, read-only template containing the application and its dependencies. A container is a runtime instance of an image, adding a thin writable layer on top of the image layers.

??? question "How do multi-stage builds improve security?"
    Multi-stage builds allow you to leave build-time tools (compilers, shells, package managers) in the first stage and copy only the final executable into the production image. This minimizes the attack surface available to an intruder.

??? question "When should you use a bind mount instead of a named volume?"
    Bind mounts are ideal for development (e.g., mapping source code for live-reloading) or for accessing massive external datasets. Named volumes are preferred for production data (e.g., databases) because they are managed by Docker and are more portable across hosts.

??? question "Why is using the `:latest` tag dangerous in a production environment?"
    The `:latest` tag is a moving target. If a new image is pushed to the registry, your infrastructure might pull a different version of the software upon restart, leading to non-deterministic deployments and "phantom" bugs.

??? question "What is the role of the Docker daemon (`dockerd`) in the architecture?"
    The daemon is the centralized background process that manages all container operations. The CLI sends API requests to the daemon, which then interacts with the host kernel and container runtimes to build images and run containers.

??? question "How does Docker use Namespaces and Cgroups to achieve isolation?"
    Namespaces provide the *illusion* of a private system (e.g., private network, process list, and mount points), while Cgroups (Control Groups) enforce *resource limits* (e.g., maximum CPU usage or memory limit) to prevent a single container from crashing the host.
