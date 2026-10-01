# Chameleon Cloud and Containers

This tutorial walks you through three ways to run containers on **Chameleon Cloud**: plain Docker on a VM, Magnum-managed Kubernetes, and Zun "Docker-as-a-service".

For a comprehensive understanding of these technologies, please refer to the **[OpenStack and Containers](/section/container/openstack/openstack-containers.md)** guide.

## Learning Objectives

By the end of this tutorial, participants will be able to:

1. **Provision** a basic VM on Chameleon Cloud and install a container runtime using cloud-init.
2. **Deploy** a managed Kubernetes cluster using OpenStack Magnum.
3. **Launch** and manage standalone containers using OpenStack Zun.
4. **Compare** and contrast the three container deployment methods on a research cloud.

---

## Overview

Chameleon Cloud provides an environment where researchers can experiment with various levels of container orchestration. Depending on whether you need a simple runtime for a single script or a full cluster for a microservices-based AI pipeline, you will choose between the DIY path, the managed path, or the serverless path.

!!! warning "Important Considerations"
    Be aware of billing and resource quotas before starting. It is highly recommended to complete the assignments regarding reservations and billing before attempting these tutorials.
    
!!! info "Why this matters"
    In research environments like Chameleon Cloud, the choice between a VM, Zun, or Magnum directly impacts the reproducibility of your experiments. Standardizing your environment via container images ensures that other researchers can run your AI models with the exact same dependency tree.

---

## Implementation

### 1 Prerequisites (run once)

Before proceeding, ensure you have obtained a reservation on Chameleon Cloud.

| Item | Command / Action |
|------|------------------|
| Authentication | Configure credentials in `~/.config/openstack/clouds.yaml` |
| OpenStack client | `pip install --user python-openstackclient` |
| SSH key pair | `ssh-keygen -t rsa -b 4096 -f ~/.ssh/chameleon_rsa` |
| `kubectl` (for Magnum) | `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && chmod +x kubectl && sudo mv kubectl /usr/local/bin/` |
| `docker` CLI (optional, for Zun) | `pip install --user docker` |

!!! info "Tip"
    After configuring `clouds.yaml`, run `openstack catalog list --os-cloud chameleon | head` – you should see `compute`, `network`, `magnum`, `zun`, etc.

### 2 Common Building Blocks (run as needed)

```bash
#  Images & flavors
openstack image list --public | grep -i rocky      # Rocky 9 works well
openstack flavor list | grep m1.medium           # 2 vCPU / 4 GB RAM

#  Keypair (once)
openstack keypair create chameleon_rsa > chameleon_rsa.pub

#  Default security group – allow HTTP if you need it
openstack security group rule create --proto tcp --dst-port 80:80 default
```

### 3 [Docker](/section/container/foundations/docker.md) on a Simple VM (quick-start)

1. **Cloud-init file** – `docker-cloudinit.yaml`

```yaml
   #cloud-config
   package_update: true
   packages:
     - docker.io
   runcmd:
     - [ systemctl, enable, --now, docker ]
     - [ docker, run, -d, -p, "80:80", --name, nginx, nginx ]
```

2. **Create the server**

```bash
   openstack server create \
     --flavor m1.medium \
     --image <ROCKY_ID> \
     --key-name chameleon_rsa \
     --user-data docker-cloudinit.yaml \
     demo-docker-vm
```

3. **Attach a floating IP & test**

```bash
   FIP=$(openstack floating ip create public -f value -c floating_ip_address)
   openstack server add floating ip demo-docker-vm $FIP
   curl http://$FIP   # should show nginx welcome page
```

*Result:* One VM running Docker with an nginx container.

### 4 Managed [Kubernetes](/section/container/orchestration/kubernetes.md) with Magnum

* Magnum user guide: <https://docs.openstack.org/magnum/latest/user/>

#### 4.1 Create a Cluster Template (once)

```bash
openstack coe cluster template create k8s-chameleon \
  --image <ROCKY_ID> \
  --keypair chameleon_rsa \
  --external-network public \
  --flavor m1.medium \
  --master-flavor m1.large \
  --docker-volume-size 5 \
  --coe kubernetes \
  --network-driver flannel   # replace with "kuryr" if you need Neutron-backed pod networking
```

#### 4.2 Spin up a cluster

```bash
openstack coe cluster create chameleon-k8s \
  --cluster-template k8s-chameleon \
  --node-count 2                # 2 workers + 1 master
```

*Watch progress:* `watch -n 5 "openstack coe cluster show chameleon-k8s -c status"`
When `status = CREATE_COMPLETE` proceed.

#### 4.3 Grab kubeconfig & verify

```bash
openstack coe cluster config chameleon-k8s > k8s.kubeconfig
export KUBECONFIG=$(pwd)/k8s.kubeconfig
kubectl get nodes   # three Ready nodes
```

#### 4.4 Deploy a demo app

`nginx-svc.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:

      - name: nginx
        image: nginx:alpine
        ports:

        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-svc
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:

  - protocol: TCP
    port: 80
    targetPort: 80
```

```bash
kubectl apply -f nginx-svc.yaml
kubectl get svc nginx-svc   # wait for EXTERNAL-IP, then browse to it
```

*Result:* A 3-node K8s cluster with a load-balanced nginx service.

### 5 Single-Container "Docker-as-a-Service" with Zun

#### 5.1 Verify Zun is enabled

```bash
openstack container service list   # expect a row with "zun" and "Enabled"
```

#### 5.2 Make sure a container image exists in Glance

If a public `alpine` image is already present, skip. Otherwise:

