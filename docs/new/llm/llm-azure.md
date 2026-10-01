
# Running a Large Language Model (LLM) on Microsoft Azure  
*Three pathways – Azure OpenAI, Azure Machine Learning, and a custom container on Azure Container Apps (or AKS).*  

The guide is split into three sections, each showing:  

* What you need before you start.  
* The Azure CLI commands required to provision the service.  
* How to invoke the model from Python (using the native SDK, the generic **libcloud** library, or the Azure‑specific SDK).  
* How to tear the resources down when you’re finished.  

A single **`clouds.yaml`** file at the end stores all credentials and a few common settings, so the same file can be read by the libcloud and native‑SDK scripts.

---

## Prerequisites (common to every method)

* **Azure subscription** – sign up at https://azure.microsoft.com/.  
* **Azure CLI** (v2.60 or newer) – install with the instructions at https://learn.microsoft.com/cli/azure/install‑azure‑cli. Verify with `az version`.  
* **Python 3.9+** – create a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`).  
* **Azure SDK for Python** – `pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-containerinstance azure-ai-ml`.  
* **libcloud** – `pip install apache‑libcloud`.  
* **SSH key pair** – `ssh-keygen -t rsa -b 2048 -f ~/.ssh/azure_llm_key -N ""`.  
* **GPU quota** – request a quota increase for the GPU size you plan to use (`Standard_NC6`, `Standard_ND40rs_v2`, etc.) via the Azure portal **Help → Support requests**.

---

## Azure OpenAI – Managed foundation models (no GPU management)

### Provision the Azure OpenAI resource

```bash
az group create --name rg-llm-openai --location eastus

az cognitiveservices account create \
  --name openai-llm-demo \
  --resource-group rg-llm-openai \
  --kind OpenAI \
  --sku s0 \
  --location eastus \
  --yes
```

If the command fails with a message that OpenAI is not enabled, request access from the Azure portal (Azure OpenAI → **Apply for access**) and wait for approval.

### Retrieve the endpoint and key

```bash
ENDPOINT=$(az cognitiveservices account show \
  --name openai-llm-demo \
  --resource-group rg-llm-openai \
  --query "properties.endpoint" -o tsv)

KEY=$(az cognitiveservices account keys list \
  --name openai-llm-demo \
  --resource-group rg-llm-openai \
  --query "key1" -o tsv)

echo "Endpoint: $ENDPOINT"
echo "Key: $KEY"
```

### Python code (native Azure OpenAI SDK)

```python
import os
import openai

os.environ["AZURE_OPENAI_ENDPOINT"] = "<ENDPOINT>"   # replace with $ENDPOINT
os.environ["AZURE_OPENAI_KEY"] = "<KEY>"            # replace with $KEY

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2023-05-15"

deployment = "gpt-35-turbo"   # default model name for the service

response = openai.ChatCompletion.create(
    engine=deployment,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about a sunrise over the ocean."}
    ],
    temperature=0.7,
    max_tokens=64,
)

print(response.choices[0].message.content.strip())
```

**Pricing** – Azure OpenAI charges per 1 000 tokens (input + output). For `gpt‑35‑turbo` the price is currently **$0.0002 per 1 K tokens**; no infrastructure cost is incurred.

### Clean‑up

```bash
az group delete --name rg-llm-openai --yes --no-wait
```

---

## Azure Machine Learning – Deploy an open‑source model (e.g., Llama 2‑7B‑Chat)

### Create an AML workspace

```bash
az group create --name rg-ml-llm --location eastus

az ml workspace create \
  --name ws-llm-demo \
  --resource-group rg-ml-llm \
  --location eastus
```

### Install the AML SDK and Hugging Face integration

```bash
pip install "azure-ai-ml>=1.13.0" "huggingface_hub>=0.22.0" "transformers>=4.35.0"
```

### Python script to register the model and expose a managed online endpoint

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    AmlCompute,
)

credential = DefaultAzureCredential()
ml_client = MLClient(
    credential=credential,
    subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID"),
    resource_group_name="rg-ml-llm",
    workspace_name="ws-llm-demo",
)

# Register the Llama‑2‑7B‑Chat model from Hugging Face
model = Model(
    path="model",               # folder that will contain the downloaded model
    name="llama2-7b-chat",
    type="mlflow_model",
)
ml_client.models.create_or_update(model)

# Create a GPU compute cluster (adjust size to your quota)
compute_name = "gpu-cluster"
if compute_name not in [c.name for c in ml_client.compute.list()]:
    compute = AmlCompute(
        name=compute_name,
        size="Standard_NC6s_v3",    # 1 GPU (V100) instance
        min_instances=0,
        max_instances=2,
        idle_time_before_scale_down=120,
    )
    ml_client.compute.begin_create_or_update(compute).result()

# Define a managed online endpoint
endpoint = ManagedOnlineEndpoint(name="llama2-endpoint", auth_mode="key")
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Deploy the model to the endpoint
deployment = ManagedOnlineDeployment(
    name="default",
    endpoint_name="llama2-endpoint",
    model=model,
    compute=compute_name,
    instance_type="Standard_NC6s_v3",
    instance_count=1,
    environment="AzureML-aci-base",
    request_settings={"request_timeout_ms": 600_000},
)
ml_client.online_deployments.begin_create_or_update(deployment).result()

# Show the scoring URL and primary key
endpoint = ml_client.online_endpoints.get("llama2-endpoint")
print("Scoring URL :", endpoint.scoring_uri)
print("Primary key :", ml_client.online_endpoints.get_keys("llama2-endpoint").primary_key)
```

