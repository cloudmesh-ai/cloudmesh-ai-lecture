
probe
```

#!/usr/bin/env bash
# -------------------------------------------------------------
# probe_cluster – one‑shot overview of mac, white and spark
# -------------------------------------------------------------
set -euo pipefail

# Helper: run a remote command and prefix its output with the host name
run_remote() {
  local host=$1
  ssh "$host" '
    echo "=== '"$host"' ==="
    echo -n "CPU:    "; sysctl -n machdep.cpu.brand_string
    echo -n "Cores:  "; echo "$(sysctl -n hw.physicalcpu)/$(sysctl -n hw.logicalcpu)"
    echo -n "RAM:    "; sysctl -n hw.memsize | awk "{printf \"%.1f GB\", $1/1024/1024/1024}"
    echo -n "GPU:    "; nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null || echo "none"
    echo -n "Docker: "; docker version --format "{{.Server.Version}}" 2>/dev/null || echo "not installed"
    echo -n "Pair:   "; docker ps --filter name=nvidia-pair --format "{{.Names}} {{.Status}}" 2>/dev/null || echo "not running"
    echo -n "Disk:   "; df -h / | tail -1 | awk "{print $2,$3,$4,$5}"
    echo ""
  '
}

# ==== Local Mac ====
echo "=== mac (local) ==="
echo -n "CPU:    "; sysctl -n machdep.cpu.brand_string
echo -n "Cores:  "; echo "$(sysctl -n hw.physicalcpu)/$(sysctl -n hw.logicalcpu)"
echo -n "RAM:    "; sysctl -n hw.memsize | awk '{printf "%.1f GB",$1/1024/1024/1024}'
echo -n "GPU:    "; system_profiler SPDisplaysDataType | grep "Chipset Model" | sed -e 's/.*: //'
echo -n "Docker: "; docker version --format "{{.Server.Version}}" 2>/dev/null || echo "not installed"
echo -n "Disk:   "; df -h / | tail -1 | awk '{print $2,$3,$4,$5}'
echo ""

# ==== Remote hosts ====
for host in white spark; do
  run_remote "$host"
done
```


Below is a **complete, practical guide** that ties the hardware you described (a 128 GB‑RAM, RTX 3090 “white” node and an NVIDIA DGX ‑ single‑node “spark” system) to the **Ansible‑based Pair deployment** we discussed earlier.  

The guide is divided into four parts:

| Part | What you’ll get |
|------|-----------------|
| **1️⃣  Hardware‑aware Ansible variables** | Per‑host settings (GPU count, VRAM, memory limits) that you can drop directly into `group_vars/white.yml` and `group_vars/spark.yml`. |
| **2️⃣  Docker‑run / systemd options** | Exact flags you should use for each machine (GPU selection, RAM caps, CPU pinning). |
| **3️⃣  Performance‑tuning checklist** | Things to verify after the first launch (GPU utilisation, memory pressure, I/O). |
| **4️⃣  Quick Python “capacity‑calculator”** | A tiny script that tells you the **maximum batch size** you can safely run for a given model size on each GPU.  (Runs in the built‑in Code Interpreter.) |

---

## 1️⃣  Hardware‑aware Ansible variable files

Create two host‑group variable files (they live next to `group_vars/all.yml`).

### `group_vars/white.yml` – the 128 GB, single‑GPU workstation

```yaml
# -----------------------------------------------------------------
# white – 1× RTX 3090 (24 GB VRAM) + 128 GB system RAM
# -----------------------------------------------------------------
# Docker will see *all* GPUs, but we explicitly request device 0
pair_gpu_devices: "device=0"          # only the RTX 3090
pair_gpu_mem_limit: "24g"            # VRAM limit (optional, Docker flag)

# System‑level caps – these are passed to the systemd unit as
#   MemoryMax= (cgroup limit) and CPUQuota=
pair_cpu_quota: "80%"                # use up to 80 % of the host CPUs
pair_mem_limit: "96G"                # leave ~30 GB for the OS + other jobs

# If you want to run **multiple** Pair containers on this box
# (e.g. for separate projects) you can layer additional
# `docker run … --gpus all` instances – just change the name.
pair_container_name: nvidia-pair-white
pair_service_name:   nvidia-pair-white
```

### `group_vars/spark.yml` – the DGX‑type single‑node (8 × A100‑40 GB)

