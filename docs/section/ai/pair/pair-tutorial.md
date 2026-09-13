# Deploying NVIDIA AI Pair Across a Hybrid Cluster

This chapter provides a comprehensive, production-ready guide to deploying **NVIDIA AI Pair** across a heterogeneous environment. We will move from understanding your hardware landscape to implementing a scalable, automated deployment using Infrastructure as Code (IaC).

!!! Learning Objectives

    By the end of this chapter, you will be able to:
    - [ ] **Analyze** a hybrid GPU cluster (`laptop`, `white`, `spark`) to determine optimal model loading strategies.
    - [ ] **Execute** a fast-track experimental deployment of NVIDIA AI Pair using Docker.
    - [ ] **Implement** a production-grade, idempotent deployment using Ansible and Ansible Vault.
    - [ ] **Configure** hardware-specific optimizations including 4-bit quantization and 8-way Tensor Parallelism.
    - [ ] **Verify** cluster health and performance using custom probe scripts and GPU metrics.
    - [ ] **Deploy** and manage AI services using `systemd` for high availability and persistence.

## 1. The Hardware Landscape

Before deploying any AI workload, you must understand the physical constraints of your compute nodes. In this setup, we manage three distinct machine profiles: the control node (**laptop**), a high-end workstation (**white**), and a powerhouse GPU node (**spark**).

### Machine Specifications

| Machine | Role | CPU/Architecture | RAM | GPU | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **laptop** | Control Node | Apple M1 Max | 64 GB | Unified Memory | Orchestration & UI Access |
| **white** | Workstation | x86_64 | 128 GB | 1x RTX 3090 (24GB) | Single-GPU, high-memory node |
| **spark** | Compute Node | aarch64 (ARM) | 128 GB | Blackwell Unified | NVIDIA DGX Spark Superchip |

:::tip
**Unified Memory on Mac**: Note that `laptop` uses Apple's Unified Memory Architecture, meaning the GPU and CPU share the same 64GB pool. This is excellent for local testing but differs from the discrete VRAM found on the Linux nodes.
:::

**Why this matters:** 
AI models are memory-bound. Knowing the exact VRAM (24GB on `white` vs. the 128GB unified pool on `spark`) determines whether you can load a model in full precision (FP16/BF16) or if you must employ **Quantization** (e.g., 4-bit). Because `spark` uses a single Blackwell superchip with unified memory, you can run significantly larger models (up to 200B parameters) without the complexity of multi-GPU Tensor Parallelism.

---

## 2. Deployment Strategy: Manual vs. Automated

There are two primary ways to roll out NVIDIA AI Pair: a quick-start Bash loop and a production-ready Ansible workflow.

### Comparison Table

| Feature | Bash Loop (Quick Start) | Makefile (Dev Workflow) | Ansible (Production) |
| :--- | :--- | :--- | :--- |
| **Speed to First Run** | Fast | Extremely Fast | Moderate |
| **Repeatability** | Low (Manual) | Medium (Templated) | High (Idempotent) |
| **Secret Management** | Plaintext files (Risk) | Local Secret File | Ansible Vault (Encrypted) |
| **Lifecycle Mgmt** | Manual `docker run` | Manual Targets | `systemd` (Auto-restart) |
| **State Management** | None (Imperative) | Basic (Target-based) | Idempotent (Declarative) |
| **Scalability** | Hard to manage $\gt$ 5 nodes | Low/Medium | Effortless for hundreds of nodes |

**Why this matters:** 
While a Bash loop is tempting for a "one-off" test, AI infrastructure evolves rapidly. When NVIDIA releases a new image or you update the `spark` node, manually updating every machine becomes a source of configuration drift ("snowflake servers"). Ansible ensures that every node is an exact clone of your defined state.

---

## 3. Experimental Setup: The "Fast-Track" Approach

Before committing to a full `systemd` production deployment, it is often beneficial to run a manual "experimental" setup. While `systemd` provides persistence and auto-restarts, it can slow down the rapid iteration cycle during the initial configuration and tuning phase.

