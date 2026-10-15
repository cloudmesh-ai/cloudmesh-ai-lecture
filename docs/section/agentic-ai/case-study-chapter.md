# Case Study: AI-Guided Code Optimization

!!! info "Learning Objectives"
    - Design an agentic loop for discovering and optimizing scientific compute kernels.
    - Apply GPU optimization techniques such as memory coalescing and shared memory tiling.
    - Build an automated validation harness for correctness and performance.
    - Implement Human-in-the-Loop (HITL) checkpoints for architectural sanity.

## Overview

Scientific computing often involves processing massive datasets through complex mathematical operations. Traditionally, optimizing these "compute kernels" for GPUs required deep expertise in hardware architecture and manual profiling. 

This chapter examines an agentic AI approach to this problem. By combining Large Language Models (LLMs) with tool-use (profilers, compilers, and benchmarks), we can automate the "Discovery -> Optimization -> Validation" cycle, reducing the time to achieve peak hardware performance while maintaining mathematical correctness.

## Designing the Optimization Loop

The core of AI-guided optimization is a closed-loop system where the AI acts as the orchestrator, using external tools to observe the code's behavior and refine its implementation.

### Discovery: Identifying Compute Kernels

**Why this matters**: In a codebase of millions of lines, only a small fraction of the code—the "hot" kernels—contribute to the majority of the execution time. Optimizing the wrong function is a waste of resources.

The agent is equipped with a toolset to run system-level profilers and analyze the resulting data.

1. **Execution**: The agent runs the simulation under a profiler, such as NVIDIA Nsight Systems or AMD ROCm Profiler.

   ```bash
   nsys profile --stats=true ./simulation_binary
   ```

2. **Analysis**: The agent parses the profiling report to find functions with the highest "Total Time" and "GPU Utilization".

3. **Mapping**: Using debug symbols (`-g`), the agent maps the binary address of the hot spot back to the specific line of source code.

**Real-World Scenario**: In a 3D fluid dynamics simulation, the agent discovers that a Laplacian stencil operation—which calculates the average of neighboring grid cells—is consuming 75% of the total runtime, making it the primary target for optimization.

!!! tip "Profiler Hint"
    When using Nsight, focus on the "GPU Kernel Summary" to identify kernels with low occupancy or high memory stall cycles.

### Optimization: GPU-Friendly Rewrites

**Why this matters**: A naive port of CPU code to a GPU often results in poor performance because GPUs rely on massive parallelism and specific memory access patterns to hide latency.

The agent uses a "knowledge-retrieval + rewrite" prompt. It analyzes the current performance bottleneck (e.g., "Global Memory Bound") and proposes a specific architectural change.

**Key Optimization Strategies**:

- **Memory Coalescing**: Ensuring that threads in a warp access adjacent memory locations in a single transaction.
- **Shared Memory Tiling**: Moving frequently accessed data from slow global memory to fast, on-chip shared memory.
- **Vectorized Loads**: Using wider data types (e.g., `float4` instead of `float`) to saturate the memory bus.

**Code Example: The Evolution of a Stencil Kernel**

The following example shows the transition from a naive GPU port to an optimized tiled implementation.

```cpp
// Naive Implementation: Each thread reads from global memory multiple times
__global__ void stencil_naive(float* input, float* output, int size) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (i > 0 && i < size - 1) {
        // Every thread performs 3 global memory reads
        output[i] = (input[i-1] + input[i] + input[i+1]) / 3.0f;
    }
}
```

```cpp
// Optimized Implementation: Using Shared Memory Tiling
__global__ void stencil_optimized(float* input, float* output, int size) {
    // Dynamic shared memory allocation
    extern __shared__ float s_data[];
    
    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + tid;

    // Load data into shared memory, including "ghost cells" for boundaries
    if (i < size) {
        s_data[tid + 1] = input[i];
    }
    
    // Handle boundary conditions for the tile
    if (tid == 0) {
        s_data[0] = (i > 0) ? input[i-1] : 0.0f;
    }
    if (tid == blockDim.x - 1) {
        s_data[blockDim.x + 1] = (i < size - 1) ? input[i+1] : 0.0f;
    }
    
    // Synchronize to ensure all threads have finished loading
    __syncthreads();

    if (i > 0 && i < size - 1) {
        // Read from fast shared memory instead of global memory
        output[i] = (s_data[tid] + s_data[tid+1] + s_data[tid+2]) / 3.0f;
    }
}
```

!!! warning "Synchronization Pitfall"
    Always call `__syncthreads()` after loading data into shared memory. Failing to do so causes "race conditions" where some threads read data before others have finished writing it.

### Validation: Automated Benchmarking

**Why this matters**: GPU optimizations often involve changing the order of floating-point operations, which can introduce precision drift. An optimization is only successful if it is both fast and correct.

The agent manages an automated validation harness that performs two primary checks:

1. **Correctness Check**:
    - The agent runs a high-precision CPU reference implementation to generate a "gold standard" output file.
    - It then runs the GPU kernel and compares the results using an $L^2$ norm.
    - If the difference exceeds a tolerance $\epsilon$ (e.g., $10^{-6}$), the iteration is marked as "Failed".

2. **Performance Check**:
    - The agent uses CUDA events to measure the exact execution time of the kernel.
    - It calculates the speedup relative to the CPU: $S = \frac{T_{CPU}}{T_{GPU}}$.

## The Iteration Cycle

