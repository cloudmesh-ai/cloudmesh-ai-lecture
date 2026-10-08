# Project-Wide FastAPI Deployment with Application-Level Access Control

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Implement application-level access control using FastAPI middleware.
    - Use Heat parameters to manage a dynamic "exclude list" of users.
    - Configure security groups to allow both project-wide internal access (via subnet CIDR) and specific external administrative access.
    - Analyze the security trade-offs between "Bastion" and "Project-Wide" access models.
    - Implement robust cloud-init scripts for automated service deployment and systemd integration.
    - Deploy a service that balances broad accessibility with specific identity restrictions.


!!! warning
    Jetstream does not have heat deployed.

## Overview

In many organizational environments, services need to be accessible to all members of a project team without requiring each user to tunnel through a bastion host. This "Project-Wide Access" model leverages internal cloud networking to provide seamless connectivity for team members while maintaining a separate, restricted path for administrative access.

### Network Traffic Patterns: North-South vs. East-West

To understand this deployment, one must distinguish between two primary traffic patterns:
- **North-South Traffic**: Traffic that enters or leaves the cloud environment (e.g., an administrator accessing the API from their home office via a Floating IP). This traffic is typically highly restricted and passes through a strict external firewall/security group.
- **East-West Traffic**: Traffic that moves laterally between resources within the same project or data center (e.g., a worker node in the project network calling the API). This traffic is typically more permissive to allow for efficient microservice communication.

This chapter demonstrates how to deploy a FastAPI service that is accessible to all users within an OpenStack project internally (East-West) and to the administrator externally (North-South), while implementing an application-level "Deny List" to exclude specific users from accessing the API.

## Core Sections

### The Scenario and Security Trade-offs

You are tasked with providing an API service for a project team. The requirements are:

1. **Internal Accessibility**: Any VM within the project's internal network must be able to reach the API.
2. **Administrative Access**: The administrator must be able to manage the service from a specific external public IP.
3. **Identity-Based Blocking**: Certain users (e.g., guest accounts or temporary contractors) must be blocked from the API at the application level, regardless of their network access.

#### Security Analysis: Project-Wide vs. Bastion Host
While the Bastion Host pattern is the "gold standard" for isolation, it introduces significant friction for internal team members.

| Aspect | Bastion Host Pattern | Project-Wide Access Pattern |
| :--- | :--- | :--- |
| **Access Path** | User $\rightarrow$ Bastion $\rightarrow$ Service | User $\rightarrow$ Service (Internal) |
| **Friction** | High (SSH Tunneling required) | Low (Direct internal connectivity) |
| **Attack Surface** | Small (Only Bastion is exposed) | Medium (Internal network is trusted) |
| **Management** | High (Bastion must be maintained) | Low (Relies on Neutron Security Groups) |
| **Primary Risk** | Bastion becomes a single point of failure | Lateral movement if one internal VM is breached |

### The Heat Template (`fastapi-project-access.yaml`)

The following template provisions the network, security groups for hybrid access, and a FastAPI application that reads an exclusion list from its environment.