### Why avoid `systemd` for experimentation?
When you are first tuning `TRTL_QUANT` or `TRTL_TENSOR_PARALLEL`, you will be restarting the container frequently. Manually managing the container with `docker run` allows for:
- **Immediate Feedback**: Change an environment variable and restart in seconds without reloading systemd daemons.
- **Easier Debugging**: Running the container in the foreground (`-it` instead of `-d`) allows you to see real-time logs and crash dumps directly in your terminal.
- **Lower Overhead**: No need to manage service files or handle permission issues with `/etc/systemd/system`.

**Why this matters:** 
In the early stages of AI deployment, the **developer velocity** (how fast you can test a hypothesis) is more critical than **system availability**. Once you have found the "magic" set of parameters for your specific hardware, you can then codify them into the Ansible/systemd workflow described in the next section.

### Manual Launch Commands

To start Pair manually, use the following commands on your nodes. Replace `YOUR_NGC_API_KEY` with your actual key.

#### For the `white` node (RTX 3090):
```bash
docker run -d --gpus '"device=0"' \
  -p 8888:8888 \
  --name nvidia-pair \
  -e NGC_API_KEY=YOUR_NGC_API_KEY \
  -e TRTL_QUANT=4 \
  nvcr.io/nvidia/pair:latest
```

#### For the `spark` node (DGX Spark):
```bash
docker run -d --gpus all \
  -p 8888:8888 \
  --name nvidia-pair \
  -e NGC_API_KEY=YOUR_NGC_API_KEY \
  -e TRTL_QUANT=4 \
  nvcr.io/nvidia/pair:latest
```

:::tip
**Log Inspection**: To see what's happening inside your experimental container, use:
`docker logs -f nvidia-pair`
:::

:::warning
**Cleanup**: Remember that manually started containers with `--name nvidia-pair` will conflict if you try to run the Ansible playbook later. Before switching to the production setup, remove your experimental container:
`docker rm -f nvidia-pair`
:::


### Makefile Launch Workflow

While manual commands are useful for one-off tasks, managing multiple nodes via SSH can quickly become tedious. A `Makefile` encapsulates these complex commands into simple, repeatable targets. This approach is faster than the manual method because the configuration is templated directly within the `Makefile`. Furthermore, it allows for better workflow coordination through `Makefile` dependency management.

#### The `Makefile` implementation

Create a file named `Makefile` in your project root:

```makefile
# Configuration
USER=ubuntu
WHITE_HOST=white
SPARK_HOST=spark
NGC_API_KEY ?= $(shell cat .ngc_api_key)

# Common Docker flags to avoid long lines
DOCKER_BASE = docker run -d \
              -p 8888:8888 \
              --name nvidia-pair \
              -e NGC_API_KEY=$(NGC_API_KEY) \
              -e TRTL_QUANT=4

IMAGE = nvcr.io/nvidia/pair:latest

.PHONY: white spark start stop logs cleanup

# Start all nodes
start: white spark

# Stop all nodes
stop: cleanup

# Start service on the white node
white:
	ssh $(USER)@$(WHITE_HOST) "docker rm -f nvidia-pair || true && $(DOCKER_BASE) --gpus '"device=0"' $(IMAGE)"

# Start service on the spark node
spark:
	ssh $(USER)@$(SPARK_HOST) "docker rm -f nvidia-pair || true && $(DOCKER_BASE) --gpus all $(IMAGE)"

# Stream logs from both nodes
logs:
	ssh $(USER)@$(WHITE_HOST) "docker logs nvidia-pair"
	ssh $(USER)@$(SPARK_HOST) "docker logs nvidia-pair"

# Remove containers from all nodes
cleanup:
	ssh $(USER)@$(WHITE_HOST) "docker rm -f nvidia-pair"
	ssh $(USER)@$(SPARK_HOST) "docker rm -f nvidia-pair"
```

#### How to use this workflow

1.  **Setup your key**: To avoid putting your API key in the Makefile, save it to a hidden file:
    ```bash
    echo "your-actual-ngc-api-key" > .ngc_api_key
    chmod 600 .ngc_api_key
    ```
2.  **Launch a node**:
    ```bash
    make white  # Launches on the RTX 3090 node
    make spark  # Launches on the DGX Spark node
    ```
3.  **Monitor and Clean**:
    ```bash
    make logs     # Checks logs for both machines
    make cleanup  # Tears down the experimental containers
    ```

