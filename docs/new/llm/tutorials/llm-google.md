
# Tutorial – Running a Large Language Model (LLM) on Google Cloud  

This guide shows three common ways to run an LLM on Google Cloud Platform (GCP):

* **Vertex AI Generative AI** – fully managed foundation‑model service (no GPU management).  
* **Vertex AI custom model deployment** – upload an open‑source model (e.g., Llama 2, Mistral) and expose a real‑time endpoint.  
* **Self‑hosted container on Cloud Run or Google Kubernetes Engine (GKE)** – total control over the runtime, supporting custom code, LoRA adapters, quantized models, etc.  

Each section contains the required setup, the commands you need to run, a short Python snippet for inference, and the steps to clean the resources after you are done.  

---  

## Common prerequisites  

* A **Google Cloud project** with billing enabled.  
* **gcloud CLI** (version >= 465). Install with  
  ```bash
  curl https://sdk.cloud.google.com | bash
  exec -l $SHELL
  gcloud init
  ```  
* **Python 3.9+** and a virtual environment.  
  ```bash
  python3 -m venv .venv && source .venv/bin/activate
  ```  
* Required Python packages (install once):  
  ```bash
  pip install --upgrade google-cloud-aiplatform google-auth requests tqdm
  ```  
* **GPU quota** if you plan to use a GPU‑backed endpoint (e.g., `nvidia-tesla-t4`, `nvidia-tesla-a100`). Request a quota increase from the GCP console → **IAM & Admin → Quotas**.  

---  

## 1. Vertex AI Generative AI (hosted foundation models)  

### Provision the Vertex AI service  

```bash
gcloud services enable aiplatform.googleapis.com
gcloud config set project YOUR_PROJECT_ID
```

### Create a model resource (optional)  

The hosted models (e.g., `chat-bison`, `gemini-pro`) are already available in the `us-central1` region, so you can start using them without creating a model resource.  

### Install the Vertex AI SDK and set up authentication  

```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/path/to/your-service-account.json
```

The service‑account must have the role **Vertex AI User** (`roles/aiplatform.user`).  

### Python inference example (using the Gemini 1.5 flash model)

```python
import os
from vertexai.preview.language_models import TextGenerationModel
import vertexai

# Initialise the Vertex AI SDK
PROJECT_ID = "YOUR_PROJECT_ID"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Choose the model – Gemini‑1.5‑flash is the most cost‑effective option for many workloads
model = TextGenerationModel.from_pretrained("gemini-1.5-flash-001")

prompt = "Write a short poem about a city at sunrise."

response = model.predict(
    prompt,
    temperature=0.7,
    max_output_tokens=64,
    top_p=0.95,
)

print(response.text)
```

### Pricing  

* **Gemini‑1.5‑flash** – $0.00025 per 1 K input tokens, $0.0005 per 1 K output tokens.  
* **Gemini‑1.5‑pro** – $0.0005 per 1 K input, $0.001 per 1 K output.  

You are billed only for the tokens processed; there is no underlying compute charge.  

### Clean‑up  

No resources are created, so disabling the Vertex AI API is enough if you want to stop all usage:  

```bash
gcloud services disable aiplatform.googleapis.com
```

---  

## 2. Deploy an open‑source LLM with Vertex AI (custom model)  

### Enable the necessary APIs  

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

### Create a storage bucket for the model artifacts  

```bash
BUCKET_NAME="llm-models-$(date +%s)"
gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME/
```

### Upload the model files  

Assuming you have the model in a local directory `./llama2-7b-chat` (downloaded from Hugging Face or another source):

```bash
gsutil -m cp -r ./llama2-7b-chat/* gs://$BUCKET_NAME/llama2-7b-chat/
```

### Register the model in Vertex AI  

```bash
MODEL_DISPLAY_NAME="llama2-7b-chat"
MODEL_ARTIFACT_URI="gs://$BUCKET_NAME/llama2-7b-chat"
gcloud ai models upload \
  --region=us-central1 \
  --display-name=$MODEL_DISPLAY_NAME \
  --container-image-uri=us-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-13:latest \
  --artifact-uri=$MODEL_ARTIFACT_URI \
  --python-package-uris=gs://$BUCKET_NAME/llama2-7b-chat/requirements.txt \
  --machine-type=n1-standard-4
```

* The container image `pytorch-cpu.1-13` works for CPU inference. For GPU inference replace the image with a GPU‑enabled one, e.g., `us-docker.pkg.dev/vertex-ai/prediction/pytorch-gpu.1-13:latest`, and add `--accelerator=type=nvidia-tesla-t4,count=1`.  

