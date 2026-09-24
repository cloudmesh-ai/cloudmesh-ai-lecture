# Understanding Resource Costs in Chameleon Cloud

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:

    - **Define** the Service Unit (SU) and explain its role as a normalized currency for cloud resources.
    - **Calculate** the hourly and monthly SU cost for various virtual machine configurations.
    - **Differentiate** between the costs of compute, block storage, object storage, and data egress.
    - **Implement** cost-reduction strategies using pre-emptible instances.
    - **Plan** and justify a project budget based on estimated resource consumption.

## Contextual Overview

In commercial clouds like AWS or Azure, costs are typically calculated in dollars and cents. However, in research-oriented clouds like Chameleon, the primary metric is the **Service Unit (SU)**. 

SUs serve as a "virtual currency" that normalizes the value of different hardware resources (CPU, RAM, GPU, Storage) across multiple physical sites. This abstraction allows researchers to receive a single allocation of credits that can be spent flexibly, regardless of whether the underlying hardware is an Intel or AMD processor, or located at TACC or other member sites. Understanding how to forecast SU usage is critical for ensuring that your research project does not run out of credits mid-experiment, which would lead to the immediate termination of your virtual resources.

## The Service Unit (SU) Framework

The SU model converts physical resource consumption over time into a numerical value. Instead of charging for a "server," Chameleon charges for the specific components that make up that server.

### Resource Rate Table

The following table describes the default rates used to calculate costs in Jetstream and Chameleon environments:

| Resource | Rate | Unit | Description |
| :--- | :--- | :--- | :--- |
| **CPU Core** | 1.0 | SU / core-hour | Every single vCPU consumes 1 SU per hour. |
| **Memory** | 0.5 | SU / GB-hour | Every GB of RAM consumes 0.5 SU per hour. |
| **GPU** | 6.0 | SU / GPU-hour | Each GPU added to an instance adds a significant overhead. |
| **Block Storage** | 0.25 | SU / GB-month | Persistent disks are charged monthly based on size. |
| **Object Storage** | 0.15 | SU / GB-month | Swift storage is slightly cheaper than block storage. |
| **Data Egress** | 0.01 | SU / GB | Moving data *out* of the cloud incurs a small fee. |
| **Data Ingress** | 0.0 | SU / GB | Bringing data *into* the cloud is free. |

**Why this matters:** By decoupling the cost from the specific hardware, the cloud provider can upgrade physical servers or add new sites without forcing researchers to rewrite their budget projections.

## Calculating Instance Costs

To find the total cost of a virtual machine, you must sum the costs of its individual components.

### The Cost Formula

The hourly cost of a standard instance is calculated as:

`Total SU/hour = (vCPUs * 1.0) + (RAM_GB * 0.5) + (GPUs * 6.0)`

### Practical Example: The "m1.medium" Flavor

Consider an instance with 2 vCPUs and 4 GB of RAM:

- **CPU Cost**: 2 cores * 1.0 = 2.0 SU/hr
- **RAM Cost**: 4 GB * 0.5 = 2.0 SU/hr
- **Total**: 4.0 SU/hr

To project this over a full month (approximately 730 hours):
`4.0 SU/hr * 730 hrs = 2,920 SU/month`

### Programmatic Calculation

For complex projects with multiple VMs, manual calculation is error-prone. The following Python function can be used to automate the estimation process.

```python
def calculate_monthly_su(cpus, ram_gb, gpus=0, block_gb=0, object_gb=0, egress_gb=0):
    """
    Calculate the estimated monthly Service Unit (SU) consumption.
    """
    HOURS_PER_MONTH = 730
    
    # Hourly compute costs
    compute_hourly = (cpus * 1.0) + (ram_gb * 0.5) + (gpus * 6.0)
    
    # Monthly storage costs
    storage_monthly = (block_gb * 0.25) + (object_gb * 0.15)
    
    # One-time egress cost
    egress_total = egress_gb * 0.01
    
    total_monthly = (compute_hourly * HOURS_PER_MONTH) + storage_monthly + egress_total
    return total_monthly

# Example: 4 vCPUs, 8GB RAM, 50GB Block Storage, 10GB Egress
estimate = calculate_monthly_su(4, 8, 0, 50, 0, 10)
print(f"Estimated Monthly Consumption: {estimate:.2f} SUs")
```

