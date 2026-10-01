# Helm: Package Management for [Kubernetes](../orchestration/kubernetes.md)

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, participants will be able to:
    - Understand the purpose of a package manager in the [Kubernetes](../orchestration/kubernetes.md) ecosystem.
    - Differentiate between Helm Charts, Values, and Releases.
    - Implement advanced Go-templates to dynamically configure AI workloads.
    - Synchronize deployment configurations across environments (Dev, Staging, Prod) using a "Templated Overlay" approach.
    - Create and customize a Helm Chart that handles GPU resource limits and production-grade hardening (PriorityClasses, PDBs).
    - Evaluate the trade-offs between Helm's templating and template-less overlay tools like Kustomize.

## Overview

### Overview
As [Kubernetes](../orchestration/kubernetes.md) applications grow in complexity, managing dozens of YAML manifests becomes error-prone and tedious. Helm solves this by introducing a package management layer. 

Helm is to [Kubernetes](../orchestration/kubernetes.md) what `apt` or `yum` is to Linux: a single source of truth for "how to run" a specific application. Instead of applying individual files, Helm allows you to bundle a set of [Kubernetes](../orchestration/kubernetes.md) resources into a versioned package called a **Chart**, which can then be parameterized and deployed as a **Release**.

### Helm Architecture and Terminology
Helm v3 operates as a client-side tool that communicates directly with the [Kubernetes](../orchestration/kubernetes.md) API server.

| Term | Meaning |
|------|---------|
| **Chart** | A directory containing `Chart.yaml`, `values.yaml`, and a `templates/` folder. |
| **Release** | A specific instance of a Chart deployed to a cluster (e.g., `my-llm-prod`). |
| **Repository** | An HTTP(S) server that stores packaged charts (`index.yaml`). |
| **Values** | Configurable parameters in `values.yaml` that are rendered into templates. |
| **Hook** | A manifest executed at specific lifecycle events (`pre-install`, `post-upgrade`). |

### Why AI Infrastructure Needs Helm
AI workloads have unique requirements that make static YAML manifests impractical:

- **Hardware Heterogeneity**: A researcher might develop on a CPU-only laptop (Dev), test on a single-GPU workstation (Staging), and deploy to an 8-GPU A100 cluster (Prod).
- **Model Versioning**: Switching from Llama-3-8B to Llama-3-70B requires changing not just the image, but also the memory limits and tensor parallel size.
- **Repeatability**: A single `helm install` can provision an entire AI stack (vLLM engine, Vector DB, and FastAPI frontend) with a single command.

!!! info "Why this matters"
    In AI production, "environment drift" (where Dev and Prod differ in subtle ways) is a leading cause of CUDA Out-of-Memory (OOM) errors. Helm eliminates this by ensuring the same template is used across all environments, with only the specific resource values changing.

### Templating vs. Overlays: The "AI Overlay" Logic
In the broader [Kubernetes](../orchestration/kubernetes.md) ecosystem, there are two primary ways to handle environment-specific changes: **Templating** (Helm) and **Overlays** (Kustomize).

- **The Overlay Pattern**: Used by Kustomize, this involves a "Base" manifest and "Patches" that overwrite specific fields for Production.
- **The Templated Approach**: Used by Helm, this involves placeholders (e.g., `{{ .Values.gpuCount }}`) that are filled during deployment.

For AI workloads, the "AI Overlay" pattern typically means adding production-grade hardening—such as `PriorityClasses` to prevent LLM eviction and `PodDisruptionBudgets` to ensure availability—only when deploying to a production cluster. While Kustomize does this via patches, Helm does this via conditional logic in the templates.

## Implementation

### Basic Operations
Helm is a client-side binary. Once installed, use these common commands:

| Action | Command | Example |
|--------|---------|----------------|
| **Add Repo** | `helm repo add <name> <url>` | `helm repo add bitnami https://charts.bitnami.com/bitnami` |
| **Install** | `helm install <release> <chart>` | `helm install my-llm ./my-chart -f values-prod.yaml` |
| **Upgrade** | `helm upgrade <release> <chart>` | `helm upgrade my-llm ./my-chart --set replicaCount=3` |
| **Rollback** | `helm rollback <release> <rev>` | `helm rollback my-llm 1` |

### Creating an AI-First Chart
To create a chart, run `helm create ai-model`. The most critical files are `values.yaml` (the API) and the `templates/` directory (the logic).

#### 1. Defining the Environment API (`values.yaml`)
Instead of just defining resources, define the *intent* of the environment.

```yaml
# values.yaml
env: dev # options: dev, staging, prod

image:
  repository: vllm/vllm-openai
  tag: "v0.4.0"

# Default resources for dev
resources:
  cpu: "4"
  memory: "16Gi"
```

#### 2. Advanced Go-Templates for AI Resource Logic
Use conditionals and loops to implement the "AI Overlay" pattern directly in your templates.

**Example A: Environment-Based GPU Allocation**
Rather than manually setting the GPU count in every file, use a conditional to switch based on the `env` value.

```yaml
# templates/deployment.yaml
spec:
  template:
    spec:
      containers:
        - name: llm-engine
          resources:
            limits:
              # Logic: 8 GPUs for prod, 1 for others
              nvidia.com/gpu: {{ if eq .Values.env "prod" }}8{{ else }}1{{ end }}
              memory: {{ if eq .Values.env "prod" }}"128Gi"}}{{ else }}"32Gi"}}{{ end }}
```