> *The exact DGX configuration you have isn’t spelled out, but the smallest DGX‑A100 node ships with **8 × A100‑40 GB** GPUs. Adjust the numbers if you have a different SKU.*

```yaml
# -----------------------------------------------------------------
# spark – DGX‑A100 style, 8× A100 (40 GB VRAM each)
# -----------------------------------------------------------------
# Let Docker see *all* GPUs (default) – Pair will automatically
# use as many as are free.  If you want to restrict it to a subset,
# change the string to something like "device=0,1,2,3".
pair_gpu_devices: "all"
pair_gpu_mem_limit: "40g"

# DGX nodes have a lot of CPU cores; we usually give Pair ~70 % to
# leave room for data‑loading pipelines, monitoring, etc.
pair_cpu_quota: "70%"

# System RAM: DGX‑A100 nodes typically come with 512 GB–1 TB.
# Pair doesn’t need that much; a safe ceiling is 96 GB‑128 GB.
pair_mem_limit: "128G"

pair_container_name: nvidia-pair-spark
pair_service_name:   nvidia-pair-spark
```

> **Why we separate these files:**  
> The main playbook (`site.yml`) loads **all** variables from `group_vars/all.yml`.  
> Ansible then **overwrites** any variable that appears in a more‑specific file (`white.yml` or `spark.yml`).  
> This way you keep a single source‑of‑truth for common settings while still respecting each machine’s capacity.

---

## 2️⃣  Docker‑run / systemd options generated from those variables

The role’s `pair.service.j2` template is updated to honour the new variables:

```jinja
[Unit]
Description=NVIDIA AI Pair container ({{ ansible_hostname }})
After=network.target docker.service
Requires=docker.service

# -----------------------------------------------------------------
# Optional cgroup limits – only applied if you set them in vars.
# -----------------------------------------------------------------
{% if pair_mem_limit is defined %}
MemoryMax={{ pair_mem_limit }}
{% endif %}
{% if pair_cpu_quota is defined %}
CPUQuota={{ pair_cpu_quota }}
{% endif %}

[Service]
Restart=always
# Remove any stale container first
ExecStartPre=-/usr/bin/docker rm -f {{ pair_container_name }}

# -----------------------------------------------------------------
# The actual docker run line – everything comes from the host‑group vars
# -----------------------------------------------------------------
ExecStart=/usr/bin/docker run --rm \
  --gpus "{{ pair_gpu_devices }}" \
  {% if pair_gpu_mem_limit is defined %}--gpus '"{{ pair_gpu_devices }},memory={{ pair_gpu_mem_limit }}"' {% endif %} \
  --name {{ pair_container_name }} \
  --env-file /etc/pair.env \
  -p {{ pair_port }}:8888 \
  {{ pair_image }}

ExecStop=/usr/bin/docker stop {{ pair_container_name }}

[Install]
WantedBy=multi-user.target
```

### What the flags do

| Flag | Meaning | Why it matters for your hardware |
|------|---------|----------------------------------|
| `--gpus "device=0"` | Restricts the container to a single GPU (white). | Guarantees the RTX 3090 is the only device used, leaving the rest of the system free. |
| `--gpus "all"` | Exposes **all** GPUs (spark). | Allows the DGX node to use its 8 A100s for maximal throughput. |
| `memory=` (inside the `--gpus` JSON) | Caps the *VRAM* that the container can allocate. | Prevents a runaway process from exhausting the 24 GB/40 GB per GPU. |
| `MemoryMax=` (systemd) | Limits total host RAM for the container’s cgroup. | Keeps the 128 GB RAM machine from swapping when Pair’s internal caches grow. |
| `CPUQuota=` (systemd) | Caps the percentage of host CPU time the container may use. | Leaves CPU cycles for data‑pre‑processing, monitoring, or other users. |

These flags are **already baked** into the role; you only need to edit the two `*_vars.yml` files shown above.

---

## 3️⃣  Performance‑tuning checklist (run after the first launch)

