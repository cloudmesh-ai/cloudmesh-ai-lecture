# Oct 8 Lecture: 


## OpenStack & Cloud Orchestration
*Focus: Moving from manual VM provisioning to automated, scalable infrastructure.*

### Fundamentals & Cost Optimization

* Presented last week

### Advanced Networking & Orchestration

*   ~~*Presented last week:* **[Multi-VM Architectures](/section/cloud/platforms/jetstream/jetstream-multi.md)**: Building distributed AI/Data clusters (Scheduler $\leftrightarrow$ Workers) with complex security group rules and private/public IP routing.~~
*   **[OpenStack Heat](/section/cloud/openstack/openstack-heat.md) (IaC)**: Moving from imperative CLI commands to declarative YAML templates (HOT) for repeatable infrastructure.
*   **[Secure API Deployment](/section/cloud/openstack/openstack-heat-fastapi.md)**: Implementing two-tier architectures using **Bastion Hosts** and **FastAPI** to balance project-wide accessibility with strict security.
*   **[Project-Wide Access](/section/cloud/openstack/openstack-heat-fast-api-project-wide-access.md)**: Analyzing the security trade-offs between "Bastion" and "Project-Wide" access models for internal team connectivity.
*   **[Multi-VM Heat Orchestration](/section/cloud/platforms/chameleon/chameleon-multi-heat.md)**: Applying Infrastructure as Code specifically to the multi-worker cluster example.

### Storage Services - to be completed on Oct 15th
*   **[Overview](/section/cloud/openstack/storage/cinder.md)**: Overview of the Openstack storage services.
*   **[Cinder](/section/cloud/openstack/storage/cinder.md) (Block Storage)**: Managing persistent virtual hard drives that survive VM lifecycles.
*   **[Swift](/section/cloud/openstack/storage/swift.md) (Object Storage)**: Using S3-compatible storage for massive, unstructured datasets (images, backups).
*   **[Glance](/section/cloud/openstack/storage/glance.md) (Image Registry)**: Managing "Golden Images" to ensure consistency across thousands of VM boots.



## Public Clouds - to be completed on Oct 15th

*Focus: Comparing private cloud capabilities with public cloud implementations.*

* **Cloudbank videos:**

    In a discussion with Cloudbank they indicated they wanted me to show them:

    * Part 1: [CloudBank Onboarding (~10m)](https://www.cloudbank.org/onboarding-video-part1)
    * Part 2: [CloudBank Portal Demo (~25m)](https://www.cloudbank.org/onboarding-video-part2)


*   **Public Cloud Implementations**:

    *   **AWS**: [Account Setup](/section/accounts/aws.md), [CLI Installation & Setup](/section/cloud/vm-cloud/aws-install-chapter.md) and [Boto3 SDK Implementation](/section/cloud/vm-cloud/aws-boto-chapter.md)
    *   **Azure**: [Account Setup](/section/accounts/azure.md), [Installation & Setup](/section/cloud/vm-cloud/azure%20install-chapter.md) and [Azure SDK Implementation](/section/cloud/vm-cloud/azure-sdk-chapter.md)
    *   **GCP**: [Account Setup](/section/accounts/google.md) and [Installation & Setup](/section/cloud/vm-cloud/gcp-install-chapter.md)

 