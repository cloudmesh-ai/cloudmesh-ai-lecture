# The Economics of LLM Services: On-Premise vs. Cloud API

!!! info "Learning Objectives"
    - Build a cost-per-token model for on-premise hardware.
    - Estimate throughput and latency for various model sizes.
    - Compare on-premise Total Cost of Ownership (TCO) against cloud API pricing.
    - Identify business differentiators for local LLM deployments.
    - Operationalize local models using the LM Studio ecosystem.

The decision to deploy Large Language Models (LLMs) typically involves a trade-off between Capital Expenditure (CAPEX) and Operational Expenditure (OPEX). On-premise deployment requires significant upfront investment in hardware and ongoing maintenance but offers potential long-term cost advantages and complete data sovereignty. Conversely, cloud-based APIs provide immediate scalability and low entry costs but involve recurring per-token fees and dependency on third-party infrastructure.

Understanding the cost-per-token metric is essential for businesses to determine the break-even point where owning hardware becomes more economical than renting API access.

## Cost-per-Token Modeling

To determine the viability of an on-premise service, a business must calculate the Total Cost of Ownership (TCO) and amortize it over the expected lifespan of the hardware.

### Hardware Amortization and Operating Expenses

The TCO includes the initial purchase price, software licensing, electricity, and operational overhead.

Example: Cost model for a single DGX Spark unit.

| Cost Item | Amount (USD) | Amortization Method |
| :--- | :--- | :--- |
| Capital cost | $35,000 | 3-year straight-line depreciation -> $11,667/yr |
| Enterprise Software & Warranty | $5,000/yr | Direct annual expense |
| Electricity (300W avg) | $315/yr | 0.3kW x 24h x 365d x $0.12/kWh |
| Ops & Staff Buffer | $5,000/yr | Standard 1-person ops benchmark |
| **Total Annual Cost** | **$22,000/yr** | |

### Calculating Cost per GPU-Hour

The cost per hour is derived by dividing the total annual cost by the total available GPU-hours. For a system with 4 GPUs running at 100% utilization:

Total GPU-hours = 4 GPUs x 24 hours x 365 days = 35,040 hours/year.

```text
Cost per GPU-hour = 22,000 / 35,040 approx $0.63 / GPU-hour
```

If utilization drops to 50%, the effective cost per hour increases to approximately $1.25.

## Performance and Throughput Estimation

Throughput is measured in tokens per second (tps). For decoder-only transformers, the computational cost is approximately 2 x parameter count in FLOPs per token. When using hardware with sparsity support, this effective cost is halved.

### Theoretical vs. Real-World Throughput

Raw FLOP rates are rarely achieved due to memory bandwidth bottlenecks and kernel launch overhead. A 40% margin is typically applied to derive production-grade estimates.

| Model | Parameters (B) | Effective FLOPs / token | Theoretical tps | Real-world tps | Latency / token |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Mistral-7B | 7 | 7 x 10^9 | 142,857 | 86,000 | 0.012 ms |
| LLaMA-2-70B | 70 | 70 x 10^9 | 14,286 | 8,600 | 0.12 ms |
| Custom 200B | 200 | 200 x 10^9 | 5,000 | 3,000 | 0.33 ms |

### Tokens per Hour Calculation

Based on the real-world tps, the hourly capacity for a single unit is:

- Mistral-7B: 86,000 x 3,600 approx 310M tokens/h
- LLaMA-2-70B: 8,600 x 3,600 approx 31M tokens/h
- 200B model: 3,000 x 3,600 approx 11M tokens/h

## Competitive Analysis: On-Premise vs. Cloud APIs

Comparing on-premise costs to cloud providers like Google Gemini allows a business to identify the volume threshold at which local hosting becomes cheaper.

### Cloud API Pricing Model

Cloud providers typically charge per 1,000 tokens. For example, a high-tier model might cost $0.01 for input and $0.03 for output per 1k tokens.

### Break-even Analysis

On-premise costs are fixed regardless of volume, while API costs scale linearly. The break-even point occurs when:

```text
(Annual TCO) / (Annual Tokens Processed) < (Average API Cost per Token)
```

For high-volume applications processing billions of tokens per month, on-premise hardware typically reduces the cost per token by 10x to 100x compared to public APIs.

## Business Differentiators and GTM Strategy

Cost is not the only factor. Local deployment provides strategic advantages that APIs cannot match.

### Key Differentiators

- **Data Privacy**: Data never leaves the local network, which is critical for healthcare, legal, and government sectors.
- **Latency**: Eliminating network round-trips to cloud servers reduces time-to-first-token.
- **Customization**: Local models can be fine-tuned on proprietary datasets without sharing data with the API provider.
- **SLA Control**: The business has full control over availability and performance.

### Go-to-Market (GTM) Pricing Suggestions

Businesses selling LLM services on-premise can use several pricing models:

1. **Flat Monthly Subscription**: Billed as "Infrastructure as a Service" (IaaS).
2. **Bundle Pricing**: Including LLM access as a feature of a larger software package.
3. **Hybrid Model**: Using a small local model for routing/filtering and a cloud API for complex reasoning.

## Operationalizing Local LLMs with LM Studio

LM Studio provides a standardized environment for loading, testing, and serving local models via an OpenAI-compatible API.

### Model Management via CLI

The `lms` command-line interface allows for automated model lifecycle management.

Loading a model with a custom identifier:

```bash
lms load <model-key> --identifier "production-model"
```

Checking the connection status of linked devices:

```bash
lms link status
```

### Programmatic Integration with Python

The `lmstudio` Python SDK enables the integration of local models into applications.

Example: Synchronous request.

```python
import lmstudio as lms

client = lms.Client()
model = client.llm.model("production-model")
response = model.respond("Explain the TCO of LLMs.")
print(response)
```

Example: Asynchronous streaming for real-time UI updates.

```python
import asyncio
from contextlib import AsyncExitStack
import lmstudio as lms

async def main():
    async with AsyncExitStack() as stack:
        client = await stack.enter_async_context(lms.AsyncClient())
        model = await client.llm.model("production-model")
        
        stream = await model.respond_stream("Explain TCO.")
        
        async for fragment in stream:
            print(fragment.content, end="", flush=True)
        print()

if __name__ == "__main__":
    asyncio.run(main())
```

!!! tip "Summary Checklist"
    - Calculated Total Cost of Ownership (TCO) including CAPEX and OPEX.
    - Derived cost per GPU-hour based on system utilization.
    - Estimated real-world throughput using the 40% margin rule.
    - Compared on-premise cost per token against cloud API pricing.
    - Identified strategic advantages of local deployment (privacy, latency).
    - Implemented local model serving using the LM Studio SDK.

!!! note "Exercise 1: TCO Calculation"
    Calculate the annual TCO for a system containing two NVIDIA RTX 4090 GPUs. Assume a hardware cost of $4,000, electricity at $0.15/kWh, and $2,000 in annual support costs. Determine the cost per GPU-hour at 70% utilization.

!!! note "Exercise 2: Throughput Projection"
    Estimate the real-world tokens per second for a 13B parameter model on a system capable of 0.5 PFLOPs. Apply the 40% real-world margin and calculate the total tokens the system can produce in a 24-hour window.

!!! note "Exercise 3: Async Implementation"
    Create a Python script using `lms.AsyncClient` that sends three different prompts to a local model concurrently and prints the results as they arrive.
