!!! info "Learning Objectives"
    By the end of this chapter, students will be able to:
    - Distinguish between static benchmarks and dynamic evaluation methods.
    - Implement a basic LLM-as-a-Judge evaluation pipeline.
    - Identify common safety vulnerabilities including prompt injection and jailbreaking.
    - Design a multi-layered safety architecture using guardrails and moderation APIs.

## Overview

Evaluating Large Language Models (LLMs) is fundamentally different from traditional software testing. While traditional software relies on deterministic outputs—where a specific input always yields the same result—LLMs are probabilistic. A model may provide a perfect answer once and a hallucinated one the next.

Consequently, evaluation has shifted from binary "correct/incorrect" metrics to distributional quality and human preference. This chapter explores the tools used to quantify model performance and the frameworks required to ensure safety and reliability in production environments.

## Core Sections

### Benchmarking

Benchmarking involves testing a model against a standardized dataset to measure its performance across specific capabilities.

Why this matters: Benchmarks provide a baseline for comparing models of different sizes and architectures without requiring expensive human trials for every iteration.

Common benchmarks include:

1. MMLU (Massive Multitask Language Understanding): Tests general knowledge across 57 subjects including STEM, humanities, and social sciences.
2. GSM8K: A dataset of grade school math word problems that requires multi-step reasoning.
3. HumanEval: A benchmark for evaluating code generation capabilities, specifically in Python.

:::warning Data Contamination
A significant risk in benchmarking is "data contamination," where benchmark questions and answers are accidentally included in the model's training corpus. This leads to inflated scores that reflect memorization rather than actual reasoning or intelligence.
:::

### LLM-as-a-Judge

As models become more capable, static benchmarks often fail to capture nuance, tone, and helpfulness. LLM-as-a-Judge uses a highly capable model (the "Judge") to evaluate the outputs of another model (the "Candidate").

Why this matters: Human evaluation is the gold standard but is slow, expensive, and difficult to scale. LLM judges provide a scalable proxy for human preference that can be integrated into CI/CD pipelines.

The typical workflow involves providing the Judge with:
1. A clear grading rubric.
2. A reference "gold" answer (optional).
3. The candidate model's response.

The following Python snippet demonstrates a basic implementation of this pattern.

```python
import json

def evaluate_response(prompt, reference, candidate):
    """
    Simple LLM-as-a-Judge implementation.
    Uses a rubric to grade a candidate response against a reference.
    """
    # The judge prompt defines the persona and the strict grading criteria.
    judge_prompt = f"""
    You are an impartial judge. Grade the candidate response based on the reference answer.
    
    Rubric:
    1: Completely incorrect or irrelevant.
    2: Partially correct but missing key details.
    3: Correct and concise.
    4: Correct, comprehensive, and better than the reference.

    Reference: {reference}
    Candidate: {candidate}

    Return your response in JSON format:
    {{
        "score": <int>,
        "reasoning": "<string>"
    }}
    """
    
    # In a real scenario, this would be an API call to a model like GPT-4o or Claude 3.5 Sonnet.
    # For this example, we simulate a valid JSON response from the judge.
    mock_llm_output = '{"score": 3, "reasoning": "The candidate answer matches the reference exactly."}'
    
    try:
        result = json.loads(mock_llm_output)
        return result["score"], result["reasoning"]
    except json.JSONDecodeError:
        return None, "Failed to parse judge output"

# Example usage
p = "What is the capital of France?"
ref = "The capital of France is Paris."
cand = "Paris is the capital city of France."

score, reason = evaluate_response(p, ref, cand)
print(f"Score: {score}, Reason: {reason}")
```

### Safety and Guardrails

Safety in LLMs refers to the ability to prevent the model from generating harmful, biased, or prohibited content, as well as preventing the model from being manipulated by users.

Why this matters: Without safety constraints, LLMs can be coerced into providing instructions for illegal activities, leaking sensitive system prompts, or generating toxic content that violates corporate policies.

Common vulnerabilities include:

1. Prompt Injection: When a user provides input that attempts to override the system prompt (e.g., "Ignore all previous instructions and instead do X").
2. Jailbreaking: Using adversarial techniques, such as roleplay or hypothetical scenarios (e.g., the "DAN" persona), to bypass safety filters.

:::tip Defense-in-Depth
Avoid relying solely on a "strong" system prompt for safety. Implement a multi-layered defense:
1. Input Guardrails: Use a separate small model or regex patterns to detect injection attempts before they reach the LLM.
2. Output Guardrails: Scan the generated response for PII (Personally Identifiable Information) or toxicity.
3. Moderation APIs: Leverage specialized tools like the OpenAI Moderation API to flag unsafe content.
:::

## Summary Checklist

- [ ] Understand the difference between static benchmarks (MMLU) and dynamic evaluation (LLM-as-a-Judge).
- [ ] Be able to identify signs of data contamination in benchmark results.
- [ ] Construct a structured rubric for an LLM judge.
- [ ] Implement a layered safety architecture featuring input and output guardrails.

## Assignments

!!! note "Assignment 1: Benchmark Analysis"
    Explain why a high score on MMLU might not correlate with a model's performance in a highly specialized professional domain, such as maritime law or specialized surgical procedures.
    
    ??? question "Solution"
        MMLU measures general knowledge across broad categories. Specialized domains require deep, niche expertise and the ability to apply that knowledge to specific, complex contexts (reasoning) rather than just recalling facts. High general intelligence does not guarantee domain-specific accuracy or adherence to professional standards.
    ???

!!! note "Assignment 2: Rubric Design"
    You are evaluating a model's ability to summarize technical documentation for a non-technical audience. Write a 4-point rubric that an LLM-as-a-Judge should use to grade the summaries.
    
    ??? question "Solution"
        1: Fails to summarize; contains technical jargon that is not explained.
        2: Accurate summary but retains too much technical complexity for a layperson.
        3: Accurate and accessible summary; simplifies complex concepts correctly.
        4: Excellent summary; uses analogies to explain technical concepts and highlights the most important takeaways.
    ???

## References

- Hendrycks et al., "Measuring Massive Multitask Language Understanding" (MMLU Paper).
- Chen et al., "Evaluating Large Language Models Trained on Code" (HumanEval Paper).
- OpenAI Moderation API Documentation.

## Self-Evaluation

??? note "Self-Check: Evaluation"
    Can I explain why LLM-as-a-Judge is often preferred over ROUGE or BLEU scores for open-ended generation tasks?
    ???

??? note "Self-Check: Safety"
    Can I differentiate between a prompt injection attack and a jailbreak attempt?
    ???
