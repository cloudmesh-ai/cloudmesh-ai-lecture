# Appendix – Ready‑to‑Copy Scripts

!!! info "Learning Objectives"
    By the end of this appendix, you will be able to:
    1. **Automate** the creation of OpenStack keypairs and security groups using bash scripts.
    2. **Implement** network isolation for multi-tier architectures using automated security group rules.
    3. **Deploy** complex multi-VM clusters (scheduler and workers) through scripted provisioning.
    4. **Develop** Python scripts to programmatically audit and summarize cloud resource states.
    5. **Apply** security best practices for managing sensitive cloud credentials and SSH keys.

!!! Note
    If things do not work its your responsibility to fix it here in GitHub.

## High-Level Design

The scripts in this appendix provide a comprehensive toolkit for automating the deployment of a multi-tier cloud architecture on OpenStack (Jetstream). The design follows a phased approach to ensure security, scalability, and maintainability:

1.  **Identity & Access Management**: Establishing trust via SSH keypairs to ensure secure, password‑less access to all virtual machines.
2.  **Network Security Architecture**: Implementing a tiered security model (Public Web $\rightarrow$ Private DB $\rightarrow$ Internal Cluster) using Security Groups to enforce strict isolation.
3.  **Compute Provisioning**: Automating the launch of diverse VM roles (Web, DB, Scheduler, Workers) with appropriate flavors and images to match specific workload needs.
4.  **Cluster Orchestration**: Setting up intra‑cluster communication for distributed workloads (e.g., Dask) and refining security rules to follow the principle of least privilege.
5.  **Infrastructure Auditing**: Using Python to programmatically verify the state of the deployed environment and generate reports for documentation and audit.

The following files can be saved directly into your project directory (or pasted into a terminal).  
All scripts are plain‑text **bash** unless otherwise noted.  
Feel free to adjust instance flavors, image names, or network names to match your own Jetstream environment.


### A1. `01‑keypair.sh` – Create a reusable SSH key‑pair  

**What this script does:**
This script automates the upload of your local public SSH key to the OpenStack cloud. By creating a named keypair (`jetstream-demo`), it ensures that any VM launched with this keypair will automatically have your public key in its `authorized_keys` file.

**Why this matters:**
Managing SSH keys through the cloud provider instead of manually copying keys to every VM reduces administrative overhead and ensures a consistent, secure access method across your entire infrastructure.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 01‑keypair.sh
# -------------------------------------------------
# Creates an OpenStack keypair named jetstream-demo
# using the public key from ~/.ssh/id_rsa.pub
# -------------------------------------------------

NAME="jetstream-demo"
PUBKEY="${HOME}/.ssh/id_rsa.pub"

if openstack keypair list -c Name -f value | grep -q "^${NAME}$"; then
    echo "Keypair ${NAME} already exists – skipping creation."
else
    openstack keypair create "${NAME}" --public-key "${PUBKEY}"
    echo "Keypair ${NAME} created."
