# AI Workloads in Containers

!!! info "Learning Objectives"
    - Understand the technical challenges of running GPU-accelerated workloads in containers.
    - Explain the role of the NVIDIA Container Toolkit and the `nvidia-container-runtime`.
    - Implement strategies for managing CUDA version compatibility between the host and the container.
    - Apply optimization techniques to reduce the size of AI-specific container images.
    - Execute and verify GPU-accelerated containers using industry-standard tools.

Standard containers are designed to isolate the CPU, memory, and network. However, AI and Deep Learning workloads require direct access to hardware accelerators—specifically GPUs. By default, a container cannot "see" the GPU of the host machine because the GPU device drivers are part of the host's kernel space, which containers are specifically designed to avoid accessing for security and portability reasons.

To bridge this gap, we need a mechanism that allows the container to communicate with the GPU hardware without compromising the isolation of the container itself.

!!! info "Why this matters"
    In AI development, the "CUDA mismatch" is a primary source of frustration. A researcher might develop a model using CUDA 12.1 on their workstation, but the production cluster only has drivers supporting CUDA 11.8. Without proper containerization and the correct runtime, the model will simply fail to initialize the GPU, leading to "CUDA error: no kernel image is available for execution" or similar cryptic failures.

## 1. The AI Container Stack

To understand how GPU passthrough works, it is helpful to visualize the layers of the software stack. The container does not replace the host driver; it relies on it.

```mermaid
graph TD
    subgraph Host_Machine [Host Machine - Physical]
        HW[NVIDIA GPU Hardware] --> Driver[NVIDIA Host Driver]
        Driver --> Toolkit[NVIDIA Container Toolkit]
    end

    subgraph Container_Image [Container Image - Virtual]
        Toolkit --> CUDA[CUDA Toolkit / cuDNN]
        CUDA --> Framework[AI Framework: PyTorch / TensorFlow]
        Framework --> Model[AI Model / Weights]
    end

    style Host_Machine fill:#f9f,stroke:#333,stroke-width:2px
    style Container_Image fill:#bbf,stroke:#333,stroke-width:2px
```
*Figure 1: The AI Container Stack. Notice that the Host Driver remains on the host, while the CUDA Toolkit is packaged inside the image.*

## 2. The NVIDIA Container Toolkit

The solution to GPU access in containers is the **NVIDIA Container Toolkit**. This is not a replacement for the container engine (like Docker or Podman) but an extension that allows them to interface with NVIDIA GPUs.

### How it Works: The Runtime Bridge
When you run a standard container, the engine uses a default runtime (usually `runc`). To enable GPU access, the engine must use the `nvidia-container-runtime`.

1.  **Host Driver**: The physical machine must have the NVIDIA Driver installed. This driver provides the low-level interface to the hardware.
2.  **The Toolkit**: The NVIDIA Container Toolkit installs a library that "hooks" into the container startup process.
3.  **Device Injection**: When the container starts with the `--gpus` flag, the toolkit dynamically injects the necessary GPU device files (`/dev/nvidia*`) and driver libraries from the host into the container's filesystem.

### Comparison: Standard vs. GPU Container

| Feature | Standard Container | AI/GPU Container |
| :--- | :--- | :--- |
| **Isolation** | Full OS isolation | OS isolation + GPU driver passthrough |
| **Runtime** | `runc` | `nvidia-container-runtime` |
| **Hardware Access** | CPU, RAM, Disk | CPU, RAM, Disk + NVIDIA GPU |
| **Key Dependency** | Base Image (e.g., Ubuntu) | Host NVIDIA Driver $\rightarrow$ Toolkit $\rightarrow$ CUDA Toolkit |

## 3. Practical Execution: Running your first GPU Container

To run an AI workload, you must explicitly tell the container engine to allocate GPU resources.

### The Command
Use the `--gpus` flag to grant the container access to the hardware:

