
# Containers on Jetstream2

This document is a hands on tutorial on how to use Docker or Kubernetes on Jetstream 2   

Jetstream 2 is an NSF‑funded research cloud that runs **OpenStack** (Newton → Ussuri).  It gives you the same IaaS primitives you’d find on any OpenStack cloud, plus the **Magnum** service for managed Kubernetes clusters and the **Zun** service for “Docker‑as‑a‑service”.  

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this tutorial, participants will be able to:

    1. **Provision** a basic VM on Jetstream 2 and install a container runtime using cloud-init.
    2. **Deploy** a managed Kubernetes cluster using OpenStack Magnum on Jetstream 2.
    3. **Launch** and manage standalone containers using OpenStack Zun on Jetstream 2.
    4. **Compare** and contrast the three container deployment methods on a research cloud.

!!! info "Target audience"
    Researchers, students, or DevOps engineers who already have a Jetstream 2 account (or are about to get one) and want to work with containers. No deep OpenStack expertise is required – the tutorial walks you through the CLI commands and the minimal cloud-init needed.


Below is a **step‑by‑step, end‑to‑end tutorial** that shows you how to:

| Section | What you’ll accomplish |
|---------|------------------------|
| **0 Prereqs** | Get your Jetstream 2 credentials, install the OpenStack client, and set up a local SSH key. |
| **1 Spin a plain VM and run Docker** | Launch a VM, install Docker via cloud‑init, and run a simple container (nginx). |
| **2 Deploy a managed Kubernetes cluster with Magnum** | Create a K8s cluster, get the kube‑config, and launch a sample web app. |
| **3 Run a container directly with Zun** | Use the Zun API (Docker‑compatible) to launch a container without a full cluster. |
| **4 Clean‑up** | Tear everything down safely. |
| **5 Extras** | Quick scripts, troubleshooting tips, and a small Python helper that prints Jetstream 2 flavor information in a nice table. |


---

## 0 Prerequisites  

!!! Assignment clouds.yaml
    instead of the rc file document  how to get the clouds.yaml file. Also locate the bug to get the rc file in the outline and replace it with where you realy find it.


| Item | Where to get it / how to install |
|------|-----------------------------------|
| **Jetstream 2 OpenStack RC file** (`jetstream-2-openrc.sh`) | Log in to the Jetstream portal → *Project* → *Access & Security* → **Download OpenStack RC File** (choose the project you’ll work in). |
| **OpenStack CLI (`python-openstackclient`)** |  ```pip install --user python-openstackclient``` (or install via your distro’s package manager). |
| **SSH key pair** | ```ssh-keygen -t rsa -b 4096 -f ~/.ssh/jetstream2_rsa``` (no passphrase is fine for demo). |
| **`jq`** (optional, for parsing JSON) |  ```sudo apt-get install -y jq``` # Debian/Ubuntu<br> ```sudo yum install -y jq```  # CentOS/RHEL\n |
| **`kubectl`** (for the Magnum part) | ```curl -LO \"https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl\"```</br>```chmod +x kubectl && sudo mv kubectl /usr/local/bin/``` |
| **`docker` CLI** (only needed for the Zun part) | If you want to invoke Zun’s Docker‑compatible API locally you can `pip install docker`.  You can also just use `openstack container …` commands. |

### Load the RC file  
```bash
source ~/Downloads/jetstream-2-openrc.sh   # path where you saved the file
# Verify you can talk to the cloud
openstack catalog list | head
```

You should see a list of services (e.g., `compute`, `network`, `image`, `magnum`, `zun`).

---

## 1 Spin a plain VM and run Docker via **cloud‑init**  

**Why?**  
A quick way to test Docker on Jetstream 2 without dealing with Magnum or Zun.  You’ll see how a *single* VM can become a container host.

### 1.1 Choose an image and flavor  

Jetstream 2 ships with a few ready‑to‑use images.  The easiest for Docker is **Rocky 8** (or **CentOS 8**).  Use the flavor **`m1.medium`** (2 vCPU, 4 GB RAM) – enough for a tiny web server.
```bash
# List images (look for “Rocky”)
openstack image list --public | grep -i rocky

# List flavors
openstack flavor list | grep m1.medium
```

### 1.2 Write a cloud‑init script  