fi
```

---  

### A2. `02‑security-groups.sh` – Build the three security groups used in the lab  

**What this script does:**
This script defines the "virtual firewalls" for your environment. It creates three distinct security groups to implement network isolation:
- `web-sg`: Permits public HTTP/HTTPS and SSH traffic from any IP address.
- `db-sg`: Restricts access so that only the web tier (`web-sg`) can communicate with the database on SSH and MySQL ports.
- `cluster-sg`: Initially allows broad communication between cluster members to simplify the setup of distributed services.

**Why this matters:**
Implementing security groups is the primary way to achieve "Defense in Depth." By restricting database access to only the web tier, you ensure that even if a database password is leaked, the database cannot be accessed directly from the public internet.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 02‑security-groups.sh
# -------------------------------------------------
# web‑sg  : public web tier (SSH, HTTP, HTTPS)
# db‑sg   : private database tier (SSH & MySQL from web‑sg)
# cluster‑sg : scheduler ↔ workers intra‑group traffic
# -------------------------------------------------

# ---- web‑sg -------------------------------------------------
if ! openstack security group list -c Name -f value | grep -q "^web-sg$"; then
    openstack security group create web-sg --description "Web tier (public)"
    openstack security group rule create --proto tcp --dst-port 22  --remote-ip 0.0.0.0/0 web-sg
    openstack security group rule create --proto tcp --dst-port 80  --remote-ip 0.0.0.0/0 web-sg
    openstack security group rule create --proto tcp --dst-port 443 --remote-ip 0.0.0.0/0 web-sg
    echo "Security group web-sg created."
fi

# ---- db‑sg --------------------------------------------------
if ! openstack security group list -c Name -f value | grep -q "^db-sg$"; then
    openstack security group create db-sg --description "DB tier (private)"
    openstack security group rule create --proto tcp --dst-port 22  --remote-group web-sg db-sg
    openstack security group rule create --proto tcp --dst-port 3306 --remote-group web-sg db-sg
    echo "Security group db-sg created."
fi

# ---- cluster‑sg ---------------------------------------------
if ! openstack security group list -c Name -f value | grep -q "^cluster-sg$"; then
    openstack security group create cluster-sg --description "Scheduler + workers"
    # SSH from anywhere (for the scheduler which receives a floating IP)
    openstack security group rule create --proto tcp --dst-port 22 --remote-ip 0.0.0.0/0 cluster-sg
    # Allow any intra‑group traffic while we build the cluster (will be tightened later)
    openstack security group rule create --proto tcp --dst-port 0-65535 --remote-group cluster-sg cluster-sg
    echo "Security group cluster-sg created."
fi
```

---  

### A3. `03‑web‑db‑instances.sh` – Spin up the 2‑tier web ↔ DB VMs  

**What this script does:**
This script deploys a classic two-tier architecture. It launches a web server and a database server, assigning them the security groups created in the previous step. It also allocates a Floating IP to the web server, making it reachable from the public internet while keeping the database server strictly private.

**Why this matters:**
This pattern separates the "presentation layer" (web) from the "data layer" (DB). It allows you to scale the web tier independently and ensures that sensitive data is never exposed to the public internet.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 03‑web‑db‑instances.sh
# -------------------------------------------------
# Requires: keypair jetstream-demo, security groups web-sg & db-sg
# -------------------------------------------------

# Configuration
FLAVOR="m1.medium"
IMAGE="ubuntu-22.04"
NETWORK="private-net"
KEYPAIR="jetstream-demo"

# ---- Web server (public) ------------------------------------
if ! openstack server list -c Name -f value | grep -q "^web01$"; then
    openstack server create \
        --flavor "${FLAVOR}" \
        --image "${IMAGE}" \
        --key-name "${KEYPAIR}" \
        --security-group web-sg \
        --network "${NETWORK}" \
        web01
    echo "Web VM (web01) launched."
else
    echo "Web VM already exists – skipping."
fi

# ---- DB server (private) ------------------------------------
if ! openstack server list -c Name -f value | grep -q "^db01$"; then
    openstack server create \
        --flavor "${FLAVOR}" \
        --image "${IMAGE}" \
        --key-name "${KEYPAIR}" \
        --security-group db-sg \
        --network "${NETWORK}" \
        db01
    echo "DB VM (db01) launched."
else
    echo "DB VM already exists – skipping."
fi

# ---- Allocate a floating IP for the web tier -----------------
FIP=$(openstack floating ip list -c "Floating IP Address" -f value | head -n1)
if [ -z "$FIP" ]; then
    FIP=$(openstack floating ip create public --format value -c floating_ip_address)
    openstack server add floating ip web01 "$FIP"
    echo "Floating IP $FIP attached to web01."
else
    echo "A floating IP already exists: $FIP"
fi