**Why this matters:** 
Using a `Makefile` transforms your "experimental" setup into a "developer tool." It eliminates the need to remember exact Docker flags or hostnames, reducing the risk of typos and allowing you to focus on tuning the model rather than managing the infrastructure.


---

## 4. Setup with Ansible

For production deployments, Ansible is the preferred approach. This treats your infrastructure as code, allowing you to version-control your deployment.

### Project Structure

Organize your project to separate global configurations from machine-specific overrides:

```text
pair-ansible/
├─ ansible.cfg                # Project configuration
├─ inventory.ini              # List of white and spark nodes
├─ group_vars/
│  ├─ all.yml                 # Global defaults (e.g., image version)
│  ├─ white.yml               # RTX 3090 specific tuning
│  └─ spark.yml               # DGX A100 specific tuning
├─ vault.yml                  # Encrypted NGC API Key
├─ roles/
│  └─ nvidia_pair/            # The deployment logic
│     ├─ tasks/main.yml       # Installation steps
│     ├─ templates/           # systemd and env templates
│     └─ files/               # Static config files
└─ site.yml                    # The master playbook
```

### Managing Secrets with Ansible Vault

Never store your NGC API key in plaintext. Use Ansible Vault to encrypt your secrets.

```bash
# Create an encrypted vault file
ansible-vault create vault.yml
```

Inside `vault.yml`, define your key:
```yaml
ngc_api_key: "your-secret-ngc-api-key-here"
```

:::warning
**Security Risk**: If you commit `vault.yml` to Git without encrypting it, your NGC credentials are leaked. Always use a vault password file or prompt during execution.
:::

### The Deployment Role

The core of the deployment is the `nvidia_pair` role. It ensures Docker is installed and the NVIDIA runtime is configured. By default, the role can also manage the Pair container as a `systemd` service, but this is optional depending on whether you need production persistence or experimental flexibility.

**Example: `roles/nvidia_pair/tasks/main.yml`** (Simplified)
```yaml
- name: Install NVIDIA Container Toolkit
  apt:
    name: nvidia-container-toolkit
    state: present
  become: true

- name: Configure Docker to use NVIDIA runtime
  copy:
    dest: /etc/docker/daemon.json
    content: '{"default-runtime": "nvidia", "runtimes": {"nvidia": {"path": "/usr/bin/nvidia-container-runtime"}}}'
  become: true
  notify: Restart Docker

- name: Deploy systemd service for Pair
  template:
    src: pair.service.j2
    dest: /etc/systemd/system/nvidia-pair.service
  become: true
  when: deploy_as_service | default(false)
  notify: Reload systemd
```

**Why this matters:** 
By making the `systemd` unit optional, you can use the same Ansible role for both "Developer" nodes (where you want to manually restart containers to test new flags) and "Production" nodes (where you need the service to automatically start after a reboot).


---

## 5. Hardware-Specific Tuning

One size does not fit all in AI. We must tune the deployment based on the target hardware.

### Tuning for `white` (RTX 3090)
The RTX 3090 has 24GB of VRAM. For larger models, we use **4-bit quantization** to reduce the memory footprint.

**`group_vars/white.yml`**
```yaml
# RTX 3090 Tuning
pair_gpu_devices: "device=0"
pair_mem_limit: "96G"           # Leave room for OS (128GB total)
pair_cpu_quota: "80%"
deploy_as_service: false        # Experimental: disable systemd auto-start
pair_extra_env:
  TRTL_QUANT: "4"              # Enable 4-bit quantization
```

### Tuning for `spark` (DGX Spark)
The `spark` node is a single superchip with unified memory. You don't need Tensor Parallelism (TP), but you can leverage the massive unified memory pool to run very large models.

**`group_vars/spark.yml`**
```yaml
# DGX Spark Tuning
pair_gpu_devices: "all"
deploy_as_service: true         # Production: enable systemd auto-start
pair_extra_env:
  TRTL_QUANT: "4"              # 4-bit for maximum model size/throughput
```

:::warning
**Architecture Note**: Since the DGX Spark uses an ARM-based Grace Blackwell chip (`aarch64`), ensure that the Docker image you are pulling supports the ARM64 architecture.
:::