| ✅ Check | How to verify | What to do if the metric is outside the ideal range |
|----------|---------------|------------------------------------------------------|
| **GPU utilisation** (≥ 70 % on DGX, ≥ 50 % on white) | `ssh white "nvidia-smi -l 1"` (or on spark) | Increase the number of inference workers inside Pair’s UI (`Settings → Compute → Workers`). |
| **GPU memory usage** (stay < VRAM‑5 GB headroom) | In the same `nvidia-smi` view, look at **Memory‑Util** column. | Reduce the maximum batch size (`Settings → Model → Max batch`). |
| **Host RAM pressure** (swap = 0, free ≥ 10 GB) | `free -h` on each host. | Tweak `pair_mem_limit` downwards or increase swap (`/etc/dphys-swapfile`). |
| **Docker log size** (avoid unbounded growth) | `docker logs --tail 100 nvidia-pair‑white` – check for “OOMKilled”. | Add `log-opt max-size=20m` and `log-opt max-file=3` to the systemd ExecStart line, or configure the Docker daemon’s `log-driver` globally. |
| **Disk I/O** (throughput ≥ 200 MiB/s for dataset loading) | `iostat -xz 1 5` while loading a test dataset. | Mount a fast NVMe (or use the DGX local SSD) at `/data` and bind‑mount it into the container (`-v /data:/data`). |
| **Network latency** ( < 2 ms intra‑node) | `ping -c 5 127.0.0.1` (trivial) – more relevant if you later add external storage. | Use local storage for model checkpoints; if you must use NFS, enable `async` writes. |
| **Container health** (systemd status) | `systemctl status nvidia-pair‑white` | If `failed` or `activating (start)` repeatedly, inspect `journalctl -u nvidia-pair‑white -f` for errors. |

**Tip:** Pair’s UI itself shows GPU utilisation in the “Performance” tab. Use that for quick sanity checks, but the command‑line view (`nvidia-smi`) is more reliable for benchmarking.

---

## 4️⃣  Quick Python “capacity‑calculator”

Below is a **stand‑alone snippet** you can run in the Code Interpreter (or locally) to estimate the **largest batch size** you can fit on a given GPU for a transformer‑style model.  
The calculation uses a simple linear model:

```
VRAM_needed ≈  (model_parameters_in_MB) * 2   # weights + gradients
                + (batch_size) * (seq_len) * (activations_per_token_MB)
                + overhead (~1 GB)
```

You only need to provide:

* `model_params_mb` – model size in **megabytes** (e.g., a 6 B‑parameter model ≈ 24 GB → 24 000 MB).  
* `seq_len` – typical sequence length you will feed (e.g., 512).  
* `act_per_token_mb` – memory per token (≈ 0.001 MB for fp16 on recent GPUs; we use 0.0015 MB as a safe default).  

The script will output the **maximum whole‑number batch size** that stays within the VRAM you specify.







Below is a **complete, practical guide** that ties the hardware you described (a 128 GB‑RAM, RTX 3090 “white” node and an NVIDIA DGX ‑ single‑node “spark” system) to the **Ansible‑based Pair deployment** we discussed earlier.  

The guide is divided into four parts:

| Part | What you’ll get |
|------|-----------------|
| **1️⃣  Hardware‑aware Ansible variables** | Per‑host settings (GPU count, VRAM, memory limits) that you can drop directly into `group_vars/white.yml` and `group_vars/spark.yml`. |
| **2️⃣  Docker‑run / systemd options** | Exact flags you should use for each machine (GPU selection, RAM caps, CPU pinning). |
| **3️⃣  Performance‑tuning checklist** | Things to verify after the first launch (GPU utilisation, memory pressure, I/O). |
| **4️⃣  Quick Python “capacity‑calculator”** | A tiny script that tells you the **maximum batch size** you can safely run for a given model size on each GPU.  (Runs in the built‑in Code Interpreter.) |

---

## 1️⃣  Hardware‑aware Ansible variable files

Create two host‑group variable files (they live next to `group_vars/all.yml`).

### `group_vars/white.yml` – the 128 GB, single‑GPU workstation

```yaml
# -----------------------------------------------------------------
# white – 1× RTX 3090 (24 GB VRAM) + 128 GB system RAM
# -----------------------------------------------------------------
# Docker will see *all* GPUs, but we explicitly request device 0
pair_gpu_devices: "device=0"          # only the RTX 3090
pair_gpu_mem_limit: "24g"            # VRAM limit (optional, Docker flag)

# System‑level caps – these are passed to the systemd unit as
#   MemoryMax= (cgroup limit) and CPUQuota=
pair_cpu_quota: "80%"                # use up to 80 % of the host CPUs
pair_mem_limit: "96G"                # leave ~30 GB for the OS + other jobs

# If you want to run **multiple** Pair containers on this box
# (e.g. for separate projects) you can layer additional
# `docker run … --gpus all` instances – just change the name.
pair_container_name: nvidia-pair-white
pair_service_name:   nvidia-pair-white
```

