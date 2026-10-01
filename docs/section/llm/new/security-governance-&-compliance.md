# Security, Governance & Compliance in LLM Applications

## Learning Objectives

!!! info "Learning Objectives"
    - Secure secrets (API keys, model weights) with vaults/KMS.
    - Enforce data-privacy (PII redaction, prompt filtering).
    - Apply model-risk governance (model cards, documentation, bias audits).

## Overview

As Large Language Models (LLMs) move from experimental prototypes to production-grade enterprise applications, the security and governance landscape shifts from a secondary concern to a primary requirement. Unlike traditional software, LLM-based systems introduce a non-deterministic element and a unique attack surface that can bypass traditional perimeter defenses.

Securing an LLM application requires a "Defense in Depth" strategy. It is not enough to secure the network; one must secure the data, the model weights, the prompts, and the governance processes that dictate how the model is deployed and monitored.

## Core Sections

### Secret Management

The risk of secret leakage in LLM workflows is significant. Secrets include API keys for model providers (e.g., OpenAI, Anthropic), encryption keys for model weights, and credentials for vector databases. Hardcoding these secrets in source code or storing them in plain-text environment files leads to unauthorized access and privilege escalation.

To mitigate these risks, organizations must move toward centralized Secret Management Systems (SMS).

#### Key Tools and Technologies

- **HashiCorp Vault:** A platform-agnostic tool providing secret storage, dynamic secret generation, and lease-based access.

- **AWS Secrets Manager / Azure Key Vault / Google Secret Manager:** Cloud-native services that integrate deeply with Identity and Access Management (IAM) roles, allowing applications to fetch secrets without ever possessing a long-lived master key.

#### Best Practices for LLM Secrets

- **Dynamic Secrets:** Instead of a static API key, use systems that generate short-lived credentials that expire automatically.

- **Automatic Rotation:** Regularly rotate keys to limit the window of opportunity for an attacker who may have silently exfiltrated a key.

- **Least Privilege:** Ensure the identity fetching the secret has the narrowest possible permission set (e.g., a pod in Kubernetes should only access the secrets required for its specific microservice).

### Data Protection and Privacy

LLMs are data-intensive. Whether during fine-tuning or via Retrieval-Augmented Generation (RAG), sensitive data often flows through the system. Failure to protect this data can result in regulatory penalties (GDPR, HIPAA, CCPA) or prompt leakage, where a model reveals sensitive training data.

#### Encryption Strategies

Data must be protected at every stage of its lifecycle.

**Encryption at Rest**
Model artifacts (weights) and the datasets used for fine-tuning are high-value targets.
- **Disk Encryption:** Using AES-256 at the storage layer.
- **KMS Integration:** Using a Key Management Service (KMS) to manage the master keys that encrypt the data disks.

**Encryption in Transit**
All communication between the application, the vector database, and the LLM provider must be encrypted.
- **TLS 1.2/1.3:** Mandatory for all API calls to prevent Man-in-the-Middle (MitM) attacks.
- **mTLS (Mutual TLS):** In high-security internal environments, both the client and server should authenticate each other using certificates.

#### Privacy-Enhancing Technologies (PETs)

Standard encryption is insufficient because the LLM needs to process the data. PETs address this gap.

**PII Redaction and Masking**
Personally Identifiable Information (PII) should be removed before it reaches the LLM.
- **Redaction:** Replacing names, emails, and SSNs with tokens (e.g., `[NAME_1]`, `[EMAIL_1]`).
- **Pseudonymization:** Replacing sensitive identifiers with artificial identifiers to maintain data utility while protecting identity.

**Prompt Filtering and Sanitization**
Input sanitization prevents "Prompt Injection" attacks.
- **Allow-listing:** Restricting the types of characters or formats allowed in a prompt.
- **Guardrails:** Using a secondary, smaller LLM (a "guardrail model") to analyze the prompt for malicious intent before passing it to the primary model.

### Model Risk Governance

LLMs can hallucinate, exhibit bias, or produce harmful content. Governance ensures that the model is transparent, accountable, and aligned with organizational values.

#### Governance Artifacts

Standardized documentation is essential for auditing and reproducibility.

**Model Cards**
A Model Card provides a standardized way to report model performance and limitations. It should include:
- **Model Details:** Architecture, version, and training date.
- **Intended Use:** Specified use cases and explicitly excluded use cases.
- **Factors:** Demographics or contexts where the model may perform poorly.
- **Metrics:** Evaluation results on standard benchmarks.

**Data Sheets for Datasets**
Since the model's behavior is a reflection of its data, the data must be documented.
- **Provenance:** Origin of the data, including scraping or licensing details.
- **Composition:** Distribution of the data.
- **Preprocessing:** Cleaning methods and PII removal steps.

#### Bias Audits and Red Teaming