### Deploy a real‑time endpoint  

```bash
ENDPOINT_DISPLAY_NAME="llama2-endpoint"
gcloud ai endpoints create \
  --region=us-central1 \
  --display-name=$ENDPOINT_DISPLAY_NAME
```

Copy the endpoint ID returned (`ENDPOINT_ID`).  

```bash
MODEL_ID=$(gcloud ai models list --region=us-central1 --filter="displayName=$MODEL_DISPLAY_NAME" --format="value(name)")
gcloud ai endpoints deploy-model $ENDPOINT_ID \
  --region=us-central1 \
  --model=$MODEL_ID \
  --display-name=llama2-deployment \
  --machine-type=n1-standard-4 \
  --traffic-split=0=100
```

If you used a GPU container, replace `--machine-type=n1-standard-4` with a GPU‑enabled machine type such as `n1-standard-4` plus `--accelerator=type=nvidia-tesla-t4,count=1`.  

### Python client for the endpoint  

```python
import os
from google.cloud import aiplatform

PROJECT_ID = "YOUR_PROJECT_ID"
REGION = "us-central1"
ENDPOINT_ID = "YOUR_ENDPOINT_ID"

client_options = {"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
aiplatform.init(project=PROJECT_ID, location=REGION, client_options=client_options)

endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

prompt = "Explain why the sky appears blue in simple terms."
instance = {"prompt": prompt, "max_new_tokens": 128, "temperature": 0.7}
response = endpoint.predict(instances=[instance])
print(response.predictions[0]["generated_text"])
```

### Pricing  

* **Compute** – charged per hour for the machine type you selected. A `n1-standard-4` CPU instance costs ~ $0.15 / hour in `us-central1`.  
* **GPU** – a `nvidia-tesla-t4` adds roughly $0.30 / hour.  
* **Storage** – model artifacts in Cloud Storage are $0.026 / GB‑month (standard).  

### Clean‑up  

```bash
# Delete the endpoint (also removes the deployment)
gcloud ai endpoints delete $ENDPOINT_ID --region=us-central1 -q

# Delete the model registration
gcloud ai models delete $MODEL_ID --region=us-central1 -q

# Delete the bucket used for artifacts
gsutil -m rm -r gs://$BUCKET_NAME
```

---  

## 3. Self‑hosted LLM in a container (Cloud Run or GKE)  

### Build a Docker image  

Create a directory `llm_container/` with the following files.

#### Dockerfile  

```dockerfile
FROM nvidia/cuda:12.2.2-runtime-ubuntu22.04

# System packages
RUN apt-get update && apt-get install -y python3-pip git && rm -rf /var/lib/apt/lists/*

# Python dependencies (add any additional packages you need)
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

#### infer.py (FastAPI wrapper for Llama 2‑7B‑Chat)  

```python
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "/model/llama2-7b-chat"        # mount point for the model files

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
        out = model.generate(**inputs, generation_config=cfg)
    return {"generated_text": tokenizer.decode(out[0], skip_special_tokens=True)}
```

#### Add the model files  

Download the model locally (e.g., from Hugging  Face) and place the directory under `llm_container/model/`.  

#### Build and push the image to Artifact Registry  

```bash
# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Create a repository
REPO_NAME="llm-repo"
REGION="us-central1"
gcloud artifacts repositories create $REPO_NAME \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker images for LLM inference"

# Build the image
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/llm:latest"
docker build -t $IMAGE_URI llm_container/

# Push the image
docker push $IMAGE_URI
```

### Deploy to Cloud Run (fully managed, autoscaling)  

```bash
gcloud run deploy llm-service \
  --image $IMAGE_URI \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --cpu 2 --memory 4Gi \
  --timeout 600 \
  --max-instances 10 \
  --set-env-vars "MODEL_PATH=/model/llama2-7b-chat" \
  --args ""
```

**Note:** Cloud Run’s “fully managed” tier does not currently support GPUs. If you require GPU acceleration, use **Cloud Run for Anthos** (GKE‑backed) or deploy the container to GKE directly.

### Deploy to GKE with GPU nodes  

```bash
# Create a GKE cluster with GPU node pools
CLUSTER_NAME="llm-gke"
gcloud container clusters create $CLUSTER_NAME \
  --region $REGION \
  --num-nodes 1 \
  --machine-type n1-standard-4 \
  --accelerator type=nvidia-tesla-t4,count=1 \
  --enable-ip-alias

