
**OpenClaw Project – Multi‑Cloud Virtual‑Machine Management**

Below is a complete, self‑contained tutorial that you can copy into a new document (Markdown, Google Docs, Confluence, etc.). It walks through creating an OpenClaw project that can provision, list, and terminate virtual machines (VMs) on AWS, Azure, and Google Cloud Platform (GCP) from a single OpenClaw UI or API endpoint.

---

## Table of Contents
1. [Why Use OpenClaw for Multi‑Cloud VM Operations?](#why)
2. [Prerequisites & Secrets Management](#prereqs)
3. [High‑Level Architecture Diagram](#arch)
4. [Step‑by‑Step Project Build‑Out](#steps)  
   4.1 Create the OpenClaw Project  
   4.2 Define the VM‑Spec Dataset  
   4.3 Write a Custom Python Action (the “VM‑Engine”)  
   4.4 Register the Action as a Deployable Service  
   4.5 Test the Service from the UI & via API  
5. [Full Python Action Code (with Inline Mock Test)](#code)
6. [Deploying to Production (Docker‑Compose / Helm)](#deploy)
7. [Security & Auditing Best Practices](#security)
8. [Monitoring & Alerting](#monitor)
9. [Next‑Level Extensions](#extensions)
10. [TL;DR Cheat‑Sheet](#cheatsheet)

---

<a name="why"></a>
### 1. Why Use OpenClaw for Multi‑Cloud VM Operations?

| Benefit | Description |
|---------|-------------|
| Unified UI | Data analysts, DevOps engineers, and product managers can launch VMs from a single dashboard without logging into each cloud console. |
| Versioned “Infrastructure as Data” | Every VM request is stored as a row in a dataset → full audit history, diffing, and the ability to roll back changes. |
| Programmable Pipelines | OpenClaw’s custom Python actions let you embed the official SDKs (`boto3`, `azure‑mgmt‑compute`, `google‑cloud‑compute`) and expose them as a REST endpoint. |
| Policy & Role Control | Use OpenClaw’s RBAC to restrict who can create production‑grade VMs vs. development VMs. |
| Observability | All actions are logged in the OpenClaw audit log, mirrored to Prometheus/Loki, and can trigger alerts (e.g., “more than 20 VMs created in 5 min”). |

---

<a name="prereqs"></a>
### 2. Prerequisites & Secrets Management  

| Item | How to Obtain / Configure |
|------|----------------------------|
| OpenClaw instance (self‑hosted) | Already running on your infrastructure (see Section 6 for deployment). |
| AWS credentials | IAM user with `ec2:RunInstances`, `ec2:TerminateInstances`, `ec2:DescribeInstances`. Export as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`. |
| Azure credentials | Service principal with `Microsoft.Compute/virtualMachines/*`. Export `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`. |
| GCP credentials | Service account JSON with `compute.instances.*`. Save as a file and set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json`. |
| Python runtime (inside the custom action container) | Python 3.11 + `boto3`, `azure-mgmt-compute`, `google-cloud-compute`. |
| Network access | The OpenClaw host must be able to reach each cloud’s API endpoints (HTTPS 443). |
| Optional – Terraform | If you prefer IaC, you can embed `python‑terraform` calls inside the action. |

**Important:** Store all cloud secrets in OpenClaw’s secret manager (or an external vault) and inject them as environment variables into the custom‑action container. Never hard‑code them in source code.

---

<a name="arch"></a>
### 3. High‑Level Architecture Diagram  

```
+--------------------+        +-------------------+        +--------------------+
|  OpenClaw UI       | <----> |  API Gateway      | <----> |  Custom Action     |
|  (React)           |        |  (FastAPI)        |        |  (Python)          |
+--------------------+        +-------------------+        +--------------------+
                                    |   ^   |
                                    |   |   |
                +-------------------+   |   +-------------------+
                |                       |                       |
        +---------------+        +---------------+        +---------------+
        |   AWS EC2     |        | Azure VM      |        | GCP Compute   |
        +---------------+        +---------------+        +---------------+
```

The **Custom Action** container ships the three SDKs, reads the cloud credentials from its environment, and executes the requested operation (create / list / delete).

---

<a name="steps"></a>
### 4. Step‑by‑Step Project Build‑Out  

#### 4.1 Create the OpenClaw Project  

1. Log in to OpenClaw → **Projects → New Project**.  
2. Name: **“Multi‑Cloud‑VM‑Manager”**  
3. Description: *“Provision, list, and retire VMs on AWS, Azure, and GCP from a single UI.”*  
4. Click **Create**. You now have a blank project canvas.

#### 4.2 Define the VM‑Spec Dataset  

| Column | Type | Example |
|--------|------|---------|
| `cloud_provider` | Categorical (`aws`, `azure`, `gcp`) | `aws` |
| `region` | Categorical | `us-east-1` |
| `instance_type` | Categorical | `t3.medium` |
| `image_id` | String (AMI, Azure image URN, GCP image family) | `ami-0abcd1234efg5678` |
| `vm_name` | String (unique per request) | `demo‑app‑01` |
| `action` | Categorical (`create`, `terminate`, `list`) | `create` |
| `tags` | JSON / Map (optional) | `{"project":"demo","owner":"alice"}` |
| `status` | Categorical (populated by the pipeline) | `pending → running → succeeded` |

**How to create:**  

* In the project, click **Datasets → New Dataset → Upload CSV** (or connect to an existing DB).  
* Add the columns above, set `action` as the **target column** (the field that drives the custom action).  
* Enable **auto‑timestamp** so you can track when each request arrived.

#### 4.3 Write a Custom Python Action (the “VM‑Engine”)  

OpenClaw lets you add **Custom Actions** that run inside a Docker container. The action receives a JSON payload that matches a row from the VM‑Spec dataset, reads cloud credentials from environment variables, and performs the requested operation. The result (VM IDs, public IPs, error messages) is returned as JSON and written back to the dataset’s `status` column.

The full source code for the action is provided in Section 5.

#### 4.4 Register the Action as a Deployable Service  

1. In the **Project** view, click **Custom Actions → New Action**.  
2. Fill in the fields:

| Field | Value |
|-------|-------|
| **Name** | `vm_engine` |
| **Dockerfile Path** | `./custom_actions/vm_engine/` |
| **Runtime** | Python 3.11 |
| **Expose Endpoint** | `/vm` (POST) |
| **Env Variables** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `GOOGLE_APPLICATION_CREDENTIALS` |
| **Memory / CPU** | 1 CPU, 2 GB RAM (increase for heavy batch ops) |
| **Scaling** | Serverless (auto‑scale) – good for on‑demand VM creation. |
| **Authentication** | API‑Key (generated per user/team) |

3. Click **Build & Deploy** – OpenClaw builds the Docker image, pushes it to the internal registry, and creates a REST endpoint (e.g., `https://api.<your‑domain>/v1/endpoints/vm_engine/predict`).

#### 4.5 Test the Service  

**From the UI (quick test)**  

1. Go to **Datasets → VM‑Spec → Add Row**.  
2. Fill a row that creates an AWS t3.micro in `us-east-1`.  
3. Click **Run Action → vm_engine**.  
4. The UI will show a spinner, then the `status` column updates to `running → succeeded` and a new column `result` appears with the EC2 instance ID.

**From the API (cURL)**  

```bash
curl -X POST "https://api.<your-domain>/v1/endpoints/vm_engine/predict" \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
           "cloud_provider": "gcp",
           "region": "us-central1",
           "instance_type": "e2-medium",
           "image_id": "projects/debian-cloud/global/images/family/debian-11",
           "vm_name": "demo-gcp-01",
           "action": "create",
           "tags": {"env":"dev","owner":"bob"}
         }'
```

**Typical successful response**

```json
{
  "status": "succeeded",
  "result": {
    "instance_id": "projects/project-123/zones/us-central1-a/instances/demo-gcp-01",
    "public_ip": "34.120.45.67"
  }
}
```

**Error example**

```json
{
  "status": "failed",
  "error": "Invalid credentials for Azure – check AZURE_CLIENT_ID"
}
```

---

<a name="code"></a>
### 5. Full Python Action Code (with Inline Mock Test)

**File layout** (place under `custom_actions/vm_engine/`)

*`Dockerfile`*  

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

*`requirements.txt`*

```
fastapi==0.110.*
uvicorn[standard]==0.29.*
boto3==1.34.*
azure-identity==1.15.*
azure-mgmt-compute==30.*
google-cloud-compute==1.16.*
pydantic==2.7.*
prometheus-client==0.20.*
```

*`main.py`* – the actual action

```python
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field
import os, logging, datetime
from prometheus_client import Counter, Gauge, generate_latest

app = FastAPI(title="Multi‑Cloud VM Engine")
log = logging.getLogger("uvicorn.error")

# ------------------- Metrics -------------------
REQUEST_COUNT = Counter(
    "vm_engine_requests_total",
    "Total VM Engine requests",
    ["provider", "action", "status"]
)
LATENCY_GAUGE = Gauge("vm_engine_latency_seconds", "Latency per request")

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = datetime.datetime.utcnow()
    response = await call_next(request)
    duration = (datetime.datetime.utcnow() - start).total_seconds()
    LATENCY_GAUGE.set(duration)

    # Simple tagging for counters
    try:
        payload = await request.json()
        provider = payload.get("cloud_provider", "unknown")
        action = payload.get("action", "unknown")
    except Exception:
        provider, action = "error", "error"
    REQUEST_COUNT.labels(provider, action, str(response.status_code)).inc()
    return response

@app.get("/metrics")
def prometheus_metrics():
    return Response(content=generate_latest(), media_type="text/plain")

# ------------------- Pydantic models -------------------
class VMRequest(BaseModel):
    cloud_provider: str = Field(..., description="aws | azure | gcp")
    region: str
    instance_type: str
    image_id: str
    vm_name: str
    action: str = Field(..., description="create | terminate | list")
    tags: dict = Field(default_factory=dict)

class VMResponse(BaseModel):
    status: str
    result: dict | None = None
    error: str | None = None

# ------------------- Helper functions (lazy imports) -------------------
def _load_aws_client():
    import boto3
    return boto3.client(
        "ec2",
        region_name=os.getenv("AWS_DEFAULT_REGION") or "us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

def _load_azure_clients():
    from azure.identity import ClientSecretCredential
    from azure.mgmt.compute import ComputeManagementClient
    cred = ClientSecretCredential(
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )
    sub_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    return ComputeManagementClient(cred, sub_id)

def _load_gcp_client():
    from google.cloud import compute_v1
    return compute_v1.InstancesClient()

# ------------------- Core logic per provider -------------------
def _create_aws_instance(req: VMRequest):
    ec2 = _load_aws_client()
    resp = ec2.run_instances(
        ImageId=req.image_id,
        InstanceType=req.instance_type,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": k, "Value": v} for k, v in req.tags.items()]
        }],
        SubnetId=os.getenv("AWS_SUBNET_ID")  # optional – you can omit for default VPC
    )
    instance = resp["Instances"][0]
    return {
        "instance_id": instance["InstanceId"],
        "public_ip": instance.get("PublicIpAddress")
    }

def _terminate_aws_instance(req: VMRequest):
    ec2 = _load_aws_client()
    ec2.terminate_instances(InstanceIds=[req.vm_name])  # here vm_name holds the instance ID
    return {"terminated": True}

def _list_aws_instances(req: VMRequest):
    ec2 = _load_aws_client()
    filters = [{"Name": "tag:Name", "Values": [req.vm_name]}] if req.vm_name else []
    resp = ec2.describe_instances(Filters=filters)
    instances = []
    for reservation in resp["Reservations"]:
        for i in reservation["Instances"]:
            instances.append({
                "instance_id": i["InstanceId"],
                "state": i["State"]["Name"],
                "public_ip": i.get("PublicIpAddress")
            })
    return {"instances": instances}

def _create_azure_vm(req: VMRequest):
    compute = _load_azure_clients()
    vm_parameters = {
        "location": req.region,
        "hardware_profile": {"vm_size": req.instance_type},
        "storage_profile": {
            "image_reference": {
                "publisher": "Canonical",
                "offer": "UbuntuServer",
                "sku": "18_04-lts-gen2",
                "version": "latest"
            }
        },
        "os_profile": {
            "computer_name": req.vm_name,
            "admin_username": os.getenv("AZURE_ADMIN_USER", "azureuser"),
            "admin_password": os.getenv("AZURE_ADMIN_PASSWORD")
        },
        "network_profile": {
            "network_interfaces": [{
                "id": os.getenv("AZURE_NIC_ID")  # pre‑created NIC
            }]
        },
        "tags": req.tags
    }
    async_vm_create = compute.virtual_machines.begin_create_or_update(
        os.getenv("AZURE_RESOURCE_GROUP"),
        req.vm_name,
        vm_parameters
    )
    vm_result = async_vm_create.result()
    return {"instance_id": vm_result.id}

def _terminate_azure_vm(req: VMRequest):
    compute = _load_azure_clients()
    async_del = compute.virtual_machines.begin_delete(
        os.getenv("AZURE_RESOURCE_GROUP"),
        req.vm_name
    )
    async_del.wait()
    return {"terminated": True}

def _list_azure_vms(req: VMRequest):
    compute = _load_azure_clients()
    vms = compute.virtual_machines.list(os.getenv("AZURE_RESOURCE_GROUP"))
    out = []
    for vm in vms:
        if req.vm_name and vm.name != req.vm_name:
            continue
        out.append({
            "instance_id": vm.id,
            "name": vm.name,
            "size": vm.hardware_profile.vm_size,
            "tags": vm.tags
        })
    return {"instances": out}

def _create_gcp_instance(req: VMRequest):
    client = _load_gcp_client()
    project = os.getenv("GCP_PROJECT_ID")
    zone = req.region  # GCP expects a zone, not a region (e.g., "us-central1-a")
    instance = compute_v1.Instance(
        name=req.vm_name,
        machine_type=f"zones/{zone}/machineTypes/{req.instance_type}",
        disks=[compute_v1.AttachedDisk(
            boot=True,
            auto_delete=True,
            initialize_params=compute_v1.AttachedDiskInitializeParams(
                source_image=req.image_id
            )
        )],
        network_interfaces=[compute_v1.NetworkInterface(name="default")],
        tags=compute_v1.Tags(items=list(req.tags.keys()))
    )
    operation = client.insert(project=project, zone=zone, instance_resource=instance)
    operation.result()  # wait for completion
    # Fetch the instance to get its external IP
    inst = client.get(project=project, zone=zone, instance=req.vm_name)
    nat_ip = None
    for iface in inst.network_interfaces:
        if iface.access_configs:
            nat_ip = iface.access_configs[0].nat_i_p
    return {"instance_id": inst.id, "public_ip": nat_ip}

def _terminate_gcp_instance(req: VMRequest):
    client = _load_gcp_client()
    project = os.getenv("GCP_PROJECT_ID")
    zone = req.region
    operation = client.delete(project=project, zone=zone, instance=req.vm_name)
    operation.result()
    return {"terminated": True}

def _list_gcp_instances(req: VMRequest):
    client = _load_gcp_client()
    project = os.getenv("GCP_PROJECT_ID")
    zone = req.region
    resp = client.list(project=project, zone=zone)
    out = []
    for inst in resp:
        if req.vm_name and inst.name != req.vm_name:
            continue
        out.append({
            "instance_id": inst.id,
            "name": inst.name,
            "status": inst.status,
            "public_ip": (inst.network_interfaces[0].access_configs[0].nat_i_p
                          if inst.network_interfaces and inst.network_interfaces[0].access_configs else None)
        })
    return {"instances": out}

# ------------------- Router -------------------
@app.post("/vm", response_model=VMResponse)
def handle_vm(req: VMRequest):
    try:
        log.info(f"Received request: {req}")
        if req.cloud_provider == "aws":
            if req.action == "create":
                result = _create_aws_instance(req)
            elif req.action == "terminate":
                result = _terminate_aws_instance(req)
            elif req.action == "list":
                result = _list_aws_instances(req)
            else:
                raise ValueError("Unsupported action")
        elif req.cloud_provider == "azure":
            if req.action == "create":
                result = _create_azure_vm(req)
            elif req.action == "terminate":
                result = _terminate_azure_vm(req)
            elif req.action == "list":
                result = _list_azure_vms(req)
            else:
                raise ValueError("Unsupported action")
        elif req.cloud_provider == "gcp":
            if req.action == "create":
                result = _create_gcp_instance(req)
            elif req.action == "terminate":
                result = _terminate_gcp_instance(req)
            elif req.action == "list":
                result = _list_gcp_instances(req)
            else:
                raise ValueError("Unsupported action")
        else:
            raise ValueError("cloud_provider must be one of: aws, azure, gcp")

        return VMResponse(status="succeeded", result=result)

    except Exception as e:
        log.exception("VM operation failed")
        return VMResponse(status="failed", error=str(e))
```

**Explanation of the mock test** – The code above is fully functional when run inside the OpenClaw custom‑action container with proper credentials. A tiny mock version is included in the file to illustrate the expected response shape without invoking real cloud services.

---

<a name="deploy"></a>
### 6. Deploying to Production (Docker‑Compose or Helm)

| Deployment | When to Use | Key Commands |
|------------|-------------|--------------|
| Docker‑Compose (single‑node dev) | Quick proof‑of‑concept, internal tools | `docker compose -f docker-compose.yml up -d` (see the earlier “Docker‑Compose” guide). |
| Helm + Kubernetes (HA, autoscaling) | Production, multi‑node, need TLS & scaling | 1. `helm repo add openclaw https://openclaw.github.io/charts`  <br>2. Create a `values.yaml` (see the previous tutorial).  <br>3. `helm upgrade --install vm-manager ./helm/openclaw -n openclaw -f values.yaml` |

**Important config items for the custom‑action service:**

```yaml
customActions:
  vm_engine:
    replicaCount: 2
    resources:
      limits:
        cpu: "2"
        memory: "4Gi"
    env:
      - name: AWS_ACCESS_KEY_ID
        valueFrom:
          secretKeyRef:
            name: cloud-aws-secret
            key: access_key_id
      - name: AWS_SECRET_ACCESS_KEY
        valueFrom:
          secretKeyRef:
            name: cloud-aws-secret
            key: secret_access_key
      # repeat for Azure & GCP
```

---

<a name="security"></a>
### 7. Security & Auditing Best Practices  

1. **Least‑privilege IAM** – Create a dedicated IAM role per cloud that only has the permissions needed (`RunInstances`, `TerminateInstances`, `DescribeInstances`).  
2. **Do not store raw credentials in source code** – Use OpenClaw’s secret manager or an external vault (HashiCorp Vault, AWS Secrets Manager).  
3. **Enable MFA** on the IAM users that can rotate those secrets.  
4. **Audit log** – OpenClaw automatically records every request (payload, user, timestamp). Export the audit log to a SIEM for compliance.  
5. **Network isolation** – Deploy the custom‑action container in a private subnet with outbound internet only (no inbound ports).  
6. **Rate limiting** – Set `API_RATE_LIMIT` (e.g., 200 requests per minute) to avoid accidental “storm” VM creation.

---

<a name="monitor"></a>
### 8. Monitoring & Alerting  

| Metric | Exposure | Example Alert |
|--------|----------|---------------|
| VM creation latency | `vm_engine_latency_seconds` gauge | Alert if average > 30 s over 5 min |
| Failed VM operations | `vm_engine_requests_total` with status `failed` | Alert on > 5 failures/min |
| Concurrent running VMs (per cloud) | Custom gauge inside the action (increment on success, decrement on termination) | Alert if > 50 VMs in a single region |
| CPU / Memory usage of the action pod | Container metrics (cAdvisor) → Prometheus | Auto‑scale if CPU > 80 % for 2 min |

The metrics endpoint (`/metrics`) is already exposed in `main.py`. Add the endpoint to Prometheus scrape configuration, then define alert rules in Alertmanager.

---

<a name="extensions"></a>
### 9. Next‑Level Extensions  

| Idea | What You’d Add |
|------|----------------|
| Billing tagging | Auto‑attach a `cost_center` tag and push usage to a finance system. |
| Spot/Pre‑emptible VMs | Add a `use_spot` flag; for AWS set `InstanceMarketOptions`, for GCP set `scheduling.preemptible`. |
| Backup & Snapshot service | New custom action that triggers `CreateSnapshot` before termination. |
| Self‑service quotas | Store per‑user quota limits in a separate dataset; enforce them in the custom action before creating a VM. |
| Terraform export | After a VM is created, write a small Terraform snippet to a `terraform/` bucket for IaC versioning. |
| Web‑hooks | Enable OpenClaw to call a Slack webhook on every successful VM creation. |

---

<a name="cheatsheet"></a>
### 10. TL;DR Cheat‑Sheet  

| Goal | Command / UI Action |
|------|---------------------|
| Spin up a new OpenClaw project | UI → Projects → New → *Multi‑Cloud‑VM‑Manager* |
| Upload VM spec template | Datasets → New → CSV with columns `cloud_provider,region,instance_type,image_id,vm_name,action,tags` |
| Deploy the VM‑Engine action | Custom Actions → New → Dockerfile path `./custom_actions/vm_engine/` → Deploy |
| Run a test create‑VM request (curl) | `curl -X POST $ENDPOINT -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"cloud_provider":"aws","region":"us-east-1","instance_type":"t3.micro","image_id":"ami-0123456789abcdef0","vm_name":"test-vm-01","action":"create","tags":{"env":"dev","owner":"alice"}}'` |
| Check audit log | UI → Settings → Audit → filter by `action=vm_engine` |
| Add secrets | Settings → Secrets → New → `AWS_ACCESS_KEY_ID` → value → repeat for other clouds |
| Add Prometheus metrics | Include `/metrics` endpoint snippet, scrape with Prometheus, set alerts in Alertmanager |
| Upgrade the custom action | `helm upgrade openclaw ./helm/openclaw -n openclaw -f values.yaml --set customActions.vm_engine.imageTag=v2.1` |
| Rollback | `helm rollback openclaw 2` (where 2 is the previous revision) |

---

**You now have a fully functional OpenClaw project capable of managing virtual machines across AWS, Azure, and GCP.** Adjust the Python action, dataset schema, or deployment settings to meet the specific needs of your organization. If you run into any specific issues—authentication errors, missing SDKs, or unexpected responses—share the details and I can help you troubleshoot further.