develop a tutorial on how i can use a LLM on AWS (no emojis and numbered items)


# Using a Large Language Model (LLM) on AWS – Step‑by‑Step Tutorial  

This tutorial shows three common ways to run an LLM on Amazon Web Services (AWS):

1. **Amazon SageMaker** – managed training and inference platform (includes JumpStart and Hugging Face integration).  
2. **Amazon Bedrock** – fully managed “foundation‑model” service (no infrastructure to manage).  
3. **Self‑managed EC2 GPU instance** – run any open‑source model you prefer on a Linux server with a GPU.

All three approaches share a common set of prerequisites (AWS account, IAM permissions, CLI configuration). The tutorial explains how to set up each environment, deploy a model, run inference, and clean up resources.

---

## 1. Prerequisites (common to all approaches)

| Item | Description |
|------|-------------|
| **AWS account** | Sign up at https://aws.amazon.com/. You need permission to create IAM roles, EC2, SageMaker, and (optionally) Bedrock resources. |
| **AWS CLI** | Install the latest version (v2). `aws --version` should show a version ≥ 2.13. |
| **Python 3.9+** | Required for the inference scripts shown below. |
| **Virtual environment** | Recommended to isolate Python dependencies: `python3 -m venv .venv && source .venv/bin/activate`. |
| **AWS credentials** | Run `aws configure` and provide *Access key ID*, *Secret access key*, *default region* (e.g., `us-east-1`), and *output format* (`json`). |
| **Sufficient quota** | For GPU workloads you need a quota for the chosen instance type (e.g., `ml.g5.xlarge`, `g5.2xlarge`, `p4d.24xlarge`). Request a limit increase via the AWS console if necessary. |
| **Optional – Docker** | Some SageMaker examples use Docker images; Docker Desktop or the Docker Engine must be installed. |

---

## 2. Deploying an LLM with Amazon SageMaker  

SageMaker provides a managed workflow that abstracts away most of the infrastructure. The steps below use **SageMaker JumpStart** to launch a pretrained Llama 2‑7B model from the Hugging Face model hub. The same pattern works for any other supported model.

### 2.1 Install SageMaker SDK and dependencies  

```bash
pip install "sagemaker>=2.152.0" "boto3>=1.34.0" "awscli>=2.13.0"
```

### 2.2 Create an execution role for SageMaker  

```bash
aws iam create-role \
  --role-name SageMakerLLMExecutionRole \
  --assume-role-policy-document file://<(cat <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "sagemaker.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF
)

# Attach the managed policies that give SageMaker access to S3 and CloudWatch
aws iam attach-role-policy \
  --role-name SageMakerLLMExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name SageMakerLLMExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess
```

Note the role ARN (`arn:aws:iam::<account-id>:role/SageMakerLLMExecutionRole`); you will need it later.

### 2.3 Create a SageMaker endpoint for Llama 2‑7B  

```python
import sagemaker
from sagemaker.huggingface import HuggingFaceModel

# -----------------------------------------------------------------
# Session and role
# -----------------------------------------------------------------
region = "us-east-1"
sagemaker_session = sagemaker.Session(boto_session=sagemaker.Session().boto_session)
role = "arn:aws:iam::<account-id>:role/SageMakerLLMExecutionRole"

# -----------------------------------------------------------------
# Model definition – Hugging Face Hub identifier
# -----------------------------------------------------------------
hub_model_id = "meta-llama/Llama-2-7b-hf"
hub_version = "1.0.0"          # use the latest version

# -----------------------------------------------------------------
# Specify the instance type that will host the model
#   - For 7 B parameters the recommended instance is ml.g5.xlarge (1 GPU)
#   - For larger models you may need ml.g5.2xlarge or p4d.24xlarge
# -----------------------------------------------------------------
instance_type = "ml.g5.xlarge"

# -----------------------------------------------------------------
# Create the Hugging Face model object
# -----------------------------------------------------------------
huggingface_model = HuggingFaceModel(
    transformers_version="4.31.0",
    pytorch_version="2.0.0",
    py_version="py39",
    model_data=None,               # Let JumpStart pull the model from HF Hub
    role=role,
    sagemaker_session=sagemaker_session,
    env={"HF_MODEL_ID": hub_model_id, "HF_TASK": "text-generation"},
)

# -----------------------------------------------------------------
# Deploy as a real‑time endpoint
# -----------------------------------------------------------------
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type=instance_type,
    endpoint_name="llama2-7b-endpoint"
)

print("Endpoint deployed:", predictor.endpoint_name)
```

