# Automating Infrastructure with Ansible

!!! info "Learning Objectives"
    - Define Ansible and its role in the DevOps ecosystem.
    - Install and configure Ansible for remote server management.
    - Create and execute Ansible Playbooks using YAML syntax.
    - Understand key Ansible concepts: Modules, Tasks, Handlers, and Inventories.
    - Implement an automated deployment of a service (e.g., Apache or MariaDB).

Managing dozens or hundreds of servers manually via SSH is inefficient and error-prone. When a system administrator has to run the same sequence of commands on fifty different machines, the risk of a typo or a missed step increases exponentially. Ansible provides a way to automate these tasks in a scalable, consistent, and reliable manner.

Ansible is an open-source IT automation engine that allows you to manage and configure compute resources. Unlike many other automation tools, Ansible is "agentless," meaning you do not need to install any special software on the target nodes; it communicates over standard SSH.

!!! info "Why this matters"
    In a professional DevOps pipeline, "Infrastructure as Code" (IaC) is a requirement. Ansible allows you to treat your server configurations as code, which can be version-controlled in Git, reviewed by peers, and tested in staging before being applied to production. This eliminates "configuration drift" and ensures that every server in a cluster is configured identically.

## Core Capabilities of Ansible

Ansible is versatile and can be used across the entire software delivery lifecycle:

- **Provisioning**: Setting up the base virtual machines or cloud instances that form your infrastructure.
- **Configuration Management**: Changing the state of the OS, installing packages, managing users, and implementing security policies.
- **Service Management**: Starting, stopping, or restarting services and managing system updates.
- **Application Deployment**: Automating the rollout of application code in a way that integrates with CI/CD strategies.

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
    One of Ansible's most powerful features is **idempotence**. If you run the same playbook a second time, Ansible will detect that Apache is already installed and will report `ok` instead of `changed`. This allows you to run playbooks frequently to ensure servers haven't drifted from their intended configuration.

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

## Key Ansible Terminology

To master Ansible, you must understand these core concepts:

- **Module**: A small program that Ansible pushes to the target node to execute a specific task (e.g., `apt`, `copy`, `service`).
- **Task**: The smallest unit of action in a playbook; it combines a module with specific arguments.
- **Handler**: A task that is triggered by a `notify` statement, typically used for restarting services after a config change.
- **Playbook**: A YAML file containing one or more "plays" (groups of tasks targeted at specific hosts).
- **Inventory**: A list of managed nodes, often organized into groups.

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

!!! note "Exercise 1: Basic Web Server"
    Set up a virtual machine and write an Ansible playbook to install Nginx. Ensure the playbook is idempotent and that you can verify the installation by visiting the server's IP in a browser.

!!! note "Exercise 2: User and Security Management"
    Create a playbook that performs the following on a target VM:
    1. Creates a new system user named `devops_user`.
    2. Adds the user to the `sudo` group.
    3. Copies a public SSH key to the user's `authorized_keys` file.
    4. Ensures the SSH service is running.

!!! note "Exercise 3: Multi-Service Deployment"
    Develop a playbook that installs both a database (e.g., PostgreSQL) and a web application. Use a handler to ensure the web application restarts only after the database configuration is successfully updated.

## References

