## Learning Objectives

!!! info "Learning Objectives"
    * Differentiate between promotional credits and "Always-Free" tiers in public cloud platforms.
    * Identify the specific free compute offerings provided by AWS, Azure, GCP, and OCI.
    * Understand the technical limitations—including region, instance type, and usage quotas—associated with free tiers.
    * Implement practical strategies, such as billing alerts, to avoid accidental charges.

    ## Overview

    Most major public cloud platforms provide a combination of two types of free access: promotional credits and "Always-Free" tiers. Promotional credits are lump-sum amounts or fixed hours available for a limited trial period (typically 12 months), while "Always-Free" tiers consist of a limited set of resources that remain free indefinitely, provided usage stays within specified limits.

    This chapter details the current offerings from the largest providers and offers guidance on how to utilize these resources without incurring unexpected costs.

    ## Core Sections

    ### The Two Types of Free Access

    Cloud providers typically use a dual-track approach to attract new users:

    1. **Promotional Credits**: These are time-limited (e.g., 90 days to 12 months) and often provide a generous amount of credit (e.g., $300) to explore a wide range of services.
    2. **Always-Free Tiers**: These are indefinite but strictly limited to specific, low-power resources (e.g., a small VM, a small amount of object storage) and often restricted to specific geographic regions.

    ### Major Provider Free Tiers

    #### Amazon Web Services (AWS)

    | Tier | What is free | Limits (per month) | Comments |
    |------|--------------|--------------------|----------|
    | **12-month Free Trial** | $300 credit (or 750 h of t2.micro/t3.micro) + other services | 750 h of t2.micro/t3.micro VM, 5 GB S3 Standard, 750 h RDS db.t2.micro | Credit expires after 12 months; usage beyond limits is billed. |
    | **Always-Free** | Subset of services that remain free indefinitely | 750 h/month t2.micro/t3.micro (eligible regions), 5 GB S3 Standard, 1 M Lambda requests, 10 GB Data Transfer Out | Limits apply only to listed services and specific regions. |
    | **Free Sandbox** | AWS CloudShell | 1 h of interactive shell per day, 2 GB home directory | Useful for quick CLI experiments; no compute charges. |

    #### Microsoft Azure

    | Tier | What is free | Limits (per month) | Comments |
    |------|--------------|--------------------|----------|
    | **12-month Free Trial** | $200 credit + access to a set of services | 750 h of B1s VM, 5 GB Blob storage, 250 GB Azure SQL DB, 15 GB outbound data | Credit expires after 12 months. |
    | **Always-Free** | Narrow set of services that stay free indefinitely | 750 h/month B1s VM (eligible regions), 5 GB Blob storage (Hot tier), 1 M Azure Functions requests | Quotas are region-restricted and applied per subscription. |
    | **Free Sandbox** | Azure Cloud Shell | 15 min of interactive session per day, 5 GB home directory | Ideal for testing Azure CLI/PowerShell. |

    #### Google Cloud Platform (GCP)

    | Tier | What is free | Limits (per month) | Comments |
    |------|--------------|--------------------|----------|
    | **12-month Free Trial** | $300 credit (valid for 90 days, usable up to 12 months) | 720 h of e2-micro VM, 5 GB Regional Cloud Storage, 1 TiB outbound network (North America) | Credit expires after 90 days, but always-free resources persist. |
    | **Always-Free** | Small quota of services that never cost anything | 720 h/month e2-micro VM (specific regions), 5 GB Regional Cloud Storage, 1 GiB Firestore, 1 TiB outbound network (North America) | VM quota is limited to specific regions (e.g., us-central1, us-west1). |
    | **Free Sandbox** | Cloud Shell | 1 h of interactive shell per day | Runs on Google infrastructure at no cost. |

    #### Oracle Cloud Infrastructure (OCI)

    | Tier | What is free | Limits (per month) | Comments |
    |------|--------------|--------------------|----------|
    | **Always-Free** | Broader set than other major clouds | 2 Arm-based (VM.Standard.A1.Flex) instances up to 4 OCPU and 24 GB RAM, 2 AMD-based (VM.Standard.E2.1.Micro) instances, 100 GB Block Volume, 10 TB outbound data | Resources are free regardless of trial credit, but must stay in the Free Tier region. |
    | **Free Sandbox** | OCI Always-Free Cloud Shell | 1 h per day, 2 GB storage | No cost. |

    ### Secondary and Niche Providers

    Beyond the "Big Four," other providers offer specialized free tiers:

    | Provider | Free offering (forever) | Typical limits | Notes |
    |----------|------------------------|----------------|-------|
    | **IBM Cloud** | Lite account | 256 MB Object Storage, 1 GB Cloudant DB, 2 GB Cloud Functions | Free as long as quota is maintained. |
    | **Alibaba Cloud** | Always-Free (limited set) | 1 t5-small instance (up to 750 h), 40 GB Object Storage | Most benefits are trial-based. |
    | **Vercel / Netlify** | Free plan for static sites / serverless | Limited bandwidth and build minutes | Platform-as-a-Service (PaaS) rather than IaaS. |
    | **GitHub Actions** | Free for public repos | 2,000 minutes/month | CI/CD focused, not a general compute VM. |
    | **Cloudflare Workers** | Edge-compute free tier | 100,000 requests/day | Edge-compute platform. |

    ### Key Take-aways

    * **Quota-Based Freeing**: "Free forever" means free within stated caps. Exceeding a quota triggers regular billing.
    * **Regional Restrictions**: Always-free compute is often restricted to specific regions (e.g., us-east-1 for AWS) and specific instance types.
    * **Trial Expiration**: Promotional credits expire. Users must transition to paid plans or strictly adhere to always-free quotas to avoid charges.
    * **Account Limits**: Quotas are per-account. Creating multiple accounts to bypass limits is generally discouraged and may violate terms of service.
    * **Billing Alerts**: Setting a budget alert (e.g., at $0.01) is the only reliable way to prevent surprise charges.

    ### Forever-Free Compute Comparison

    | Provider | Free compute type | vCPU / RAM | Max monthly hours | Eligible regions |
    |----------|-------------------|-----------|-------------------|------------------|
    | AWS      | t2.micro / t3.micro | 1 vCPU / 1 GiB | 750 h | us-east-1, us-west-2, etc. |
    | Azure    | B1s | 1 vCPU / 1 GiB | 750 h | East US, West US, etc. |
    | GCP      | e2-micro | 1 vCPU (shared) / 0.5 GiB | 720 h | us-central1, us-west1, etc. |
    | OCI      | VM.Standard.A1.Flex (Arm) | Up to 4 vCPU / 24 GiB total | Unlimited (subject to caps) | us-ashburn-1, us-phoenix-1 |
    | IBM Cloud | Lite "f1-1-2X" | 0.25 vCPU / 256 MiB | Unlimited (subject to caps) | Global (Lite plan) |

    ### Strategies for Staying Free

    To ensure a workload remains at zero cost, follow these steps:

    1. **Dedicated Organization**: Create a single resource group or project specifically for free resources.
    2. **Regional Locking**: Strictly deploy resources in the provider's designated free-tier regions.
    3. **Budget Alerts**: Configure a billing alert to trigger immediately upon any spending (e.g., at $0.01).
    4. **Regular Audits**: Use CLI tools (e.g., `aws ce get-cost-and-usage`) to monitor consumption.
    5. **Avoid Ancillary Costs**: Be cautious with managed load balancers, NAT gateways, or premium storage, which are rarely free.
    6. **Resource Hygiene**: Stop or delete resources that are not actively in use; orphaned disks can still generate charges.

    ## Summary Checklist

    * [ ] Can distinguish between a promotional credit and an always-free tier.
    * [ ] Knows the free instance type for AWS, Azure, GCP, and OCI.
    * [ ] Understands why choosing the correct region is critical for free tiers.
    * [ ] Knows how to set up a billing alert to prevent unexpected costs.
    * [ ] Understands the difference between IaaS (VMs) and PaaS (Vercel/Netlify) free offerings.

    ## Assignments

