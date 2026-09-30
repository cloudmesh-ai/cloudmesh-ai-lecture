# Multi-Cloud Virtual Machine Management with OpenClaw

## Learning Objectives

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    * Design an OpenClaw project to manage infrastructure across multiple cloud providers (AWS, Azure, GCP).
    * Configure a multi-cloud dataset for VM specifications and state tracking.
    * Develop a custom Python action (VM-Engine) that interfaces with cloud SDKs.
    * Implement secure secrets management for cloud credentials within OpenClaw.
    * Deploy and monitor a custom action service using Docker and Prometheus.

## Overview

This chapter provides a complete tutorial on creating an OpenClaw project that can provision, list, and terminate virtual machines (VMs) on AWS, Azure, and Google Cloud Platform (GCP) from a single unified interface. 

By leveraging OpenClaw's "Infrastructure as Data" approach, organizations can move away from fragmented cloud consoles and towards a programmable, audited, and role-controlled management layer. This project demonstrates how to wrap complex cloud SDKs into a simple REST endpoint that can be triggered via a UI, API, or automated pipeline.

## Project Architecture

The Multi-Cloud VM Manager follows a decoupled architecture where the orchestration logic is separated from the cloud-specific API calls.

| Component | Role | Implementation Detail |
|-----------|------|-----------------------|
| **OpenClaw UI** | Control Plane | React-based dashboard for triggering VM operations and viewing status. |
| **API Gateway** | Routing Layer | FastAPI-based gateway that routes requests to the appropriate custom action. |
| **Custom Action** | VM-Engine | Python service containing `boto3` (AWS), `azure-mgmt-compute`, and `google-cloud-compute`. |
| **Cloud APIs** | Infrastructure | The target provider endpoints (AWS EC2, Azure VM, GCP Compute Engine). |

```text
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

Figure 1: High-level architecture of the Multi-Cloud VM Manager.

## Prerequisites & Secrets Management

To build this project, the following components must be configured.

| Item | Requirement | Configuration |
|------|--------------|----------------|
| OpenClaw Instance | Running $\ge$ v2.5 | Installed via Docker-Compose or Helm. |
| Cloud Credentials | IAM/Service Account | `AWS_ACCESS_KEY_ID`, `AZURE_CLIENT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`. |
| Python Runtime | `python:3.11-slim` | Installed inside the custom action container. |
| Network Access | HTTPS (Port 443) | Outbound access to cloud provider API endpoints. |

**Important:** Store all cloud secrets in OpenClaw's secret manager. Inject them as environment variables into the custom-action container to avoid hard-coding sensitive keys in the source code.

## Step-by-Step Project Build-Out

### 1. Create the OpenClaw Project

1. Log in to OpenClaw $\rightarrow$ **Projects $\rightarrow$ New Project**.
2. Name: **"Multi-Cloud-VM-Manager"**
3. Description: *"Provision, list, and retire VMs on AWS, Azure, and GCP from a single UI."*

### 2. Define the VM-Spec Dataset

The dataset acts as the request queue and audit log for all VM operations.

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `cloud_provider` | Categorical | `aws` | Target cloud (`aws`, `azure`, `gcp`). |
| `region` | Categorical | `us-east-1` | Target region/zone. |
| `instance_type` | Categorical | `t3.medium` | Machine size. |
| `image_id` | String | `ami-0abcd...` | OS image identifier. |
| `vm_name` | String | `demo-app-01` | Unique name for the instance. |
| `action` | Categorical | `create` | Operation (`create`, `terminate`, `list`). |
| `status` | Categorical | `pending` | Processing state (`pending` $\rightarrow$ `running` $\rightarrow$ `succeeded`). |

### 3. Develop the Custom Action (VM-Engine)

The VM-Engine is a Python service that translates the dataset row into a cloud SDK call.

#### Directory Layout
```text
custom_actions/
└─ vm_engine/
   ├─ Dockerfile
   ├─ requirements.txt
   └─ main.py
```

#### Implementation Logic (`main.py`)
The engine uses a router pattern to handle different providers:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os, boto3, google.cloud.compute_v1 as gcp_compute

app = FastAPI(title="Multi-Cloud VM Engine")

class VMRequest(BaseModel):
    cloud_provider: str
    region: str
    instance_type: str
    image_id: str
    vm_name: str
    action: str

@app.post("/vm")
def handle_vm(req: VMRequest):
    if req.cloud_provider == "aws":
        return _handle_aws(req)
    elif req.cloud_provider == "gcp":
        return _handle_gcp(req)
    # ... other providers
    raise HTTPException(status_code=400, detail="Unsupported provider")

def _handle_aws(req):
    ec2 = boto3.client("ec2", region_name=req.region)
    if req.action == "create":
        resp = ec2.run_instances(ImageId=req.image_id, InstanceType=req.instance_type, MinCount=1, MaxCount=1)
        return {"instance_id": resp["Instances"][0]["InstanceId"]}
    # ... other actions
```