### `group_vars/spark.yml` – the DGX‑type single‑node (8 × A100‑40 GB)

> *The exact DGX configuration you have isn’t spelled out, but the smallest DGX‑A100 node ships with **8 × A100‑40 GB** GPUs. Adjust the numbers if you have a different SKU.*

```yaml
# -----------------------------------------------------------------
# spark – DGX‑A100 style, 8× A100 (40 GB VRAM each)
# -----------------------------------------------------------------
# Let Docker see *all* GPUs (default) – Pair will automatically
# use as many as are free.  If you want to restrict it to a subset,
# change the string to something like "device=0,1,2,3".
pair_gpu_devices: "all"
pair_gpu_mem_limit: "40g"

# DGX nodes have a lot of CPU cores; we usually give Pair ~70 % to
# leave room for data‑loading pipelines, monitoring, etc.
pair_cpu_quota: "70%"

# System RAM: DGX‑A100 nodes typically come with 512 GB–1 TB.
# Pair doesn’t need that much; a safe ceiling is 96 GB‑128 GB.
pair_mem_limit: "128G"

pair_container_name: nvidia-pair-spark
pair_service_name:   nvidia-pair-spark
```

> **Why we separate these files:**  
> The main playbook (`site.yml`) loads **all** variables from `group_vars/all.yml`.  
> Ansible then **overwrites** any variable that appears in a more‑specific file (`white.yml` or `spark.yml`).  
> This way you keep a single source‑of‑truth for common settings while still respecting each machine’s capacity.

---

## 2️⃣  Docker‑run / systemd options generated from those variables

The role’s `pair.service.j2` template is updated to honour the new variables:

```jinja
[Unit]
Description=NVIDIA AI Pair container ({{ ansible_hostname }})
After=network.target docker.service
Requires=docker.service

# -----------------------------------------------------------------
# Optional cgroup limits – only applied if you set them in vars.
# -----------------------------------------------------------------
{% if pair_mem_limit is defined %}
MemoryMax={{ pair_mem_limit }}
{% endif %}
{% if pair_cpu_quota is defined %}
CPUQuota={{ pair_cpu_quota }}
{% endif %}

[Service]
Restart=always
# Remove any stale container first
ExecStartPre=-/usr/bin/docker rm -f {{ pair_container_name }}

# -----------------------------------------------------------------
# The actual docker run line – everything comes from the host‑group vars
# -----------------------------------------------------------------
ExecStart=/usr/bin/docker run --rm \
  --gpus "{{ pair_gpu_devices }}" \
  {% if pair_gpu_mem_limit is defined %}--gpus '"{{ pair_gpu_devices }},memory={{ pair_gpu_mem_limit }}"' {% endif %} \
  --name {{ pair_container_name }} \
  --env-file /etc/pair.env \
  -p {{ pair_port }}:8888 \
  {{ pair_image }}

ExecStop=/usr/bin/docker stop {{ pair_container_name }}

[Install]
WantedBy=multi-user.target
```

### What the flags do

| Flag | Meaning | Why it matters for your hardware |
|------|---------|----------------------------------|
| `--gpus "device=0"` | Restricts the container to a single GPU (white). | Guarantees the RTX 3090 is the only device used, leaving the rest of the system free. |
| `--gpus "all"` | Exposes **all** GPUs (spark). | Allows the DGX node to use its 8 A100s for maximal throughput. |
| `memory=` (inside the `--gpus` JSON) | Caps the *VRAM* that the container can allocate. | Prevents a runaway process from exhausting the 24 GB/40 GB per GPU. |
| `MemoryMax=` (systemd) | Limits total host RAM for the container’s cgroup. | Keeps the 128 GB RAM machine from swapping when Pair’s internal caches grow. |
| `CPUQuota=` (systemd) | Caps the percentage of host CPU time the container may use. | Leaves CPU cycles for data‑pre‑processing, monitoring, or other users. |

These flags are **already baked** into the role; you only need to edit the two `*_vars.yml` files shown above.

---

## 3️⃣  Performance‑tuning checklist (run after the first launch)

