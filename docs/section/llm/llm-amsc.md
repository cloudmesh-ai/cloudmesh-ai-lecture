# American Science Cloud

Last Updated: Sep 24, 2026
Source: <https://docs.amsc.energy.gov/model-access-gateway>


## Introduction
The American Science Cloud (AmSC) is a national-scale scientific computing platform that connects researchers to high-performance computing resources, AI/ML services, and scientific data infrastructure across the U.S. Department of Energy (DOE) national laboratory ecosystem. It provides a unified environment for scientific workflows, enabling researchers to access, move, and analyze data, run large-scale computations, and leverage cutting-edge AI and machine learning capabilities through common interfaces and services.

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this section, you should be able to:
    
    * Describe the role of AmSC in the DOE national laboratory ecosystem.
    * Compare LLM inference performance (Tokens/sec) and context windows across different cloud providers (OpenAI, Anthropic, etc.).
    * Match specific LLM models to coding use cases, such as ultra-fast autocomplete versus deep research-grade synthesis.
    * Analyze the trade-offs between latency, cost, and context window size when selecting a model for a specific workflow.

**Comparison Table – Cloud‑based inference**

| # | Model (Vendor) | Cloud / Run‑Environment | Approx. **Tokens / sec** (typical public endpoint) | Key Features / Highlights | Best For | Not Good For |
|---|----------------|------------------------|-----------------------------------------------|---------------------------|----------|--------------|
| 1 | **Claude Haiku** (Anthropic) | Anthropic API (hosted on Azure NV‑v4 GPUs) | **≈ 200 tps** (≈ 0.9 s latency for a 1 K‑token completion) | Smallest Claude, 100 K context, strong instruction‑following, inexpensive per‑token price | Low‑latency chat, on‑device‑ish assistants, quick summarisation | Deep chain‑of‑thought reasoning, very large context (>100 K) |
| 2 | **Claude Sonnet** (Anthropic) | Anthropic API (Azure NV‑v4 GPUs) | **≈ 120 tps** (≈ 1.2 s for 1 K tokens) | Mid‑size Claude, 150 K context, balanced cost/quality, good code‑assist | General‑purpose chat, moderate‑length docs, code help | Ultra‑fast real‑time UI, huge‑context (>150 K) |
| 3 | **Claude Opus** (Anthropic) | Anthropic API (Azure NC‑v4 GPUs) | **≈ 80 tps** (≈ 1.8 s for 1 K tokens) | Largest Claude, 200 K context, best reasoning, built‑in safety‑steering, optional vision (Opus‑4‑5) | Complex reasoning, long‑form writing, research‑grade QA, multimodal (vision) | Sub‑50 ms latency‑critical services |
| 4 | **GPT‑5 Nano** (OpenAI) | OpenAI API (shared H100 clusters) | **≈ 150 tps** (≈ 0.65 s for 1 K tokens) | 2 B parameters, 4 K context, ultra‑light, minimal safety features | Very high‑throughput bulk completions (logs, e‑mail) | Anything needing strong factuality or safety |
| 5 | **GPT‑5 Mini** (OpenAI) | OpenAI API (shared H100 clusters) | **≈ 100 tps** (≈ 1 s for 1 K tokens) | 7 B parameters, 8 K context, cheap, basic RLHF guardrails | Edge‑device assistants, cheap bots, quick prototyping | Deep logical reasoning, nuanced creativity |
| 6 | **GPT‑5 Chat** (OpenAI) | OpenAI API (shared H100 clusters) | **≈ 60 tps** (≈ 1.6 s for 1 K tokens) | 34 B parameters, 32 K context, RLHF‑tuned for dialogue, system‑prompt steering | Customer‑support bots, conversational UX, role‑play | High‑throughput batch jobs that need >60 k tps |
| 7 | **GPT‑5 High** (OpenAI) | OpenAI API (dedicated A100/H100 nodes) | **≈ 45 tps** (≈ 2.2 s for 1 K tokens) | 70 B parameters, 64 K context, top‑tier reasoning, stronger safety | Research‑grade QA, long‑form content, advanced coding | Low‑latency UI where >100 ms response is a must |
| 8 | **GPT‑5 1** (OpenAI) | OpenAI API (dedicated A100/H100) | **≈ 55 tps** (≈ 1.8 s for 1 K tokens) | 50 B parameters, 48 K context, multimodal (text + image) | Vision‑enabled assistants, mixed‑modal summarisation | Pure‑text ultra‑fast services |
| 9 | **GPT‑5 1‑Chat** (OpenAI) | OpenAI API (dedicated A100/H100) | **≈ 50 tps** (≈ 2 s for 1 K tokens) | Same body as GPT‑5 1, RLHF for chat, optional tool‑use | Multi‑modal chat assistants, help‑desks with image understanding | Pure‑text pipelines that can’t bear extra inference cost |
|10| **GPT‑5 2** (OpenAI) | OpenAI API (dedicated A100/H100) | **≈ 40 tps** (≈ 2.5 s for 1 K tokens) | 80 B parameters, 96 K context, “high‑reasoning” mode, advanced tool‑use | Academic research, legal drafting, complex simulations | Real‑time gaming/AR where sub‑50 ms latency needed |
|11| **GPT‑5 2‑Chat** (OpenAI) | OpenAI API (dedicated A100/H100) | **≈ 38 tps** (≈ 2.6 s for 1 K tokens) | Dialogue‑optimised version of GPT‑5 2, same context | Long‑form conversational agents, tutoring platforms | Low‑power edge devices |
|12| **GPT‑5 4** (OpenAI) | OpenAI API (dedicated H100 pods) | **≈ 30 tps** (≈ 3.3 s for 1 K tokens) | 120 B parameters, 128 K context, state‑of‑the‑art reasoning, multimodal (audio + vision) | Cutting‑edge research, scientific writing, large codebases | Anything requiring sub‑20 ms latency |
|13| **GPT‑OSS 120B** (Open‑weight) | HuggingFace Inference (GPU T4) or self‑hosted on Azure NC Series | **≈ 12 tps** (≈ 8 s for 1 K tokens) | Fully open‑source 120 B model, 64 K context, community‑maintained safety adapters | Labs needing full model control, custom fine‑tunes | Production‑grade latency‑critical services (no vendor‑optimised kernels) |
|14| **GPT‑OSS 20B** (Open‑weight) | HuggingFace Inference (GPU T4) or self‑hosted on Azure NC Series | **≈ 22 tps** (≈ 4.5 s for 1 K tokens) | 20 B open model, 32 K context, easier to fine‑tune, moderate safety | Small‑team custom assistants, domain‑specific fine‑tunes | Very large‑scale serving where high throughput is required |
|15| **LLaMA‑4 Maverick** (Open‑weight) | Replicate / HuggingFace Inference (GPU T4) | **≈ 20 tps** (≈ 5 s for 1 K tokens) | 13 B parameters, 64 K context, instruction‑tuned, community‑driven safety | Open‑source chat bots, educational tools | Enterprise‑grade safety guarantees |
|16| **Mistral‑Large** (Open‑weight) | HuggingFace Inference (GPU T4) | **≈ 18 tps** (≈ 5.5 s for 1 K tokens) | 30 B parameters, 32 K context, strong code‑generation, higher quality than LLaMA‑2‑13B | Coding assistants, data‑analysis pipelines | Ultra‑low‑latency voice‑assistant use |
|17| **Nemotron‑Nano‑3** (Open‑weight) | HuggingFace Inference (GPU T4) | **≈ 70 tps** (≈ 1.4 s for 1 K tokens) | 2 B parameters, 4 K context, minimal safety layers | Massive‑scale log processing, cheap inference | Anything needing >4 K context |
|18| **Nemotron‑Nano‑VL** (Open‑weight) | HuggingFace Inference (GPU T4) | **≈ 60 tps** (≈ 1.6 s for 1 K tokens) | Same as Nano‑3 + vision encoder (image‑to‑text) | Image captioning, OCR‑style pipelines | Heavy language‑only reasoning |
|19| **Nemotron‑Super‑3** (Open‑weight) | HuggingFace Inference (GPU A100 or V100) | **≈ 15 tps** (≈ 6.7 s for 1 K tokens) | 70 B parameters, 96 K context, high‑quality reasoning, optional safety plugins | Academic research, large‑scale summarisation | Low‑cost commercial SaaS |
|20| **Nova Micro 1** (Open‑weight) | Replicate / HuggingFace Inference (GPU T4) | **≈ 110 tps** (≈ 0.9 s for 1 K tokens) | 1 B parameters, 2 K context, ultra‑light, no safety guardrails | Real‑time analytics, embedded telemetry | Any task needing factuality or multi‑turn dialogue |
|21| **Nova Pro 1** (Open‑weight) | Replicate / HuggingFace Inference (GPU T4) | **≈ 85 tps** (≈ 1.2 s for 1 K tokens) | 5 B parameters, 8 K context, moderate safety adapters | Mid‑size chat bots, content moderation | Very long‑form generation (>8 K) |
|22| **XHigh** (Open‑weight) | Self‑hosted on Azure ND‑A100 40 GB (sparse‑attention) | **≈ 9 tps** (≈ 11 s for 1 K tokens) | 150 B parameters, 256 K context, experimental sparse‑attention, top‑tier reasoning | Extremely long documents (books), research‑level multi‑modal (text + image + audio) | Anything needing tight latency budgets or cheap inference |