!!! info "Why this matters"
    Hard-coding GPU counts leads to "Pending" pods in Dev (because the dev cluster doesn't have 8 GPUs) or under-utilized hardware in Prod. This logic ensures the workload fits the cluster it is landing on.

**Example B: Dynamic Accelerator Lists (Loops)**
If your AI stack needs to support multiple types of accelerators (e.g., NVIDIA GPUs and TPU slices), use the `range` function.

```yaml
# values.yaml
accelerators:
  - name: "nvidia.com/gpu"
    count: 1
  - name: "nvidia.com/mig-1g.10gb"
    count: 2
```

```yaml
# templates/deployment.yaml
resources:
  limits:
    {{- range .Values.accelerators }}
    {{ .name }}: {{ .count }}
    {{- end }}
```

**Example C: Production Hardening (The "AI Overlay" in Helm)**
Incorporate concepts from the [Kubernetes](../orchestration/kubernetes.md) orchestration layer—such as `PriorityClass` and `Tolerations`—only for production environments.

```yaml
# templates/deployment.yaml
spec:
  template:
    spec:
      {{- if eq .Values.env "prod" }}
      priorityClassName: system-cluster-critical
      tolerations:
      - key: "ai-gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      {{- end }}
      containers:
        - name: llm-engine
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
```

Additionally, create a `templates/pdb.yaml` that only renders in production:

```yaml
{{- if eq .Values.env "prod" }}
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ include "ai-model.fullname" . }}-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      {{- include "ai-model.selectorLabels" . | nindent 4 }}
{{- end }}
```

## Self-Evaluation

??? question "What is the 'AI Overlay' pattern and how is it implemented in Helm?"
    The "AI Overlay" pattern is the practice of adding production-specific hardening (like PriorityClasses, PDBs, and higher resource limits) to a base deployment. In Helm, this is implemented using Go-template conditionals (`{{ if eq .Values.env "prod" }}`) that inject these resources only when the environment is set to production.

??? question "When would you use a `range` loop instead of a simple value replacement in a Helm chart?"
    You use `range` when the number of resources is dynamic. For example, if a model needs a variable list of hardware accelerators (MIG profiles, different GPU types) that varies by cluster, a loop allows the `values.yaml` to define a list of accelerators without changing the template.

??? question "How does Helm prevent 'environment drift' in AI infrastructure?"
    By using a single template for all environments and separating the configuration into `values.yaml` files, Helm ensures that the structural logic of the deployment (e.g., how volumes are mounted, how probes are configured) is identical in Dev and Prod, reducing the risk of "it works in Dev but fails in Prod."

??? question "What is the benefit of using a `PriorityClass` for an LLM engine in a shared cluster?"
    LLMs are resource-heavy and critical. A `PriorityClass` ensures that if the cluster runs out of resources, the [Kubernetes](../orchestration/kubernetes.md) scheduler evicts less important pods (like a frontend or a monitoring agent) before evicting the LLM engine, maintaining API availability.

## Assignments

!!! note "Assignment.1: Environment-Aware Resource Chart"
    Create a Helm chart for a vLLM deployment. Implement a `values.yaml` with an `env` key. In the deployment template, ensure that:
    - If `env == 'prod'`, the pod requests 4 GPUs and has a `PriorityClass` of `high-priority`.
    - If `env == 'dev'`, the pod requests 1 GPU and has no `PriorityClass`.
    
    ??? tip "Solution: Environment Awareness"
        Use `{{ if eq .Values.env "prod" }}` blocks around the `nvidia.com/gpu` limit and the `priorityClassName` field in the pod spec.

!!! note "Assignment.2: Dynamic Accelerator Mapping"
    Modify your chart to support a list of accelerators in `values.yaml`. Use a `range` loop in the template so that any number of accelerators defined in the values file are automatically added to the `resources.limits` section.
    
    ??? tip "Solution: Dynamic Mapping"
        Define `accelerators` as a list of objects in `values.yaml`. In the template, use `{{- range .Values.accelerators }}` to iterate and print `{{ .name }}: {{ .count }}`.

!!! note "Assignment.3: The Production Hardening Toggle"
    Create a `pdb.yaml` template in your chart. Use a conditional so that the `PodDisruptionBudget` is only deployed if `.Values.env` is set to `prod` or `staging`. Verify this by running `helm template` with different value files.
    
    ??? tip "Solution: Hardening Toggle"
        Wrap the entire PDB manifest in `{{- if or (eq .Values.env "prod") (eq .Values.env "staging") }}` and `{{- end }}`.

## References

- Official Helm Documentation: [helm.sh/docs/](https://helm.sh/docs/)
- Chart Best Practices: [helm.sh/docs/topics/charts/](https://helm.sh/docs/topics/charts/)
- Artifact Hub: [artifacthub.io](https://artifacthub.io/)

## What's Next?

Now that you know how to package and deploy AI workloads with Helm, the final step is to automate this entire process. Head over to **[Bridging Containers and CI/CD](/section/container/security/containers-in-pipeline.md)** to see how to turn your Dockerfile and Helm charts into a production-ready pipeline.