```yaml
heat_template_version: 2018-03-02
description: FastAPI with Project-Wide Access, External Admin Access, and Exclude List

parameters:
  prefix:
    type: string
    description: Prefix for resource names
  my_public_ip:
    type: string
    description: Your public IP address for external administrative access
  image:
    type: string
    default: ubuntu-20.04
  flavor:
    type: string
    default: m1.small
  key_name:
    type: string
    description: SSH keypair for administrative access
  excluded_users:
    type: string
    default: "guest,temp_user"
    description: Comma-separated list of usernames to exclude from accessing the API

resources:
  net:
    type: OS::Neutron::Net
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-proj-net" ] }

  subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: net }
      cidr: 192.168.20.0/24
      ip_version: 4

  secgroup:
    type: OS::Neutron::SecurityGroup
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-proj-sg" ] }
      security_group_rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: { get_param: my_public_ip }
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: { get_attr: [subnet, cidr] }
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: { get_param: my_public_ip }

  server:
    type: OS::Nova::Server
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-proj-api-server" ] }
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - network: { get_resource: net }
      security_groups:
        - { get_resource: secgroup }
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
                from fastapi import FastAPI, Header, HTTPException, Request
                from fastapi.middleware.base import BaseHTTPMiddleware
                import os

                app = FastAPI()
                EXCLUDED_USERS = os.getenv("EXCLUDED_USERS", "").split(",")

                class AccessControlMiddleware(BaseHTTPMiddleware):
                    async def dispatch(self, request: Request, call_next):
                        user = request.headers.get("X-User")
                        if user in EXCLUDED_USERS:
                            from fastapi.responses import JSONResponse
                            return JSONResponse(
                                status_code=403, 
                                content={"detail": "User is excluded from this service"}
                            )
                        return await call_next(request)

                app.add_middleware(AccessControlMiddleware)

                @app.get("/")
                async def read_root(x_user: str = Header(None)):
                    return {"Hello": "Project Member", "User": x_user, "Status": "Access Granted"}
                EOF
              - |
                cat <<EOF > /etc/systemd/system/fastapi.service
                [Unit]
                Description=FastAPI Project Access Service
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
          - "export EXCLUDED_USERS="
          - { get_param: excluded_users }
          - " && systemctl restart fastapi"

  floating_ip:
    type: OS::Neutron::FloatingIP
    properties:
      floating_network: public

  fip_assoc:
    type: OS::Neutron::FloatingIPAssociation
    properties:
      floating_ip: { get_resource: floating_ip }
      port_id: { get_attr: [server, first_interface] }

outputs:
  api_url:
    description: URL of the FastAPI service
    value: { "fn::concat": [ "http://", { get_attr: [floating_ip, floating_ip_address] }, ":8000" ] }
```

#### Deep Dive: Security Group Logic
The `secgroup` resource implements the hybrid access model using two different `remote_ip_prefix` strategies:
1. **The Admin Path**: Rules for port 22 (SSH) and port 8000 (API) are restricted to `my_public_ip`. This ensures that only the administrator's specific external IP can manage the server or access the API from the public internet.
2. **The Project Path**: A rule for port 8000 is mapped to `{ get_attr: [subnet, cidr] }`. This tells OpenStack to allow any traffic originating from the `192.168.20.0/24` subnet. This is the mechanism that enables "Project-Wide Access" for internal VMs.

#### Deep Dive: Cloud-Init and Systemd Integration
The `user_data` section uses `cloud-config` to bootstrap the server. 
- **Package Installation**: It installs `python3-pip` and `python3-dev` to ensure the environment can build any C-extensions required by Python libraries.
- **Service Persistence**: Instead of running `uvicorn` in a background shell (which would die if the session ended), the script creates a proper `systemd` service unit file at `/etc/systemd/system/fastapi.service`. This ensures the API starts automatically on boot and restarts if it crashes.
- **Dynamic Configuration**: The `EXCLUDED_USERS` environment variable is injected via the Heat template, allowing the administrator to change the access list without modifying the application code.

### Deployment Steps

Follow these steps to deploy your Project-Wide FastAPI service.

#### Step 1: Identify your Public IP
Since you need administrative access from your home or office, find your public IP address.

```bash
curl ifconfig.me
```

#### Step 2: Validate the Template
Ensure the template is syntactically correct.

```bash
openstack stack template-validate -t fastapi-project-access.yaml
```

#### Step 3: Create the Stack
Run the following command to create the stack. Replace `<YOUR_KEY>` with your primary OpenStack keypair, `<YOUR_PREFIX>` with a unique identifier, and `<YOUR_IP>` with the IP from Step 1.

```bash
openstack stack create -t fastapi-project-access.yaml \
    -P prefix=<YOUR_PREFIX> \
    -P my_public_ip=<YOUR_IP> \
    -P key_name=<YOUR_KEY> \
    -P excluded_users="guest,temp_user" \
    proj-fastapi-stack
```