!!! note "Assignment.1: Billing Alert Setup"
    Log into one of the major cloud consoles (AWS, Azure, GCP, or OCI) and create a billing budget or alert that notifies you via email when your monthly spend reaches $0.01.

??? tip "Solution: Billing Alert Setup"
    The solution involves navigating to the "Billing" or "Cost Management" section of the console and creating a "Budget" or "Alert" with a threshold of $0.01.

!!! note "Assignment.2: Resource Audit"
    Using the CLI for a cloud provider of your choice, list all running instances in your account and verify if they match the free-tier instance type and region.

??? tip "Solution: Resource Audit"
    Example for AWS: `aws ec2 describe-instances --query 'Reservations[*].Instances[*].{ID:InstanceId,Type:InstanceType,Region:Placement.AvailabilityZone}'`. Verify that the type is `t2.micro` or `t3.micro`.

    ## References

    * AWS Free Tier: <https://aws.amazon.com/free/>
    * Azure Free Account: <https://azure.microsoft.com/free/>
    * GCP Free Program: <https://cloud.google.com/free>
    * OCI Always Free: <https://www.oracle.com/cloud/free/>

    ## Self-Evaluation

??? note "What is the primary difference between a 12-month trial and an always-free tier?"
    A 12-month trial provides a broad set of resources or a cash credit for a limited time, whereas an always-free tier provides a very limited set of resources indefinitely.

??? note "Why might a user be billed for a VM even if they are using a free-tier instance type?"
    Billing can occur if the instance is launched in a region not eligible for the free tier, if the user exceeds the monthly hour quota, or if they attach non-free resources like premium SSDs or NAT gateways.

??? note "How does OCI's free compute offering differ from those of AWS, Azure, and GCP?"
    OCI offers a significantly more powerful always-free tier, particularly its Arm-based instances, which allow for up to 4 OCPUs and 24 GB of RAM, far exceeding the 1 vCPU / 1 GiB typical of the other three providers.
