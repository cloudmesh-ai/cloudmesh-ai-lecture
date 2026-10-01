# Cloud Virtual Machines

<!--start-->

This chapter provides a comprehensive guide to provisioning and managing virtual machines across the major public cloud providers, focusing on accessibility, cost-efficiency, and automation.


### Part I: Foundations and Cost Analysis

* **[🔵 Understanding Cloud Free Tiers](/section/cloud/vm-cloud/free-chapter.md)**: Navigating promotional credits and "Always-Free" offerings to start learning without cost.
* **[🔵 Pay-as-you-go Cost Comparison](/section/cloud/vm-cloud/cost-chapter.md)**: A detailed price analysis for small Linux VMs across AWS, Azure, GCP, and Oracle.
* **[🔵 Spot Pricing Guide](/section/cloud/vm-cloud/cost-spot-chapter.md)**: Understanding pre-emptible and spot instances to reduce compute costs by up to 80%.
* **[🔵 Launching Spot Instances](/section/cloud/vm-cloud/using-spot-pricing-chapter.md)**: Practical implementation of spot instances using CLI, Libcloud, and Native SDKs.

### Part II: Cloud-Specific Implementation

#### Amazon Web Services (AWS)
* **[🔵 AWS CLI Free-Tier Tutorial](/section/cloud/vm-cloud/aws-install-chapter.md)**: Step-by-step guide from account creation to a running EC2 instance.
* **[🔵 AWS Native Python SDK (boto3)](/section/cloud/vm-cloud/aws-boto-chapter.md)**: Automating EC2 provisioning and cleanup using the official AWS SDK.

#### Microsoft Azure
* **[🔵 Azure CLI Free-Tier Tutorial](/section/cloud/vm-cloud/azure%20install-chapter.md)**: Guide to setting up a B1s Linux VM within the Azure free tier.
* **[🔵 Azure Native Python SDK](/section/cloud/vm-cloud/azure-sdk-chapter.md)**: Programmatic VM management using `azure-mgmt-compute` and `azure-identity`.

#### Google Cloud Platform (GCP)
* **[🔵 GCP SDK Free-Tier Tutorial](/section/cloud/vm-cloud/gcp-install-chapter.md)**: Provisioning an `e2-micro` instance using the `gcloud` tool.
* **[🔵 GCP Native Python SDK](/section/cloud/vm-cloud/google-sdk-chapter.md)**: Using `google-cloud-compute` for automated VM lifecycle management.

#### Oracle Cloud Infrastructure (OCI)
* **[🔵 Oracle Cloud Free-Tier Tutorial](/section/cloud/vm-cloud/oracle-chapter.md)**: Leveraging the generous "Always-Free" ARM and AMD shapes.
* **[🔵 Oracle Native Python SDK](/section/cloud/vm-cloud/oracle-sdk-chapter.md)**: Automating OCI compute instances using the `oci` Python library.

### Part III: Multi-Cloud Automation

* **[🔵 Managing VMs with Apache Libcloud](/section/cloud/vm-cloud/libcloud-chapter.md)**: Using a single Python API to manage VMs across multiple providers and avoid vendor lock-in.
* **[🔵 Summary and Provider Comparison](/section/cloud/vm-cloud/comparison-chapter.md) [MISSING]**: A final synthesis comparing the ease of use, reliability, and performance of the providers.

<!--end-->
