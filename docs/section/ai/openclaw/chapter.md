
# OpenClaw Chapter Generator for Graduate Lectures  

**Purpose** – This document describes how to build a reusable OpenClaw project that automatically creates structured chapter outlines (titles, subtitles, summaries, and key take‑aways) from graduate‑level lecture material (slides, transcripts, PDFs, or recordings). The solution leverages OpenClaw’s low‑code pipeline, a custom Python action that calls a large‑language model (LLM), and the platform’s dataset, model‑registry, and deployment capabilities.  

---  

## 1. Project Overview  

| Component | Role |
|-----------|------|
| **Dataset** | Stores raw lecture assets (text ↔ PDF, OCR, or transcript) and the generated chapter information. |
| **Custom Action – LLM Generator** | Executes a prompt‑engineered call to an LLM (OpenAI, Anthropic, or Hugging‑Face) and returns a structured JSON payload. |
| **Model Registry** | Version‑controls the prompt template and any fine‑tuned model you may create later. |
| **Deployment** | Exposes a REST endpoint (`/generate-chapter`) that can be called from the OpenClaw UI, notebooks, or external LMS systems. |
| **Monitoring** | Captures latency, success‑rate, and token‑usage metrics for cost‑control and quality assurance. |

---  

## 2. Prerequisites  

| Item | Minimum Requirement |
|------|----------------------|
| OpenClaw instance (Docker‑Compose or Helm) | Running ≥ v2.5 |
| Python 3.11 runtime (inside custom‑action container) | `python:3.11‑slim` |
| LLM API key (OpenAI, Anthropic, or Hugging‑Face) | Stored as an OpenClaw secret |
| (Optional) GPU node | For locally fine‑tuned models |
| Access to lecture material in a machine‑readable format (TXT, PDF, SRT) | – |

---  

## 3. Dataset Design  

Create a dataset called **`lecture_material`** with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `lecture_id` | String (primary key) | Unique identifier for the lecture (e.g., `CS101-2024-03-12`). |
| `source_type` | Categorical | `pdf`, `txt`, `transcript`, `audio`. |
| `content` | Text (large) | Full text extracted from the source. |
| `language` | Categorical | `en`, `de`, … (used for multilingual prompts). |
| `generated_chapters` | JSON (nullable) | Result of the generation step (array of chapters). |
| `status` | Categorical | `pending`, `running`, `succeeded`, `failed`. |
| `created_at` | Timestamp | Ingestion time (auto‑populated). |
| `processed_at` | Timestamp (nullable) | Time when generation finished. |

**Tip:** Enable versioning on the dataset so you can keep a historical record of each generation run.

---  

## 4. Custom Action – LLM Chapter Generator  

### 4.1. Directory Layout  

```
custom_actions/
└─ chapter_generator/
   ├─ Dockerfile
   ├─ requirements.txt
   ├─ main.py
   └─ prompt.txt
```

### 4.2. Prompt Template (`prompt.txt`)  

```
You are an expert academic writer. Given the full text of a graduate‑level lecture, produce a structured chapter outline.

Output format (JSON):
{
  "lecture_id": "<same as input>",
  "chapters": [
    {
      "title": "<concise chapter title>",
      "subtitle": "<optional detailed subtitle>",
      "summary": "<150‑200 word summary>",
      "key_points": ["point 1", "point 2", "..."]
    },
    …
  ]
}

Guidelines:
- Create 4‑7 chapters that follow a logical pedagogical flow.
- Titles must be title‑cased, no trailing punctuation.
- Summaries should be self‑contained and avoid referencing “the previous chapter”.
- Key points must be short (≤ 12 words) and actionable.
- Preserve domain‑specific terminology.
```

### 4.3. `requirements.txt`  

```
fastapi==0.110.*
uvicorn[standard]==0.29.*
pydantic==2.7.*
openai==1.30.*   # or anthropic, or huggingface_hub
python-dotenv==1.0.*
```

### 4.4. Dockerfile  

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

### 4.5. Core Logic (`main.py`)  