echo "Web server reachable at http://$FIP"
```

---  

### A4. `04‑scheduler‑workers.sh` – Build the AI/Data cluster  

**What this script does:**
This script provisions a distributed computing cluster consisting of one scheduler and two worker nodes. The scheduler is given a Floating IP for external management, while the workers remain on the private network. All nodes are placed in the `cluster-sg` to enable them to communicate with each other.

**Why this matters:**
Distributed computing is essential for AI and Big Data tasks. This architecture allows you to centralize job management (scheduler) while distributing the actual computation across multiple worker nodes to increase processing speed and memory capacity.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 04‑scheduler‑workers.sh
# -------------------------------------------------
# Builds one scheduler (public) and two workers (private)
# -------------------------------------------------

FLAVOR="m1.large"
IMAGE="ubuntu-22.04"
NETWORK="private-net"
KEYPAIR="jetstream-demo"

# ---- Scheduler (public) ------------------------------------
if ! openstack server list -c Name -f value | grep -q "^scheduler$"; then
    openstack server create \
        --flavor "${FLAVOR}" \
        --image "${IMAGE}" \
        --key-name "${KEYPAIR}" \
        --security-group cluster-sg \
        --network "${NETWORK}" \
        scheduler
    echo "Scheduler VM created."
else
    echo "Scheduler already exists – skipping."
fi

# ---- Workers (private) --------------------------------------
for i in 1 2; do
    NAME="worker${i}"
    if ! openstack server list -c Name -f value | grep -q "^${NAME}$"; then
        openstack server create \
            --flavor "${FLAVOR}" \
            --image "${IMAGE}" \
            --key-name "${KEYPAIR}" \
            --security-group cluster-sg \
            --network "${NETWORK}" \
            "${NAME}"
        echo "Worker VM ${NAME} created."
    else
        echo "Worker ${NAME} already exists – skipping."
    fi
done

# ---- Floating IP for the scheduler -------------------------
FIP=$(openstack floating ip list -c "Floating IP Address" -f value | head -n1)
if [ -z "$FIP" ]; then
    FIP=$(openstack floating ip create public --format value -c floating_ip_address)
    openstack server add floating ip scheduler "$FIP"
    echo "Floating IP $FIP attached to scheduler."
else
    echo "A floating IP already exists: $FIP"
fi

echo "Scheduler reachable at $FIP"
```

---  

### A5. `05‑ssh‑setup.sh` – Password‑less SSH from scheduler $\rightarrow$ workers  

**What this script does:**
To enable the scheduler to manage workers without manual password entry, this script generates a dedicated intra‑cluster SSH key on your local machine and distributes the public part to all worker nodes.

**Why this matters:**
Automated orchestration requires non-interactive communication. By setting up a dedicated cluster key, you enable the scheduler to launch processes on workers securely and programmatically, which is a prerequisite for distributed frameworks like Dask or Kubernetes.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 05‑ssh‑setup.sh
# -------------------------------------------------
# Run this **on your local workstation**, not inside any VM.
# It copies a newly generated intra‑cluster key to the workers.
# -------------------------------------------------

# 1) Generate a dedicated key (if it does not already exist)
CLUSTER_KEY="${HOME}/.ssh/id_cluster"
if [ ! -f "${CLUSTER_KEY}" ]; then
    ssh-keygen -t rsa -b 4096 -N "" -f "${CLUSTER_KEY}"
    echo "Cluster key generated at ${CLUSTER_KEY}"
fi

# 2) Pull the private IP addresses of the workers
WORKERS=$(openstack server list -c Name -c Networks -f value | grep "^worker" | awk '{print $2}' | cut -d'=' -f2)

# 3) Copy the public key to each worker
for IP in ${WORKERS}; do
    echo "Copying key to worker ${IP} ..."
    ssh-copy-id -i "${CLUSTER_KEY}.pub" -o StrictHostKeyChecking=no ubuntu@"${IP}"
done

