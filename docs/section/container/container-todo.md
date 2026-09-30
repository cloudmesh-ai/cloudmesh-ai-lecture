# Containerization Chapter Improvements TODO

This document tracks suggested enhancements to the Containerization section to ensure it matches the pedagogical depth, stylistic consistency, and "AI-first" focus of the DevOps chapter.

## 🛠️ General Improvements (All Files)

- [ ] **Standardized Structure**: Verify that every file follows the sequence: `Learning Objectives` $\rightarrow$ `Introduction/Concepts` $\rightarrow$ `Implementation/Examples` $\rightarrow$ `Self-Assessment` $\rightarrow$ `Assignments` $\rightarrow$ `What's Next?`.
- [ ] **Cross-Linking**: Implement a "web" of links between files (e.g., linking from `docker.md` to `container-security.md` when mentioning root users).
- [ ] **Image Audit**: Verify all images have descriptive captions and are correctly linked. Add diagrams where complex flows are described (e.g., CNI/CSI flows in storage).
- [ ] **Consistent Callouts**: Ensure every file uses the `!!! info "Why this matters"` callout to explain the real-world relevance of the technical concepts, especially for AI/Data Science.
- [ ] **Consistency in Self-Assessment**: Ensure all self-assessments use the `??? question` format consistently.

---

## 📄 Per-File Improvements

### Foundations
- [x] **`containers.md`**
    - [x] Expand technical depth on Namespaces (`pid`, `net`, `mnt`) and Cgroups.
    - [ ] Add a "History of Containerization" case study (Chroot $\rightarrow$ LXC $\rightarrow$ Docker).
    - [x] Upgrade assignments from "Identify" to "Analyze/Compare" level.
- [x] **`docker.md`**
    - [x] Add "Docker in Production" vs "Docker for Dev" distinction (Compose vs K8s).
    - [x] Create a "Bad vs. Good" AI Dockerfile comparison (optimization for large weights).
    - [x] Add a "Production Hardening" assignment (rootless, distroless, scanning).
- [x] **`podman.md`**
    - [x] Add a "Docker $\rightarrow$ Podman Migration" checklist.
    - [x] Expand on `podman generate kube` for K8s alignment.
    - [x] Implement a "Sidecar Pattern" assignment for AI monitoring.
- [x] **`apptainer.md`**
    - [x] Add real SLURM/PBS script examples for supercomputing clusters.
    - [ ] Create a comparison matrix: Apptainer vs Docker vs Podman (HPC focus).

### Security
- [ ] **`container-security.md`**
    - [ ] Add a "Real-world Container Breakout" case study (CVE analysis).
    - [ ] Introduce runtime security tools (**Falco**, **Tetragon**).
    - [ ] Add a section on "Prompt Injection" as a trigger for container-level attacks.
    - [ ] Create a "Security Audit" assignment (finding bugs in a provided "bad" Dockerfile).
- [ ] **`containers-in-pipeline.md`**
    - [ ] Provide a full `.github/workflows/main.yml` example (Build $\rightarrow$ Scan $\rightarrow$ Push $\rightarrow$ Deploy).
    - [x] Detail the "Observability Feedback Loop" (Prometheus $\rightarrow$ ArgoCD).
    - [x] Create a "Canary Deployment Design" assignment for a specific LLM model.

### Specialized
- [x] **`ai-containers.md`**
    - [x] Expand hardware support to include AMD (ROCm) and Intel (OneAPI).
    - [x] Add a deep dive on GPU VRAM vs System RAM limits.
    - [x] Add a "VRAM Optimization" case study (Quantization, PagedAttention).
- [x] **`container-storage-networking.md`**
    - [x] Mention enterprise storage solutions (**Ceph**, **GlusterFS**) for AI.
    - [x] Add a "Traffic Flow" diagram (Pod $\rightarrow$ Service $\rightarrow$ Ingress $\rightarrow$ External).
    - [x] Create a "Storage Strategy" design assignment.
- [ ] **`helm.md`**
    - [ ] Add advanced Go-template examples (loops/conditionals for dynamic GPU counts).
    - [x] Expand on `helm rollback` and `helm upgrade --atomic`.
    - [ ] Synchronize content with the new Helm sections in `kubernetes.md`.

### Enterprise & Cloud
- [x] **`openstack/openstack.md`**
    - [x] **Complete Rewrite**: Convert from "Lecture" style to "Guide" style (Objectives $\rightarrow$ Concepts $\rightarrow$ Evaluation).
- [x] **`kubernetes-advanced/`**
    - [x] Audit `hpa-autoscaling.md` and `rps-autoscaling.md` for "Production Guide" depth.