Set the environment variable `AZURE_SUBSCRIPTION_ID` before running the script.

### Inference from Python

```python
import requests, json, os

scoring_uri = "<SCORING_URL_FROM_ABOVE>"
api_key = "<PRIMARY_KEY_FROM_ABOVE>"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
}

payload = {
    "input_data": [
        {
            "columns": ["text"],
            "values": [["Explain why the sky appears blue."]]
        }
    ]
}

response = requests.post(scoring_uri, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))
```

**Pricing** – AML charges for the underlying compute. A `Standard_NC6s_v3` GPU costs roughly **$1.35 / hour** in East US. The endpoint is billed only while the compute is allocated; you can scale the instance count to zero by stopping the compute cluster (`ml_client.compute.begin_stop(compute_name)`).

### Clean‑up

```bash
az ml online-endpoint delete --name llama2-endpoint --workspace-name ws-llm-demo --resource-group rg-ml-llm -y
az ml compute delete -n gpu-cluster -w ws-llm-demo -g rg-ml-llm -y
az group delete --name rg-ml-llm --yes --no-wait
```

---

## Custom Container on Azure Container Apps (or AKS)

### Build a Docker image that serves the LLM via FastAPI

Create a directory `llm_container/` with the following files.

**Dockerfile**

```dockerfile
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip git && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    torch==2.2.0+cu122 \
    transformers==4.38.2 \
    accelerate==0.27.2 \
    fastapi==0.110.0 \
    uvicorn[standard]==0.27.1

WORKDIR /app
COPY infer.py /app/infer.py

EXPOSE 8080

CMD ["uvicorn", "infer:app", "--host", "0.0.0.0", "--port", "8080"]
```

**infer.py** (example for Llama 2‑7B‑Chat)

```python
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "/model/llama2-7b-chat"       # mount point where the model will be placed

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
    gen_cfg = GenerationConfig(
        max_new_tokens=req.max_new_tokens,
        temperature=req.temperature,
        do_sample=True,
    )
    with torch.no_grad():
        out_ids = model.generate(**inputs, generation_config=gen_cfg)
    output = tokenizer.decode(out_ids[0], skip_special_tokens=True)
    return {"generated_text": output}
```

Download the model locally (e.g., with `git lfs clone https://huggingface.co/meta-llama/Llama-2-7b-chat-hf`) and place the folder at `llm_container/model/`.

Build and push the image to Azure Container Registry (ACR):

```bash
az group create --name rg-llm-acr --location eastus

az acr create \
  --resource-group rg-llm-acr \
  --name myllmregistry \
  --sku Basic \
  --admin-enabled true

az acr login --name myllmregistry

docker build -t myllmregistry.azurecr.io/llm:latest llm_container/
docker push myllmregistry.azurecr.io/llm:latest
```

### Deploy to Azure Container Apps (GPU preview)

> GPU support for Container Apps is still in preview. Ensure your subscription is enabled for the feature (`az provider register --namespace Microsoft.App`).

```bash
az group create --name rg-llm-aca --location eastus

az provider register --namespace Microsoft.App

az containerapp env create \
  --name aca-env-llm \
  --resource-group rg-llm-aca \
  --location eastus \
  --enable-workload-profiles true

az containerapp create \
  --name llm-app \
  --resource-group rg-llm-aca \
  --environment aca-env-llm \
  --image myllmregistry.azurecr.io/llm:latest \
  --cpu 2 --memory 4Gi \
  --workload-profile-name D4s_v3 \   # corresponds to 1 GPU (NVIDIA A10) in preview
  --target-port 8080 \
  --ingress external \
  --registry-server myllmregistry.azurecr.io \
  --registry-username myllmregistry \
  --registry-password $(az acr credential show -n myllmregistry --query "passwords[0].value" -o tsv)
```

The command returns a fully qualified domain name (e.g., `https://llm-app.rg-llm-aca.eastus.azurecontainerapps.io`). Test it:

```bash
curl -X POST https://<FQDN>/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Write a limerick about coffee.", "max_new_tokens":64}'
```

You should receive a JSON payload containing the generated limerick.

### Clean‑up Container Apps deployment