```bash
# Grant access to all available GPUs
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Verification Workflow
Once the container is running, you should perform a two-step verification:

1.  **Hardware Level**: Run `nvidia-smi` inside the container. If you see the GPU table, the **NVIDIA Container Toolkit** is working.
2.  **Framework Level**: Check if your AI library (e.g., PyTorch) can actually initialize the device.

```python
# Run this inside your container
import torch
print(f"Is CUDA available? {torch.cuda.is_available()}")
print(f"Device Name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None'}")
```

## 4. Managing CUDA and cuDNN Versions

One of the most confusing aspects of AI containers is the distinction between the **Host Driver** and the **CUDA Toolkit**.

- **The Host Driver**: Installed on the physical machine. It must be a version that is compatible with the CUDA version inside the container.
- **The CUDA Toolkit**: Installed *inside* the container image. This includes the compiler (`nvcc`) and the libraries (cuBLAS, cuDNN) that the AI framework (PyTorch/TensorFlow) uses.

### The Compatibility Rule
The general rule is: **The Host Driver version must be equal to or newer than the version required by the CUDA Toolkit inside the container.** 

If you use a container built for CUDA 12.2 on a host that only has drivers for CUDA 11.0, the container will fail. However, the NVIDIA "Forward Compatibility" feature allows some newer CUDA versions to run on older drivers, provided the drivers meet a minimum baseline.

## 5. GPU Resource Allocation

In production clusters or shared research environments, you rarely grant a single container access to all GPUs.

### Specific Device Allocation
You can limit a container to specific GPUs using device IDs:
```bash
# Only grant access to GPU 0 and 1
docker run --gpus '"device=0,1"' my-ai-app
```

### MIG (Multi-Instance GPU)
For high-end cards (like the A100 or H100), NVIDIA supports **MIG**. This allows a single physical GPU to be partitioned into several smaller, hardware-isolated instances. This is critical for serving multiple small models on one expensive card without them interfering with each other's memory.

## 6. Optimizing AI Images

AI images are notoriously large—often exceeding 10GB. This leads to slow pull times and inefficient scaling.

### 1. Use Slim Base Images
Instead of starting from a full Ubuntu image, use official NVIDIA or framework-specific images:
- `nvidia/cuda:12.1.0-base-ubuntu22.04` (Very small, only runtime)
- `nvidia/cuda:12.1.0-runtime-ubuntu22.04` (Includes CUDA libraries)
- `nvidia/cuda:12.1.0-devel-ubuntu22.04` (Includes compiler; only needed for building custom C++ extensions)

!!! tip "Pro Tip: Use Framework Images"
    Building from `nvidia/cuda` is the "hard way." Most researchers should use official framework images (e.g., `pytorch/pytorch` or `tensorflow/tensorflow`). These images are pre-optimized and have the correct CUDA/cuDNN versions already matched to the framework version.

### 2. Multi-Stage Builds
Use multi-stage builds to compile dependencies in a "builder" stage and copy only the final binaries to the "production" stage.

```dockerfile
# Stage 1: Build
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Production
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY app/ /app/
WORKDIR /app
CMD ["python", "main.py"]
```

### 3. Handling Model Weights
**Never bake large model weights (e.g., Llama-3 70B) directly into the image.**
- **Volume Mounts**: Mount weights from the host filesystem at runtime.
- **S3/Object Storage**: Download weights to a shared cache volume during the first boot.

## 7. Troubleshooting & Common Errors

When working with GPU containers, most errors occur at the boundary between the host and the container.

| Symptom | Likely Cause | Fix |
| :--- | :--- | :--- |
| `nvidia-smi` returns `"Failed to initialize NVML"` | NVIDIA Container Toolkit not installed or configured. | Install the toolkit and restart the Docker daemon. |
| `"CUDA error: no kernel image is available for execution"` | Host Driver is too old for the CUDA version in the image. | Update the host NVIDIA driver to a newer version. |
| `torch.cuda.is_available()` is `False` but `nvidia-smi` works | Version mismatch between PyTorch and the CUDA Toolkit in the image. | Rebuild the image using a PyTorch version that matches your CUDA Toolkit. |
| Container crashes with `Out of Memory (OOM)` | VRAM limit exceeded on the GPU. | Use a smaller batch size or implement MIG to isolate memory. |
| `docker run` fails with `unknown flag: --gpus` | Using an outdated Docker version or a runtime that doesn't support NVIDIA. | Update Docker to v19.03+ and ensure `nvidia-container-runtime` is installed. |

---

## Self-Assessment

Test your knowledge by expanding the questions below.

??? question "What happens if I run a GPU container on a machine without the NVIDIA Container Toolkit installed?"
    The container will likely start, but it will not have access to the GPU. Commands like `nvidia-smi` inside the container will return an error, and the AI framework will fall back to the CPU, resulting in extremely slow performance.

??? question "Can I run a container with CUDA 11.8 on a host with drivers for CUDA 12.0?"
    Yes. Newer host drivers are generally backward compatible with older CUDA toolkit versions.

??? question "Why is it recommended to use the 'runtime' image instead of the 'devel' image for production?"
    The 'devel' image contains the full CUDA compiler and header files, which are large and unnecessary for running a model. The 'runtime' image contains only the libraries needed for execution, significantly reducing the image size and attack surface.

## Assignments

!!! note "Assignment 1: Driver Compatibility Audit"
    Check the NVIDIA driver version on your local machine or cluster using `nvidia-smi`. Then, go to the [NVIDIA CUDA Compatibility matrix](https://docs.nvidia.com/deploy/cuda-compatibility/) and determine the oldest and newest CUDA-based container images you can run on that driver.

!!! note "Assignment 2: Image Size Comparison"
    Build two images: one using a `devel` base image and one using a `runtime` base image. Compare their final sizes using `docker images`. Calculate the percentage of space saved by switching to the runtime image.

## References

- NVIDIA Container Toolkit Documentation: [docs.nvidia.com/datacenter/cloud-native/container-toolkit/](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- PyTorch Docker Hub: [hub.docker.com/r/pytorch/pytorch](https://hub.docker.com/r/pytorch/pytorch)
- CUDA Installation Guide: [docs.nvidia.com/cuda/cuda-installation-guide/](https://docs.nvidia.com/cuda/cuda-installation-guide/)

---

## What's Next?

Now that you know how to handle GPUs, you need to ensure your containers are secure. Head over to **Container Security & Hardening** to learn how to protect your AI workloads from vulnerabilities.
