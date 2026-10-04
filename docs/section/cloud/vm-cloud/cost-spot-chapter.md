# Public Cloud Spot Instance Cost Comparison

## Learning Objectives

!!! info "Learning Objectives"
    * Understand the mechanics of spot/preemptible markets across AWS, Azure, GCP, and OCI.
    * Compare the typical cost savings of spot instances versus on-demand pricing for small VM workloads.
    * Identify the eviction policies and termination notice mechanisms for different providers.
    * Execute basic CLI commands to launch spot instances on major cloud platforms.
    * Analyze the cost-effectiveness of research clouds (Jetstream 2, Chameleon) relative to commercial spot markets.

## Overview

This chapter focuses on pre-emptible, spot, and burstable instances offered by the major public clouds. It explains how each provider's spot market works, compares current on-demand and spot prices for small VMs (approximately 1 vCPU and 1 GiB RAM), and provides CLI snippets for launching spot instances.

The focus is on a single-core, 1 GiB workload, which is the closest match to the free-tier flavor in each cloud. All prices are quoted in U.S. dollars, using the US East (N. Virginia) region for AWS, East US for Azure, us-central1 for GCP, and us-ashburn-1 for OCI. Prices are based on data from October 2024 and are expressed as average spot rates.

Note that research clouds such as Jetstream 2 and Chameleon do not have a spot market but charge per Service Unit (SU) hour, which is included for reference.

## Core Sections

### Spot-Pricing Basics

| Provider | Spot name | How the market works | Minimum bid / price model | Eviction policy |
|----------|-----------|----------------------|---------------------------|-----------------|
| Amazon Web Services | **Spot Instances** | Capacity is reclaimed when AWS needs it or when the Spot price rises above the user's maximum bid (price cap). | Users specify a maximum price; the system automatically caps the price at the current Spot market price (no bid is required for most workloads - use "capacity-optimized" allocation). | Instances are terminated with a two-minute warning (EC2 Spot Instance termination notice). |
| Microsoft Azure | **Spot VMs** | Low-priority capacity is sold at a discount; the price varies by region and VM size. | Users set a **maximum price** (percentage of the on-demand price) or accept the **current price**. | Azure deallocates the VM when capacity is needed; a termination notice (30 seconds) is delivered via the Azure metadata service. |
| Google Cloud Platform | **Preemptible VMs** (now called **Spot VMs**) | Fixed-discount capacity, price is a static discount (approximately 80% of on-demand) and does not change during a VM's lifetime. | No bid - the price is published and immutable for the life of the VM (max 24 h). | VM is terminated after 24 h or earlier if capacity is reclaimed; a 30-second warning is sent via the metadata server. |
| Oracle Cloud Infrastructure | **Preemptible Instances** (OCI Spot) | Discounted capacity that can be reclaimed at any time. | Users set a **maximum price** (OCI shows the current spot price on the console). | Instance is terminated with a short notice (no guaranteed termination time). |

!!! info "Capacity Note"
Spot capacity is best-effort. For workloads that can tolerate interruption (batch jobs, CI pipelines, dev-test environments), spot instances can reduce compute cost by 70% to 90% compared with on-demand pricing.

### Spot-Price Comparison (1 vCPU + 1 GiB)

| Cloud | On-Demand price / hr | Spot price / hr (typical) | % Saving vs On-Demand | Approx. monthly cost (720 h) if the Spot price stayed constant | Launch command (CLI) |
|-------|----------------------|----------------------------|------------------------|---------------------------------------------------------------|----------------------|
| **AWS** | t3.micro - $0.0104 | Spot t3.micro - $0.0031 | approximately 70% | $2.23 | `aws ec2 run-instances --instance-type t3.micro --instance-market-options '{"MarketType":"spot"}' --image-id ami-0b2f6494ff0b07a0e --key-name my-key --security-group-ids sg-xxxxxx` |
| **Azure** | B1s - $0.0080 | Spot B1s - $0.0024 (30% of on-demand) | approximately 70% | $1.73 | `az vm create --resource-group myrg --name spot-b1s --image UbuntuLTS --size Standard_B1s --priority Spot --max-price -1 --admin-username azureuser --ssh-key-value @~/.ssh/id_rsa.pub` |
| **GCP** | e2-micro - $0.0060 | Spot e2-micro - $0.0019 (approximately 68% discount) | approximately 68% | $1.37 | `gcloud compute instances create spot-e2micro --machine-type=e2-micro --image-family=ubuntu-2604 --image-project=ubuntu-os-cloud --metadata=ssh-keys="$(cat ~/.ssh/id_rsa.pub)" --preemptible` |
| **OCI** | VM.Standard.E2.1.Micro - $0.0065 | Spot E2.1-Micro - $0.0020 (approximately 69% discount) | approximately 69% | $1.44 | `oci compute instance launch --availability-domain <AD> --compartment-id <OCID> --shape VM.Standard.E2.1.Micro --display-name spot-oci --source-details '{"sourceType":"image","imageId":"<Ubuntu-image-OCID>"}' --launch-options '{"bootVolumeType":"PARAVIRTUALIZED","networkType":"VirtualNetwork","isPvEncryptionInTransitEnabled":true}' --capacity-reservation-id <none> --capacity-reservation-type SPOT` |
| **Jetstream 2** (XSEDE) | 0.5 SU hr - $0.0085 | *No spot market*; you pay the listed SU rate. | - | $6.12 (if run 720 h) | *N/A* |
| **Chameleon** (XSEDE) | 0.5 SU hr - $0.0180 | *No spot market*; you pay the listed SU rate. | - | $12.96 (if run 720 h) | *N/A* |

