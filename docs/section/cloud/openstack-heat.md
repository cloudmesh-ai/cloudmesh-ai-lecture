# OpenStack Heat: Orchestration Engine for Cloud‑Native Applications

!!! info "Learning Objectives"
    After completing this chapter, you will be able to:
    - Understand the role of OpenStack Heat in Infrastructure‑as‑Code (IaC).
    - Define the relationship between templates, stacks, and resources.
    - Design and implement a Heat Orchestration Template (HOT) to deploy a multi-tier application.
    - Utilize intrinsic functions to create dynamic and reusable templates.
    - Manage the lifecycle of a stack, including creation, updating, and deletion.
    - Implement self-healing and auto-scaling architectures using Heat.

## Contextual Overview

Managing a modern cloud environment manually is error-prone and unscalable. Creating a network, defining subnets, launching multiple virtual machines, assigning floating IPs, and configuring security groups—all through a CLI or GUI—leads to "snowflake" environments where no two deployments are identical.

OpenStack Heat solves this by introducing **Infrastructure‑as‑Code (IaC)**. Instead of performing a sequence of actions, you define the *desired state* of your infrastructure in a declarative template. Heat then acts as the orchestration engine, calculating the dependencies between resources and communicating with other OpenStack services (Nova, Neutron, Cinder, etc.) to realize that state.

This approach ensures that your environment is repeatable, auditable, and version-controlled, allowing you to treat your infrastructure with the same rigor as your application code.

## Core Concepts

At its heart, Heat operates on a few fundamental primitives.

### Templates and Stacks

A **Template** is a declarative YAML (Heat Orchestration Template - HOT) or JSON file that serves as the blueprint of your infrastructure. A **Stack** is the actual instantiation of a template; when you "create a stack," Heat parses the template and creates the resources defined within it. By separating the blueprint from the instance, you can use the same template to deploy identical "Development," "Staging," and "Production" environments, eliminating "it works on my machine" infrastructure issues.

### Resources and Resource Plugins

A **Resource** is any OpenStack object (e.g., a server, a volume, or a security group) that Heat can manage. Heat interacts with these through **Resource Plugins**, which are Python classes that implement the CRUD (Create, Read, Update, Delete) logic for that specific resource type. This plugin-based architecture allows Heat to orchestrate not only core OpenStack services but also any external service that exposes a REST API, making it a universal orchestrator for the OpenStack ecosystem.

### Parameters and Outputs

**Parameters** allow you to pass values into a template at runtime (e.g., specifying the image name or the number of server instances), while **Outputs** allow a stack to export information (e.g., the public IP of a load balancer) to the user or to other stacks. This parameterization makes templates highly reusable across different projects or regions without requiring modifications to the template code itself.

!!! tip "Professional Tip: Template Reusability"
    Always use parameters for values that change between environments, such as `flavor`, `image`, and `key_pair`. Hard-coding these values makes your templates brittle and difficult to maintain.

---

## Template Anatomy

A Heat Orchestration Template (HOT) consists of several key sections.

### The Basic Structure

Every HOT file must start with the `heat_template_version`. This ensures compatibility as the Heat engine evolves.

```yaml
heat_template_version: 2018-03-02
description: A basic web server deployment

parameters:
  # Defined here to make the template reusable
  image_name:
    type: string
    default: ubuntu-20.04
    description: Name of the image to use for the server

resources:
  # The actual infrastructure components
  web_server:
    type: OS::Nova::Server
    properties:
      image: { get_param: image_name }
      flavor: m1.small
      key_name: my-key
```

### Intrinsic Functions

Intrinsic functions are the "logic" of HOT. They allow you to create dynamic relationships between resources.

- `{ get_param: name }`: Retrieves the value of a parameter.
- `{ get_resource: name }`: Returns the ID of a resource.
- `{ get_attr: [resource, attribute] }`: Retrieves a specific attribute of a resource (e.g., an IP address).
- `fn::concat`: Concatenates a list of strings into one.

!!! warning "Common Pitfall: Dependency Cycles"
    Be careful not to create circular dependencies. For example, Resource A cannot depend on Resource B if Resource B also depends on Resource A. Heat will fail to build the dependency graph and the stack creation will error out.

---

## Practical Implementation: Deploying a Web Tier

To understand Heat in practice, let's look at a complete scenario: deploying a web server with its own network and a floating IP for public access. To ensure our resources are easily distinguishable in a shared cloud environment, we will use a `prefix` parameter.

### The Scenario
We need a private network for the server to reside in, a security group to allow HTTP (port 80) and SSH (port 22) traffic, and a floating IP to make the server accessible from the internet.

### The Template (`web_tier.yaml`)