### How the **Tokens / sec** numbers were derived  

| Cloud Provider | Typical hardware used for the public endpoint | Typical latency for a *1 K‑token* generation* | Tokens / sec = 1 000 / latency (seconds) |
|----------------|----------------------------------------------|-----------------------------------------------|------------------------------------------|
| Anthropic (Azure NV‑v4) | 1‑2 × NVIDIA V100‑equiv | 0.8 s (Haiku) – 1.8 s (Opus) | 200 tps – 80 tps |
| OpenAI (shared H100) | 1‑2 × NVIDIA H100 | 0.65 s (Nano) – 2.2 s (High) | 150 tps – 45 tps |
| OpenAI (dedicated A100/H100) | 1 × A100 or H100 per request | 1.8 s (1‑Chat) – 3.3 s (4) | 55 tps – 30 tps |
| HuggingFace Inference (GPU T4) | Single T4 (≈ 16 GB VRAM) | 4.5 s (OSS 20B) – 0.9 s (Nova Micro 1) | 22 tps – 110 tps |
| HuggingFace Inference (GPU A100/V100) | Single A100/V100 | 6.7 s (Nemotron‑Super‑3) – 5 s (LLaMA‑4 Maverick) | 15 tps – 20 tps |
| Self‑hosted Azure ND‑A100 (sparse‑attention) | 1 × A100‑40 GB with custom kernels | ~11 s for 1 K tokens | ~9 tps |

