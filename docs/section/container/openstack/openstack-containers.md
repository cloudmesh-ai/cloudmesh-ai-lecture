# OpenStack and Containers

## 1 Lecture Overview

| Time | Segment | Key Focus |
|------|----------|-----------|
| 5 min | **Welcome & agenda** | Set expectations and goals |
| 10 min | **OpenStack fundamentals** | Control plane vs. Data plane, Core services |
| 10 min | **Why containers in a cloud?** | Efficiency, agility, and the hybrid VM/Container world |
| 15 min | **OpenStack services for containers** | High-level overview: Magnum, Zun, Kuryr |
| 10 min | **CaaS vs. COaaS** | Zun (Container-as-a-Service) vs. Magnum (Orchestration-as-a-Service) |
| 10 min | **Deep dive: Magnum** | Cluster templates, Heat orchestration, K8s lifecycle |
| 10 min | **Deep dive: Zun** | Serverless container experience, avoiding VM overhead |
| 5 min | **Networking integration** | Kuryr, CNI, and the Neutron bridge |
| 5 min | **Security & Isolation** | Multi-tenancy, RBAC, and namespace isolation |
| 5 min | **Operational considerations** | Quotas, monitoring, and day-2 operations |
| 5 min | **Guided Mini-Lab** | Hands-on walkthrough (CLI based) |
| 10 min | **Q&A & wrap‑up** | Final synthesis and student questions |

*Total ≈ 90 min (adjustable).*


---

## 2 Learning Objectives

By the end of the lecture, participants will be able to:

1.  **Explain** the core OpenStack architecture, distinguishing between the control plane and the data plane.

2.  **Analyze** the technical trade-offs between running containers on VMs versus using native OpenStack container services.

3.  **Differentiate** between *Container-as-a-Service* (Zun) and *Container-Orchestration-as-a-Service* (Magnum).

4.  **Evaluate** how Kuryr optimizes container networking by bypassing traditional overlays in favor of native Neutron ports.

5.  **Outline** the workflow of provisioning a managed Kubernetes cluster via Magnum.

6.  **Execute** basic container lifecycle operations using the Zun CLI.

7.  **Design** a basic security and quota strategy for containerized workloads in a multi-tenant environment.

---

## 3 Slide‑by‑Slide Content

### Slide 1 – Title

- **Title:** *OpenStack & Containers – Bridging IaaS & Cloud‑Native*

- **Subtitle:** Scaling from Virtual Machines to Microservices

- **Presenter Note:** Set the stage: We are moving from "managing servers" to "managing applications."

---

### Slide 2 – Agenda

- (Use bullet list from the Overview table)

---

### Slide 3 – OpenStack 101 (The Foundation)

- **Core Concept:** Open‑source IaaS that transforms physical hardware into programmable virtual resources.

- **The Split:**

    - **Control Plane:** APIs and managers (Keystone, Glance, Nova-api) that decide *what* happens.

    - **Data Plane:** The actual resources (KVM hypervisors, OVS switches, Cinder volumes) where the *work* happens.

- **Key services:** Nova (compute), Neutron (network), Cinder (block storage), Swift (object), Glance (image), Keystone (identity).

- **The "Cloud" Formula:** $\text{Modular Services} + \text{Unified APIs} + \text{Orchestration} = \text{Cloud}$.

**Speaker note:** Emphasize that for containers to work, they must plug into this existing identity (Keystone) and networking (Neutron) fabric.

**Visual suggestion:** A layered diagram. Bottom: Physical Hardware $\rightarrow$ Middle: OpenStack Control Plane $\rightarrow$ Top: Consumer (CLI/Horizon).

---

### Slide 4 – Evolution of Workloads

- **Legacy Era:** Monolithic apps $\rightarrow$ Bare Metal $\rightarrow$ VMs (Slow boot, heavy overhead).

- **Cloud-Native Era:** Microservices $\rightarrow$ Containers (Fast boot, shared kernel, portable).

- **The Paradox:** We want the *isolation* and *governance* of a Cloud (OpenStack) with the *speed* and *density* of Containers.

- **Current State:** The "Hybrid Cloud" within a single data center—running VMs and Containers side-by-side.

**Visual suggestion:** A timeline showing the shift from a single large "cube" (Monolith) to many small "cubes" (Microservices) over the years.

---

### Slide 5 – Why Run Containers on OpenStack?
| Reason | Technical Benefit | Business Value |
|--------|-------------------|-----------------|
| **Resource Density** | Shared kernel reduces RAM/CPU overhead vs. VMs. | Lower infrastructure costs. |
| **Rapid Scaling** | Pods start in seconds, not minutes. | Better responsiveness to traffic spikes. |
| **Governance** | Leverage existing Keystone RBAC and Neutron security groups. | Consistent security policy across all workloads. |
| **Unified Fabric** | Use Kuryr to give containers "first-class" IP addresses. | Simplified networking and auditing. |
| **Infrastructure-as-Code** | Use Heat/Terraform to provision the cluster and the app. | Repeatable, automated deployments. |

