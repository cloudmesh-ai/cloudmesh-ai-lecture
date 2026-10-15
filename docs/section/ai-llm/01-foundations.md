# LLM Foundations: The Transformer Era

!!! info "Learning Objectives"
    By the end of this chapter, students will be able to:
    - Contrast the architectural differences between Encoder-only, Decoder-only, and Encoder-Decoder Transformers.
    - Calculate a basic self-attention score using the Query-Key-Value (QKV) mechanism.
    - Implement a simple Byte Pair Encoding (BPE) merge logic.
    - Explain how positional encodings resolve the lack of sequence order in parallel processing.
    - Identify the causes of the "Lost in the Middle" phenomenon in long-context LLMs.

## Overview

The current era of artificial intelligence is defined by the transition from sequential processing to parallel attention. Previous sequence models, such as Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTMs), processed text token by token. This sequential nature created a computational bottleneck and led to the "vanishing gradient" problem, where the model would "forget" information from the beginning of a long sentence by the time it reached the end.

The Transformer architecture, introduced in the 2017 paper "Attention Is All You Need," solved these issues by replacing recursion with a mechanism called **Self-Attention**. This allows the model to process all tokens in a sequence simultaneously, weighing the importance of every token relative to every other token regardless of their distance.

In this chapter, we examine the internal mechanics of the Transformer, the mathematics of attention, and the process of converting raw text into the high-dimensional vectors that LLMs use to reason.

## Core Sections

### The Transformer Architecture

Modern LLMs are not a monolithic design but a family of architectures based on the Transformer block. Depending on the intended task, the architecture is stripped down or combined.

#### Architectural Flavors

1. **Encoder-only (e.g., BERT)**: These models process the entire input sequence simultaneously to create a rich representation of every token. They are used for understanding tasks like sentiment analysis or named entity recognition.
2. **Decoder-only (e.g., GPT-4, Llama, Claude)**: These models are designed for generation. They use "masked self-attention," meaning a token can only attend to tokens that came before it. This prevents the model from "cheating" by looking at the next word during training.
3. **Encoder-Decoder (e.g., T5)**: These combine both. The encoder creates a context vector of the input, and the decoder generates a sequence based on that vector. This is the standard for high-quality machine translation.

Why this matters: Choosing the right architecture affects both latency and capability. A decoder-only model is optimized for fluid text generation, whereas an encoder-only model is significantly more efficient for analyzing existing text.

#### The Attention Mechanism: Q, K, and V

Self-attention mimics human cognitive focus. When you read the word "bank" in a sentence, you look at surrounding words to determine if it refers to a river bank or a financial institution. The Transformer does this using three learned vectors: **Query (Q)**, **Key (K)**, and **Value (V)**.

- **Query**: Represents the current token's search criteria (e.g., "I am a verb, I am looking for my subject").
- **Key**: Represents the identity of other tokens (e.g., "I am a noun, I might be a subject").
- **Value**: The actual information contained in the token.

The model calculates the dot product of the Query of token A and the Key of token B. A high score indicates a strong relationship.

```python
import numpy as np

def simple_attention(query, keys, values):
    # Calculate dot product of Q and K_transpose
    # scores shape: (1, seq_len)
    scores = np.dot(query, keys.T)
    
    # Scale by sqrt of dimension to prevent gradient explosion
    scaled_scores = scores / np.sqrt(keys.shape[1])
    
    # Softmax to get probabilities (weights)
    weights = np.exp(scaled_scores) / np.sum(np.exp(scaled_scores))
    
    # Weighted sum of values
    output = np.dot(weights, values)
    return output

# Example: 1 query, 3 keys/values with dim 4
q = np.array([[1, 0, 1, 0]])
k = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [1, 1, 0, 0]])
v = np.array([[10, 0], [0, 20], [5, 5]])

print(f"Attention Output: {simple_attention(q, k, v)}")
```

#### Multi-Head Attention (MHA) and Positional Encoding

Single-head attention can only capture one type of relationship at a time. **Multi-Head Attention** runs multiple attention processes in parallel, allowing the model to simultaneously track grammatical structure, semantic meaning, and entity relationships.

Because Transformers process all tokens at once, they lack an inherent sense of order. **Positional Encoding** solves this by adding a unique vector to each token embedding based on its position. These encodings use sine and cosine functions, allowing the model to learn relative distances between tokens.

:::tip
**Computational Complexity**
The self-attention mechanism has a computational complexity of $O(n^2)$, where $n$ is the sequence length. This quadratic growth is why increasing the context window from 8k to 128k tokens requires massive advances in memory management and hardware.
:::

### Tokenization and Embeddings

LLMs do not read text; they process integers. The process of converting text to integers is tokenization.

#### Byte Pair Encoding (BPE)

