# DevOps Pipelines for Large Language Models (LLMs)

!!! info "Learning Objectives"
    - Design and implement detailed CI/CD pipelines for LLM applications, covering model code, datasets, and inference APIs.
    - Integrate model versioning tools such as MLflow, DVC, and Weights & Biases.
    - Implement a multi-layered testing strategy, including traditional software tests and LLM-specific evaluations like prompt-regression and safety testing.
    - Automate the deployment of LLM inference services using cloud-native tools like Helm and ArgoCD.

## Overview

Traditional DevOps focuses on the lifecycle of software code—building, testing, and deploying deterministic applications. However, the introduction of Large Language Models (LLMs) introduces a new dimension of complexity: **stochasticity**. Unlike traditional software, where the same input always produces the same output, LLMs can produce varied responses to the same prompt. Furthermore, the logic of an LLM application is distributed across three distinct but interdependent artifacts: the **model weights**, the **training/fine-tuning data**, and the **prompts**.

**LLMOps (Large Language Model Operations)** is the application of DevOps principles to the unique lifecycle of LLMs. The goal is to create a repeatable, automated pipeline that ensures model quality, safety, and performance from the initial prompt engineering phase to production deployment and monitoring.

## Core Sections

### The LLM Pipeline Lifecycle

An LLM pipeline is not a linear path but a continuous loop. It differs from traditional CI/CD in that it must handle "Data-as-Code" and "Model-as-Artifact."

The core loop consists of:

1. **Source**: Versioning of code (Python/TypeScript), prompts (YAML/JSON), and data pointers (DVC).
2. **CI (Continuous Integration)**: Linting, unit testing of wrapper code, and initial prompt validation.
3. **Model Build/Fine-Tuning**: The process of taking a base model and adapting it via SFT (Supervised Fine-Tuning) or RLHF (Reinforcement Learning from Human Feedback).
4. **Artifact Store**: Saving the resulting model weights, tokenizer, and configuration in a registry.
5. **CD (Continuous Deployment)**: Deploying the model to an inference server (e.g., vLLM, TGI) via Kubernetes.
6. **Validation & Monitoring**: Post-deploy checks to ensure the model behaves as expected in the real world.

### Detailed Pipeline Stages

#### Source Control: Managing the Trinity

In LLMOps, "source" includes more than just `.py` files.

- **Code**: The application logic, API wrappers, and orchestration code (e.g., LangChain or LlamaIndex). Managed via Git.
- **Data**: Raw datasets and processed training sets. Since datasets are too large for Git, tools like **DVC (Data Version Control)** are used to store metadata in Git while keeping the actual data in S3/GCS.
- **Prompts**: Prompts are the "source code" of the LLM's behavior. They should be treated as first-class citizens, versioned in YAML files or managed via Prompt Management Systems (e.g., Pezzo, LangSmith) to avoid hard-coding prompts in the application.

#### Continuous Integration (CI)

The CI stage ensures that changes to the code or prompts do not break the system.

- **Static Analysis**: Standard linting (Ruff, Flake8) and type checking (MyPy).
- **Unit Testing**: Testing individual components (e.g., a function that cleans input text).
- **Integration Testing**: Testing the connection between the application and the LLM API.
- **Prompt Validation**: Running a small set of "golden examples" through the new prompt to ensure the output format (e.g., JSON) remains consistent.

#### Model Build and Training

This stage transforms a base model into a specialized one.

- **Training Pipelines**: Automated scripts that pull data from DVC, run fine-tuning jobs on GPU clusters (using frameworks like PyTorch or Hugging Face Accelerate).
- **Experiment Tracking (MLflow/W&B)**: During training, hyperparameters (learning rate, batch size) and metrics (loss, perplexity) are logged. This allows engineers to compare different training runs and select the best model.

Example Workflow:

1. Trigger: New dataset version committed to DVC.
2. Action: GitHub Action triggers a SageMaker or Vertex AI training job.
3. Result: Model weights saved to an S3 bucket.

