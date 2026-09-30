# OpenClaw Chapter Generator for Graduate Lectures

## Learning Objectives

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    * Design and implement a custom OpenClaw action for automated content generation.
    * Structure datasets for raw lecture material and generated output.
    * Engineer prompts for structured JSON output from Large Language Models (LLMs).
    * Deploy a containerized custom action within the OpenClaw ecosystem.
    * Implement monitoring and quality assurance for AI-generated academic content.

## Overview

This chapter describes how to build a reusable OpenClaw project that automatically creates structured chapter outlines (titles, subtitles, summaries, and key take-aways) from graduate-level lecture material such as slides, transcripts, PDFs, or recordings. 

The solution leverages OpenClaw's low-code pipeline, a custom Python action that interfaces with an LLM, and the platform's dataset and model-registry capabilities. By automating the distillation of lecture content, educators can rapidly generate study guides and syllabus structures while maintaining a consistent pedagogical flow.

## Project Architecture

The Chapter Generator is composed of five primary integrated components:

| Component | Role | Implementation Detail |
|-----------|------|-----------------------|
| **Dataset** | Data Persistence | Stores raw lecture assets (PDF, TXT, SRT) and the resulting generated JSON chapters. |
| **Custom Action** | Logic Engine | A FastAPI-based service that executes prompt-engineered calls to an LLM. |
| **Model Registry** | Version Control | Manages versions of the prompt templates and the specific LLM models used. |
| **Deployment** | Service Exposure | Exposes a REST endpoint (`/generate-chapter`) accessible via UI or external LMS. |
| **Monitoring** | Quality Assurance | Captures latency and token usage via Prometheus to control costs and ensure performance. |

## Prerequisites

| Item | Minimum Requirement |
|------|----------------------|
| OpenClaw instance | Running $\ge$ v2.5 (Docker-Compose or Helm) |
| Python Runtime | `python:3.11-slim` (for custom action container) |
| LLM API Key | Valid key for OpenAI, Anthropic, or HuggingFace (stored as OpenClaw secret) |
| Lecture Material | Machine-readable format (TXT, PDF, or SRT) |

## Dataset Design

A dedicated dataset called **`lecture_material`** is required to track the state of processing.

| Column | Type | Description |
|--------|------|-------------|
| `lecture_id` | String (PK) | Unique identifier for the lecture (e.g., `CS101-2024-03-12`). |
| `source_type` | Categorical | `pdf`, `txt`, `transcript`, `audio`. |
| `content` | Text (Large) | Full text extracted from the source. |
| `language` | Categorical | Language code (e.g., `en`, `de`) for multilingual prompt routing. |
| `generated_chapters` | JSON | Array of generated chapter objects (title, summary, key points). |
| `status` | Categorical | `pending`, `running`, `succeeded`, `failed`. |
| `created_at` | Timestamp | Ingestion time (auto-populated). |
| `processed_at` | Timestamp | Time when generation finished. |

**Tip:** Enable versioning on the dataset to maintain a historical record of generation runs for auditing and prompt comparison.

## Custom Action: LLM Chapter Generator

### Directory Layout

The custom action is packaged as a standalone directory for containerization:

```text
custom_actions/
└─ chapter_generator/
   ├─ Dockerfile
   ├─ requirements.txt
   ├─ main.py
   └─ prompt.txt
```

### Prompt Template (`prompt.txt`)

The system uses a separate text file for prompts to decouple the logic from the code.

```text
You are an expert academic writer. Given the full text of a graduate-level lecture, produce a structured chapter outline.

Output format (JSON):
{
  "lecture_id": "<same as input>",
  "chapters": [
    {
      "title": "<concise chapter title>",
      "subtitle": "<optional detailed subtitle>",
      "summary": "<150-200 word summary>",
      "key_points": ["point 1", "point 2", "..."]
    }
  ]
}

Guidelines:
- Create 4-7 chapters that follow a logical pedagogical flow.
- Titles must be title-cased, no trailing punctuation.
- Summaries should be self-contained and avoid referencing "the previous chapter".
- Key points must be short (<= 12 words) and actionable.
- Preserve domain-specific terminology.
```

### Implementation Details

#### Dependencies (`requirements.txt`)

```text
fastapi==0.110.*
uvicorn[standard]==0.29.*
pydantic==2.7.*
openai==1.30.*
python-dotenv==1.0.*
```

#### Containerization (`Dockerfile`)

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

#### Core Logic (`main.py`)

```python
import os
import json
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import openai

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment")
openai.api_key = OPENAI_API_KEY

with open("prompt.txt", "r", encoding="utf-8") as f:
    PROMPT_TEMPLATE = f.read()

app = FastAPI(title="Graduate Lecture Chapter Generator")
log = logging.getLogger("uvicorn.error")

class LectureRequest(BaseModel):
    lecture_id: str = Field(..., description="Unique lecture identifier")
    content: str = Field(..., description="Full lecture text")
    language: str = Field(default="en", description="Language code")

class LectureResponse(BaseModel):
    lecture_id: str
    chapters: list[dict]

@app.post("/generate-chapter", response_model=LectureResponse)
def generate(request: LectureRequest):
    try:
        prompt = PROMPT_TEMPLATE.replace("<lecture_text>", request.content)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3,
            max_tokens=1500,
        )
        raw = response.choices[0].message.content.strip()
        json_start = raw.find("{")
        json_end   = raw.rfind("}") + 1
        json_blob = raw[json_start:json_end]
        parsed = json.loads(json_blob)

        return LectureResponse(
            lecture_id=parsed["lecture_id"],
            chapters=parsed["chapters"]
        )
    except Exception as exc:
        log.exception("Chapter generation failed")
        raise HTTPException(status_code=500, detail=str(exc))
```