```python
import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import openai   # replace with anthropic or huggingface if needed

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment")
openai.api_key = OPENAI_API_KEY

# Load prompt template once
with open("prompt.txt", "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

# ----------------------------------------------------------------------
# FastAPI app
# ----------------------------------------------------------------------
app = FastAPI(title="Graduate Lecture Chapter Generator")
log = logging.getLogger("uvicorn.error")

class LectureRequest(BaseModel):
    lecture_id: str = Field(..., description="Unique lecture identifier")
    content: str = Field(..., description="Full lecture text")
    language: str = Field(default="en", description="Language code (e.g., en, de)")

class LectureResponse(BaseModel):
    lecture_id: str
    chapters: list[dict]

@app.post("/generate-chapter", response_model=LectureResponse)
def generate(request: LectureRequest):
    """Generate a chapter outline from raw lecture text."""
    try:
        # Fill the template
        prompt = PROMPT_TEMPLATE.replace("<lecture_text>", request.content)

        # Call the LLM
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",                # adjust to your model
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )
        # Extract the JSON part from the model output
        raw = response.choices[0].message.content.strip()
        # Ensure it is valid JSON – guard against stray text
        json_start = raw.find("{")
        json_end   = raw.rfind("}") + 1
        json_blob = raw[json_start:json_end]
        parsed = json.loads(json_blob)

        # Return only the chapters (lecture_id is echoed)
        return LectureResponse(
            lecture_id=parsed["lecture_id"],
            chapters=parsed["chapters"]
        )
    except Exception as exc:
        log.exception("Chapter generation failed")
        raise HTTPException(status_code=500, detail=str(exc))
```

**Explanation of key sections**

* **Prompt handling** – The template is loaded from `prompt.txt` and the lecture content is interpolated at runtime, keeping the prompting logic separate from code.
* **Model selection** – `gpt-4o-mini` is inexpensive for bulk processing. Swap it for a fine‑tuned model later without changing the endpoint.
* **JSON extraction** – The response is trimmed to the first `{` … last `}` pair to robustly retrieve the JSON payload even if the model adds explanatory text.
* **Error handling** – All exceptions are logged and transformed into a 500 HTTP response, which OpenClaw’s audit log captures automatically.

---  

## 5. Registering the Action in OpenClaw  

1. **Create a secret** named `openai-secret` with key `OPENAI_API_KEY`.  
2. In the OpenClaw UI, navigate to **Project → Custom Actions → New Action**.  
   * **Name:** `chapter_generator`  
   * **Dockerfile path:** `./custom_actions/chapter_generator/`  
   * **Environment variables:** add `OPENAI_API_KEY` referencing the secret (`valueFrom.secretKeyRef`).  
   * **Expose endpoint:** `/generate-chapter` (POST).  
   * **Scaling:** Serverless (auto‑scale) or Dedicated (if you need guaranteed latency).  
3. Click **Build & Deploy**. OpenClaw builds the image, stores it in the internal registry, and creates an endpoint URL (e.g., `https://api.myorg.com/v1/endpoints/chapter_generator/predict`).  

---  

## 6. Pipeline Orchestration  

Create a **pipeline** that ties the dataset and the custom action together:

1. **Ingestion step** – Upload or stream lecture PDFs → use OpenClaw’s built‑in OCR connector to fill the `content` column.  
2. **Trigger step** – A scheduled job or a UI button that reads rows with `status = pending` and calls the `/generate-chapter` endpoint.  
3. **Result handling** – The response JSON is written back to the `generated_chapters` column and `status` is set to `succeeded`. Failures write the error message into a separate `error_message` column and set `status = failed`.  

OpenClaw’s visual pipeline editor can represent these steps as nodes:

```
[Dataset: lecture_material] → [Action: chapter_generator] → [Dataset: lecture_material (update)]
```

---  

## 7. Evaluation & Quality Assurance  

| Metric | How to compute |
|--------|----------------|
| **Coverage** | Compare number of generated chapters against a manually curated baseline (e.g., `len(generated) / len(baseline)`). |
| **Readability** | Run `textstat.flesch_reading_ease` on each chapter summary. |
| **Terminology fidelity** | Use a domain‑specific keyword list; compute recall of these keywords in the generated text. |
| **Human rating** | Export a sample set to a spreadsheet and collect a 1‑5 rating from subject‑matter experts. |

Store the evaluation results in a separate dataset (`chapter_evaluation`) to track improvements over time.

