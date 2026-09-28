# Running OpenStack Locally with DevStack

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    - Understand the purpose and core services of DevStack.
    - Set up a local OpenStack environment on a Linux host.
    - Configure DevStack using the `local.conf` file.
    - Deploy and manage a DevStack instance using Docker.
    - Troubleshoot common installation and runtime issues in a DevStack environment.

## Overview

DevStack is an **automated script collection** that builds a complete OpenStack cloud from source on a fresh Ubuntu, Fedora, or CentOS host. It is primarily intended for **development, testing, and learning**, not for production deployments. By cloning the DevStack repository and running a handful of commands, a developer can obtain a working OpenStack installation that includes the core services.

| Service | Role in OpenStack |
|---------|-------------------|
| **Keystone** | Identity (authentication and authority) |
| **Glance**   | Image service (store and retrieve VM images) |
| **Nova**     | Compute service (manage VM lifecycle) |
| **Neutron**  | Networking service (virtual networking) |
| **Cinder**   | Block storage service |
| **Horizon**  | Web dashboard (GUI) |
| **Swift**    | Object storage service (optional) |
| **Heat**     | Orchestration (template-driven deployment) |
| **Troves**   | Database as a service (optional) |

Because DevStack installs everything from the latest upstream source, it provides a **reference environment** that reflects the current OpenStack codebase. It is an excellent platform for:

- Experimenting with new features or patches.
- Writing and testing third-party OpenStack plugins.
- Running integration tests for CI pipelines.
- Teaching OpenStack fundamentals in a lab setting.

## Prerequisites

### Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8 GB+ |
| Disk | 30 GB | 50 GB+ (SSD preferred) |
| Network | Single NIC with internet access | Separate NIC for management & external traffic (optional) |

DevStack performs a full source checkout, compilation of some components (e.g., Nova compute, Neutron plugins), and launches multiple services, so lack of memory or CPU will result in long build times or unstable operation.

### Operating System

Supported distributions (as of the latest documentation) are:

- **Ubuntu LTS** – 22.04 (Jammy Jellyfish) and 20.04 (Focal Fossa)
- **Fedora** – most recent stable release
- **CentOS / Rocky Linux** – versions that provide systemd and the required package versions

The OS must be a **clean installation** (no conflicting OpenStack services) and should be updated (`apt update && apt upgrade` or equivalent) before proceeding.

### Software Dependencies

DevStack automates most dependency installation, but the host must provide:

| Dependency | Purpose |
|------------|---------|
| `git` | Retrieve the DevStack source repository |
| `python3` (≥ 3.8) and `pip` | Run OpenStack services written in Python |
| `curl`, `wget` | Download external resources |
| `virt-manager`/`qemu-kvm` | Provide the hypervisor for Nova |
| `iptables`, `iproute2` | Network configuration for Neutron |
| `libvirt`, `lxc` (optional) | Alternate compute drivers |
| `gcc`, `make`, `automake` | Build native extensions |

All required packages are listed in DevStack's `tools/install_prereqs.sh` script and are installed automatically when the `stack.sh` script is executed with root privileges.

### User Account

DevStack expects a **non-root user** named `stack`. The usual workflow is:

```bash
# As root
adduser --disabled-password --gecos "" stack
usermod -aG sudo stack

# Switch to the new user
su - stack
```

The `stack` user will own the DevStack working directory (`/opt/devstack` by default) and run all subsequent scripts.

## Acquiring and Configuring DevStack

### Acquiring the Source

The canonical source is the official Git repository:

```bash
# As the stack user
git clone https://opendev.org/openstack/devstack.git
cd devstack
```

The repository contains several important files:

| File/Directory | Description |
|----------------|-------------|
| `stack.sh` | Primary driver script – performs all installation steps. |
| `unstack.sh` | Gracefully stops all services without removing the configuration. |
| `clean.sh` | Removes all services, databases, and configuration, returning the host to a pre-DevStack state. |
| `local.conf.example` | Sample configuration file that can be copied to `local.conf` for customization. |
| `extras.d/` | Directory for optional plugins and services (e.g., Swift, Sahara). |
| `tools/` | Helper scripts for prerequisite installation and diagnostics. |
| `releasenotes/` | Release-specific notes and known issues. |

You may optionally checkout a particular release branch (e.g., `stable/2024.1`) to freeze the code at a known state:

```bash
git checkout stable/2024.1
```

### The `local.conf` File

