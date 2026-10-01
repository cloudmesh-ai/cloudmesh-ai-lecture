## Learning Objectives

!!! info "Learning Objectives"
    * Compare pay-as-you-go pricing for small virtual machines across major cloud providers.
    * Understand the components of monthly cloud costs, including compute, storage, and data egress.
    * Evaluate the impact of free tiers on the effective cost of small VM workloads.
    * Identify the most cost-effective platform for various experimental and production use cases.

    ## Overview

    This chapter provides a detailed cost comparison for Linux virtual machines (approximately 1 vCPU and 1 GiB RAM) running Ubuntu 26.04. The analysis focuses on pay-as-you-go pricing to establish a baseline cost for small development workloads.

    The comparison assumes a specification of 1 vCPU, 1 GiB RAM, a 30 GiB general-purpose SSD boot disk, and 100 GiB of outbound data transfer per month. All prices are on-demand and are expressed in U.S. dollars based on public pricing data from October 2024.

    ## Core Sections

    ### Price Comparison Table

    The table below shows the pay-as-you-go price for a Linux VM matching the specified requirements.

    | Provider | Instance type (closest match) | vCPU + RAM price / hr | Monthly compute* (720 h) | 30 GiB SSD / mo | 100 GiB egress / mo | Total / mo (compute + storage + egress) | Free-tier / always-free eligibility |
    |----------|------------------------------|-----------------------|--------------------------|----------------|--------------------|-------------------------------------------|--------------------------------------|
    | **Amazon Web Services** | t3.micro (Linux) - 1 vCPU / 1 GiB | **$0.0104** | $7.49 | $3.00 (GP2 $0.10 / GB-mo) | $9.00 (first 10 TB $0.09 / GB) | **$19.49** | 750 h / month free (t2.micro/t3.micro) -> $0 if you stay <= 750 h |
    | **Microsoft Azure** | B1s (Linux) - 1 vCPU / 1 GiB | **$0.0080** | $5.76 | $1.20 (Standard SSD $0.04 / GB-mo) | $8.70 (first 5 TB $0.087 / GB) | **$15.66** | 750 h / month free (B1s) -> $0 if <= 750 h |
    | **Google Cloud Platform** | e2-micro (Linux) - 0.25 vCPU / 1 GiB | **$0.0060** | $4.32 | $1.20 (PD-Standard $0.04 / GB-mo) | $12.00 (first 1 TB $0.12 / GB) | **$17.52** | 720 h / month free (e2-micro) -> $0 if <= 720 h |
    | **Oracle Cloud Infrastructure** | VM.Standard.E2.1.Micro (Linux) - 1 OCPU / 1 GiB | **$0.0065** | $4.68 | $0.75 (Block Volume $0.025 / GB-mo) | $9.00 (first 10 TB $0.09 / GB) | **$14.43** | Always-free: 1 OCPU + 1 GiB RAM + 100 GB block storage -> $0 if you stay within limits |
    | **Jetstream 2 (XSEDE OpenStack)** | 1 vCPU + 1 GiB RAM = **0.5 SU** (1 SU = 1 core + 2 GiB) | **$0.0085 / SU-hr** -> $0.00425 / hr | $3.06 | $0.60 (local SSD approx. $0.02 / GB-mo) | $9.00 (same public-cloud egress rates) | **$12.66** | No free tier - you pay per SU-hour |
    | **Chameleon (XSEDE OpenStack)** | 1 vCPU + 1 GiB RAM = **0.5 SU** (1 SU = 1 core + 2 GiB) | **$0.018 / SU-hr** -> $0.009 / hr | $6.48 | $0.60 (approx. $0.02 / GB-mo) | $9.00 | **$16.08** | No free tier - you pay per SU-hour |

    \* Monthly compute assumes a full month of 720 hours (30 days x 24 h). The actual billing period for most clouds is per-second, but 720 h is used as a consistent reference.

    ### Cost Derivation

    The values in the comparison table are derived from the following sources and formulas.

    | Component | Source / formula |
    |-----------|------------------|
    | **AWS t3.micro** | $0.0104 / h (US East (N. Virginia) - Linux on-demand) - <https://aws.amazon.com/ec2/pricing/on-demand/> |
    | **Azure B1s** | $0.008 / h (East US - Linux Pay-As-You-Go) - <https://azure.microsoft.com/pricing/details/virtual-machines/> |
    | **GCP e2-micro** | $0.0060 / h (us-central1 - Linux) - <https://cloud.google.com/compute/all-pricing> |
    | **OCI E2.1-Micro** | $0.0065 / h (US East (ashburn) - Linux) - <https://www.oracle.com/cloud/compute/pricing.html> |
    | **Jetstream 2 SU price** | $0.0085 / SU-hr (2024 XSEDE rate card) - <https://www.xsede.org/resource/jetstream2> |
    | **Chameleon SU price** | $0.018 / SU-hr (2024 XSEDE rate card) - <https://www.xsede.org/resource/chameleon> |
    | **SSD storage** | AWS gp2 $0.10 / GB-mo, Azure Standard SSD $0.04 / GB-mo, GCP PD-Standard $0.04 / GB-mo, OCI Block Volume $0.025 / GB-mo, OpenStack (local SSD) approx. $0.02 / GB-mo. |
    | **Outbound data** | AWS $0.09 / GB (first 10 TB), Azure $0.087 / GB (first 5 TB), GCP $0.12 / GB (first 1 TB), OCI $0.09 / GB (first 10 TB). OpenStack sites charge $0.09 / GB on XSEDE Usage Units. |
    | **Free-tier limits** | AWS 750 h / month t2.micro/t3.micro, Azure 750 h / month B1s, GCP 720 h / month e2-micro, OCI Always-Free 1 OCPU + 1 GiB RAM + 100 GB block storage. |

    ### Price Interpretation

    The following table compares the cheapest pay-as-you-go price against the effective price when a free tier is available.

    | Provider | Cheapest pay-as-you-go price (no free tier) | Cheapest effective price when the free tier is applicable |
    |----------|----------------------------------------------|---------------------------------------------------------------|
    | AWS | **$19.49 / mo** (compute + storage + egress) | $0 / mo if you stay <= 750 h on the free tier (egress beyond 15 GB/month is billed). |
    | Azure | **$15.66 / mo** | $0 / mo if <= 750 h on the free tier (egress above 15 GB/mo is billed). |
    | GCP | **$17.52 / mo** | $0 / mo if <= 720 h on the free tier (egress above 1 GB/mo is billed). |
    | OCI | **$14.43 / mo** | $0 / mo always (the Always-Free tier already includes 1 OCPU + 1 GiB RAM + 100 GB storage). |
    | Jetstream 2 | **$12.66 / mo** (no free tier) | No free tier - you pay per SU-hour, but the price is lower than the major public clouds for research allocations. |
    | Chameleon | **$16.08 / mo** (no free tier) | No free tier - price per SU-hour is higher than Jetstream 2 but comparable to commercial clouds. |

    ### Platform Selection Guide

    Depending on the use case, different platforms offer better value.

    | Use-case | Recommendation |
    |----------|----------------|
    | **Purely experimental / learning** - minimal to no cost for a small VM. | **OCI Always-Free** or **AWS / Azure / GCP free tier** - OCI's free tier does not expire. |
    | **Research projects** - guaranteed allocation and integration with XSEDE. | **Jetstream 2** (cheapest per SU-hour) or **Chameleon** for specific hardware (e.g., GPUs). |
    | **Production or multi-region workloads** | Commercial cloud based on region, SLA, and ecosystem. OCI is the cheapest on-demand for this VM size, followed by Azure, GCP, then AWS. |
    | **High-performance networking / large-scale data egress** | Compare egress rates: Azure is marginally cheapest ($0.087 / GB), OCI and AWS are $0.09 / GB, and GCP is most expensive ($0.12 / GB). |
    | **Long-term, predictable usage** | Use reserved-instance or committed-use discounts to reduce hourly rates by 30% to 60%. |

    ### Quick Reference - Cost per Hour (Compute Only)

    | Provider | Compute price / h | Equivalent per-month (720 h) |
    |----------|-------------------|------------------------------|
    | AWS t3.micro | $0.0104 | $7.49 |
    | Azure B1s | $0.0080 | $5.76 |
    | GCP e2-micro | $0.0060 | $4.32 |
    | OCI E2.1-Micro | $0.0065 | $4.68 |
    | Jetstream 2 (0.5 SU) | $0.00425 | $3.06 |
    | Chameleon (0.5 SU) | $0.0090 | $6.48 |

    ### Summary Conclusions

    If the workload stays within the free allocation, **OCI** is the most cost-effective choice due to its permanent always-free VM.

    For research-grade allocations, **Jetstream 2** is the cheapest per-hour option (approximately $3 / mo), though usage must be paid.

    For commercial clouds with a broad ecosystem, the ordering from cheapest to most expensive (on-demand) for this VM size is: **OCI -> Azure -> GCP -> AWS**.

    ## Summary Checklist

    * [ ] Can identify the cheapest on-demand provider for a small Linux VM.
    * [ ] Understands the components of a monthly cloud bill (compute, storage, egress).
    * [ ] Can differentiate between pay-as-you-go pricing and effective pricing with free tiers.
    * [ ] Knows which provider offers a permanent "Always-Free" compute tier.
    * [ ] Understands the cost structure of research clouds like Jetstream 2 and Chameleon.

    ## Assignments