**What the code does**

* Creates a **Hugging Face Model** object that tells SageMaker to download the model from the HF hub at container launch time.  
* Deploys the model to a **real‑time inference endpoint** using one GPU (`ml.g5.xlarge`).  
* The container image includes the required versions of PyTorch, Transformers, and the inference script (`/opt/program/infer.py`) automatically provided by SageMaker.

### 2.4 Run inference against the endpoint  

```python
import json

prompt = "Write a short poem about the sunrise over a mountain range."

response = predictor.predict({
    "inputs": prompt,
    "parameters": {"max_new_tokens": 64, "temperature": 0.7}
})

# The response is a JSON object; extract the generated text
generated_text = response[0]["generated_text"]
print(generated_text)
```

### 2.5 Clean up  

```python
predictor.delete_endpoint()
```

This deletes the endpoint and stops billing for the GPU instance.

---

## 3. Using Amazon Bedrock (Fully Managed Foundation Models)

Amazon Bedrock offers hosted versions of popular foundation models (e.g., Anthropic Claude, Meta Llama 2, Mistral, Cohere). Bedrock removes the need to manage any compute resources.

### 3.1 Enable Bedrock in your account  

1. Open the **AWS Management Console** → **Amazon Bedrock**.  
2. Click **Enable Bedrock**. The request may take a few minutes for the service to become available.  

### 3.2 Set up IAM permissions for Bedrock  

```bash
aws iam create-policy \
  --policy-name BedrockAccessPolicy \
  --policy-document file://<(cat <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:*",
        "bedrock-runtime:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
EOF
)

aws iam create-role \
  --role-name BedrockLLMRole \
  --assume-role-policy-document file://<(cat <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
)

aws iam attach-role-policy \
  --role-name BedrockLLMRole \
  --policy-arn arn:aws:iam::<account-id>:policy/BedrockAccessPolicy
```

You can also attach the policy directly to a user or group instead of creating a dedicated role.

### 3.3 Install the Bedrock runtime SDK  

```bash
pip install "boto3>=1.34.0"
```

### 3.4 Invoke a Bedrock model (example using Llama 2‑13B)  

```python
import boto3
import json

client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

# Choose a model ID from the Bedrock console (e.g., "meta.llama2-13b-chat-v1")
model_id = "meta.llama2-13b-chat-v1"

prompt = "Explain the significance of the Pythagorean theorem in simple terms."

body = {
    "prompt": prompt,
    "max_gen_len": 256,
    "temperature": 0.7,
    "top_p": 0.9
}

response = client.invoke_model(
    modelId=model_id,
    body=json.dumps(body).encode('utf-8')
)

generated = json.loads(response["body"].read())
print(generated["generation"])
```

**Notes**

