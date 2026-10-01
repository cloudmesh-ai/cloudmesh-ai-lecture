
# Tutorial – Running a Large Language Model (LLM) on Oracle Cloud Infrastructure (OCI)

This guide shows three practical ways to run an LLM on OCI:

* **OCI Generative AI (GenAI) Service** – fully managed foundation‑model API (similar to OpenAI).  
* **OCI Data Science Service** – managed Jupyter notebooks and model‑deployment endpoints for custom open‑source models (Llama 2, Mistral, etc.).  
* **Self‑hosted GPU instance** – launch a GPU‑enabled Compute instance, install Docker, and run any containerised LLM.

All sections share a common set of prerequisites, a single `clouds.yaml` file for credentials, and cleanup instructions to avoid unwanted charges.

---

## Prerequisites (common to every approach)

* **OCI tenancy** with a compartment that you can use for resources.  
* **OCI CLI** (version ≥ 3.18). Install with  

  ```bash
  bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
  ```

  Verify with `oci --version`.  

* **Python 3.9+** – create a virtual environment  

  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  ```

* **OCI Python SDK**  

  ```bash
  pip install oci oci-cli-libcloud
  ```

* **SSH key pair** for any VM you may provision  

  ```bash
  ssh-keygen -t rsa -b 2048 -f ~/.ssh/oci_llm_key -N ""
  ```

* **GPU quota** – request a quota increase for the shape you intend to use (`VM.Standard.E2.1.Micro` for the free tier, `VM.Standard.A1.Flex`, `VM.GPU3.1`, `VM.GPU4.8`, etc.) via the OCI Console → **Governance → Limits, Quotas and Usage**.  

* **Service‑account (API signing key)** – generate a key pair, upload the public key in the OCI console, and download the private key (`oci_api_key.pem`).  

---

## `clouds.yaml` – single source of truth for credentials

Create a file named `clouds.yaml` in the directory where you will run the scripts.

```yaml
oci:
  tenancy: ocid1.tenancy.oc1..YOUR_TENANCY_OCID
  user: ocid1.user.oc1..YOUR_USER_OCID
  fingerprint: 12:34:56:78:9a:bc:de:f0:12:34:56:78:9a:bc:de:f0
  key_file: /home/you/.oci/oci_api_key.pem
  region: us-ashburn-1               # free‑tier region (us‑ashburn‑1 or us‑phx‑1)
  compartment: ocid1.compartment.oc1..YOUR_COMPARTMENT_OCID
  gpu_shape: VM.GPU3.1                # example GPU shape; replace with desired shape
  free_shape: VM.Standard.E2.1.Micro   # always‑free shape (1 OCPU + 1 GiB RAM)
  bucket_name: llm-models-$(date +%s)  # unique bucket for model artifacts
```

All scripts in this tutorial read the same file, so you only need to edit credentials once.

---

## Option 1 – OCI Generative AI Service (hosted foundation models)

OCI GenAI provides APIs for pre‑trained large models such as **Claude‑2**, **Llama 2‑70B**, **Mistral‑7B**, and **Gemini‑1**. You are billed per 1 K tokens processed.

### Enable the GenAI service

```bash
oci iam policy create \
  --name allow-genai \
  --description "Allow use of OCI Generative AI" \
  --compartment-id ${COMPARTMENT_OCID} \
  --statements '["Allow service OCPU to read groups application-users in tenancy"]'

oci iam compartment list  # confirm COMPARTMENT_OCID
```

Enable the service in the console (GenAI → **Enable Service**) if it is not already active.

### Create a model endpoint (no explicit resource creation required)

The GenAI service is fully managed; you only need the endpoint URL and an API key.

```bash
GENAI_ENDPOINT=$(oci iam region subdomain get --region ${REGION} | jq -r .data.subdomain)
GENAI_KEY=$(oci iam user api-key list --user-id ${USER_OCID} --query "data[0].keyValue" -o text)

echo "GenAI endpoint: $GENAI_ENDPOINT"
echo "GenAI key: $GENAI_KEY"
```

### Python client for inference

```python
import os
import json
import requests

# Load from clouds.yaml
with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["oci"]

