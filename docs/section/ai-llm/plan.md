# Section Plan: Large Language Models (LLMs)

This section provides a comprehensive deep-dive into the architecture, training, deployment, and application of Large Language Models. It moves from the theoretical foundations of the Transformer to the practicalities of deploying LLMs in production cloud environments.

## Learning Objectives
By the end of this section, students will be able to:
- Explain the Transformer architecture, specifically the Self-Attention mechanism.
- Describe the LLM lifecycle: Pre-training $\rightarrow$ Supervised Fine-Tuning (SFT) $\rightarrow$ RLHF.
- Implement and optimize advanced prompting techniques (Chain-of-Thought, ReAct).
- Design and build a Retrieval Augmented Generation (RAG) pipeline.
- Analyze the hardware requirements for LLM inference (VRAM, TFLOPS, Memory Bandwidth).
- Deploy an LLM using modern serving frameworks (vLLM, TGI, Ollama).
- Evaluate LLM performance using both automated benchmarks and LLM-as-a-Judge.

---
v

## 1. LLM Foundations: The Transformer Era
- [ ] **The Transformer Architecture**
    - [ ] Encoder-Decoder vs. Decoder-only (GPT style) vs. Encoder-only (BERT style).
    - [ ] The Attention Mechanism: Queries, Keys, and Values (Q, K, V).
    - [ ] Multi-Head Attention: Learning different representation subspaces.
    - [ ] Positional Encoding: How models handle sequence order.
- [ ] **Tokenization & Embeddings**
    - [ ] Byte Pair Encoding (BPE) and SentencePiece.
    - [ ] The Embedding Space: Mapping tokens to high-dimensional vectors.
    - [ ] Token limits and the "Lost in the Middle" phenomenon.

## 2. The LLM Lifecycle: Training & Alignment
- [ ] **Stage 1: Pre-training**
    - [ ] Self-supervised learning on massive corpora (Common Crawl, The Pile).
    - [ ] Next-Token Prediction: The core objective.
    - [ ] Scaling Laws: The relationship between compute, data, and parameters.
- [ ] **Stage 2: Supervised Fine-Tuning (SFT)**
    - [ ] Instruction Tuning: Teaching the model to follow directions.
    - [ ] Dataset curation for high-quality instruction pairs.
- [ ] **Stage 3: Alignment (RLHF & DPO)**
    - [ ] Reward Modeling: Learning human preferences.
    - [ ] PPO (Proximal Policy Optimization) vs. DPO (Direct Preference Optimization).
    - [ ] Constitutional AI: Scaling oversight.

## 3. Inference & Performance Optimization
- [ ] **The Bottleneck: Memory vs. Compute**
    - [ ] VRAM requirements: Calculating model size (Parameters $\times$ Precision).
    - [ ] Memory Bandwidth: Why LLMs are memory-bound, not compute-bound.
- [ ] **Acceleration Techniques**
    - [ ] KV Caching: Avoiding redundant computations of previous tokens.
    - [ ] Quantization: FP16 $\rightarrow$ INT8 $\rightarrow$ INT4 (GPTQ, AWQ, GGUF).
    - [ ] Speculative Decoding: Using a small model to draft for a large one.
    - [ ] PagedAttention (vLLM): Reducing memory fragmentation.

## 4. Advanced Prompting & Steering
- [ ] **Prompt Engineering Fundamentals**
    - [ ] Zero-shot vs. Few-shot prompting.
    - [ ] System Prompts: Defining persona and constraints.
- [ ] **Reasoning Strategies**
    - [ ] Chain-of-Thought (CoT): "Let's think step by step."
    - [ ] Tree-of-Thoughts (ToT) and Graph-of-Thoughts.
    - [ ] Self-Consistency: Voting across multiple reasoning paths.
- [ ] **Steering the Model**
    - [ ] Logit bias and temperature control.
    - [ ] Stop sequences and constrained output (JSON mode).

## 5. RAG: Retrieval Augmented Generation
- [ ] **The Need for RAG**
    - [ ] Hallucinations vs. Knowledge Cutoffs.
    - [ ] Data Privacy: Keeping proprietary data out of training sets.
- [ ] **The RAG Pipeline**
    - [ ] Ingestion: Chunking strategies and Overlap.
    - [ ] Embedding Models: Turning text into searchable vectors.
    - [ ] Vector Databases: HNSW, FAISS, and semantic search.
- [ ] **Advanced RAG Patterns**
    - [ ] Query Expansion and Hypothetical Document Embeddings (HyDE).
    - [ ] Re-ranking: Using Cross-Encoders to refine retrieval results.
    - [ ] Contextual Compression: Reducing noise in the retrieved context.

## 6. LLM Infrastructure & Deployment
- [ ] **Hardware Selection**
    - [ ] NVIDIA H100/A100 vs. Consumer GPUs (L40S, RTX 4090).
    - [ ] Interconnects: NVLink and InfiniBand for distributed inference.
- [ ] **Serving Frameworks**
    - [ ] vLLM: Throughput optimization via PagedAttention.
    - [ ] NVIDIA Triton & TensorRT-LLM.
    - [ ] Ollama: Simplified local LLM deployment.
- [ ] **Cloud Strategies**
    - [ ] Model-as-a-Service (MaaS): OpenAI, Anthropic, Azure AI.
    - [ ] Self-hosting on Kubernetes (KServe, Ray Serve).

## 7. Evaluation, Ethics, and Safety
- [ ] **How to Measure "Intelligence"**
    - [ ] Standard Benchmarks (MMLU, GSM8K, HumanEval).
    - [ ] LLM-as-a-Judge: Using GPT-4 to grade other models.
    - [ ] Human Evaluation: A/B testing and Elo ratings.
- [ ] **Safety & Alignment**
    - [ ] Jailbreaking and Prompt Injection.
    - [ ] Red-teaming: Adversarial testing.
    - [ ] Content Filtering and Moderation APIs.

---

## Resources & Dependencies
- **Required Reading**:
    - [ ] *Attention Is All You Need* (Vaswani et al.)
    - [ ] *Training language models to follow instructions with human feedback* (InstructGPT paper)
- **Tooling**:
    - [ ] Hugging Face Transformers & Accelerate
    - [ ] PyTorch / JAX
    - [ ] vLLM or Ollama
    - [ ] Vector DB (ChromaDB or Pinecone)
- **Related Course Modules**:
    - [[02-cloud]] (GPU Infrastructure)
    - [[agentic-ai]] (Building Agents on top of LLMs)
