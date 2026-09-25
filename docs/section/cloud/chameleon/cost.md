# Understanding Resource Costs in Chameleon Cloud

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:

    - **Define** the Service Unit (SU) and explain its role as a normalized currency for cloud resources.
    - **Distinguish** between the bare-metal node-hour pricing model and component-based KVM pricing.
    - **Calculate** hourly, weekly, monthly, semester, and yearly SU costs for various virtual machine configurations and bare-metal nodes.
    - **Differentiate** between the costs of compute, specialized hardware, block storage, object storage, network resources, and data egress.
    - **Implement** cost-reduction strategies using pre-emptible instances.
    - **Plan** and justify a project budget based on estimated resource consumption.

## Contextual Overview

In commercial clouds like AWS or Azure, costs are typically calculated in dollars and cents. However, in research-oriented clouds like Chameleon, the primary metric is the **Service Unit (SU)**.

SUs serve as a "virtual currency" that normalizes the value of different hardware resources (CPU, RAM, GPU, Storage) across multiple physical sites. This abstraction allows researchers to receive a single allocation of credits that can be spent flexibly, regardless of whether the underlying hardware is an Intel or AMD processor, or located at TACC, UC, or other member sites. Understanding how to forecast SU usage is critical for ensuring that your research project does not run out of credits mid-experiment, which would lead to the immediate termination of your virtual resources.

---

## The Service Unit (SU) Framework

The SU model converts physical resource consumption over time into a numerical value. Unlike commercial public clouds that bill strictly by granular multi-tenant vCPU allocation, Chameleon utilizes a **bare-metal node-hour model** alongside component-based KVM pricing to ensure full resource isolation for scientific reproducibility.

### Comprehensive Cost & Timeframe Matrix (Bare-Metal & Infrastructure)

To assist with academic planning, grant proposals, and long-term research design, the table below outlines default rates alongside cumulative consumption profiles across common operational windows:

* *1 Week = 168 hours*
* *1 Month = 730 hours*
* *1 Semester (4 Months) = 2,920 hours*
* *1 Year = 8,760 hours*

| Resource Type | Hourly Rate | 1 Week (168 hrs) | 1 Month (730 hrs) | 1 Semester (2,920 hrs) | 1 Year (8,760 hrs) |
| --- | --- | --- | --- | --- | --- |
| **Base Bare Metal Server** | 1.0 SU/hr | 168 SUs | 730 SUs | 2,920 SUs | 8,760 SUs |
| **Specialized BM (GPUs / FPGAs / High-RAM)** | 2.0 SUs/hr | 336 SUs | 1,460 SUs | 5,840 SUs | 17,520 SUs |
| **NVIDIA A100 Node (Single)** | 4.0 SUs/hr | 672 SUs | 2,920 SUs | 11,680 SUs | 35,040 SUs |
| **NVIDIA A100 Node (Quad)** | 16.0 SUs/hr | 2,688 SUs | 11,680 SUs | 46,720 SUs | 140,160 SUs |
| **Block Storage** (per 100 GB) | 0.25 SU/GB-mo | 10.14 SUs* | 25.0 SUs | 100.0 SUs | 300.0 SUs |
| **Floating IP / Active VLAN** | 1.0 SU/hr | 168 SUs | 730 SUs | 2,920 SUs | 8,760 SUs |

**Note: Storage is billed monthly based on capacity, so short-term weekly rates are prorated proportionally.*

**Why this matters:** Because bare-metal nodes are dedicated entirely to a single user to eliminate noisy-neighbor performance interference, they are billed by the node-hour rather than by individual active vCPUs.

---

## KVM@TACC Virtual Machine Costs

In addition to bare-metal servers, Chameleon provides traditional OpenStack KVM instances hosted at the Texas Advanced Computing Center (**KVM@TACC**). Unlike bare-metal nodes which have short maximum lease durations (typically capped at 7 days), KVM@TACC instances are designed for long-term development, staging, and testing, supporting lease durations of up to **6 months**.

### KVM Instance Flavors and Rates Over Time

KVM instances use predefined "flavors" priced at fractional Service Unit (SU) rates per hour, making them significantly more economical for lightweight tasks, continuous development workflows, or long-running database and web services.