**Why this matters:** 
Unified memory on the DGX Spark removes the "bottleneck" of transferring data between CPU RAM and GPU VRAM. This allows for much higher efficiency when loading huge models that would typically require a cluster of 8 A100s, but simplifies the configuration since it behaves as a single, massive device.


---

## 6. Verification and Performance

Once deployed, you need a way to verify the health of your cluster from your Mac.

### The Cluster Probe Script

Use a central script to check the status of all nodes in one go.

**`probe_cluster.sh`**
```bash
#!/usr/bin/env bash
# probe_cluster – Quick overview of laptop, white, and spark
set -euo pipefail

run_remote() {
  local host=$1
  ssh "$host" '
    echo "=== '"$host"' ==="
    echo -n "GPU:    "; nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "none"
    echo -n "Pair:   "; docker ps --filter name=nvidia-pair --format "{{.Names}} {{.Status}}" 2>/dev/null || echo "not running"
    echo ""
  '
}

echo "=== mac (local) ==="
echo -n "GPU:    "; system_profiler SPDisplaysDataType | grep "Chipset Model" | sed -e "s/.*: //"
echo ""

for host in white spark; do
  run_remote "$host"
done
```

### Performance Checklist

After launch, verify these metrics to ensure you aren't leaving performance on the table:

| Metric | Target Range | Verification Command |
| :--- | :--- | :--- |
| **GPU Util** | $\ge 70\%$ | `nvidia-smi -l 1` |
| **VRAM Util** | $\le 80\%$ | `nvidia-smi` (Avoid OOM) |
| **Latency** | $\le 150\text{ms}$ | Measure Time-to-First-Token in UI |
| **Host RAM** | Free $\ge 20\text{GB}$ | `free -h` |

---

!!! assignment "Hands-on Lab: Cluster Deployment"
    Carry out the following tasks to demonstrate your mastery of the material:

    1. **The Fast-Track**: Deploy NVIDIA AI Pair on the `white` node using the manual `docker run` command. Verify you can access the UI from your Mac.
    2. **The Power-Up**: Deploy Pair on the `spark` node. Configure it for 4-bit quantization and verify it can leverage the Blackwell unified memory. 
    3. **The Automator**: Initialize the `pair-ansible` project. Encrypt your API key using `ansible-vault` and successfully run the `site.yml` playbook across the entire cluster.
    4. **The Hardening**: For one of the nodes, manually implement the `systemd` service. Restart the machine and verify that the Pair UI is automatically available upon reboot.
    5. **The Analyst**: Use the `probe_cluster.sh` script to generate a report of all nodes. Note the VRAM usage on `white` versus `spark` while running a 7B parameter model.

---


---

## 7. Knowledge Check

Verify your understanding of the deployment before moving to the next chapter:

- [ ] **Do I know why Ansible is preferred over a Bash loop for this setup?** (Repeatability & Secret Management)
- [ ] **Can I explain the difference between `TRTL_QUANT` and `TRTL_TENSOR_PARALLEL`?** (Memory reduction vs. Compute distribution)
- [ ] **Am I storing the NGC API key securely?** (Using Ansible Vault, not plaintext)
- [ ] **Do the `group_vars` for `white` and `spark` reflect their actual GPU counts?**
- [ ] **Does the `probe_cluster.sh` script successfully connect to all nodes?**


---

## Appendix A: Manual `systemd` Deployment

If you have completed your experimentation and want the benefits of `systemd` (auto-restart, boot-time start) but are not yet using the full Ansible workflow, you can set up the service manually on each node.

### 1. Create the Environment File
Create a file at `/etc/pair.env` to store your credentials and hardware-specific tuning. This keeps the service unit clean and reusable.

```bash
sudo nano /etc/pair.env
```

**For the `white` node (RTX 3090):**
```ini
NGC_API_KEY=your_actual_ngc_api_key
PAIR_PORT=8888
TRTL_QUANT=4
```

**For the `spark` node (DGX A100):**
```ini
NGC_API_KEY=your_actual_ngc_api_key
PAIR_PORT=8888
TRTL_QUANT=4
TRTL_TENSOR_PARALLEL=8
```

Set strict permissions on this file since it contains your API key:
```bash
sudo chmod 600 /etc/pair.env
```

### 2. Create the `systemd` Unit File
Create the service definition at `/etc/systemd/system/nvidia-pair.service`.

