# Observability & Reliability for LLM Services

## Learning Objectives

!!! info "Learning Objectives"
    * Instrument logging, metrics, and tracing for LLM services using OpenTelemetry, Prometheus, and Grafana.
    * Define Service Level Objectives (SLOs) and Service Level Agreements (SLAs) for latency, token-error-rate, and hallucination detection.
    * Implement resiliency patterns including autoscaling, circuit breakers, and bulkhead isolation.

## Overview

In traditional software engineering, observability is the measure of how well the internal states of a system can be inferred from its external outputs. For Large Language Model (LLM) services, this challenge is magnified by non-determinism, stochastic outputs, and the complex interplay between the prompt, the model, and the retrieved context in Retrieval-Augmented Generation (RAG) systems.

Reliability in the context of LLMs is not just about availability (uptime), but about "quality-time"—ensuring that the model provides accurate, safe, and timely responses consistently.

## The Three Pillars of LLM Observability

To effectively monitor LLM services, the traditional pillars of logging, metrics, and tracing must be extended to capture the nuances of generative AI.

### Structured Logging

Unlike traditional logs that might record a simple error message, LLM logs must capture the full context of the generation process to enable debugging and reproducibility.

**What to log:**

* Request-ID: A unique identifier that correlates logs across multiple microservices.
* Prompt Hash: A cryptographic hash of the input prompt to identify patterns in repeated queries without storing massive amounts of text in every log line.
* Model Version: The exact version or snapshot of the model (e.g., `gpt-4-0613` vs `gpt-4-turbo`) to track regressions.
* Hyperparameters: Temperature, top-p, and max tokens used for the specific request.
* Metadata: User ID, session ID, and application context.

LLMs are sensitive to minor prompt changes. Without structured logs containing the exact model version and prompt hash, it is nearly impossible to reproduce a hallucination or a refusal that occurred in production.

### Metrics: Measuring Performance and Quality

Metrics provide a high-level view of system health. LLM metrics are categorized into Operational, Performance, and Quality buckets.

#### Operational Metrics

* Request Count: Total throughput of the system.
* Error Rate: Percentage of requests resulting in 4xx or 5xx errors (e.g., API timeouts, rate limits).
* Token Usage: Total input and output tokens. This is critical for cost management and identifying token-heavy prompts.

#### Performance Metrics

* Time to First Token (TTFT): The time between the request and the first character of the response. This is the primary metric for perceived latency in streaming applications.
* Total Latency (p95/p99): The 95th and 99th percentile of the total request time.
* Tokens Per Second (TPS): The generation speed of the model.

#### Quality Metrics

* Hallucination Score: Using an LLM-as-a-Judge or a deterministic check to score the factual accuracy of a response.
* Faithfulness: In RAG systems, the degree to which the answer is derived solely from the retrieved context.
* Answer Relevance: How well the response addresses the user's actual query.

### Distributed Tracing with OpenTelemetry

LLM applications are typically pipelines rather than single-call scripts. A typical request flow may look as follows:

`User` $\rightarrow$ `API Gateway` $\rightarrow$ `Orchestrator` $\rightarrow$ `Embedding Model` $\rightarrow$ `Vector DB` $\rightarrow$ `LLM Inference Service` $\rightarrow$ `Post-processing Guardrail`.

By using OpenTelemetry (OTel) spans, engineers can visualize the waterfall of a request:

* Span 1: Embedding Generation (Latency: 50ms)
* Span 2: Vector DB Retrieval (Latency: 120ms)
* Span 3: Prompt Augmentation (Latency: 10ms)
* Span 4: LLM Generation (Latency: 2s)

Tracing allows the identification of bottlenecks. It distinguishes whether the Vector DB indexing is slow or if the LLM is struggling with a long context window.

## Defining SLOs and SLAs for LLMs

A Service Level Agreement (SLA) is a formal contract, while a Service Level Objective (SLO) is a target aimed at maintaining user satisfaction.

### Latency SLOs

Because LLMs stream data, two distinct latency objectives are defined:

1. TTFT SLO: "95% of requests shall have a Time to First Token $\leq$ 500ms."
2. End-to-End SLO: "90% of requests shall complete within 5 seconds."

### Quality and Reliability SLOs

* Token-Error-Rate: "Less than 0.1% of responses should be truncated due to `max_tokens` limits."
* Hallucination Rate: "Less than 5% of responses in the 'Medical Fact' category should be flagged as non-faithful to the source context by the LLM-Judge."

## Alerting and Incident Response

Alerts must be actionable. A spike in latency is a symptom, whereas a Vector DB connection timeout is a cause.

The standard alerting pipeline follows this flow:

`Prometheus (Scraping Metrics)` $\rightarrow$ `Alertmanager (Grouping/Routing)` $\rightarrow$ `PagerDuty/Opsgenie (Notification)`.

**Key LLM Alerting Rules:**

