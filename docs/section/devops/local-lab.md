# Local Lab: Deploying the Course Site Locally

This guide provides a collection of methods to deploy and serve the `cloudmesh-ai-lecture` site on your local machine. These examples demonstrate how different DevOps tools can be used to standardize local development environments, ensuring that every student is running the site in an identical configuration.

## 1. Local Deployment with Terraform (Docker)

While Terraform is typically used for cloud infrastructure, you can use the **Docker Provider** to automate the deployment of this site locally. This ensures that every student is running the site in the exact same containerized environment.

### Local Configuration

Create a file named `local_site.tf` with the following configuration:

```hcl
terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
      version = "~> 3.0.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "python_site" {
  name = "python:3.11-slim"
}

resource "docker_container" "site_server" {
  image = docker_image.python_site.image_id
  name = "cloudmesh-ai-site"
  
  ports {
    internal = 8000
    external = 8000
  }
  
  # We simulate the deployment by running the install and serve commands
  command = [
    "sh", "-c", 
    "pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions && mkdocs serve -a 0.0.0.0:8000"
  ]
  
  # Mount the current directory as a volume so changes are reflected in real-time
  volumes {
    host_path = "."
    container_path = "/app"
  }
  
  working_dir = "/app"
}

output "site_url" {
  value = "http://localhost:8000"
}
```

### Execution

Run the following commands to launch the site:

```bash
terraform init
terraform apply -auto-approve
```

Once the apply is complete, Terraform will output the URL. You can then open your browser and visit `http://localhost:8000`.

### Destruction

To stop the server and remove the container:

```bash
terraform destroy -auto-approve
```

### Why use Terraform for this?

Unlike a simple shell script, Terraform tracks the **state** of the container. If you change the port mapping in the `.tf` file and run `apply` again, Terraform will intelligently destroy and recreate the container to match the new configuration, ensuring your environment never drifts from the definition.

---

## 2. Local Deployment with Ansible

## Assignments

!!! note "Assignment: Localhost Automation"
    As a practical exercise in "Localhost Automation," you can use Ansible to set up the environment and launch this very lecture site on your own machine. This demonstrates how Ansible can be used not just for remote servers, but for standardizing local development environments.

### Local Inventory

Since we are targeting the machine we are currently on, we use a special local inventory. Create a file named `local_inventory` with the following content:

```ini
[local]
localhost ansible_connection=local
```

### The Deployment Playbook

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

### Execution

Run the following command from the root of the `cloudmesh-ai-lecture` directory:

```bash
ansible-playbook -i local_inventory deploy_site.yml
```

### What happens under the hood?

1. **`ansible_connection=local`**: This tells Ansible to bypass SSH and execute commands directly on the local shell.
2. **`async: 10, poll: 0`**: Because `mkdocs serve` is a blocking process, we tell Ansible to launch it as an asynchronous task and not wait for it to finish.
3. **`nohup`**: Ensures that the server continues to run even after the Ansible session ends.
4. **`become: no`**: We switch back to the regular user for the `open` command so the browser launches in your user session rather than as the root user.

---

## 3. Local Deployment with Puppet

Puppet is designed for "state enforcement." While it's typically used for thousands of servers, you can use it locally to ensure your development environment is always correctly configured to serve the course site.

### The Puppet Manifest

Create a file named `site.pp`. This manifest ensures that Python is installed, the required MkDocs plugins are present, and the server is running as a system service.

```puppet
# Ensure Python and Pip are installed

package { 'python3-pip':
  ensure => installed,
}

# Install MkDocs and Plugins using a shell command

exec { 'install_mkdocs_plugins':
  command => '/usr/bin/pip3 install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions',
  require => Package['python3-pip'],
}

# Define a systemd unit to run mkdocs serve in the background

file { '/etc/systemd/system/mkdocs.service':
  ensure => file,
  content => "
[Unit]
Description=MkDocs Course Site Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cloudmesh-ai-lecture
ExecStart=/usr/local/bin/mkdocs serve -a 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
",
}

# Ensure the service is started and enabled

service { 'mkdocs':
  ensure => running,
  enable => true,
  subscribe => File['/etc/systemd/system/mkdocs.service'],
}
```

### Execution

Run the manifest locally using the `puppet apply` command:

```bash
sudo puppet apply site.pp
```

Once applied, you can open your browser and visit `http://localhost:8000`.