DevStack is intentionally opinionated but fully configurable via a single **`local.conf`** file placed in the top-level DevStack directory. The file follows an INI-style syntax. A minimal configuration might look like:

```ini
[[local|localrc]]
ADMIN_PASSWORD=secretadmin
DATABASE_PASSWORD=secretdb
RABBIT_PASSWORD=secretrabbit
SERVICE_PASSWORD=secretservice
HOST_IP=192.168.56.101
LOGFILE=$HOME/devstack.log
```

Key configuration points:

- **Passwords**: Only a handful of passwords are required; DevStack propagates them to all services.
- **HOST_IP**: Explicitly set the management interface IP; DevStack otherwise attempts to auto-detect it.
- **LOGFILE**: Useful for post-mortem debugging; the default location is `$HOME/devstack.log`.

### Enabling and Disabling Services

To tailor the cloud, you can toggle services with `enable_service` and `disable_service` directives in `local.conf`:

```ini
[[local|localrc]]
enable_service horizon
disable_service tempest
```

Common toggles include:

| Directive | Effect |
|-----------|--------|
| `enable_service q-svc q-agt q-dhcp q-l3 q-meta` | Activate Neutron components (service, agent, DHCP, L3 router, metadata). |
| `disable_service s-proxy` | Turn off Swift proxy service (if you do not need object storage). |
| `enable_plugin heat https://opendev.org/openstack/heat` | Add Heat as an extra plugin from its upstream repository. |

### Customizing Hypervisors and Networks

By default, DevStack uses **KVM/QEMU** with the `libvirt` driver. To switch to the LXC driver, add:

```ini
[[local|localrc]]
LIBVIRT_TYPE=lxc
```

Neutron can be launched in several modes:

| Mode | Description | Typical Setting |
|------|-------------|-----------------|
| **Flat** | Single layer-2 bridge; all VMs share the host's physical network. | `Q_AGENT=flat` |
| **VLAN** | VLAN tagging for tenant isolation. | `Q_AGENT=vlan` |
| **VXLAN** | Overlay network using VXLAN tunnels (default). | No special setting required. |
| **GRE** | Legacy GRE overlay. | `Q_AGENT=gre` |

The default VXLAN mode works on most single-node setups; it requires the kernel module `vxlan` and appropriate iptables rules, which DevStack configures automatically.

## Running and Managing DevStack

### Deployment

All installation steps are performed by executing **`./stack.sh`** as the `stack` user:

```bash
./stack.sh
```

The orchestration process includes:

1. **Prerequisite Installation**: Installs missing OS packages via `tools/install_prereqs.sh`.
2. **Database Setup**: Creates MySQL (or MariaDB) databases for each OpenStack service.
3. **Keystone Initialization**: Sets up tenants, users, and service catalog entries.
4. **Service Deployment**: Launches components (Glance, Nova, Neutron, etc.) using systemd unit files.
5. **Horizon Web UI**: Configures Apache and starts the dashboard on port 80 (or 8080).
6. **Templating & Extras**: Executes `extras.d` scripts and optional plugins.

Completion is signaled by the message: `stack.sh screen log file is /opt/devstack/logs/stack.sh.log`.

### Verification

After `stack.sh` finishes:

- **Dashboard**: Navigate to `http://<HOST_IP>/dashboard`. Log in with username `admin` and the password set in `ADMIN_PASSWORD`.
- **CLI**: Source the OpenStack client credentials and verify with a token issue:

  ```bash
  source openrc admin admin
  openstack token issue
  ```

- **Service Status**: Use `systemctl` or `ps aux | grep nova` to verify daemons are running.

### Lifecycle Management

| Action | Command | Description |
|--------|---------|-------------|
| Stop Services | `./unstack.sh` | Gracefully stops all OpenStack processes. |
| Clean Host | `./clean.sh` | Removes all services, databases, and configuration. |
| Update Code | `git pull` | Pulls latest changes; re-run `./stack.sh` to upgrade. |

## Extending DevStack

### Adding Plugins

DevStack's extensibility revolves around the `extras.d/` directory and the `enable_plugin` directive in `local.conf`. To add an external service (e.g., **Magnum**):

1. Add the plugin line to `local.conf`:

   ```ini
   enable_plugin magnum https://opendev.org/openstack/magnum
   ```

2. Optionally provide configuration in `local.conf`.
3. Re-run `./stack.sh`.

### Overriding Service Defaults

You can override service-specific configuration by placing a snippet in the `local.conf` section named after the service. For example, to change Nova's compute driver:

```ini
[[local|localrc]]
NOVA_COMPUTE_DRIVER=libvirt.LibvirtDriver
```

### Integration Testing

DevStack integrates **Tempest**, the official OpenStack integration test suite. To run baseline tests:

```bash
cd /opt/stack/tempest
tempest run --smoke
```

## Troubleshooting

### Common Failure Modes

| Symptom | Root Cause | Resolution |
|--------|------------|------------|
| `stack.sh` aborts early | Missing package or insufficient memory | Re-run `tools/install_prereqs.sh` or increase swap space. |
| `HTTP 401 Unauthorized` | Password mismatch or Keystone down | Verify `ADMIN_PASSWORD` and restart Keystone service. |
| Network creation failed | Missing OVS kernel module or bridge conflict | Load `openvswitch` module or delete stale bridges. |
| Horizon 502 Bad Gateway | Apache down or missing Python dependencies | Restart Apache or re-install Horizon virtual environment. |
| Image upload fails | Insufficient RAM or invalid image format | Raise swap size or verify image format with `qemu-img info`. |

## Running DevStack in Docker

DevStack can be built and started inside a Docker container, which provides isolation and repeatability. However, the container must run in **privileged mode** to manipulate kernel networking and the hypervisor.

### Docker Deployment Workflow

1. **Build the Image**:
   ```bash
   docker build -t devstack:latest .
   ```

2. **Run the Container**:

   ```bash
   docker run -d \
       --name devstack \
       --privileged \
       --network host \
       -e ADMIN_PASSWORD=MySecretPass \
       -e SERVICE_PASSWORD=MySecretPass \
       devstack:latest
   ```

### Accessing the Cloud

| Service | URL (if `HOST_IP=192.168.56.101`) | Default credentials |
|---------|------------------------------------|----------------------|
| Horizon dashboard | `http://192.168.56.101/` | `admin / <ADMIN_PASSWORD>` |
| Keystone API (public) | `http://192.168.56.101/v3` | `admin / <ADMIN_PASSWORD>` |
| Nova API | `http://192.168.56.101:8774/v2.1` | — |
| Neutron API | `http://192.168.56.101:9696` | — |

To use the CLI from the host, copy the `openrc` file:

```bash
docker cp devstack:/opt/devstack/openrc ./devstack-openrc
source ./devstack-openrc admin admin
openstack server list
```

### Docker Limitations and Gotchas

| Issue | Resolution |
|-------|------------|
| **Nested virtualization** | Enable nested virtualization on the host VM or use the `QEMU` driver. |
| **Port conflicts** | Change port mapping (e.g., `-p 8080:80`) or stop conflicting services. |
| **Persistent data** | Mount a host directory or Docker volume to `/opt/stack/data`. |
| **Resource consumption** | Ensure the Docker daemon has sufficient memory (>= 8 GB). |

## Summary Checklist

- [ ] DevStack repository cloned.
- [ ] `local.conf` configured with passwords and `HOST_IP`.
- [ ] `stack.sh` executed successfully.
- [ ] OpenStack CLI credentials sourced.
- [ ] Horizon dashboard accessible.

## Assignments

!!! note "Practical Exercises"
    **Goal**: Deploy a functional OpenStack environment and perform basic operations.

    **Tasks**:
    1. Deploy DevStack on a clean Ubuntu 22.04 host.
    2. Configure a custom `local.conf` with a strong `ADMIN_PASSWORD`.
    3. Launch a CirrOS instance using the CLI.
    4. Verify the instance is accessible via the Horizon dashboard.
    5. Use `unstack.sh` to stop the services and `clean.sh` to reset the host.

## References

- [Official DevStack Documentation](https://docs.openstack.org/devstack/latest/)
- [OpenStack Foundation](https://docs.openstack.org/en/latest/)
- [Ubuntu LTS Documentation](https://ubuntu.com/server/lts)

## Self-Assessment
Test your knowledge by expanding the questions below.
??? note "What is the primary purpose of DevStack?"
    DevStack is used for development and testing of OpenStack services, providing an automated way to deploy a complete cloud environment from source on a single machine.

??? note "What is the laocal.conf file and why is it important?"
    The `local.conf` file is the primary configuration point for DevStack; it allows users to define passwords, host IPs, and which services should be enabled or disabled.

??? note "What is the difference between `unstack.sh` and `clean.sh`?"
    S_unstack.sh_ stops the OpenStack services but keeps the configuration and databases, while _clean.sh_ removes all services, databases, and configuration files to return the host to a pristine state.