* Rate Limit Alert: Triggered when the 429 (Too Many Requests) error rate exceeds 1% over a 5-minute window.
* Cost Spike Alert: Triggered when token usage exceeds the daily budget by 20%.
* Quality Drop Alert: Triggered when the average Hallucination Score drops below a predefined threshold (e.g., $\text{Score} < 0.7$).

## Resiliency Patterns for LLM Services

LLM APIs are external dependencies that can fail or throttle. Systems must be designed for graceful degradation.

### Retry with Exponential Backoff

When encountering a 429 (Rate Limit) or 503 (Service Unavailable), the system should not retry immediately, as this worsens congestion. Instead, exponential backoff is used:

$WaitTime = Base \times 2^{attempt} + jitter$

### Circuit Breaker Pattern

If an LLM provider is experiencing a major outage, continuing to send requests wastes resources and increases latency.

* Closed State: Requests flow normally.
* Open State: If the error rate exceeds a threshold (e.g., 50% failure), the circuit trips. All subsequent requests fail fast or use a fallback.
* Half-Open State: Periodically allows a few requests through to check if the service has recovered.

This is often implemented at the infrastructure layer via Envoy or Istio service meshes.

### Bulkhead Isolation

Bulkheads prevent a single heavy user or complex task from consuming all available tokens or concurrency.

* User-based Bulkheads: Limit the number of concurrent requests per API key.
* Model-based Bulkheads: Separate queues for fast, low-cost models (e.g., GPT-4o-mini) and slow, powerful models (e.g., GPT-4o).

### Fallback Strategies

When the primary model fails or is too slow, the system should automatically downgrade:

* Model Fallback: `GPT-4o` $\rightarrow$ `GPT-4o-mini` $\rightarrow$ `Llama-3 (Self-hosted)`.
* Cache Fallback: If the LLM is down, return a cached response for the same prompt hash if available.
* Static Fallback: Return a polite error message indicating technical difficulties.

## Summary Checklist

| Component | Requirement | Check |
| :--- | :--- | :---: |
| Logging | Structured JSON with Request-ID, Prompt Hash, and Model Version | [ ] |
| Metrics | Tracking of TTFT, TPS, and Hallucination Scores | [ ] |
| Tracing | OpenTelemetry spans across the entire request pipeline | [ ] |
| SLOs | Defined targets for TTFT and Token-Error-Rate | [ ] |
| Resiliency | Implementation of Circuit Breakers and Exponential Backoff | [ ] |
| Fallbacks | Automated model downgrade paths configured | [ ] |

## Assignments

!!! note "Assignment.1: Observability Stack Design"
    Design a monitoring architecture for a RAG-based medical chatbot. Specify which metrics you would track in Prometheus and how you would use OpenTelemetry to identify latency in the retrieval step.

    ??? tip "Solution: Observability Stack Design"
        The architecture should include:
        1. Prometheus scraping TTFT, TPS, and Error Rates from the API gateway.
        2. A Grafana dashboard visualizing the p95 latency of the Vector DB vs. the LLM.
        3. OpenTelemetry spans wrapping the `vector_db.query()` and `llm.generate()` calls.
        4. An LLM-as-a-Judge service calculating faithfulness scores, exported as a gauge metric to Prometheus.

!!! note "Assignment.2: Implementing Circuit Breakers"
    Write a Python pseudo-code implementation or describe the Istio configuration needed to trip a circuit breaker when the LLM API returns a 5xx error rate of 20% over a 30-second window.

    ??? tip "Solution: Implementing Circuit Breakers"
        In Istio, this is configured via a `DestinationRule`:
        ```yaml
        apiVersion: networking.istio.io/v1alpha3
        kind: DestinationRule
        metadata:
          name: llm-service-cb
        spec:
          host: llm-api.provider.com
          trafficPolicy:
            outlierDetection:
              consecutive5xxErrors: 5
              interval: 30s
              baseEjectionTime: 30s
              maxEjectionPercent: 100
        ```

## References

* OpenTelemetry Documentation: [opentelemetry.io](https://opentelemetry.io)
* Prometheus Monitoring: [prometheus.io](https://prometheus.io)
* Istio Service Mesh: [istio.io](https://istio.io)
* Google SRE Book: [sre.google/sre-book/](https://sre.google/sre-book/)

## Self-Evaluation

??? note "What is the difference between TTFT and Total Latency in LLM services?"
    Time to First Token (TTFT) measures the time until the first character is generated, which is critical for user perceived performance in streaming. Total Latency measures the time until the entire response is complete.

??? note "Why is a Prompt Hash useful in structured logging?"
    A Prompt Hash allows engineers to group and analyze requests with identical inputs without storing large amounts of raw text in every log entry, facilitating the detection of patterns in hallucinations or errors.

??? note "How does Bulkhead Isolation improve LLM service reliability?"
    Bulkhead isolation prevents a single resource-intensive user or task from exhausting the system's global concurrency limits or token quotas, ensuring that other users still receive service.
