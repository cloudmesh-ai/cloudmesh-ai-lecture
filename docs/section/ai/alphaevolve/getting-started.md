# AlphaEvolve: Getting Started

!!! info "Learning Objectives"
    * Set up a basic AlphaEvolve environment using the Vertex AI SDK.
    * Define a seed algorithm and a problem specification.
    * Implement a scoring function to evaluate candidate algorithms.
    * Configure a basic search space to guide the evolutionary process.
    * Launch a first study and analyze the resulting evolution.

## Overview

While the conceptual loop of AlphaEvolve (**Define $\rightarrow$ Measure $\rightarrow$ Optimize $\rightarrow$ Apply**) describes the system's logic, implementing it requires translating these phases into Vertex AI components. 

This guide bridges the gap between understanding the theory and launching your first study. We will move from a raw piece of code (the seed) to a fully automated evolutionary process that discovers optimized versions of that code.

## Core Sections

### Environment Setup

Before interacting with AlphaEvolve, ensure your environment is authenticated and the necessary libraries are installed.

```bash
pip install -U "google-cloud-aiplatform[all]"
```

Initialize the SDK with your project details:

```python
from google.cloud import aiplatform

aiplatform.init(
    project="your-project-id",
    location="us-central1"
)
```

### Step 1: Defining the Seed (The "Define" Phase)

The "Seed" is the starting point of the evolution. It must be a piece of working code that solves the problem, even if it is inefficient. AlphaEvolve uses this seed as the first "parent" for all future mutations.

#### Example: A Simple Matrix Vector Multiplication

Suppose we want to optimize a function that multiplies a large matrix by a vector. Our seed is a basic nested loop implementation.

```python
def seed_algorithm(matrix, vector):
    """Basic matrix-vector multiplication."""
    rows = len(matrix)
    cols = len(matrix[0])
    result = [0] * rows
    for i in range(rows):
        for j in range(cols):
            result[i] += matrix[i][j] * vector[j]
    return result
```

!!! tip "Seed Quality"
    The seed should be correct but not necessarily optimized. If the seed is broken, the "Measure" phase will fail, and the evolution will have no viable parents to mutate.

### Step 2: Implementing the Scoring Function (The "Measure" Phase)

The scoring function defines the "fitness landscape." It tells AlphaEvolve which mutations are improvements and which are regressions. A professional scoring function must validate two things: **Correctness** and **Performance**.

```python
import time

def scoring_function(candidate_code, matrix, vector, ground_truth):
    # 1. Execute the candidate code
    # In practice, this is done in a secure sandbox
    try:
        start_time = time.time()
        result = exec_candidate(candidate_code, matrix, vector)
        end_time = time.time()
    except Exception:
        return 0.0 # Failure is the lowest possible score

    # 2. Validate Correctness
    # If the result is wrong, the candidate is discarded regardless of speed
    if result != ground_truth:
        return 0.0

    # 3. Measure Performance
    # We use the inverse of the execution time as the score
    duration = end_time - start_time
    score = 1.0 / duration
    return score
```

!!! warning "The Correctness Trap"
    Never score based on speed alone. An algorithm that returns a constant zero instantly is "fast" but useless. Always verify correctness before measuring performance.

### Step 3: Defining the Search Space (The "Optimize" Phase)

The search space provides the "guardrails" for the LLM (Gemini). Instead of letting the model rewrite the code randomly, you specify the dimensions it should explore.

```python
search_spec = {
    "model_family": ["python-optimized"], 
    "optimization_goals": ["latency", "memory_bandwidth"],
    "constraints": {
        "allow_external_libraries": ["numpy"],
        "max_code_length": 1000
    },
    "mutation_strategy": "diversified"
}
```

By specifying `numpy` as an allowed library, you guide AlphaEvolve to explore vectorized implementations, which are typically much faster than the nested loops in our seed.

### Step 4: Launching the Study (The "Apply" Phase)

