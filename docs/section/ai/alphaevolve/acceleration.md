# AlphaEvolve: Hardware Acceleration with GPUs and TPUs

!!! info "Learning Objectives"
    * Verify regional support for required hardware accelerators.
    * Request and manage compute quotas for GPUs and TPUs in Vertex AI.
    * Configure `custom_job_spec` to enable hardware acceleration via Python and YAML.
    * Select appropriate container images that support CUDA or TPU runtimes.
    * Monitor resource utilization to ensure candidate models are training on accelerators.

## Overview

Neural Architecture Search (NAS) is computationally expensive, often requiring hundreds of trials to converge on an optimal model. Running these trials on standard CPUs can lead to prohibitively long training times. AlphaEvolve leverages Vertex AI CustomJobs to distribute these trials, allowing users to attach hardware accelerators like NVIDIA GPUs or Google TPUs to each worker.

By moving from CPU-based training to hardware acceleration, users can achieve a 2-10x speedup per epoch, significantly reducing the time-to-discovery for high-performing architectures. This chapter provides the technical workflow for configuring these accelerators, from quota requests to runtime verification.

## Core Sections

### Infrastructure Readiness

Before configuring AlphaEvolve, the underlying Google Cloud project must have the necessary resources available in the target region.

#### Region Support

Not all accelerators are available in every region. Selecting a region that does not support the requested hardware will result in a `ResourceUnavailable` error during trial launch.

| Accelerator | Supported Regions (as of 2026-10) |
|-------------|----------------------------------|
| NVIDIA T4 | `us-central1`, `us-west1`, `europe-west1`, `asia-north1` |
| NVIDIA A100 | `us-central1`, `us-east4`, `europe-west4`, `asia-south1` |
| Google TPU v4-64 | `us-central1`, `europe-west4`, `asia-south1` |
| Google TPU v5-p | `us-east5`, `europe-west1`, `asia-east2` |

!!! tip "Regional Expansion"
    If your required region is not listed, request a regional expansion via the Cloud Console: **Quotas → Request increase**.

#### Quota Management

Hardware accelerators are governed by strict quotas to prevent accidental overspend and ensure resource availability. AlphaEvolve may spin up several workers concurrently, meaning your quota must account for the `max_parallel_trials` setting.

| Resource | Typical Requirement | Request Path |
|----------|---------------------|--------------|
| GPU (e.g., T4) | 8-12 GPUs per region | IAM & Admin → Quotas → filter **GPU** |
| TPU cores | 8-16 v4-64 cores | IAM & Admin → Quotas → filter **TPU** |
| Vertex AI Nodes | 1+ Custom training machines | IAM & Admin → Quotas → filter **AI Platform Training** |

!!! warning "Quota Lag"
    Quota approvals typically take several business days. Request 20% more than your estimated peak usage to avoid trial failures during scaling.

### Configuring Hardware Acceleration

AlphaEvolve inherits its compute configuration from the Vertex AI `CustomJob` it creates for each trial. This configuration is defined in the `custom_job_spec` field within the `Study` definition.

#### CustomJob Specification

The `custom_job_spec` allows you to define the machine type and the specific accelerator attached to each worker. For TPUs, an additional `tpu_topology` field is required to define the core layout.

#### Python Configuration

Using the Python SDK is the recommended approach for interactive development in notebooks.

```python
from google.cloud import aiplatform

# Define the accelerator specification
# For GPU: use "type": "NVIDIA_TESLA_T4" or "NVIDIA_TESLA_A100"
# For TPU: use "type": "TPU_V4" and define a topology
accelerator_config = {
    "type": "TPU_V4",
    "topology": "2x2x2", # v4-64 provides 8 cores
    "runtime_version": "tpu-v4-base",
}

machine_type = "n1-standard-8" # Required base CPU for accelerator attachment

# Build the specification that AlphaEvolve will inject into every trial
custom_job_spec = {
    "worker_pool_specs": [
        {
            "machine_spec": {
                "machine_type": machine_type,
                "accelerator_type": accelerator_config["type"],
                "accelerator_count": accelerator_config.get("count", 1),
                **(
                    {"tpu_topology": accelerator_config["topology"]}
                    if "topology" in accelerator_config
                    else {}
                ),
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-11:latest",
            },
        }
    ]
}
```