**Speaker note:** Highlight that the biggest value is not "running a container" (you can do that on a laptop), but "managing containers at scale with enterprise governance."


---

### Slide 6 – The "Container Strategy" Decision

- **Option A: The DIY Path** (VM $\rightarrow$ Install OS $\rightarrow$ Install K8s/Docker).

    - *Pros:* Total control, custom kernel, specific CNI choices.

    - *Cons:* High operational overhead ("The K8s Tax").

- **Option B: The Managed Path** (OpenStack Magnum).

    - *Pros:* One-click clusters, integrated lifecycle, OpenStack-native scaling.

    - *Cons:* Less control over the master node configuration.

- **Option C: The Serverless Path** (OpenStack Zun).

    - *Pros:* No VM to manage, instant start, "just run my image."

    - *Cons:* No complex orchestration (no K8s pods/services).

**Visual suggestion:** A decision tree: "Do I need a full cluster?" $\rightarrow$ Yes (Magnum) / No $\rightarrow$ "Do I want to manage the OS?" $\rightarrow$ Yes (VM) / No (Zun).

---

### Slide 7 – Zun vs. Magnum: A Detailed Comparison
| Feature | OpenStack Zun | OpenStack Magnum |
|---------|----------------|-------------------|
| **Analogy** | "Docker as a Service" | "Kubernetes as a Service" |
| **Unit of Work** | Single Container | Entire Cluster (Master + Workers) |
| **Abstraction** | Hides the VM completely | Manages the VMs for the cluster |
| **Best For** | Short-lived tasks, CI/CD runners, simple apps | Production microservices, complex stateful apps |
| **Networking** | Direct Neutron port per container | Cluster-wide CNI (e.g., Flannel, Calico) or Kuryr |
| **Complexity** | Low (One API call to start) | Medium (Template $\rightarrow$ Cluster $\rightarrow$ Kubeconfig) |

---

### Slide 8 – Deep Dive: OpenStack Magnum

- **Purpose:** Provides "Container Orchestration as a Service" (COaaS).

- **The Workflow:**

    1. **Cluster Template:** Define the "blueprint" (OS image, flavor, K8s version, network).

    2. **Cluster:** Instantiate the blueprint (Specify number of nodes).

    3. **Access:** Magnum provides a `kubeconfig` file for the user.

- **Under the Hood:** Magnum uses **Heat** (OpenStack Orchestration) to launch the VM instances, configure the network, and run the installation scripts.

**Speaker note:** Explain that Magnum doesn't "run" Kubernetes; it "provisions and manages" the infrastructure that runs Kubernetes.

**Visual suggestion:** A flow chart: User $\rightarrow$ Magnum API $\rightarrow$ Heat $\rightarrow$ Nova/Neutron $\rightarrow$ K8s Cluster.

---

### Slide 9 – Magnum: Lifecycle & Management

- **Provisioning:** Automated installation of the COE (Container Orchestration Engine).

- **Scaling:** Add or remove worker nodes via a single API call.

- **Updating:** Rolling updates of the cluster version.

- **Integration:** Use **Octavia** (OpenStack Load Balancer) to expose K8s services to the internet.

---

### Slide 10 – Deep Dive: OpenStack Zun

- **Purpose:** Provides "Container as a Service" (CaaS).

- **The Experience:** "I have a Docker image; I want it to run in the cloud. I don't care about VMs, SSH keys, or Kubeconfigs."

- **Key Features:**

    - **No-VM Management:** Zun handles the underlying compute (can be a VM or a bare-metal node).

    - **Image Integration:** Pulls from Docker Hub, Quay, or local Glance images.

    - **Direct Access:** Containers get their own IP from Neutron.

**Speaker note:** Compare this to AWS Fargate or Google Cloud Run. It's about removing the "server" from the developer's mind.

---

### Slide 11 – Zun: Use Cases

- **CI/CD Pipelines:** Spin up a container to run a test suite, then destroy it immediately.

- **Quick Prototyping:** Test a new image without setting up a full K8s cluster.

- **Edge Computing:** Deploy lightweight containers to edge nodes where a full K8s stack is too heavy.

- **Task Offloading:** Running a heavy data-processing script as a one-off container.

---

### Slide 12 – Networking: The Magic of Kuryr

- **The Problem:** Standard K8s uses "overlays" (VXLAN/UDP), which creates a "network inside a network." This leads to double-encapsulation and poor performance.