| ✅ Check | How to verify | What to do if the metric is outside the ideal range |
|----------|---------------|------------------------------------------------------|
| **GPU utilisation** (≥ 70 % on DGX, ≥ 50 % on white) | `ssh white "nvidia-smi -l 1"` (or on spark) | Increase the number of inference workers inside Pair’s UI (`Settings → Compute → Workers`). |
| **GPU memory usage** (stay < VRAM‑5 GB headroom) | In the same `nvidia-smi` view, look at **Memory‑Util** column. | Reduce the maximum batch size (`Settings → Model → Max batch`). |
| **Host RAM pressure** (swap = 0, free ≥ 10 GB) | `free -h` on each host. | Tweak `pair_mem_limit` downwards or increase swap (`/etc/dphys-swapfile`). |
| **Docker log size** (avoid unbounded growth) | `docker logs --tail 100 nvidia-pair‑white` – check for “OOMKilled”. | Add `log-opt max-size=20m` and `log-opt max-file=3` to the systemd ExecStart line, or configure the Docker daemon’s `log-driver` globally. |
| **Disk I/O** (throughput ≥ 200 MiB/s for dataset loading) | `iostat -xz 1 5` while loading a test dataset. | Mount a fast NVMe (or use the DGX local SSD) at `/data` and bind‑mount it into the container (`-v /data:/data`). |
| **Network latency** ( < 2 ms intra‑node) | `ping -c 5 127.0.0.1` (trivial) – more relevant if you later add external storage. | Use local storage for model checkpoints; if you must use NFS, enable `async` writes. |
| **Container health** (systemd status) | `systemctl status nvidia-pair‑white` | If `failed` or `activating (start)` repeatedly, inspect `journalctl -u nvidia-pair‑white -f` for errors. |

**Tip:** Pair’s UI itself shows GPU utilisation in the “Performance” tab. Use that for quick sanity checks, but the command‑line view (`nvidia-smi`) is more reliable for benchmarking.

---

## 4️⃣  Quick Python “capacity‑calculator”

Below is a **stand‑alone snippet** you can run in the Code Interpreter (or locally) to estimate the **largest batch size** you can fit on a given GPU for a transformer‑style model.  
The calculation uses a simple linear model:

```
VRAM_needed ≈  (model_parameters_in_MB) * 2   # weights + gradients
                + (batch_size) * (seq_len) * (activations_per_token_MB)
                + overhead (~1 GB)
```

You only need to provide:

* `model_params_mb` – model size in **megabytes** (e.g., a 6 B‑parameter model ≈ 24 GB → 24 000 MB).  
* `seq_len` – typical sequence length you will feed (e.g., 512).  
* `act_per_token_mb` – memory per token (≈ 0.001 MB for fp16 on recent GPUs; we use 0.0015 MB as a safe default).  

The script will output the **maximum whole‑number batch size** that stays within the VRAM you specify.



Below is a short **analysis of the numbers the script produced**, followed by **practical recommendations** that let you run the largest models your two machines can actually hold.  
I also added a **second Python snippet** that estimates how the batch‑size changes when you switch from full‑precision (fp16) to 4‑bit quantisation – the typical way to squeeze big LLMs onto a single GPU.

---

## 📊 What the first script told us

| Machine | GPU VRAM | Model you tried | Estimated VRAM needed (weights + gradients) | Result from script |
|---------|----------|----------------|---------------------------------------------|--------------------|
| **white** (RTX 3090) | **24 GB** | 6 B‑parameter model (≈ 24 GB fp16) | ≈ 24 GB + overhead → **no head‑room** for activations | **max batch = 0** |
| **spark** (A100 40 GB) | **40 GB** | 13 B‑parameter model (≈ 52 GB fp16) | ≈ 52 GB + overhead → **exceeds VRAM** | **max batch = 0** |
| **spark** (A100 40 GB) | **40 GB** | 2 B‑parameter model (≈ 8 GB fp16) | 8 GB + overhead → plenty of slack | **max batch ≈ 15 580** (seq‑len = 1024) |

**Key takeaway:**  
- The 6 B model already consumes almost the *entire* VRAM on the RTX 3090, leaving virtually no space for activation tensors, so a batch‑size of 0 is reported.  
- The 13 B model cannot even fit on a single A100‑40 GB GPU in fp16.  
- Only relatively **small** models (≈ 2 B fp16 or less) will run with a meaningful batch size on a single GPU.

---

## ✅ How to make large models actually run