#### YAML Configuration

For declarative pipelines, the same settings can be provided in a YAML search-space file.

```yaml
# alphaevolve_study.yaml
study:
  display_name: "flowers-cnn-gpu"
  dataset: "projects/PROJECT_ID/locations/us-central1/datasets/12345"
  search_space: {...}
  
  custom_job_spec:
    worker_pool_specs:
      - machine_spec:
          machine_type: "n1-standard-8"
          accelerator_type: "NVIDIA_TESLA_T4"
          accelerator_count: 1
        replica_count: 1
        container_spec:
          image_uri: "us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-11:latest"
```

### Runtime Environment

Hardware acceleration requires a runtime environment that includes the necessary device drivers (CUDA/cuDNN) and framework binaries.

#### Accelerator-Aware Container Images

AlphaEvolve uses the image specified in `container_spec.image_uri`. You must select an image that matches your hardware choice.

| Use-case | Public Container Image | Notes |
|----------|------------------------|-------|
| GPU TensorFlow | `us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-11:latest` | CUDA 12.x, cuDNN, TF-GPU |
| GPU PyTorch | `us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1:latest` | CUDA 12.x, torch-gpu |
| TPU TensorFlow | `us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-11:latest` | TPU runtime is injected by Vertex AI |
| TPU PyTorch XLA | `us-docker.pkg.dev/vertex-ai/training/pytorch-xla.2-1:latest` | For PyTorch-XLA workloads |

#### Framework-Specific Requirements

When using the REST API directly, the `trainingTaskInputs` must explicitly set the `scaleTier` to `CUSTOM` and provide the `acceleratorConfig` (for GPUs) or `tpuConfig` (for TPUs) within the `masterConfig` block. The Python SDK handles this translation automatically when a `custom_job_spec` is provided.

### Launching and Monitoring

#### Executing the Study

Once the `custom_job_spec` is defined, pass it to the `create` method of the `AlphaEvolveStudy` class.

```python
study = aiplatform.AlphaEvolveStudy.create(
    display_name="flowers-cnn-gpu",
    dataset=dataset,
    search_space=search_spec,
    max_trial_count=150,
    max_trial_duration=3600 * 6, # 6 hours per trial
    custom_job_spec=custom_job_spec,
)
operation = study.run()
operation.result()
```

#### Verifying Hardware Utilization

It is critical to verify that the trial is actually using the accelerator and not falling back to the CPU.

1. **Vertex AI Console**: Check the "Accelerator" column in the Training jobs view.
2. **Cloud Monitoring**: Plot the metric `accelerator.googleapis.com/nvidia_gpu/utilization` (for GPUs) or `tpu.googleapis.com/v4/cores/utilization` (for TPUs).
3. **Log Inspection**: Search for framework-level confirmation in the logs, such as `TensorFlow: Using GPU:0`.

### Cost and Budgetary Control

Accelerators significantly increase the hourly cost of a study.

| Item | Approx. Price (USD/hr) | Recommendation |
|------|-----------------------|----------------|
| NVIDIA T4 | $0.35 per GPU hour | Balanced cost/speed for most image tasks |
| NVIDIA A100 | $1.30 per GPU hour | Large models or high TFLOP requirements |
| TPU v4-64 | $5.60 per node hour | Large batch training / Transformers |

!!! tip "Budget Optimization"
    * **Set `max_trial_duration`**: Prevent runaway costs by capping the time per trial.
    * **Limit `max_parallel_trials`**: Control the peak hourly burn rate.
    * **Preemptible VMs**: Add `"preemptible": true` to `worker_pool_specs` to reduce costs if the workload is fault-tolerant.
    * **Early Stopping**: Configure AlphaEvolve to terminate trials that plateau early.

## Summary Checklist

