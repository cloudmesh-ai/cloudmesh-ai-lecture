# Installing OpenClaw on OpenStack

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    * Provision a virtual machine on an OpenStack cloud using the CLI.
    * Configure OpenStack networking and security groups for AI service access.
    * Install and configure Docker and Docker Compose on an Ubuntu host.
    * Deploy the OpenClaw AI platform stack using Docker Compose.
    * Adapt the installation process for specific research clouds like Jetstream and Chameleon.

## Overview

OpenClaw is a low-code AI platform that can be deployed on any OpenStack cloud. This chapter walks you through a complete, production-ready installation of OpenClaw on an OpenStack environment. Two widely-used OpenStack-based research clouds—Jetstream and Chameleon—are covered in separate appendices so you can adapt the steps to those specific sites.

## Scope and Assumptions

| Item | Assumption |
|------|------------|
| **OpenStack version** | Queens or newer (Nova, Neutron, Keystone, Glance, Cinder, Heat). |
| **User privileges** | Cloud user with the *admin* role on a tenant/project that can create networks, subnets, security groups, floating IPs, and volumes. |
| **Compute resources** | At least one flavor with 4 vCPU, 8 GB RAM, and 40 GB root disk. |
| **Operating system** | Ubuntu 22.04 LTS (or any modern Ubuntu) for the VM that will host OpenClaw. |
| **Network** | Public (floating) IP allocation is possible, or a VPN tunnel to the OpenStack cloud is available. |
| **Software** | `openstack` CLI, `ssh`, `git`, `docker`, `docker-compose` installed on the local workstation. |

## Architecture Overview

```text
+-------------------+          +-------------------+          +-------------------+
|   OpenStack Cloud |   Nova   |   OpenClaw VM     |   Docker |   OpenClaw Services |
| (Controller Nodes)--------->| (Ubuntu 22.04)  |--------->| (postgres, minio, |
|                     |          |                   |          |  api, UI, etc.)    |
+-------------------+          +-------------------+          +-------------------+
        ^  ^                           ^  ^                           ^
        |  |                           |  |                           |
        |  +--- Neutron (private net)  |  +--- Docker-compose         |
        |                              +--- Security groups         |
        +--- External network (floating IP)                       |
                                                                    |
                              Users access via HTTPS (port 443)   |
```

Figure 1: OpenClaw deployment architecture on OpenStack.

The OpenClaw stack runs inside Docker containers on a single Ubuntu VM. The VM is provisioned through the standard OpenStack self-service API (Nova, Neutron, Cinder).

## Preparing the OpenStack Environment

### Install the OpenStack client

```bash
# On your workstation (Linux/macOS)
sudo apt-get update
sudo apt-get install -y python3-openstackclient
```

### Authenticate

Obtain the OpenStack RC file (`project-openrc.sh`) from the Horizon dashboard or from your cloud provider and source it:

```bash
source project-openrc.sh
```

Verify the authentication:

```bash
openstack token issue
```

You should see a token and details of the project you are using.

### Verify quotas

```bash
openstack quota show
```

Make sure you have enough quota for:

1. **Instances** – at least 1.
2. **Cores** – $\ge 4$.
3. **RAM** – $\ge 8192$ MiB.
4. **Floating IPs** – $\ge 1$.
5. **Volumes** – $\ge 1$ (for persistent data).

If needed, request quota increase from the cloud administrators.

## Provisioning the OpenClaw Host VM

Below is a reproducible series of OpenStack CLI commands. Adjust the names, flavors, and network IDs to match your cloud.

```bash
# 1. Create a dedicated private network
openstack network create openclaw-net

# 2. Create a subnet (use a CIDR that does not overlap existing networks)
openstack subnet create --network openclaw-net \
    --subnet-range 192.168.100.0/24 \
    --gateway 192.168.100.1 \
    openclaw-subnet

# 3. Create a security group allowing SSH, HTTP, HTTPS
openstack security group create openclaw-secgroup
openstack security group rule create --proto tcp --dst-port 22 openclaw-secgroup       # SSH
openstack security group rule create --proto tcp --dst-port 80 openclaw-secgroup       # HTTP (optional)
openstack security group rule create --proto tcp --dst-port 443 openclaw-secgroup      # HTTPS

# 4. Reserve a floating IP
FLOATING_IP=$(openstack floating ip create public-net -f value -c floating_ip_address)

# 5. Boot the VM
openstack server create \
    --flavor m1.large \
    --image ubuntu-22.04 \
    --network openclaw-net \
    --security-group openclaw-secgroup \
    --key-name my-keypair \
    openclaw-host
```

