
**Cost Comparison of Major LLM Offering Platforms (October 2024)**  

The table below summarizes the *pay‑as‑you‑go* prices for the most common usage patterns on each cloud vendor. All numbers are shown in US dollars and are rounded to three significant figures. Prices vary by region, service tier, and volume discounts; the values listed represent the **default on‑demand rate for the “US East/West” region** unless a specific region is noted.

| Provider | Service / Model | Billing Unit | Approx. Price (per 1 000 tokens *input + output*) | Approx. Compute Cost (GPU hour) | Free‑Tier / Always‑Free offering | Comments |
|----------|----------------|--------------|-----------------------------------------------|--------------------------------|----------------------------------|----------|
| **AWS** | **Bedrock – Claude‑3 Haiku** | Token | $0.0002 / 1 k tokens (input + output) | – | No dedicated free tier; new accounts receive $300 credits for 12 months (can be applied to Bedrock). | Bedrock also offers Claude‑3 Sonnet ($0.0008) and Claude‑3 Opus ($0.0015). |
| **AWS** | **Bedrock – Anthropic Claude‑2** | Token | $0.00025 / 1 k tokens | – | – | Same $300 free‑credit applies. |
| **AWS** | **SageMaker Real‑time Endpoint (custom model, e.g., Llama 2‑7B)** | GPU hour | – | ml.g5.xlarge (1 × NVIDIA A10G) ≈ $1.36 / hour | No free tier; the **SageMaker Serverless Inference** option bills per request (≈ $0.0002 / 1 k tokens) but only supports CPU‑based models. | GPU pricing rises sharply for larger instances (ml.g5.2xlarge ≈ $2.72 / h). |
| **Azure** | **Azure OpenAI – gpt‑35‑turbo** | Token | $0.0002 / 1 k input, $0.0002 / 1 k output | – | No free tier; new customers receive $200 credits (can be used for Azure OpenAI). | Higher‑capacity models (gpt‑4, gpt‑4‑turbo) cost $0.00075 – $0.001 / k input and $0.0015 – $0.003 / k output. |
| **Azure** | **Azure ML Managed Endpoint (custom LLM, e.g., Llama 2‑13B)** | GPU hour | – | Standard_NC6s_v3 (1 × V100) ≈ $1.35 / hour | No free tier; **Azure Free Account** gives $200 credits for 30 days (usable for Azure ML). | GPU pricing varies by family; A100‑based VMs cost ≈ $2.30 / hour. |
| **Google Cloud** | **Vertex AI – Gemini 1.5 Flash** | Token | $0.00025 / 1 k input, $0.0005 / 1 k output | – | No dedicated free tier; **$300 credits** for new accounts (can cover Vertex AI). | Gemini 1.5 Pro costs $0.00075 / k input and $0.0015 / k output. |
| **Google Cloud** | **Vertex AI Custom Model (e.g., Llama 2‑7B on NVIDIA T4)** | GPU hour | – | n1-standard‑4 + 1 × T4 ≈ $0.30 / hour (US‑central1) | No free tier; the **Always‑Free** tier includes 1 vCPU + 1 GiB RAM but **no GPU**. | Larger GPU shapes (A100) cost ≈ $2.20 / hour. |
| **Oracle Cloud** | **OCI Generative AI – Claude‑2‑100k** | Token | $0.0005 / 1 k input, $0.0015 / 1 k output | – | **Always‑Free**: 1 OCPU + 1 GiB RAM, 100 GB block storage, 10 TB outbound data. No free GPU. | OCI also offers **Claude‑3‑haiku** (≈ $0.0002 / k input, $0.0006 / k output). |
| **Oracle Cloud** | **OCI Data Science / Custom GPU (e.g., Llama 2‑7B on VM.Standard.NC6)** | GPU hour | – | VM.Standard.NC6 (1 × V100) ≈ $0.30 / hour (US‑Ashburn) | No separate free tier; you can run the **Always‑Free** shape (VM.Standard.E2.1.Micro) for CPU‑only inference at $0 / hour. | GPU pricing similar to other vendors; A100‑based shapes are ≈ $2.00 / hour. |
| **Anthropic** | **Claude 3‑Haiku** | Token | $0.0002 / 1 k input, $0.0006 / 1 k output | – | No free tier; new accounts receive $5 credit (usable for up to 100 k tokens). | Claude 3‑Sonnet and Claude 3‑Opus cost roughly 3 × and 6 × the Haiku rates respectively. |
| **OpenAI** | **GPT‑4o‑mini** | Token | $0.00015 / 1 k input, $0.00060 / 1 k output | – | No free tier; **Free‑Trial credit** of $18 (≈ $5 / month for 2 months) can be applied to GPT‑4o‑mini usage. | GPT‑4‑turbo: $0.00075 / k input, $0.003 / k output. GPT‑4‑32k: $0.003 / k input, $0.012 / k output. |
| **OpenAI** | **Fine‑tuned Custom Model (hosted on OpenAI Platform)** | Token | Same as base model used for fine‑tuning | – | No free tier; same trial credit applies. | Custom fine‑tuning incurs an additional per‑token training cost (≈ $0.003 / 1 k tokens). |

