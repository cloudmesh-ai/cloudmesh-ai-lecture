## Chapter: OpenStack and Research Cloud Platforms

<!--start-->

Welcome to the OpenStack and Research Cloud Platforms section of the course. This chapter focuses on the implementation and management of private clouds using OpenStack, exploring how this powerful IaaS platform is utilized by research clouds like Chameleon and Jetstream to provide scalable compute, networking, and storage resources.

- **Part I: Introduction to OpenStack**
    * **Fundamentals**: [🟢 Introduction to OpenStack: IaaS for the Enterprise](/section/cloud/openstack/openstack.md): A comprehensive overview of OpenStack's role, its core services (Nova, Neutron, Cinder, etc.), and its importance for AI workloads.
    * **Control Plane**: [🟢 Managing the Cloud: The OpenStack Horizon Dashboard](/section/cloud/openstack/horizon.md): A guide to navigating the web-based GUI and managing cloud resources visually.
    * **Optimization**: [🟢 Strategies for reducing OpenStack costs](/section/cloud/openstack/openstack-reduce-cost.md).

- **Part II: OpenStack Research Cloud Platforms**
    * **Chameleon Cloud**:
        * **Environment**: [🟢 Introduction to the Chameleon environment](/section/cloud/platforms/chameleon/environment.md).
        * **Provisioning**: [🟢 Managing reservations](/section/cloud/platforms/chameleon/reservation.md) and using the [🟢 Horizon dashboard](/section/cloud/platforms/chameleon/horizon.md).
        * **Operations**: [🟢 OS command-line management](/section/cloud/platforms/chameleon/os-commandline.md) and [🟢 OS-level Python automation](/section/cloud/platforms/chameleon/os-python.md).
        * **Integration**: [🟢 Using the Python CHI library](/section/cloud/platforms/chameleon/python-chi.md).
        * **Economics**: [🟢 Understanding and managing costs on Chameleon](/section/cloud/platforms/chameleon/cost.md).
    * **Jetstream**:
        * **VM Basics**: [🟢 Deploying and managing VMs on Jetstream](/section/cloud/platforms/jetstream/jetstream-vm.md).
        * **Scaling**: [🟢 Multi-node deployments](/section/cloud/platforms/jetstream/jetstream-multi.md), including [🔵 Visualizing multi-node deployments](/section/cloud/platforms/jetstream/images/multi-jetstream-mermaid.md) and [🔴 Orchestration with Heat](/section/cloud/platforms/jetstream/jetstream-multi-heat.md).
        * **Administration**: [🟢 Jetstream cost management](/section/cloud/platforms/jetstream/jetstream-cost.md) and [🟢 Documentation via mkdocs](/section/cloud/platforms/jetstream/jetstream-mkdocs.md).

- **Part III: Openstack CLI**

    * [🟢 OpenStack command-line management](/section/cloud/platforms/chameleon/os-commandline.md): A step-by-step guide for provisioning and managing VMs using the `openstack` CLI.

- **Part IV: Openstack programming**

    * [🟢 Python automation with OpenStack SDK](/section/cloud/platforms/chameleon/os-python.md): Tutorial on using `openstacksdk` for programmatic VM creation and management.
    * [🟢 High-level automation with python-chi](/section/cloud/platforms/chameleon/python-chi.md): Simplified OpenStack resource management for Chameleon Cloud.
    * [🟢 Multi-cloud abstraction with Libcloud](/section/cloud/platforms/chameleon/os-python.md): Using Apache Libcloud for vendor-neutral cloud management.

- **Part V: Openstack Automation**
    * **[🔴 Introduction to OpenStack Heat](/section/cloud/openstack/openstack-heat.md)**: Understanding the concept of orchestration, Heat templates (HOT), and the lifecycle of a stack.
    * **[🔴 Advanced API Integration](/section/cloud/openstack/openstack-heat-fastapi.md)**: Implementing FastAPI wrappers to simplify Heat operations.
    * **[🔴 Project-Wide Access](/section/cloud/openstack/openstack-heat-fast-api-project-wide-access.md)**: Configuring and managing Heat API access across different project scopes.
    * **[🔴 Jetstream Multi-Node Orchestration](/section/cloud/platforms/jetstream/jetstream-multi-heat.md)**: Using Heat templates to deploy complex, multi-node clusters on the Jetstream platform.

- **Part VI: OpenStack Storage**
    * **Overview:** [🔴 Overview of Storage Services in Openstack](/section/cloud/openstack/storage/overview.md).
    * **Block Storage (Cinder)**: [🔴 Management of persistent block devices and volume attachment](/section/cloud/openstack/storage/cinder.md).
    * **Object Storage (Swift)**: [🔴 Scalable, S3-compatible storage for unstructured data](/section/cloud/openstack/storage/swift.md).
    * **Image Registry (Glance)**: [🔴 Storage and retrieval of VM snapshots and base images](/section/cloud/openstack/storage/glance.md).

- **Part VII: Openstack Development and Testing**
    * **Development**: [🔴 Getting started with DevStack for local OpenStack development](/section/cloud/openstack/devstack.md).

- **Part VIII: Application Development**
    * **API Integration**: [🔴 Building FastAPI wrappers for Heat](/section/cloud/openstack/openstack-heat-fastapi.md) and [🔴 managing project-wide access](/section/cloud/openstack/openstack-heat-fast-api-project-wide-access.md).

<!--end-->