echo "Password‑less SSH setup complete."
```

---  

### A6. `06‑run‑dask.sh` – Start the scheduler and workers  

**What this script does:**
This script orchestrates the launch of a Dask cluster. It uses SSH to remotely execute commands on the scheduler (installing Dask and starting the scheduler process) and then loops through the workers to start the `dask-worker` processes, pointing them to the scheduler's private IP.

**Why this matters:**
Manual installation of software on multiple VMs is error-prone. Scripting the installation and launch sequence ensures that all nodes are running compatible versions of the software and are correctly linked to the central scheduler.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 06‑run‑dask.sh
# -------------------------------------------------
# 1) SSH to the scheduler, install Dask, and launch the scheduler.
# 2) From the scheduler (or from your laptop), start the workers.
# -------------------------------------------------
# ----- 1) Scheduler side -------------------------------------------------
SCHED_FIP=$(openstack floating ip list -c "Floating IP Address" -f value | head -n1)

ssh -i ~/.ssh/id_rsa ubuntu@"${SCHED_FIP}" <<'EOSSH'
    sudo apt update && sudo apt install -y python3-pip
    pip3 install --user dask[distributed]

    # Launch Dask scheduler in the background (port 8786, dashboard on 8787)
    dask-scheduler --port 8786 --dashboard-address :8787 &
    echo "Dask scheduler started."
EOSSH

# ----- 2) Workers side ---------------------------------------------------
# Get private IP of scheduler (needed for workers to connect)
SCHED_PRIV=$(openstack server list -c Name -c Networks -f value | grep "^scheduler " | awk '{print $2}' | cut -d'=' -f2)

for i in 1 2; do
    WORKER_IP=$(openstack server show -c addresses -f value worker${i} | cut -d'=' -f2)
    echo "Starting Dask worker on ${WORKER_IP} ..."
    ssh -i ~/.ssh/id_rsa ubuntu@"${WORKER_IP}" \
        "dask-worker tcp://${SCHED_PRIV}:8786 &"
done

echo "All workers launched. You can now connect from your laptop:"
echo "   pip install dask[distributed]"
echo "   from dask.distributed import Client"
echo "   client = Client('tcp://${SCHED_PRIV}:8786')"
```

---  

### A7. `07‑tighten‑security.sh` – Apply the asymmetric security‑group rules  

**What this script does:**
After the cluster is running, this script removes the broad, permissive "all ports" rule created during the setup of `cluster-sg` and replaces it with a narrow rule that only allows traffic on port 8786 (the Dask scheduler port).

**Why this matters:**
This represents the transition from "Development" to "Production" security. By closing unnecessary ports, you minimize the attack surface of your cluster, preventing potential attackers from exploiting other services that might be running on your VMs.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 07‑tighten‑security.sh
# -------------------------------------------------
# Removes the permissive intra‑group rule and adds a
# rule that only permits workers → scheduler on port 8786.
# -------------------------------------------------

# 1) List the permissive rule (port range 0‑65535) and delete it
RULE_ID=$(openstack security group rule list cluster-sg -c ID -c "Port Range" -f value | grep "0:65535" | awk '{print $1}')
if [ -n "$RULE_ID" ]; then
    openstack security group rule delete "$RULE_ID"
    echo "Removed permissive intra‑group rule ($RULE_ID)."
else
    echo "No permissive rule found – nothing to delete."
fi

# 2) Add a narrow rule for Dask scheduler port (8786)
openstack security group rule create \
    --protocol tcp --dst-port 8786 \
    --remote-group cluster-sg \
    --description "Workers → Scheduler (Dask)" \
    cluster-sg

echo "Added tight rule allowing only port 8786 from workers to scheduler."
```

---  

### A8. `08‑custom‑network.sh` – Build a user‑defined private network  

**What this script does:**
This script demonstrates how to create a completely custom Virtual Private Cloud (VPC). It defines a new network, a specific subnet with a custom CIDR range, and a router to manage traffic between the custom network and the external public network.

**Why this matters:**
In enterprise environments, you often cannot rely on default networks. Creating custom networks allows you to design your own IP addressing scheme, implement complex routing, and ensure total isolation from other projects in the same cloud tenant.

```bash
#!/usr/bin/env bash
# -------------------------------------------------
# 08‑custom‑network.sh
# -------------------------------------------------
# Creates a private network, subnet, router, and attaches
# the subnet to the external (public) network.
# -------------------------------------------------

NET_NAME="custom-net"
SUBNET_NAME="custom-subnet"
ROUTER_NAME="custom-router"
CIDR="192.168.100.0/24"
GW="192.168.100.1"

# Create network
if ! openstack network list -c Name -f value | grep -q "^${NET_NAME}$"; then
    openstack network create "${NET_NAME}"
    echo "Network ${NET_NAME} created."
fi

