
# Project ideas

## Simple One Week Project Ideas

Here are 10 demo‑project ideas that blend **REST services**, **cloud computing**, **DevOps**, and **AI**. Each one is scoped so students can build a working end‑to‑end prototype in a single lab session (≈30 min) and then extend it for deeper exploration.

!!! warning
    🔴 4. not recommended. MongoDB had some issues in the past due to licensing. Maybe instead use Openstack, AWS, Azure, Object store.  4. needs to be modified. At one point MongoDB wanted to make money and broke their deployment stack to do so. I spend time to get around this, but why make your life complicated. FerretDB may be an alternative, but we can just avoid MongoDB alltogether. I will update 4. at one point.

| # | Project idea | Core AI task | Cloud/DevOps focus |
|---|--------------|--------------|--------------------|
| 1 | **Document‑summarizer API** | Text summarisation with a Hugging Face `pegasus` model | Deploy to a serverless function (AWS Lambda / Azure Functions) → API Gateway, versioned CI/CD, cost‑monitoring |
| 2 | **Image‑tagger microservice** | Multi‑label image classification (e.g., MobileNet) | Containerise, push to a private registry, roll out on a K8s cluster with a Horizontal‑Pod‑Autoscaler |
| 3 | **Real‑time language‑translation gateway** | Translate English↔Spanish using MarianMT | Blue‑green deployment with Helm, traffic split via an ingress controller, observability with OpenTelemetry |
| 🔴 4 | **SQL‑to‑NoSQL migration assistant** | Parse SQL DDL and suggest equivalent MongoDB schema (NLP + rule‑based) | IaC (Terraform) to provision the DB services, GitOps‑style rollout with Argo CD |
| 5 | **Chat‑bot “FAQ” endpoint** | Retrieval‑augmented generation (RAG) on a static knowledge‑base | Deploy to a managed Kubernetes service (EKS/AKS/GKE), integrate Secrets Manager for API keys, log queries with Loki |
| 6 | **Anomaly‑detector for IoT telemetry** | One‑class Isolation Forest on streaming sensor data (CSV payload) | Use Kafka → KNative → REST, demonstrate canary releases and automated rollback on error‑rate thresholds |
| 7 | **Voice‑to‑text transcription service** | Whisper‑tiny model (audio → text) | GPU‑enabled node pool, show resource‑request tuning, expose Prometheus metrics for inference latency |
| 8 | **Resume‑skill extractor** | Named‑entity recognition for skills, experience, education | Deploy via a Helm chart, enable auto‑scaling based on request rate, visualize usage in Grafana |
| 9 | **Personalised product‑recommendation API** | Collaborative‑filtering model (lightFM) returning top‑N items | Show blue‑green rollout of a new model version, A/B test with a feature flag stored in ConfigMap |
|10| **Compliance‑checker for GDPR** | Detect personal data entities in free‑text (PII detection) | Use serverless containers on Cloud Run / Azure Container Apps, integrate CloudWatch/Log Analytics alerts for high‑risk detections |
|11| **Define your own** | Define your own | Use serverless containers and other DevOps if needed, Use Cloud, Use AI |


### How to use them

1. **Pick one** (or let teams choose).  
2. **Start with a minimal FastAPI (or Flask) skeleton** that accepts JSON and returns a prediction.  
3. **Containerise** with the provided Dockerfile pattern.  
4. **Push** the image to a registry (Docker Hub, ECR, GHCR).  
5. **Create a simple CI pipeline** (GitHub Actions) that builds, tests, and pushes the image.  
6. **Deploy** via Helm to a K8s cluster (or serverless if the idea uses Functions).  
7. **Add observability** – expose `/metrics` for Prometheus, send traces to Jaeger/OTel.  
8. **Optional extensions** – Auth‑API‑Key, rate‑limiting, canary rollout, GPU node pool, A/B testing, etc.

These ideas give a ready‑made menu of projects that are **different enough** but share a common skeleton so students can focus on the *specific* AI or DevOps concept you want to highlight. 

## Semester Long Project ideas

A **semester long** project is ideal for a focused, highly scoped technical project. It allows for 1 week of research/setup, 4 weeks of core implementation, and 1 week of testing, documentation, and final write-up and 1 week of refining the project. The midterm deliverable is an extensive project report justifying the cloud resources and haveing finished a detailed implementation plan.

All projects need to have:

* All projects must demnstarte dockerization (this can be as easy as installing it in a container. Some projects may need multiple containers)
* README.md
* TUTORIAL.md
* Final report.