#### Artifact Store and Model Registry

Once a model is trained, it must be stored and indexed.

- **Model Registry (MLflow Model Registry)**: Acts as a catalog for models. It tracks versions (v1, v2, v3) and stages (`Staging`, `Production`, `Archived`).
- **Container Registry (ECR/GHCR)**: The inference engine (e.g., vLLM) is packaged as a Docker image and stored in a registry.
- **The Bundle**: A deployment artifact typically consists of the model weights from the registry, the inference image from ECR, and the configuration or prompt template from Git.

#### Continuous Deployment (CD)

Deploying an LLM requires managing significant GPU resources.

- **Infrastructure as Code (IaC)**: Using Terraform or Pulumi to provision GPU nodes in Kubernetes.
- **Helm**: Packaging the inference service deployment. Helm charts define the required GPU memory, CPU limits, and environment variables.
- **GitOps (ArgoCD)**: ArgoCD monitors a Git repository containing the Helm charts. When the model version is updated in Git, ArgoCD automatically synchronizes the state of the Kubernetes cluster, performing a rolling update of the inference pods.

#### Post-Deploy Validation

The final stage ensures the model is safe and performant.

- **Smoke Tests**: Simple queries to ensure the API is reachable.
- **Canary Deployments**: Routing 5% of traffic to the new model and comparing its performance against the old model using an LLM-as-a-Judge.

### Model Versioning and Tracking

Versioning is the backbone of reproducibility in LLMOps.

| Tool | Primary Purpose | Key Feature |
| :--- | :--- | :--- |
| **MLflow** | Lifecycle Management | Model Registry, Experiment Tracking, Deployment tracking. |
| **DVC** | Data Versioning | Git-like versioning for large files (S3/Azure/GCS backend). |
| **Weights & Biases (W&B)** | Experiment Analysis | Deep visualization of training gradients, loss curves, and system metrics. |

If a model starts producing toxic outputs in production, you must be able to trace back exactly which dataset version was used, which hyperparameters were set, and which prompt version was active at that moment.

### Automated Testing Strategies

Testing LLMs requires moving beyond "pass/fail" assertions to probabilistic evaluation.

#### Traditional Software Tests

- **Unit Tests**: Verify the logic of pre-processing and post-processing code.
- **Integration Tests**: Ensure the API can handle timeouts and retries when calling the LLM.
- **Contract Tests**: Ensure the LLM output adheres to a specific schema (e.g., Pydantic models) using tools like **Instructor** or **Guardrails AI**.

#### LLM-Specific Evaluations

**Prompt Regression Testing**
When a prompt is modified, it may fix one edge case but break others.

- **Golden Dataset**: A curated set of `(input, expected_output)` pairs.
- **Regression Suite**: The new prompt is run against the golden dataset. An "LLM-as-a-Judge" (usually a more powerful model like GPT-4o) compares the new output to the expected output and assigns a similarity score.

**Safety and Guardrail Tests**
Ensuring the model does not leak sensitive data or generate harmful content.

- **PII Detection**: Using tools like Presidio to ensure no Personally Identifiable Information is present in the model's responses.
- **Adversarial Testing (Red Teaming)**: Automated scripts that attempt to "jailbreak" the model to force it to ignore its system instructions.
- **Toxicity Scanning**: Running outputs through a toxicity classifier to ensure adherence to safety guidelines.

**Performance and Load Testing**
LLMs are computationally expensive and have high latency.

- **Latency Benchmarking**: Measuring Time-To-First-Token (TTFT) and Tokens-Per-Second (TPS).
- **Load Testing (k6 / Locust)**: Simulating hundreds of concurrent users to find the saturation point of the GPU memory (VRAM) and determine when to trigger horizontal autoscaling in Kubernetes.

### Recommended Practices and Common Pitfalls

#### Recommended Practices