- **The Solution (Kuryr):**

    - Bypasses the overlay.

    - Maps K8s pods **directly** to Neutron ports.

    - The container gets a "real" IP from the OpenStack network.

- **Benefits:**

    - **Visibility:** You can see container traffic in the Neutron dashboard.

    - **Security:** Apply Neutron Security Groups directly to pods.

    - **Performance:** Lower latency by removing the overlay layer.

**Visual suggestion:** "Before" (Pod $\rightarrow$ CNI $\rightarrow$ VM $\rightarrow$ Neutron) vs "After" (Pod $\rightarrow$ Kuryr $\rightarrow$ Neutron).

**Speaker note:** Mention you can watch the Heat stack creation in Horizon → **Project > Orchestration > Stacks**.

---

### Slide 10 – Deep Dive: Zun Architecture

1. **User** → **OpenStack CLI / Zun API** (Docker‑compatible).  

2. **Zun API** authenticates via **Keystone**.  

3. **Zun Conductor** schedules containers onto **Nova compute nodes** (by default).  

4. **Container runtime** (Docker, containerd, or CRI‑O) runs the image, using **Glance** as the image registry.  

5. **Neutron** provides networking (port, security‑group, floating IP).  

**Speaker note:** Zun treats containers as *first‑class resources* – they appear in `openstack server list`‑like tables.

**Visual suggestion:** Similar flow diagram, but replace “Heat → COE” with “Zun Conductor → Nova”.

---

### Slide 11 – Zun Quick CLI Example


```bash
# Pull an image into Glance (if not already there)
openstack image create cirros --file cirros-0.5.2-x86_64-disk.img --disk-format qcow2 --container-format bare

# Create and start a container
openstack container create mycirros \
    --image cirros \
    --flavor m1.tiny \
    --net private

openstack container start mycirros

# Exec into container (like docker exec)
openstack container exec mycirros hostname


```

**Speaker note:** Show how the container shows up in the **“Containers”** menu in Horizon (if enabled).

---

### Slide 12 – Networking Integration – Kuryr

- **Kuryr‑Kubernetes** implements the Kubernetes *CNI* plugin using **Neutron ports** for each pod.  

- **Benefits:**  

  * Native Neutron security groups & QoS per pod.  

  * Consistent IPAM (IP address management) across VMs & containers.  

  * Ability to attach containers to provider networks or VLANs.  

- **Alternatives:** Use Calico, Flannel (standalone) – but you lose OpenStack‑level policy integration.

**Speaker note:** Mention the *Kuryr‑Kubernetes* DaemonSet runs on each node and translates pod CIDR to Neutron.

**Visual suggestion:** Diagram with a K8s node, a pod, a Neutron port, and a security group.

---

### Slide 13 – Security & Multi‑Tenant Isolation
| Layer | Mechanism |
|-------|-----------|
| **Identity** | Keystone tokens used for API calls (Magnum, Zun, Kuryr). |
| **Compute** | Nova‑flavors, CPU pinning, PCI‑passthrough. |
| **Network** | Neutron security groups, network policies, provider vs. tenant networks. |
| **Image** | Glance image signatures, Trusted‑Registry. |
| **Runtime** | SELinux/AppArmor profiles for Docker/CRI‑O, gVisor/Kata for extra isolation. |
| **Encryption** | Cinder encrypted volumes, Barbican secrets for container env vars. |

**Speaker note:** Stress that containers inherit the same **tenant‑level quotas** as VMs – great for chargeback.

---

### Slide 14 – Operational Considerations

- **Quota & Billing** – Set limits on containers, pods, CPUs, RAM, volumes.  

- **Monitoring** – Use **Monasca**, **Ceilometer**, or **Prometheus** (via kube‑state‑metrics).  

- **Logging** – Centralised via **ELK** or **OpenSearch**, capture both VM and container logs.  

- **Backup/Recovery** – Snapshot Cinder volumes, export etcd (K8s) or persist container data to Cinder.  

- **Upgrade Path** – Magnum supports **Kubernetes version upgrades** via Heat updates; Zun upgrades are runtime‑based (Docker → containerd).  

**Speaker note:** Provide a short checklist for a production deployment.

---

### Slide 15 – Mini‑Lab: “Spin a K8s Cluster with Magnum”

1. **Prerequisite:** Access to an OpenStack cloud with Magnum enabled.  

2. **Task:** Use the CLI commands from Slide 9 to create a 2‑node K8s cluster.  

3. **Validate:** `kubectl get nodes`, deploy a simple Nginx deployment, expose via a LoadBalancer service.  

4. **Cleanup:** `openstack coe cluster delete myk8s`.

**Speaker note:** Allocate 5 min for students to try it (or show a recorded demo if time‑pressed).

---

### Slide 16 – Mini‑Lab: “Run a Container with Zun”

1. **Prerequisite:** Zun service enabled, image uploaded.  