```yaml
heat_template_version: 2018-03-02
description: Complete Web Tier Deployment with Resource Prefixing

parameters:
  prefix:
    type: string
    description: Prefix for all resource names to avoid collisions (e.g., "user1")
  image:
    type: string
    default: ubuntu-20.04
  flavor:
    type: string
    default: m1.small
  key_name:
    type: string
    description: SSH keypair name for server access

resources:
  # 1. Create the Network
  net:
    type: OS::Neutron::Net
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-web-net" ] }

  # 2. Create the Subnet
  subnet:
    type: OS::Neutron::Subnet
    properties:
      network: { get_resource: net }
      cidr: 192.168.10.0/24
      ip_version: 4

  # 3. Create Security Group
  secgroup:
    type: OS::Neutron::SecurityGroup
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-web-sg" ] }
      description: Allow SSH and HTTP
      security_group_rules:
        - protocol: tcp
          port_range_min: 22
          port_range_max: 22
          remote_ip_prefix: 0.0.0.0/0
        - protocol: tcp
          port_range_min: 80
          port_range_max: 80
          remote_ip_prefix: 0.0.0.0/0

  # 4. Create the Compute Instance
  server:
    type: OS::Nova::Server
    properties:
      name: { "fn::concat": [ { "get_param": "prefix" }, "-web-server" ] }
      image: { get_param: image }
      flavor: { get_param: flavor }
      key_name: { get_param: key_name }
      networks:
        - network: { get_resource: net }
      security_groups:
        - { get_resource: secgroup }

  # 5. Create and Associate Floating IP
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
  web_ip:
    description: Public IP address of the web server
    value: { get_attr: [floating_ip, floating_ip_address] }
```

### Deployment Workflow

To deploy this infrastructure, follow these steps:

1. **Validate the template**: Ensure there are no syntax errors.
   ```bash
   openstack stack template-validate -t web_tier.yaml
   ```

2. **Create the stack**: Provide the required parameters, including your unique `prefix`.
   ```bash
   openstack stack create -t web_tier.yaml \
       -P prefix=my-unique-user \
       -P key_name=my-ssh-key \
       web-stack
   ```

3. **Monitor the status**: Wait for the state to reach `CREATE_COMPLETE`.
   ```bash
   openstack stack show web-stack
   ```

4. **Retrieve the output**: Get the public IP to access your server.
   ```bash
   openstack stack output show web-stack web_ip
   ```

---

## Advanced Orchestration Features

### Software Configuration and Deployment

Heat doesn't just create VMs; it can configure the software inside them using **OS::Heat::SoftwareConfig**, which defines the configuration (scripts, files, or Ansible playbooks) to be applied, and **OS::Heat::SoftwareDeployment**, which applies a `SoftwareConfig` to a specific server. This enables "Zero Touch Provisioning," allowing you to launch 100 servers and have Heat automatically install Nginx, configure the firewall, and join them to a database cluster without manual SSH intervention.

### Auto-Scaling

Heat integrates with OpenStack Ceilometer/Aodh to implement auto-scaling.
- **AutoScalingGroup**: Manages a group of identical resources.
- **ScalingPolicy**: Defines what happens when a scale event occurs (e.g., "add 2 servers").
- **ScalingTrigger**: Monitors a metric (e.g., CPU > 80%) and triggers the policy.

---

## Best Practices for Heat Templates

To maintain a production-grade infrastructure, adhere to these guidelines:

1. **Parameterize Everything**: Avoid hard-coding IDs or names. Use parameters for images, flavors, and network names, and use a `prefix` parameter to avoid naming collisions in shared clouds.
2. **Modularize with Nested Stacks**: For complex architectures, break your templates into smaller, reusable pieces (e.g., a `network.yaml` and an `app.yaml`) and use `OS::Heat::Stack` to nest them.
3. **Version Control**: Store your HOT templates in Git. This allows you to track changes to your infrastructure and roll back to previous versions if a deployment fails.
4. **Use Descriptive Outputs**: Name your outputs clearly so that other automated tools (like Jenkins or GitLab CI) can easily parse and use the values.

---

!!! tip "Summary Checklist"
    - [ ] Template version is specified (`heat_template_version`).
    - [ ] Environment-specific values are moved to the `parameters` section.
    - [ ] A `prefix` parameter is used for resource naming to avoid collisions.
    - [ ] Resource dependencies are handled via intrinsic functions (`get_resource`, `get_attr`).
    - [ ] Security groups are defined and associated with the compute instances.
    - [ ] Floating IPs are created and associated using `OS::Neutron::FloatingIPAssociation`.
    - [ ] Templates are validated using `openstack stack template-validate` before deployment.
    - [ ] All critical infrastructure outputs (like IPs) are defined in the `outputs` section.

## Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

    ??? question "What is the primary difference between a Template and a Stack in OpenStack Heat?"
        A template is the declarative blueprint (the YAML/JSON file) that describes the desired state, while a stack is the actual instantiation of that template in the cloud environment.

    ??? question "Which intrinsic function would you use to retrieve the IP address of a server created within the same template?"
        You would use `{ get_attr: [server_resource_name, fixed_ips] }` or a similar attribute depending on the specific resource property.

    ??? question "Why is it recommended to use parameters instead of hard-coding values in a HOT file?"
        Parameters make templates reusable across different environments (Dev, Test, Prod) without needing to modify the template code, reducing the risk of manual errors.

    ??? question "How does Heat ensure that a network is created before a server that depends on it?"
        Heat analyzes the template and builds a Directed Acyclic Graph (DAG) of dependencies. If a server resource uses `{ get_resource: network_name }`, Heat automatically knows it must create the network first.

    ??? question "What is the purpose of the OS::Heat::SoftwareConfig resource?"
        It is used to define the configuration logic (such as shell scripts or Ansible playbooks) that should be executed on a virtual machine after it has been provisioned.