### Why use Puppet for this?

The power of Puppet lies in **drift detection**. If you accidentally uninstall a plugin or stop the server, running `puppet apply` will immediately detect that the system is not in the "desired state" and will automatically reinstall the dependencies and restart the server, ensuring your environment is always stable.

---

## 4. Local Deployment with Jenkins

While Jenkins is usually a centralized server, you can use it to orchestrate local deployments by running a **Jenkins Agent** on your own machine. This allows you to use the same pipeline logic for your local development as you do for production.

### Local Deployment Pipeline

Create a `Jenkinsfile` in the root of the project. This pipeline uses a Declarative syntax to prepare the environment and launch the site.

```groovy
pipeline {
    agent any
    
    stages {
        stage('Environment Setup') {
            steps {
                echo 'Installing MkDocs and Plugins...'
                sh 'pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions'
            }
        }
        
        stage('Deploy and Serve') {
            steps {
                echo 'Launching Site on Port 8000...'
                // Use nohup to keep the server running after the job finishes
                sh 'nohup mkdocs serve -a 0.0.0.0:8000 > jenkins_mkdocs.log 2>&1 &'
            }
        }
        
        stage('Open Browser') {
            steps {
                echo 'Opening browser to http://localhost:8000'
                sh 'open http://localhost:8000 || xdg-open http://localhost:8000'
            }
        }
    }
    
    post {
        success {
            echo 'Site is now live at http://localhost:8000'
        }
    }
}
```

---

## 5. Local Deployment with CircleCI

CircleCI is a hosted platform, but you can simulate the deployment process locally using a **CircleCI Runner**. This allows you to test your CI configuration on your own machine before pushing it to GitHub.

### The Configuration

Create a `.circleci/config.yml` file in your project root. This configuration defines a job that prepares the environment and launches the site.

```yaml
version: 2.1

jobs:
  deploy_local:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install Dependencies
          command: pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions
      - run:
          name: Serve Site
          command: |
            nohup mkdocs serve -a 0.0.0.0:8000 > circleci_mkdocs.log 2>&1 &
            echo "Site is serving at http://localhost:8000"
      - run:
          name: Open Browser
          command: open http://localhost:8000 || xdg-open http://localhost:8000
```

### Execution with Local Runner

To execute this locally, you would use the CircleCI local CLI:

```bash
circleci local execute --job deploy_local
```

### Why use CircleCI for this?

CircleCI's strength is its **container-first approach**. By defining your deployment in a `config.yml`, you ensure that the environment (OS, Python version, and plugins) is identical regardless of whether the site is being served on your laptop or in a cloud-based preview environment.

---

## 6. Local Deployment with Travis CI

Travis CI is primarily a cloud-based CI service, but its "Configuration as Code" philosophy using `.travis.yml` can be applied to standardize the deployment of the `cloudmesh-ai-lecture` site. By defining the environment and execution steps in a YAML file, we ensure that the site is served identically regardless of the environment.

### The Travis Configuration

Create a `.travis.yml` file in the root of the project. This file defines the language, the installation phase for dependencies, and the script to launch the server.

```yaml
language: python
python:
  - "3.11"

# Install required MkDocs plugins and dependencies

install:
  - pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions

# Launch the server and open the browser

script:
  - nohup mkdocs serve -a 0.0.0.0:8000 > travis_mkdocs.log 2>&1 &
  - sleep 5 # Give the server a few seconds to start
  - open http://localhost:8000 || xdg-open http://localhost:8000
```

### Execution

While Travis CI usually triggers on a Git push, you can simulate the `install` and `script` phases locally by running the commands defined in the `.travis.yml` file:

```bash
# Simulate 'install' phase

pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions

# Simulate 'script' phase

nohup mkdocs serve -a 0.0.0.0:8000 > travis_mkdocs.log 2>&1
open http://localhost:8000

---

## What's Next?

Now that you have your local environment running, you can experiment with the playbooks and configurations described throughout this chapter. Return to the **[Master Index](/section/devops/devops.md)** to explore more advanced topics.
```

### Why use Travis CI for this?

Travis CI's power lies in its **transparent build process**. By documenting the deployment in `.travis.yml`, any contributor to the `cloudmesh-ai-lecture` project can immediately see exactly which dependencies are required to run the site locally, eliminating the "it works on my machine" problem.
