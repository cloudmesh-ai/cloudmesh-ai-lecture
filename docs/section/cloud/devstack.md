
# Running OpenStack Locally with DevStack

*Author’s Note: This chapter is a self‑contained guide to the official DevStack documentation (https://docs.openstack.org/devstack/latest/). All the material has been reorganised, expanded, and presented in a narrative format suitable for readers who want to set up a functional OpenStack development environment on a single machine.*

---

## 1. Introduction  

DevStack is an **automated script collection** that builds a complete OpenStack cloud from source on a fresh Ubuntu, Fedora, or CentOS host. It is primarily intended for **development, testing, and learning**, not for production deployments. By cloning the DevStack repository and running a handful of commands, a developer can obtain a working OpenStack installation that includes the core services:

| Service | Role in OpenStack |
|---------|-------------------|
| **Keystone** | Identity (authentication and authority) |
| **Glance**   | Image service (store and retrieve VM images) |
| **Nova**     | Compute service (manage VM lifecycle) |
| **Neutron**  | Networking service (virtual networking) |
| **Cinder**   | Block storage service |
| **Horizon**  | Web dashboard (GUI) |
| **Swift**    | Object storage service (optional) |
| **Heat**     | Orchestration (template‑driven deployment) |
| **Troves**   | Database as a service (optional) |

Because DevStack installs everything from the latest upstream source, it provides a **reference environment** that reflects the current OpenStack code‑base. It is an excellent platform for:

* Experimenting with new features or patches.  
* Writing and testing third‑party OpenStack plugins.  
* Running integration tests for CI pipelines.  
* Teaching OpenStack fundamentals in a lab setting.

---

## 2. Prerequisites  

### 2.1 Hardware Requirements  

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 + cores |
| RAM | 4 GB | 8 GB + |
| Disk | 30 GB | 50 GB + (SSD preferred) |
| Network | Single NIC with internet access | Separate NIC for management & external traffic (optional) |

DevStack performs a full source checkout, compilation of some components (e.g., Nova compute, Neutron plugins), and launches multiple services, so lack of memory or CPU will result in long build times or unstable operation.

### 2.2 Operating System  

Supported distributions (as of the latest documentation) are:

* **Ubuntu LTS** – 22.04 (Jammy Jellyfish) and 20.04 (Focal Fossa)  
* **Fedora** – most recent stable release  
* **CentOS / Rocky Linux** – versions that provide systemd and the required package versions  

The OS must be a **clean installation** (no conflicting OpenStack services) and should be updated (`apt update && apt upgrade` or equivalent) before proceeding.

### 2.3 Software Dependencies  

DevStack automates most dependency installation, but the host must provide:

| Dependency | Purpose |
|------------|---------|
| `git` | Retrieve the DevStack source repository |
| `python3` (≥ 3.8) and `pip` | Run OpenStack services written in Python |
| `curl`, `wget` | Download external resources |
| `virt‑manager`/`qemu‑kvm` | Provide the hypervisor for Nova |
| `iptables`, `iproute2` | Network configuration for Neutron |
| `libvirt`, `lxc` (optional) | Alternate compute drivers |
| `gcc`, `make`, `automake` | Build native extensions |

All required packages are listed in DevStack’s `tools/install_prereqs.sh` script and are installed automatically when the `stack.sh` script is executed with root privileges.

### 2.4 User Account  

DevStack expects a **non‑root user** named `stack`. The usual workflow:

```bash
# As root
adduser --disabled-password --gecos "" stack
usermod -aG sudo stack

# Switch to the new user
su - stack
```

The `stack` user will own the DevStack working directory (`/opt/devstack` by default) and run all subsequent scripts.

---

## 3. Acquiring DevStack  

The canonical source is the official Git repository:

```bash
# As the stack user
git clone https://opendev.org/openstack/devstack.git
cd devstack
```

The repository contains the following important items:

| File/Directory | Description |
|----------------|-------------|
| `stack.sh` | Primary driver script – performs all installation steps. |
| `unstack.sh` | Gracefully stops all services without removing the configuration. |
| `clean.sh` | Removes all services, databases, and configuration, returning the host to a pre‑DevStack state. |
| `local.conf.example` | Sample configuration file that can be copied to `local.conf` for customization. |
| `extras.d/` | Directory for optional plugins and services (e.g., Swift, Sahara). |
| `tools/` | Helper scripts for prerequisite installation and diagnostics. |
| `releasenotes/` | Release‑specific notes and known issues. |

You may optionally checkout a particular release branch (e.g., `stable/2024.1`) to freeze the code at a known state:

```bash
git checkout stable/2024.1
```

---

## 4. Configuring DevStack  

### 4.1 The `local.conf` File  

DevStack is intentionally *opinionated* but fully configurable via a single **`local.conf`** file placed in the top‑level DevStack directory. The file follows the INI‑style syntax with sections and key/value pairs. A minimal configuration might look like:

```ini
[[local|localrc]]
ADMIN_PASSWORD=secretadmin
DATABASE_PASSWORD=secretdb
RABBIT_PASSWORD=secretrabbit
SERVICE_PASSWORD=secretservice
HOST_IP=192.168.56.101
LOGFILE=$HOME/devstack.log
```

Key points:

* **Passwords** – Only a handful of passwords are required; DevStack propagates them to all services.  
* **HOST_IP** – Explicitly set the management interface IP; DevStack otherwise attempts to auto‑detect it.  
* **LOGFILE** – Useful for post‑mortem debugging; the default location is `$HOME/devstack.log`.  

### 4.2 Enabling/Disabling Services  

To tailor the cloud, you can toggle services with `enable_service` and `disable_service` directives:

```ini
[[local|localrc]]
enable_service horizon
disable_service tempest
```

Common toggles:

| Directive | Effect |
|-----------|--------|
| `enable_service q-svc q-agt q-dhcp q-l3 q-meta` | Activate Neutron components (service, agent, DHCP, L3 router, metadata). |
| `disable_service s-proxy` | Turn off Swift proxy service (if you do not need object storage). |
| `enable_plugin heat https://opendev.org/openstack/heat` | Add Heat as an extra plugin from its upstream repository. |

### 4.3 Customizing Hypervisors  

By default DevStack uses **KVM/QEMU** with the `libvirt` driver. To switch to the LXC driver, add:

```ini
[[local|localrc]]
LIBVIRT_TYPE=lxc
```

For use of **bare-metal** bare‑metal (Ironic) or **Docker** as a compute driver, refer to the “Advanced Compute” section in the official docs and add the corresponding plugins.

### 4.4 Network Configuration  

Neutron can be launched in several modes:

| Mode | Description | Typical Setting |
|------|-------------|-----------------|
| **Flat** | Single layer‑2 bridge; all VMs share the host’s physical network. | `Q_AGENT=flat` |
| **VLAN** | VLAN tagging for tenant isolation. | `Q_AGENT=vlan` |
| **VXLAN** | Overlay network using VXLAN tunnels (default). | No special setting required. |
| **GRE** | Legacy GRE overlay. | `Q_AGENT=gre` |

The default VXLAN mode works on most single‑node setups; it requires the kernel module `vxlan` and appropriate iptables rules, which DevStack configures automatically.

### 4.5 Persistent Configuration  

Because DevStack rebuilds the environment each time `stack.sh` runs, configuration edits should be done **only** in `local.conf`. Avoid editing files under `/etc/` directly; they will be overwritten on the next `stack.sh` invocation.

---

## 5. Running DevStack  

### 5.1 The Main Script  

All installation steps are performed by executing **`./stack.sh`** as the `stack` user:

```bash
./stack.sh
```

What happens under the hood:

1. **Prerequisite Installation** – Installs missing OS packages (`tools/install_prereqs.sh`).  
2. **Database Setup** – Creates MySQL (or MariaDB) databases for each OpenStack service.  
3. **Keystone Initialization** – Sets up tenants, users, and service catalog entries.  
4. **Service Deployment** – Sequentially launches each component (Glance, Nova, Neutron, etc.) using systemd unit files generated on‑the‑fly.  
5. **Horizon Web UI** – Configures Apache with the dashboard; starts the HTTP service on port 80 (or 8080 if port 80 is unavailable).  
6. **Templating & Extras** – Executes any `extras.d` scripts (e.g., Heat, Magnum) and optional plugins.  

The script logs progress to both the console and the file defined by `LOGFILE`. Completion is signaled by the message:

```
stack.sh screen log file is /opt/devstack/logs/stack.sh.log
```

### 5.2 Verifying the Installation  

After `stack.sh` finishes:

* **Dashboard** – Open a browser and navigate to `http://<HOST_IP>/dashboard`. Log in with username `admin` and the password set in `ADMIN_PASSWORD`.  
* **CLI** – Source the OpenStack client credentials:

  ```bash
  source openrc admin admin
  openstack token issue
  ```

  A successful token issuance confirms that Keystone, the CLI, and the environment variables are correctly set.  

* **Service Status** – Use `systemctl` or `ps aux | grep nova` to verify that the daemons are running.  

### 5.3 Common Post‑Installation Tasks  

| Task | Command |
|------|---------|
| List available flavors | `openstack flavor list` |
| Upload a test image (CirrOS) | `openstack image create --disk-format qcow2 --container-format bare --public --file cirros-0.5.2-x86_64-disk.img cirros` |
| Create a network | `openstack network create private-net` |
| Create a subnet | `openstack subnet create --network private-net --subnet-range 192.168.100.0/24 private-subnet` |
| Launch an instance | `openstack server create --flavor m1.tiny --image cirros --network private-net test-instance` |
| Access the instance console | `openstack console log show test-instance` |

These commands illustrate that the core services are operational and ready for experimentation.

---

## 6. Managing the DevStack Lifecycle  

### 6.1 Stopping Services (`unstack.sh`)  

When you need to halt the cloud without destroying the configuration (e.g., to free system resources), run:

```bash
./unstack.sh
```

`unstack.sh` stops all OpenStack processes **gracefully** using the generated systemd unit files. The databases and configuration files remain intact, allowing a quick `./stack.sh` later.

### 6.2 Cleaning Up (`clean.sh`)  

To bring the host back to a pristine state (useful before reinstalling or repurposing the machine), execute:

```bash
./clean.sh
```

`clean.sh` removes:

* All OpenStack databases.  
* All generated configuration files under `/etc/`.  
* The `stack` user’s local directories (`$HOME/devstack`).  
* Any residual network bridges or iptables rules created by Neutron.

After `clean.sh` the host is effectively a clean OS box, ready for a fresh DevStack run.

### 6.3 Updating DevStack  

To pull the latest changes from the upstream repository:

```bash
git pull
```

Then re‑run `./stack.sh`. DevStack detects existing resources and will upgrade the services as needed. For major version changes you may prefer to `clean.sh` first to avoid incompatibilities.

---

## 7. Extending DevStack  

### 7.1 Adding Plugins  

DevStack’s extensibility revolves around the `extras.d/` directory and the `enable_plugin` directive in `local.conf`. The workflow for an external service (e.g., **Magnum** for container orchestration) is:

1. **Add the plugin line** to `local.conf`:

   ```ini
   enable_plugin magnum https://opendev.org/openstack/magnum
   ```

2. **Optionally provide configuration** in `local.conf` (e.g., `MAGNUM_HOST=...`).  
3. **Re‑run** `./stack.sh`. During the “Extras” phase DevStack clones the plugin repository, installs its dependencies, and registers the service with Keystone.

### 7.2 Overriding Service Defaults  

You can override any service-specific configuration by placing a snippet in the `local.conf` section named after the service. For example, to change Nova’s compute driver:

```ini
[[local|localrc]]
NOVA_COMPUTE_DRIVER=libvirt.LibvirtDriver
```

Or to force Neutron to use an alternate OVS bridge name:

```ini
[[local|localrc]]
Q_ML2_PLUGIN_MECHANISM_DRIVERS=linuxbridge
Q_AGENT=linuxbridge
```

### 7.3 Running Tests  

DevStack integrates **Tempest**, the official OpenStack integration test suite. To run the baseline tests:

```bash
cd /opt/stack/tempest
tempest run --smoke
```

Pass `--regex` or `--exclude-list` to focus on or omit specific test sets. This is valuable for validating patches before submitting them upstream.

---

## 8. Troubleshooting  

Below is a collection of frequent failure modes and recommended remediation steps.

### 8.1 Stack Script Aborts Early  

*Symptom*: `stack.sh` exits with a non‑zero status after the *“Running in screen…”* message.  

*Root Causes & Fixes*:

| Cause | Fix |
|-------|-----|
| Missing package (e.g., `libffi-dev`) | Re‑run `tools/install_prereqs.sh` or install manually (`apt install libffi-dev`). |
| Incompatible Python version (e.g., Python 3.6 on Ubuntu 22.04) | Install the required Python (≥ 3.8) and ensure the `python3` symlink points to it. |
| Insufficient memory (swap exhausted) | Increase swap space (`sudo fallocate -l 2G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`). |

Inspect the tail of `stack.sh.log` for the exact traceback.

### 8.2 Keystone Authentication Fails  

*Symptom*: `openstack token issue` returns `HTTP 401 Unauthorized`.  

*Checks*:

1. Verify that `source openrc admin admin` sourced the correct `OS_PASSWORD`.  
2. Ensure `ADMIN_PASSWORD` in `local.conf` matches the password you entered.  
3. Confirm the Keystone service is up: `systemctl status devstack@keystone.service`.  

If Keystone is down, restart it with `sudo systemctl restart devstack@keystone.service` and inspect `/var/log/keystone/keystone.log`.

### 8.3 Neutron Network Not Created  

*Symptom*: `openstack network create` returns `Network creation failed`.  

*Typical Reasons*:

| Reason | Resolution |
|--------|------------|
| Missing OVS kernel module | Load it: `sudo modprobe openvswitch`. |
| iptables rules block VXLAN UDP traffic | Flush conflicting rules: `sudo iptables -F`. |
| Bridge name conflict (`br-int` already exists) | Delete the stale bridge: `sudo ip link delete br-int`. |

After fixing, run `./unstack.sh && ./stack.sh` to rebuild the networking stack.

### 8.4 Horizon Returns 502 Bad Gateway  

*Symptom*: Browser shows a 502 error for `http://<HOST_IP>/dashboard`.  

*Diagnose*:

```bash
sudo systemctl status apache2      # Ubuntu
sudo systemctl status httpd        # Fedora/CentOS
```

If the Apache service is down, check the error log (`/var/log/apache2/error.log` or `/var/log/httpd/error_log`). Common issues include:

* **WSGI daemon process failed** – often due to missing Python dependencies. Re‑install the `horizon` virtual environment: `cd /opt/stack/horizon && ./tools/install_venv.sh`.  
* **Permission errors on `/var/lib/horizon`** – ensure the `stack` user owns the directory.

Restart Apache after fixing: `sudo systemctl restart apache2`.

### 8.5 Image Upload Fails  

*Symptom*: `openstack image create` ends with `Cannot allocate memory` or `InvalidImageBadMagic`.  

*Resolution*:

* For memory‑related failures, raise the swap size or free RAM.  
* For “BadMagic”, verify the image format matches the command line flags (`--disk-format qcow2`). Use `qemu-img info <image>` to confirm.

---

## 9. Best Practices for a DevStack Lab  

1. **Isolate the DevStack host** – Use a dedicated VM or physical machine; avoid installing other services that may conflict with ports 80, 443, 5000, 8774, etc.  
2. **Version Pinning** – If you need repeatability, checkout a specific tag (`git checkout tags/2024.1`) and lock the `requirements.txt` files.  
3. **Regular Snapshots** – Take snapshots of the VM after a successful `stack.sh`. This allows rapid rollback.  
4. **Separate Data Directory** – By default DevStack stores images and volumes under `/opt/stack/data`. Mount a dedicated disk to this path to prevent disk‑full issues.  
5. **Use a Dedicated Virtual Network** – Configure a host‑only network (e.g., `192.168.56.0/24`) for tenant traffic, keeping external internet access via NAT.  
6. **Automate with CI** – Wrap `stack.sh` and `unstack.sh` in a Jenkins or GitHub Actions pipeline to run integration tests on each patch.  

---

## 10. Summary  

DevStack transforms a clean Linux host into a **fully functional OpenStack cloud** with a single command. By understanding its workflow—prerequisite installation, `local.conf`‑driven configuration, the `stack.sh` orchestration script, and the management utilities (`unstack.sh`, `clean.sh`)—developers can quickly prototype features, validate patches, and gain hands‑on experience with OpenStack’s myriad services.

Key takeaways:

* **Preparation matters**: Satisfy hardware, OS, and user‑account prerequisites before cloning the repository.  
* **Configuration is declarative**: All customisations belong in `local.conf`. Avoid editing service files directly.  
* **Lifecycle commands are idempotent**: `stack.sh` can be rerun safely; `unstack.sh` stops services, and `clean.sh` resets the host.  
* **Extensibility**: Use `enable_plugin` and the `extras.d` mechanism to add optional services such as Heat, Magnum, or Swift.  
* **Troubleshooting**: The log files (`devstack.log`, service‑specific logs under `/var/log/`) are the first line of defense when something goes wrong.  

With these concepts mastered, the reader can confidently spin up, modify, and dismantle OpenStack environments for development, testing, or instructional purposes—exactly as the official DevStack documentation intends.


## DevStck in docker


## Running DevStack inside Docker  

DevStack is primarily intended to be executed on a clean host OS, but it can also be built and started inside a Docker container. The container must be given a level of privilege that allows it to create network bridges, manage libvirt/KVM, and run system services. Below is a practical, step‑by‑step guide that shows how to create a reproducible Docker image, start a DevStack instance, and access the OpenStack services from the host.

---

### 1. Why run DevStack in Docker?  

| Benefit | What you get |
|---------|--------------|
| **Isolation** – The OpenStack services live in a separate PID, network, and filesystem namespace. |
| **Portability** – The same image can be moved between laptops, CI runners, or temporary VMs. |
| **Repeatability** – The build process is captured in a Dockerfile, so you can recreate the exact environment on demand. |
| **Fast teardown** – Removing the container restores the host to the pre‑DevStack state without a “clean‑up” script. |

> **Caveat** – Because DevStack needs to manipulate kernel networking (iptables, bridges) and the hypervisor, the container must run in **privileged mode** (or be granted a specific set of capabilities). This means the container is not suitable for untrusted users or for production workloads.

---

### 2. Prerequisites on the Host  

| Item | Minimum version / configuration |
|------|---------------------------------|
| Docker Engine | 24.0+ (Docker Desktop or native daemon) |
| Kernel modules | `bridge`, `ip_tables`, `vxlan`, `openvswitch`, `kvm` (if you want KVM) |
| Sufficient resources | ≥ 8 GB RAM, ≥ 4 CPU cores, ≥ 30 GB free disk |
| Network access | Outbound internet connectivity (for `git clone` and package installation) |

Make sure the current user can run Docker commands, e.g.:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

### 3. Dockerfile – Building a DevStack Image  

Below is a minimal, production‑ready Dockerfile that follows the official DevStack documentation. It is based on Ubuntu 22.04, installs all required packages, clones the DevStack repository, and provides a default `local.conf` that can be overridden at run‑time.

```dockerfile
# --------------------------------------------------------------
# Dockerfile – DevStack in Docker
# --------------------------------------------------------------

# 1️⃣ Base image
FROM ubuntu:22.04

# 2️⃣ Environment variables used by DevStack
ENV DEVSTACK_DIR=/opt/devstack \
    DEVSTACK_LOG=/opt/devstack/logs/devstack.log \
    HOST_IP=127.0.0.1 \
    ADMIN_PASSWORD=secretadmin \
    DATABASE_PASSWORD=secretdb \
    RABBIT_PASSWORD=secretrabbit \
    SERVICE_PASSWORD=secretservice

# 3️⃣ Install OS packages required for DevStack
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    git \
    sudo \
    curl \
    wget \
    vim \
    less \
    net-tools \
    iproute2 \
    iptables \
    bridge-utils \
    openvswitch-switch \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    libffi-dev \
    libssl-dev \
    gcc \
    g++ \
    make \
    automake \
    libtool \
    pkg-config \
    libpq-dev \
    libmysqlclient-dev \
    libvirt-daemon-system \
    libvirt-clients \
    qemu-kvm \
    virtinst \
    ovmf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 4️⃣ Create the non‑root “stack” user (the official DevStack user)
RUN useradd -ms /bin/bash stack && echo "stack ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 5️⃣ Switch to the stack user and clone DevStack
USER stack
WORKDIR /opt

RUN git clone https://opendev.org/openstack/devstack.git

# 6️⃣ Provide a default local.conf (can be overridden at container start)
RUN cat > /opt/devstack/local.conf <<'EOF'
[[local|localrc]]
HOST_IP=$(hostname -I | awk '{print $1}')
ADMIN_PASSWORD=secretadmin
DATABASE_PASSWORD=secretdb
RABBIT_PASSWORD=secretrabbit
SERVICE_PASSWORD=secretservice
LOGFILE=$HOME/devstack.log
ENABLE_TEMPEST_NOTIFICATIONS=False
EOF

# 7️⃣ Expose the ports that Horizon, Keystone, Nova, Neutron, etc. use.
#    (Only the most common ports are listed; additional ports can be added
#    via -p when the container is launched.)
EXPOSE 80 443 5000 5001 8774 8776 8777 9696 3260

# 8️⃣ Entry point – start DevStack when the container runs.
#    The script will block until all services are up, then tail the log.
ENTRYPOINT ["/bin/bash", "-c", "\
    cd $DEVSTACK_DIR && \
    sudo ./stack.sh && \
    tail -F $DEVSTACK_LOG \
"]
```

**Explanation of the key sections**

* **Base image** – Ubuntu 22.04 matches the list of officially supported distributions.
* **Package installation** – Mirrors `tools/install_prereqs.sh`; all binaries needed for compute, networking, and database back‑ends are installed.
* **Non‑root `stack` user** – DevStack expects to be run as a non‑root account.
* **`local.conf`** – Supplies minimal passwords and enables the log file. The `HOST_IP` is resolved at container start time, which works when the container is attached to the host network (`--network host`) or when you map a specific IP.
* **Exposed ports** – Horizon (80/443), Keystone (5000/5001), Nova (8774/8776/8777), Neutron (9696), iSCSI (3260) … you can add more if you enable extra services.
* **Entry point** – Runs `stack.sh`; after the installation finishes it tails the DevStack log so the container does not exit.

---

### 4. Building the Image  

```bash
docker build -t devstack:latest .
```

The build takes 15‑30 minutes on a typical workstation because it compiles a few components and pulls a large number of packages. When the build completes you will have a `devstack:latest` image ready for launch.

---

### 5. Running the Container  

Because DevStack needs to manipulate networking and the hypervisor, the container must be launched with elevated privileges. There are two common approaches:

#### 5.1 Host‑network mode (simplest)

```bash
docker run -d \
    --name devstack \
    --privileged \
    --network host \
    -e ADMIN_PASSWORD=MySecretPass \
    -e SERVICE_PASSWORD=MySecretPass \
    devstack:latest
```

* `--network host` bypasses Docker’s NAT layer, allowing the OpenStack services to bind directly on the host’s interfaces.  
* `--privileged` grants all capabilities, including `CAP_NET_ADMIN` and `CAP_SYS_MODULE`, which DevStack needs for bridge and OVS setup.  
* Environment variables can be used to override the passwords defined in the image.

#### 5.2 Bridged network with explicit port mapping

If you prefer not to use host networking, map the required ports explicitly:

```bash
docker run -d \
    --name devstack \
    --privileged \
    -p 80:80 -p 443:443 \
    -p 5000:5000 -p 5001:5001 \
    -p 8774:8774 -p 8776:8776 -p 8777:8777 \
    -p 9696:9696 \
    -e ADMIN_PASSWORD=MySecretPass \
    devstack:latest
```

When using a bridged network, you must still set `HOST_IP` inside the container to an address reachable from the host (e.g., the host’s eth0 address). This can be done by passing a custom `local.conf` as a bind‑mount:

```bash
# Create a host‑side custom configuration
cat > my_local.conf <<EOF
[[local|localrc]]
HOST_IP=192.168.56.101
ADMIN_PASSWORD=MySecretPass
DATABASE_PASSWORD=MySecretPass
RABBIT_PASSWORD=MySecretPass
SERVICE_PASSWORD=MySecretPass
EOF

docker run -d \
    --name devstack \
    --privileged \
    -p 80:80 -p 5000:5000 \
    -v $(pwd)/my_local.conf:/opt/devstack/local.conf:ro \
    devstack:latest
```

---

### 6. Accessing the OpenStack Cloud  

| Service | URL (if `HOST_IP=192.168.56.101`) | Default credentials |
|---------|------------------------------------|----------------------|
| Horizon dashboard | `http://192.168.56.101/` | `admin / <ADMIN_PASSWORD>` |
| Keystone API (public) | `http://192.168.56.101:5000/v3` | `admin / <ADMIN_PASSWORD>` |
| Nova API | `http://192.168.56.101:8774/v2.1` | — |
| Neutron API | `http://192.168.56.101:9696` | — |

You can source the OpenStack RC file inside the container (or copy it to the host) to use the CLI:

```bash
# Inside the container (as stack user)
source /opt/devstack/openrc admin admin
openstack token issue
```

If you prefer to run the CLI on the host, copy the `openrc` file out:

```bash
docker cp devstack:/opt/devstack/openrc ./devstack-openrc
source ./devstack-openrc admin admin
openstack server list
```

---

### 7. Stopping and Cleaning Up  

| Action | Command |
|--------|---------|
| Stop the DevStack services (container continues to exist) | `docker stop devstack` |
| Remove the container and its filesystem | `docker rm -f devstack` |
| Re‑run from a clean state (re‑build not required) | `docker run …` again |
| Rebuild the image after changing the Dockerfile | `docker build -t devstack:latest .` |

Because the container runs `stack.sh` each time it starts, you do **not** need to invoke `unstack.sh` or `clean.sh` manually; the container is destroyed and recreated from the image.

---

### 8. Known Limitations & Gotchas  

| Issue | Why it happens | Work‑around |
|-------|----------------|------------|
| **Nested virtualization** – Running DevStack inside Docker on a laptop that already runs inside a VM may fail because KVM cannot be accessed. | The container needs `/dev/kvm`. If the host VM does not expose KVM, libvirt will fall back to QEMU‑software mode (much slower). | Either enable nested virtualization on the outer VM (e.g., `VBoxManage modifyvm … --nested-hw-virt on`) or use the *QEMU* driver (`LIBVIRT_TYPE=qemu`). |
| **Port conflicts** – The host may already have services listening on ports 80, 5000, etc. | Docker tries to bind the same ports for Horizon/Keystone. | Change the port mapping (`-p 8080:80`) or stop the conflicting host services. |
| **Persistent data** – By default, images, volumes, and databases disappear when the container is removed. | All data lives inside the container’s writable layer. | Mount a host directory or a Docker volume to `/opt/stack/data` and to `/var/lib/mysql` if you need persistence across container restarts. |
| **Resource consumption** – DevStack spawns many processes; a single container can easily use > 4 GB RAM. | The OpenStack services themselves are memory‑hungry. | Ensure the Docker daemon is configured with enough memory (`--memory` limit can be raised) or use a dedicated VM for the Docker host. |
| **Systemd services** – DevStack creates its own systemd units, but Docker does not run a full init system. | The `stack.sh` script launches services directly (via `systemctl` targeting the DevStack unit files). | The official DevStack Dockerfile uses the same approach; no additional init system is required. |

---

### 9. Alternative Approaches  

If the privileged‑container model feels too “heavy”, consider the following more production‑oriented projects that also provide a Docker‑based OpenStack deployment:

| Project | Description |
|---------|-------------|
| **Kolla‑Ansible** | Builds each OpenStack service as an individual Docker container and runs them with Docker‑Compose or Kubernetes. Suitable for more realistic multi‑node simulations. |
| **OpenStack‑Helm** | Deploys OpenStack on a Kubernetes cluster using Helm charts. Requires a K8s environment but gives the same level of isolation as containers. |
| **DevStack‑in‑Docker (community images)** | Some users have published pre‑built images (e.g., `tianon/devstack`). They are convenient for quick demos but may be outdated and lack customisation. We do not recommend them due to security concerns. |

These alternatives are recommended when you eventually need to experiment with scaling, HA, or integration with orchestration platforms.

---

### 10. Quick Reference Cheat‑Sheet  

```bash
# 1️⃣ Build the image
docker build -t devstack:latest .

# 2️⃣ Run (host‑network, privileged)
docker run -d --name devstack --privileged --network host devstack:latest

# 3️⃣ Verify
docker logs -f devstack            # watch the DevStack log
curl http://$(hostname -I | awk '{print $1}')/dashboard   # should show Horizon login

# 4️⃣ Use the CLI from the host
docker cp devstack:/opt/devstack/openrc .
source openrc admin admin
openstack server list

# 5️⃣ Stop & remove
docker stop devstack && docker rm devstack
```

---

## 11. TL;DR  

*Yes, you can run DevStack in Docker.*  
Create a Dockerfile (see Section 3), build the image, and launch the container with `--privileged` (and preferably `--network host`). After the container finishes its startup routine, Horizon is reachable on port 80 and the OpenStack CLI works after sourcing the generated `openrc`. The setup is fully reproducible, easy to tear down, and can be integrated into CI pipelines, but it requires privileged access and sufficient host resources.  

Feel free to adapt the `local.conf` template to enable extra services (Swift, Heat, Magnum) or to bind persistent volumes for images and block storage. If you later need a more granular, multi‑node deployment, explore Kolla‑Ansible or OpenStack‑Helm.