| Flavor Name | vCPUs | RAM | SU / Hour | 1 Week (168 hrs) | 1 Month (730 hrs) | 1 Semester (2,920 hrs) | 1 Year (8,760 hrs) | Max Duration |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **m1.tiny** | 1 | 512 MB | 0.01 SU | 1.68 SUs | 7.30 SUs | 29.20 SUs | 87.60 SUs | 6 months |
| **m1.small** | 1 | 2 GB | 0.02 SU | 3.36 SUs | 14.60 SUs | 58.40 SUs | 175.20 SUs | 6 months |
| **m1.medium** | 2 | 4 GB | 0.04 SU | 6.72 SUs | 29.20 SUs | 116.80 SUs | 350.40 SUs | 6 months |
| **m1.large** | 4 | 8 GB | 0.08 SU | 13.44 SUs | 58.40 SUs | 233.60 SUs | 700.80 SUs | 6 months |
| **m1.xlarge** | 8 | 16 GB | 0.15 SU | 25.20 SUs | 109.50 SUs | 438.00 SUs | 1,314.00 SUs | 6 months |
| **m1.xxlarge** | 16 | 32 GB | 0.30 SU | 50.40 SUs | 219.00 SUs | 876.00 SUs | 2,628.00 SUs | 6 months |
| **g1.h100.pci.1** | 24 | 48 GB | 4.00 SUs | 672.00 SUs | 2,920.00 SUs | 11,680.00 SUs | 35,040.00 SUs* | 7 days |
| **g1.h100.pci.4** | 192 | ~1000 GB | 16.00 SUs | 2,688.00 SUs | 11,680.00 SUs | 46,720.00 SUs | 140,160.00 SUs* | 7 days |

**Note: High-end GPU flavors are subject to a maximum 7-day lease policy; long-term cumulative projections are provided for mathematical reference.*

### Key Policy Rules for KVM@TACC

* **Expiration and Shelf Life:** When a project allocation expires, KVM instances are automatically shut down and offloaded to storage after **48 hours**. They can be restored (unshelved) once the allocation is successfully renewed, and are permanently deleted 1 year after expiration.
* **Network & Security Configuration:** Unlike bare-metal nodes, KVM instances require an explicitly associated floating IP address for external access, and security group rules must be manually configured to permit inbound traffic like ICMP (ping) or SSH (port 22).

---

## Calculating Instance and Node Costs

To find the total cost of a project's infrastructure, you must sum the costs of bare-metal node rentals or KVM component instances alongside storage and networking.

### Practical Example: Bare-Metal vs. KVM Node Pricing

* **Standard Bare-Metal Node**: Runs at a flat **1.0 SU/hr**. Over a 7-day max lease (168 hours), a single node consumes `1.0 * 168 = 168 SUs`.
* **NVIDIA A100 Single GPU Node**: Runs at **4.0 SU/hr**. Over a 7-day lease, it consumes `4.0 * 168 = 672 SUs`.
* **KVM `m1.medium` Instance**: Runs at **0.04 SU/hr**. Over a full 4-month semester (2,920 hours), it consumes `0.04 * 2920 = 116.8 SUs`.

### Programmatic Calculation

For complex projects combining bare-metal reservations, KVM instances, and persistent storage, manual calculation is error-prone. The following Python function can be used to automate estimation across custom timeframes.

```python
def calculate_su_cost(hours, standard_bm_nodes=0, a100_nodes=0, kvm_hourly_rate=0.0, block_gb=0, network_ips=0):
    """
    Calculate estimated Service Unit (SU) consumption over an arbitrary 
    number of hours (e.g., 168 for a week, 2920 for a semester).
    """
    # Compute costs
    bm_cost = (standard_bm_nodes * 1.0 * hours) + (a100_nodes * 4.0 * hours)
    kvm_cost = kvm_hourly_rate * hours
    
    # Storage costs prorated by hours (assuming ~730 hours in a standard month)
    storage_monthly = block_gb * 0.25
    storage_cost = storage_monthly * (hours / 730.0)
    
    # Active networking (Floating IPs billed hourly)
    network_cost = network_ips * 1.0 * hours
    
    total_cost = bm_cost + kvm_cost + storage_cost + network_cost
    return total_cost

# Example: 1 Semester (2920 hours) for 1 x m1.large KVM instance, 100GB block storage, and 1 floating IP
semester_estimate = calculate_su_cost(hours=2920, standard_bm_nodes=0, a100_nodes=0, kvm_hourly_rate=0.08, block_gb=100, network_ips=1)
print(f"Estimated Semester Consumption: {semester_estimate:.2f} SUs")

```

---

## Optimization and Cost Reduction

Managing a finite SU budget requires strategic resource allocation.

