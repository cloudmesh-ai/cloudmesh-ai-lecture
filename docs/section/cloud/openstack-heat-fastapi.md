# Secure Multi-User FastAPI Deployment on OpenStack with a Bastion Host and Heat

Deploying web services in a multi-tenant cloud environment requires balancing accessibility for project members with strict security hardening. Exposing backend application ports directly to the public internet invites brute-force attacks and unwanted scanning.

This tutorial guides you through creating a secure, production-grade architecture using **OpenStack Heat**. You will provision an isolated private network, a public **Bastion Host (Jump Box)** with restricted administrative access, a private **FastAPI backend server**, and automatic generation of local SSH configuration files for your team.

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Design a two-tier cloud architecture separating public ingress (Bastion) from private compute (Backend).
    - Write a complete OpenStack Heat Orchestration Template (HOT) handling subnets, routers, security groups, and cloud-init scripts.
    - Automate FastAPI and Uvicorn installation via cloud-init.
    - Secure internal backend communication so that SSH and API traffic are restricted strictly to the private subnet.
    - Use Heat outputs to dynamically generate local SSH configuration snippets for project members.

## 1. Architecture Overview

```text
[ Team Member ] --(SSH via Public FIP)--> [ Bastion Host (Public) ]
                                                     |
                                           (Private Network Tunnel)
                                                     |
                                                     v
                                          [ FastAPI Backend (Private) ]
                                          (Runs Uvicorn on Port 8000)
```

1. **Bastion Host**: The single entry point equipped with a Floating IP. Its security group blocks all incoming traffic except SSH from authorized administrative IP ranges.
2. **FastAPI Backend Server**: Resides entirely on a private internal network with **no public Floating IP**. It accepts SSH and application traffic exclusively from the Bastion / private subnet.
3. **SSH ProxyJump**: Team members tunnel seamlessly through the Bastion host to access the private backend and forward ports for local browser testing.

## 2. The Complete Heat Template (`secure-fastapi-stack.yaml`)

Save the following Heat Orchestration Template to your machine. It automates the entire infrastructure deployment.

```yaml
heat_template_version: 2018-03-02
description: Secure Multi-User FastAPI Deployment with Bastion Host Architecture

parameters:
  prefix:
    type: string
    description: Prefix for resource naming (e.g., "team-project")
    default: "fastapi-secure"
  allowed_admin_cidr:
    type: string
    description: Trusted CIDR block allowed to access the Bastion (e.g., campus VPN or office IP)
    default: "0.0.0.0/0"
  image:
    type: string
    description: Glance image name or ID (Ubuntu 22.04 recommended)
    default: "ubuntu-22.04"
  flavor:
    type: string
    description: Nova flavor for instances
    default: "m1.small"
  key_name:
    type: string
    description: OpenStack keypair name for initial node provisioning
  authorized_keys:
    type: string
    description: Newline-separated public SSH keys for project team members

resources:
  net:
    type: OS::Neutron::Net
    properties:
      name: { list_join: [ "-", [{ get_param: prefix }, "net"] ] }

  subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: net }
      cidr: 192.168.10.0/24
      ip_version: 4

  router:
    type: OS::Neutron::Router
    properties:
      name: { list_join: [ "-", [{ get_param: prefix }, "router"] ] }

  router_interface:
    type: OS::Neutron::RouterInterface
    properties:
      router_id: { get_resource: router }
      subnet_id: { get_resource: subnet }

  bastion_sg:
    type: OS::Neutron::SecurityGroup
    properties:
      name: { list_join: [ "-", [{ get_param: prefix }, "bastion-sg"] ] }
      security_group_rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: { get_param: allowed_admin_cidr }

  backend_sg:
    type: OS::Neutron::SecurityGroup
    properties:
      name: { list_join: [ "-", [{ get_param: prefix }, "backend-sg"] ] }
      security_group_rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: 192.168.10.0/24
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: 192.168.10.0/24

  bastion_server:
    type: OS::Nova::Server
    properties:
      name: { list_join: [ "-", [{ get_param: prefix }, "bastion"] ] }
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - network: { get_resource: net }
      security_groups:
        - { get_resource: bastion_sg }

  fastapi_server:
    type: OS::Nova::Server
    properties:
      name: { list_join: [ "-", [{ get_param: prefix }, "backend"] ] }
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - network: { get_resource: net }
      security_groups:
        - { get_resource: backend_sg }
      user_data:
        fn::join:
          - ""
          - - |
            #cloud-config
            package_upgrade: true
            packages:
              - python3-pip
              - python3-dev

            runcmd:
              - pip3 install fastapi uvicorn
              - |
                cat <<EOF > /home/ubuntu/main.py
                from fastapi import FastAPI
                app = FastAPI()

                @app.get("/")
                def read_root():
                    return {"Hello":"World","Status":"FastAPI running securely behind Bastion!"}
                EOF
              - |
                cat <<EOF > /etc/systemd/system/fastapi.service
                [Unit]
                Description=FastAPI Service
                After=network.target

                [Service]
                User=ubuntu
                WorkingDirectory=/home/ubuntu
                ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
                Restart=always

                [Install]
                WantedBy=multi-user.target
                EOF
              - systemctl daemon-reload
              - systemctl enable fastapi
              - systemctl start fastapi
              - mkdir -p /home/ubuntu/.ssh
          - "echo '"
          - { get_param: authorized_keys }
          - "' > /home/ubuntu/.ssh/authorized_keys\n"
          - "chown -R ubuntu:ubuntu /home/ubuntu/.ssh\n"
          - "chmod 700 /home/ubuntu/.ssh\n"
          - "chmod 600 /home/ubuntu/.ssh/authorized_keys\n"

  floating_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: public

  fip_assoc:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floating_ip: { get_resource: floating_ip }
      port_id: { get_attr: [bastion_server, first_interface] }

outputs:
  stack_access_summary:
    description: Copy-paste configuration instructions for project team members
    value:
      list_join:
        - ""
        - - "--- ADD TO YOUR LOCAL ~/.ssh/config ---\n"
          - "Host "
          - { get_param: prefix }
          - "-bastion\n    HostName "
          - { get_attr: [floating_ip, floating_ip_address] }
          - "\n    User ubuntu\n    IdentityFile ~/.ssh/your_key.pem\n\n"
          - "Host "
          - { get_param: prefix }
          - "-backend\n    HostName "
          - { get_attr: [fastapi_server, networks, { get_param: prefix }, 0] } 
          - "\n    User ubuntu\n    IdentityFile ~/.ssh/your_key.pem\n    ProxyJump "
          - { get_param: prefix }
          - "-bastion\n"
          - "----------------------------------------\n"
```