```bash
docker pull alpine:latest
docker save alpine:latest -o alpine.tar
openstack image create alpine \
  --file alpine.tar \
  --disk-format raw \
  --container-format bare \
  --public
```

#### 5.3 Create & run the container

```bash
# Create (stopped) container
openstack container create my-alpine \
  --image alpine \
  --flavor m1.tiny \
  --net public

# Start it
openstack container start my-alpine

# Execute a command (Docker-compatible)
openstack container exec my-alpine echo "Hello from Zun!"
```

#### 5.4 Inspect & clean up

```bash
openstack container logs my-alpine
openstack container delete my-alpine
```

*Result:* A container that behaves like a VM – respects quotas, security groups, and can have a floating IP if needed.

### 6 Clean-up (run at the end of any demo)

```bash
# Docker VM
openstack server delete demo-docker-vm
openstack floating ip delete $FIP

# Magnum cluster (removes all underlying Heat resources)
openstack coe cluster delete chameleon-k8s

# Verify nothing is left
openstack server list
openstack coe cluster list
openstack container list
openstack floating ip list
```

---

## Self-Evaluation

Test your knowledge by expanding the questions below.

??? question "What are the three main ways to run containers on Chameleon Cloud?"
        The three ways are:
        1. **Docker-on-VM**: Provisioning a standard VM and installing Docker manually or via `cloud-init`.
        2. **Magnum-managed Kubernetes**: Deploying a full K8s cluster managed by OpenStack Magnum.
        3. **Zun**: Launching standalone containers as a service via OpenStack Zun.

??? question "How can `cloud-init` be used to automate the installation of a container runtime on a Chameleon VM?"
        A `cloud-init` YAML file can be passed as `--user-data` during server creation. It can specify the installation of the `docker.io` package and include `runcmd` instructions to enable the Docker service and launch a specific container (e.g., Nginx) automatically upon boot.

??? question "When would you choose Zun over Magnum for deploying containers?"
        Zun is preferable for one-off containers, simple workflows, or short-lived batch jobs where the overhead of deploying and managing a full Kubernetes cluster (via Magnum) is unnecessary.

---

## Assignments

Goal is to conduct the following assignments:

!!! assignment "Assignment 1. **Basic Commands**"
    Refresh your knowledge of the basic VM commands. Make sure to have the `~/.config/openstack/clouds.yaml` file in place.

    ```bash
    # Load credentials
    export OS_CLOUD=chameleon

    # Common listings
    openstack server list
    openstack image list
    openstack flavor list
    openstack network list
    openstack floating ip list

    # Keypair (once)
    openstack keypair create chameleon_rsa > chameleon_rsa.pub

    # Open port 80 on default SG
    openstack security group rule create --proto tcp --dst-port 80:80 default
    ```

!!! assignment "Assignment 2. **Basic Python Programming**" 
    Refresh your knowledge about basic python programming for OpenStack. We review how to print a Markdown table of Chameleon flavors. It pulls the flavor list from the OpenStack API and prints a clean markdown table (RAM shown in GB). Run it in a notebook or a local Python environment.

    !!! warning "Improvement Opportunity"
        The current implementation uses `subprocess` to call the CLI. Consider using the official `openstacksdk` Python library for a more robust and professional implementation.

    ??? tip "Solution Assignment 2"
        ```python
        import subprocess, json, sys

        def get_flavors():
            cmd = "openstack flavor list -f json"
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if proc.returncode != 0:
                print("Error:", proc.stderr, file=sys.stderr)
                sys.exit(1)
            return json.loads(proc.stdout)

        def md_table(flavors):
            headers = ["Name", "RAM (GB)", "VCPU", "Disk (GB)"]
            rows = []
            for f in flavors:
                ram_gb = int(f["RAM"]) // 1024
                rows.append([f["Name"], str(ram_gb), f["VCPUs"], f["Disk"]])
            # column widths
            colw = [max(len(str(item)) for item in col) for col in zip(*([headers] + rows))]
            line = " | ".join(h.ljust(w) for h, w in zip(headers, colw))
            sep  = "-|-".join("-"*w for w in colw)
            body = "\n".join(" | ".join(c.ljust(w) for c, w in zip(r, colw)) for r in rows)
            return f"{line}\n{sep}\n{body}"

        flavors = get_flavors()
        print("\n## Chameleon Flavor Summary\n")
        print(md_table(flavors))
        ```

!!! assignment "Assignment 3. **Deployment Challenge**"
    Deploy an Nginx web server using the Zun method and verify it is reachable via a floating IP.

!!! assignment "Assignment 4. **K8s Exploration**"
    Create a Magnum cluster, deploy a simple pod, and identify the underlying OpenStack VM instances.

!!! assignment "Assignment 5. **Automation**" 
    Write a cloud-init script that installs both Docker and a custom monitoring agent on a Chameleon VM.

!!! assignment "Assignment 6. **Analysis**" 
    Create a table comparing the startup time and resource overhead of a Zun container vs. a Magnum node. This includes not only features, but also billing.

---

### Summary Matrix

| Goal | Recommended approach |
|------|----------------------|
| **One-off container / workflow step** | **Zun** (Docker-as-a-service) |
| **Full micro-service stack, auto-scale** | **Magnum + Kubernetes** |
| **Just want Docker on a VM** | **Plain VM + cloud-init** |

## What's Next?
Now that you've explored containers on research clouds, it's time to learn how to secure these workloads for production. Proceed to the **[Container Security & Hardening](/section/container/security/container-security.md)** guide.
