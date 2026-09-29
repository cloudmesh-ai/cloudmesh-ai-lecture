# Automating Infrastructure with Ansible

!!! info "Learning Objectives"
    - Compare the roles of Ansible, Docker, and Kubernetes in a modern DevOps stack.
    - Identify specific scenarios where Ansible is essential even in containerized environments.
    - Understand the concept of "bootstrapping" infrastructure.
    - Determine when to use a managed cloud service versus self-managed infrastructure.
    - Define Ansible and its role in the DevOps ecosystem.
    - Install and configure Ansible for remote server management.
    - Create and execute Ansible Playbooks using YAML syntax.
    - Understand key Ansible concepts: Modules, Tasks, Handlers, and Inventories.
    - Implement an automated deployment of a service (e.g., Apache or MariaDB).

## Ansible in the Age of Kubernetes and Docker

A common question for developers moving to the cloud is: *"If I'm using Docker and Kubernetes, do I still need a configuration management tool like Ansible?"*

The answer depends on which layer of your infrastructure you are managing. While these tools are often discussed together, they solve fundamentally different problems and are complementary rather than interchangeable.

### The DevOps Trinity

To understand why you might need all three, consider their primary roles:

| Tool | Primary Role | Analogy |
| :--- | :--- | :--- |
| **Docker** | **Packaging**: Wraps an application and its dependencies into a portable container. | The "shipping container" that holds the goods. |
| **Kubernetes** | **Orchestration**: Manages the deployment, scaling, and networking of those containers across a cluster. | The "crane and ship captain" managing the containers. |
| **Ansible** | **Provisioning**: Sets up the underlying servers, OS, and network settings that allow Kubernetes to run. | The "dockyard" building the pier and installing the electricity. |

!!! info "Why this matters"
    Containers abstract the application from the OS, but they do not abstract the *hardware or the VM* from the cloud provider. Someone still has to install the OS, configure the firewall, set up the container runtime (like containerd), and join the node to the Kubernetes cluster. This "bootstrapping" phase is where Ansible excels.

### When Ansible is Essential

Even in a "Kubernetes-first" world, Ansible is critical for the following tasks:

- **Provisioning and Bootstrapping Nodes**: Setting up raw virtual machines on AWS, GCP, or Azure. This includes installing OS dependencies, security hardening, and preparing the machine to join a K8s cluster.
- **Managing Non-Containerized Infrastructure**: Not everything can be a container. You still need to configure physical load balancers, external database clusters, storage arrays, or corporate monitoring agents that must run directly on the host OS.
- **Day-2 Infrastructure Operations**: Automating critical OS-level tasks such as kernel updates, disk partitioning, or managing SSH access and user accounts across your cluster nodes.
- **Cluster Bootstrapping (GitOps)**: Using tools like **Kubespray** (which is built on Ansible) to provision the Kubernetes cluster itself from scratch.

### When You Can Skip Ansible

You may find that you don't need Ansible if your environment fits these criteria:

1.  **Fully Managed Kubernetes**: If you use AWS EKS, Google GKE, or Azure AKS, the cloud provider manages the underlying worker nodes for you. You interact with the API, and the provider handles the OS and runtime.
2.  **Pure Immutable Infrastructure**: If you use Terraform to create "Golden Images" (via Packer) that already have everything installed, and you replace the entire VM whenever a change is needed rather than updating it in place.
3.  **Pure GitOps**: If you use ArgoCD or Flux to manage everything *inside* the cluster, and your cluster was provisioned via a managed service.

---

Managing dozens or hundreds of servers manually via SSH is inefficient and error-prone. When a system administrator has to run the same sequence of commands on fifty different machines, the risk of a typo or a missed step increases exponentially. Ansible provides a way to automate these tasks in a scalable, consistent, and reliable manner.

Ansible is an open-source IT automation engine that allows you to manage and configure compute resources. Unlike many other automation tools, Ansible is "agentless," meaning you do not need to install any special software on the target nodes; it communicates over standard SSH.

!!! info "Why this matters"
    In a DevOps pipeline, "Infrastructure as Code" (IaC) is a requirement. Ansible allows you to treat your server configurations as code, which can be version-controlled in Git, reviewed by peers, and tested in staging before being applied to production. This eliminates "configuration drift" and ensures that every server in a cluster is configured identically.