# Enable the GPU driver on the node pool
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/stable/nvidia-driver-installer/cos/daemonset-preloaded.yaml

# Create a Kubernetes deployment
cat <<'EOF' > llm-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: llm
  template:
    metadata:
      labels:
        app: llm
    spec:
      containers:
        - name: llm
          image: REPLACE_WITH_IMAGE_URI
          ports:
            - containerPort: 8080
          resources:
            limits:
              nvidia.com/gpu: 1
            requests:
              cpu: "2"
              memory: "4Gi"
EOF

# Replace placeholder
sed -i "s|REPLACE_WITH_IMAGE_URI|$IMAGE_URI|g" llm-deployment.yaml

kubectl apply -f llm-deployment.yaml

# Expose the service
kubectl expose deployment llm-deployment --type=LoadBalancer --port=80 --target-port=8080
```

Retrieve the external IP:

```bash
kubectl get service llm-deployment -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
```

### Test the endpoint  

```bash
curl -X POST http://<EXTERNAL_IP>/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Summarize the plot of Shakespeare’s Hamlet in three sentences.", "max_new_tokens":128}'
```

You should receive a JSON response containing `generated_text`.  

### Clean‑up GKE resources  

```bash
kubectl delete service llm-deployment
kubectl delete deployment llm-deployment
gcloud container clusters delete $CLUSTER_NAME --region $REGION --quiet
gcloud artifacts repositories delete $REPO_NAME --location $REGION --quiet
```

---  

## 4. Using a single `clouds.yaml` for the three approaches  

```yaml
gcp:
  project_id: YOUR_PROJECT_ID
  region: us-central1
  service_account_key: /home/you/.config/gcloud/sa-key.json

vertex_ai:
  endpoint: https://us-central1-aiplatform.googleapis.com
  model_display_name: llama2-7b-chat
  compute_type: n1-standard-4           # or n1-standard-4 + accelerator for GPU
  accelerator_type: nvidia-tesla-t4     # leave empty for CPU only

cloud_run:
  service_name: llm-service
  image_uri: us-central1-docker.pkg.dev/YOUR_PROJECT_ID/llm-repo/llm:latest
  cpu: 2
  memory: 4Gi
  max_instances: 10

gke:
  cluster_name: llm-gke
  node_count: 1
  machine_type: n1-standard-4
  accelerator_type: nvidia-tesla-t4
  accelerator_count: 1
```

All scripts in this tutorial can read the file with a small helper:

```python
import yaml, os
with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)

PROJECT_ID = cfg["gcp"]["project_id"]
REGION = cfg["gcp"]["region"]
# Use cfg["vertex_ai"], cfg["cloud_run"], cfg["gke"] as needed.
```

---  

## 5. Cost‑management checklist  

* **Vertex AI Generative AI** – token‑based billing only; set a budget alert in the Cloud Console (Billing → Budgets & alerts).  
* **Custom Vertex AI model** – GPU instances cost ~ $0.30 / hour (T4) or ~ $2.30 / hour (A100) in `us-central1`. Stop the endpoint when not in use:  
  ```bash
  gcloud ai endpoints undeploy-model ENDPOINT_ID \
    --region=us-central1 \
    --model=MODEL_ID \
    --quiet
  ```  
* **Cloud Run** – billed per vCPU‑second, memory‑second, and request count. No GPU support in the fully managed tier, so expect lower cost for CPU‑only models.  
* **GKE with GPUs** – GPU cost dominates; enable **autoscaling** and **node‑auto‑repair** to avoid idle GPU charges.  

Add a budget to keep daily spend under control:

```bash
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --budget-amount=50 \
  --budget-filter-project-id=$PROJECT_ID \
  --notifications-threshold=0.5,0.9,1.0
```

---  

## 6. Summary of the three options  

* **Vertex AI Generative AI** – zero‑ops, token‑based pricing, ideal for prototyping or production apps that can use Google’s hosted models.  
* **Vertex AI custom model** – managed endpoint with your own open‑source model, supports GPU acceleration, useful when you need a specific model or want to fine‑tune.  
* **Self‑hosted container (Cloud Run / GKE)** – full control over the runtime, dependencies, and model optimizations (quantization, LoRA). Best for experimental setups or when you need features not yet supported by Vertex AI.  

Pick the approach that best matches your latency, cost, and customization needs, follow the steps in the corresponding section, and you’ll have a functional LLM on Google Cloud in minutes. Happy building!