* Bedrock charges **per token** (input + output). The pricing page (https://aws.amazon.com/bedrock/pricing/) shows the exact USD per 1 K tokens for each model.  
* No GPU instances are created; you are billed only for the tokens generated.  

### 3.5 Optional – Use Bedrock from AWS Lambda  

Bedrock is designed to be called from serverless functions. Create a simple Lambda function (Python runtime) that uses the same `boto3` code as above, attach the `BedrockLLMRole` to the function, and expose the function via API Gateway for a REST endpoint.

---

## 4. Self‑Managed LLM on an EC2 GPU Instance  

If you want full control over the runtime (custom tokenizers, LoRA adapters, or a model not yet supported by SageMaker/Bedrock), you can spin up an EC2 instance with a GPU and run the model directly.

### 4.1 Choose an EC2 GPU instance type  

| Instance | GPU | vCPU | Memory | Typical on‑demand price (USD / hour) |
|----------|-----|------|--------|--------------------------------------|
| `g5.xlarge` | NVIDIA A10G (1 GPU) | 4 | 16 GiB | ≈ $1.36 |
| `g5.2xlarge` | 2 × A10G | 8 | 32 GiB | ≈ $2.72 |
| `p4d.24xlarge` | 8 × NVIDIA A100 | 96 | 1.1 TiB | ≈ $32.77 |

For a 7 B‑parameter model a **g5.xlarge** is sufficient; for 13 B‑parameter models use **g5.2xlarge** or larger.

### 4.2 Launch the EC2 instance  

```bash
# Example: launch a g5.xlarge with Ubuntu 22.04 AMI
aws ec2 run-instances \
  --image-id ami-0b2f6494ff0b07a0e \
  --instance-type g5.xlarge \
  --key-name my-ssh-key \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=llm-ec2}]' \
  --block-device-mappings DeviceName=/dev/sda1,Ebs={VolumeSize=100,VolumeType=gp3}
```

*The AMI ID above corresponds to Ubuntu 22.04 in `us-east-1`; replace with the Ubuntu 24.04 (or 26.04 when available) AMI if you prefer.*

Wait for the instance to become **running**, then retrieve its public IP:

```bash
INSTANCE_ID=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=llm-ec2" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].InstanceId" --output text)

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text)

echo "Connect with: ssh -i ~/.ssh/my-ssh-key ubuntu@$PUBLIC_IP"
```

### 4.3 Install CUDA, PyTorch, and the model  

```bash
ssh -i ~/.ssh/my-ssh-key ubuntu@$PUBLIC_IP

# Inside the instance
sudo apt-get update && sudo apt-get install -y build-essential git wget curl

# Install Miniconda (recommended for isolation)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
source $HOME/miniconda/etc/profile.d/conda.sh
conda create -n llm python=3.10 -y
conda activate llm

# Install PyTorch with CUDA 12.1 (verify the version supported by the GPU)
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install Hugging Face Transformers and accelerate
pip install transformers accelerate

# Pull the model (example: Llama‑2‑7B‑Chat) – use the appropriate repo ID
git lfs install
git clone https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
cd Llama-2-7b-chat-hf

# Optional: convert to a faster format (e.g., GQA, flash‑attention) if needed
pip install flash-attn
```

### 4.4 Simple inference script  

Create a file `infer.py` inside the model directory:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

model_name = "./"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

def generate(prompt, max_new_tokens=128, temperature=0.7):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    generation_config = GenerationConfig(
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        do_sample=True,
    )
    with torch.no_grad():
        generated_ids = model.generate(**inputs, generation_config=generation_config)
    return tokenizer.decode(generated_ids[0], skip_special_tokens=True)

if __name__ == "__main__":
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Explain why the sky is blue."
    print(generate(prompt))
```

Run the script:

```bash
python infer.py "Write a short story about a robot learning to paint."
```

The output will be streamed to your terminal. The model runs in **half‑precision (fp16)** on the GPU, delivering inference latency of a few seconds per request.

### 4.5 Serving the model behind an API (optional)  

You can expose the model as a REST service using **FastAPI**:

```bash
pip install fastapi uvicorn
```

Create `api.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "./"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

class Prompt(BaseModel):
    text: str
    max_new_tokens: int = 256
    temperature: float = 0.7

@app.post("/generate")
def generate(request: Prompt):
    inputs = tokenizer(request.text, return_tensors="pt").to(device)
    gen_cfg = GenerationConfig(
        max_new_tokens=request.max_new_tokens,
        temperature=request.temperature,
        do_sample=True,
    )
    with torch.no_grad():
        out_ids = model.generate(**inputs, generation_config=gen_cfg)
    result = tokenizer.decode(out_ids[0], skip_special_tokens=True)
    return {"generated_text": result}
```

Run the API:

```bash
uvicorn api:app --host 0.0.0.0 --port 8080
```

The endpoint is now reachable at `http://<PUBLIC_IP>:8080/generate`. You can call it from any client:

```python
import requests
payload = {"text": "Summarize the plot of Shakespeare's Hamlet in 3 sentences."}
r = requests.post("http://<PUBLIC_IP>:8080/generate", json=payload)
print(r.json()["generated_text"])
```

### 4.6 Clean up EC2 resources  

```bash
# Terminate the instance (stop billing for the GPU)
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
```

---

## 5. Cost‑Tracking Tips  

| Service | Billing unit | Example monthly cost (7 B model, 100 k tokens or 100 h GPU) |
|---------|--------------|-------------------------------------------------------------|
| SageMaker real‑time endpoint | Hourly instance charge + data processing | 1 × ml.g5.xlarge → $1.36 / h × 720 h = $979.20 (no extra inference charge). |
| SageMaker **Serverless Inference** (optional) | Pay per request (per 1 M tokens) + compute seconds | For 100 k tokens ≈ $0.05 (very cheap for low‑volume workloads). |
| Bedrock | Tokens (input + output) | Llama 2‑13B‑chat ≈ $0.0005 / 1 k tokens → 100 k tokens ≈ $0.05. |
| EC2 GPU instance | Hourly instance charge | g5.xlarge $1.36 / h × 100 h = $136. |
| EC2 Storage | GB‑month for EBS volume | 100 GB gp3 ≈ $0.08 / GB‑mo → $8. |

**Recommendation**  

* For **development or low‑traffic inference**, use **SageMaker Serverless Inference** or **Bedrock** – you pay only for the tokens processed.  
* For **high‑throughput or low‑latency** requirements, a **real‑time SageMaker endpoint** or a **self‑managed EC2 GPU** may be more cost‑effective, especially if you can keep the instance running only when needed (use start/stop automation or auto‑scaling).  

---

## 6. End‑to‑End Example – From Notebook to Production  

Below is a compact workflow that a data scientist can run from a Jupyter notebook (hosted on SageMaker Studio or locally) and then promote to a production endpoint.

```python
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
import json
import time

# -----------------------------------------------------------------
# 1. Define the model and role
# -----------------------------------------------------------------
role = "arn:aws:iam::<account-id>:role/SageMakerLLMExecutionRole"
hub_model_id = "meta-llama/Llama-2-7b-hf"

hf_model = HuggingFaceModel(
    transformers_version="4.31.0",
    pytorch_version="2.0.0",
    py_version="py39",
    env={"HF_MODEL_ID": hub_model_id, "HF_TASK": "text-generation"},
    role=role,
)

# -----------------------------------------------------------------
# 2. Deploy a serverless endpoint (pay‑per‑request)
# -----------------------------------------------------------------
predictor = hf_model.deploy(
    endpoint_name="llama2-7b-serverless",
    instance_type="ml.m5.large",   # CPU is fine for serverless; scaling handled by SageMaker
    endpoint_type="Serverless",
    serverless_config={"memory_size_in_mb": 4096, "max_concurrency": 10},
)

# -----------------------------------------------------------------
# 3. Run inference (token‑based pricing)
# -----------------------------------------------------------------
prompt = "Give a brief definition of quantum entanglement."
payload = {"inputs": prompt, "parameters": {"max_new_tokens": 64}}
response = predictor.predict(payload)
print(json.dumps(response, indent=2))

# -----------------------------------------------------------------
# 4. Clean up
# -----------------------------------------------------------------
predictor.delete_endpoint()
```

* This notebook creates a **serverless inference endpoint** that automatically scales to handle bursts while charging only for the tokens processed.  
* Switching to a **real‑time endpoint** only requires changing `endpoint_type` to `"RealTime"` and selecting a GPU instance type.

---

## 7. Security and Best Practices  

| Practice | Reason |
|----------|--------|
| **Least‑privilege IAM** | Grant only the necessary actions (`sagemaker:*`, `bedrock:*`, `ec2:*`) to the execution role. |
| **Encrypt data at rest** | Attach an SSE‑KMS encrypted EBS volume to EC2 or use an encrypted S3 bucket for model artifacts. |
| **Network isolation** | Deploy SageMaker endpoints inside a VPC, attach a security group that only allows inbound traffic from trusted IP ranges. |
| **Logging** | Enable CloudWatch Logs for SageMaker endpoints and EC2 instances to audit usage. |
| **Model versioning** | Store model artifacts in a versioned S3 bucket or use the Hugging Face model hub tags to keep track of updates. |
| **Spot‑instance interruption handling** | When using EC2 spot, set up a termination‑notice handler (`/var/lib/cloud/instance/termination-notice`) that gracefully shuts down the model server. |
| **Cost monitoring** | Create a CloudWatch alarm on SageMaker/EC2 billing metrics or use AWS Cost Explorer to cap daily spend. |

---

## 8. Summary  

* **Amazon SageMaker** – best for a managed experience, supports both real‑time and serverless inference, integrates with the Hugging Face model hub, and provides automatic scaling.  
* **Amazon Bedrock** – fully managed LLM service; you only pay per token, no infrastructure to provision, ideal for low‑latency SaaS‑style usage.  
* **EC2 GPU** – gives full control over the environment, supports any open‑source model, but you must manage the OS, drivers, and scaling yourself; useful for research, custom fine‑tuning, or models not yet available in SageMaker/Bedrock.  

All three approaches can be driven from the same **AWS CLI / Boto3** tooling and share a common IAM policy structure. Choose the option that matches your cost, latency, and control requirements, then follow the steps in the appropriate section to get an LLM up and running on AWS.