# Apptainer: Containers for High-Performance Computing

## Learning Objectives

!!! info "Why this matters"
    By the end of this chapter, participants will be able to:
    - Distinguish between Apptainer and Docker, specifically comparing the SIF format to layered images.
    - Execute containers using the `exec`, `shell`, and `run` commands.
    - Build custom immutable images using Apptainer definition files (`.def`).
    - Manage host-to-container data flow using bind mounts (`--bind`).
    - Understand why Apptainer's "no-root" architecture is critical for shared HPC clusters.
    - Optimize container execution for parallel file systems used in supercomputing.

## Implementation

In a standard [Docker](/section/container/foundations/docker.md) environment, a background daemon runs with root privileges. On a shared supercomputer with thousands of users, giving users access to a root daemon is a massive security risk. Apptainer solves this by eliminating the daemon entirely.

!!! info "Why this matters"
    In High-Performance Computing (HPC), security and performance are the primary drivers. HPC administrators cannot allow users to run processes as root on a shared login or compute node. Apptainer allows researchers to bring their entire software stack (OS, libraries, CUDA, Python) into the cluster as a single file, which then runs with the *exact same privileges* as the user who launched it. This provides the reproducibility of containers with the security required by supercomputing centers.

### HPC Container Comparison Matrix

To understand where Apptainer fits, it is helpful to compare it with other popular container runtimes from an HPC and AI perspective.

| Dimension | Docker | Podman | Apptainer |
| :--- | :--- | :--- | :--- |
| **Daemon** | Required (Root-privileged) | Daemonless | Daemonless |
| **Root Privileges** | Required for daemon | Rootless by default | Rootless by design |
| **Image Format** | OCI (Layered) | OCI (Layered) | SIF (Single File) / OCI |
| **Host Integration** | Isolated (Virtual Net/FS) | Isolated (Virtual Net/FS) | Integrated (Host Net/FS) |
| **Cluster Suitability** | Poor (Root risks, daemon) | Moderate (Rootless) | Excellent (Native HPC) |
| **SLURM/PBS Integration**| Complex/Limited | Possible | Native/Standard |

## Core Sections


### The SIF: Single-File Image Format

Unlike Docker images, which are composed of many layers stored in a hidden directory, Apptainer primarily uses the **SIF (Singularity Image Format)**. A SIF image is a single, compressed, read-only file.

#### Advantages of the SIF Format

- **Portability**: Moving a container is as simple as copying a single file (`my_env.sif`). You can store it in your home directory or a project folder without needing a registry.
- **Performance**: SIF images are highly optimized for parallel file systems (like Lustre or GPFS) used in HPC. Because the image is a single file, the filesystem handles metadata more efficiently than if it had to manage thousands of small layer files.
- **Security**: Because the image is immutable and runs as the user who launched it, there is no risk of a "container breakout" to gain root access to the host.

!!! info "Why this matters for AI"
    AI environments are often massive (gigabytes of CUDA libraries, PyTorch, and dependencies). In a shared cluster, if 100 users all launch a Docker-style layered container, the storage system must manage millions of small file lookups across different layers for every single user. This creates a "metadata storm" that can crash a parallel filesystem. 
    
    Apptainer's SIF format collapses everything into a single file. For the filesystem, launching a container becomes a single large sequential read rather than thousands of random small reads. This ensures that scaling an AI workload from one GPU to one thousand GPUs doesn't bottleneck the entire cluster's storage.


### Running Containers

You do not need to build an image to start using Apptainer; you can pull existing images from OCI registries (like Docker Hub) and convert them to SIF on the fly.

#### Pulling and Executing

```bash
# 1. Pull a Docker image and convert it to a .sif file
apptainer pull docker://alpine

# 2. Execute a specific command inside the container
apptainer exec alpine_latest.sif cat /etc/os-release

# 3. Open an interactive shell inside the container
apptainer shell alpine_latest.sif

# 4. Run the container's default script (the %runscript)
apptainer run alpine_latest.sif
```

#### Command Reference

| Goal | Command | Effect |
| :--- | :--- | :--- |
| **Fetch Image** | `apptainer pull <url>` | Downloads an image and saves it as a `.sif` file. |
| **Run Command** | `apptainer exec <img.sif> <cmd>` | Runs a specific command and exits. |
| **Interactive** | `apptainer shell <img.sif>` | Drops you into a bash/sh session inside the image. |
| **Default Execution**| `apptainer run <img.sif>` | Executes the image's predefined `%runscript`. |
| **Build Image** | `apptainer build <img.sif> <def>` | Creates a SIF image from a definition file. |