The following project suggestions are tailored for a cloud, automation, and AI-focused course context:

!!! tip "The cmc command trick"
    Gregor will help you with the setup of the cmc command interface so you can essentially plug in your functions. This will safe you a lot of work.
    cmc contains a command generator.\, but if it does not work, get Gregors help

    ```
    mkdir vm
    cd cm
    cmc command generate vm .
    ```

    is an example 

### Overview Table


**Semester‑Long Project List**

| # | Project Title | Core Concept (one‑sentence summary) | Key Elements Mentioned in the Prompt |
|---|---------------|--------------------------------------|---------------------------------------|
| 1 | **Multi‑Cloud VM Provisioning CLI Wrapper** | A Python CLI (using `cloudmesh‑ai‑cmc` / libcloud) that can start, stop, suspend, checkpoint, and account VM instances on multiple clouds with a unified syntax. | `cmc cloud set`, `cmc vm start/stop/...`, SSH‑key & security‑group setup, `~/.config/cloudmesh/ai/clouds.yaml`, Dockerization of the tool |
| 2 | **Local LLM vs. Cloud API Benchmark Tool** | Automated benchmarking of latency, token‑throughput, and cost for a prompt suite against a local Ollama model versus a cloud LLM API. | Async harness, `cloudmesh‑ai StopWatch` (thread‑safe), per‑run unique directories, Jupyter for result prototyping, logging & data analysis |
| 3 | **Containerized RAG Microservice with Object Storage** | A Dockerised service that watches an OpenStack, S3, or Azure Blob bucket, embeds new PDFs, and serves retrieval‑augmented generation via a query endpoint. | Architecture & storage hooks, embedding + vector store, API route, end‑to‑end testing, final paper |
| 4 | **Raspberry Pi Edge Telemetry & Cloud Forwarder** | A script (Pi or Ubuntu VM) that collects system metrics and securely forwards them every minute to a cloud database/dashboard; optionally runs a lightweight LLM for prompt routing. | Metric gathering, secure transmission, cloud DB ingestion, dashboard, reliability testing, LiteLLM interface |
| 5 | **AI‑Powered Natural Language Shell Command Translator** | Plugin/extension that turns natural‑language requests (e.g., “List all active EC2 instances with high CPU usage”) into safe Cloudmesh or cloud‑CLI commands using a lightweight LLM. | Prompt engineering, safety guardrails, parser, CLI integration, edge‑case testing |
| 6 | **Automated Cloud Cost and Idle Resource Auditor** | Python script that scans a cloud account for unattached volumes, idle instances, old snapshots, estimates wasted spend, and outputs a Markdown/CSV audit report. | Read‑only SDK permissions, resource mapping, cost‑estimation formulas, reporting options |
| 7 | **Serverless Webhook Log Analyzer** | AWS Lambda or Google Cloud Function that receives error webhooks, summarizes stack traces (regex or LLM), and forwards critical alerts to Discord/Slack. | Webhook configuration, parsing logic, chat‑platform integration, security/token management, load simulation |
| 8 | **Kubernetes Edge Cluster Deployment Automation** | Ansible playbook or Python script that bootstraps K3s across local VMs/servers; includes a `cloudmesh‑ai‑cmc` CLI for cluster management. | CLI design, K3s install automation, health‑check scripts, multi‑node validation, user guide |
| 9 | **Multi‑Cloud Secret Management Utility** | Unified CLI to encrypt, store, rotate, and sync secrets/API keys across local storage and cloud parameter stores (AWS SSM, Azure Key Vault, etc.). | AES/Fernet encryption, `cmc sec` commands (init, set, get, list, sync, rotate), cloud‑key‑vault integration |
| 10 | **Automated Documentation & Architecture Diagram Generator** | Tool that parses a GitHub repo (Dockerfiles, compose files, requirements) and automatically produces an architectural summary and dependency graph (e.g., Mermaid.js). | Repo traversal, dependency parsing, graph generation, integration tests, package release |
| 11 | **Code Optimization** | Define an Agentic AI that has as input a scientific code, identifies its cernals and provides improved implementations based on GPU optimizations. Create a benchmark automatically and let it improve. | Design, implementation, deployment, testing, refinement, GitHub workflow, documentation. |
| 12 | **Define Your Own** | Student‑chosen project that must involve cloud resources (VM/Container/DB), Dockerization, and AI integration, following the same DevOps workflow. | Design, implementation, deployment, testing, refinement, GitHub workflow, documentation |

