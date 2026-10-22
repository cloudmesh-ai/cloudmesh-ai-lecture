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
*   🔴  **[Overview](/section/cloud/openstack/storage/cinder.md)**: Overview of the Openstack storage services.
*   🔴  **[Cinder](/section/cloud/openstack/storage/cinder.md) (Block Storage)**: Managing persistent virtual hard drives that survive VM lifecycles.
*   🔴  **[Swift](/section/cloud/openstack/storage/swift.md) (Object Storage)**: Using S3-compatible storage for massive, unstructured datasets (images, backups).
*   🔴  **[Glance](/section/cloud/openstack/storage/glance.md) (Image Registry)**: Managing "Golden Images" to ensure consistency across thousands of VM boots.

## Reminder: Sample Project Directory Layout  

* <https://github.com/cloudmesh-ai/cloudmesh-ai-vm>
* <https://github.com/cloudmesh-ai/cloudmesh-ai-llm-mock>

* Where to place directories in GitHub:

    * <https://github.com/orgs/cloudmesh-ai-luc/repositories>

    Obviously, your project documentation will be in

    ```./project/project.md```

    and once you have access to LLMs

    ```./docs```

    the code will be in

    ```./src```

    your assignments are in

    ```./assignments```

    and are this way nicely separated from your project.
    The only thing that is different is your README.md as it relates to the class. For that reason we obviously have ./project/project.md


* Please note that all of you have decided to work **individually**. Hence, there is no need to do a very large task based project document. You are highly suggested to create an **academic style project report** which is more in line of an academic paper and is not like a company focussed project report. (See my notes on project report). Examples:


    * <https://www.mdpi.com/1999-4893/15/7/230>
    * <https://journals.flvc.org/UFJUR/article/view/139103>
    * <https://www.frontiersin.org/journals/high-performance-computing/articles/10.3389/fhpcp.2023.1233877/full>

    This shows that one does not have to distinguish if you have no degree, a BA, a MS, or a PhD, or are a Prof. In the team we all contribute the best we can and organize the work around individual strenght.

## SMOKE Tests for VMs (You show us not just me)

I also like to hear from anyone that has updates to vm. and can show me concrete results from your smoke tests. Clarification of repo for result posts (see last lecture, reminder as some did not use it.)

* <https://github.com/cloudmesh-ai/cloudmesh-ai-vm-results>

## Cloud LLMs using jetstream

Using LLMs for the class. This is for those that do not use LLMs in the cloud as costly.

* <https://github.com/cloudmesh-ai/cloudmesh-ai-llm-mock>
* <https://llm.jetstream-cloud.org/>
* <https://docs.jetstream-cloud.org/inference-service/overview/>


## Public Clouds

*Focus: Comparing private cloud capabilities with public cloud implementations.*

* **Cloudbank videos:**

    In a discussion with Cloudbank they indicated they wanted me to show them:

    * 🔴  Part 1: [CloudBank Onboarding (~10m)](https://www.cloudbank.org/onboarding-video-part1)
    * 🔴  Part 2: [CloudBank Portal Demo (~25m)](https://www.cloudbank.org/onboarding-video-part2)
    * 🔴 Part 3: [Onpoarding (PDF)](https://www.cloudbank.org/docs/onboarding)


*   **Public Cloud Implementations**:

    *   🔴  **AWS**: [Account Setup](/section/accounts/aws.md), [CLI Installation & Setup](/section/cloud/vm-cloud/aws-install-chapter.md) and [Boto3 SDK Implementation](/section/cloud/vm-cloud/aws-boto-chapter.md)
    *   🔴 **Azure**: [Account Setup](/section/accounts/azure.md), [Installation & Setup](/section/cloud/vm-cloud/azure%20install-chapter.md) and [Azure SDK Implementation](/section/cloud/vm-cloud/azure-sdk-chapter.md)
    *   🔴 **GCP**: [Account Setup](/section/accounts/google.md) and [Installation & Setup](/section/cloud/vm-cloud/gcp-install-chapter.md)