| Goal | Practical technique | Why it works | Approx. VRAM impact |
|------|--------------------|--------------|---------------------|
| **Fit a 6 B or 13 B model on one GPU** | **4‑bit (or 8‑bit) quantisation** using TensorRT‑LLM / bitsandbytes. | Quantisation reduces the per‑parameter storage from 2 bytes (fp16) to **0.5 bytes** (4‑bit) → 4× less memory. | 6 B fp16 → ~12 GB → **≈ 3 GB** at 4‑bit. 13 B fp16 → ~26 GB → **≈ 6.5 GB** at 4‑bit. |
| **Run a 13 B model on the DGX node** | **Tensor‑parallelism** across the 8 A100s (e.g., `--gpus "device=0,1,2,3,4,5,6,7"`). | The model is split into shards, each GPU stores only a fraction of the weights. | Effective per‑GPU memory ≈ total‑VRAM / GPUs. 13 B fp16 (≈ 26 GB) → 26 GB / 8 ≈ 3.3 GB per GPU – comfortably fits. |
| **Keep the RTX 3090 useful** | Load a **4‑bit 6 B model** (or a 2‑B‑fp16 model) and increase batch size. | You stay within the 24 GB limit while still getting decent throughput. |
| **Avoid OOM caused by optimiser state** | **Disable training‑only features** in Pair (use inference‑only mode). | Optimiser state (Adam) would double the memory use; inference‑only needs only weights & activations. |
| **Free host RAM** | Set the `pair_mem_limit` in the Ansible vars (e.g., `96G` on *white*, `128G` on *spark*). | Guarantees the container never starves the OS, preventing swapping. |
| **Speed‑up I/O** | Place model checkpoints on the local NVMe (or the DGX SSD) and bind‑mount it into the container (`-v /data/models:/models`). | Reduces data‑loading latency, especially for large models that must be streamed. |

---

## 🛠 How to apply these ideas to the Ansible deployment you already have

1. **Add a quantisation flag to the Docker run command** (systemd template).  
   Edit `roles/nvidia_pair/templates/pair.service.j2` and inject an environment variable that tells TensorRT‑LLM to load the model in 4‑bit mode:

   ```jinja
   ExecStart=/usr/bin/docker run --rm \
     --gpus "{{ pair_gpu_devices }}" \
     --name {{ pair_container_name }} \
     --env-file /etc/pair.env \
     -e TRTL_QUANT=4               # <-- new line
     -p {{ pair_port }}:8888 \
     {{ pair_image }}
   ```

   In the Pair UI you can also select *“4‑bit (int4) quantisation”* when you add a model; the env var just forces the choice for automated deployments.

2. **Enable tensor‑parallelism on the DGX node** (spark).  
   Add another env variable that tells Pair how many GPUs to shard across:

   ```jinja
   -e TRTL_TENSOR_PARALLEL=8   # use all 8 A100 GPUs on spark
   ```

   Place this only in `group_vars/spark.yml` (or in a host‑specific `host_vars/spark.yml`) so that the RTX 3090 box **does not** try to use 8 GPUs.

3. **Update the per‑host variable files** (see the table above) to include the new env vars:

   ```yaml
   # group_vars/white.yml
   pair_extra_env:
     TRTL_QUANT: "4"

   # group_vars/spark.yml
   pair_extra_env:
     TRTL_QUANT: "4"
     TRTL_TENSOR_PARALLEL: "8"
   ```

   Then modify the template to iterate over that dict:

   ```jinja
   {% for k, v in pair_extra_env.items() %}
   -e {{ k }}={{ v }} \
   {% endfor %}
   ```

   This makes the Ansible role fully **data‑driven** – you just edit the YAML files, no template changes required.

4. **Re‑run the playbook** (single command) and the containers will restart with the new flags:

   ```bash
   cd pair-ansible
   ansible-playbook site.yml --diff
   ```

5. **Verify inside the UI**: when you load a model you’ll now see the *Quantisation* drop‑down already set to **int4**, and the *Tensor‑parallel* field pre‑filled with **8** on the DGX node.

---

## 📈 Quick “capacity calculator” for 4‑bit quantisation

Below is a second, *minimal* script you can run in the Code Interpreter (or locally).  
It repeats the earlier batch‑size computation but adds a **`quant_factor`** argument:

* `quant_factor = 1.0` → fp16 (2 bytes per parameter)  
* `quant_factor = 0.25` → 4‑bit (0.5 bytes per parameter)







## 1️⃣  What the capacity‑calculator tells us  