#### Step 4: Retrieve the API URL
Once the stack status is `CREATE_COMPLETE`, retrieve the public URL of your service.

```bash
openstack stack output show proj-fastapi-stack api_url
```

### Verification and Testing

#### Test as an Allowed User
Use a header to identify yourself as a user NOT in the exclude list:

```bash
curl -H "X-User: alice" $(openstack stack output show proj-fastapi-stack api_url -c output_value -f value)
```

Expected output: `{"Hello": "Project Member", "User": "alice", "Status": "Access Granted"}`

#### Test as an Excluded User
Try to access the API as a user who is in the exclude list:

```bash
curl -H "X-User: guest" $(openstack stack output show proj-fastapi-stack api_url -c output_value -f value)
```

Expected output: A `403 Forbidden` response.

#### Verify Internal Project Access
If you have another VM in the same project network, try calling the API using its Private IP. It should work because the security group allows the subnet CIDR.

### Application-Level Security Analysis

The current implementation relies on the `X-User` header for identity. This is a **demonstration pattern** and is not secure for production.

!!! warning "Security Risk: Header Spoofing"
    In this example, any user who knows the header name `X-User` can spoof their identity by simply changing the header value (e.g., `curl -H "X-User: admin"`). In a production environment, identity must be verified using:
    - **JWT (JSON Web Tokens)**: A signed token that the user cannot modify without the secret key.
    - **OAuth2 / OpenID Connect**: Integration with a central identity provider (like Keycloak or Okta).
    - **mTLS (Mutual TLS)**: Verifying the client's certificate at the network layer.

### Troubleshooting Common Issues

If the service is not responding, check the following:
- **Security Group Rules**: Run `openstack security group rule list <group_id>` to verify the CIDR and public IP rules are correctly applied.
- **Service Status**: SSH into the server and run `sudo systemctl status fastapi`. If it is inactive, check the logs with `sudo journalctl -u fastapi`.
- **Sudo Permissions**: If `runcmd` fails, ensure the `ubuntu` user has the necessary permissions to run `systemctl` commands.
- **Cloud-Init Logs**: If the server boots but the app isn't installed, check `/var/log/cloud-init-output.log` for installation errors.

### Handling Multiple Access Sources

In the basic example, we used a single parameter `my_public_ip` to restrict administrative access. In real-world scenarios, you may need to allow access from multiple specific IP addresses or different network ranges (CIDRs).

#### Option 1: Adding Multiple Rules to the Security Group
You can add multiple rule entries within the `security_group_rules` list in the `OS::Neutron::SecurityGroup` resource.

```yaml
  secgroup:
    type: OS::Neutron::SecurityGroup
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-proj-sg" ] }
      security_group_rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: { get_param: my_public_ip }
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: 203.0.113.10/32
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: { get_attr: [subnet, cidr] }
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: 1.2.3.0/24
```

#### Option 2: Using Independent Security Group Rule Resources
For better maintainability or when rules are added dynamically, use the `OS::Neutron::SecurityGroupRule` resource. This allows you to define rules separately from the group definition.

```yaml
  admin_ssh_rule:
    type: OS::Neutron::SecurityGroupRule
    properties:
      security_group_id: { get_resource: secgroup }
      direction: ingress
      protocol: tcp
      port_range_min: 22
      port_range_max: 22
      remote_ip_prefix: { get_param: my_public_ip }

  colleague_ssh_rule:
    type: OS::Neutron::SecurityGroupRule
    properties:
      security_group_id: { get_resource: secgroup }
      direction: ingress
      protocol: tcp
      port_range_min: 22
      port_range_max: 22
      remote_ip_prefix: 203.0.113.50/32
```

## Summary Checklist

