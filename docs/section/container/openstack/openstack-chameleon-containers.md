# Chameleon Cloud and Containers

Below is a **compact  tutorial** that walks you through the three ways to run containers on **Chameleon Cloud** (plain Docker‑on‑VM, Magnum‑managed Kubernetes, and Zun “Docker‑as‑a‑service”).  
It captures only the essential commands, decision points, and gotchas – no duplicated explanations.

Be aware of the billing before you start it.

Do Assignment 6 in this regard first before you attempt trying it out

!!! warning 
    There could be issues in this tutorial. It is your assignment to improve it and make sure it runs.

!!! tip 
    Do not forget o get a reservation. Add a section oon how to do this to this tutorial in the Prerequisit section.

## Learning Objectives

By the end of this tutorial, participants will be able to:

1. **Provision** a basic VM on Chameleon Cloud and install a container runtime using cloud-init.
2. **Deploy** a managed Kubernetes cluster using OpenStack Magnum.
3. **Launch** and manage standalone containers using OpenStack Zun.
4. **Compare** and contrast the three container deployment methods on a research cloud.

---

## 1 Prerequisites (run once)


| Item | Command / Action |
|------|------------------|
| Authentication | Configure credentials in ~/.config/openstack/clouds.yaml |
| OpenStack client | `pip install --user python-openstackclient` |
| SSH key pair | `ssh-keygen -t rsa -b 4096 -f ~/.ssh/chameleon_rsa` |
| `kubectl` (for Magnum) | `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && chmod +x kubectl && sudo mv kubectl /usr/local/bin/` |
| `docker` CLI (optional, for Zun) | `pip install --user docker` |

!!! info "Tip"
    After configuring `clouds.yaml`, run `openstack catalog list --os-cloud chameleon | head` – you should see `compute`, `network`, `magnum`, `zun`, etc.

---

## 2 Common Building Blocks (run as needed)


```bash
#  Images & flavors
openstack image list --public | grep -i rocky      # Rocky 9 works well
openstack flavor list | grep m1.medium           # 2 vCPU / 4 GB RAM

#  Keypair (once)
openstack keypair create chameleon_rsa > chameleon_rsa.pub

#  Default security group – allow HTTP if you need it
openstack security group rule create --proto tcp --dst-port 80:80 default


```

---

## 3 Docker on a Simple VM (quick‑start)

1. **Cloud‑init file** – `docker-cloudinit.yaml`  


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

---

## 4 Managed Kubernetes with Magnum  

* Magnum user guide: <https://docs.openstack.org/magnum/latest/user/>

### 4.1 Create a Cluster Template (once)


```bash
openstack coe cluster template create k8s-chameleon \
  --image <ROCKY_ID> \
  --keypair chameleon_rsa \
  --external-network public \
  --flavor m1.medium \
  --master-flavor m1.large \
  --docker-volume-size 5 \
  --coe kubernetes \
  --network-driver flannel   # replace with “kuryr” if you need Neutron‑backed pod networking


```

### 4.2 Spin up a cluster


```bash
openstack coe cluster create chameleon-k8s \
  --cluster-template k8s-chameleon \
  --node-count 2                # 2 workers + 1 master


```

*Watch progress:* `watch -n 5 "openstack coe cluster show chameleon-k8s -c status"`  
When `status = CREATE_COMPLETE` proceed.

### 4.3 Grab kubeconfig & verify


```bash
openstack coe cluster config chameleon-k8s > k8s.kubeconfig
export KUBECONFIG=$(pwd)/k8s.kubeconfig
kubectl get nodes   # three Ready nodes


```

### 4.4 Deploy a demo app

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

*Result:* A 3‑node K8s cluster with a load‑balanced nginx service.

---

## 5 Single‑Container “Docker‑as‑a‑Service” with Zun  

### 5.1 Verify Zun is enabled


```bash
openstack container service list   # expect a row with “zun” and “Enabled”
```

### 5.2 Make sure a container image exists in Glance  

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

### 5.3 Create & run the container


```bash
# Create (stopped) container
openstack container create my-alpine \
  --image alpine \
  --flavor m1.tiny \
  --net public

# Start it
openstack container start my-alpine

# Execute a command (Docker‑compatible)
openstack container exec my-alpine echo "Hello from Zun!"
```

### 5.4 Inspect & clean up


```bash
openstack container logs my-alpine
openstack container delete my-alpine
```

*Result:* A container that behaves like a VM – respects quotas, security groups, and can have a floating IP if needed.

---

## 6 Clean‑up (run at the end of any demo)


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


## Assignments

Goal is to conduct the follwoing assignments:

1. **Basic Commands:** Refresh your knowledg of the basic VM commands.
2. **Basic Python Programming:** Refresh you knowlade about basic python programming for OpenStack.
2. **Deployment Challenge**: Deploy an Nginx web server using the Zun method and verify it is reachable via a floating IP.
3. **K8s Exploration**: Create a Magnum cluster, deploy a simple pod, and identify the underlying OpenStack VM instances.
4. **Automation**: Write a cloud-init script that installs both Docker and a custom monitoring agent on a Chameleon VM.
5. **Analysis**: Create a table comparing the startup time and resource overhead of a Zun container vs. a Magnum node.

---

!!! note "Assignment.1: Basic Commands"

    To refresh your knowledge please try these commands.
    Make sure to have the `~/config/openstack/clouds.yaml" file in place.

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

!!! note "Assignment.2: Basic Python Programming" 

    Refresh you knowlade about basic python programming for OpenStack. We review how to print a Markdown table of Chameleon flavors. It pulls the flavor list from the OpenStack API and prints a clean markdown table (RAM shown in GB). Run it in a notebook or a local Python environment.


    !!! warning
        Why is this program not so goo? You could have use the Openstack API instead. provide such a script and add here witha pull request.


!!! tip "Solution Assignemt 2"

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

    *Result example* (will reflect the actual flavors in your project):


    ```
    ## Chameleon Flavor Summary

    Name       | RAM (GB) | VCPU | Disk (GB)
    -----------|----------|------|-----------
    m1.tiny    | 1        | 1    | 10
    m1.small   | 2        | 1    | 20
    m1.medium  | 4        | 2    | 40
    m1.large   | 8        | 4    | 80
    ...
    ```

!!! tip
    Use that table when choosing a flavor for Docker, Magnum workers, or Zun containers.

---

!!! assignment "Assignment 2. **Deployment Challenge**"
    Deploy an Nginx web server using the Zun method and verify it is reachable via a floating IP.

!!! assignment "Assignment 3. **K8s Exploration**"
    Create a Magnum cluster, deploy a simple pod, and identify the underlying OpenStack VM instances.

!!! assignment "Assignment 4. **Automation**" 
    Write a cloud-init script that installs both Docker and a custom monitoring agent on a Chameleon VM.

!!! assignment "Assignment 5. **Analysis**" 
    Create a table comparing the startup time and resource overhead of a Zun container vs. a Magnum node.
    This includes not only features, but also billing.


###  Summary
| Goal | Recommended approach |
|------|----------------------|
| **One‑off container / workflow step** | **Zun** (Docker‑as‑a‑service) |
| **Full micro‑service stack, auto‑scale** | **Magnum + Kubernetes** |
| **Just want Docker on a VM** | **Plain VM + cloud‑init** |