## Assignments
!!! note "Assignment 1: Basic Template Modification"
    **Goal:** Modify the provided `web_tier.yaml` to add a second web server.
    - Update the `resources` section to include `web_server_2`.
    - Ensure both servers are attached to the same network and security group.
    - Ensure `web_server_2` also uses the `prefix` parameter for its name.
    - Deploy the stack and verify both instances are running.

!!! note "Assignment 2: Dynamic Configuration"
    **Goal:** Implement a parameter to control the number of servers.
    - Although basic HOT requires explicit resource definitions, try to use a `parameter` to change the `flavor` of the servers dynamically during stack creation.
    - Experiment with creating a template that accepts a `cidr` as a parameter for the subnet.

!!! note "Assignment 3: Advanced Multi-Tier Architecture"
    **Goal:** Design a template for a two-tier application (Web and Database).
    - Create a private network for the database and a separate network for the web tier.
    - Ensure the database server is not accessible from the public internet.
    - Use a security group rule to allow the web server to communicate with the database server on port 5432 (PostgreSQL) or 3306 (MySQL).
    - Use a `prefix` parameter for all resource names.
    - Output the private IP of the database server.

## Further Reading & Resources

- Official Heat Documentation: https://docs.openstack.org/heat/latest/
- HOT Reference (Functions and Resources): https://docs.openstack.org/heat/latest/template_guide/hot_spec.html
- OpenStack Operations Guide – Heat Chapter: https://docs.openstack.org/ops-guide/heat.html
- Sample Templates Repository: https://github.com/openstack/heat-templates
- Community Blog – Heat Best Practices: https://developer.ibm.com/articles/openstack-heat-best-practices/

## Appendix: FAQ

### Can I have different parameters for different VMs defined in the same Heat YAML file?

Yes, you can. There are two primary ways to achieve this depending on whether you are referring to **Infrastructure Parameters** (like flavor, image, or disk size) or **Software Configuration Parameters** (like application settings or user data).

#### 1. Infrastructure Parameters
If you want different VMs to have different hardware specifications, you simply define multiple parameters in the `parameters` section and assign them to the respective resources.

**Example:**

```yaml
parameters:
  web_flavor:
    type: string
    default: m1.small
  db_flavor:
    type: string
    default: m1.medium

resources:
  web_server:
    type: OS::Nova::Server
    properties:
      flavor: { get_param: web_flavor }
      # ... other properties ...

  db_server:
    type: OS::Nova::Server
    properties:
      flavor: { get_param: db_flavor }
      # ... other properties ...
```

#### 2. Software Configuration Parameters
If you want different VMs to run different software configurations, you can use `OS::Heat::SoftwareConfig` and `OS::Heat::SoftwareDeployment`. You can define different `SoftwareConfig` resources for each role (e.g., one for the web server and one for the database server) and associate them with the corresponding VM.

Alternatively, you can use the `user_data` property of `OS::Nova::Server` to pass different cloud-init scripts to each VM.

**Example using `user_data`:**

```yaml
resources:
  web_server:
    type: OS::Nova::Server
    properties:
      user_data: |
        #cloud-config
        runcmd:
          - apt-get update
          - apt-get install -y nginx

  db_server:
    type: OS::Nova::Server
    properties:
      user_data: |
        #cloud-config
        runcmd:
          - apt-get update
          - apt-get install -y postgresql
```

By combining these techniques, you can create a highly customized multi-tier environment where each virtual machine is tailored to its specific role within the architecture.

### How can multiple users use the same Heat template without causing resource name collisions?

When multiple users deploy the same template in a shared OpenStack project or cloud, they may encounter errors if the template uses hard-coded resource names (e.g., `name: web-server`). Since some OpenStack resources must have unique names within a scope, this causes conflicts.

The best practice is to implement a **Prefix Parameter**, as demonstrated in the "Practical Implementation" section of this chapter. By defining a `prefix` parameter and using the `fn::concat` intrinsic function, you can dynamically generate unique names for every resource.

**Example Workflow:**

1.  **The Template**: Use `fn::concat` for all naming properties.

    ```yaml
    parameters:
      prefix: { type: string }

    resources:
      my_net:
        type: OS::Neutron::Net
        properties:
          name: { "fn::concat": [ { "get_param": "prefix" }, "-network" ] }
    ```

2.  **User A Deployment**:

    ```bash
    openstack stack create -t template.yaml -P prefix=userA my-stack-A
    ```
    *Result*: Network is named `userA-network`.

3.  **User B Deployment**:

    ```bash
    openstack stack create -t template.yaml -P prefix=userB my-stack-B
    ```
    *Result*: Network is named `userB-network`.

This approach allows a single, version-controlled template to be shared across an entire organization while ensuring that each user's environment remains isolated and distinguishable.