*All projects must demonstrate use of clouds, Dockerization, and AI, and follow a GitHub‑based DevOps workflow as outlined in the original brief.*
---

### 1. Multi-Cloud VM Provisioning CLI Wrapper

* **Concept:** Build a Python command-line utility using Cloudmesh-ai-cmc interfacing with a native SDKs, and/or libcloud to spin up and terminate a small virtual machine instance across two different providers (e.g., OpenStack, local, AWS or Google Cloud) using a single unified syntax. Create a cmc based comandline tool that can manage single VMs, but also create a Python API. Make sure it automatically sets up ssh-keys, security groups, 

    * You are allowed to use libcloud
    * You need to define all clouds in ~/.config/cloudmesh/ai/clouds.yaml

    Suggested commands include:

    ```
    cmc cloud set chameleon
    cmc vm start [--name=vm1] [--cloud=chameleon]
        # vm's have a counter in cloudmesh.yml so if you call the command it 
        # increases the counter. You can use yamldb for clouds.yaml
    cmc vm status
    cmc vm ps
    cmc vm kill
    cmc vm suspend
    cmc vm checkpoint
    cmc vm accounting
    cmc cloud accounting
    cmc vm start --name="vm[3-10]"
    ```

* **Breakdown:**: 

    * refine project paln (midterm)
    * use github 
    * API research & auth setup; 
    * Core wrapper script development; use cmc command generate
    * Multi-provider testing; 
    * Error handling & logging;
    * Demonstarte dockerization of the cmc command tool


### 2. Local LLM vs. Cloud API Benchmark Tool

* **Concept:** Create an automated benchmarking script that measures latency, token throughput, and cost estimation for running a specific prompt suite against a local model (via Ollama) versus a cloud API (like OpenAI or Anthropic).

* **Breakdown:** 

    * Select test prompts & setup APIs; 
    * Write async benchmarking harness; 
    * Run data collection and parse metrics;
    * Generate visual charts;
    * Use cloudmesh-ai StopWatch. make sure its threadsafe.
    * Provide logging and dataaanlysis
    * Allow independent runs to store in uniqe directories and files so that the runs and analysis can be done over multiple days and do not overwrite each other
    * Anly use jupyter for prototyping the results if needed
    * Documentation.

### 3. Containerized RAG Microservice with Object Storage

* **Concept:** Deploy a lightweight Retrieval-Augmented Generation (RAG) pipeline where a Docker container watches an Openstack Object store, AWS S3 or Azure Blob storage bucket, automatically embeds newly uploaded PDFs, and serves them via a simple query endpoint.

* **Breakdown:**

    * Architecture design & storage hooks;
    * Embedding & vector store logic;
    * API route creation;
    * Dockerization & end-to-end testing;
    * Final paper & repository cleanup.

### 4. Raspberry Pi Edge Telemetry & Cloud Forwarder

* **Concept:** Set up a script on a Raspberry Pi (or a local Linux VM simulating one) to collect system metrics (CPU, temp, memory) and securely batch-forward them to a centralized cloud database or dashboard every minute. Deply on each a micro llm. Develop a LiteLLM interafce that directs prompts to empty servers. Queue them if they are buisy.

    * Note: This can also be done on non PI servers such as VMs and you do not have to use RaspberryOS. Use ubuntu.

* **Breakdown:**
    * Metric gathering script;
    * Secure transmission protocol;
    * Cloud database ingestion setup;
    * Dashboard creation;
    * Reliability and fail-safe testing;
    * Documentation.
    * Research existig solutions.
    * Review the Lecture nots to decide if you want to do prompt distribition or if you want answers from multiple LLMs and get the best answer

### 5. AI-Powered Natural Language Shell Command Translator

* **Concept:** Develop a plugin or extension that takes a natural language string (e.g.,
*"List all active EC2 instances with high CPU usage"*) and utilizes a lightweight LLM to parse, validate, and output the correct Cloudmesh or cloud CLI command safely.
(see Project 1.)

* **Breakdown:**
    * Prompt engineering & safety guardrails;
    * Parser implementation;
    * CLI integration;
    * Edge-case testing;
    * Report writing.

### 6. Automated Cloud Cost and Idle Resource Auditor

* **Concept:** Write a Python script that scans an active cloud account for unattached storage volumes, idle compute instances, or old snapshots, calculates wasted spend, and outputs a clean markdown or CSV audit report.

