# Orchestrating Multi-VM Architectures with OpenStack Heat

!!! info "Learning Objectives"

    By the end of this lab, students will be able to:

    1. Understand the concept of **Infrastructure as Code (IaC)** using OpenStack Heat.
    2. Create a **Heat Orchestration Template (HOT)** to deploy a multi-tier architecture.
    3. Manage the full lifecycle of a "stack" (Create, Update, Delete) using the OpenStack CLI.
    4. Implement resource dependencies (e.g., ensuring security groups exist before servers are launched).
    5. Compare imperative deployment (running individual commands) with declarative orchestration.

---

## Overview

In the previous lab, we manually created servers, security groups, and floating IPs. While this is great for learning, it is error-prone and difficult to reproduce. **OpenStack Heat** allows us to define our entire infrastructure in a single YAML file.

Instead of running 20 separate commands, we define a **Stack**. A stack is a collection of resources that are managed as a single unit.

This contrasts the experience from the 

* [comandline only management](/section/cloud/jetstream/jetstream-multi.md)

*Figure: The diagram of the multiple VM example*

![The diagram of the multiple VM example](images/jetstream-multi.png)

### Architecture to be Orchestrated

We will deploy the same architecture as the manual lab:
1. **Two-Tier Web-DB**: A public web server (`web01`) and a private database server (`db01`).
2. **AI/Data Cluster**: A scheduler node (`scheduler`) and multiple worker nodes (`worker01`, `worker02`).

---

## 1. The Heat Orchestration Template (HOT)

Create a file named `multi-vm.yaml` on your local machine. This template defines the desired state of your infrastructure.

```yaml
heat_template_version: 2018-08-31

description: Template for a multi-tier Web/DB and AI Cluster architecture.

parameters:
  image:
    type: string
    description: Image to use for all servers.
    default: Featured-Ubuntu-24.04
  flavor:
    type: string
    description: Flavor to use for all servers.
    default: m1.medium
  key_name:
    type: string
    description: SSH keypair name.
    default: jetstream-demo

resources:
  # --- SECURITY GROUPS ---
  web_sg:
    type: OS::Nova::SecurityGroup
    properties:
      name: web-sg-heat
      rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: 0.0.0.0/0
        - protocol: tcp
          port_range_min: 80
          port_range_max: 80
          remote_ip_prefix: 0.0.0.0/0
        - protocol: tcp
          port_range_min: 443
          port_range_max: 443
          remote_ip_prefix: 0.0.0.0/0

  db_sg:
    type: OS::Nova::SecurityGroup
    properties:
      name: db-sg-heat
      rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_group: { get_resource: web_sg }
        - protocol: tcp
          port_range_min: 3306
          port_range_max: 3306
          remote_group: { get_resource: web_sg }

  cluster_sg:
    type: OS::Nova::SecurityGroup
    properties:
      name: cluster-sg-heat
      rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: 0.0.0.0/0
        - protocol: all
          remote_group: { get_resource: cluster_sg }


  # --- SERVERS ---
  web01:
    type: OS::Nova::Server
    properties:
      name: web01-heat
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      security_groups: [{ get_resource: web_sg }]
      networks: [{ net: private-net }]

  db01:
    type: OS::Nova::Server
    properties:
      name: db01-heat
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      security_groups: [{ get_resource: db_sg }]
      networks: [{ net: private-net }]

  scheduler:
    type: OS::Nova::Server
    properties:
      name: scheduler-heat
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      security_groups: [{ get_resource: cluster_sg }]
      networks: [{ net: private-net }]

  worker01:
    type: OS::Nova::Server
    properties:
      name: worker01-heat
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      security_groups: [{ get_resource: cluster_sg }]
      networks: [{ net: private-net }]

  worker02:
    type: OS::Nova::Server
    properties:
      name: worker02-heat
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      security_groups: [{ get_resource: cluster_sg }]
      networks: [{ net: private-net }]

  # --- FLOATING IPS ---
  web_float_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: public

  web_float_ip_assoc:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floating_ip: { get_resource: web_float_ip }
      port: { get_attr: [web01, interfaces, 0, port] }

  scheduler_float_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: public

  scheduler_float_ip_assoc:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floating_ip: { get_resource: scheduler_float_ip }
      port: { get_attr: [scheduler, interfaces, 0, port] }

outputs:
  web_ip:
    description: Public IP of the web server
    value: { get_attr: [web_float_ip, floating_ip_address] }
  scheduler_ip:
    description: Public IP of the scheduler
    value: { get_attr: [scheduler_float_ip, floating_ip_address] }
```


## 2. Deploying the Stack

### 2.1 Creating the Stack
Once you have saved the `multi-vm.yaml` file, use the OpenStack CLI to create the stack.

```bash
openstack stack create -t multi-vm.yaml jetstream-multi-stack
```

### 2.2 Monitoring Deployment
Heat creates resources in parallel where possible, but respects dependencies (e.g., it will not create `web01` until `web_sg` is ready). You can monitor the progress:

```bash
openstack stack list
openstack stack resource list jetstream-multi-stack
```

### 2.3 Retrieving Outputs
Instead of searching for IPs manually, Heat provides the outputs we defined in the template:

```bash
openstack stack output show jetstream-multi-stack
```

---

## 3. Lifecycle Management

### 3.1 Updating the Infrastructure
If you want to add a third worker (`worker03`), you don't need to run more commands. Simply:
1. Edit `multi-vm.yaml` and add the `worker03` resource.
2. Update the stack:
   ```bash
   openstack stack update -t multi-vm.yaml jetstream-multi-stack
   ```
Heat will detect that only one server needs to be added and will leave the others untouched.

### 3.2 Tearing Down the Infrastructure
To delete everything—servers, security groups, and floating IPs—in one command:

```bash
openstack stack delete jetstream-multi-stack
```

---

## 4. Imperative vs. Declarative: Comparison

| Feature | Imperative (Manual CLI) | Declarative (Heat) |
| :--- | :--- | :--- |
| **Process** | Run a sequence of commands | Define the final state in YAML |
| **Error Handling** | If command 5 fails, you must clean up 1-4 | Heat handles rollbacks automatically |
| **Reproducibility** | Hard (must re-run script/commands) | Easy (reuse the `.yaml` file) |
| **Cleanup** | Must delete resources in reverse order | One command: `stack delete` |
| **Updates** | Manual addition/deletion of resources | Update template $\rightarrow$ `stack update` |

---

## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is a 'Stack' in OpenStack Heat?"
    A stack is a collection of OpenStack resources (servers, networks, security groups) managed as a single unit via a template.

??? question "How does Heat handle dependencies between resources?"
    By using the `get_resource` or `get_attr` functions, Heat automatically determines the order of creation. For example, if a server references a security group, Heat ensures the group is created first.

??? question "What is the benefit of using 'outputs' in a HOT template?"
    Outputs allow you to programmatically retrieve critical information (like Floating IPs) immediately after deployment without having to query individual resources.

??? question "If you change the flavor of a server in the template and update the stack, what happens?"
    Depending on the resource, Heat will either modify the existing server or delete and recreate it to match the new specification.
