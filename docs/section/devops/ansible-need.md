# Do I  need ansible?

Whether you still need Ansible when using Docker and Kubernetes depends on what layer of your infrastructure you are managing. They solve different problems and are generally complementary rather than interchangeable.

### The Short Answer

* **Docker** packages your application and its dependencies into containers.
* **Kubernetes** orchestrates and manages those containers at scale (handling scaling, networking, and deployments).
* **Ansible** provisions, configures, and manages the underlying infrastructure (such as virtual machines, bare-metal servers, network switches, and OS-level settings).

Even if your applications run entirely inside Docker and Kubernetes, you often still need Ansible to set up the environment *before* Kubernetes can run.

---

### When You Still Need Ansible

You will likely still need Ansible for tasks such as:

* **Provisioning and Bootstrapping Nodes:** Setting up raw virtual machines (on AWS, GCP, Azure, or on-premise) by installing operating system dependencies, configuring security hardening, setting up firewalls, and preparing them to join a Kubernetes cluster.
* **Managing Non-Containerized Infrastructure:** Configuring load balancers, external databases, storage systems, or monitoring agents that live outside of your Kubernetes cluster.
* **Day-2 Infrastructure Operations:** Automating OS updates, disk partitioning, or user access management on your cluster nodes.
* **GitOps and Cluster Bootstrap:** Using Ansible to provision the Kubernetes cluster itself (e.g., using tools like Kubespray) and deploying initial system-level Helm charts or operators.

---

### When You Might *Not* Need Ansible

You can skip Ansible if:

* You use a fully managed Kubernetes service (like AWS EKS, Google GKE, or Azure AKS) where the cloud provider completely manages the underlying infrastructure nodes.
* Your infrastructure is entirely immutable and managed via Infrastructure as Code (IaC) tools like Terraform or OpenTofu for provisioning, combined with ArgoCD or Flux for deploying applications directly to Kubernetes.