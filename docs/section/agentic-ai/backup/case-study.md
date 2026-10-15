# Case Study: AI-Guided Code Optimization

## Overview
This case study explores the application of an agentic AI loop to optimize compute-intensive scientific kernels. We focus on the transition from a CPU-based scientific simulation to a high-performance GPU implementation using CUDA/HIP.

## Designing the Loop

### 1. Discovery: Identifying Compute Kernels
**Why this matters**: Scientific codes are often "needle in a haystack" problems. 90% of the execution time is typically spent in 1% of the code (the kernels). Manually identifying these in million-line codebases is inefficient.

**The Agentic Approach**:
The agent is equipped with tools to run profilers (e.g., NVIDIA Nsight Systems, AMD ROCm Profiler) and parse their outputs.
- **Input**: The executable and a representative input dataset.
- **Process**: 
    1. Run profiler: `nsys profile ./simulation`
    2. Parse the `.nsys-rep` or CSV output.
    3. Identify functions with the highest "Total Time" and "GPU Utilization".
    4. Map the binary address back to the source code line using debug symbols (`-g`).
- **Output**: A list of "hot" kernels targeted for optimization.

**Real-World Scenario**: In a fluid dynamics simulation, the agent discovers that a 3D Laplacian stencil operation is consuming 75% of the runtime.

---

### 2. Optimization: Proposing GPU-Friendly Rewrites
**Why this matters**: Simply moving a loop to a GPU (`#pragma acc parallel loop`) often results in poor performance due to memory bottlenecks. True optimization requires architectural changes like memory coalescing and shared memory tiling.

**The Agentic Approach**:
The agent uses a "knowledge-retrieval + rewrite" prompt. It provides the original C++ code and the profiling data (e.g., "Memory Bound: 80%").

**Optimization Strategies used by the Agent**:
- **Memory Coalescing**: Ensuring adjacent threads access adjacent memory locations.
- **Shared Memory Tiling**: Loading a block of data into fast on-chip memory to reduce global memory trips.
- **Loop Unrolling**: Reducing branch overhead in the inner loop.
- **Vectorized Loads**: Using `float4` instead of `float` to maximize bus width.

**Code Example: The Evolution of a Kernel**

*Initial Basic Port (Naive)*:
```cpp
__global__ void stencil_naive(float* input, float* output, int size) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i > 0 && i < size - 1) {
        output[i] = (input[i-1] + input[i] + input[i+1]) / 3.0f;
    }
}
```

*Optimized Version (Tiling with Shared Memory)*:
```cpp
__global__ void stencil_optimized(float* input, float* output, int size) {
    extern __shared__ float s_data[];
    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + tid;

    // Load data into shared memory, including ghost cells
    if (i < size) s_data[tid + 1] = input[i];
    if (i == 0) s_data[0] = (i > 0) ? input[i-1] : 0;
    if (i == size - 1) s_data[blockDim.x + 1] = (i < size - 1) ? input[i+1] : 0;
    
    __syncthreads();

    if (i > 0 && i < size - 1) {
        output[i] = (s_data[tid] + s_data[tid+1] + s_data[tid+2]) / 3.0f;
    }
}
```

---

### 3. Validation: Automated Benchmark and Correctness
**Why this matters**: Optimization is useless if the results are wrong. Floating-point drift is common when changing the order of operations on GPUs.

**The Agentic Approach**:
The agent manages a validation harness.
- **Correctness**:
    - Run the CPU reference implementation $\rightarrow$ `ref_output.bin`.
    - Run the GPU optimized kernel $\rightarrow$ `gpu_output.bin`.
    - Compare using an $L^2$ norm or absolute difference with a tolerance $\epsilon$ (e.g., $10^{-6}$).
- **Performance**:
    - Measure execution time using CUDA events.
    - Calculate Speedup: $S = \frac{T_{CPU}}{T_{GPU}}$.
    - Calculate Effective Bandwidth: $\text{GB/s} = \frac{\text{Bytes Read/Written}}{\text{Time}}$.

---

## The Iteration Cycle

The agent does not optimize once; it iterates.

**The Feedback Loop**:
1. **Observation**: The agent sees that the "Optimized Version" is only 2x faster than the naive version, but the profiler shows "High L2 Cache Misses".
2. **Thought**: "The current tiling size is too small, failing to hide memory latency. I should try increasing the block size and implementing double buffering."
3. **Action**: Update the kernel code and the launch configuration (block size).
4. **Validation**: Run the benchmark $\rightarrow$ Speedup increases to 5x. Correctness check passes.

**Iteration Table**:
| Iteration | Strategy | Result | Bottleneck |
|-----------|----------|--------|------------|
| 1 | Naive Port | 2x Speedup | Global Memory Latency |
| 2 | Shared Memory | 8x Speedup | L2 Cache Misses |
| 3 | Vectorized Loads | 12x Speedup | Compute Bound (Peak) |

---

## Human-in-the-Loop (HITL)

**Why this matters**: AI can propose "hallucinated" optimizations that are technically valid but architecturally risky (e.g., using too much shared memory, causing the kernel to fail to launch on smaller GPUs).

**Strategic Checkpoints**:
1. **Architecture Approval**: After the Discovery phase, the agent presents the "Hot List" to the human. The human confirms: "Yes, the Laplacian kernel is the right target."
2. **Complexity Gate**: Before attempting a highly complex rewrite (e.g., introducing asynchronous memory copies using `cudaMemcpyAsync`), the agent asks: "I propose moving to an async pipeline. This increases code complexity. Do you approve?"
3. **Correctness Audit**: If the agent fails to converge on a correctness check for 3 iterations, it pauses and asks the human to review the floating-point precision handling.

---

## Diagrams (Placeholders)

[Diagram 1: The AI-Guided Optimization Loop]
- A circular flow: Discovery $\rightarrow$ Optimization $\rightarrow$ Validation $\rightarrow$ Analysis $\rightarrow$ (back to Optimization).
- A side-loop for HITL approval.
- Caption: Figure 1: The agentic loop for GPU kernel optimization.
- Footnote: [1] (Synthesized based on NVIDIA Nsight and LLM Agent patterns).

[Diagram 2: Memory Access Pattern: Naive vs Tiled]
- Left: Multiple threads hitting global memory (many arrows).
- Right: Threads hitting shared memory (few arrows to global, many to shared).
- Caption: Figure 2: Contrast between global memory bottlenecks and shared memory tiling.
- Footnote: [2] (Reference to CUDA Programming Guide).