## Registering the Action in OpenClaw

1. **Create a Secret**: Add `openai-secret` with the key `OPENAI_API_KEY` in the OpenClaw secret store.
2. **Configure Action**: In the UI, navigate to **Project $\rightarrow$ Custom Actions $\rightarrow$ New Action**.
    * **Name**: `chapter_generator`
    * **Dockerfile path**: `./custom_actions/chapter_generator/`
    * **Env Vars**: Map `OPENAI_API_KEY` to the secret.
    * **Endpoint**: `/generate-chapter` (POST).
3. **Deploy**: Click **Build & Deploy**. OpenClaw will build the image and provide a REST endpoint URL.

## Pipeline Orchestration

The full automation is implemented as a three-step pipeline:

1. **Ingestion**: Upload lecture PDFs $\rightarrow$ Use OpenClaw OCR connector to fill the `content` column.
2. **Trigger**: A scheduled job reads rows where `status = pending` and calls the `/generate-chapter` endpoint.
3. **Result Handling**: The response JSON is written to the `generated_chapters` column and `status` is updated to `succeeded`.

```text
[Dataset: lecture_material] $\rightarrow$ [Action: chapter_generator] $\rightarrow$ [Dataset: lecture_material (update)]
```

## Evaluation and Monitoring

### Quality Metrics

| Metric | Computation Method |
|--------|--------------------|
| **Coverage** | $\frac{\text{Generated Chapters}}{\text{Baseline Chapters}}$ |
| **Readability** | Flesch Reading Ease score of the summaries. |
| **Fidelity** | Recall of domain-specific keywords in the generated text. |
| **Human Rating** | SME (Subject Matter Expert) 1-5 scale rating. |

### Monitoring with Prometheus

Integrate the following metrics into `main.py` to track system health:

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

## Extending the Generator

| Extension | Implementation Approach |
|-----------|-------------------------|
| **Domain Fine-tuning** | Train a small model on existing outlines and replace the OpenAI call with a local HuggingFace model. |
| **Multilingual Support** | Implement language-specific prompt variations and route to appropriate LLMs. |
| **Citation Extraction** | Update the JSON schema and prompt to request academic citations from the source text. |
| **LMS Integration** | Use OpenClaw webhooks to push generated content to Canvas or Moodle. |

## Deployment Checklist

* [ ] **Secrets**: `OPENAI_API_KEY` is configured in the secret store.
* [ ] **Build**: Docker image builds without errors.
* [ ] **Endpoint**: Manual `curl` test returns valid JSON.
* [ ] **Pipeline**: End-to-end flow updates the dataset `status` correctly.
* [ ] **Monitoring**: Prometheus scrapes `/metrics` and alerts are configured.
* [ ] **RBAC**: "Lecturer" role has `execute` permissions; "Student" has `read-only` access.

## Summary Checklist

* [ ] Define a versioned dataset for lecture content.
* [ ] Implement a lightweight custom action with a reusable prompt.
* [ ] Expose the action as a REST endpoint.
* [ ] Build an OpenClaw pipeline to automate the end-to-end flow.
* [ ] Instrument the service with Prometheus metrics and alerts.

## Assignments

!!! note "Assignment.1: Custom Action Implementation"

    Build the `chapter_generator` custom action as described in Section 4, ensuring the Docker image builds and the `/generate-chapter` endpoint returns valid JSON.

??? tip "Solution: Custom Action Implementation"
    The key is ensuring the `Dockerfile` uses a slim Python image and the `main.py` includes robust JSON extraction (finding the first `{` and last `}`) to handle LLM verbosity.

!!! note "Assignment.2: Pipeline Orchestration"

    Create an OpenClaw pipeline that automatically processes all `pending` lectures in the `lecture_material` dataset and updates their status.

??? tip "Solution: Pipeline Orchestration"
    Use the OpenClaw visual pipeline editor to create a loop: Dataset $\rightarrow$ Action $\rightarrow$ Dataset Update. Ensure the update step uses the `lecture_id` as the key to avoid duplicating rows.

!!! note "Assignment.3: Prompt Optimization"

    Modify `prompt.txt` to include a "Few-Shot" example of a high-quality chapter outline and compare the readability scores of the output against the zero-shot version.

??? tip "Solution: Prompt Optimization"
    Add a section to `prompt.txt` called `## Example` followed by a sample input and its ideal JSON output. Use a library like `textstat` in a separate script to compute the Flesch Reading Ease score for both outputs to quantify the improvement.

## References

* OpenClaw Documentation: https://github.com/openclaw/openclaw
* FastAPI Documentation: https://fastapi.tiangolo.com/
* Prometheus Metrics Guide: https://prometheus.io/docs/instrumenting/python/
* OpenAI API Reference: https://platform.openai.com/docs/api-reference