```bash
sudo nano /etc/systemd/system/nvidia-pair.service
```

Paste the following configuration:

```ini
[Unit]
Description=NVIDIA AI Pair container
After=network.target docker.service
Requires=docker.service

[Service]
Restart=always
# Ensure any existing container with the same name is removed before starting
ExecStartPre=-/usr/bin/docker rm -f nvidia-pair
ExecStart=/usr/bin/docker run --rm \
  --gpus all \
  --name nvidia-pair \
  --env-file /etc/pair.env \
  -p 8888:8888 \
  nvcr.io/nvidia/pair:latest
ExecStop=/usr/bin/docker stop nvidia-pair

[Install]
WantedBy=multi-user.target
```

:::tip
**GPU Selection**: If you are on the `white` node and want to be explicit about the GPU, change `--gpus all` to `--gpus '"device=0"'`.
:::

### 3. Activate the Service
Run the following commands to tell `systemd` about the new service and start it:

```bash
# Reload systemd to pick up the new unit file
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable nvidia-pair

# Start the service now
sudo systemctl start nvidia-pair
```

### 4. Management Commands
Once the service is running, use these commands for maintenance:

| Action | Command |
| :--- | :--- |
| **Check Status** | `sudo systemctl status nvidia-pair` |
| **View Logs** | `sudo journalctl -u nvidia-pair -f` |
| **Restart** | `sudo systemctl restart nvidia-pair` |
| **Stop** | `sudo systemctl stop nvidia-pair` |

**Why this matters:** 
Moving from manual `docker run` to `systemd` transforms your AI node from a "lab experiment" into a "production service." It ensures that if a node reboots due to a power outage or a kernel update, your AI Pair instance is back online automatically without manual intervention.


---

## Appendix B: Adapting for OpenStack GPU VMs

In many enterprise environments, you won't have access to bare-metal workstations like `white` or `spark`. Instead, you will use **OpenStack** to provision Virtual Machines (VMs) with GPU passthrough. While the core `nvidia_pair` logic remains the same, the infrastructure orchestration changes.

### 1. Infrastructure Adjustments

When moving to OpenStack, there are three primary changes to your workflow:

#### A. Networking & Security Groups
Unlike a local network, OpenStack VMs are protected by **Security Groups**. 
- **Action**: You must create a rule to allow inbound TCP traffic on port `8888` (or your configured `PAIR_PORT`) from your Mac's IP address.
- **Why this matters**: Without this, your Mac will be unable to reach the Pair UI, even if the container is running perfectly on the VM.

#### B. GPU Passthrough & Drivers
OpenStack typically provides GPUs via PCI Passthrough. 
- **Verification**: Once the VM is booted, run `lspci | grep -i nvidia`. If no device is found, the "Flavor" selected during VM creation did not include a GPU.
- **Driver Installation**: Depending on the image provided by your OpenStack admin, you may need to install the NVIDIA drivers manually before running the Ansible playbook.

#### C. Dynamic Inventory
Instead of a static `inventory.ini`, you can leverage the `openstack.cloud` Ansible collection to automatically discover your GPU VMs based on tags.

**Example `openstack_inventory.yml`:**
```yaml
plugin: openstack.cloud.openstack
projects:
  - project_name: "ai-lecture-project"
groups:
  gpu_nodes: "tags == 'gpu-node'"
```

### 2. Modified Ansible Workflow for OpenStack

To scale your deployment to $N$ OpenStack VMs, follow this updated pipeline:

1.  **Provision**: Use OpenStack CLI or Terraform to spin up $N$ VMs using a GPU-enabled flavor.
2.  **Tag**: Tag these VMs as `gpu-node`.
3.  **Auth**: Configure your `clouds.yaml` file on your Mac with the OpenStack credentials.
4.  **Deploy**: Run the playbook using the dynamic inventory:
    ```bash
    ansible-playbook -i openstack_inventory.yml site.yml
    ```

:::tip
**Elastic Scaling**: The beauty of the OpenStack approach is that you can scale your compute power up or down in minutes. To add a new node, simply boot a new VM with the `gpu-node` tag and re-run the playbook.
:::