!!! note "Assignment.1: Monthly Cost Calculation"
    Calculate the total monthly cost for a VM on AWS if the compute is 720 hours, storage is 100 GiB of gp2 SSD, and egress is 500 GiB.

??? tip "Solution: Monthly Cost Calculation"
    Compute: 720 * $0.0104 = $7.49
    Storage: 100 * $0.10 = $10.00
    Egress: 500 * $0.09 = $45.00
    Total: $7.49 + $10.00 + $45.00 = $62.49

!!! note "Assignment.2: Free Tier Comparison"
    Compare the Always-Free compute offering of OCI with the 12-month Free Trial of AWS. Which one is more sustainable for a long-term (2+ year) personal project?

??? tip "Solution: Free Tier Comparison"
    OCI is more sustainable because its Always-Free tier does not expire, whereas the AWS Free Trial compute benefits typically expire after 12 months.

    ## References

    * AWS EC2 Pricing: <https://aws.amazon.com/ec2/pricing/on-demand/>
    * Azure VM Pricing: <https://azure.microsoft.com/pricing/details/virtual-machines/>
    * GCP Compute Engine Pricing: <https://cloud.google.com/compute/all-pricing>
    * OCI Compute Pricing: <https://www.oracle.com/cloud/compute/pricing.html>
    * XSEDE Jetstream 2: <https://www.xsede.org/resource/jetstream2>
    * XSEDE Chameleon: <https://www.xsede.org/resource/chameleon>

    ## Self-Evaluation

??? note "Which cloud provider offers the lowest on-demand compute price for a 1 vCPU / 1 GiB VM?"
    Based on the comparison table, Google Cloud Platform (e2-micro) has the lowest hourly compute price at $0.0060, although it provides only 0.25 vCPU. Among those providing a full vCPU or OCPU, OCI and Azure are very competitive.

??? note "Why is egress often a significant part of the total monthly cost?"
    While compute and storage costs are relatively low for small VMs, outbound data transfer (egress) is billed per GiB. For workloads that send large amounts of data to the internet, egress charges can easily exceed the compute and storage costs combined.

??? note "What is a Service Unit (SU) in the context of Jetstream 2 and Chameleon?"
    A Service Unit is a measure of resource allocation where 1 SU typically equals 1 core and 2 GiB of RAM. For a 1 vCPU and 1 GiB RAM VM, the cost is 0.5 SU per hour.