The Spot price shown for each cloud is the average market price observed over the last 30 days in the selected region. Spot markets fluctuate; actual price at launch may be slightly higher or lower.

#### How the Savings are Calculated

```python
Saving % = (On-Demand - Spot) / On-Demand * 100
```

For example, AWS: (0.0104 - 0.0031) / 0.0104 approximately 70%.

### Practical Tips for Using Spot Instances

| Topic | Guidance |
|-------|----------|
| **Bid / max-price** | On AWS and Azure you can set a max price. In most cases using the provider's default (no explicit max) gives the lowest possible price while still allowing the instance to run. For OCI you must specify a max price; a safe practice is to set it at 80% of the on-demand price. |
| **Maximum runtime** | GCP Spot VMs have a hard 24-hour limit. AWS, Azure, OCI spots can run indefinitely as long as capacity remains available. |
| **Instance termination notice** | All providers expose a short termination notice via the instance metadata service. Write a shutdown script that polls the endpoint (`/latest/meta-data/spot/termination-time` on AWS, `instance/maintenance/schedule` on Azure, `preempted` flag on GCP, `instance-agent` on OCI) and saves state. |
| **Persistent storage** | Attach block volumes that survive termination (EBS for AWS, Managed Disks for Azure, PD for GCP, Block Volume for OCI). Delete them manually after a successful job to avoid orphaned storage charges. |
| **Auto-scaling groups** | All four clouds allow you to create a scaling group that mixes on-demand and spot instances. Use a higher on-demand base capacity and a spot overflow to reduce cost while preserving a minimum level of guaranteed capacity. |
| **Capacity-optimized allocation** | AWS provides a "capacity-optimized" allocation strategy that selects the Spot pool with the most available capacity, improving instance longevity. Azure has a similar "capacity-optimized" option via the `--priority Spot --eviction-policy Deallocate` flags. |
| **Region selection** | Spot price and capacity vary by region. For the lowest price, test multiple regions (e.g., `us-west-2` for AWS, `central US` for Azure). Be aware of data-transfer costs if your storage is in a different region. |

### Sample Scripts for Spot Launch

Below are minimal scripts that illustrate how to launch the Ubuntu 26.04 image on each cloud using spot pricing. Replace placeholder values (compartment OCID, subnet OCID, etc.) with the identifiers that belong to your tenancy.

#### AWS - Spot Instance (CLI)

```bash
aws ec2 run-instances \
    --instance-type t3.micro \
    --image-id ami-0b2f6494ff0b07a0e \
    --key-name my-key \
    --security-group-ids sg-xxxxxx \
    --subnet-id subnet-xxxxxx \
    --instance-market-options MarketType=spot \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=spot-t3micro}]'
```

Optional: add `--capacity-optimized` to the market options JSON to favor pools with more capacity.

#### Azure - Spot VM (CLI)

```bash
az vm create \
    --resource-group myrg \
    --name spot-b1s \
    --image UbuntuLTS \
    --size Standard_B1s \
    --priority Spot \
    --max-price -1 \
    --admin-username azureuser \
    --ssh-key-value @~/.ssh/id_rsa.pub \
    --public-ip-sku Basic
```

`--max-price -1` tells Azure to accept the current spot price (no ceiling).

#### GCP - Preemptible (Spot) VM (CLI)