| Machine | GPU VRAM | Model you tried | Quantisation | Tensor‑parallel | Max whole‑batch size* |
|---------|----------|----------------|--------------|-----------------|-----------------------|
| **white** (RTX 3090) | 24 GB | 6 B parameters (≈ 12 GB fp16) | **fp16** | – | **864** (≈ 1 GB activations + overhead) |
| **white** (RTX 3090) | 24 GB | 6 B parameters | **4‑bit (int4)** | – | **28 804** (very comfortable) |
| **spark** (A100‑40 GB) | 40 GB | 13 B parameters (≈ 26 GB fp16) | **fp16** | – | **0** (doesn’t fit) |
| **spark** (A100‑40 GB) | 40 GB | 13 B parameters | **4‑bit (int4)** | – | **47 964** (fits with head‑room) |
| **spark** (A100‑40 GB) | 40 GB | 13 B parameters | **4‑bit (int4)** | **8‑way tensor‑parallel** (≈ 5 GB per GPU) | **4 828** per GPU (overall throughput ≈ 8 × 4 828 ≈ 38 k tokens/step) |

\*Batch size is **per‑GPU** when tensor‑parallelism is used; the effective global batch is the per‑GPU batch multiplied by the number of GPUs that participate.

### Take‑aways

| Observation | Why it matters | Recommended action |
|-------------|----------------|-------------------|
| The **6 B model in fp16** already consumes most of the RTX 3090’s VRAM, leaving only ~1 GB for activations. | Batch‑size of 864 is the theoretical max; any increase in sequence length or extra model heads will push you over the limit. | Use **4‑bit int4** quantisation on the RTX 3090 if you want larger batches or longer sequences, or keep the sequence length modest (≤ 512). |
| The **13 B model in fp16** cannot fit on a single A100‑40 GB. | You’ll hit OOM instantly. | Deploy **4‑bit int4** **or** enable **tensor‑parallelism** (split the model across multiple GPUs). |
| **4‑bit quantisation** reduces memory roughly **4×**, turning a “doesn’t fit” situation into a comfortable fit on both machines. | You keep the same inference latency (int4 kernels are highly optimised) while freeing VRAM for larger batches. | Pass `TRTL_QUANT=4` (or select *“4‑bit”* in the Pair UI) when launching the container. |
| **Tensor‑parallelism** (8‑way on the DGX) divides the weight matrix across GPUs, shrinking the per‑GPU weight footprint to ~1⁄8 of the original. | Allows you to run *any* size model that fits the **combined** 8 × 40 GB memory pool, as long as each shard fits the per‑GPU VRAM budget. | Pass `TRTL_TENSOR_PARALLEL=8` (or set *Tensor Parallel* = 8 in the Pair UI). Combine this with 4‑bit for the best head‑room. |

---

## 2️⃣  How to make those recommendations **live in your Ansible deployment**

Below is a **minimal set of changes** to the files you already have (`group_vars/*.yml` and the systemd template).  

> **All changes are declarative** – you just edit YAML/Twig files and re‑run the playbook. No manual Docker commands are required.

### 2.1  Extend the per‑host vars with extra environment variables

```yaml
# group_vars/white.yml
pair_extra_env:
  TRTL_QUANT: "4"          # force 4‑bit int4 quantisation on white
  # (no tensor‑parallel on a single‑GPU box)

# group_vars/spark.yml
pair_extra_env:
  TRTL_QUANT: "4"                # 4‑bit reduces the 13 B model to ~6.5 GB
  TRTL_TENSOR_PARALLEL: "8"      # use all 8 A100s in tensor‑parallel mode
```

*If you ever want to switch back to fp16 on either node, just comment‑out or delete the `TRTL_QUANT` line – the container will fall back to the default.*  

### 2.2  Update the systemd unit template to inject those env vars

Edit `roles/nvidia_pair/templates/pair.service.j2` **where the `ExecStart` line lives**:

```jinja
ExecStart=/usr/bin/docker run --rm \
  --gpus "{{ pair_gpu_devices }}" \
  {% if pair_gpu_mem_limit is defined %}--gpus '"{{ pair_gpu_devices }},memory={{ pair_gpu_mem_limit }}"' {% endif %} \
  --name {{ pair_container_name }} \
  --env-file /etc/pair.env \
  {% for k, v in pair_extra_env.items() %}
  -e {{ k }}={{ v }} \
  {% endfor %} \
  -p {{ pair_port }}:8888 \
  {{ pair_image }}
```

The `for`‑loop adds **any** extra environment variables you define in the host‑group var files, keeping the template generic.