### Key Take‑aways

* **Token‑based services** (Bedrock, Azure OpenAI, Vertex AI, OCI GenAI, Anthropic, OpenAI) are cheapest when the workload is lightweight (few hundred tokens per request). Prices cluster around **$0.0002 – $0.0008 per 1 k input tokens** and **$0.0005 – $0.003 per 1 k output tokens**.
* **GPU‑accelerated custom endpoints** (SageMaker, Azure ML, Vertex AI, OCI Data Science) cost **$0.30 – $2.30 per GPU‑hour** depending on the GPU family. They are the only practical way to run very large models (13 B + parameters) with low latency.
* **Free‑tier / always‑free offerings** are limited to **CPU‑only** inference (small models) and small storage quotas. No major cloud currently offers a permanent free‑tier for GPU‑based LLM inference. The only free‑tier entry points are:
  * **Oracle Cloud Always‑Free** – 1 OCPU + 1 GiB RAM, 100 GB block storage, 10 TB outbound data (CPU‑only).  
  * **Google Cloud Free Tier** – 1 vCPU + 1 GiB RAM (F1‑micro) for 744 h/month; no GPU.  
  * **AWS Free Tier** – 750 h/month of t2.micro/t3.micro (CPU‑only).  
  * **Azure Free Account** – 750 h/month of B1s (CPU‑only).  
* **Trial credits** (AWS $300, Azure $200, GCP $300, Anthropic $5, OpenAI $18) can be used to experiment with any service, including GPU‑based custom models, but they expire after the designated period (usually 12 months for the major clouds).  
* **Regional price differences** can be ≈ 10 % higher in Europe or Asia‑Pacific regions; always verify pricing in the target region via the provider’s pricing calculator.  

### When to Choose Each Option  

* **Pure token‑based APIs** (Bedrock, Azure OpenAI, Vertex AI, OCI GenAI, Anthropic, OpenAI) – best for low‑latency, low‑volume workloads where you do not need a custom model. They require no GPU management and scale automatically.  
* **Custom GPU endpoints** – required when you need to run open‑source models not offered as a service, fine‑tune a model, or need deterministic latency at scale. Choose the provider whose GPU pricing best matches your expected utilization (e.g., T4 for moderate loads, A100 for heavy loads).  
* **Free‑tier CPU‑only** – suitable for prototyping small prompts, teaching, or running very small models (e.g., distilled 2‑B‑parameter LMs). Not realistic for production‑grade LLMs.  

---  

## Example Cost Scenarios  

| Scenario | Approximate Monthly Cost (USD) | Details |
|----------|------------------------------|---------|
| **Chatbot using GPT‑4o‑mini** – 10 k tokens per day (≈ 300 k tokens/month) | $0.12 (input ≈ $0.045, output ≈ $0.075) | Token‑only pricing; no compute charges. |
| **Claude 3‑Haiku via Anthropic** – 50 k tokens per day (≈ 1.5 M tokens/month) | $2.10 (input ≈ $0.30, output ≈ $1.80) | Token‑only. |
| **Custom Llama 2‑7B on a T4 GPU (ml.g5.xlarge) – 24/7 operation** | $972 (720 h × $1.36) | GPU compute dominates; no token charge beyond storage. |
| **Fine‑tuned GPT‑3.5‑Turbo (50 k training tokens, 100 k inference tokens/month)** | $0.45 (training ≈ $0.15, inference ≈ $0.30) | Uses OpenAI token pricing; fine‑tuning cost is minimal at this scale. |
| **Vertex AI custom model on a T4 (n1-standard‑4 + 1 T4) – 12 h/day** | $108 (≈ $0.30 / h × 12 h × 30 d) | GPU compute only; token usage added if you enable request‑level logging. |
| **Oracle OCI GenAI Claude 2‑100k – 200 k tokens/month** | $0.40 (input ≈ $0.10, output ≈ $0.30) | Token‑only. |
| **Free‑tier CPU‑only model (e.g., Mistral‑7B‑instruct on AWS t3.micro) – 100 k tokens/month** | $0 (within 750 h free tier, storage ≤ 5 GB) | No compute charge; only minimal storage cost (≈ $0.10). |

These examples illustrate that **token‑only services** are dramatically cheaper for low‑volume workloads, while **GPU‑based custom deployments** become cost‑effective only when the workload demands high throughput or low latency for large models.

---  

## Bottom Line  

* For **most applications** where you can work with the models offered as a service, choose a token‑based API (Bedrock, Azure OpenAI, Vertex AI, Anthropic, OpenAI).  
* If you need **full control over the model architecture, fine‑tuning, or larger parameter counts**, provision a GPU instance through SageMaker, Azure ML, Vertex AI, or OCI Data Science—remember to size the GPU appropriately to avoid paying for idle capacity.  
* **Free‑tier resources** are limited to CPU‑only instances and modest storage; they are useful for initial prototyping but not for production‑grade LLM inference.  
* Leverage **trial credits** where available to evaluate each platform before committing to ongoing spend.  

Use the pricing figures above as a baseline, verify the latest rates on each provider’s pricing calculator, and model your expected token or GPU usage to obtain a precise forecast for your specific workload.