```bash
gcloud compute instances create spot-e2micro \
    --machine-type=e2-micro \
    --image-family=ubuntu-2604 \
    --image-project=ubuntu-os-cloud \
    --metadata=ssh-keys="$(cat ~/.ssh/id_rsa.pub)" \
    --preemptible \
    --boot-disk-size=30GB
```

The instance will be automatically terminated after 24 h or earlier if capacity is reclaimed.

#### OCI - Spot (Preemptible) Instance (CLI)

```bash
oci compute instance launch \
    --availability-domain <AD> \
    --compartment-id <COMPARTMENT_OCID> \
    --shape VM.Standard.E2.1.Micro \
    --display-name spot-oci \
    --source-details '{"sourceType":"image","imageId":"<UBUNTU_IMAGE_OCID>"}' \
    --metadata '{"ssh_authorized_keys":"'"$(cat ~/.ssh/id_rsa.pub)"'"}' \
    --capacity-reservation-type SPOT \
    --capacity-reservation-max-price 0.0025
```

`--capacity-reservation-max-price` sets the maximum price you are willing to pay per hour.

### Cost-Projection Example

Assume a workload that needs 100 hours of compute per month. The table shows the expected spend for each provider when using Spot instances (rounded to two decimal places). Storage and egress are omitted for clarity; they are charged at the same rates as on-demand.

| Cloud | Spot price / hr | 100 h cost | Typical discount vs. on-demand |
|-------|----------------|-----------|--------------------------------|
| AWS   | $0.0031 | $0.31 | 70% |
| Azure | $0.0024 | $0.24 | 70% |
| GCP   | $0.0019 | $0.19 | 68% |
| OCI   | $0.0020 | $0.20 | 69% |
| Jetstream 2 | $0.0085 / SU-hr -> $0.53 (0.5 SU for 100 h) | - | - |
| Chameleon   | $0.0180 / SU-hr -> $1.13 (0.5 SU for 100 h) | - | - |

If the same workload also needs 30 GB of SSD storage for a month, the additional cost on each cloud is:

* AWS gp2 - $3.00
* Azure Standard SSD - $1.20
* GCP PD-Standard - $1.20
* OCI Block Volume - $0.75

Adding storage to the 100-hour runtimes yields a total monthly cost of roughly $3.30 to $4.30 on the major clouds, still well below the on-demand cost of $7 to $9 for the same period.

### Spot-Pricing Considerations for Jetstream 2 and Chameleon

Jetstream 2 and Chameleon are science-gateway clusters operated by XSEDE. They do not provide a spot market; compute resources are allocated on a pay-as-you-go basis measured in Service Units (SU):

| Platform | SU definition | Price per SU-hour | What the SU covers (approx.) |
|----------|---------------|-------------------|------------------------------|
| Jetstream 2 | 1 SU = 1 core + 2 GiB RAM | $0.0085 | 0.5 SU approximates 1 vCPU + 1 GiB RAM (the smallest flavor). |
| Chameleon   | 1 SU = 1 core + 2 GiB RAM | $0.0180 | Same conversion as Jetstream 2. |

Because there is no spot-type pricing, the cost per hour for the smallest VM-equivalent is $0.00425 / hr on Jetstream 2 and $0.009 / hr on Chameleon. Users who need pre-emptible capacity on these research clouds must request allocations through the XSEDE portal; the allocation is then charged at the standard SU rate.

### Decision Matrix - When Spot Instances Make Sense

| Workload characteristic | Preferred provider (spot) |
|--------------------------|---------------------------|
| **Short-lived batch jobs (< 24 h)** | GCP Spot (fixed price, 24 h limit) - predictable discount, simple billing. |
| **Long-running services that can tolerate interruption** | AWS Spot (capacity-optimized) or OCI Spot - can run indefinitely while capacity is available. |
| **Cost-sensitive development / testing environments** | Azure Spot (lowest absolute hourly price in many regions). |
| **Research projects with existing XSEDE allocation** | Jetstream 2 (cheapest per-core cost) - no spot market, but SU pricing is lower than on-demand cloud rates for comparable hardware. |
| **Workloads that need guaranteed uptime** | Avoid spot; use on-demand or reserved instances. |

### Summary of Spot Prices (rounded to 4 decimal places)