### Pre-emptible Instances

One of the most effective ways to reduce costs is by using **pre-emptible instances**. These are VMs that can be reclaimed by the cloud provider if other users need the resources. In exchange for this lack of guaranteed availability, they typically receive a **50% discount** on the compute SU rate.

### Storage and Network Efficiency

While compute costs often dominate the budget, storage and networking can become "silent killers" if not managed.

* **Delete unused volumes**: Block storage is charged as long as the volume exists, even if the VM is deleted.
* **Use Object Storage**: For large datasets that do not require a filesystem, Swift (Object Storage) is more cost-effective than Block Storage.
* **Release floating IPs**: Floating IPs left allocated to inactive resources continue accumulating hourly charges.

!!! warning "The Zombie Resource Pitfall"
Deleting a virtual machine or terminating a lease does **not** always automatically release associated floating IPs, active VLANs, or persistent block storage volumes. These "zombie" resources continue to consume SUs every hour (e.g., floating IPs add up to 730 SUs a month if left floating), potentially draining your entire project budget while you are not even using the cloud. Always verify your resource dashboard before logging off.

---

## Summary Checklist

!!! tip "Summary Checklist"
- [ ] I can explain the difference between a Service Unit (SU) and a dollar amount.
- [ ] I understand how bare-metal node-hour pricing differs from KVM fractional hourly rates.
- [ ] I know the SU multiplier rates for specialized hardware and NVIDIA A100 nodes.
- [ ] I can calculate weekly, monthly, semester, and yearly costs for mixed infrastructure fleets.
- [ ] I understand the cost impact of persistent block storage, object storage, and active network IPs.
- [ ] I know how to apply the 50% discount for pre-emptible instances.
- [ ] I have a process for identifying and deleting unused "zombie" resources.

---

## Assignments

!!! note "Assignment 1: Basic Rate Identification"
    Visit the official Chameleon Cloud FAQ. Find the section on allocations and verify the current node-hour SU rate for a standard bare-metal node versus an NVIDIA A100 node. Compare these to the values in this chapter to ensure they are still current.

!!! note "Assignment 2: Semester Budget Projection"
    You are planning a semester-long project (4 months / 2,920 hours) that requires:
    - 1 x `m1.large` KVM instance running continuously for the full semester.
    - 1 x Floating IP address attached to the KVM instance for the entire semester.
    - 200 GB of Block Storage maintained for the full 4 months.
    Calculate the total cumulative SU cost for this configuration over the semester.

!!! note "Assignment 3: Architecture Optimization"
    Your project has a strict budget allocation of 10,000 SUs for the semester. Your current plan running continuous bare-metal nodes exceeds your budget limits by over 50%.
    Propose two specific architectural adjustments (e.g., shifting baseline services to KVM@TACC instances, leveraging 7-day bare-metal bursts only when testing, or cleaning up unreleased floating IPs) to bring the project securely under budget.

---

## Self-Assessment

!!! tip "Self-Assessment"
Test your knowledge by expanding the questions below.

??? question "Why does Chameleon use Service Units (SUs) instead of currency?"
    SUs normalize the cost of different hardware types and sites. This ensures that a researcher's allocation remains consistent in terms of "computing power" regardless of the specific physical hardware used.

??? question "How are standard bare-metal nodes billed compared to KVM instances?"
    Bare-metal nodes are billed at a flat node-hour rate (typically 1.0 SU/hr for standard nodes) to guarantee full physical isolation, whereas KVM instances use granular fractional hourly rates based on vCPU and RAM flavors.

??? question "What is the primary benefit of using KVM@TACC instances over bare metal?"
    KVM@TACC instances offer low fractional hourly SU rates (e.g., 0.04 SU/hr for `m1.medium`) and support extended lease durations of up to 6 months, making them ideal for long-term development and testing.

??? question "If you have a 100GB block storage volume, how many SUs does it cost over a semester (4 months)?"
    At a rate of 0.25 SU / GB-month, a 100GB volume costs 25 SUs per month, which totals 100 SUs across a 4-month semester.

??? question "What is the financial impact of data ingress versus data egress?"
    Data ingress (bringing data into the cloud) is free (0 SU), whereas data egress (sending data out) costs 0.01 SU per GB.

??? question "What is the most common cause of unexpected budget depletion in research clouds?"
    Leaving "zombie" resources—such as unreleased floating IPs, active VLAN reservations, and orphaned block storage volumes—active after the main virtual machine or lease has been terminated.
