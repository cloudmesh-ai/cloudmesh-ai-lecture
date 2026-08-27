# Cost

Here is a comparison table featuring **approximate monthly costs** for a standard general-purpose virtual machine (configured with **4 vCPU and 16 GB of RAM**) running continuously 24/7 (approx. 730 hours in a month) on-demand.

### VM Cost & Monthly Expense Comparison Table

| Feature / Dimension | Amazon Web Services (AWS) | Microsoft Azure | Google Cloud Platform (GCP) |
| --- | --- | --- | --- |
| **Equivalent General Purpose Instance** | `m7i.xlarge` (4 vCPU, 16 GB) | `Standard_D4s_v5` (4 vCPU, 16 GB) | `n2-standard-4` (4 vCPU, 16 GB) |
| **Approx. On-Demand Base Rate** | ~$0.202 / hour | ~$0.192 / hour | ~$0.194 / hour |
| **Estimated Cost Per Month** *(24/7 Continuous Uptime)* | **~$147 / month** | **~$140 / month** | **~$142 / month** |
| **Estimated Cost with 1-Yr Commitment** | **~$40 – $45 / month** *(Using Savings Plans / RIs)* | **~$40 – $45 / month** *(Using Azure Savings Plans / RIs)* | **~$45 – $50 / month** *(Using Committed Use Discounts)* |
| **Estimated Spot / Preemptible Cost** | **~$15 – $30 / month** *(Up to ~70-80% off)* | **~$15 – $30 / month** *(Up to ~70-80% off)* | **~$35 – $40 / month** *(Varies heavily by region)* |
| **Billing Increments** | Per-second (after 60-sec min. for some) | Per-second (containers/some) to minute-based | True per-second billing (1-min minimum) |
| **Customizability** | Fixed instance shapes | Fixed instance shapes grouped by family | **Custom Machine Types** (Mix/match vCPU and RAM to scale monthly costs down if you need less memory) |
| **Data Egress (Outbound Traffic)** | First 1 GB free, tiered down to ~$0.05–$0.09 / GB | First 5 GB free, competitive tiered outbound pricing | Generally higher standard per-GB internet egress rates |

---

### Important Notes on Monthly Billing:

1. **The 730-Hour Math:** Monthly figures are calculated based on a full 24/7 runtime ($730 \text{ hours} \times \text{hourly rate}$). If you turn off your development VMs on nights and weekends (running them roughly 160 hours a month instead), your monthly bill will drop by about 75%.
2. **Additional Storage Costs Are Separate:** The figures above represent **compute-only** costs. Standard block storage (such as AWS EBS, Azure Managed Disks, or GCP Persistent Disk) is billed separately—typically adding an extra **$5 to $15 per month** depending on whether you choose standard SSD or high-performance storage capacity (e.g., 50 GB to 100 GB).


### Startup cost 

Major cloud providers **do not charge an upfront activation or "startup fee"** just to launch or boot up a virtual machine. You only pay for the time the machine is actively running, measured down to the second (with a 1-minute minimum charge on AWS and GCP when you first boot).

### Traps

There are a few important cost traps related to starting and stopping VMs that catch many users off guard:

#### 1. The Minimum Billing Threshold

* **AWS & GCP:** When you turn on a VM, they enforce a **1-minute minimum charge**. If you boot up a VM, run a script for 10 seconds, and immediately shut it down, you will be billed for 1 full minute of compute time. After that first minute, billing is strictly per-second.

#### 2. "Stopped" Does Not Always Mean "Free"

If you shut down a VM to stop paying for compute, you must ensure it is fully released from the underlying hardware:

* **AWS:** Stopping an EC2 instance stops compute charges immediately, but **storage (EBS) and any Elastic IP addresses will continue to cost money** while it sits idle.
* **Azure:** If you shut down a VM from *inside* the guest operating system (like typing `shutdown` in Linux), Azure keeps the hardware allocated and **continues billing you for compute**. You must explicitly use the Azure portal or CLI to **Stop (Deallocate)** the VM to stop compute charges. Like AWS, attached managed disks will still incur storage fees.
* **GCP:** Stopping a Compute Engine instance halts CPU/GPU charges, but attached **persistent disks and static IP addresses keep billing** until deleted.

### Summary

Launching a VM is free; you only pay for active runtime. To truly stop accumulating charges when you are done using a VM, you must either **terminate/delete it** entirely or ensure it is fully stopped/deallocated so that you are only left paying for the passive storage (hard drive space) it occupies.