### Building Custom Images with `.def` Files

To create a reproducible environment, you use a **Definition File (`.def`)**. This is a recipe that Apptainer follows to build the SIF image.

#### Anatomy of a Definition File

A `.def` file is divided into sections:

- **Bootstrap**: Defines the base image (e.g., `docker`, `ubuntu`).
- **%post**: A shell script that runs *during* the build to install software and configure the system.
- **%environment**: Sets environment variables that persist when the container runs.
- **%runscript**: The default command executed when `apptainer run` is called.

#### Case Study: Packaging a Documentation Site (MkDocs)

To package a site built with **MkDocs**, the `.def` file would look like this:

```aiignore
Bootstrap: docker
From: python:3.11-slim

%post
    apt-get update && apt-get install -y git curl
    pip install --no-cache-dir mkdocs mkdocs-material

%environment
    export LC_ALL=C.UTF-8

%runscript
    # Serve the site from the /docs mount point
    cd /docs
    exec mkdocs serve -a 0.0.0.0:8000
```

**Building the image:**

Because building requires temporary root privileges to create the filesystem, use the `--fakeroot` flag:

```bash
apptainer build --fakeroot mkdocs.sif mkdocs.def
```

### Advanced Runtime: Bind Mounts and Ports

Apptainer containers are immutable, meaning you cannot save files *inside* the image. To work with your own data, you must **bind** host directories into the container.

#### Bind Mounts (`--bind`)

Bind mounts map a directory or file on your host machine to a path inside the container.

!!! info "Why this matters for AI and HPC"
    AI datasets are often massive (TBs) and stored on high-performance parallel filesystems. You cannot bake these into the image. Instead, you mount the dataset directory from the host into the container. This allows the container to read the data at native speed while keeping the image small and portable.

```bash
# Mount current directory to /docs inside the container
apptainer run --bind $(pwd):/docs mkdocs.sif
```

!!! warning "Read-Only Filesystem"
    By default, the root filesystem of a SIF image is **read-only**. If your application tries to write to `/etc/` or `/usr/bin/` at runtime, it will fail with a `Read-only file system` error. Always use `--bind` or environment variables like `HOME` to map writable directories for logs or temp files.

#### Port Mapping (`-p`)

If your container runs a server (like MkDocs or a Flask API), you must expose the port to your host:

```bash
apptainer run --bind $(pwd):/docs -p 8000:8000 mkdocs.sif
```

#### AI Model Deployment Example: Supercomputing Cluster

Imagine you are deploying a Large Language Model (LLM) on a cluster. Your workflow would look like this:

1. **Build**: Create a `.def` file with `PyTorch`, `Transformers`, and `CUDA` libraries $\rightarrow$ build `llm_env.sif`.
2. **Deploy**: Upload `llm_env.sif` to the cluster's shared `/project/software` directory.
3. **Execute**: Use a SLURM script to launch the container on 4 GPUs, binding the model weights:

```bash
srun apptainer exec --nv \
     --bind /project/data/weights:/models \
     llm_env.sif python3 inference.py --model /models/llama-3
```
*Note: The `--nv` flag is critical—it tells Apptainer to pass the NVIDIA GPU libraries from the host into the container.*

## Summary Checklist

- [ ] Distinguish between the layered Docker format and the single-file SIF format.
- [ ] Execute containers using `exec`, `shell`, and `run`.
- [ ] Build a custom SIF image from a `.def` file using `--fakeroot`.
- [ ] Implement bind mounts using the `--bind` flag for data access.
- [ ] Use the `--nv` flag to enable GPU acceleration in Apptainer.
- [ ] Explain the security benefits of the "no-root" architecture in shared HPC clusters.
- [ ] Create a comparison matrix: Apptainer vs Docker vs Podman (HPC focus).

## Assignments

!!! note "Assignment.1: Pull and Inspect"
    Pull the official `alpine` image from Docker Hub using Apptainer. Use `apptainer exec` to find the version of the OS and the current user's ID inside the container. Compare this to your ID on the host.
    
    ??? tip "Solution: Pull and Inspect"
        Run `apptainer pull docker://alpine`, then `apptainer exec alpine_latest.sif cat /etc/os-release` and `apptainer exec alpine_latest.sif id`.