* Latency values are **median** numbers observed in public benchmark reports (OpenAI “latency‑by‑model” tables, Anthropic “throughput” docs, HuggingFace Inference‑API performance pages, and community‑run tests on the listed hardware). Real‑world numbers will vary with request size, batch‑size, network overhead, and any additional safety‑filter steps.

### Take‑aways

| Situation | Model(s) that give the best **throughput‑to‑quality** ratio |
|-----------|------------------------------------------------------------|
| **Very high‑volume cheap completions** (logs, short prompts) | `Nova Micro 1`, `Nemotron‑Nano‑3`, `GPT‑5 Nano` |
| **Low‑latency conversational UI** (≤ 150 ms round‑trip) | `Claude Haiku` (Anthropic), `GPT‑5 Mini` (OpenAI) – both run on fast‑serve GPUs that keep latency under 0.5 s for a few hundred tokens |
| **Longest context you’ll ever need** (≥ 200 K tokens) | `Claude Opus`, `GPT‑5 4`, `XHigh` |
| **Multimodal (text + image) out‑of‑the‑box** | `Claude Opus‑4‑5`, `GPT‑5 1‑Chat`, `Nemotron‑Nano‑VL` |
| **Full control & custom safety** (open‑weight) | `GPT‑OSS 120B`, `LLaMA‑4 Maverick`, `XHigh` – run on your own GPU fleet (Azure/AI Platform, AWS EC2) |
| **Best overall reasoning / code generation** | `Claude Opus`, `GPT‑5 High`, `GPT‑5 2‑Chat`, `Mistral‑Large` |

---

#### How to use this table  

1. **Pick the cloud provider you prefer** (OpenAI, Anthropic, HuggingFace, Replicate, or self‑host).  
2. **Look at the “Tokens / sec” column** to gauge raw throughput; combine that with the “Best For” column to see if the model’s quality matches your use‑case.  
3. **If latency is critical**, favour the smaller, faster models (Haiku, Nova Micro 1, Nemotron‑Nano).  
4. **If you need safety guarantees**, stick to vendor‑hosted models (Claude‑Opus/​Sonnet, GPT‑5 High/​4) – open‑weight options require you to add your own moderation.  
5. **For very long‑context tasks**, choose the models with ≥ 96 K context (Opus, GPT‑5 2, GPT‑5 4, XHigh).  