## Optimization and Cost Reduction

Managing a finite SU budget requires strategic resource allocation.

### Pre-emptible Instances

One of the most effective ways to reduce costs is by using **pre-emptible instances**. These are VMs that can be reclaimed by the cloud provider if other users need the resources. In exchange for this lack of guaranteed availability, they typically receive a **50% discount** on the compute SU rate.

**Why this matters:** Pre-emptible instances are ideal for batch processing, checkpointed simulations, or stateless applications where a sudden reboot is acceptable.

### Storage and Egress Efficiency

While compute costs often dominate the budget, storage can become a "silent killer" if not managed.

- **Delete unused volumes**: Block storage is charged as long as the volume exists, even if the VM is deleted.
- **Use Object Storage**: For large datasets that do not require a filesystem, Swift (Object Storage) is more cost-effective than Block Storage.

!!! warning "The Zombie Resource Pitfall"
    Deleting a virtual machine does **not** always delete its associated floating IPs or block storage volumes. These "zombie" resources continue to consume SUs every hour, potentially draining your entire project budget while you are not even using the cloud. Always verify your resource list before logging off.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] I can explain the difference between a Service Unit (SU) and a dollar amount.
    - [ ] I know the SU rates for CPU, RAM, and GPUs.
    - [ ] I can calculate the hourly and monthly cost of a specific VM flavor.
    - [ ] I understand the cost difference between block and object storage.
    - [ ] I know how to apply the 50% discount for pre-emptible instances.
    - [ ] I have a process for identifying and deleting unused "zombie" resources.

## Practical Exercises

!!! note "Exercise 1: Basic Rate Identification"
    Visit the official Chameleon Cloud FAQ. Find the section on allocations and verify the current SU rate for a single CPU core and 1 GB of RAM. Compare these to the values in this chapter to ensure they are still current.

!!! note "Exercise 2: Budget Projection"
    You are planning an experiment that requires three VMs:
    - 2 x `m1.small` (1 vCPU, 2GB RAM)
    - 1 x `g1.large` (4 vCPUs, 16GB RAM, 1 GPU)
    Calculate the total hourly SU cost for this fleet and the total cost if they run for exactly 14 days.

!!! note "Exercise 3: Architecture Optimization"
    Your project has a strict budget of 10,000 SUs for the month. Your current plan (standard instances) exceeds this by 30%. 
    Propose two specific changes to your architecture (e.g., switching to pre-emptible instances or reducing RAM) to bring the project under budget while maintaining the same number of vCPUs.

## Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

    ??? question "Why does Chameleon use Service Units (SUs) instead of currency?"
        SUs normalize the cost of different hardware types and sites. This ensures that a researcher's allocation remains consistent in terms of "computing power" regardless of the specific physical hardware used.

    ??? question "How does the cost change if you switch a VM from 'Standard' to 'Pre-emptible'?"
        The compute portion of the SU rate (CPU, RAM, and GPU) is reduced by 50%.

    ??? question "If you have a 100GB block storage volume, how many SUs does it cost per month?"
        At a rate of 0.25 SU / GB-month, a 100GB volume costs 25 SUs per month.

    ??? question "What is the financial impact of data ingress versus data egress?"
        Data ingress (bringing data into the cloud) is free (0 SU), whereas data egress (sending data out) costs 0.01 SU per GB.

    ??? question "What is the most common cause of unexpected budget depletion in research clouds?"
        Leaving "zombie" resources—such as floating IPs and block storage volumes—active after the main virtual machine has been deleted.
