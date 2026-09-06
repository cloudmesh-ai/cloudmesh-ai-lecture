# Installing Apptainer locally

Setting up **Apptainer** (formerly known as Singularity) on a local Linux computer is a straightforward process. Because Apptainer is designed natively for Linux, native installation is easiest, though Windows and macOS users can run it via a Linux virtual machine.

This tutorial walks through installing Apptainer on a local **Ubuntu / Debian** system and running your first container.

---

## Step 1: Install System Dependencies

First, open your terminal and make sure your package lists are up to date. Then, install the essential packages required to compile and run Apptainer (such as `build-essential`, `squashfs-tools`, and `cryptsetup`).

```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    libseccomp-dev \
    pkg-config \
    squashfs-tools \
    cryptsetup \
    curl \
    wget \
    git
```

---

## Step 2: Install Go (Golang)

Apptainer is written in Go. Since system repositories often carry outdated versions, it is best to download and install a recent stable version directly from the official Go website.

1. **Download Go** (check the official site for the latest version if needed; `1.22.x` or newer is standard):
```bash
export GO_VERSION=1.22.0
wget https://golang.org/dl/go$GO_VERSION.linux-amd64.tar.gz
```


2. **Extract and install** it to `/usr/local`:
```bash
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go$GO_VERSION.linux-amd64.tar.gz
```


3. **Add Go to your system PATH**:
```bash
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc
```



Verify the installation by running:

```bash
go version
```

---

## Step 3: Download and Compile Apptainer

Next, download the source code for the latest Apptainer release from GitHub and compile it.

1. **Clone or download the release archive** (check GitHub releases for the latest version number, e.g., `v1.3.x` or later):
```bash
export APPTAINER_VERSION=1.3.0
wget https://github.com/apptainer/apptainer/releases/download/v${APPTAINER_VERSION}/apptainer-${APPTAINER_VERSION}.tar.gz
tar -xzf apptainer-${APPTAINER_VERSION}.tar.gz
cd apptainer-${APPTAINER_VERSION}
```


2. **Configure and compile**:
```bash
./mconfig
make -C builddir
```


3. **Install globally**:
```bash
sudo make -C builddir install
```



Verify that Apptainer is successfully installed:

```bash
apptainer --version
```

---

## Step 4: Run Your First Container

Unlike Docker, Apptainer runs containers as single-file images called **SIF (Singularity Image Format)** and executes them with the privileges of the invoking user, making it ideal for local workstations and shared clusters.

1. **Pull a test image** from an OCI registry (like Docker Hub):
```bash
apptainer pull docker://alpine
```


*This downloads the Alpine Linux Docker image and automatically converts it into a local `alpine_latest.sif` file.*
2. **Execute a command** inside the container:
```bash
apptainer exec alpine_latest.sif cat /etc/os-release
```


3. **Open an interactive shell** inside the container:
```bash
apptainer shell alpine_latest.sif
```


*You are now inside an isolated Alpine environment. Type `exit` to return to your host terminal.*

---

!!! tip  "Using Windows or macOS?"

    Apptainer requires a Linux kernel. If you are on Windows, install **WSL 2 (Ubuntu)** and follow the steps above inside your WSL terminal. If you are on a Mac, use **Lima** or **UTM** to spin up a lightweight Linux environment first.

---

## Appendix: Creating a Custom Apptainer Image for MkDocs

If you want to package a documentation site built with **MkDocs** and its Material theme inside an immutable Apptainer image, you can use a definition (`.def`) file. This approach ensures your documentation is fully self-contained and reproducible.

### 1. Create the Definition File (`mkdocs.def`)

Create a file named `mkdocs.def` using a text editor:

```aiignore
Bootstrap: docker
From: python:3.11-slim

%post
    # Update system packages and install necessary tools
    apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        && rm -rf /var/lib/apt/lists/*

    # Install MkDocs and the Material theme
    pip install --no-cache-dir \
        mkdocs \
        mkdocs-material

%environment
    # Set default environment variables if needed
    export LC_ALL=C.UTF-8
    export LANG=C.UTF-8

%runscript
    # Default behavior when running the container (e.g., serve the site)
    # Assumes your MkDocs project directory is mounted to /docs inside the container
    cd /docs
    exec mkdocs serve -a 0.0.0.0:8000

%labels
    Author YourName
    Version 1.0
    Description Apptainer image containing MkDocs and MkDocs-Material

```

---

### 2. Build the SIF Image

Because building a container image requires administrative privileges to create the file system, you can build it locally using `--fakeroot` (which allows unprivileged users to build containers using user namespaces):

```bash
apptainer build --fakeroot mkdocs.sif mkdocs.def

```

This compiles your definition file and outputs a single, portable `mkdocs.sif` file.

---

### 3. Run the MkDocs Container and Serve Your Website

To use the image, navigate to the local directory where your MkDocs project (containing your `mkdocs.yml` file and `docs/` folder) is located.

You can bind your current host directory to the `/docs` mount point inside the container and expose port `8000` to your host machine:

```bash
apptainer run --bind $(pwd):/docs -p 8000:8000 mkdocs.sif

```

Once running, open your web browser and navigate to `http://localhost:8000` to view your live MkDocs website.