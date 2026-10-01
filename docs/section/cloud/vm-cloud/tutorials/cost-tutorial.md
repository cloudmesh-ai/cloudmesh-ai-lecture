
**Cost comparison – Ubuntu 26.04 VMs (≈ 1 vCPU + 1 GiB RAM)**  

The table below shows the *pay‑as‑you‑go* price for a Linux VM that is as close as possible to the following specification:

* 1 vCPU (or 1 OCPU)  
* 1 GiB RAM  
* 30 GiB boot disk (general‑purpose SSD)  
* 100 GiB outbound data transfer per month (typical for a small development workload)  

All prices are **on‑demand / pay‑as‑you‑go** (no reserved‑instance discounts) and are expressed in U.S. dollars.  Prices are taken from the public pricing pages that were current (2024‑10).  Small rounding differences are inevitable because each provider rounds its billing periods differently.

| Provider | Instance type (closest match) | vCPU + RAM price / hr | Monthly compute* (720 h) | 30 GiB SSD / mo | 100 GiB egress / mo | Total / mo (compute + storage + egress) | Free‑tier / always‑free eligibility |
|----------|------------------------------|-----------------------|--------------------------|----------------|--------------------|-------------------------------------------|--------------------------------------|
| **Amazon Web Services** | t3.micro (Linux) – 1 vCPU / 1 GiB | **$0.0104** | $7.49 | $3.00 (GP2 $0.10 / GB‑mo) | $9.00 (first 10 TB $0.09 / GB) | **$19.49** | 750 h / month free (t2.micro/t3.micro) → $0 if you stay ≤ 750 h |
| **Microsoft Azure** | B1s (Linux) – 1 vCPU / 1 GiB | **$0.0080** | $5.76 | $1.20 (Standard SSD $0.04 / GB‑mo) | $8.70 (first 5 TB $0.087 / GB) | **$15.66** | 750 h / month free (B1s) → $0 if ≤ 750 h |
| **Google Cloud Platform** | e2‑micro (Linux) – 0.25 vCPU / 1 GiB | **$0.0060** | $4.32 | $1.20 (PD‑Standard $0.04 / GB‑mo) | $12.00 (first 1 TB $0.12 / GB) | **$17.52** | 720 h / month free (e2‑micro) → $0 if ≤ 720 h |
| **Oracle Cloud Infrastructure** | VM.Standard.E2.1.Micro (Linux) – 1 OCPU / 1 GiB | **$0.0065** | $4.68 | $0.75 (Block Volume $0.025 / GB‑mo) | $9.00 (first 10 TB $0.09 / GB) | **$14.43** | Always‑free: 1 OCPU + 1 GiB RAM + 100 GB block storage → $0 if you stay within limits |
| **Jetstream 2 (XSEDE OpenStack)** | 1 vCPU + 1 GiB RAM = **0.5 SU** (1 SU = 1 core + 2 GiB) | **$0.0085 / SU‑hr** → $0.00425 / hr | $3.06 | $0.60 (local SSD ≈ $0.02 / GB‑mo) | $9.00 (same public‑cloud egress rates) | **$12.66** | No free tier – you pay per SU‑hour |
| **Chameleon (XSEDE OpenStack)** | 1 vCPU + 1 GiB RAM = **0.5 SU** (1 SU = 1 core + 2 GiB) | **$0.018 / SU‑hr** → $0.009 / hr | $6.48 | $0.60 (≈ $0.02 / GB‑mo) | $9.00 | **$16.08** | No free tier – you pay per SU‑hour |

\* **Monthly compute** assumes a full‑month of 720 hours (30 days × 24 h).  The actual billing period for most clouds is per‑second, but 720 h is a useful reference.  

### How the numbers were derived  

| Component | Source / formula |
|-----------|------------------|
| **AWS t3.micro** | $0.0104 / h (US East (N. Virginia) – Linux on‑demand) – <https://aws.amazon.com/ec2/pricing/on-demand/> |
| **Azure B1s** | $0.008 / h (East US – Linux Pay‑As‑You‑Go) – <https://azure.microsoft.com/pricing/details/virtual-machines/> |
| **GCP e2‑micro** | $0.0060 / h (us‑central1 – Linux) – <https://cloud.google.com/compute/all-pricing> |
| **OCI E2.1‑Micro** | $0.0065 / h (US East (ashburn) – Linux) – <https://www.oracle.com/cloud/compute/pricing.html> |
| **Jetstream 2 SU price** | $0.0085 / SU‑hr (2024 XSEDE rate card) – <https://www.xsede.org/resource/jetstream2> |
| **Chameleon SU price** | $0.018 / SU‑hr (2024 XSEDE rate card) – <https://www.xsede.org/resource/chameleon> |
| **SSD storage** | AWS gp2 $0.10 / GB‑mo, Azure Standard SSD $0.04 / GB‑mo, GCP PD‑Standard $0.04 / GB‑mo, OCI Block Volume $0.025 / GB‑mo, OpenStack (local SSD) ≈ $0.02 / GB‑mo (typical campus‑cluster price). |
| **Outbound data** | AWS $0.09 / GB (first 10 TB), Azure $0.087 / GB (first 5 TB), GCP $0.12 / GB (first 1 TB), OCI $0.09 / GB (first 10 TB).  OpenStack sites charge $0.09 / GB on XSEDE’s “Usage Units” (converted to $). |
| **Free‑tier limits** | AWS 750 h / month t2.micro/t3.micro, Azure 750 h / month B1s, GCP 720 h / month e2‑micro, OCI Always‑Free 1 OCPU + 1 GiB RAM + 100 GB block storage. |