```bash
az containerapp delete --name llm-app --resource-group rg-llm-aca -y
az containerapp env delete --name aca-env-llm --resource-group rg-llm-aca -y
az group delete --name rg-llm-aca --yes --no-wait
az acr delete --name myllmregistry -g rg-llm-acr -y
az group delete --name rg-llm-acr --yes --no-wait
```

---

## Using libcloud to launch a GPU VM and run an LLM (generic approach)

Libcloud supports Azure ARM for VM provisioning. The following script creates a GPU VM, installs Docker, pulls the container built above, and runs it.

```python
import yaml
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

# Load credentials from clouds.yaml
with open("clouds.yaml") as f:
    config = yaml.safe_load(f)["azure"]

# Get the Azure driver
Azure = get_driver(Provider.AZURE_ARM)
driver = Azure(
    tenant_id=config["tenant_id"],
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    subscription_id=config["subscription_id"],
    region=config["location"]
)

# Choose a GPU size (Standard_NC6s_v3)
size = next(s for s in driver.list_sizes() if s.id == "Standard_NC6s_v3")

# Use the latest Ubuntu image
image = driver.get_image(
    publisher="Canonical",
    offer="UbuntuServer",
    sku="22_04-lts-gen2",
    version="latest"
)

# Launch the VM
node = driver.create_node(
    name="llm-gpu-vm",
    size=size,
    image=image,
    ex_admin_username="azureuser",
    ex_ssh_key="~/.ssh/azure_llm_key.pub",
    ex_network="default",
    ex_tags={"Purpose": "LLM"},
)

print("VM ID:", node.id)
print("Public IP:", node.public_ips[0])
```

After the VM is running, SSH in and install Docker:

```bash
ssh -i ~/.ssh/azure_llm_key azureuser@<PUBLIC_IP>

# Inside the VM
sudo apt-get update && sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
newgrp docker
docker login myllmregistry.azurecr.io   # use ACR credentials
docker run -d -p 8080:8080 myllmregistry.azurecr.io/llm:latest
```

Now you can call the model from your local machine:

```bash
curl -X POST http://<PUBLIC_IP>:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"What are the benefits of functional programming?", "max_new_tokens":128}'
```

When you’re done, destroy the VM:

```python
driver.destroy_node(node)
```

---

## Consolidated `clouds.yaml` (single source of truth)

```yaml
azure:
  tenant_id: YOUR_AZURE_TENANT_ID
  client_id: YOUR_AZURE_CLIENT_ID
  client_secret: YOUR_AZURE_CLIENT_SECRET
  subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
  location: eastus
  spot:
    # Azure VM spot settings – leave empty to accept the current price
    max_price: ""

openai:
  endpoint: https://openai-llm-demo.openai.azure.com/
  key: YOUR_OPENAI_KEY
  deployment: gpt-35-turbo   # default model name

ml:
  workspace_name: ws-llm-demo
  resource_group: rg-ml-llm
  subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
  location: eastus
  gpu_size: Standard_NC6s_v3
  compute_name: gpu-cluster

container:
  acr_name: myllmregistry
  resource_group: rg-llm-acr
  location: eastus
  image_tag: llm:latest
  workload_profile: D4s_v3    # GPU profile for Container Apps (preview)
```

*All sections reference the same values (subscription ID, location, resource group names), making it easy to keep the configuration consistent across libcloud scripts, native SDK code, and Azure CLI commands.*

---

## Cost‑Management Tips

* **Azure OpenAI** – only token usage is billed. Monitor via **Cost Management → Usage details**, filter on `Microsoft.CognitiveServices/accounts`.  
* **Azure Machine Learning** – GPU compute is billed per second. Turn the compute cluster off when idle (`ml_client.compute.begin_stop(...)`).  
* **Container Apps (GPU)** – preview pricing is roughly **$1.40 / hour** for a D4s_v3 profile. Use the **scale‑to‑zero** setting (`az containerapp update … --min-replicas 0`) to stop billing while the app is idle.  
* **Custom VM (libcloud)** – same rates as standard GPU VMs (`Standard_NC6s_v3` ≈ $1.35 / hour). Set `ex_instance_market=spot` in the libcloud script to use spot pricing and reduce cost by ~70 %.  

Add an Azure budget alert to stay within limits:

```bash
az consumption budget create \
  --resource-group rg-ml-llm \
  --budget-name llm-budget \
  --amount 50 \
  --time-grain Monthly \
  --category Cost
```

---

## Recap

* **Azure OpenAI** – fastest way to get a hosted foundation model, pay‑per‑token, no GPU handling.  
* **Azure Machine Learning** – managed endpoints for any open‑source model you can package; you control the exact model version and can fine‑tune it.  
* **Custom container on Azure Container Apps / AKS** – full control over runtime, dependencies, and model modifications (LoRA, quantization, custom preprocessing).  

Pick the path that matches your latency, cost, and custom‑code requirements, follow the steps in the corresponding section, and you’ll have a working LLM on Azure in minutes. Happy building!