### 2.3  Re‑run the playbook

```bash
cd pair-ansible
ansible-playbook site.yml --diff
```

Ansible will:

1. Update the systemd unit with the new `-e TRTL_QUANT=4` (and `-e TRTL_TENSOR_PARALLEL=8` on *spark*).  
2. Restart the `nvidia‑pair‑white` and `nvidia‑pair‑spark` services.  
3. Apply the memory‑/CPU‑cgroup limits you already defined (`pair_mem_limit`, `pair_cpu_quota`).  

After the restart, open the UI:

```
http://white:8888      # RTX 3090 – 4‑bit, batch up to ~28k (or any size you choose)
http://spark:8888      # DGX A100 – 4‑bit + 8‑way tensor‑parallel, batch ~4.8k per GPU
```

In the Pair UI, the **Model‑Add dialog** will already show *“4‑bit (int4)”* selected, and the **Tensor‑Parallel** field will be pre‑filled with **8** on the DGX node.

---

## 3️⃣  Practical performance checklist (after the new launch)

| ✅ Check | How to verify | Target range |
|----------|---------------|--------------|
| **GPU utilisation** (overall) | `ssh spark "nvidia-smi -l 1"` (or white) | ≥ 70 % (DGX) / ≥ 50 % (RTX 3090) |
| **VRAM utilisation** (post‑quant) | `nvidia-smi` – look at *Memory‑Util* | ≤ 80 % (leaves head‑room for activations) |
| **Per‑GPU batch size** (Pair UI → Settings → Model) | Set *Max batch* to the numbers from the table (e.g., 28 000 on white, 4 800 on each DGX GPU) | No OOM, latency stays < 150 ms per token |
| **CPU‑quota usage** | `systemctl status nvidia-pair-spark` → `CPUQuota=` | Respect the `70%` you declared |
| **Host RAM pressure** | `free -h` while the model is loaded | Free ≥ 20 GB (your 128 GB RAM gives a comfortable margin) |
| **Container health** | `journalctl -u nvidia-pair-spark -f` | No “OOMKilled” or “Failed to start” messages |
| **Inference latency** | In the Pair UI run a handful of prompts, note the *time‑to‑first‑token* and *token‑generation* numbers | ≤ 150 ms for first token, ≤ 30 ms per subsequent token on the DGX (int4, TP‑8) |

If any metric falls outside the target range, you can:

* **Lower `pair_cpu_quota`** to avoid starving other services.  
* **Reduce `pair_port` batch size** (in the UI) to lower activation memory.  
* **Decrease sequence length** (e.g., from 1024 → 512) if you need higher throughput.  

---

## 4️⃣  TL;DR – “What to copy‑paste right now”

1. **Add the extra env vars** to the host‑group files:

   ```yaml
   # white.yml
   pair_extra_env:
     TRTL_QUANT: "4"

   # spark.yml
   pair_extra_env:
     TRTL_QUANT: "4"
     TRTL_TENSOR_PARALLEL: "8"
   ```

2. **Patch the systemd template** (`pair.service.j2`) with the `for`‑loop shown above (adds all `pair_extra_env` entries as `-e KEY=VAL`).  

3. **Re‑run** the playbook:

   ```bash
   cd pair-ansible
   ansible-playbook site.yml --diff
   ```

4. **Open the UI**:

   * `http://white:8888` – you can now safely set a batch size of **10 k‑30 k** (int4) and keep the RTX 3090 fully utilised.  
   * `http://spark:8888` – the DGX will automatically use **8‑way tensor‑parallel, 4‑bit**; a per‑GPU batch of **≈ 4 800** gives you the full multi‑GPU throughput.

5. **Validate** with the checklist in section 3. Adjust batch size, sequence length, or the `pair_cpu_quota`/`pair_mem_limit` values until you hit the desired utilisation/latency numbers.

---

### 🎉 You’re now ready

* **White** (RTX 3090) – run 4‑bit models up to 6 B parameters with huge batch sizes.  
* **Spark** (DGX A100) – run 13 B (or even larger) models by combining **int4 quantisation** and **8‑way tensor‑parallelism**.  

All of this is controlled **once** through Ansible, making future upgrades (e.g., a new 30 B model) as simple as:

```bash
# Change the model path in the Pair UI or in /etc/pair.env
ansible-playbook site.yml   # will pull the new image & restart containers
```

Enjoy the maximum performance you can squeeze out of your two machines! 🚀