endpoint = f"https://generativeai.{cfg['region']}.oci.oraclecloud.com"
api_key = GENAI_KEY      # or read from a secret manager

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "opc-request-id": "demo-request"
}

payload = {
    "model_id": "cohere.command-r-plus-v1.0",   # replace with desired model ID
    "prompt": "Write a haiku about a sunrise over the ocean.",
    "max_tokens": 64,
    "temperature": 0.7
}

response = requests.post(f"{endpoint}/20231101/actions/predict", headers=headers, data=json.dumps(payload))
print(response.json()["generated_text"])
```

#### Pricing (as of Oct 2024)

| Model | Input token price (USD / 1 K) | Output token price (USD / 1 K) |
|-------|------------------------------|--------------------------------|
| Claude‑2 | $0.0004 | $0.0012 |
| Llama 2‑70B | $0.0005 | $0.0015 |
| Mistral‑7B | $0.0002 | $0.0006 |

Only token usage is billed; there are no instance‑hour charges.

### Cleanup

Since no compute resources are created, deleting the policy created earlier is enough:

```bash
oci iam policy delete --policy-id <policy-ocid>
```

---

## Option 2 – OCI Data Science Service (custom open‑source LLM)

The Data Science service provides managed Jupyter notebooks, GPU‑enabled notebooks, and **Model Deployment** (real‑time endpoints). This is the most flexible option for custom models.

### Enable required services

```bash
oci iam policy create \
  --name allow-datascience \
  --description "Allow use of Data Science resources" \
  --compartment-id ${COMPARTMENT_OCID} \
  --statements '["Allow service datascience to manage all-resources in compartment id ${COMPARTMENT_OCID}"]'

oci ds notebook session create \
  --compartment-id ${COMPARTMENT_OCID} \
  --display-name ds-llm-notebook \
  --notebook-session-configuration-details '
{
  "shapeName": "VM.GPU3.1",
  "blockStorageSizeInGBs": 100,
  "subnetId": "YOUR_SUBNET_OCID"
}'
```

The command returns a URL for the JupyterLab interface. Open the URL in your browser.

### Install model dependencies inside the notebook

```python
!pip install torch==2.2.0+cu122 transformers==4.38.2 accelerate==0.27.2 fastapi==0.110.0 uvicorn[standard]==0.27.1
```

### Download and prepare the model (example: Llama 2‑7B‑Chat)

```python
from huggingface_hub import snapshot_download

model_dir = "/home/datascience/llama2-7b-chat"
snapshot_download(repo_id="meta-llama/Llama-2-7b-chat-hf", local_dir=model_dir, local_dir_use_symlinks=False)
```

### Create a FastAPI inference app (inside the notebook)

```python
%%writefile /home/datascience/infer.py
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "/home/datascience/llama2-7b-chat"

tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)

class Prompt(BaseModel):
    text: str
    max_new_tokens: int = 256
    temperature: float = 0.7

@app.post("/generate")
def generate(req: Prompt):
    inputs = tokenizer(req.text, return_tensors="pt").to(device)
    cfg = GenerationConfig(
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        do_sample=True,
    )
    with torch.no_grad():
        out_ids = model.generate(**inputs, generation_config=cfg)
    return {"generated_text": tokenizer.decode(out_ids[0], skip_special_tokens=True)}
```

### Deploy the model as a managed endpoint

```bash
# Create a model artifact (zip the inference code and model directory)
cd /home/datascience
zip -r llm-model.zip infer.py llama2-7b-chat

# Upload the artifact to Object Storage
BUCKET=${BUCKET_NAME:-llm-models-$(date +%s)}
oci os bucket create --name $BUCKET --compartment-id ${COMPARTMENT_OCID}
oci os object put --bucket-name $BUCKET --name llm-model.zip --file llm-model.zip

# Register the model in Data Science
oci ds model create \
  --compartment-id ${COMPARTMENT_OCID} \
  --display-name llama2-7b-chat-model \
  --model-artifact-url "https://objectstorage.${REGION}.oraclecloud.com/n/${NAMESPACE}/b/${BUCKET}/o/llm-model.zip" \
  --is-primary