### Interpretation  

| Provider | Cheapest *pay‑as‑you‑go* price (no free tier) | Cheapest *effective* price when the free tier is applicable |
|----------|----------------------------------------------|---------------------------------------------------------------|
| AWS | **$19.49 / mo** (compute + storage + egress) | $0 / mo if you stay ≤ 750 h on the free tier (you still pay for any egress beyond the free‑tier 15 GB/month). |
| Azure | **$15.66 / mo** | $0 / mo if ≤ 750 h on the free tier (egress above 15 GB/mo is billed). |
| GCP | **$17.52 / mo** | $0 / mo if ≤ 720 h on the free tier (egress above 1 GB/mo is billed). |
| OCI | **$14.43 / mo** | $0 / mo *always* (the “Always‑Free” tier already includes 1 OCPU + 1 GiB RAM + 100 GB storage). |
| Jetstream 2 | **$12.66 / mo** (no free tier) | No free tier – you pay per SU‑hour, but the price is already lower than the major public clouds because you are using a research‑focused allocation. |
| Chameleon | **$16.08 / mo** (no free tier) | Same – no free tier, price per SU‑hour is higher than Jetstream 2 but comparable to the commercial clouds. |

### When to choose which platform  

| Use‑case | Recommendation |
|----------|----------------|
| **Purely experimental / learning** – you want *no* cost as long as you stay within a small VM for a month. | **OCI Always‑Free** or **AWS / Azure / GCP free tier** – they all give you a free VM for the first 12 months (OCI’s free tier never expires). |
| **Research projects that need guaranteed allocation and integration with XSEDE resources** | **Jetstream 2** (cheapest per SU‑hour) or **Chameleon** if you need the specific hardware offered there (e.g., GPU‑enabled nodes). |
| **Production or multi‑region workloads** | Choose a commercial cloud with the region, SLA and ecosystem you need. OCI is the cheapest on‑demand for this exact VM size, followed by Azure, GCP, then AWS. |
| **High‑performance networking or large‑scale data egress** | Compare egress rates; AWS and OCI are $0.09 / GB, Azure $0.087 / GB, GCP $0.12 / GB. For heavy outbound traffic, Azure is marginally cheaper, OCI is comparable to AWS, and GCP is the priciest. |
| **Long‑term, predictable usage** | Consider reserved‑instance or committed‑use discounts (30‑ or 3‑year contracts) on AWS, Azure, GCP, OCI – they can reduce the hourly rate by 30‑60 %. Not covered in this “on‑demand” table. |

### Quick reference – cost per hour (compute only)

| Provider | Compute price / h | Equivalent per‑month (720 h) |
|----------|-------------------|------------------------------|
| AWS t3.micro | $0.0104 | $7.49 |
| Azure B1s | $0.0080 | $5.76 |
| GCP e2‑micro | $0.0060 | $4.32 |
| OCI E2.1‑Micro | $0.0065 | $4.68 |
| Jetstream 2 (0.5 SU) | $0.00425 | $3.06 |
| Chameleon (0.5 SU) | $0.0090 | $6.48 |

*(All numbers are rounded to the nearest cent.)*

### Bottom line  

*If you stay within the free allocation*, **OCI** gives you a permanent always‑free VM for $0, which makes it the most cost‑effective choice for a small development box.  
*If you need research‑grade allocations*, **Jetstream 2** is the cheapest per‑hour option (≈ $3 / mo) but you must pay for the usage; **Chameleon** is a little more expensive.  
*If you are looking for a commercial cloud with the broadest ecosystem*, the ordering from cheapest to most expensive (on‑demand) for this particular VM size is: **OCI → Azure → GCP → AWS** (excluding the free‑tier benefit).  

All prices are subject to change; always verify the current rates on the provider’s pricing page before provisioning.