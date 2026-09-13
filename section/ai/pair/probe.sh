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