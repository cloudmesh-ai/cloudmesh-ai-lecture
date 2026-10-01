import re

file_path = '/Users/grey/work/cloudmesh-ai-lecture/docs/section/cloud/jetstream/jeststream-cost.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Section 3 and 4
# We find the block from ## 3. Storage to the end of Section 4 (before ## 5. How to Estimate)
pattern = r'(## 3\. Storage & Object‑Store Costs.*?)(\n\n## 5\. How to Estimate Your Allocation)'
replacement = r'\1\n\n## 3. Storage & Object‑Store Costs\n\nStorage in Jetstream 2 is primarily split between block storage (for VM disks) and object storage (for unstructured data). Unlike compute, storage is billed based on the amount of capacity reserved per month.\n\n| Storage type | Unit | SU cost (per unit) |\n|--------------|------|-------------------|\n| **Block (Cinder) volume** | GB‑month | **0.25 SU** |\n| **Object (Swift) bucket** | GB‑month | **0.15 SU** |\n| **Snapshot** | GB‑month | **0.30 SU** (double the block rate) |\n\n**Example:** If you reserve 100 GB of Block Storage for one month, the cost is 100 GB × 0.25 SU = 25 SU for that month.\n\n*Because allocations are typically measured **per‑hour**, convert the monthly rate by dividing by the average number of hours in a month (≈ 730 h).  Example: 0.25 SU / GB‑month → 0.00034 SU / GB‑hour.*\n\n---\n\n## 4. Networking (Data Transfer)\n\nNetworking costs are only applied to data leaving the Jetstream 2 environment. Inbound traffic (ingress) is free, which encourages importing large datasets into the cloud.\n\n| Direction | Unit | SU cost |\n|-----------|------|---------|\n| **Egress (outbound)** | GB | **0.01 SU** |\n| **Ingress (inbound)** | GB | **0 SU** |\n\n**Example:** Transferring a 50 GB dataset from Jetstream 2 to an external server costs 50 GB × 0.01 SU = 0.5 SU.\n\nOnly traffic that leaves the Jetstream 2 cloud (e.g., to the public internet or another federation site) is charged.\n\n---\n\n\2'
# Wait, the regex is a bit tricky. Let's just replace the whole chunk from ## 3. to ## 5.

# Better approach: split and replace
parts = re.split(r'(## 3\. Storage & Object‑Store Costs.*?\n\n## 5\. How to Estimate Your Allocation)', content, flags=re.DOTALL)
if len(parts) > 1:
    # parts[1] is the block we want to replace
    new_block = (
        "## 3. Storage & Object‑Store Costs\n\n"
        "Storage in Jetstream 2 is primarily split between block storage (for VM disks) and object storage (for unstructured data). Unlike compute, storage is billed based on the amount of capacity reserved per month.\n\n"
        "| Storage type | Unit | SU cost (per unit) |\n"
        "|--------------|------|-------------------|\n"
        "| **Block (Cinder) volume** | GB‑month | **0.25 SU** |\n"
        "| **Object (Swift) bucket** | GB‑month | **0.15 SU** |\n"
        "| **Snapshot** | GB‑month | **0.30 SU** (double the block rate) |\n\n"
        "**Example:** If you reserve 100 GB of Block Storage for one month, the cost is 100 GB × 0.25 SU = 25 SU for that month.\n\n"
        "*Because allocations are typically measured **per‑hour**, convert the monthly rate by dividing by the average number of hours in a month (≈ 730 h).  Example: 0.25 SU / GB‑month → 0.00034 SU / GB‑hour.*\n\n"
        "---\n\n"
        "## 4. Networking (Data Transfer)\n\n"
        "Networking costs are only applied to data leaving the Jetstream 2 environment. Inbound traffic (ingress) is free, which encourages importing large datasets into the cloud.\n\n"
        "| Direction | Unit | SU cost |\n"
        "|-----------|------|---------|\n"
        "| **Egress (outbound)** | GB | **0.01 SU** |\n"
        "| **Ingress (inbound)** | GB | **0 SU** |\n\n"
        "**Example:** Transferring a 50 GB dataset from Jetstream 2 to an external server costs 50 GB × 0.01 SU = 0.5 SU.\n\n"
        "Only traffic that leaves the Jetstream 2 cloud (e.g., to the public internet or another federation site) is charged.\n\n"
        "---\n\n"
        "## 5. How to Estimate Your Allocation"
    )
    content = parts[0] + new_block + parts[2]

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