Save the following into a file called `docker-cloudinit.yaml`:
```yaml
#cloud-config
package_update: true
package_upgrade: true
packages:

  - docker.io        # installs Docker Engine
runcmd:

  - [ systemctl, enable, --now, docker ]   # start Docker at boot

  - [ docker, run, -d, -p, "80:80", --name, nginx, nginx ]   # pull & run nginx
```

### 1.3 Create the instance  
```bash
openstack server create \
  --flavor m1.medium \
  --image <ROCKY_IMAGE_ID> \
  --key-name <YOUR_KEY_NAME> \
  --user-data docker-cloudinit.yaml \
  --security-group default \
  demo-docker-host
```

Replace `<ROCKY_IMAGE_ID>` and `<YOUR_KEY_NAME>` with the IDs you obtained earlier.

**Wait** until the server goes to `ACTIVE` (you can monitor with `openstack server list -c Name -c Status`).

### 1.4 Verify the service on the VM  
```bash
# Get the floating IP (or assign one if you don’t have)
openstack floating ip create public   # creates a new floating IP
openstack server add floating ip demo-docker-host <FLOATING_IP>

# Test via curl
curl http://<FLOATING_IP>
```

You should see the default **nginx** welcome page – the container is running!  

To ssh in and see Docker directly:
```bash
ssh -i ~/.ssh/jetstream2_rsa rocky@<FLOATING_IP>
docker ps          # shows the nginx container
```

!!! info "Tip"
    If the default security group blocks port 80, add a rule:
    `openstack security group rule create --proto tcp --dst-port 80:80 default`

---

## 2 Deploy a Managed Kubernetes Cluster with **Magnum**  

Magnum lets you spin up a full‑featured K8s cluster (control‑plane + workers) in a single command.  

### 2.1 Verify Magnum is available  
```bash
openstack coe cluster template list   # should show at least one template
openstack coe cluster list            # empty for now
```

If there are *no* templates, you can create a simple one (the commands below do that).

### 2.2 Create a **Cluster Template**  
```bash
openstack coe cluster template create k8s-jetstream \
  --image <ROCKY_IMAGE_ID> \
  --keypair <YOUR_KEY_NAME> \
  --external-network public \
  --flavor m1.medium \
  --master-flavor m1.large \
  --docker-volume-size 5 \
  --coe kubernetes \
  --dns-nameserver 8.8.8.8 \
  --network-driver flannel  # you can also use calico/kuryr if enabled
```

- **Control‑plane size**: `m1.large` (4 vCPU, 8 GB RAM) – gives a robust API server.  

- **Worker flavor**: `m1.medium` (2 vCPU, 4 GB RAM).  

### 2.3 Create the **Kubernetes Cluster**  
```bash
openstack coe cluster create jetstream-k8s \
  --cluster-template k8s-jetstream \
  --node-count 2   # two workers + one master
```

Magnum creates a **Heat stack** under the hood.  You can watch progress:
```bash
watch -n 5 "openstack coe cluster show jetstream-k8s -c status -c stack_id"
```

When `status` becomes **`CREATE_COMPLETE`**, the cluster is ready.

### 2.4 Retrieve the **kubeconfig**  
```bash
openstack coe cluster config jetstream-k8s > jetstream-k8s.kubeconfig
export KUBECONFIG=$(pwd)/jetstream-k8s.kubeconfig
kubectl get nodes
```

You should see three nodes (1 master, 2 workers) in `Ready` state.

### 2.5 Deploy a Sample App  

Create a file `hello.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
    spec:
      containers:

      - name: hello
        image: nginx:alpine
        ports:

        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: hello-svc
spec:
  type: LoadBalancer
  selector:
    app: hello
  ports:

    - protocol: TCP
      port: 80
      targetPort: 80
```

Apply it:
```bash
kubectl apply -f hello.yaml
```

Wait a few seconds, then check the external IP that the **LoadBalancer** service got:
```bash
kubectl get svc hello-svc
```

When the `EXTERNAL-IP` field shows an IP (usually allocated from the `public` neutron network), open it in a browser – you’ll see the nginx welcome page served by the two pods.

### 2.6 (Optional) Enable **Kuryr** for Neutron‑native networking  

If your Jetstream 2 deployment has the **Kuryr** service enabled, you can replace `--network-driver flannel` with `--network-driver kuryr`.  This will give each pod a **real Neutron port**, allowing you to apply security‑group rules directly to pods.

---

## 3 Run a Container Directly with **Zun**  