!!! tip "AI Insight"
    AI can significantly accelerate the creation of Ansible Playbooks and Roles by generating YAML tasks based on a list of requirements. When using AI for configuration, ensure you validate the modules being suggested, as LLMs may occasionally suggest deprecated modules. See [[ai-devops]] for more.

## Core Capabilities of Ansible

Ansible is versatile and can be used across the entire software delivery lifecycle:

- **Provisioning**: Setting up the base virtual machines or cloud instances that form your infrastructure.
- **Configuration Management**: Changing the state of the OS, installing packages, managing users, and implementing security policies.
- **Service Management**: Starting, stopping, or restarting services and managing system updates.
- **Application Deployment**: Automating the rollout of application code in a way that integrates with CI/CD strategies.

## Detailed Use Case: Automating a Web Stack

To see Ansible in action, let's look at a real-world scenario: deploying a secure web server with a custom configuration and a firewall.

### The Playbook: `webserver.yml`

```yaml
---
- hosts: webservers
  become: yes
  vars:
    http_port: 80
    app_user: www-data

  tasks:
    - name: Update package cache
      apt:
        update_cache: yes

    - name: Install Nginx and basic tools
      apt:
        name: 
          - nginx
          - curl
          - ufw
        state: present

    - name: Configure Nginx custom index page
      template:
        src: index.html.j2
        dest: /var/www/html/index.html
        owner: {{ app_user }}
        group: {{ app_user }}
        mode: '0644'
      notify: restart nginx

    - name: Setup basic firewall (Allow SSH and HTTP)
      ufw:
        rule: allow
        port: "{{ item }}"
        proto: tcp
      loop:
        - 22
        - "{{ http_port }}"

    - name: Enable UFW firewall
      ufw:
        state: enabled
        policy: deny

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

### Typical Usage Reference

| Task | Ansible Module | Key Attribute | Effect |
| :--- | :--- | :--- | :--- |
| **Install Software** | `apt` / `yum` | `state: present` | Ensures package is installed. |
| **Manage Files** | `copy` / `template` | `dest: /path/to/file` | Copies a file or renders a Jinja2 template. |
| **Control Services** | `service` / `systemd` | `state: started` | Ensures a service is running. |
| **User Mgmt** | `user` | `state: present` | Creates or updates a system user. |
| **Firewall** | `ufw` / `firewalld` | `rule: allow` | Opens or closes network ports. |
| **Shell Commands** | `shell` / `command` | `cmd: "ls -l"` | Runs a raw shell command (use sparingly). |

---

## Detailed Use Case: Automating a Web Stack

To see Ansible in action, let's look at a real-world scenario: deploying a secure web server with a custom configuration and a firewall.

### The Playbook: `webserver.yml`

```yaml
---
- hosts: webservers
  become: yes
  vars:
    http_port: 80
    app_user: www-data

  tasks:
    - name: Update package cache
      apt:
        update_cache: yes

    - name: Install Nginx and basic tools
      apt:
        name: 
          - nginx
          - curl
          - ufw
        state: present

    - name: Configure Nginx custom index page
      template:
        src: index.html.j2
        dest: /var/www/html/index.html
        owner: {{ app_user }}
        group: {{ app_user }}
        mode: '0644'
      notify: restart nginx

    - name: Setup basic firewall (Allow SSH and HTTP)
      ufw:
        rule: allow
        port: "{{ item }}"
        proto: tcp
      loop:
        - 22
        - "{{ http_port }}"

    - name: Enable UFW firewall
      ufw:
        state: enabled
        policy: deny

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

### Typical Usage Reference

| Task | Ansible Module | Key Attribute | Effect |
| :--- | :--- | :--- | :--- |
| **Install Software** | `apt` / `yum` | `state: present` | Ensures package is installed. |
| **Manage Files** | `copy` / `template` | `dest: /path/to/file` | Copies a file or renders a Jinja2 template. |
| **Control Services** | `service` / `systemd` | `state: started` | Ensures a service is running. |
| **User Mgmt** | `user` | `state: present` | Creates or updates a system user. |
| **Firewall** | `ufw` / `firewalld` | `rule: allow` | Opens or closes network ports. |
| **Shell Commands** | `shell` / `command` | `cmd: "ls -l"` | Runs a raw shell command (use sparingly). |