To avoid the pitfalls of word-level tokenization (too many words) and character-level tokenization (too many tokens), LLMs use **Byte Pair Encoding (BPE)**. BPE starts with individual characters and iteratively merges the most frequent adjacent pairs into new tokens.

Example: If "t" and "h" appear together most often, they become "th". If "th" and "e" appear together, they become "the".

```python
def simple_bpe_merge(text, pair):
    # Replace a pair of tokens with a merged version
    # Example: pair = ('t', 'h'), text = ['t', 'h', 'e'] -> ['th', 'e']
    new_text = []
    i = 0
    while i < len(text):
        if i < len(text) - 1 and (text[i], text[i+1]) == pair:
            new_text.append(pair[0] + pair[1])
            i += 2
        else:
            new_text.append(text[i])
            i += 1
    return new_text

tokens = ['t', 'h', 'e', ' ', 'c', 'a', 't']
merged = simple_bpe_merge(tokens, ('t', 'h'))
print(f"Merged Tokens: {merged}")
```

#### The Embedding Space

After tokenization, each token ID is mapped to a high-dimensional vector called an **Embedding**. These vectors are learned during training such that tokens with similar semantic meanings are placed closer together in the vector space.

Why this matters: This allows the model to generalize. If the model learns that "The dog is happy" is a positive sentence, it can infer that "The puppy is joyful" is also positive because "dog" is close to "puppy" and "happy" is close to "joyful" in the embedding space.

:::warning
**The "Lost in the Middle" Problem**
As context windows expand, LLMs exhibit a U-shaped performance curve. They are highly effective at recalling information from the very beginning (primacy effect) and the very end (recency effect) of a prompt, but accuracy drops significantly for information located in the middle of the context.
:::

## Summary Checklist

- [ ] I can explain why a Decoder-only architecture is preferred for generative LLMs.
- [ ] I can describe the role of Query, Key, and Value vectors in self-attention.
- [ ] I can explain the difference between a word-level and a BPE tokenizer.
- [ ] I understand why positional encoding is necessary for parallel processing.
- [ ] I can identify the computational bottleneck associated with the $O(n^2)$ complexity of attention.

## Assignments

!!! note "Manual Attention Calculation"
    Given a Query vector $Q = [1, 0]$ and two Key vectors $K_1 = [1, 0]$ and $K_2 = [0, 1]$, calculate the attention weights. Assume no scaling factor is used.
    
    ??? question "Solution"
        1. Dot product $Q \cdot K_1 = (1*1) + (0*0) = 1$
        2. Dot product $Q \cdot K_2 = (1*0) + (0*1) = 0$
        3. Softmax: $\exp(1) / (\exp(1) + \exp(0)) \approx 2.718 / (2.718 + 1) \approx 0.73$
        4. Weights: Token 1 = 73%, Token 2 = 27%.

!!! note "BPE Merge Simulation"
    Starting with the sequence `['a', 'b', 'a', 'b', 'a', 'c']`, perform two merge steps. In step 1, merge `('a', 'b')`. In step 2, merge `('ab', 'a')`. Show the resulting sequence.
    
    ??? question "Solution"
        Step 1: `['ab', 'ab', 'a', 'c']`
        Step 2: `['aba', 'b', 'a', 'c']` (Note: only the first occurrence is merged if iterating linearly).

## References

- Vaswani, A., et al. *Attention Is All You Need*.
- Radford, A., et al. *Language Models are Unsupervised Multitask Learners* (GPT-2).
- Devlin, J., et al. *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*.

## Self-Evaluation

??? note "Why do we divide the dot product of Q and K by the square root of the dimension?"
    As the dimensionality $d_k$ increases, the dot product can grow very large in magnitude. This pushes the softmax function into regions where the gradient is extremely small (vanishing gradients), making the model difficult to train. Scaling stabilizes the gradients.

??? note "What is the difference between a token and a word?"
    A word is a linguistic unit; a token is a computational unit. A single word can be split into multiple tokens (e.g., "unhappy" $\rightarrow$ "un", "happy") or multiple words can be merged into one token if they are frequent enough.

??? note "Why can't a Decoder-only model see future tokens during training?"
    If it could, the model would simply learn to copy the next token from the input rather than learning to predict it based on context. This is prevented by a "causal mask" that sets the attention scores of future tokens to $-\infty$.

??? note "How does Multi-Head Attention improve upon Single-Head Attention?"
    It allows the model to attend to different types of relationships in parallel. For example, one head can track the subject-verb agreement while another tracks the coreference of a pronoun.

??? note "What is the primary advantage of BPE over character-level tokenization?"
    BPE reduces the sequence length the model must process, which reduces computational cost and allows the model to capture more semantic meaning per token.
