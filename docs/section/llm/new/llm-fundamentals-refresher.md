# LLM Fundamentals Refresher

!!! info "Learning Objectives"
    - Explain the Transformer architecture, including self-attention, multi-head attention, and positional encoding.
    - Contrast different tokenization methods: BPE, SentencePiece, and byte-level UTF-8.
    - Differentiate between zero-shot, few-shot, and chain-of-thought prompting strategies.
    - Compare full fine-tuning with parameter-efficient methods like LoRA.
    - Analyze inference control techniques including temperature, top-k, and top-p sampling.
    - Identify the resource requirements and bottlenecks (VRAM, KV cache) associated with LLM deployment.

## Overview

The LLM Fundamentals Refresher provides the theoretical and practical foundations of Large Language Models. For DevOps engineers, this knowledge is essential for optimizing inference latency, managing GPU memory, and choosing the correct adaptation strategy for domain-specific tasks.

## The Transformer Architecture

The Transformer shifted the paradigm of Natural Language Processing (NLP) from sequential processing to parallel processing.

### Self-Attention Mechanism

Traditional sequential models processed text word-by-word, often losing context from the beginning of a long sequence. Self-attention allows every token in a sequence to attend to every other token simultaneously.

For every token, the model generates three vectors:
- Query ($Q$): What the token is looking for.
- Key ($K$): What the token contains.
- Value ($V$): The information the token provides.

The attention score is calculated using a scaled dot-product:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

The dot product measures similarity between the Query and Keys, while the scaling factor $\sqrt{d_k}$ prevents gradients from becoming too small during training.

### Multi-Head Attention (MHA)

A single attention head may only capture one type of relationship. Multi-Head Attention runs multiple attention mechanisms in parallel, allowing the model to simultaneously track different aspects of the text:
- Grammatical structure.
- Coreference (e.g., resolving what "it" refers to).
- Semantic meaning.

The outputs are concatenated and linearly transformed back to the original dimension.

### Positional Encoding

Transformers process all tokens in parallel and are permutation invariant. To maintain word order, positional encodings are added to input embeddings. These vectors use sine and cosine functions of different frequencies to provide a coordinate system, allowing the model to distinguish the order of words.

## Tokenization: From Text to Tensors

LLMs process tensors of numbers rather than raw text. Tokenization is the process of converting strings into these numerical representations.

### The Tokenization Trade-off

- Word-level tokenization creates massive vocabularies and fails on unknown words (the Out-of-Vocabulary problem).
- Character-level tokenization results in sequences that are too long, increasing compute costs and hindering the learning of semantic meaning.

### Byte Pair Encoding (BPE)

BPE is a subword tokenization method. It starts with individual characters and iteratively merges the most frequent adjacent pairs into new, single tokens. Common suffixes and prefixes become single tokens, while rare words are represented as sequences of sub-units.

### SentencePiece and Byte-level UTF-8

- SentencePiece: Treats input as a raw stream and includes spaces as a special character (`_`), making it effective for languages without clear word boundaries.
- Byte-level UTF-8 (BBPE): Starts with the 256 possible bytes of UTF-8. This ensures any string can be tokenized without encountering "Unknown" (`<UNK>`) tokens.

## Prompt Engineering: Steering the Model

Prompting provides context to steer a pre-trained model toward a desired output without modifying internal weights.

### Zero-Shot Prompting

The model is given a task without examples, relying entirely on general knowledge from pre-training.
*Example: "Translate the following English text to French: 'Hello, how are you?'"*

### Few-Shot Prompting

The model is provided with several input-output pairs before the actual query to establish format or logic.
*Example:*
"Input: Happy $\rightarrow$ Output: Positive"
"Input: Sad $\rightarrow$ Output: Negative"
"Input: Excited $\rightarrow$ Output: "

### Chain-of-Thought (CoT)

CoT encourages the model to generate intermediate reasoning steps. By breaking complex problems into smaller steps, the model improves its performance on math, logic, and symbolic reasoning.

## Adapting Models: Fine-Tuning vs. PEFT

General-purpose models are often adapted for specific domains using specialized datasets.

### Full Fine-Tuning

This involves updating all parameters of the model.
- Pros: Maximum performance on the target task.
- Cons: High compute and VRAM cost, risk of "catastrophic forgetting" of general knowledge, and high storage overhead for each model version.

### Parameter-Efficient Fine-Tuning (PEFT)

PEFT updates only a small fraction of parameters to reduce cost and storage.

#### Low-Rank Adaptation (LoRA)

LoRA freezes the main weight matrix $W$ and adds two smaller matrices, $A$ and $B$. The update is represented as:
$$W_{\text{updated}} = W_{\text{frozen}} + (A \times B)$$

