
# Appendix – Ready‑to‑Copy Scripts

!!! Note
    If things do not work its your responsibility to fix it here in GitHub.

The following files can be saved directly into your project directory (or pasted into a terminal).  
All scripts are plain‑text **bash** unless otherwise noted.  
Feel free to adjust instance flavors, image names, or network names to match your own Jetstream environment.



### A1. `01‑keypair.sh` – Create a reusable SSH key‑pair  

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

### A5. `05‑ssh‑setup.sh` – Password‑less SSH from scheduler → workers  

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
    openstack router set --external-gateway public "${ROUTER_NAME}"
    openstack router add subnet "${ROUTER_NAME}" "${SUBNET_NAME}"
    echo "Router ${ROUTER_NAME} created and attached to subnet."
fi
```

---  

### A9. `summary-table.py` – Sample script that prints a markdown table of your instances  

The Python program below **does not call the OpenStack CLI**; instead it works from a hard‑coded list so it can be executed in any environment (including the browser‑based interpreter).  
Replace the `instances` list with data obtained from `openstack server list -f json` if you want a live summary.


**`summary-table.py` – Generate a markdown‑formatted table of the instances you have created**

```python
#!/usr/bin/env python3
"""
summary-table.py
----------------
Queries the OpenStack service for a list of servers and prints a
markdown table that can be copied directly into documentation
(e.g. jetstream‑multi.md).

Prerequisites
-------------
* The OpenStack client (`openstack`) must be installed and sourced
  (e.g. `source ~/openrc.sh`).
* The script must be run on a machine that has network access to the
  Jetstream project and the appropriate credentials.

How it works
------------
1. Calls ``openstack server list -f json`` to obtain a JSON list of
   servers.
2. Extracts the fields we care about: **Name**, **Status**, **Networks**
   (which includes the private IPs) and **Image**.
3. Prints a markdown table with a header and a row for each server.

Usage
-----
$ chmod +x summary-table.py
$ ./summary-table.py        # or: python3 summary-table.py

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