- Ansible Official Documentation: [docs.ansible.com](http://docs.ansible.com)
- Ansible Module Index: [modules_by_category](http://docs.ansible.com/modules_by_category.html)

---

## Appendix: Local Deployment of the Course Site

### 0. Clone the Repository
Before running the automation, clone the course repository to your local machine:

```bash
git clone https://github.com/cloudmesh-ai/cloudmesh-ai-lecture.git
cd cloudmesh-ai-lecture
```


As a practical exercise in "Localhost Automation," you can use Ansible to set up the environment and launch this very lecture site on your own machine. This demonstrates how Ansible can be used not just for remote servers, but for standardizing local development environments.

### 1. Local Inventory
Since we are targeting the machine we are currently on, we use a special local inventory. Create a file named `local_inventory` with the following content:

```ini
[local]
localhost ansible_connection=local
```

### 2. The Deployment Playbook
Create a playbook named `deploy_site.yml`. This playbook ensures that all required Python dependencies for the MkDocs site are installed and then launches the server in the background.

```yaml
---
- hosts: local
  become: yes
  tasks:
    - name: Update apt cache
      apt:
        update_cache: yes

    - name: Install Python and Pip
      apt:
        name: 
          - python3
          - python3-pip
        state: present

    - name: Install MkDocs and required plugins
      pip:
        name: 
          - mkdocs-material
          - mkdocs-video
          - mkdocs-slides
          - mkdocs-caption
          - mkdocs-blog
          - pymdown-extensions
        state: present
        
    - name: Start MkDocs server on port 8000
      shell: "nohup mkdocs serve -a 0.0.0.0:8000 > mkdocs.log 2>&1 &"
      async: 10
      poll: 0

    - name: Open the browser to view the site
      shell: "open http://localhost:8000"
      become: no # 'open' command should be run as the regular user, not root
```

### 3. Execution
Run the following command from the root of the `cloudmesh-ai-lecture` directory:

```bash
ansible-playbook -i local_inventory deploy_site.yml
```

### What happens under the hood?
1. **`ansible_connection=local`**: This tells Ansible to bypass SSH and execute commands directly on the local shell.
2. **`async: 10, poll: 0`**: Because `mkdocs serve` is a blocking process (it stays open to serve requests), we tell Ansible to launch it as an asynchronous task and not wait for it to finish.
3. **`nohup`**: Ensures that the server continues to run even after the Ansible session ends.
4. **`become: no`**: We switch back to the regular user for the `open` command so the browser launches in your user session rather than as the root user.


### 4. Alternative: Using a Makefile for Local Deployment

While Ansible is powerful for orchestration, for simple local tasks, a `Makefile` is often the industry standard. It provides a short, memorable interface for complex shell commands.

Create a file named `Makefile` in the root of the project:

```makefile
PORT=8000
URL=http://localhost:$(PORT)

.PHONY: install serve open all clean

# Install all required Python dependencies
install:
	pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions

# Start the MkDocs server in the background
serve:
	nohup mkdocs serve -a 0.0.0.0:$(PORT) > mkdocs.log 2>&1 &
	@echo "Server started in background on $(URL)"

# Open the site in the default browser
open:
	open $(URL)

# Complete setup: Install, Serve, and Open
all: install serve open

# Stop the server and clean logs
clean:
	pkill -f "mkdocs serve"
	rm -f mkdocs.log
```

#### Execution
To deploy and view the site in one go, simply run:

```bash
make all
```

#### Ansible vs. Makefile: Which one to use?

| Feature | Ansible | Makefile |
| :--- | :--- | :--- |
| **Scope** | Cross-server orchestration | Local task automation |
| **Complexity** | High (YAML, Inventories) | Low (Shell scripts) |
| **Idempotency** | Built-in (checks state) | Manual (requires shell checks) |
| **Target** | Remote and Local | Local only |
| **Standard** | DevOps Industry Standard | Developer Build Standard |

For this local course site, the `Makefile` is faster and more lightweight, but the Ansible approach prepares you for managing a fleet of production servers.


# Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What does 'agentless' mean in the context of Ansible, and how does it communicate with target nodes?"
    Being "agentless" means that you do not need to install any special software or "agent" on the target servers being managed. Ansible communicates with these nodes using standard SSH (for Linux/Unix) or WinRM (for Windows).

??? question "Explain the concept of 'Infrastructure as Code' (IaC) and how Ansible helps prevent 'configuration drift'."
    IaC is the practice of managing and provisioning infrastructure through machine-readable definition files rather than manual hardware configuration or interactive configuration tools. Ansible prevents "configuration drift" (where servers slowly become different over time) by ensuring that the desired state defined in the playbook is applied consistently across all target machines.

??? question "What is an Ansible Inventory, and why are groups useful?"
    An inventory is a file (or a script) that lists the hosts and groups of hosts that Ansible can manage. Groups allow you to target sets of servers (e.g., `[webservers]`, `[dbservers]`) with a single command or playbook, rather than specifying every individual IP address.

??? question "Differentiate between an Ansible Module and an Ansible Playbook."
    A **Module** is a small, discrete piece of code that performs a specific task (e.g., `apt` for package management, `copy` for moving files). A **Playbook** is a YAML file that orchestrates multiple modules in a specific order to achieve a larger goal (e.g., "Install and Configure Apache").

??? question "What is the purpose of the `become: yes` directive in a playbook?"
    The `become: yes` directive tells Ansible to perform the task with privileged permissions (usually as the `root` user), which is necessary for tasks like installing packages or modifying system configuration files.

??? question "When should you use `async` and `poll` in an Ansible task?"
    Use `async` and `poll` when a task is expected to take a long time to complete or is a blocking process (like starting a server) that should not hang the Ansible connection. Setting `poll: 0` allows Ansible to fire off the task and move on immediately without waiting for a result.

??? question "Contrast Ansible with a `Makefile` for automation tasks."
    **Ansible** is designed for cross-server orchestration, focuses on idempotency (checking state before acting), and is an industry standard for DevOps. **Makefiles** are primarily used for local task automation (e.g., compiling code or local deployments) and generally rely on simple shell scripts without built-in state checking.