- [ ] Analyze the trade-offs between Project-Wide and Bastion Host access models.
- [ ] Configure the `OS::Neutron::SecurityGroup` to allow both internal CIDR and external admin IP.
- [ ] Implement a FastAPI `BaseHTTPMiddleware` for identity-based access control.
- [ ] Use a `systemd` unit file to ensure the API service is persistent across reboots.
- [ ] Pass dynamic user exclusion lists via Heat parameters and environment variables.
- [ ] Verify the "Deny List" logic using the `X-User` header.
- [ ] Implement a secure cleanup process for ephemeral resources.

## Assignments

!!! note "Assignment.1: Basic Modification"
    Update the `excluded_users` parameter in the stack to add your own username and verify that you are now blocked from the API.

    ??? tip "Solution: Basic Modification"
        Update the stack using `openstack stack update -P excluded_users="your_user,guest,temp_user" proj-fastapi-stack`. Verify the block with a curl request using your username in the `X-User` header.

!!! note "Assignment.2: Network Adjustment"
    Modify the template to allow access to port 8000 from a second specific public IP (e.g., a colleague's IP) without opening it to the whole world.

    ??? tip "Solution: Network Adjustment"
        Add a second entry to the `security_group_rules` list in the `OS::Neutron::SecurityGroup` resource, specifying the colleague's IP in the `remote_ip_prefix` field for port 8000.

!!! note "Assignment.3: Logic Inversion"
    Modify the FastAPI `main.py` code in the template to implement a "Permit List" (White List) instead of a "Deny List", where only users in the parameter list are allowed access.

    ??? tip "Solution: Logic Inversion"
        Change the logic in `main.py` from `if x_user in EXCLUDED_USERS: raise HTTPException` to `if x_user not in PERMITTED_USERS: raise HTTPException`.

!!! note "Assignment.4: Token-Based Hardening"
    Instead of relying on the `X-User` header, modify the FastAPI code to require a simple static token passed in the `Authorization` header (e.g., `Authorization: Bearer my-secret-token`).

    ??? tip "Solution: Token-Based Hardening"
        Implement a dependency in FastAPI that checks if the `Authorization` header matches a secret stored in an environment variable. Return `401 Unauthorized` if the token is missing or incorrect.

## References

- OpenStack Neutron Security Groups: [docs.openstack.org/neutron/latest/admin/config-security-groups.html](https://docs.openstack.org/neutron/latest/admin/config-security-groups.html)
- FastAPI Middleware Documentation: [fastapi.tiangolo.com/tutorial/middleware/](https://fastapi.tiangolo.com/tutorial/middleware/)
- OpenStack Heat Parameters: [docs.openstack.org/heat/latest/](https://docs.openstack.org/heat/latest/)

## Self-Evaluation

??? note "What is the primary benefit of using a subnet CIDR in a security group rule for internal access?"
    It allows any VM launched within the same project network to communicate with the service without needing to manage individual IP addresses for every single internal node, simplifying internal connectivity for project members.

??? note "How does the FastAPI application handle the 'Exclude List' provided by the Heat template?"
    The Heat template passes the comma-separated list of users as an environment variable (`EXCLUDED_USERS`). The FastAPI application reads this variable at startup, splits it into a Python list, and uses a `BaseHTTPMiddleware` to check the `X-User` request header against this list before the request reaches the endpoint.

??? note "Why is it critical to use a specific public IP for administrative access rather than opening port 22 to the world?"
    Opening port 22 (SSH) to `0.0.0.0/0` exposes the server to constant brute-force attacks and vulnerability scanning from the entire internet. Restricting access to a known administrative IP drastically reduces the attack surface.

??? note "What is the security risk associated with using the `X-User` header for identity verification?"
    The `X-User` header is sent in plain text and can be easily spoofed by any client. Anyone who knows the header name can impersonate any user, including the administrator. For production, cryptographic identities like JWTs or OIDC should be used.

??? note "How does the `systemd` service integration improve the reliability of the API deployment?"
    By using a `systemd` unit file, the API is managed by the OS init system. This provides automated startup on boot, automatic restarts upon failure (via `Restart=always`), and centralized logging via `journalctl`, which is far more robust than running a process in a background shell.