```

#### Create a deployment

```bash
oci ds model deployment create \
  --compartment-id ${COMPARTMENT_OCID} \
  --model-id <MODEL_OCID> \
  --display-name llama2-deployment \
  --deployment-type CUSTOM_CONTAINER_DEPLOYMENT \
  --project-id <PROJECT_OCID> \
  --shape-name VM.GPU3.1 \
  --gpu-count 1 \
  --environment-variables '{"MODEL_PATH":"/home/datascience/llama2-7b-chat"}' \
  --image-uri "iad.ocir.io/<tenancy>/custom-llm-image:latest"
```

If you prefer not to build a custom container, you can use OCI’s **Data Science custom container** images that already contain Python and GPU drivers. Replace `--image-uri` with `iad.ocir.io/<tenancy>/datascience/pytorch-gpu:latest`.

The command returns a **deployment ID** and an **HTTPS endpoint URL**.

### Inference from Python

```python
import requests, json, os
endpoint = "https://<DEployment_HOSTNAME>/predict"

payload = {"text": "Explain why the sky appears blue.", "max_new_tokens": 128}
headers = {"Content-Type": "application/json"}

resp = requests.post(endpoint, headers=headers, data=json.dumps(payload))
print(resp.json()["generated_text"])
```

### Pricing

* **GPU compute** – `VM.GPU3.1` (NVIDIA T4) costs roughly **$0.30 / hour** in the `us-ashburn-1` region.  
* **Object Storage** – $0.026 / GB‑month (standard tier).  
* **Data Science service** – no extra charge beyond the underlying compute used for the deployment.

### Cleanup Data Science resources

```bash
# Delete the deployment
oci ds model deployment delete --deployment-id <DEPLOYMENT_OCID> -y

# Delete the model
oci ds model delete --model-id <MODEL_OCID> -y

# Delete the bucket (optional)
oci os bucket delete --name $BUCKET --namespace <NAMESPACE> -y

# Remove the notebook session
oci ds notebook session delete --notebook-session-id <SESSION_OCID> -y
```

---

## Option 3 – Self‑hosted GPU instance (Compute)  

When you need full control over the runtime (custom quantization, LoRA adapters, or non‑standard libraries), launch a GPU Compute instance and run the model in Docker.

### Create a VCN, subnet, and security list (one‑time network setup)

```bash
VCN_NAME="llm-vcn"
SUBNET_NAME="llm-subnet"
SECURITY_LIST_NAME="llm-sec-list"

oci network vcn create \
  --compartment-id ${COMPARTMENT_OCID} \
  --cidr-block 10.0.0.0/16 \
  --display-name $VCN_NAME

VCN_OCID=$(oci network vcn list --compartment-id ${COMPARTMENT_OCID} --display-name $VCN_NAME --query "data[0].id" -o tsv)

oci network subnet create \
  --compartment-id ${COMPARTMENT_OCID} \
  --vcn-id $VCN_OCID \
  --cidr-block 10.0.0.0/24 \
  --display-name $SUBNET_NAME

SUBNET_OCID=$(oci network subnet list --compartment-id ${COMPARTMENT_OCID} --display-name $SUBNET_NAME --query "data[0].id" -o tsv)

oci network security-list create \
  --compartment-id ${COMPARTMENT_OCID} \
  --vcn-id $VCN_OCID \
  --display-name $SECURITY_LIST_NAME \
  --egress-security-rules '[{"destination":"0.0.0.0/0","protocol":"6","isStateless":false}]' \
  --ingress-security-rules '[{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{"destinationPortRange":{"max":22,"min":22}},"isStateless":false}]'
```

### Launch a GPU Compute instance

```bash
INSTANCE_NAME="llm-gpu-instance"
IMAGE_OCID="ocid1.image.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"   # Ubuntu 22.04 image in your region
SSH_KEY=$(cat ~/.ssh/oci_llm_key.pub)

oci compute instance launch \
  --compartment-id ${COMPARTMENT_OCID} \
  --availability-domain <AD> \
  --shape ${GPU_SHAPE} \
  --display-name $INSTANCE_NAME \
  --image-id $IMAGE_OCID \
  --subnet-id $SUBNET_OCID \
  --assign-public-ip true \
  --ssh-authorized-keys "$SSH_KEY"