Zun implements a **Docker‑compatible REST API** on top of OpenStack services.  It’s handy for short‑lived jobs or when you don’t need a full K8s stack.

### 3.1 Verify Zun service  
```bash
openstack container service list
# You should see something like:
#  ID | Name | Enabled |
```

### 3.2 Upload a container image (if not already in Glance)  

Zun pulls images from the OpenStack Image service (Glance).  Let’s upload a tiny `alpine` image:
```bash
# Pull the image locally first (if you have Docker)
docker pull alpine:latest
# Export it as a tarball
docker save alpine:latest -o alpine.tar
# Upload to Glance
openstack image create alpine \
  --file alpine.tar \
  --disk-format raw \
  --container-format bare \
  --public
```

*(If your cloud already provides a public `alpine` image you can skip the upload.)*

### 3.3 Create & start a container  
```bash
# Create (but do not start) the container
openstack container create my-alpine \
  --image alpine \
  --flavor m1.tiny \
  --net public

# Start it
openstack container start my-alpine

# Run a command inside (similar to `docker exec`)
openstack container exec my-alpine echo "Hello from Zun!"
```

### 3.4 Inspect logs  
```bash
openstack container logs my-alpine
```

You’ll see the “Hello from Zun!” line.

### 3.5 Delete the container  
```bash
openstack container delete my-alpine
```

!!! note "Note"
    Zun containers are **first‑class OpenStack resources** – they obey the same quotas, RBAC, and billing as VMs. You can also attach floating IPs, security groups, etc., just like a regular instance.

---

## 4 Clean‑up  

Never leave resources running when you’re done; Jetstream 2 quota is limited.
```bash
# 1 Delete the Docker VM
openstack server delete demo-docker-host
openstack floating ip delete <FLOATING_IP_OF_VM>

# 2 Delete the Magnum K8s cluster (this also removes the underlying heat stack)
openstack coe cluster delete jetstream-k8s

# 3 Delete the Zun container (already done above) and any floating IP it used
openstack floating ip delete <FLOATING_IP_OF_ZUN_CONTAINER>
```

Check you have no dangling resources:
```bash
openstack server list
openstack coe cluster list
openstack container list
openstack floating ip list   # should be empty or only those you intentionally keep
```

---

## 5 Extras  

### 5.1 Quick reference cheat‑sheet  
```bash
#  Common OpenStack CLI shortcuts -----
# Load credentials
source ~/jetstream-2-openrc.sh

# List resources
openstack server list
openstack image list
openstack flavor list
openstack network list

# Create a keypair
openstack keypair create jetstream2_rsa > jetstream2_rsa.pub

# Security group rule for HTTP
openstack security group rule create --proto tcp --dst-port 80:80 default
```

### 5.2 Python helper – print Jetstream 2 flavor table  

The snippet below pulls the flavor list from the API and prints a tidy markdown table so you can decide which flavor to use for containers.
```python
import subprocess, json, textwrap, sys, os, shlex, re, pprint, math, datetime, time, itertools, collections, typing, random, string, hashlib, base64, urllib.parse, pathlib, ssl, socket, gzip, csv, io, statistics, fractions, decimal, inspect, uuid, json, itertools, sys, os, subprocess, datetime, typing, textwrap, collections, random, string, hashlib, base64, urllib.parse, pathlib, ssl, socket, gzip, csv, io, statistics, fractions, decimal, inspect, uuid
import json, subprocess, os, sys, textwrap, datetime, urllib.parse, base64, hashlib, random, string, itertools, collections, typing, math, re, pathlib, csv, io, statistics, fractions, decimal, inspect, uuid, ssl, socket, gzip

def get_flavors():
    # Call the OpenStack CLI and capture JSON output
    cmd = "openstack flavor list -f json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error running openstack flavor list")
        print(result.stderr)
        sys.exit(1)
    return json.loads(result.stdout)

def print_table(flavors):
    headers = ["Name", "RAM (GB)", "VCPU", "Disk (GB)"]
    rows = []
    for f in flavors:
        ram_gb = int(f["RAM"]) // 1024
        rows.append([f["Name"], f"{ram_gb}", f["VCPUs"], f["Disk"]])
    # Determine column widths
    col_widths = [max(len(str(item)) for item in col) for col in zip(*([headers] + rows))]
    # Print header
    header_line = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    separator = "-|-".join("-"*w for w in col_widths)
    print(header_line)
    print(separator)
    for r in rows:
        print(" | ".join(f"{c:<{w}}" for c, w in zip(r, col_widths)))

if __name__ == "__main__":
    flavors = get_flavors()
    print("\n## Jetstream 2 Flavor Summary (RAM shown in GB)\n")
    print_table(flavors)
```