This reduces the training compute budget and allows small "adapters" (a few megabytes) to be swapped on top of a single base model.

## Inference Techniques: Controlling Output

Text generation is a probabilistic process of predicting the next token.

### Greedy Search vs. Beam Search

- Greedy Search: Always picks the token with the highest probability. It is fast but can be repetitive.
- Beam Search: Maintains $k$ most likely sequences and chooses the one with the highest cumulative probability.

### Temperature and Sampling

Temperature ($T$) scales the logits before the softmax function:
- Low Temperature ($T < 1$): Sharpens the distribution, making the output more deterministic and focused.
- High Temperature ($T > 1$): Flattens the distribution, increasing diversity and randomness.

### Top-K and Top-P (Nucleus) Sampling

To avoid nonsensical tokens from the "long tail" of the distribution:
- Top-K: Only the top $K$ most likely tokens are considered.
- Top-P: The smallest set of tokens whose cumulative probability exceeds $P$ is considered.

## Resource Profiles & Infrastructure Requirements

LLMs are both compute-bound and memory-bound.

### The VRAM Bottleneck

Model weights must reside in VRAM. Space requirements depend on precision:
- FP32: 4 bytes per parameter.
- FP16/BF16: 2 bytes per parameter.
- INT4: $\approx 0.5$ bytes per parameter.

A 7-billion parameter model in FP16 requires approximately 14 GB of VRAM for weights alone.

### The KV Cache

The model stores Key (K) and Value (V) vectors for previous tokens to avoid redundant calculations. The KV cache grows linearly with sequence length and batch size, often becoming the primary memory bottleneck for long-context windows.

### Latency vs. Throughput

- Time to First Token (TTFT): Time to process the input prompt.
- Tokens Per Second (TPS): Speed of generation.
- Trade-off: Increasing batch size improves total throughput but increases latency for individual users.

## Summary Checklist

- [ ] Explain the role of Queries, Keys, and Values in self-attention.
- [ ] Describe how positional encoding solves the permutation invariance of Transformers.
- [ ] Differentiate between BPE and Byte-level UTF-8 tokenization.
- [ ] Compare the resource requirements of full fine-tuning vs. LoRA.
- [ ] Explain the effect of temperature on token probability distributions.
- [ ] Calculate VRAM requirements for a model based on parameter count and precision.

## Assignments

!!! note "Assignment.1: VRAM Calculation"
    Calculate the minimum VRAM required to load a 13B parameter model in FP16 precision and INT4 precision.

    ??? tip "Solution: VRAM Calculation"
        - FP16: $13 \times 10^9 \text{ parameters} \times 2 \text{ bytes/param} = 26 \text{ GB}$.
        - INT4: $13 \times 10^9 \text{ parameters} \times 0.5 \text{ bytes/param} = 6.5 \text{ GB}$.

!!! note "Assignment.2: Prompt Engineering"
    Convert the following zero-shot prompt into a few-shot prompt: "Classify the sentiment of this review as Positive or Negative: 'The battery life is amazing!'"

    ??? tip "Solution: Prompt Engineering"
        "Review: 'The food was bland.' $\rightarrow$ Sentiment: Negative"
        "Review: 'Fast shipping and great quality.' $\rightarrow$ Sentiment: Positive"
        "Review: 'The battery life is amazing!' $\rightarrow$ Sentiment: "

!!! note "Assignment.3: Inference Trade-offs"
    Describe how increasing the beam width in Beam Search affects both the quality of the output and the computational latency.

    ??? tip "Solution: Inference Trade-offs"
        Increasing beam width generally improves the quality and coherence of the output by exploring more potential sequences. However, it increases computational latency and memory usage because the model must track and score multiple candidates at each step.

## References

- Vaswani, A., et al. (2017). "Attention is All You Need".
- Hugging Face. "Tokenizers Course".
- Hu, E. J., et al. (2021). "LoRA: Low-Rank Adaptation of Large Language Models".

## Self-Evaluation

??? note "Why is positional encoding necessary in the Transformer architecture?"
    Transformers process all tokens in a sequence in parallel and do not have a built-in mechanism to understand the order of tokens. Positional encoding adds a unique vector to each token embedding, providing the model with information about the token's position in the sequence.

??? note "How does LoRA achieve parameter efficiency during fine-tuning?"
    LoRA freezes the pre-trained weight matrices and instead trains two smaller, low-rank matrices that represent the update to the weights. Because the number of trainable parameters is significantly smaller than the original matrix, it reduces VRAM and compute requirements.

??? note "What is the purpose of the KV cache in LLM inference?"
    The KV cache stores the Key and Value vectors of previously processed tokens. This prevents the model from having to re-calculate these vectors for every new token generated, significantly reducing the computational cost of the decoding phase.