---  

## 8. Monitoring & Alerting  

Add the following Prometheus metrics to `main.py` (insert after the imports):

```python
from prometheus_client import Counter, Histogram

REQ_COUNTER = Counter(
    "chapter_generator_requests_total",
    "Total requests to chapter generator",
    ["model", "status"]
)
LATENCY = Histogram(
    "chapter_generator_latency_seconds",
    "Latency of chapter generation",
    buckets=[0.5, 1, 2, 5, 10, 30]
)
```

Wrap the generation call:

```python
with LATENCY.time():
    # existing LLM call
    ...
REQ_COUNTER.labels(model="gpt-4o-mini", status="success").inc()
```

Configure alerts in Alertmanager, for example:

```
- alert: ChapterGenHighLatency
  expr: chapter_generator_latency_seconds_bucket{le="10"} < 0.9
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Chapter generation latency > 10 s for 90 % of requests"
```

---  

## 9. Extending the Generator  

| Extension | Description |
|-----------|-------------|
| **Fine‑tuned domain model** | Train a small instruction‑tuned model on a collection of existing lecture outlines and replace the OpenAI call with a local Hugging‑Face model (`transformers`). |
| **Multilingual support** | Add language‑specific prompt variations in `prompt.txt` and switch the LLM model (e.g., `gpt‑4o‑turbo‑fr` for French). |
| **Citation extraction** | Extend the JSON schema with a `references` array and augment the prompt to request academic citations. |
| **Integration with LMS** | Use OpenClaw’s webhook feature to push generated chapters directly into a Canvas or Moodle course page. |
| **Batch processing** | Implement a bulk endpoint that accepts a list of lecture IDs and returns a zip of JSON files. |

---  

## 10. Deployment Checklist  

1. **Secrets** – Verify that `OPENAI_API_KEY` (or alternative) is present in OpenClaw’s secret store.  
2. **Docker image** – Ensure the custom action builds without errors (`docker build .`).  
3. **Endpoint test** – Perform a manual `curl` call with a short lecture excerpt; confirm the JSON structure.  
4. **Pipeline validation** – Run the end‑to‑end pipeline on a single lecture and check that `generated_chapters` is populated and `status` updates correctly.  
5. **Monitoring** – Confirm Prometheus scrapes `/metrics` and that alerts fire as expected when latency spikes.  
6. **Access control** – Grant the “Lecturer” role `execute` permission on the `chapter_generator` action; restrict “Student” role to read‑only access on the dataset.  

---  

## 11. Reference Implementation (Optional)  

Below is a minimal Python script that can be run locally to test the prompt and JSON extraction logic before packaging it into the OpenClaw action. It uses the same `prompt.txt` and OpenAI API.

```python
import os, json, openai

# Load environment
openai.api_key = os.getenv("OPENAI_API_KEY")
with open("prompt.txt", "r", encoding="utf-8") as f:
    prompt_template = f.read()

# Sample lecture excerpt
lecture_text = """
In this lecture we discuss the dual formulation of linear programming, the concept of complementary slackness, and how these ideas lead to the simplex algorithm’s optimality conditions. ...
"""

prompt = prompt_template.replace("<lecture_text>", lecture_text)

response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": prompt}],
    temperature=0.3,
    max_tokens=1200,
)

raw = response.choices[0].message.content.strip()
json_start = raw.find("{")
json_end   = raw.rfind("}") + 1
parsed = json.loads(raw[json_start:json_end])

print(json.dumps(parsed, indent=2))
```

Running this script yields a JSON object matching the schema defined in Section 4.2. Use it to iterate on prompt wording before committing the version to OpenClaw.

---  

## 12. Summary  

*Define a versioned dataset for lecture content.*  
*Implement a lightweight custom action that calls an LLM with a clear, reusable prompt.*  
*Expose the action as a REST endpoint and build an OpenClaw pipeline to automate the end‑to‑end flow.*  
*Instrument the service with Prometheus metrics, set up alerts, and store evaluation results for continuous improvement.*  

With this setup, graduate programs can quickly produce high‑quality chapter outlines for lecture series, facilitating syllabus creation, study guides, and automated content publishing—all while retaining full auditability and governance through OpenClaw.