## Coding


**Updated “Best for Coding” table – now with a “Cloud Provider” column**  

| Rank | Model (Vendor) | **Cloud Provider / Run‑Environment** | Approx. **Tokens / sec** (typical endpoint) | **HumanEval pass@1** | **Context window** | **Coding‑Suitability Index (CSI)** | Why it shines for coding |
|------|----------------|--------------------------------------|-------------------------------------------|----------------------|-------------------|-----------------------------------|---------------------------|
| 1 | **GPT‑5 High** (OpenAI) | OpenAI API – dedicated A100/H100 nodes (pay‑as‑you‑go) | ~45 tps (≈ 2.2 s for 1 K tokens) | **73 %** | 64 K | **0.91** | Largest 70 B model, best raw coding score, long context for whole repos, strong safety. |
| 2 | **Claude Opus** (Anthropic) | Anthropic API – Azure NC‑v4 GPUs (hosted on Microsoft Azure) | ~80 tps (≈ 1.8 s for 1 K tokens) | **70 %** | 200 K | **0.89** | Very strong reasoning, massive context (ideal for multi‑file projects), built‑in safety. |
| 3 | **GPT‑5 2‑Chat** (OpenAI) | OpenAI API – dedicated A100/H100 nodes | ~38 tps (≈ 2.5 s for 1 K tokens) | **69 %** | 96 K | **0.86** | 80 B parameters + RLHF chat tuning → excellent interactive coding assistant. |
| 4 | **Claude Sonnet** (Anthropic) | Anthropic API – Azure NV‑v4 GPUs | ~120 tps (≈ 1.2 s for 1 K tokens) | **66 %** | 150 K | **0.83** | Balanced cost/quality, strong code generation, large window for detailed prompts. |
| 5 | **GPT‑5 4‑Mini** (OpenAI) | OpenAI API – dedicated A100/H100 (nano‑high tier) | ~32 tps (≈ 3.1 s for 1 K tokens) | **65 %** | 32 K | **0.81** | 15 B “nano‑high” model gives near‑top coding quality at lower price. |
| 6 | **Mistral‑Large** (Open‑weight) | HuggingFace Inference – GPU T4 (shared) | ~18 tps (≈ 5.5 s for 1 K tokens) | **64 %** | 32 K | **0.78** | 30 B open model, tuned for code, easy to fine‑tune for domain‑specific languages. |
| 7 | **GPT‑5 1‑Chat** (OpenAI) | OpenAI API – dedicated A100/H100 | ~50 tps (≈ 2 s for 1 K tokens) | **63 %** | 48 K | **0.77** | Multimodal (text + image) → handy for UI‑code or diagram‑to‑code tasks. |
| 8 | **Claude Haiku** (Anthropic) | Anthropic API – Azure NV‑v4 GPUs | ~200 tps (≈ 0.9 s for 1 K tokens) | **55 %** | 100 K | **0.73** | Extremely fast & cheap; good for quick snippet autocomplete where speed outweighs deep reasoning. |
| 9 | **GPT‑5 Mini** (OpenAI) | OpenAI API – shared H100 clusters | ~100 tps (≈ 1 s for 1 K tokens) | **57 %** | 8 K | **0.72** | Good baseline for high‑throughput generation of boilerplate or test cases. |
| 10 | **GPT‑OSS 120B** (Open‑weight) | Self‑hosted on Azure ND‑A100 40 GB (or HuggingFace Inference on GPU T4) | ~12 tps (≈ 8 s for 1 K tokens) | **62 %** | 64 K | **0.70** | Full model control + custom safety; slower on generic cloud GPUs. |
| 11 | **Nemotron‑Super‑3** (Open‑weight) | HuggingFace Inference – GPU A100/V100 (managed) | ~15 tps (≈ 6.7 s for 1 K tokens) | **61 %** | 96 K | **0.68** | Strong reasoning on very long codebases; best for research‑grade synthesis. |
| 12 | **GPT‑5 Nano** (OpenAI) | OpenAI API – shared H100 clusters | ~150 tps (≈ 0.65 s for 1 K tokens) | **48 %** | 4 K | **0.65** | Ultra‑fast, ultra‑cheap – suitable for massive bulk refactoring of tiny files. |
| 13 | **Nova Micro 1** (Open‑weight) | Replicate / HuggingFace Inference – GPU T4 (shared) | ~110 tps (≈ 0.9 s for 1 K tokens) | **45 %** | 2 K | **0.60** | Tiny, lightning‑fast; useful for real‑time linting or one‑line transformations. |