---

## Detailed Use Case: Automating a Web Stack

To see Ansible in action, let's look at a real-world scenario: deploying a secure web server with a custom configuration and a firewall.

### The Playbook: `webserver.yml`

```yaml
---
- hosts: webservers
  become: yes
  vars:
    http_port: 80
    app_user: www-data

  tasks:
    - name: Update package cache
      apt:
        update_cache: yes

    - name: Install Nginx and basic tools
      apt:
        name: 
          - nginx
          - curl
          - ufw
        state: present

    - name: Configure Nginx custom index page
      template:
        src: index.html.j2
        dest: /var/www/html/index.html
        owner: {{ app_user }}
        group: {{ app_user }}
        mode: '0644'
      notify: restart nginx

    - name: Setup basic firewall (Allow SSH and HTTP)
      ufw:
        rule: allow
        port: "{{ item }}"
        proto: tcp
      loop:
        - 22
        - "{{ http_port }}"

    - name: Enable UFW firewall
      ufw:
        state: enabled
        policy: deny

  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

### Typical Usage Reference

| Task | Ansible Module | Key Attribute | Effect |
| :--- | :--- | :--- | :--- |
| **Install Software** | `apt` / `yum` | `state: present` | Ensures package is installed. |
| **Manage Files** | `copy` / `template` | `dest: /path/to/file` | Copies a file or renders a Jinja2 template. |
| **Control Services** | `service` / `systemd` | `state: started` | Ensures a service is running. |
| **User Mgmt** | `user` | `state: present` | Creates or updates a system user. |
| **Firewall** | `ufw` / `firewalld` | `rule: allow` | Opens or closes network ports. |
| **Shell Commands** | `shell` / `command` | `cmd: "ls -l"` | Runs a raw shell command (use sparingly). |

---

## Getting Started with Ansible

### Prerequisites

To follow the examples in this chapter, you will need:
- An Ubuntu (e.g., 18.04+) virtual machine installed on VirtualBox or a cloud provider.
- Ability to install software via `apt-get`.
- SSH credentials and the ability to log in to your target virtual machines without manual password entry (using SSH keys).

### Installation and Setup

First, update your local package index and install Ansible:

```bash
sudo apt-get update
sudo apt-get install ansible

```

To keep your projects organized, create a dedicated working directory:

```bash
mkdir ansible-apache
cd ansible-apache

```

### Managing Target Hosts (The Inventory)

Ansible needs to know which servers it is managing. This is handled by an **Inventory** file. By default, Ansible looks for `/etc/ansible/hosts`, but for project-specific work, it is better to use a local configuration.

Create a file named `inventory.cfg` to specify a custom host file:

```ini
[defaults]
hostfile = hosts.txt

```

Now, create the `hosts.txt` file and define your server groups. For example, to create a group called `apache`:

```ini
[apache]
<server_ip> ansible_ssh_user=<server_username>

```

Replace `<server_ip>` and `<server_username>` with your actual VM details. By grouping servers, you can target all machines in the `apache` group with a single command.

## Creating Your First Playbook

An Ansible **Playbook** is a YAML file that describes the desired state of your systems. It tells Ansible *what* to do, rather than *how* to do it.

### Example: Installing Apache

Create a file named `apache.yml`. This playbook ensures that the Apache2 web server is installed and the package cache is updated.

```yaml
---
- hosts: apache
  become: yes
  tasks:
    - name: install apache2
      apt:
        name: apache2
        update_cache: yes
        state: present