* **Breakdown:**

    * Cloud provider read-only permissions & SDK setup;
    * Scanning and resource mapping logic;
    * Cost-estimation formula integration;
    * Reporting output options;
    * Final walkthrough and documentation.

### 7. Serverless Webhook Log Analyzer

* **Concept:** Implement a lightweight AWS Lambda or Google Cloud Function that receives application error webhooks, parses the stack trace using a regular expression or LLM summary, and routes critical alerts to a Discord or Slack channel.

* **Breakdown:**

    * Webhook endpoint configuration;
    * Parsing logic implementation;
    * Chat platform integration;
    * Security and token management;
    * Load and error simulation;
    * Final documentation.

### 8. Kubernetes Edge Cluster Deployment Automation

* **Concept:** Write an Ansible playbook or Python automation script that bootstraps a lightweight Kubernetes distribution (like K3s) across a set of local nodes or virtual machines to create a unified test cluster. Use cloudmesh-ai-cmc to write a commandline interface for it. 

* **Breakdown:**

    * Commandline interface design;
    * Ansible/scripting requirements definition;
    * K3s installation automation sequence;
    * Health-check verification scripts;
    * Multi-node deployment validation;
    * Write-up and user guide.

### 9. Multi-Cloud Secret Management Utility

* **Concept:** Build a unified CLI tool that securely stores, rotates, and synchronizes configuration secrets/API keys across different developer environments or cloud parameter stores.

    * Organize your tool around intuitive verb-noun or direct action patterns using `cloudmesh-ai-cmc`:

        ```
        # Initialization: Setup configuration and local encryption keys.
        cmc sec init --backend [local|aws|azure]

        # Storing Secrets: Add or update a secret value.
        cmc sec set <KEY> --env [dev|staging|prod]

        # Retrieving Secrets: Fetch and view a decrypted secret.
        cmc sec get <KEY> --env [dev|staging|prod]

        # Listing Secrets: View all available secret keys (masking the values).
        cmc sec list --env [dev|staging|prod]

        # Syncing Environments: Push local secrets to a cloud parameter store (or vice versa).
        cmc sec sync --from local --to aws-ssm

        # Rotating Secrets: Trigger a rotation workflow for an API key.
        cmc sec rotate <KEY>
        ```

* **Breakdown:**

    * Encryption scheme research (AES/Fernet);
    * Core encryption/decryption CLI features;
    * Cloud key-vault integration;
    * Security auditing;
    * Final documentation.

!!! note
    Thos project may be too easy and may need to be enhanced in some fashion.

### 10. Automated Documentation & Architecture Diagram Generator

* **Concept:** Create a tool that parses a GitHub repository's directory layout and configuration files (`Dockerfile`, `docker-compose.yml`, requirements) to automatically generate an architectural summary and component dependency graph.

This may already exist, so if it does figure out if you can come up with a modification or a different project.

* **Breakdown:**

    * Repo traversal logic;
    * Dependency parser rules;
    * Graph generation output (e.g., Mermaid.js format);
    * Integration tests against sample repos;
    * Refinement;
    * Final package release.

### 11 AI Guided Code Optimization 

* **Concept:** Define an Agentic AI that has as input a scientific code, identifies its compute kernals and provides improved implementations based on GPU optimizations. Create a benchmark automatically and let it improve. 

* **Breakdown**: 

    * Design
    * Implementation
    * Deployment
    * Testing
    * Refinement
    * GitHub workflow
    * Documentation. 

### 12. Define your own

* **Concept:** Define your own. Must use 

    * Cloud (VM, Container, optionally cloudhosted DB/object store).
    * Dockerization
    * (Optional) Other DevOps where needed 
    * AI integration

* **Breakdown:** Define your own and expand upon

    * Design
    * Implement
    * Deploy 
    * Test 
    * Refinement;
    * add ...
    

---

### Key Milestones for a Plan:

* **Midterm**: Completed project proposal with cloud utilization estimates

* **3/4 of Semester**: Working proof-of-concept (skeleton code running).
* **Final:** Finished implementation, documentation, and code in github. Clean GitHub repository, robust `README.md`, and a 2-to-3 page technical report summary.
* **Presentation:** On final day of class presentation, you have 
    `class time + 1 / Number projects`

!!! warning
    You can customize the project based on your interests, however you need to show use of Clouds, DevOps (github workrflow for documentation how it is shown in cloudmesh-ai is minimum), and AI. All projects must show Dorkerization.
    