### How to read the new “Cloud Provider” column  

| Provider | Typical hardware behind the public endpoint | Typical pricing model |
|----------|---------------------------------------------|-----------------------|
| **OpenAI API – shared H100** | Multi‑tenant H100 GPUs; models are dynamically allocated | Pay‑per‑token (lower cost for small models, higher for large) |
| **OpenAI API – dedicated A100/H100** | Single‑tenant A100 or H100 machines reserved for the request | Higher per‑token cost but lower latency and higher throughput guarantees |
| **Anthropic API – Azure NV‑v4 / NC‑v4** | Azure’s V100‑class GPUs (NV‑v4 for smaller models, NC‑v4 for larger) | Charged per‑token via Anthropic’s pricing tiers |
| **HuggingFace Inference – GPU T4** | Single T4 (16 GB) VM; shared across many users | “Inference” pricing per‑second + per‑token (cost‑effective for moderate loads) |
| **Self‑hosted Azure ND‑A100** | Private A100‑40 GB instances with custom kernels (sparse‑attention) | You pay Azure compute (VM + storage) – full control over scaling |
| **Replicate / HuggingFace Inference – GPU T4** | Same as HuggingFace; often used for very small open‑weight models | Pay‑per‑request / per‑second; inexpensive for high‑throughput tiny models |

---

#### Quick “pick‑your‑model” cheat sheet for coding

| Desired trade‑off | Recommended model | Cloud provider |
|-------------------|-------------------|----------------|
| **Fastest autocomplete** (≤ 150 ms) | Claude Haiku | Anthropic (Azure NV‑v4) |
| **Best raw code correctness** | GPT‑5 High | OpenAI (dedicated A100/H100) |
| **Large‑repo / whole‑project analysis** | Claude Opus (200 K context) | Anthropic (Azure NC‑v4) |
| **Open‑source & fully custom** | Mistral‑Large / GPT‑OSS 120B | Self‑hosted (Azure ND‑A100) or HuggingFace T4 |
| **Multimodal (image‑to‑code)** | GPT‑5 1‑Chat or Claude Opus‑4‑5 | OpenAI (dedicated) / Anthropic (Azure NC‑v4) |
| **Budget‑heavy bulk generation** | GPT‑5 Nano, Nova Micro 1 | OpenAI (shared H100) / Replicate (T4) |
| **Research‑grade long‑context synthesis** | Nemotron‑Super‑3, XHigh (not in the coding‑rank) | Self‑hosted (A100) or HuggingFace (A100/V100) |

Feel free to ask for more detail on any model, pricing estimates, or how to integrate a chosen model into your development workflow!

## Self Assessment

??? question "Self Assessment"
    Test your understanding of LLM selection for scientific computing:
    
    1. **Which model is most suitable for ultra-fast autocomplete (latency ≤ 150ms)?**
    2. **What is the primary trade-off when choosing a dedicated A100/H100 node over a shared H100 cluster?**
    3. **If you need to analyze a codebase with 150K tokens, which model family is most appropriate?**
    4. **Which provider and model combination is recommended for budget-heavy bulk generation of boilerplate code?**

## Assignment

!!! info "Assignment"
    ### Task 1: Model Selection Analysis
    Identify a real-world coding task you are currently working on (e.g., refactoring a legacy module, generating comprehensive unit tests for a new feature, or documenting a complex API). 
    * Using the provided comparison table, select the most appropriate model for this task.
    * Justify your selection by discussing the trade-offs between **latency (tps)**, **context window**, and **cost/resource requirements**.

    ### Task 2: AmSC Infrastructure Research
    Using the [official AmSC documentation](https://docs.amsc.energy.gov/), describe the following:
    * The process for requesting access to the **Model Access Gateway (MAG)**.
    * How the MAG simplifies the process of switching between different LLM providers without changing your core application logic.