### 4. Register and Deploy the Action

1. **Create Secrets**: Add `AWS_ACCESS_KEY_ID`, etc., to the OpenClaw secret store.
2. **Configure Action**: In the UI, navigate to **Project $\rightarrow$ Custom Actions $\rightarrow$ New Action**.
    * **Name**: `vm_engine`
    * **Dockerfile Path**: `./custom_actions/vm_engine/`
    * **Endpoint**: `/vm` (POST).
    * **Env Vars**: Map cloud secrets to environment variables.
3. **Build & Deploy**: Click **Build & Deploy** to create the container and expose the REST endpoint.

## Deployment & Production Scaling

For production environments, use Helm to deploy OpenClaw on Kubernetes for high availability.

| Deployment | Use Case | Command |
|------------|----------|----------|
| Docker-Compose | Dev/PoC | `docker compose up -d` |
| Helm (K8s) | Production | `helm upgrade --install vm-manager ./helm/openclaw` |

### Production Configuration Example

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
```

## Security & Auditing Best Practices

To prevent accidental resource exhaustion or security breaches, implement the following:

1. **Least-Privilege IAM**: Create dedicated IAM roles for the OpenClaw service with only `RunInstances` and `TerminateInstances` permissions.
2. **Audit Logging**: Export OpenClaw's audit log to a SIEM (e.g., ELK stack) to track who launched which VM and when.
3. **Network Isolation**: Deploy the custom action container in a private subnet with no inbound ports open to the public internet.
4. **Rate Limiting**: Configure `API_RATE_LIMIT` to prevent "VM storms" caused by script errors or malicious actors.

## Monitoring & Alerting

The `vm_engine` exposes a `/metrics` endpoint for Prometheus scraping.

| Metric | Type | Alert Trigger |
|--------|------|----------------|
| `vm_engine_latency_seconds` | Gauge | Alert if avg latency $> 30$s over 5m. |
| `vm_engine_requests_total` | Counter | Alert if failures $> 5$/min. |
| `container_cpu_usage` | Gauge | Auto-scale if CPU $> 80\%$ for 2m. |

## Summary Checklist

* [ ] Configure cloud IAM roles with least-privilege permissions.
* [ ] Set up cloud secrets in the OpenClaw secret manager.
* [ ] Define the VM-Spec dataset with required columns.
* [ ] Implement and deploy the `vm_engine` custom action.
* [ ] Verify VM creation via the OpenClaw UI and API.
* [ ] Configure Prometheus alerts for latency and failure rates.

## Assignments

!!! note "Assignment.1: Project Setup"

    Create an OpenClaw project and a VM-Spec dataset configured for at least two different cloud providers.

??? tip "Solution: Project Setup"
    In the UI, create a project named "Cloud-Manager" and define a dataset with columns: `cloud_provider` (aws, azure, gcp), `region`, `instance_type`, `image_id`, `vm_name`, `action`, and `status`.

!!! note "Assignment.2: Custom Action Implementation"

    Develop a Python custom action that implements the `create` and `list` actions for AWS EC2 using `boto3`.

??? tip "Solution: Custom Action Implementation"
    Implement a FastAPI app that uses `boto3.client('ec2')`. For `create`, use `run_instances()`; for `list`, use `describe_instances()`. Ensure the action reads `AWS_ACCESS_KEY_ID` from the environment.

!!! note "Assignment.3: Security Hardening"

    Implement a validation check in the `vm_engine` that rejects any `instance_type` larger than `t3.medium` for users with the "Developer" role.

??? tip "Solution: Security Hardening"
    In the `handle_vm` router, add a check: `if user_role == 'Developer' and req.instance_type not in ALLOWED_TYPES: raise HTTPException(status_code=403, detail="Instance type too large")`.

## References

* Boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
* Azure SDK for Python: https://learn.microsoft.com/en-us/azure/developer/python/
* Google Cloud Compute Engine API: https://cloud.google.com/compute/docs/reference/rest
* OpenClaw Custom Actions Guide: https://github.com/openclaw/openclaw/docs/custom-actions