:::warning
**Flavor Constraints**: Not all OpenStack flavors are created equal. Ensure you select a flavor that specifies **GPU passthrough**. If you use a vGPU (virtual GPU) flavor, you may need to install the NVIDIA GRID drivers instead of the standard datacenter drivers.
:::

**Why this matters:** 
Shifting from static hardware to OpenStack VMs transforms your AI setup into an **elastic resource**. You can provision a massive cluster for a weekend of heavy training/testing and then destroy the VMs to save costs, all while maintaining a consistent software environment through the same Ansible roles used for bare metal.


---

## Appendix C: Obtaining your NGC API Key

To pull the private **NVIDIA AI Pair** image from the NVIDIA GPU Cloud (NGC), you must authenticate using a personal API key. This key acts as your credential for the `nvcr.io` registry.

### Step-by-Step Guide

1.  **Visit the NGC Portal**: Go to [ngc.nvidia.com](https://ngc.nvidia.com).
2.  **Sign In / Create Account**: Log in with your NVIDIA account. If you don't have one, you will need to create a free account.
3.  **Access Setup**: Once logged in, click on your username in the top right corner and select **Setup** from the dropdown menu.
4.  **Generate API Key**: 
    -   Under the **API Key** section, click the **Generate API Key** button.
    -   A modal will appear containing your unique key.
5.  **Secure the Key**: **Copy the key immediately**. For security reasons, NGC will not show the key again once you close the window. If you lose it, you will have to generate a new one.

### How to use the key

Once you have the key, you can use it in the following ways:

- **Direct Docker Login**:
  ```bash
  docker login nvcr.io
  # Username: $oauthtoken (literally the string "$oauthtoken")
  # Password: <YOUR_GENERATED_API_KEY>
  ```
- **Ansible Vault**: Store it in your `vault.yml` as `ngc_api_key: "your_key_here"` to automate deployments securely.
- **Environment File**: Paste it into `/etc/pair.env` (for manual setup) as `NGC_API_KEY=your_key_here`.

:::warning
**Credential Safety**: Your API key provides access to your NGC resources. **Never commit your API key in plaintext to a public Git repository.** Always use environment variables, `.env` files (added to `.gitignore`), or secret managers like Ansible Vault.
:::

**Why this matters:** 
NVIDIA hosts many of its high-performance AI containers in private registries to ensure that users are authenticated and can be provided with the latest stable versions of the software. The API key is the "passport" that allows your `laptop`, `white`, and `spark` nodes to securely fetch the latest AI Pair images.


---

## Appendix D: Can I run this without the NVIDIA API Key?

A common question when setting up this environment is whether the `NGC_API_KEY` is strictly necessary or if there is a "community" or "public" version of the software.

**The short answer is: No.** You cannot run the official NVIDIA AI Pair setup without an NGC API key.

### Why the key is mandatory

There are two primary "barriers" that make the API key a hard requirement:

#### 1. The Registry Barrier (Pulling the Image)
The software is distributed as a Docker container hosted on the **NVIDIA GPU Cloud (NGC)** registry (`nvcr.io`). Unlike public images on Docker Hub, the AI Pair image is **private**.
- **Without the key**: Any attempt to run `docker pull nvcr.io/nvidia/pair:latest` will result in an `unauthorized: authentication required` error.
- **With the key**: The API key allows you to authenticate (using the username `$oauthtoken`) and download the official, optimized image.

#### 2. The Runtime Barrier (Starting the Application)
Even if the image was acquired through other means, the application is designed to require authentication at runtime.
- **Authentication Check**: In all our deployment methods (Ansible, Bash, and systemd), we pass the key into the container via the `-e NGC_API_KEY=...` environment variable.
- **Backend Access**: The software uses this key to communicate with NVIDIA's backend services for licensing, telemetry, and potentially for downloading specific model weights. Without this key, the application will fail to initialize.

### Summary for Users

- **Cost**: Creating an NGC account and generating an API key is **free**.
- **Mandatory Status**: It is a strict requirement for accessing the official NVIDIA distribution.
- **Security**: Because the key is a credential, always store it securely (e.g., using **Ansible Vault** or protected environment files) and **never commit it to a public Git repository**.

**Verdict**: The `NGC_API_KEY` is the "passport" for the AI Pair ecosystem; it is required both to obtain the software and to execute it.