Governance is an active process.
- **Bias Audits:** Systematically testing the model with diverse prompts to identify skewed outputs across demographics.
- **Red Teaming:** An adversarial approach where security experts attempt to force the model to generate hate speech, leak secrets, or provide instructions for illegal acts.

### Audit Trails and Monitoring

In regulated environments, organizations must be able to reconstruct why a model produced a specific output at a specific time.

#### Infrastructure Audit Logs

These logs track system access.
- **CloudTrail (AWS) / Activity Log (Azure):** Captures API calls to the infrastructure.
- **Kubernetes Audit Logs:** Tracks changes to the pods and services hosting the model.

#### Application-Level Logging

Standard infrastructure logs are insufficient for LLMs; "Prompt-Completion" pairs are required.
- **Traceability:** Every output should be linked to a unique Request ID, the specific model version, and the exact prompt.
- **Identity Mapping:** Logs must associate the request with a verified user identity to detect abuse.

#### Monitoring for Drift and Abuse

LLM performance can degrade over time (Model Drift) or be targeted by coordinated attacks.
- **Sentiment and Toxicity Monitoring:** Real-time analysis of model outputs to detect spikes in harmful content.
- **Quota Monitoring:** Tracking token usage per user to identify potential "denial-of-wallet" attacks.

## Summary Checklist

| Domain | Requirement | Tool/Method |
| :--- | :--- | :--- |
| **Secrets** | No hardcoded keys | Vault / KMS |
| **Secrets** | Key rotation | Automated Rotation Policies |
| **Data** | PII Protection | Redaction / Masking |
| **Data** | Transit Security | TLS 1.3 / mTLS |
| **Governance** | Model Transparency | Model Cards |
| **Governance** | Data Provenance | Data Sheets |
| **Governance** | Adversarial Testing | Red Teaming |
| **Audit** | Request Traceability | Request ID $\rightarrow$ Prompt $\rightarrow$ Output |
| **Audit** | Infra Accountability | CloudTrail / Activity Log |

## Assignments

!!! note "Assignment.1: Secret Rotation Implementation"
    Describe the workflow for implementing automatic secret rotation for an LLM API key using AWS Secrets Manager and a Lambda function.

    ??? tip "Solution: Secret Rotation Implementation"
        1. **Store Secret**: Store the API key in AWS Secrets Manager.
        2. **Lambda Trigger**: Configure a rotation schedule (e.g., every 30 days) that triggers a Lambda function.
        3. **Generate New Key**: The Lambda function calls the LLM provider's API to generate a new key.
        4. **Update Secret**: The Lambda function updates the secret value in Secrets Manager.
        5. **Test/Verify**: The function tests the new key before marking the rotation as complete.
        6. **Deprecated Key**: The old key is deleted or disabled after a short overlap period.

!!! note "Assignment.2: PII Redaction Strategy"
    Design a pipeline for a healthcare LLM application that ensures no Patient Health Information (PHI) is sent to a third-party LLM provider.

    ??? tip "Solution: PII Redaction Strategy"
        1. **Input Capture**: Receive user prompt.
        2. **NER Processing**: Use a local Named Entity Recognition (NER) model (e.g., SpaCy or Presidio) to identify PHI (names, dates, IDs).
        3. **Tokenization**: Replace PHI with tokens (e.g., `[PATIENT_NAME_1]`).
        4. **Prompt Delivery**: Send the redacted prompt to the LLM provider.
        5. **Output Reception**: Receive the response.
        6. **De-tokenization**: Replace tokens back with the original PHI using a local mapping table before presenting the result to the authorized user.

## References

- GDPR (General Data Protection Regulation) official documentation.
- "Model Cards for Model Reporting" (Mitchell et al., 2019).
- "Datasheets for Datasets" (Gebru et al., 2018).
- NIST AI Risk Management Framework (AI RMF).

## Self-Evaluation

??? note "What is the difference between redaction and pseudonymization in the context of LLM privacy?"
    Redaction completely removes the sensitive information and replaces it with a generic placeholder (e.g., `[REDACTED]`), whereas pseudonymization replaces it with an artificial identifier (e.g., `[USER_A123]`) that allows the system to maintain consistency across a session or dataset without revealing the actual identity.

??? note "Why is a 'guardrail model' used instead of simple regex for prompt filtering?"
    Regex is effective for fixed patterns (like emails) but fails to capture semantic intent. A guardrail model (a smaller LLM) can understand the context and intent of a prompt to detect sophisticated prompt injection attacks or attempts to bypass safety filters that regex would miss.

??? note "What are the critical components of a Model Card for an enterprise LLM?"
    Critical components include the model's intended use cases, explicit limitations or "out-of-scope" uses, training data provenance, evaluation metrics on representative benchmarks, and documented bias or performance gaps across different demographic groups.