!!! note "Assignment.2: Custom Tool Image"
    Create a `.def` file that starts from `ubuntu:latest`, installs a simple CLI tool (e.g., `htop` or `tree`), and sets the `%runscript` to execute that tool. Build the image using `--fakeroot` and run it.
    
    ??? tip "Solution: Custom Image"
        Create a `.def` file with a `%post` section containing `apt-get install -y htop` and a `%runscript` containing `exec htop`. Build with `apptainer build --fakeroot htop.sif htop.def`.

!!! note "Assignment.3: Data Processing Workflow"
    Create a local directory with a text file. Build or pull an image containing `grep`. Use `apptainer exec` with a `--bind` mount to search for a specific keyword in your host file from *inside* the container.
    
    ??? tip "Solution: Data Workflow"
        Create a file `test.txt` in `~/data`. Run `apptainer exec --bind ~/data:/mnt alpine grep "keyword" /mnt/test.txt`.

## What's Next?

With the foundations of container runtimes complete, we will now shift our focus to how we secure these environments and manage them at scale. Next, we will cover [Container Security & Hardening](/section/container/security/container-security.md).

## References

- Apptainer Documentation: [apptainer.org/docs/](https://apptainer.org/docs/)
- SIF Format Specification: [apptainer.org/docs/userguide/sif.html](https://apptainer.org/docs/userguide/sif.html)
- HPC Container Best Practices: [hpc-containers.org](https://hpc-containers.org)

## Self-Evaluation

??? question "What is the primary difference between Apptainer and Docker regarding image formats?"
    Unlike Docker, which uses layers managed by a daemon, Apptainer primarily uses the **SIF (Singularity Image Format)**, which packages the entire container as a single, immutable file. This makes Apptainer images easier to move and execute on shared systems.

??? question "Why is Apptainer particularly well-suited for High-Performance Computing (HPC) clusters?"
    Apptainer is designed for HPC because it executes containers with the privileges of the invoking user rather than requiring a root-privileged daemon. This prevents security risks on shared supercomputers where users are not allowed to have root access.

??? question "What is the purpose of a `.def` (definition) file in Apptainer?"
    A `.def` file is a recipe used to build an Apptainer image. It defines the base image, the packages to install (`%post` section), environment variables (`%environment`), and the default command to run (`%runscript`).

??? question "What does the `--bind` flag do and why is it essential in Apptainer?"
    The `--bind` flag maps a directory or file from the host system into the container's filesystem. It is essential because SIF images are read-only; any data the container needs to read (like AI datasets) or write (like logs) must be provided via a bind mount.

??? question "Explain the significance of the `--nv` flag when running AI workloads in Apptainer."
    The `--nv` flag tells Apptainer to mount the NVIDIA GPU drivers and libraries from the host system into the container. Since the container cannot package the kernel-level driver, this flag is required for the container's CUDA libraries to communicate with the physical GPU hardware.

??? question "Why is the SIF format preferred over Docker's layered format for parallel filesystems like Lustre?"
    Parallel filesystems are optimized for large sequential reads of a few files rather than many small random reads of thousands of files. Because a SIF image is a single file, it minimizes metadata overhead on the filesystem, leading to significantly faster image loading across thousands of compute nodes.

??? question "How does Apptainer handle the 'root' user inside a container differently than Docker?"
    In Docker, the root user inside the container is often mapped to the root user on the host (unless rootless mode is used). In Apptainer, the user inside the container is the *same* as the user outside. If you are `user123` on the host, you are `user123` inside the Apptainer container.

## Appendix: Local Installation Guide

If you are installing Apptainer on a local **Ubuntu/Debian** system, follow these steps:

#### 1. Install Dependencies

```bash
sudo apt-get update
sudo apt-get install -y build-essential libseccomp-dev pkg-config squashfs-tools cryptsetup curl wget git
```

#### 2. Install Go (Golang)

```bash
export GO_VERSION=1.22.0
wget https://golang.org/dl/go$GO_VERSION.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go$GO_VERSION.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Compile and Install Apptainer

```bash
export APPTAINER_VERSION=1.3.0
wget https://github.com/apptainer/apptainer/releases/download/v${APPTAINER_VERSION}/apptainer-${APPTAINER_VERSION}.tar.gz
tar -xzf apptainer-${APPTAINER_VERSION}.tar.gz
cd apptainer-${APPTAINER_VERSION}
./mconfig
make -C builddir
sudo make -C builddir install
```

!!! tip "Using Windows or macOS?"
    Apptainer requires a Linux kernel. If you are on Windows, install **WSL 2 (Ubuntu)** and follow the steps above. If you are on a Mac, use **Lima** or **UTM** to spin up a lightweight Linux environment.