AI-guided optimization is an iterative process of observation and refinement. The agent follows a feedback loop:

1. **Observation**: The agent observes that the optimized kernel has a 5x speedup, but the profiler still reports "High L2 Cache Misses".
2. **Thought**: "The current tile size is too small to effectively hide memory latency. I should increase the block size and implement double buffering to overlap computation with memory transfer."
3. **Action**: The agent updates the kernel code and the launch configuration.
4. **Validation**: The benchmark is re-run, and the speedup increases to 12x.

**Optimization Progress Table**

| Iteration | Strategy | Speedup | Bottleneck | Result |
|-----------|----------|---------|------------|--------|
| 1 | Naive Port | 2x | Global Memory Latency | Correct |
| 2 | Shared Memory | 8x | L2 Cache Misses | Correct |
| 3 | Vectorized Loads | 12x | Compute Bound | Correct |

## Human-in-the-Loop (HITL) Strategic Gates

**Why this matters**: LLMs can propose "hallucinations" that are syntactically correct but architecturally invalid—such as requesting more shared memory than is available on a specific GPU model, causing the kernel to fail to launch.

To mitigate this, the agent uses strategic checkpoints for human approval:

- **Target Approval**: After the Discovery phase, the agent presents the "Hot List" of kernels. The human confirms the priority of targets to avoid wasting compute on low-impact functions.
- **Complexity Gate**: Before implementing high-risk patterns (e.g., asynchronous memory copies using `cudaMemcpyAsync`), the agent asks: "I propose moving to an async pipeline. This increases code complexity significantly. Do you approve?"
- **Convergence Audit**: If the agent fails the correctness check for three consecutive iterations, it pauses and requests a human review of the floating-point precision handling.

!!! tip "HITL Best Practice"
    Use HITL gates not just for errors, but for architectural alignment. A human can steer the agent toward a specific design pattern (e.g., "prefer readability over a 2% speed increase").

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] Identify hot kernels using system profilers (Nsight/ROCm).
    - [ ] Map binary hot-spots back to source code using debug symbols.
    - [ ] Implement GPU-specific patterns: Memory coalescing, Shared Memory Tiling, and Vectorized Loads.
    - [ ] Validate correctness against a CPU reference using a tolerance $\epsilon$.
    - [ ] Iterate based on profiler feedback (e.g., L2 cache misses $\rightarrow$ larger tiles).
    - [ ] Use HITL gates for architecture approval and complexity management.

## Assignments

!!! note "Exercise 1: Profiling Analysis (Basic)"
    Given a profiling report showing a kernel with 90% "Global Memory Load Efficiency" but 80% "Memory Stall Cycles", explain why the kernel is still slow.
    
    ??? question "Solution"
        The kernel is memory-bound. High load efficiency means the memory transactions are coalesced, but the high stall cycles indicate that the GPU is spending most of its time waiting for data to arrive from global memory. The solution is to use shared memory tiling to reduce the number of global memory trips.

!!! note "Exercise 2: Tiling Implementation (Intermediate)"
    Rewrite a simple 1D array summation kernel to use shared memory for partial reductions within a block.
    
    ??? question "Solution"
        The solution should involve:
        1. Allocating a shared memory array of size `blockDim.x`.
        2. Each thread loading one element from global memory to shared memory.
        3. Using `__syncthreads()`.
        4. Performing a tree-based reduction in shared memory.
        5. Having the first thread of each block write the partial sum to global memory.

!!! note "Exercise 3: Loop Design (Advanced)"
    Design a prompt for an AI agent that instructs it to optimize a kernel for "Compute Bound" scenarios specifically. What metrics should the agent look for in the profiler to confirm it is actually compute-bound?
    
    ??? question "Solution"
        The prompt should instruct the agent to focus on instruction-level parallelism (ILP) and loop unrolling. The agent should monitor "Arithmetic Intensity" (FLOPs per byte) and "SM Occupancy". A compute-bound kernel will show high SM utilization but low memory stall cycles.

## References

- NVIDIA CUDA C++ Programming Guide
- AMD ROCm Profiler Documentation
- "Programming Massively Parallel Processors" by David Kirk and Wen-mei Hwu

## Self-Evaluation

??? note "How does an agentic loop differ from a standard LLM code generation task?"
    An agentic loop uses tools (profilers, compilers) to observe the real-world execution of that code and uses the results to iteratively refine the implementation, whereas a standard LLM generates code based on a prompt without runtime feedback.

??? note "What is the primary purpose of 'ghost cells' in shared memory tiling?"
    Ghost cells are the boundary elements of a tile that are required by the stencil operation but reside outside the current tile's main data range. They prevent boundary threads from accessing invalid memory.

??? note "Why is an L2 norm used for validation instead of a bit-for-bit comparison?"
    GPUs often change the order of floating-point additions (which are not associative). This leads to small differences in the least significant bits. An L2 norm allows for a controlled tolerance ($\epsilon$) to account for this drift.

??? note "When should a Human-in-the-Loop (HITL) gate be triggered during the optimization process?"
    HITL should be triggered during target selection (Discovery), when proposing high-complexity architectural changes, or when the agent fails to converge on a correctness check.

??? note "What is the relationship between memory coalescing and global memory bandwidth?"
    Memory coalescing ensures that multiple memory requests from a warp are combined into a single transaction. This maximizes the effective bandwidth of the memory bus, reducing the number of cycles the GPU spends waiting for data.