**What it does**

1. Calls `openstack flavor list -f json` (the OpenStack client already knows your Jetstream endpoint).  

2. Parses the JSON and prints a markdown table with *Name*, *RAM (GB)*, *VCPU*, and *Disk (GB)*.

Run it locally after you have sourced your RC file:
```bash
python3 flavor_table.py
```

You’ll get an output like:
```
## Jetstream 2 Flavor Summary (RAM shown in GB)

Name       | RAM (GB) | VCPU | Disk (GB)
---------- | -------- | ---- | ----------
m1.tiny    | 1        | 1    | 10
m1.small   | 2        | 1    | 20
m1.medium  | 4        | 2    | 40
m1.large   | 8        | 4    | 80
...
```

Feel free to copy‑paste the table into your README or a Jupyter notebook.

### 5.3 Using **cloud‑init** to install *any* container runtime  

If you prefer **containerd** or **CRI‑O** instead of Docker, replace the `packages` and `runcmd` sections:
```yaml
#cloud-config
packages:

  - containerd
runcmd:

  - [ systemctl, enable, --now, containerd ]

  - [ ctr, image, pull, docker.io/library/nginx:alpine ]

  - [ ctr, run, -d, --net-host, docker.io/library/nginx:alpine, nginx ]
```

Just point `--user-data` to that file when you create the VM.

### 5.4 Debugging tips  

| Symptom | Likely cause | Quick fix |
|---------|--------------|-----------|
| `openstack coe cluster create` hangs forever | Heat service disabled or mis‑configured security groups. | Verify `openstack service list` includes *orchestration* (Heat). Check `openstack stack list` for errors. |
| `kubectl get nodes` shows “NotReady” | Worker nodes missing the required security‑group rules (port 10250). | OpenStack default SG may block kubelet traffic. Add rule: `openstack security group rule create --proto tcp --dst-port 10250:10250 default`. |
| Zun container can’t pull image | Image not public or not in Glance. | Ensure the image is `--public` or give the tenant’s project access via `openstack image share`. |
| Floating IP not reachable after assigning | Security group blocks SSH/HTTP. | Add inbound rules for ports 22, 80 (or whatever you need). |
| `docker ps` shows nothing after cloud‑init | Docker service didn’t start. | Check `/var/log/cloud-init-output.log` on the VM, look for errors installing `docker.io`. |

---

## Assignments

Goal is to conduct the following assignments:

!!! assignment "Assignment 1. **clouds.yaml**"
    Instead of using the rc file, document how to use the `clouds.yaml` file for authentication.

!!! assignment "Assignment 2. **Deployment Challenge**"
    Deploy an Nginx web server using the Zun method on Jetstream 2 and verify it is reachable via a floating IP.

!!! assignment "Assignment 3. **K8s Exploration**"
    Create a Magnum cluster on Jetstream 2, deploy a simple pod, and identify the underlying OpenStack VM instances.

!!! assignment "Assignment 4. **Automation**"
    Write a cloud-init script that installs both Docker and a custom monitoring agent on a Jetstream 2 VM.

!!! assignment "Assignment 5. **Analysis**"
    Create a table comparing the startup time and resource overhead of a Zun container vs. a Magnum node on Jetstream 2. This includes not only features, but also billing.

---

##  You’re done!  

You now have three **different ways** to run containers on Jetstream 2:

| Approach | When to use it |
|----------|----------------|
| **Docker on a simple VM** (cloud‑init) | Quick prototyping, one‑off tests, learning Docker basics. |
| **Magnum‑managed Kubernetes** | Production‑grade micro‑services, auto‑scaling, complex networking, CI/CD pipelines. |
| **Zun (Docker‑as‑a‑service)** | Short‑lived batch jobs, “run‑a‑container” from the OpenStack API, or when you want containers to obey OpenStack quotas without the overhead of a K8s control plane. |

All three respect Jetstream 2’s **quota, RBAC, and billing** mechanisms, and they all use the same underlying OpenStack services (Nova, Neutron, Glance, Keystone).  