```

**Key components of this playbook:**
- `hosts: apache`: Targets all servers defined in the `[apache]` group of your inventory.
- `become: yes`: Tells Ansible to execute the tasks with root privileges (sudo).
- `tasks`: A list of actions to perform.
- `apt`: The Ansible **module** used to manage packages on Debian/Ubuntu systems.

### Executing the Playbook

Run the playbook using the `ansible-playbook` command:

```bash
ansible-playbook -i hosts.txt apache.yml
```

!!! info "Why this matters"
    One of Ansible's most features is **idempotence**. If you run the same playbook a second time, Ansible will detect that Apache is already installed and will report `ok` instead of `changed`. This allows you to run playbooks frequently to ensure servers haven't drifted from their intended configuration.

## Advanced Implementation: Deploying MariaDB

For more complex services, you may need to perform multiple steps, such as importing GPG keys and adding external repositories.

```yaml
---
- hosts: db_servers
  become: yes
  tasks:
    - name: Import MariaDB public GPG key
      apt_key:
        url: https://mariadb.org/mariadb_release_signing_key.asc
        state: present
    
    - name: Add MariaDB repository
      apt_repository:
        repo: deb [arch=amd64] http://mirror.mariadb.org/repo/10.6/ubuntu focal main
        state: present
    
    - name: Install MariaDB Server
      apt:
        name: mariadb-server
        state: present
    
    - name: Ensure MariaDB is started and enabled
      service:
        name: mariadb
        state: started
        enabled: yes

```

### Understanding the "Handled" Logic

In a real-world scenario, you might want to restart a service only if a configuration file was changed. This is where **Handlers** come in. A handler is a special task that only runs when "notified" by another task.

```yaml
  tasks:
    - name: Update MariaDB configuration
      template:
        src: my.cnf.j2
        dest: /etc/mysql/mariadb.conf.d/50-server.cnf
        notify: restart mariadb
  
  handlers:
    - name: restart mariadb
      service:
        name: mariadb
        state: restarted

```

## Structuring Automation with Ansible Roles

As playbooks grow in complexity, putting all tasks in a single YAML file becomes difficult to manage. **Ansible Roles** provide a standardized way to bundle tasks, handlers, variables, and files into a reusable directory structure.

### The Anatomy of a Role
A role is organized into specific folders, each with a dedicated purpose:
- `tasks/main.yml`: The primary list of tasks to be executed.
- `handlers/main.yml`: Handlers that can be notified by tasks.
- `vars/main.yml`: High-priority variables for the role.
- `defaults/main.yml`: Default variables that can be easily overridden.
- `templates/`: Jinja2 templates for configuration files.
- `files/`: Static files to be copied to the target nodes.

### Why Use Roles?
- **Organization**: Separates the *logic* of a service (e.g., "how to install MariaDB") from the *deployment* (e.g., "which servers get MariaDB").
- **Shareability**: Roles can be shared publicly via **Ansible Galaxy**, allowing you to leverage community-tested automation instead of writing everything from scratch.
- **Reusability**: You can apply the same "common" role (SSH hardening, NTP sync) to every server in your infrastructure regardless of its primary purpose.

### Example: Using a Role in a Playbook
Once a role is created, your playbook becomes significantly cleaner:

```yaml
---
- hosts: db_servers
  become: yes
  roles:
    - common
    - mariadb_server