- **Decouple Prompts from Code**: Store prompts in a separate configuration layer to allow non-developers (Product Managers, Domain Experts) to iterate on them without needing a full code deployment.
- **Implement "Human-in-the-Loop"**: For high-stakes models, include a manual approval step in the CD pipeline where a human reviews the LLM-as-a-Judge report before the model is promoted to `Production`.
- **Monitor for Drift**: LLMs can experience "concept drift" where the nature of user queries changes over time, making the original fine-tuning obsolete.

#### Common Pitfalls

- **Over-reliance on a Single Metric**: Relying solely on Accuracy or Perplexity. Always use a combination of quantitative metrics and qualitative human review.
- **Ignoring VRAM Limits**: Deploying a model without calculating the KV cache requirements, leading to `Out-of-Memory (OOM)` crashes during peak load.
- **Hard-coding Model Versions**: Using `model: "gpt-4"` instead of a specific version like `model: "gpt-4-0613"`, which can lead to unexpected behavior when the provider updates the model.

## Summary Checklist

- [ ] Implement Git versioning for application code and prompts.
- [ ] Use DVC or similar tools for large dataset versioning.
- [ ] Establish an experiment tracking system using MLflow or W&B.
- [ ] Create a Golden Dataset for prompt regression testing.
- [ ] Implement a Model Registry to track version stages (Staging vs Production).
- [ ] Automate deployment using Helm and a GitOps controller like ArgoCD.
- [ ] Integrate safety guardrails for PII and toxicity detection.
- [ ] Perform load testing to determine GPU autoscaling thresholds.

## Assignments

!!! note "Assignment.1: Prompt Versioning Implementation"
    Create a YAML-based prompt management system where prompts are stored separately from the Python code. Implement a loader that fetches the prompt by version tag.

    ??? tip "Solution: Prompt Versioning Implementation"
        Define a `prompts.yaml` file:
        ```yaml
        summarization:
          v1: "Summarize the following text: {text}"
          v2: "Summarize the following text in 3 bullet points: {text}"
        ```
        In Python, use a helper function:
        ```python
        import yaml

        def get_prompt(task, version):
            with open("prompts.yaml", "r") as f:
                prompts = yaml.safe_load(f)
            return prompts[task][version]
        ```

!!! note "Assignment.2: Model Registry Workflow"
    Describe a GitHub Action workflow that triggers a model training job and, upon successful validation, updates a Helm chart value to point to the new model version in the MLflow Registry.

    ??? tip "Solution: Model Registry Workflow"
        1. Trigger: Push to `main` branch.
        2. Step 1: Run training script $\rightarrow$ Log model to MLflow.
        3. Step 2: Run evaluation script $\rightarrow$ If score > threshold, mark model as `Staging`.
        4. Step 3: Use `yq` or `sed` to update `values.yaml` in the GitOps repo: `modelVersion: "v2.1.0"`.
        5. Step 4: Commit and push change $\rightarrow$ ArgoCD syncs to K8s.

## References

- MLflow Documentation: https://mlflow.org/docs/latest/index.html
- DVC (Data Version Control): https://dvc.org/doc
- Weights & Biases: https://docs.wandb.ai/
- ArgoCD: https://argo-cd.readthedocs.io/

## Self-Evaluation

??? note "What is the difference between traditional CI/CD and LLMOps pipelines?"
    Traditional CI/CD manages deterministic code. LLMOps must manage stochastic outputs and version three distinct artifacts: code, data, and prompts.

??? note "Why is an 'LLM-as-a-Judge' used in prompt regression testing?"
    Because LLM outputs are probabilistic, exact string matching fails. A more powerful LLM can evaluate the semantic correctness and quality of a response compared to a reference.

??? note "What is the purpose of a Model Registry in a production pipeline?"
    A Model Registry provides a centralized catalog to track model versions, metadata, and lifecycle stages (e.g., Staging, Production), ensuring the correct model artifact is deployed.
