
**Short answer**

All of the major public‑cloud platforms give you a *mix* of two kinds of free access:

1. **Promotional credit** – a lump‑sum amount (or a fixed number of hours) that you can spend during a limited trial period (usually 12 months).  
2. **“Always‑Free” or “Free‑forever”** – a small set of services that remain free **indefinitely**, provided you stay within the quoted usage limits.

So the answer is: **yes, most clouds have a forever‑free tier, but it is limited to a narrow set of resources; the broader free‑trial credit is time‑limited.** Below is a snapshot of the current (2024‑10) offerings from the four largest providers and a few notable secondary ones. The details can change, so always verify on the provider’s pricing page before relying on them.

---

### 1. Amazon Web Services (AWS)

| Tier | What is free | Limits (per month) | Comments |
|------|--------------|--------------------|----------|
| **12‑month Free Trial** | $‑300 credit (or 750 h of t2.micro/t3.micro) + many other services | 750 h of a t2.micro/t3.micro Linux/Windows VM, 5 GB of S3 Standard, 750 h of RDS db.t2.micro, etc. | Credit expires after 12 months; usage beyond limits is billed. |
| **Always‑Free** (no expiration) | A subset of services that remain free after the trial ends | • 750 h / month of **t2.micro / t3.micro** (only in the *Free Tier*‑eligible regions)  <br>• 5 GB of **S3** (Standard) plus 20 000 GET and 2 000 PUT requests  <br>• 1 M Lambda requests + 400 k GB‑seconds  <br>• 1 GB of **EFS** (standard)  <br>• 1 M Amazon SNS push notifications  <br>• 10 GB of **Data Transfer Out** (to Internet) per month  | The always‑free limits apply **only** to the listed services and **only** in the specific “Free Tier” regions (e.g., us‑east‑1, us‑west‑2, eu‑west‑1, etc.). If you launch a larger instance type or run in a non‑eligible region you are immediately billed. |
| **Free‑forever sandbox** | AWS CloudShell (2 GB of persistent storage) | 1 h of interactive shell per day, 2 GB home directory | Useful for quick CLI experiments; no compute charges. |

---

### 2. Microsoft Azure

| Tier | What is free | Limits (per month) | Comments |
|------|--------------|--------------------|----------|
| **12‑month Free Trial** | $‑200 credit + access to a set of services | 750 h of **B1s** Linux/Windows VM, 5 GB of **Blob** storage, 250 GB of Azure SQL DB, 15 GB outbound data, etc. | Credit expires after 12 months; afterwards you pay for any usage that exceeds the “Always‑Free” quotas. |
| **Always‑Free** (no expiration) | A narrow set of services that stay free indefinitely | • 750 h / month of **B1S** VM (Linux or Windows) in eligible regions  <br>• 5 GB of **Blob** storage (Hot tier)  <br>• 1 M requests per month for **Azure Functions** (consumption plan)  <br>• 1 GB of **File** storage (standard)  <br>• 5 GB of **SQL Database** (single‑core) *only in the free‑tier offering*  | The free‑forever quotas are **region‑restricted** (e.g., East US, West US, Europe West) and are applied **per subscription**. If you exceed any limit you are billed at the regular rate. |
| **Free sandbox** | Azure Cloud Shell (5 GB persisted storage) | 15 min of interactive session per day, 5 GB home directory | No compute charges; ideal for testing Azure CLI/PowerShell. |

---

### 3. Google Cloud Platform (GCP)

