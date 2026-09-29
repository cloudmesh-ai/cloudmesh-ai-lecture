# Apptainer: Containers for High-Performance Computing

Apptainer (formerly known as Singularity) is a container platform specifically designed for High-Performance Computing (HPC) and enterprise environments. While Docker is the standard for microservices and cloud-native apps, Apptainer is the standard for scientific research and supercomputing.

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    1. **Distinguish** between Apptainer and Docker (specifically the SIF format vs. layers).
    2. **Execute** containers using `exec`, `shell`, and `run` commands.
    3. **Build** custom immutable images using Apptainer definition files (`.def`).
    4. **Manage** host-to-container data flow using bind mounts (`--bind`).
    5. **Understand** why Apptainer's "no-root" architecture is critical for shared HPC clusters.

---

## 1. Why Apptainer? (The HPC Perspective)

In a standard Docker environment, a background daemon runs with root privileges. On a shared supercomputer with thousands of users, giving users access to a root daemon is a massive security risk. Apptainer solves this by eliminating the daemon entirely.

### SIF: The Single-File Image
Unlike Docker images, which are composed of many layers stored in a hidden directory, Apptainer primarily uses the **SIF (Singularity Image Format)**. A SIF image is a single, compressed, read-only file.

**Advantages of the SIF format:**
*   **Portability**: Moving a container is as simple as copying a single file (`my_env.sif`).
*   **Performance**: SIF images are highly optimized for parallel file systems (like Lustre or GPFS) used in HPC.
*   **Security**: Because the image is immutable and runs as the user who launched it, there is no risk of "container breakout" to gain root access to the host.

---

## 2. Quick Start: Running Containers

You don't need to build an image to start using Apptainer. You can pull existing images from OCI registries (like Docker Hub) and convert them to SIF on the fly.

### Pulling and Executing
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

### Command Reference
| Goal | Command | Effect |
| :--- | :--- | :--- |
| **Fetch Image** | `apptainer pull <url>` | Downloads an image and saves it as a `.sif` file. |
| **Run Command** | `apptainer exec <img.sif> <cmd>` | Runs a specific command and exits. |
| **Interactive** | `apptainer shell <img.sif>` | Drops you into a bash/sh session inside the image. |
| **Default Execution**| `apptainer run <img.sif>` | Executes the image's predefined `%runscript`. |
| **Build Image** | `apptainer build <img.sif> <def>` | Creates a SIF image from a definition file. |

---

## 3. Building Custom Images with `.def` Files

To create a reproducible environment, you use a **Definition File (`.def`)**. This is a recipe that Apptainer follows to build the SIF image.

### Anatomy of a Definition File
A `.def` file is divided into sections:
*   **Bootstrap**: Defines the base image (e.g., `docker`, `ubuntu`).
*   **%post**: A shell script that runs *during* the build to install software and configure the system.
*   **%environment**: Sets environment variables that persist when the container runs.
*   **%runscript**: The default command executed when `apptainer run` is called.

### Case Study: Packaging a Documentation Site (MkDocs)
If you want to package a site built with **MkDocs**, your `.def` file would look like this:

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
Because building requires temporary root privileges to create the file system, use the `--fakeroot` flag:
```bash
apptainer build --fakeroot mkdocs.sif mkdocs.def
```

---

## 4. Advanced Runtime: Bind Mounts and Ports

Apptainer containers are immutable, meaning you cannot save files *inside* the image. To work with your own data, you must **bind** host directories into the container.

### Bind Mounts (`--bind`)
Bind mounts map a directory on your host machine to a path inside the container.
```bash
# Mount current directory to /docs inside the container
apptainer run --bind $(pwd):/docs mkdocs.sif
```

### Port Mapping (`-p`)
If your container runs a server (like MkDocs), you must expose the port to your host:
```bash
apptainer run --bind $(pwd):/docs -p 8000:8000 mkdocs.sif
```

---

## Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the primary difference between Apptainer and Docker regarding image formats?"
    Unlike Docker, which uses layers managed by a daemon, Apptainer primarily uses the **SIF (Singularity Image Format)**, which packages the entire container as a single, immutable file. This makes Apptainer images easier to move and execute on shared systems.

??? question "Why is Apptainer particularly well-suited for High-Performance Computing (HPC) clusters?"
    Apptainer is designed for HPC because it executes containers with the privileges of the invoking user rather than requiring a root-privileged daemon. This prevents security risks on shared supercomputers where users are not allowed to have root access.

??? question "What is the purpose of a `.def` (definition) file in Apptainer?"
    A `.def` file is a recipe used to build an Apptainer image. It defines the base image, the packages to install (`%post` section), environment variables (`%environment`), and the default command to run (`%runscript`).

??? question "What does the `--bind` flag do?"
    The `--bind` flag maps a directory or file from the host system into the container's filesystem. This is essential because SIF images are read-only, so any data the container needs to read or write must be provided via a bind mount.

---

## Assignments

!!! note "Assignment 1: Pull and Inspect"
    Pull the official `alpine` image from Docker Hub using Apptainer. Use `apptainer exec` to find the version of the OS and the current user's ID inside the container. Compare this to your ID on the host.

!!! note "Assignment 2: Custom Tool Image"
    Create a `.def` file that starts from `ubuntu:latest`, installs a simple CLI tool (e.g., `htop` or `tree`), and sets the `%runscript` to execute that tool. Build the image using `--fakeroot` and run it.

!!! note "Assignment 3: Data Processing Workflow"
    Create a local directory with a text file. Build or pull an image containing `grep`. Use `apptainer exec` with a `--bind` mount to search for a specific keyword in your host file from *inside* the container.

---

## Appendix: Local Installation Guide

If you are installing Apptainer on a local **Ubuntu/Debian** system, follow these steps:

### 1. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y build-essential libseccomp-dev pkg-config squashfs-tools cryptsetup curl wget git
```

### 2. Install Go (Golang)
```bash
export GO_VERSION=1.22.0
wget https://golang.org/dl/go$GO_VERSION.linux-amd64.tar.gz
sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go$GO_VERSION.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
```

### 3. Compile and Install Apptainer
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