!!! tip "Summary Checklist"
    * [ ] Target region verified for accelerator support.
    * [ ] Quotas requested and approved for GPUs/TPUs and AI Platform nodes.
    * [ ] `custom_job_spec` defined with correct `machine_type` and `accelerator_type`.
    * [ ] TPU-specific `tpu_topology` included for TPU workloads.
    * [ ] Container image selected based on framework (TF/PyTorch) and hardware (GPU/TPU).
    * [ ] `custom_job_spec` passed to `AlphaEvolveStudy.create()`.
    * [ ] `max_trial_duration` and `max_parallel_trials` configured for budget control.
    * [ ] Hardware utilization verified via Cloud Monitoring or logs.

## Assignments

!!! note "Assignment 1: Basic GPU Deployment"
    Initialize an AlphaEvolve study using an NVIDIA T4 GPU. Configure the `custom_job_spec` using the Python SDK and verify the deployment by checking the "Accelerator" column in the Vertex AI console.

    ??? question "Solution"
        1. Define `accelerator_config` with `type: "NVIDIA_TESLA_T4"` and `count: 1`.
        2. Set `machine_type` to `"n1-standard-8"`.
        3. Use the `tf-gpu` container image.
        4. Pass the resulting `custom_job_spec` to `aiplatform.AlphaEvolveStudy.create()`.

!!! note "Assignment 2: TPU Transition"
    Modify your previous study to use a Google TPU v4-64. Update the `custom_job_spec` to include the required `tpu_topology` and verify the core utilization via Cloud Monitoring.

    ??? question "Solution"
        1. Change `accelerator_type` to `"TPU_V4"`.
        2. Add `"tpu_topology": "2x2x2"`.
        3. Ensure the image is TPU-compatible (e.g., `tf-cpu` for TensorFlow).
        4. Run the study and plot the `tpu.googleapis.com/v4/cores/utilization` metric.

!!! note "Assignment 3: Custom Runtime Environment"
    Build a custom container image containing a specialized Op library required for a specific model family. Push the image to the Artifact Registry and update the `custom_job_spec` to use your custom URI.

    ??? question "Solution"
        1. Create a Dockerfile starting `FROM us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-11:latest`.
        2. Install the required libraries via `pip install`.
        3. Build and push: `docker build -t us-central1-docker.pkg.dev/PROJECT/repo/image:v1 .` followed by `docker push`.
        4. Update `container_spec.image_uri` in the `custom_job_spec` to the new URI.

## References

* [Vertex AI Custom Training Documentation](https://cloud.google.com/vertex-ai/docs/training/custom-training)
* [Google Cloud GPU Quotas](https://cloud.google.com/compute/docs/gpus/quotas)
* [Cloud TPU Documentation](https://cloud.google.com/tpu/docs)

## Self-Evaluation

??? note "Why is it necessary to specify a `machine_type` like `n1-standard-8` when attaching a GPU?"
    Accelerators cannot operate in isolation; they must be attached to a host virtual machine that provides the necessary CPU, RAM, and PCIe bus connectivity to manage the data flow to the GPU or TPU.

??? note "What is the impact of the `max_parallel_trials` setting on quota requirements?"
    Each parallel trial spawns a separate `CustomJob` worker. If `max_parallel_trials` is set to 10 and each worker requires 1 GPU, the project must have a quota of at least 10 GPUs in that region to avoid `QuotaExceeded` errors.

??? note "When should a user choose a TPU over a GPU for AlphaEvolve trials?"
    TPUs are generally superior for large-batch training and models based on the Transformer architecture due to their high-bandwidth memory and specialized matrix processing units (MXUs). GPUs are more flexible for a wider variety of custom operations and smaller batch sizes.

??? note "How does the `custom_job_spec` influence the behavior of AlphaEvolve?"
    AlphaEvolve acts as an orchestrator. By injecting the `custom_job_spec` into the `Study` definition, the orchestrator ensures that every candidate model generated by the NAS process is trained on identical hardware, ensuring that the performance metrics used for selection are consistent and fair.

??? note "What is the risk of using a CPU-only container image with a GPU-enabled `custom_job_spec`?"
    The trial will launch successfully, but the deep learning framework (TensorFlow/PyTorch) will fail to detect the CUDA libraries in the container. Consequently, the training will fall back to the CPU, resulting in significantly slower training times and misleading performance data.
