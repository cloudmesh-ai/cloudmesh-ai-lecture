# Project-Wide FastAPI Deployment with Application-Level Access Control

In many organizational environments, services need to be accessible to all members of a project team without requiring each user to tunnel through a bastion host. This "Project-Wide Access" model leverages internal cloud networking to provide seamless connectivity for team members while maintaining a separate, restricted path for administrative access.

This chapter demonstrates how to deploy a FastAPI service that is accessible to all users within an OpenStack project (internally) and to the administrator (externally), while implementing an application-level "Deny List" to exclude specific users from accessing the API.

!!! info "Learning Objectives"
    After completing this chapter, you will be able to:
    - Implement application-level access control using FastAPI middleware.
    - Use Heat parameters to manage a dynamic "exclude list" of users.
    - Configure security groups to allow both project-wide internal access (via subnet CIDR) and specific external administrative access.
    - Deploy a service that balances broad accessibility with specific identity restrictions.

## 1. The Scenario

You are tasked with providing an API service for a project team. The requirements are:
1. **Internal Accessibility**: Any VM within the project's internal network must be able to reach the API.
2. **Administrative Access**: The administrator must be able to manage the service from a specific external public IP.
3. **Identity-Based Blocking**: Certain users (e.g., guest accounts or temporary contractors) must be blocked from the API at the application level, regardless of their network access.

This approach differs from the Bastion Host pattern by prioritizing internal ease-of-use over absolute isolation.

## 2. The Heat Template (`fastapi-project-access.yaml`)

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
                from fastapi import FastAPI, Header, HTTPException

                app = FastAPI()

                # Load excluded users from environment variable
                import os
                EXCLUDED_USERS = os.getenv("EXCLUDED_USERS", "").split(",")

                @app.get("/")
                async def read_root(x_user: str = Header(None)):
                    if x_user in EXCLUDED_USERS:
                        raise HTTPException(status_code=403, detail="User is excluded from this service")
                    
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

## 3. Deployment Steps

Follow these steps to deploy your Project-Wide FastAPI service.

### Step 1: Identify your Public IP
Since you need administrative access from your home or office, find your public IP address.

```bash
curl ifconfig.me
```

### Step 2: Validate the Template
Ensure the template is syntactically correct.

```bash
openstack stack template-validate -t fastapi-project-access.yaml
```

### Step 3: Create the Stack
Run the following command to create the stack. Replace `<YOUR_KEY>` with your primary OpenStack keypair, `<YOUR_PREFIX>` with a unique identifier, and `<YOUR_IP>` with the IP from Step 1.

```bash
openstack stack create -t fastapi-project-access.yaml \
    -P prefix=<YOUR_PREFIX> \
    -P my_public_ip=<YOUR_IP> \
    -P key_name=<YOUR_KEY> \
    -P excluded_users="guest,temp_user" \
    proj-fastapi-stack
```

### Step 4: Retrieve the API URL
Once the stack status is `CREATE_COMPLETE`, retrieve the public URL of your service.

```bash
openstack stack output show proj-fastapi-stack api_url
```

## 4. Verification and Testing

### Test as an Allowed User
Use a header to identify yourself as a user NOT in the exclude list:

```bash
curl -H "X-User: alice" $(openstack stack output show proj-fastapi-stack api_url -c output_value -f value)
```

*Expected output:* `{"Hello": "Project Member", "User": "alice", "Status": "Access Granted"}`

### Test as an Excluded User
Try to access the API as a user who is in the exclude list:

```bash
curl -H "X-User: guest" $(openstack stack output show proj-fastapi-stack api_url -c output_value -f value)
```

*Expected output:* A `403 Forbidden` response.

### Verify Internal Project Access
If you have another VM in the same project network, try calling the API using its **Private IP**. It should work because the security group allows the subnet CIDR.

---

!!! tip "Summary Checklist"
    - [ ] Subnet CIDR configured in the security group for internal project access.
    - [ ] Administrative public IP configured for external management access.
    - [ ] FastAPI application deployed with environment-based exclusion logic.
    - [ ] `excluded_users` parameter correctly passed to the Heat stack.
    - [ ] Verified `403 Forbidden` for users on the deny list.
    - [ ] Verified successful access for permitted users via the `X-User` header.

!!! note "Exercise 1: Basic Modification"
    Update the `excluded_users` parameter in the stack to add your own username and verify that you are now blocked from the API.

!!! note "Exercise 2: Network Adjustment"
    Modify the template to allow access to port 8000 from a second specific public IP (e.g., a colleague's IP) without opening it to the whole world.

!!! note "Exercise 3: Logic Inversion"
    Modify the FastAPI `main.py` code in the template to implement a "Permit List" (White List) instead of a "Deny List", where only users in the parameter list are allowed access.

## Further Reading & Resources

- OpenStack Neutron Security Groups: https://docs.openstack.org/neutron/latest/admin/config-security-groups.html
- FastAPI Header Parameters: https://fastapi.tiangolo.com/tutorial/header-params/
- OpenStack Heat Parameters: https://docs.openstack.org/heat/latest/

## Appendix: Handling Multiple Access Sources

In the basic example, we used a single parameter `my_public_ip` to restrict administrative access. In real-world scenarios, you may need to allow access from multiple specific IP addresses or different network ranges (CIDRs).

### Option 1: Adding Multiple Rules to the Security Group
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
          remote_ip_prefix: 203.0.113.10/32  # Additional Admin IP
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: { get_attr: [subnet, cidr] }
        - protocol: tcp
          port_range_min: 8000
          port_range_max: 8000
          remote_ip_prefix: 1.2.3.0/24       # Corporate Office CIDR
```

### Option 2: Using Independent Security Group Rule Resources

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