```

Replace `<AD>` with an availability domain (e.g., `Uocm:PHX-AD-1`). The CLI returns the instance OCID. Retrieve the public IP:

```bash
PUBLIC_IP=$(oci compute instance list-vnics --instance-id <INSTANCE_OCID> --query "data[0].\"public-ip\"" -o tsv)
echo "Connect with: ssh -i ~/.ssh/oci_llm_key ubuntu@$PUBLIC_IP"
```

### Install Docker and pull the LLM container

```bash
ssh -i ~/.ssh/oci_llm_key ubuntu@$PUBLIC_IP

# Inside the VM
sudo apt-get update && sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
newgrp docker

# Pull a publicly available LLM container (example: Llama 2‑7B‑Chat)
docker pull ghcr.io/huggingface/text-generation-inference:0.9.4
```

### Run the container (expose port 80)

```bash
docker run -d --gpus all -p 80:80 \
  -e MODEL_ID=meta-llama/Llama-2-7b-chat-hf \
  -e MAX_INPUT_LENGTH=1024 \
  ghcr.io/huggingface/text-generation-inference:0.9.4
```

The container starts a FastAPI server listening on port 80. Test from your local machine:

```bash
curl -X POST http://$PUBLIC_IP/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Write a short story about a robot learning to paint.", "max_new_tokens":128}'
```

You should receive a JSON response with the generated text.

### Using the OCI Python SDK to invoke the VM (optional)

```python
import oci
import requests

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["oci"]

config = oci.config.from_dict({
    "user": cfg["user"],
    "fingerprint": cfg["fingerprint"],
    "key_file": cfg["key_file"],
    "tenancy": cfg["tenancy"],
    "region": cfg["region"]
})

compute = oci.core.ComputeClient(config)
instance = compute.get_instance("<INSTANCE_OCID>").data
public_ip = instance.public_ip

response = requests.post(f"http://{public_ip}/generate",
                         json={"prompt": "Explain quantum entanglement in simple terms.", "max_new_tokens": 128})
print(response.json()["generated_text"])
```

### Pricing for the GPU instance

| Shape               | Approx. on‑demand price (US Ashburn) |
|---------------------|--------------------------------------|
| `VM.Standard.E2.1.Micro` (always‑free) | $0 / hour (includes 1 OCPU + 1 GiB RAM) |
| `VM.GPU3.1` (NVIDIA T4) | ≈ $0.30 / hour |
| `VM.GPU4.8` (NVIDIA A100) | ≈ $2.30 / hour |

Stop the instance when not needed to avoid charges:

```bash
oci compute instance stop --instance-id <INSTANCE_OCID>
```

### Cleanup GPU resources

```bash
oci compute instance terminate --instance-id <INSTANCE_OCID>
oci network vcn delete --vcn-id $VCN_OCID
oci os bucket delete --name $BUCKET_NAME --namespace <NAMESPACE> -y
```

---

## Cost‑management recommendations

* Set a **budget alert** in the OCI console (Governance → Budgets).  
* For the always‑free shape (`VM.Standard.E2.1.Micro`) you can run a small inference server 24/7 without incurring compute charges; you only pay for Block Volume storage (≈ $0.025 / GB‑month).  
* When using GPU shapes, enable **auto‑stop** by creating a Cloud‑Shell script that checks instance idle time and issues `oci compute instance stop`.  
* Delete any temporary Object Storage buckets after model upload to avoid storage fees.

---

## Summary of pathways

* **OCI Generative AI** – quickest route to a production‑grade LLM; you only pay per token, no infrastructure to manage.  
* **OCI Data Science** – managed notebooks and model‑deployment endpoints; suitable for custom open‑source models, fine‑tuning, and GPU‑accelerated inference.  
* **Self‑hosted GPU Compute instance** – full control over the runtime, ideal for experimental workloads, quantized models, or custom inference servers.  

Pick the approach that matches your latency, cost, and customization requirements, follow the corresponding steps, and you’ll have a functional LLM on Oracle Cloud Infrastructure ready for use.