| Tier | What is free | Limits (per month) | Comments |
|------|--------------|--------------------|----------|
| **12‑month Free Trial** | $‑300 credit (valid for 90 days, can be used up to 12 months) | 720 h of **e2‑micro** VM, 5 GB of **Regional Cloud Storage**, 1 GiB of **Firestore**, 1 TiB outbound network from North America, etc. | Credit expires after 90 days (but you can continue using the free‑forever resources afterward). |
| **Always‑Free** (no expiration) | Small quota of services that never cost anything | • 720 h / month of **e2‑micro** VM (only in specific regions: us‑central1, us‑west1, northamerica‑north1, southamerica‑east1)  <br>• 5 GB of **Regional Cloud Storage** (Standard)  <br>• 1 GiB of **Firestore** (in‑datastore mode)  <br>• 1 GiB of **Cloud Functions** (invocations)  <br>• 1 GiB of **BigQuery** query processing per month  <br>• 5 GiB of **Cloud Run** (CPU‑seconds)  <br>• 1 TiB of outbound network from North America  | The always‑free VM quota is limited to the regions listed above; launching the same type in any other region incurs normal charges. |
| **Free sandbox** | Cloud Shell (5 GB persistent home directory) | 1 h of interactive shell per day | No cost, runs on Google’s infrastructure. |

---

### 4. Oracle Cloud Infrastructure (OCI)

| Tier | What is free | Limits (per month) | Comments |
|------|--------------|--------------------|----------|
| **Always‑Free** (no trial credit needed) | A broader set than the other three major clouds | • 2 **Arm‑based** (VM.Standard.A1.Flex) instances **up to 4 OCPU** total (max 1 OCPU each) and **24 GB RAM** combined  <br>• 2 **AMD‑based** (VM.Standard.E2.1.Micro) instances **up to 1 OCPU** total and **1 GB RAM** each  <br>• 100 GB of **Block Volume**  <br>• 10 GB of **Object Storage** (standard)  <br>• 10 TB of outbound data transfer per month  <br>• 2 TB of **Autonomous Database** (always‑free)  | The free compute instances are *always* free, but you must keep them in the **Free Tier** region (`us‑phoenix-1` or `us‑ashburn-1`). If you move them to another region you are billed. OCI also gives a **$‑300** credit for a 30‑day trial, but the always‑free resources are available even without it. |
| **Free sandbox** | Oracle Cloud **Always‑Free** Cloud Shell (2 GB) | 1 h per day, 2 GB storage | No cost. |

---

### 5. Other providers that offer a **forever‑free** tier (usually for development or hobby projects)

| Provider | Free offering (forever) | Typical limits | Notes |
|----------|------------------------|----------------|-------|
| **IBM Cloud** | Lite account | 256 MB Cloud Object Storage, 1 GB Cloudant DB, 2 GB Cloud Functions, 30 GB of Kubernetes Free tier (no charge for the control plane) | Services stay free as long as you stay under the quota. |
| **Alibaba Cloud** | Free tier (12 months for most services) + **“Always‑Free”** for a limited set | 1 t5‑small instance (up to 750 h), 40 GB Object Storage, 1 TB outbound traffic in selected regions | The “Always‑Free” part is tiny; most benefits are trial‑based. |
| **DigitalOcean** | Free credits for new users ($‑100 for 60 days) – *no* permanent free tier | – | No forever‑free compute; only trial credit. |
| **Linode** | $‑100 credit for 60 days – *no* permanent free tier | – | Same as above. |
| **Vercel / Netlify / Render / Fly.io** | Free plan for static sites / serverless functions | Limited bandwidth (e.g., 100 GB/month on Vercel), limited build minutes, limited function execution time | These are *platform‑as‑a‑service* rather than full IaaS; they stay free for hobby sites as long as you stay within the free limits. |
| **GitHub Actions** | 2 000 minutes/month for public repos (free forever) | 500 MB storage, 2 GB data transfer | Useful for CI/CD; not a compute VM you can SSH into. |
| **Gitlab CI/CD** | 400 minutes/month for free tier | Similar to GitHub Actions. |
| **Cloudflare Workers** | 100 000 requests/day free | 30 ms CPU time per request, 1 GiB KV storage | Edge‑compute platform, free forever. |

---

## Key take‑aways

