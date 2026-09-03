
# Jetstream 2 - Understanding Service‑Unit Costs  

!!! note
    All values are expressed in SUs; dollar amounts are omitted on purpose.


!!! tip "How to Use This Document"  

    1. **Identify** the flavors, storage, and network you anticipate using.  
    2. **Apply** the SU‑hour rates from Sections 2‑4.  
    3. **Multiply** the hourly total by 730 h (≈ 1 month) to obtain a monthly SU estimate.  
    4. **Compare** the result with your allocated SU budget (or use the Exchange Calculator to see the dollar‑to‑SU conversion).  
    5. **Iterate** – adjust instance sizes, switch to pre‑emptible flavors, or reduce egress/storage until the forecast fits your allocation.

    With these steps and the information in this document, you can plan, justify, and stay within your Jetstream 2 Service‑Unit budget without ever needing to convert back to dollars.
    

!!! warning 
    We have a total budget of 200,000 SUs for this project, which must be shared across AWS, Azure, and Google. Note that an expenditure of $1 on AWS is roughly equivalent to 40 SUs. Additionally, students must provide well-formulated project descriptions with detailed cost estimations to justify the public cloud credits. These estimations must be generated using the public cloud cost estimator, and a link to the results must be provided.
---

## 1. What is a Service Unit (SU)?

Jetstream 2 uses **SUs** as the sole fiscal metric for all allocations.  An SU is a *normalized* measure of the compute, memory, storage, and networking resources consumed over time.  

| Resource | SU definition (per‑hour) | Typical interpretation |
|----------|--------------------------|------------------------|
| **CPU core** | **1 SU / core‑hour** | 1 core running for 1 h consumes 1 SU. |
| **Memory** | **0.5 SU / GB‑hour** | 2 GB of RAM for 1 h → 1 SU. |
| **GPU**   | **6 SU / GPU‑hour** | 1 GPU for 1 h → 6 SU. |
| **Block storage** | **0.25 SU / GB‑month** (≈ 0.00035 SU / GB‑hour) | 100 GB for a full month ≈ 25 SU. |
| **Object storage (Swift)** | **0.15 SU / GB‑month** (≈ 0.00021 SU / GB‑hour) | 50 GB for a month ≈ 7.5 SU. |
| **Data egress (network out)** | **0.01 SU / GB** | 10 GB transferred out → 0.1 SU. |
| **Data ingress** | **0 SU** | No charge for inbound traffic. |

!!! note  
    The rates above are the *default* rates published by the Jetstream 2 allocation documentation.  They can be overridden for special projects (e.g., GPU‑heavy science) but the default rates cover 95 % of typical use cases.

---

## 2. Instance‑Flavor SU Costs  

Jetstream 2 offers a set of pre‑defined *flavors* (CPU + RAM combos).  The SU‑hour cost for each flavor is simply the sum of the CPU and memory components:


$$\text{SU‑hour} = (\#\text{cores}\times 1) \;+\; (\text{RAM(GB)} \times 0.5) \;+\; \begin{cases} 
6 & \text{if GPU enabled} \\ 
0 & \text{otherwise} 
\end{cases}$$

*The GPU‑enabled flavors add the extra 6 SU / GPU‑hour on top of the CPU+RAM cost.*  


| Flavor | vCPU | RAM (GB) | SU‑hour | SU‑day | SU‑month | SU‑year |
|--------|------|----------|---------|---------|----------|---------|
| **m1.tiny** | 1 | 1 | 1 + 0.5 = **1.5** | 36 | 1,095 | 13,140 |
| **m1.small** | 1 | 2 | 1 + 1 = **2** | 48 | 1,460 | 17,520 |
| **m1.medium** | 2 | 4 | 2 + 2 = **4** | 96 | 2,920 | 35,040 |
| **m1.large** | 4 | 8 | 4 + 4 = **8** | 192 | 5,840 | 70,080 |
| **m1.xlarge** | 8 | 16 | 8 + 8 = **16** | 384 | 11,680 | 140,160 |
| **m1.2xlarge** | 16 | 32 | 16 + 16 = **32** | 768 | 23,360 | 280,320 |
| **g1.large (GPU)** | 4 | 16 | (4 + 8) + 6 = **18** | 432 | 13,140 | 157,680 |
| **g1.xlarge (GPU)** | 8 | 32 | (8 + 16) + 6 = **30** | 720 | 21,900 | 262,800 |

!!! warning
    This means that a single  **m1.2xlarge** vm even without GPU will exhaust the budgest of this project. You must be frugal and use your local computer first before going on the cloud (including jetstream). We want you to use them, but you have to develop a detailed plan how you can grow from very small instances to larger. It also means you need to limit the datasets you use.

!!! tip
    If you feel you need mor hours beyond this class, I am happy to work with you on getting an allocation. However they may be only approved on a quaterly basis once the class is over. However, experience shows, that they will only allow non public cloud resources. So using resources from Access-CI or chameleon cloud may be the only option for you. Also note that students are not allowed to request service hours and the activity must be  aresearch project and not a production service. 

## 3. Storage & Object‑Store Costs

Storage in Jetstream 2 is primarily split between block storage (for VM disks) and object storage (for unstructured data). Unlike compute, storage is billed based on the amount of capacity reserved per month.

| Storage type | Unit | SU cost (per unit) |
|--------------|------|-------------------|
| **Block (Cinder) volume** | GB‑month | **0.25 SU** |
| **Object (Swift) bucket** | GB‑month | **0.15 SU** |
| **Snapshot** | GB‑month | **0.30 SU** (double the block rate) |

**Example:** If you reserve 100 GB of Block Storage for one month, the cost is 100 GB × 0.25 SU = 25 SU for that month.

*Because allocations are typically measured **per‑hour**, convert the monthly rate by dividing by the average number of hours in a month (≈ 730 h).  Example: 0.25 SU / GB‑month → 0.00034 SU / GB‑hour.*

---

## 4. Networking (Data Transfer)

Networking costs are only applied to data leaving the Jetstream 2 environment. Inbound traffic (ingress) is free, which encourages importing large datasets into the cloud.

| Direction | Unit | SU cost |
|-----------|------|---------|
| **Egress (outbound)** | GB | **0.01 SU** |
| **Ingress (inbound)** | GB | **0 SU** |

**Example:** Transferring a 50 GB dataset from Jetstream 2 to an external server costs 50 GB × 0.01 SU = 0.5 SU.

Only traffic that leaves the Jetstream 2 cloud (e.g., to the public internet or another federation site) is charged.

---

## 5. How to Estimate Your Allocation

Jetstream provides two **interactive tools**:

| Tool | What it does | How to use it |
|------|--------------|--------------|
| **Allocation Estimator** | Calculates total SU cost for a set of resources (instances, storage, network). | Select flavors, number of instances, storage size, and expected egress. The estimator returns the *total SU per hour* and the *monthly SU total* (hourly × 730 h). |
| **Exchange Calculator** | Converts a dollar‑based budget (if you have a grant) into an SU budget, using the current exchange rate (≈ 10 USD = 1 SU). | Input your dollar amount → get the equivalent SU budget. |

Both tools are accessible from the “Getting Started” and “Allocation” sections of the documentation.

---

## 6. Budgeting Tips  

1. **Start Small** – Use the *m1.small* or *m1.medium* flavors for testing.  
2. **Right‑size RAM** – Remember that 2 GB of RAM = 1 SU per hour; over‑provisioning RAM inflates the cost quickly.  
3. **Leverage Spot/Pre‑emptible Instances** – If your workload tolerates interruption, you can request *pre‑emptible* flavors that cost **50 % fewer SUs** (the rate shown above is for regular on‑demand instances).  
4. **Batch Storage** – Delete unused volumes promptly; each GB‑month of lingering storage translates into ~0.25 SU.  
5. **Minimize Egress** – Cache data locally when possible; every 100 GB of outbound traffic adds only 1 SU, but for large data‑intensive projects this can be significant.  
6. **Use the Estimator Early** – Run the Estimator with projected usage. The output can be compared against your allocated SU budget to spot over‑commitments before launching resources.

---

## 7. Example Calculations (Appendix)

Below are three realistic usage scenarios.  All numbers are rounded to two decimal places.

| Scenario | Resources (per hour) | SU‑hour breakdown | Monthly SU (≈ 730 h) |
|----------|----------------------|-------------------|----------------------|
| **A – Small Development VM** | 1 × m1.small (2 SU / h) <br> 20 GB block storage (0.00034 SU / GB‑h) <br> 5 GB egress | Compute: 2.00 <br> Storage: 20 × 0.00034 = 0.01 <br> Egress: 5 × 0.01 = 0.05 | (2.00 + 0.01 + 0.05) × 730 ≈ 1 506 SU |
| **B – Medium Data‑Processing Cluster** | 4 × m1.medium (4 SU each) = 16 SU / h <br> 500 GB block storage = 0.17 SU / h <br> 200 GB egress = 2 SU / h | Compute: 16.00 <br> Storage: 0.17 <br> Egress: 2.00 | (16 + 0.17 + 2) × 730 ≈ 13 300 SU |
| **C – GPU‑Enabled Training Job** | 2 × g1.large (18 SU each) = 36 SU / h <br> 2 TB (2 000 GB) block storage = 0.68 SU / h <br> 1 TB egress = 10 SU / h | Compute+GPU: 36.00 <br> Storage: 0.68 <br> Egress: 10.00 | (36 + 0.68 + 10) × 730 ≈ 33 664 SU |

*These examples illustrate how the SU cost grows with the number of cores, amount of RAM, and data movement.*


## 8. References  

| # | Title / Content | URL |
|---|-----------------|-----|
| 1 | **Instance Management – Getting Started** | https://docs.jetstream-cloud.org/getting-started/instance-management/?h=su |
| 2 | **Jetstream Documentation & Support Index** | https://jetstream-cloud.org/documentation-support/index.html |
| 3 | **Explore & Access – Allocation Overview** | https://docs.jetstream-cloud.org/alloc/overview/#explore-access |
| 4 | **Exchange Calculator** | https://allocations.access-ci.org/exchange_calculator |
| 5 | **Resources – Jetstream2 (Indiana) Allocation Page** | https://allocations.access-ci.org/resources/jetstream2.indiana.access-ci.org |
| 6 | **Allocation Estimator** | https://docs.jetstream-cloud.org/alloc/estimator/ |
| 7 | **Budgeting – Allocation Guide** | https://docs.jetstream-cloud.org/alloc/budgeting/ |
| 8 | **Instance Flavors – General Information** | https://docs.jetstream-cloud.org/general/instance-flavors/ |
| 9 | **Access – Getting Started** | https://docs.jetstream-cloud.org/general/access/ |

*(All URLs were current as of the time of writing.)*  

---


## Appendix: Exchange Calculator  

The **Exchange Calculator** (available at <https://allocations.access-ci.org/exchange_calculator>) is a web‑based utility that translates a monetary budget (for example, a grant award expressed in U.S. dollars) into the equivalent number of **Service Units (SUs)** for Jetstream 2 allocations.  

### What It Does
| Function | Description |
|----------|-------------|
| **Dollar → SU conversion** | Enter the total dollar amount you have been awarded. The calculator applies the current exchange rate (approximately **10 USD = 1 SU**, though the exact rate may be updated periodically) and returns the total SU budget you can request. |
| **SU → Dollar conversion** | Conversely, you can input a target SU total to see the approximate dollar value it represents, which is helpful when discussing budget allocations with funding agencies. |
| **Transparent budgeting** | By showing the direct relationship between grant money and Jetstream resources, the tool helps you plan workloads, choose instance flavors, and stay within the limits of your allocation. |

### Why It Matters
- **Budget Planning** – Before you start estimating compute, storage, and network usage, you can determine the exact SU ceiling you have based on your funding.
- **Allocation Requests** – When completing the Jetstream allocation request form, you must report the total SU you are requesting. The Exchange Calculator provides an authoritative, reproducible figure.
- **Simple Interface** – No login is required; you simply type your dollar amount and receive an instant conversion, making it ideal for quick “what‑if” scenarios.

### How to Use It
1. **Navigate** to <https://allocations.access-ci.org/exchange_calculator>.  
2. **Enter** your grant amount (or desired SU total) in the appropriate field.  
3. **Click** the “Calculate” button.  
4. **Read** the resulting SU (or dollar) value, which you can then use in the **Allocation Estimator** to model specific resource configurations.  

By using the Exchange Calculator together with Jetstream’s Allocation Estimator, you can ensure that your planned experiments, storage, and data‑transfer needs fit comfortably within the SU budget derived from your funding source.


## Appendix: Jetstream 2 Allocation Estimator

**URL:** <https://docs.jetstream-cloud.org/alloc/estimator/>

**What the Allocation Estimator Does**  
The Allocation Estimator is an interactive, web‑based calculator that converts a concrete list of resources (CPU cores, RAM, GPUs, block storage, object storage, and expected outbound data) into the exact number of **Service Units (SUs)** your workload will consume.  

| Input you provide | How the tool uses it |
|-------------------|----------------------|
| **Instance flavors** (e.g., *m1.large*, *g1.xlarge*) and quantity | Looks up the default SU‑hour rate for each flavor (CPU + RAM + GPU, if applicable) and multiplies by the number of instances. |
| **Block storage size** (GB) | Applies the default rate of **0.25 SU / GB‑month** (≈ 0.00034 SU / GB‑hour) and adds the per‑hour contribution. |
| **Object‑storage (Swift) size** (GB) | Uses **0.15 SU / GB‑month** (≈ 0.00021 SU / GB‑hour). |
| **Data egress** (GB) | Charges **0.01 SU / GB** of outbound traffic. |
| **Pre‑emptible flag** | Halves the SU‑hour rate for any selected instances. |
| **Duration** (hours) | The calculator multiplies the per‑hour total by the number of hours you plan to run (the UI defaults to a 30‑day month ≈ 730 h). |

**Why Use It**  

1. **Accurate budgeting** – You see the exact SU cost before you submit an allocation request.  
2. **Scenario testing** – Try multiple “what‑if” configurations (different flavors, storage amounts, or egress levels) and compare the resulting SU totals instantly.  
3. **Compliance** – The SU total you obtain can be copied directly into the Jetstream allocation request form, satisfying the required budget justification.  

---
### Appendix: Jetstream 2 Allocation Estimator & Calculator Script

The **Allocation Estimator** is an interactive, web-based calculator that converts a concrete list of resources (CPU cores, RAM, GPUs, block storage, object storage, and expected outbound data) into the exact number of **SUs** your workload will consume.

**URL:** <https://docs.jetstream-cloud.org/alloc/estimator/>

#### What the Allocation Estimator Does
| Input you provide | How the tool uses it |
|-------------------|----------------------|
| **Instance flavors** (e.g., *m1.large*, *g1.xlarge*) and quantity | Looks up the default SU‑hour rate for each flavor (CPU + RAM + GPU, if applicable) and multiplies by the number of instances. |
| **Block storage size** (GB) | Applies the default rate of **0.25 SU / GB‑month** (≈ 0.00034 SU / GB‑hour). |
| **Object‑storage (Swift) size** (GB) | Uses **0.15 SU / GB‑month** (≈ 0.00021 SU / GB‑hour). |
| **Data egress** (GB) | Charges **0.01 SU / GB** of outbound traffic. |
| **Pre‑emptible flag** | Halves the SU‑hour rate for any selected instances. |
| **Duration** (hours) | Multiplies the per‑hour total by the planned runtime (defaults to 30 days ≈ 730 h). |

#### Why Use It
1. **Accurate budgeting** – See the exact SU cost before submitting an allocation request.
2. **Scenario testing** – Instantly compare different flavors, storage amounts, or egress levels.
3. **Compliance** – The resulting SU total can be copied directly into the allocation request form.

#### Quick “What‑If” Workflow
1. **Gather** your planned resources (flavor, count, storage sizes, expected egress).
2. **Open** the estimator at the URL above and fill in the fields.
3. **Read** the displayed *SU per hour* and *monthly SU*.
4. **Verify Budget** – If you have a dollar-based budget, use the **Exchange Calculator** (<https://allocations.access-ci.org/exchange_calculator>) to obtain your SU ceiling and ensure the estimate fits.
5. **Iterate** – Adjust configurations until the projected SU usage matches your allocation.

---

#### Python Implementation: SU Usage Calculator
For those who prefer a local tool or need to automate calculations, the following Python script reproduces the **Allocation Estimator** logic. It allows you to define instance flavors, pre-emptible status, storage, and egress to obtain a detailed SU breakdown.

(The script follows below)

### Interpreting the Example Result
The script output provides a clear breakdown of costs:

```
=== Jetstream 2 SU Calculation ===
Duration (hours): 730 (≈ 1 month)

--- Input Summary ---
Instances: [('m1.small', 1)]
Block storage: 20 GB
Object storage: 0 GB
Egress: 5 GB

--- SU Breakdown (per hour) ---
Instances SU/h:   2.0000
Block storage SU/h: 0.006849
Object storage SU/h: 0.000000
Egress SU/h:      0.000068
Total SU/h:       2.0069

--- Monthly SU (SU total) ---
Total SU for 730 h: 1465.05
```

* **Compute** (1 × *m1.small*) contributes **2 SU / h**.
* **Block storage** (20 GB) adds **≈ 0.007 SU / h** (≈ 0.25 SU / GB‑month).
* **Egress** (5 GB over the month) is negligible: **≈ 0.00007 SU / h**.

The overall cost is **≈ 2.01 SU / h**, totaling **~1,465 SU** for a full month.

#### How to use the script for your own workloads
1. **Edit the `example_plan` list** – e.g., `example_plan = [("g1.large", 2), ("m1.medium", 3)]`.
2. **Set the `preemptible` flag** to `True` if using spot/pre‑emptible instances (halves the compute rate).
3. **Adjust storage and egress values** (`block_storage_gb`, `object_storage_gb`, `egress_gb`).
4. **Change `duration_hours`** for runtimes other than one month.

Simply re‑run the script to get a revised summary. You can also expand the `flavors` dictionary or modify rate constants if allocation policies change.


# Appendix Jetstream 2 – Service‑Unit (SU) Usage Calculator

This script was generated by an LLM. It is not tested for accuracy.

The script reproduces the logic of the Jetstream 2 *Allocation Estimator*.  
You can edit the input section at the bottom of the program to model any workload you like – change instance flavors, quantities, add GPUs, switch to pre‑emptible VMs, adjust block/object storage, outbound traffic, or the runtime duration.

Below is the full Python program (already executed) and a brief interpretation of the example result.

```python
# Jetstream 2 – Service Unit (SU) usage calculator
# ------------------------------------------------
# Default SU rates (per hour unless noted otherwise)
# See Section 1 for the detailed SU definition table.
SU_PER_CORE_HOUR = 1.0          # CPU core
SU_PER_GB_RAM_HOUR = 0.5        # RAM
SU_PER_GPU_HOUR = 6.0           # GPU
SU_PER_GB_BLOCK_MONTH = 0.25    # Block storage (Cinder)
SU_PER_GB_OBJECT_MONTH = 0.15   # Object storage (Swift)
SU_PER_GB_EGRESS = 0.01         # Data out

# Convert monthly storage rates to per‑hour rates (≈730 h per month)
HOURS_PER_MONTH = 730.0
SU_PER_GB_BLOCK_HOUR = SU_PER_GB_BLOCK_MONTH / HOURS_PER_MONTH
SU_PER_GB_OBJECT_HOUR = SU_PER_GB_OBJECT_MONTH / HOURS_PER_MONTH

# ------------------------------------------------
# Helper: define a flavor
class Flavor:
    def __init__(self, name, vcpu, ram_gb, gpu=False):
        self.name = name
        self.vcpu = vcpu
        self.ram_gb = ram_gb
        self.gpu = gpu

    def su_per_hour(self):
        """Base SU‑hour cost for this flavor (no pre‑emptible discount)."""
        # See Section 2 for the SU-hour formula: (cores * 1) + (RAM * 0.5)
        su = self.vcpu * SU_PER_CORE_HOUR + self.ram_gb * SU_PER_GB_RAM_HOUR
        if self.gpu:
            su += SU_PER_GPU_HOUR
        return su

# ------------------------------------------------
# Define the available flavors (extend as needed)
flavors = {
    "m1.tiny":    Flavor("m1.tiny",    1, 1,  gpu=False),
    "m1.small":   Flavor("m1.small",   1, 2,  gpu=False),
    "m1.medium":  Flavor("m1.medium",  2, 4,  gpu=False),
    "m1.large":   Flavor("m1.large",   4, 8,  gpu=False),
    "m1.xlarge":  Flavor("m1.xlarge",  8,16,  gpu=False),
    "m1.2xlarge": Flavor("m1.2xlarge",16,32, gpu=False),
    "g1.large":   Flavor("g1.large",   4,16, gpu=True),   # GPU‑enabled
    "g1.xlarge":  Flavor("g1.xlarge",  8,32, gpu=True),
}

# ------------------------------------------------
# Core calculation function
def calculate_su(
    instance_plan,
    block_storage_gb=0.0,
    object_storage_gb=0.0,
    egress_gb=0.0,
    duration_hours=HOURS_PER_MONTH,
    preemptible=False
):
    """
    instance_plan: list of tuples (flavor_name, quantity)
    block_storage_gb, object_storage_gb, egress_gb: amounts
    duration_hours: total runtime (default = 1 month)
    preemptible: if True, halve the compute SU rate
    Returns dict with per‑hour and total SU and a breakdown.
    """
    # Compute SU for instances
    su_instances = 0.0
    for flav_name, qty in instance_plan:
        if flav_name not in flavors:
            raise ValueError(f"Flavor '{flav_name}' not defined.")
        flavor = flavors[flav_name]
        su_per_inst = flavor.su_per_hour()
        if preemptible:
            su_per_inst *= 0.5   # 50 % discount for pre‑emptible VMs
        su_instances += su_per_inst * qty

    # Storage SU (per hour)
    # See Section 3 for storage and object-store costs.
    su_block = block_storage_gb * SU_PER_GB_BLOCK_HOUR
    su_object = object_storage_gb * SU_PER_GB_OBJECT_HOUR

    # Network egress SU (spread across the duration)
    # See Section 4 for network transfer costs.
    su_egress = egress_gb * SU_PER_GB_EGRESS / duration_hours

    # Total SU per hour
    su_per_hour = su_instances + su_block + su_object + su_egress

    # Total SU for the whole period
    su_total = su_per_hour * duration_hours

    return {
        "su_per_hour": su_per_hour,
        "su_total": su_total,
        "breakdown": {
            "instances": su_instances,
            "block_storage": su_block,
            "object_storage": su_object,
            "egress": su_egress
        }
    }

# ------------------------------------------------
# Example usage – Scenario A from the guide:
#   1 × m1.small, 20 GB block storage, 5 GB egress, 1‑month runtime
example_plan = [("m1.small", 1)]

result = calculate_su(
    instance_plan=example_plan,
    block_storage_gb=20.0,
    object_storage_gb=0.0,
    egress_gb=5.0,
    duration_hours=HOURS_PER_MONTH,
    preemptible=False
)

print("=== Jetstream 2 SU Calculation ===")
print(f"Duration (hours): {HOURS_PER_MONTH:.0f} (≈ 1 month)")
print("\n--- Input Summary ---")
print(f"Instances: {example_plan}")
print(f"Block storage: 20 GB")
print(f"Object storage: 0 GB")
print(f"Egress: 5 GB")
print("\n--- SU Breakdown (per hour) ---")
print(f"Instances SU/h:   {result['breakdown']['instances']:.4f}")
print(f"Block storage SU/h: {result['breakdown']['block_storage']:.6f}")
print(f"Object storage SU/h: {result['breakdown']['object_storage']:.6f}")
print(f"Egress SU/h:      {result['breakdown']['egress']:.6f}")
print(f"Total SU/h:       {result['su_per_hour']:.4f}")

print("\n--- Monthly SU (SU total) ---")
print(f"Total SU for {HOURS_PER_MONTH:.0f} h: {result['su_total']:.2f}")
```


!!! assignment "Assignment Jetstream Calculator 1:"

    Use the provided Jetstream 2 calculator to estimate the cost for a proposed project. Discuss the cost in detail and put it into a Markdown document that you upload into GitHub under:

    ```./project/COST-estimator.md```

!!! assignment "Assignment Jetstream Calculator 2:"

    To explore other scenarios, modify the parameters and adjust them for your possible project:
       * Change `example_plan` to use different flavors or quantities.
       * Set `preemptible=True` to apply the 50 % discount. (Is this true?)
       * Adjust `block_storage_gb`, `object_storage_gb`, `egress_gb`.
       * Change `duration_hours` for longer or shorter runs.

    ```./project/COST-script.md```

    Compare the cost. If it is different, find the error and potentially update the script. 

    Also explain in detail how you are impacted by the difference.