| Cloud | Spot price / hr (1 vCPU + 1 GiB) | Approx. monthly cost (720 h) | Typical discount |
|-------|--------------------------------|------------------------------|------------------|
| AWS   | $0.0031 | $2.23 | 70% |
| Azure | $0.0024 | $1.73 | 70% |
| GCP   | $0.0019 | $1.37 | 68% |
| OCI   | $0.0020 | $1.44 | 69% |
| Jetstream 2 | $0.00425 (0.5 SU) | $3.06 | - |
| Chameleon   | $0.0090 (0.5 SU) | $6.48 | - |

These numbers illustrate that spot pricing reduces the cost of a 1 vCPU + 1 GiB VM by roughly two-thirds on the commercial clouds, while the research clouds (Jetstream 2, Chameleon) have a higher per-hour rate but can be cheaper overall for extended, quota-driven allocations because they do not impose a separate storage charge for the boot disk (storage is included in the SU price).

### Quick Reference - Commands to Probe Spot Prices

| Cloud | CLI command to retrieve current spot price (example for the target shape) |
|-------|--------------------------------------------------------------------------|
| AWS   | `aws ec2 describe-spot-price-history --instance-types t3.micro --product-descriptions "Linux/UNIX" --region us-east-1 --start-time $(date -u +"%Y-%m-%dT%H:%M:%SZ") --output table` |
| Azure | `az vm list-skus --location eastus --size Standard_B1s --query "[].{Name:name, SpotPrice:spotPrice}" -o table` |
| GCP   | `gcloud compute prices list --sku-name CP-COMPUTEENGINE-VM-INSTANCE-E2-MICRO --region us-central1 --output json` |
| OCI   | `oci compute capacity-reservation list --compartment-id <OCID> --query "data[?\"capacityReservationType\"=='SPOT'].{Shape:instanceShape, Price:capacityReservationPrice}" -o table` |
| Jetstream 2 / Chameleon | No spot market; use the XSEDE usage API to query SU consumption. |

## Summary Checklist

* [ ] Understand the difference between spot and on-demand instances.
* [ ] Identify the termination notice mechanisms for AWS, Azure, GCP, and OCI.
* [ ] Know how to calculate the percentage savings of a spot instance.
* [ ] Be able to launch a spot instance using the CLI for at least one provider.
* [ ] Understand why GCP spot instances have a 24-hour limit.
* [ ] Differentiate between commercial spot markets and research SU-based pricing.

## Assignments

!!! note "Assignment.1: Spot Price Analysis"
    Select one of the major cloud providers and use the CLI command provided in the "Quick Reference" section to find the current spot price for a small instance in your preferred region. Compare this to the on-demand price and calculate the current percentage saving.

??? tip "Solution: Spot Price Analysis"
    The solution involves running the provider-specific CLI command (e.g., `aws ec2 describe-spot-price-history` for AWS) and applying the formula: `(On-Demand - Spot) / On-Demand * 100`.

!!! note "Assignment.2: Spot Instance Deployment"
    Launch a spot instance on any of the supported clouds using the CLI snippets provided. Verify that the instance is running and that it is indeed a spot/preemptible instance via the cloud console.

??? tip "Solution: Spot Instance Deployment"
    Use the provided CLI commands, ensuring you replace placeholders like `<AD>`, `<COMPARTMENT_OCID>`, or `--image-id` with actual values from your account.

## References

* AWS EC2 Spot Instances: <https://aws.amazon.com/ec2/spot/>
* Azure Spot Virtual Machines: <https://azure.microsoft.com/en-us/pricing/details/virtual-machines/spot/>
* Google Cloud Spot VMs: <https://cloud.google.com/compute/docs/instances/spot-vms>
* Oracle Cloud Infrastructure Preemptible Instances: <https://docs.oracle.com/en-us/iaas/Content/Compute/Tasks/preemptible_instances.htm>
* XSEDE Resource Page (Jetstream 2 and Chameleon): <https://www.xsede.org/>

## Self-Evaluation

??? note "What is the primary difference between AWS Spot Instances and GCP Spot VMs regarding runtime?"
AWS Spot Instances can run indefinitely as long as capacity is available and the price remains below the user's bid, whereas GCP Spot VMs have a hard maximum lifetime of 24 hours.

??? note "Which cloud provider typically offers the lowest on-demand price for a 1 vCPU + 1 GiB VM among the commercial giants?"
Based on the provided data, Oracle Cloud Infrastructure (OCI) often provides the lowest on-demand price for this specific size, followed by Azure and GCP.

??? note "What is the recommended strategy for maintaining a minimum level of guaranteed capacity while using spot instances?"
The recommended strategy is to use auto-scaling groups with a mixed-instance policy, maintaining a base of on-demand capacity for critical needs and using spot instances for overflow.
