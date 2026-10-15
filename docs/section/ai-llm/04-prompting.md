!!! info "Learning Objectives"
    - Distinguish between zero-shot and few-shot prompting and identify appropriate use cases.
    - Implement system prompts to define model personas and operational constraints.
    - Apply reasoning strategies, including Chain-of-Thought (CoT) and Tree-of-Thoughts (ToT), to improve logic and accuracy.
    - Configure model steering parameters such as temperature, logit bias, and stop sequences.
    - Enforce structured output using JSON mode for software integration.

## Overview

Prompting is the primary mechanism for steering the behavior of Large Language Models (LLMs). While base models are trained on massive datasets to predict the next token, prompting allows users to narrow the model's probability distribution toward a specific desired outcome. Moving from basic instructions to structured reasoning strategies and parameter-level steering is essential for building reliable, production-ready AI systems.

## Core Sections

### Prompt Engineering Fundamentals

Prompt engineering is the process of optimizing the input text to elicit the most accurate and useful response from an LLM.

1. Zero-shot Prompting
    Zero-shot prompting involves giving the model a task without any prior examples.
    Why this matters: It tests the model's inherent capabilities and general knowledge.

2. Few-shot Prompting
    Few-shot prompting provides a small number of examples (exemplars) within the prompt to demonstrate the desired output format or reasoning style.
    Why this matters: Examples align the model's output distribution more effectively than natural language descriptions alone.

3. System Prompts
    System prompts are high-level instructions that define the model's persona, boundaries, and global constraints. They are typically processed with higher priority than user prompts.
    Why this matters: They ensure consistent behavior across multiple turns of a conversation and reduce the need to repeat constraints in every user message.

:::tip Best Practice: Use delimiters
Use clear delimiters (e.g., `###`, `---`, or XML tags like `<context></context>`) to separate instructions from the data the model needs to process. This reduces confusion and minimizes prompt injection risks.

:::warning Pitfall: Over-prompting
Providing too many contradictory or overly verbose instructions can lead to "prompt fatigue," where the model ignores certain constraints in favor of others. Keep instructions concise and hierarchical.

### Reasoning Strategies

For complex tasks involving logic, mathematics, or multi-step planning, standard prompting often fails because the model attempts to generate the answer in a single forward pass.

1. Chain-of-Thought (CoT)
    CoT encourages the model to produce intermediate reasoning steps before arriving at the final answer. This is often triggered by the phrase "Let's think step by step."
    Why this matters: It allows the model to allocate more computation (tokens) to the reasoning process, significantly reducing hallucinations in logical tasks.

2. Tree-of-Thoughts (ToT)
    ToT extends CoT by allowing the model to explore multiple reasoning paths in parallel, evaluate them, and backtrack if a path leads to a dead end.
    Why this matters: It is critical for problems requiring look-ahead or strategic planning, where the first intuitive path may be incorrect.

3. Self-Consistency
    Self-consistency involves generating multiple CoT paths for the same problem and taking a majority vote on the final answer.
    Why this matters: It increases robustness by filtering out stochastic errors that might occur in a single reasoning chain.

### Model Steering & Structured Output

Beyond the prompt text, LLM behavior is governed by sampling parameters and output constraints.

1. Temperature
    Temperature controls the randomness of the sampling process. A temperature of 0 makes the model deterministic (greedy decoding), while higher values (e.g., 0.7 to 1.0) increase variety.
    Why this matters: Low temperature is required for factual or technical tasks; high temperature is better for creative writing.

2. Logit Bias
    Logit bias allows users to manually increase or decrease the probability of specific tokens appearing in the output.
    Why this matters: It provides a hard mechanism to force the model to use specific terminology or strictly forbid certain words.

3. Stop Sequences
    Stop sequences are strings that tell the model to immediately cease generation.
    Why this matters: They prevent the model from rambling, repeating itself, or leaking internal thought processes in a production UI.

4. JSON Mode
    Many modern LLMs support a constrained decoding mode that forces the output to be a syntactically valid JSON object.
    Why this matters: It transforms the LLM from a chatbot into a reliable component of a software pipeline, enabling automated parsing and validation.

The following Python example demonstrates a simple prompt manager that handles templates and validates JSON output.

```python
import json
import re

class PromptManager:
    """Handles prompt templating and basic output validation."""

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def format_prompt(self, template: str, **kwargs) -> str:
        """Substitutes variables into a prompt template."""
        return template.format(**kwargs)

    def validate_json(self, text: str):
        """Extracts and validates JSON from model output."""
        try:
            # Find content between curly braces to handle potential conversational filler
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("No JSON object found in output")
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}"}

# Usage example
if __name__ == "__main__":
    manager = PromptManager(system_prompt="You are a technical data extractor.")
    
    user_template = "Extract the following entities from the text: {text}. Return as JSON."
    formatted = manager.format_prompt(user_template, text="The server is hosted in us-east-1 using t3.medium.")
    
    # Mock LLM response
    mock_response = "Here is the extracted data: {\"region\": \"us-east-1\", \"instance\": \"t3.medium\"}"
    
    result = manager.validate_json(mock_response)
    print(f"Validated Output: {result}")
```

## Summary Checklist

1. [ ] I can explain the difference between zero-shot and few-shot prompting.
2. [ ] I can implement a system prompt to define a model persona and operational constraints.
3. [ ] I can apply Chain-of-Thought (CoT) to a multi-step reasoning problem.
4. [ ] I understand when to use Tree-of-Thoughts (ToT) over simple CoT.
5. [ ] I can configure temperature for deterministic vs. creative output.
6. [ ] I can enforce structured output using JSON mode for software integration.

## Assignments

!!! note "Assignment 1: Few-Shot Transition"
    Convert a zero-shot sentiment analysis prompt into a few-shot prompt. Provide three examples of varying sentiment (Positive, Negative, Neutral) and observe how the model's consistency improves.
    ??? question "Solution"
        The solution should include a prompt that lists 3-5 examples in the format:
        Input: [Text] -> Sentiment: [Label]
        Input: [New Text] -> Sentiment:

!!! note "Assignment 2: Logic via CoT"
    Create a prompt for a complex logic puzzle (e.g., a knights and knaves problem). Compare the accuracy of a direct answer prompt versus a prompt that explicitly requires "thinking step by step."
    ??? question "Solution"
        The solution should demonstrate a prompt that forces the model to list its assumptions and deductions before stating the final conclusion.

!!! note "Assignment 3: System Prompt Constraints"
    Design a system prompt for a technical API assistant that:
    1. Only answers questions about the provided API documentation.
    2. Refuses to answer general knowledge questions.
    3. Always formats code snippets in Python.
    ??? question "Solution"
        The system prompt should contain explicit instructions like "You are a strict API assistant. If the answer is not in the provided context, respond with 'I do not have information on that.' Always use Python for examples."

## References

- Vaswani, A. et al. (2017). *Attention Is All You Need*.
- Wei, J. et al. (2022). *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*.
- Yao, S. et al. (2023). *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*.

## Self-Evaluation

??? note "Conceptual Check: CoT vs ToT"
    When would you prefer Tree-of-Thoughts (ToT) over Chain-of-Thought (CoT)?
    The answer should mention tasks requiring strategic look-ahead, exploration of multiple competing hypotheses, or backtracking when a reasoning path is found to be invalid.

??? note "Parameter Check: Temperature"
    What happens to the probability distribution of the next token when temperature is set to 0?
    The answer should explain that the distribution becomes a "one-hot" vector where the token with the highest probability is always selected (greedy decoding), removing all randomness.