Now, we combine the seed, the scoring function, and the search space into an `AlphaEvolveStudy`.

```python
study = aiplatform.AlphaEvolveStudy.create(
    display_name="matrix-mult-evolution",
    seed_code=seed_algorithm,
    scoring_function=scoring_function,
    search_space=search_spec,
    max_trial_count=100,
    max_trial_duration=3600, # 1 hour per trial
)

# Start the evolutionary loop
operation = study.run()
operation.result() 

# Retrieve the best discovered algorithm
best_model = study.get_best_candidate()
print(f"Optimized Code:\n{best_model.code}")
print(f"Improvement: {best_model.improvement_factor}x")
```

## Summary Checklist

!!! tip "Summary Checklist"
    * [ ] Vertex AI SDK initialized and authenticated.
    * [ ] Seed algorithm defined and verified as functionally correct.
    * [ ] Scoring function implemented with both correctness and performance checks.
    * [ ] Search space configured with appropriate constraints and goals.
    * [ ] `AlphaEvolveStudy` created and executed.
    * [ ] Best candidate retrieved and verified against the ground truth.

## Assignments

!!! note "Assignment 1: Basic Evolution"
    Using the matrix-vector multiplication example, launch a study with a small budget (10 trials). Record the performance of the seed vs. the best candidate.

    ??? question "Solution"
        Follow the "Launching the Study" code block. Use a small matrix (e.g., 100x100) to ensure trials finish quickly. Compare the `duration` of the seed with the `duration` of the `best_model`.

!!! note "Assignment 2: Constrained Optimization"
    Modify the `search_spec` to prohibit the use of `numpy`. Observe how the evolution changes when the model is forced to optimize raw Python loops instead of using vectorized libraries.

    ??? question "Solution"
        Change `allow_external_libraries` to an empty list `[]`. The resulting best candidate will likely use techniques like list comprehensions or `itertools` rather than NumPy arrays.

!!! note "Assignment 3: Complex Scoring"
    Implement a scoring function that rewards both speed and memory efficiency. The score should be a weighted average of `1/execution_time` and `1/peak_memory_usage`.

    ??? question "Solution"
        Use a memory profiler (like `tracemalloc`) inside the scoring function. Calculate `score = (w1 * (1/time)) + (w2 * (1/memory))`.

## References

* [Vertex AI SDK Reference](https://cloud.google.com/python/docs/reference/aiplatform)
* [AlphaEvolve API Documentation](https://cloud.google.com/vertex-ai/docs/alphaevolve)

## Self-Evaluation

??? note "What happens if the scoring function is too lenient?"
    If the scoring function ignores correctness or allows "cheating" (e.g., returning a hardcoded answer for a specific test case), AlphaEvolve will converge on a "degenerate" solution that appears high-performing but is functionally broken.

??? note "Why is a 'seed' necessary if the LLM can write code from scratch?"
    A seed provides a known-correct baseline. It ensures the evolution starts from a point of functional viability, which significantly reduces the number of trials wasted on syntactically incorrect or fundamentally broken code.

??? note "How does the 'Search Space' prevent the LLM from hallucinating invalid Python?"
    The search space defines constraints and target families. While the LLM generates the code, AlphaEvolve's "Measure" phase acts as a filter; any hallucinated or invalid code will fail to execute and receive a score of 0.0, preventing it from becoming a parent in the next generation.

??? note "In what scenario would a low `max_trial_count` be acceptable?"
    When the problem is simple or the search space is very narrow, the optimal solution might be found quickly. However, for complex algorithmic discovery, a higher count is needed to explore a wider variety of mutations.

??? note "What is the relationship between the `scoring_function` and the `best_model`?"
    The `best_model` is simply the candidate that achieved the highest numerical value from the `scoring_function`. The quality of the "best" model is entirely dependent on how accurately the scoring function reflects the real-world goal.