2. **Task:** Create a container from the `alpine` image, run `echo hello`.  

3. **Validate:** `openstack container logs <id>` – see output.  

4. **Cleanup:** `openstack container delete <id>`.

**Speaker note:** Highlight the similarity to Docker CLI for a smooth learning curve.

---

### Slide 17 – When to Choose Which Service?
| Scenario | Recommended OpenStack component |
|----------|-----------------------------------|
| **Fully‑fledged micro‑services app** (multiple services, auto‑scale) | **Magnum + Kubernetes** |
| **Batch job or CI step** (run a script, then exit) | **Zun** |
| **Need per‑pod network policies and Neutron security groups** | **Magnum + Kuryr** |
| **Legacy app that only needs a single container** | **Zun** (or a minimal K8s pod via Magnum) |
| **Want to expose containers to external network via floating IP** | Both – use Neutron’s floating IPs (Zun) or LoadBalancer service (Magnum). |

**Speaker note:** Use a decision tree diagram for quick visual reference.

---

### Slide 18 – Future Roadmap (2024‑2026)

- **Magnum**: Support for newest K8s releases, integration with **Cluster‑API**, hardened TLS, optional **GPU‑operator** support.  

- **Zun**: Move from Docker to **containerd/CRI‑O** as default runtime, pilot **K8s‑style pod API** (experimental).  

- **Kuryr**: Full support for **K8s NetworkPolicy**, tighter coupling with **Octavia** for Service Load‑Balancing.  

- **OpenStack‑CNCF bridge**: Projects like **Aodh‑based autoscaling for Magnum clusters** and **Barbican‑backed secrets for pods**.

**Speaker note:** Mention that OpenStack remains a **CNCF member**, ensuring alignment with cloud‑native standards.

---

### Slide 19 – Recap & Take‑aways

- OpenStack provides a **unified control plane** for VMs **and** containers.  

- **Magnum** = Managed orchestration clusters; **Zun** = Docker‑like CaaS.  

- **Kuryr** ties container networking into the robust Neutron ecosystem.  

- Security, quota, and monitoring are **first‑class** for containers just as they are for VMs.  

- Choose the service that matches **workload complexity** and **operational preferences**.

---

### Slide 20 – Q&A

---

## 4 Additional Resources (handout URLs)

| Resource | Link |
|----------|------|
| OpenStack Magnum Docs | https://docs.openstack.org/magnum/latest/ |
| OpenStack Zun Docs | https://docs.openstack.org/zun/latest/ |
| Kuryr‑Kubernetes GitHub | https://github.com/openstack/kuryr-kubernetes |
| Magnum Quick‑Start Tutorial | https://docs.openstack.org/magnum/latest/user/quickstart.html |
| Zun CLI Reference | https://docs.openstack.org/python-zunclient/latest/ |
| OpenStack Containers Lab (GitHub) | https://github.com/openstack/openstack-helm/tree/master/containers |
| Video: “Running Kubernetes on OpenStack” (OpenStack Summit 2023) | https://www.youtube.com/watch?v=example123 |

*(Replace the placeholder YouTube link with the actual video URL you prefer.)*

---

## 5 Suggested Homework / Follow‑up Activities

1. **Deploy a two‑node Kubernetes cluster** on a test OpenStack cloud, then **install the Prometheus‑Operator** and expose metrics.  

2. **Create a Zun container** that pulls secrets from **Barbican**, demonstrating secure handling of credentials.  

3. **Write a Heat template** that provisions a Magnum cluster and an external load‑balancer (Octavia) in one transaction.  

4. **Compare cost**: launch the same micro‑service workload on VMs vs. containers (track CPU, RAM, storage consumption).  

---

## 6 Quick Reference Cheat Sheet (One‑pager)


```
# Magnum
openstack coe cluster template create <name> --coe kubernetes ...
openstack coe cluster create <cluster> --cluster-template <name> --node-count N
openstack coe cluster config <cluster> > kubeconfig.yaml
kubectl get nodes

# Zun
openstack image create <img> --file <path> --disk-format qcow2 --container-format bare
openstack container create <cname> --image <img> --flavor m1.tiny --net <net>
openstack container start <cname>
openstack container exec <cname> <cmd>
openstack container logs <cname>


```

Feel free to print this on a small card and hand it out.

---

### How to Use This Lecture Package

1. **Copy slide titles & bullet points** into your slide authoring tool.  

2. Insert the suggested visuals (architecture diagrams, timelines, decision tree).  

3. Prepare a **demo environment** (or recorded screencast) that shows the CLI commands in action.  

4. Allocate time for the **mini‑labs** – they reinforce concepts and give participants a sense of accomplishment.  

5. Conclude with **Q&A** and hand out the cheat sheet and resource list.