Wait for the server to become ACTIVE:

```bash
openstack server list -c Name -c Status
```

### Attach the floating IP

```bash
SERVER_ID=$(openstack server list --name openclaw-host -f value -c ID)
openstack server add floating ip $SERVER_ID $FLOATING_IP
```

You can now SSH into the host:

```bash
ssh -i ~/.ssh/my-keypair ubuntu@$FLOATING_IP
```

## Installing Docker and Docker-Compose on the VM

```bash
# Update the package index
sudo apt-get update

# Install Docker Engine
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker packages
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker version
docker compose version

# Add the ubuntu user to the docker group (so sudo is not needed)
sudo usermod -aG docker $USER
newgrp docker
```

## Deploying the OpenClaw Stack

OpenClaw provides an official `docker-compose.yml` that defines all required services (PostgreSQL, MinIO, Redis, the FastAPI services, Nginx, and optional monitoring).

### Clone the OpenClaw repository

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
```

### Create a .env file

```bash
cat > .env <<EOF
# Database
POSTGRES_USER=openclaw
POSTGRES_PASSWORD=$(openssl rand -hex 16)
POSTGRES_DB=openclaw

# MinIO (object storage)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=$(openssl rand -hex 16)

# JWT secret for the auth service
SECRET_KEY=$(openssl rand -hex 32)

# Optional: API rate limits, external storage endpoints, etc.
EOF
```

### Build and start the stack

```bash
docker compose up -d
```

Docker Compose will pull the required images, create persistent volumes, and start all containers. The startup time is typically 2-3 minutes.

### Verify the deployment

```bash
docker compose ps
```

You should see services such as `postgres`, `minio`, `auth`, `dataset`, `inference`, and `nginx` in the **Up** state.

Open a web browser and navigate to `http://<FLOATING_IP>` (or `https://<FLOATING_IP>` if you later configure TLS). The OpenClaw UI should appear, and you can register an admin account.

## Optional: Enabling TLS

For production use you should terminate TLS at the Nginx reverse proxy.