# Create subnet
if ! openstack subnet list -c Name -f value | grep -q "^${SUBNET_NAME}$"; then
    openstack subnet create \
        --network "${NET_NAME}" \
        --subnet-range "${CIDR}" \
        --gateway "${GW}" \
        "${SUBNET_NAME}"
    echo "Subnet ${SUBNET_NAME} created."
fi

# Create router
if ! openstack router list -c Name -f value | grep -q "^${ROUTER_NAME}$"; then
    openstack router create "${ROUTER_NAME}"
    echo "Router ${ROUTER_NAME} created."
fi

# Attach router to external network
openstack router set router ${ROUTER_NAME} --external-gateway public

# Add interface to the custom subnet
openstack router add subnet ${ROUTER_NAME} ${SUBNET_NAME}
echo "Router ${ROUTER_NAME} configured with external gateway and interface to ${SUBNET_NAME}."
```

---  

### A9. `summary-table.py` – Audit and summarize cloud resources  

**What this script does:**
This is a Python utility that uses the OpenStack CLI to retrieve a JSON list of all servers in the current project, parses the network information to isolate private IP addresses, and outputs a clean Markdown table.

**Why this matters:**
As your infrastructure grows, manually tracking IP addresses in a text file becomes impossible. Programmatic auditing ensures that your documentation is always in sync with the actual state of the cloud, providing a "single source of truth" for your cluster's topology.

```bash
$ chmod +x summary-table.py
$ ./summary-table.py        # or: python3 summary-table.py
```

```python
import json
import subprocess
import sys
from typing import List, Dict


def run_openstack_cmd() -> List[Dict]:
    """Execute the OpenStack CLI and return parsed JSON."""
    try:
        result = subprocess.run(
            ["openstack", "server", "list", "-f", "json"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        sys.stderr.write("Error: the `openstack` command is not installed.\n")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"OpenStack CLI failed: {e.stderr}\n")
        sys.exit(1)

    try:
        servers = json.loads(result.stdout)
    except json.JSONDecodeError:
        sys.stderr.write("Error: failed to parse JSON output from OpenStack.\n")
        sys.exit(1)

    return servers


def extract_private_ip(networks: str) -> str:
    """
    ``networks`` is a string like
    "private-net=10.0.0.5; public=203.0.113.10".
    We return only the private IP(s) (comma‑separated if more than one).
    """
    ips = []
    for pair in networks.split(";"):
        name, ip = pair.strip().split("=")
        if name.startswith("private"):
            ips.append(ip)
    return ", ".join(ips) if ips else "—"


def print_markdown_table(servers: List[Dict]):
    """Print a markdown table with the selected columns."""
    header = ["Name", "Status", "Image", "Private IP(s)"]
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")

    for srv in servers:
        name = srv.get("Name", "—")
        status = srv.get("Status", "—")
        image = srv.get("Image", "—")
        networks = srv.get("Networks", "")
        private_ips = extract_private_ip(networks)

        row = [name, status, image, private_ips]
        print("| " + " | ".join(row) + " |")


def main():
    servers = run_openstack_cmd()
    if not servers:
        print("No instances found in the current project.")
        return

    print_markdown_table(servers)


if __name__ == "__main__":
    main()
```

## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the purpose of the `01-keypair.sh` script?"
    It creates a reusable OpenStack keypair named `jetstream-demo` using a local public key, ensuring that you can SSH into your VMs.

??? question "In `02-security-groups.sh`, what is the difference between `web-sg` and `db-sg` in terms of access?"
    `web-sg` allows public traffic (SSH, HTTP, HTTPS) from anywhere (`0.0.0.0/0`), while `db-sg` only allows SSH and MySQL traffic originating from the `web-sg` group.

??? question "What does the `summary-table.py` script do?"
    It queries the OpenStack API for a list of servers and prints a formatted markdown table containing the Name, Status, Image, and Private IPs of the instances.

??? question "How do you run the `summary-table.py` script to generate a markdown table of your instances?"
    After making it executable (`chmod +x summary-table.py`), run it as `./summary-table.py`.

??? question "Why is it important to use `chmod 600` on the keypair or RC files?"
    To ensure that sensitive credentials and private keys are only readable by the owner, preventing other users on the system from accessing them.