---

## 3. Deploying the Heat Stack

Execute the following OpenStack CLI command to deploy your infrastructure, passing your team's authorized keys as a parameter string:

```bash
openstack stack create \
  -t secure-fastapi-stack.yaml \
  --parameter key_name=my_admin_keypair \
  --parameter allowed_admin_cidr="128.143.0.0/16" \
  --parameter "authorized_keys=$(cat ~/.ssh/team_members.pub)" \
  secure-fastapi-deployment
```

Monitor the deployment progress until status changes to `CREATE_COMPLETE`:

```bash
openstack stack show secure-fastapi-deployment
```

---

## 4. Team Member Configuration & Access

Once deployment finishes, retrieve the generated SSH configuration block:

```bash
openstack stack output show secure-fastapi-deployment stack_access_summary -c output_value -f value
```

### Setting Up Local Workstations

Project members simply copy the output block and append it to their local `~/.ssh/config` file (located at `~/.ssh/config` on Linux/macOS or `C:\\Users\\Username\\.ssh\\config` on Windows), updating `IdentityFile` to point to their local private key.

### Interacting with the Private Backend

With the SSH config in place, team members gain seamless access:

1. **Forward Port Securely:** SSH Tunneling.
Run local port forwarding to connect port 8000 on the private backend directly to your local machine:

```bash
ssh -L 8000:localhost:8000 fastapi-secure-backend
```


2. **Query the FastAPI Service:** Validation.
Open a web browser or run `curl` locally on your workstation to verify the API response:

```bash
curl http://localhost:8000/
```

*Expected output:*

```json
{"Hello":"World","Status":"FastAPI running securely behind Bastion!"}
```

---

!!! tip "Summary Checklist"
    - [ ] Bastion host created with public Floating IP.
    - [ ] Backend server created with only internal network access.
    - [ ] Security groups restrict SSH access to the administrative CIDR.
    - [ ] FastAPI service installed and enabled via systemd.
    - [ ] `authorized_keys` injected into the backend server.
    - [ ] Team members configured `~/.ssh/config` with ProxyJump.

!!! note "Exercise 1: Basic Modification"
    Modify the template to add a second backend server (a replica) and ensure both are accessible through the same Bastion host.

!!! note "Exercise 2: Network Hardening"
    Change the `allowed_admin_cidr` to a specific IP instead of a range and verify that only that IP can SSH into the Bastion.

!!! note "Exercise 3: Advanced Configuration"
    Implement a load balancer (OS::Neutron::LBaaS) between the Bastion and the backend servers to distribute API traffic.

## Further Reading & Resources

- OpenStack Heat Documentation: https://docs.openstack.org/heat/latest/
- SSH ProxyJump Guide: https://www.ssh.com/academy/ssh/proxyjump
- FastAPI Documentation: https://fastapi.tiangolo.com/