1. **Obtain a certificate** (e.g., from Let's Encrypt using Certbot on the VM, or upload a commercial certificate).
2. **Place the certificate files** in `/home/ubuntu/openclaw/certs/` (e.g., `fullchain.pem` and `privkey.pem`).
3. **Replace the Nginx config** (provided in `nginx/conf.d/openclaw.conf`) with a TLS-enabled version that points to these files.
4. **Restart Nginx**:

```bash
docker compose restart nginx
```

After this, access the UI via `https://<FLOATING_IP>`.

## Summary Checklist

| Item | Verification |
|------|--------------|
| **OpenClaw UI reachable** | Load `https://<FLOATING_IP>` in a browser; the login page appears. |
| **Database persistence** | Create a project, stop the stack (`docker compose down`), start again, and verify the project still exists. |
| **Object storage** | Upload a small dataset through the UI; confirm the file appears in MinIO (`http://<FLOATING_IP>:9001`). |
| **API access** | From a remote workstation, run: `curl -X GET http://<FLOATING_IP>/api/health` (or the appropriate health endpoint). |
| **Security groups** | Verify that only ports 22 (SSH) and 443 (HTTPS) are open to the world. |
| **Monitoring (optional)** | If you enabled Prometheus/Grafana, check that metrics are being collected. |
| **Backup strategy** | Create snapshots of the Cinder volume(s) used for the Docker volumes, or schedule regular `docker volume export` backups. |

## Appendix A: Installing OpenClaw on Jetstream

Jetstream2 is an OpenStack-based cloud operated by the NSF XSEDE program. The steps below are identical to the generic OpenStack installation, with a few Jetstream-specific details.

### Obtain Jetstream credentials

1. Log in to the Jetstream2 portal: `https://jetstream2.nimbul.utah.edu/`
2. From **My Projects**, download the *OpenStack RC file* for your project (e.g., `jetstream2-openrc.sh`).
3. Source the file on your workstation:

```bash
source jetstream2-openrc.sh
```

### Select a flavor

Jetstream provides the following convenient flavors for container workloads:

| Flavor | vCPU | RAM (GiB) | Disk (GB) |
|--------|------|-----------|-----------|
| `jetstream2.large` | 4 | 8 | 80 |
| `jetstream2.xlarge`| 8 | 16| 160 |

Use the larger flavor if you anticipate heavy model training.

### Create a public network (floating IP pool)

Jetstream ships with a pre-configured external network called `public`. Use it directly:

```bash
FLOATING_IP=$(openstack floating ip create public -f value -c floating_ip_address)
```

All remaining steps (network, security group, VM boot, Docker install, OpenClaw deployment) are identical to the main sections.

**Tip:** Jetstream's default security group `default` already allows inbound SSH (22) and outbound traffic. You may only need to add a rule for HTTPS (443):

```bash
openstack security group rule create --proto tcp --dst-port 443 default
```

### Persistent storage

Jetstream provides Cinder volume types `ssd` and `magnetic`. Create an SSD volume for better I/O performance:

```bash
openstack volume create --size 100 --type ssd openclaw-data
openstack server add volume openclaw-host openclaw-data
```

Mount the volume inside the VM (`/dev/vdb`) and bind Docker volumes to it for PostgreSQL and MinIO data.

```bash
sudo mkfs.ext4 /dev/vdb
sudo mkdir /mnt/openclaw-data
sudo mount /dev/vdb /mnt/openclaw-data
# Add to /etc/fstab for persistence
echo '/dev/vdb /mnt/openclaw-data ext4 defaults 0 2' | sudo tee -a /etc/fstab
# Adjust docker-compose.yml volume paths to /mnt/openclaw-data/*
```

### Example one-liner to start OpenClaw on Jetstream

```bash
ssh -i ~/.ssh/jetstream-key ubuntu@$FLOATING_IP "\
  sudo apt-get update && \
  sudo apt-get install -y docker-compose git && \
  git clone https://github.com/openclaw/openclaw.git && \
  cd openclaw && \
  cp .env.example .env && \
  docker compose up -d"
```

After the command finishes, the OpenClaw UI will be reachable at `https://$FLOATING_IP`.

## Appendix B: Installing OpenClaw on Chameleon

Chameleon Cloud is another NSF-funded OpenStack testbed. The installation flow matches the generic OpenStack path, with a few Chameleon-specific nuances.

### Access the Chameleon Horizon dashboard

* URL: `https://dashboard.chameleoncloud.org/`
* After logging in with your XSEDE credentials, navigate to **Project $\rightarrow$ OpenStack RC File** and download `chameleon-openrc.sh`.

```bash
source chameleon-openrc.sh
```

### Choose a flavor

Chameleon offers high-performance flavors for GPU work. For a CPU-only OpenClaw installation, the `m1.medium` flavor (4 vCPU, 8 GiB RAM) is sufficient.

```bash
openstack flavor list
# Example: use m1.medium
```

### Create a private network and allocate a floating IP

```bash
# Private network
openstack network create openclaw-net
openstack subnet create --network openclaw-net \
    --subnet-range 10.0.0.0/24 \
    openclaw-subnet

# Security group (allow SSH and HTTPS)
openstack security group create openclaw-secgroup
openstack security group rule create --proto tcp --dst-port 22 openclaw-secgroup
openstack security group rule create --proto tcp --dst-port 443 openclaw-secgroup

# Floating IP from the public external network (named 'public')
FLOATING_IP=$(openstack floating ip create public -f value -c floating_ip_address)
```

### Boot the VM

```bash
openstack server create \
    --flavor m1.medium \
    --image ubuntu-22.04 \
    --network openclaw-net \
    --security-group openclaw-secgroup \
    --key-name my-chameleon-key \
    openclaw-host

# Attach the floating IP
SERVER_ID=$(openstack server list --name openclaw-host -f value -c ID)
openstack server add floating ip $SERVER_ID $FLOATING_IP
```

### Optional: Use a shared file system

Chameleon provides a **shared filesystem (CephFS)** that can be mounted on multiple instances. If you plan to run a high-availability OpenClaw deployment across several nodes, mount CephFS and store Docker volumes there.

```bash
# Install Ceph client utilities
sudo apt-get install -y ceph-fuse

# Mount CephFS (example values; replace with your project's FS ID)
sudo mkdir /mnt/cephfs
sudo ceph-fuse -n client.admin -k /etc/ceph/ceph.client.admin.keyring \
    -r / cephfs:/ /mnt/cephfs
```

Then point Docker volume mounts to `/mnt/cephfs/openclaw/*`.

### Deploy OpenClaw

The remaining steps (Docker installation, cloning the repository, creating `.env`, `docker compose up -d`) are identical to the main sections.

**Note:** Chameleon's default security group may block inbound traffic on port 443. Verify that your security group rule has been applied:

```bash
openstack security group rule list openclaw-secgroup
```

### Verify

```bash
curl -k https://$FLOATING_IP   # -k skips cert verification if you use a self-signed cert
```

You should see the OpenClaw landing page HTML.

## Troubleshooting Guide

| Symptom | Likely Cause | Remedy |
|---------|--------------|--------|
| SSH connection timed out | Security group missing port 22 or floating IP not associated | Add rule `openstack security group rule create --proto tcp --dst-port 22 <sg>` and verify floating IP attachment. |
| HTTP(S) returns 502 Bad Gateway | Nginx cannot reach the backend containers (Docker network failed) | Run `docker compose ps`; restart the stack (`docker compose down && docker compose up -d`). |
| Database connection error | Incorrect `POSTGRES_PASSWORD` in `.env` or volume permissions | Re-export the password, ensure PostgreSQL container has read/write access to its volume (`chmod 700` on the host directory). |
| MinIO UI not reachable on port 9001 | Security group blocks port 9001 (optional) | Add rule for port 9001 or use SSH tunneling (`ssh -L 9001:localhost:9001 ubuntu@$FLOATING_IP`). |
| High latency on API calls | VM flavor insufficient (CPU throttling) | Upgrade to a larger flavor (more vCPU/RAM) or enable hardware-accelerated instances (GPU). |
| Certificate errors after enabling TLS | Nginx config still points to missing cert files | Verify that `fullchain.pem` and `privkey.pem` exist in the mounted `certs/` directory and reload Nginx. |

## Assignments

!!! note "Assignment.1: Deployment of OpenClaw" 
    Deploy a basic OpenClaw instance on your assigned OpenStack project.

??? tip "Solution: Deployment of OpenClaw"
    The deployment is successful when you can SSH into the VM and access the OpenClaw UI via the floating IP. Follow the steps in Section 5 (Provisioning) and Section 7 (Deploying the OpenClaw Stack).

!!! note "Assignment.2: Set Security Groups"
    Configure a custom security group that restricts HTTPS access to only your workstation's IP address.

??? tip "Solution: Set Security Groups"
    Use the command: `openstack security group rule create --proto tcp --dst-port 443 --remote-ip <YOUR_WORKSTATION_IP>/32 openclaw-secgroup`. This restricts access to a specific IP rather than allowing all traffic (0.0.0.0/0).

!!! note "Assignment.3: Volumes"
    Install a persistent SSD volume and migrate the PostgreSQL data directory to that volume.

??? tip "Solution: Volumes"
    1. Create the volume: `openstack volume create --size 100 --type ssd openclaw-data`.
    2. Attach it: `openstack server add volume openclaw-host openclaw-data`.
    3. Format and mount it at `/mnt/openclaw-data` and add it to `/etc/fstab`.
    4. Update `docker-compose.yml` to map the postgres volume to `/mnt/openclaw-data/postgres`.


## References

* OpenClaw GitHub repository – <https://github.com/openclaw/openclaw>
* OpenStack command-line client documentation – <https://docs.openstack.org/python-openstackclient/latest/>
* Jetstream2 user guide – <https://jetstream2.nimbul.utah.edu/docs>
* Chameleon Cloud documentation – <https://www.chameleoncloud.org/docs/>

## Self-Assessment
Test your knowledge by expanding the questions below.
??? note "What is the purpose of the floating IP in the OpenStack deployment?"
    The floating IP provides a public-facing IP address that allows users to access the OpenClaw UI and API from the external internet, as the VM's internal IP is only reachable within the private network.

??? note "How does Docker Compose simplify the deployment of OpenClaw?"
    Docker Compose allows for the definition of multiple interconnected services (database, storage, API, UI) in a single YAML file, ensuring that they are started in the correct order and share a common network.

??? note "What is the critical step when moving data volumes to an external SSD volume on Jetstream?"
    The external volume must be formatted (e.g., `mkfs.ext4`), mounted to a directory (e.g., `/mnt/openclaw-data`), and added to `/etc/fstab` for persistence across reboots, before updating the `docker-compose.yml` volume mappings.