```

!!! info "Why this matters"
    Roles transform Ansible from a task-runner into a full-scale configuration management system. They allow teams to build a library of "company-standard" configurations that can be deployed consistently across thousands of nodes.

## Key Ansible Terminology

To master Ansible, you must understand these core concepts:

- **Module**: A small program that Ansible pushes to the target node to execute a specific task (e.g., `apt`, `copy`, `service`).
- **Task**: The smallest unit of action in a playbook; it combines a module with specific arguments.
- **Handler**: A task that is triggered by a `notify` statement, typically used for restarting services after a config change.
- **Playbook**: A YAML file containing one or more "plays" (groups of tasks targeted at specific hosts).
- **Inventory**: A list of managed nodes, often organized into groups.

## Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the difference between agent-based and agentless automation?"
 	Agent-based automation (like Puppet or Chef) requires a dedicated software agent to be installed and running on every target node. Agentless automation (like Ansible) communicates over standard protocols like SSH, meaning no special software is needed on the target nodes, which simplifies deployment and reduces resource overhead.

??? question "How do I set up an Ansible inventory and target specific host groups?"
 	An inventory is a file (e.g., `hosts.txt`) that lists the IP addresses or hostnames of your managed nodes. By organizing these hosts into groups (e.g., `[webservers]`, `[databases]`), you can target specific subsets of your infrastructure in your playbooks or ad-hoc commands using the group name instead of individual IPs.

??? question "How do I write a basic YAML playbook to install software?"
 	A basic playbook is a YAML file that defines one or more \"plays\". Each play targets a specific host group and contains a list of tasks. To install software, you use a module like `apt` (for Ubuntu/Debian) or `yum` (for CentOS/RHEL), specifying the package name and ensuring the state is set to `present`.

??? question "What is the concept of idempotence and how can I verify it in Ansible?"
 	Idempotence is the property where an operation can be applied multiple times without changing the result beyond the initial application. In Ansible, if a system is already in the desired state, Ansible will not make any changes. You can verify this by running the same playbook twice; the second run should report `changed=0` for all tasks.

??? question "How do handlers manage service restarts based on configuration changes?"
 	Handlers are special tasks that are only executed if they are \"notified\" by another task using the `notify` keyword. This is typically used when a configuration file is updated (e.g., via the `template` module); the task notifies the handler to restart the service, ensuring the service is only restarted when a change actually occurs, rather than on every playbook run.

??? question "How do I distinguish between packaging (Docker), orchestration (Kubernetes), and provisioning (Ansible)?"
    **Packaging** (Docker) focuses on bundling an application and its dependencies into a portable container. **Orchestration** (Kubernetes) manages the deployment, scaling, and networking of those containers across a cluster. **Provisioning** (Ansible) handles the setup of the underlying servers, operating systems, and network settings that allow the orchestration layer to run.

??? question "What does 'bootstrapping a node' mean in a DevOps context?"
    Bootstrapping a node is the process of taking a "vanilla" or raw virtual machine and installing the necessary OS dependencies, performing security hardening, and setting up the container runtime (like containerd) so that the node can successfully join a Kubernetes cluster.

??? question "What are three tasks that still require Ansible even if the application is containerized?"
    1. **Provisioning raw VMs**: Setting up the base OS on AWS, GCP, or Azure.
    2. **Managing non-containerized infrastructure**: Configuring physical load balancers, external databases, or storage arrays.
    3. **Day-2 Operations**: Performing OS-level maintenance like kernel updates, disk partitioning, or managing SSH access.

??? question "When does a managed service (like EKS, GKE, or AKS) remove the need for manual provisioning?"
    Managed services remove the need for manual provisioning because the cloud provider manages the underlying worker nodes' operating system, security patches, and container runtime. The user interacts with the Kubernetes API, and the provider handles the "bootstrapping" and maintenance of the nodes.

## Assignments

!!! note "Assignment 1: Basic Web Server"
 	Set up a virtual machine and write an Ansible playbook to install Nginx. Ensure the playbook is idempotent and that you can verify the installation by visiting the server's IP in a browser.

!!! note "Assignment 2: User and Security Management"
		Create a playbook that performs the following on a target VM:
		1. Creates a new system user named `devops_user`.
		2. Adds the user to the `sudo` group.
		3. Copies a public SSH key to the user's `authorized_keys` file.
		4. Ensures the SSH service is running.

!!! note "Assignment 3: Multi-Service Deployment"
 	Develop a playbook that installs both a database (e.g., PostgreSQL) and a web application. Use a handler to ensure the web application restarts only after the database configuration is successfully updated.

!!! note "Assignment 4: Infrastructure Audit"
    Look at a hypothetical architecture consisting of: an AWS VPC, three EC2 instances running a K8s cluster, an external RDS database, and an S3 bucket. Identify which parts of this architecture would be managed by Terraform, which by Ansible, and which by Kubernetes.

!!! note "Assignment 5: Bootstrapping Workflow"
    Describe the sequence of events required to take a "vanilla" Ubuntu VM and turn it into a Kubernetes worker node. Which of these steps are "provisioning" (Ansible) and which are "orchestration" (Kubernetes)?

!!! note "Assignment 6: Managed vs. Self-Managed"
    Compare the operational overhead of managing a K8s cluster via Kubespray (Ansible) versus using Google GKE. List two advantages and two disadvantages of each approach.

## References

- Ansible Official Documentation: [docs.ansible.com](http://docs.ansible.com)
- Ansible Module Index: [modules_by_category](http://docs.ansible.com/modules_by_category.html)

---

## What's Next?

With infrastructure and configuration managed, it's time to look at how to scale this to an enterprise level. Explore **Enterprise Configuration Management with Puppet** to see the pull-based model in action.

Visit the [Local Lab](local-lab.md) for instructions on how to run Ansible locally.