* **“Free forever”** generally means *“free within the stated caps”*. As soon as you exceed a quota you are charged at the regular rate.
* Most major clouds restrict the always‑free compute resources to **specific regions** and **specific instance types** (e.g., AWS t2.micro, Azure B1s, GCP e2‑micro, OCI VM.Standard.A1.Flex). Creating a larger VM or using a different region will immediately incur charges.
* The **promotional credit** (12‑month trial) is **time‑limited**; when it expires you either switch to a paid plan or shut down everything that is not covered by the always‑free quotas.
* The **always‑free quotas are per‑account** (or per‑subscription). If you create multiple accounts you can get multiple copies of the free resources, but this is discouraged and can be considered abuse by the provider.
* **Billing alerts** are essential. All providers let you set a budget or an email alert that triggers when you approach $0.01 of spend, preventing surprise charges once you exceed the free limits.
* For **learning, prototyping, or small personal projects**, the always‑free tiers of AWS, Azure, GCP, and especially OCI are usually sufficient. If you need more persistent compute, consider staying inside the free limits (e.g., a single e2‑micro or B1s instance that you keep running 24/7) and use the providers’ managed services (databases, storage, serverless functions) that also have free quotas.

---

### Quick comparison table (forever‑free compute)

| Provider | Free compute type | vCPU / RAM | Max monthly hours | Eligible regions |
|----------|-------------------|-----------|-------------------|------------------|
| AWS      | t2.micro / t3.micro (Linux/Windows) | 1 vCPU / 1 GiB | 750 h | us‑east‑1, us‑west‑2, eu‑west‑1, ap‑southeast‑1, ap‑northeast‑1, ap‑south‑1, ca‑central‑1, sa‑east‑1 |
| Azure    | B1s (Linux/Windows) | 1 vCPU / 1 GiB | 750 h | East US, East US 2, West US, West US 2, Canada Central, Canada East, Brazil South, South Africa North, UK South, Germany West Central, etc. |
| GCP      | e2‑micro (Linux) | 1 vCPU (shared) / 0.5 GiB | 720 h | us‑central1, us‑west1, northamerica‑north1, southamerica‑east1 |
| OCI      | VM.Standard.A1.Flex (Arm) | Up to 1 vCPU / 2 GiB each (max 4 vCPU, 24 GiB total) | Unlimited (subject to total OCPU/RAM caps) | us‑ashburn‑1, us‑phoenix‑1 (Free Tier regions) |
| IBM Cloud | Lite “f1‑1‑2X” (shared) | 0.25 vCPU / 256 MiB | Unlimited (subject to 1 GB memory per month) | Global (but limited to Lite plan) |

---

## How to stay strictly within the forever‑free tier

1. **Create a single resource group / project** dedicated to the free resources.  
2. **Lock the region** to one of the allowed free‑tier regions.  
3. **Set a budget alert** at $0.01 (or $1) in the provider’s billing console.  
4. **Periodically audit usage** (`aws ce get-cost-and-usage`, `az consumption usage list`, `gcloud beta billing budgets describe`, `oci usage ...`).  
5. **Avoid ancillary services** that are not explicitly free (e.g., managed load balancers, NAT gateways, premium storage).  
6. **Delete or stop** any resource that you are not actively using – even a small persistent disk left attached to a stopped VM can generate storage charges.

---

**Bottom line:**  
All four of the largest cloud vendors (AWS, Azure, Google Cloud, Oracle Cloud) provide a *forever‑free* subset of services, most notably a modest VM that can run continuously within the free‑tier limits. The broader “free trial” credits are time‑limited, but once they expire you can continue operating at zero cost as long as you stay inside the always‑free quotas. Smaller or niche providers often offer free tiers for specific workloads (static sites, serverless functions, CI/CD) that also remain free indefinitely. The key is to understand the exact limits, keep resources in the designated regions, and monitor usage to avoid accidental charges.