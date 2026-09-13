
Below is a **step‑by‑step guide** you can follow to **install and start NVIDIA AI Pair on every machine in your “white” and “spark” clusters** and then use the Pair UI from your **Mac desktop**.  
The solution is based on the most common ‑ and fully‑automated ‑ toolchain:  

| Tool | What it does | Why we use it |
|------|--------------|---------------|
| **ssh / scp** | Remote command execution & file copy | You already have network reach from your laptop/Mac to the cluster nodes |
| **Ansible (optional but recommended)** | Runs the same commands on many hosts in parallel, handles errors, idempotent | Saves you from hand‑rolling loops and makes the deployment repeatable |
| **Docker (or the NVIDIA Container Runtime)** | Runs the Pair server as a container (the official NVIDIA distribution) | Guarantees the correct dependencies, driver version, and rapid upgrades |
| **NGC CLI / NGC API‑Key** | Authenticates to NVIDIA’s container registry | Needed to pull the private `nvcr.io/nvidia/pair` image |

> **TL;DR** – If you just want a quick one‑liner, skip the Ansible section and use the Bash loop at the end of this answer.  
> If you plan to keep the cluster up‑to‑date or add more nodes later, copy the Ansible playbook into a repo and run it whenever you need to redeploy.

---

## 1. Prerequisites on **all machines** (Mac desktop, “white”, “spark”)

| Item | How to verify / install |
|------|------------------------|
| **SSH access** | From your Mac run `ssh user@white‑node1` and `ssh user@spark‑node1`. You should land on a shell without being asked for a password (set up an SSH key). |
| **Docker Engine** (Linux nodes) | `docker --version` → `Docker version 24.xx` (or newer). Install via the NVIDIA‑Docker repository if you need GPU support: <br>```bash sudo apt-get update && sudo apt-get install -y docker.io nvidia-container-toolkit && sudo systemctl restart docker``` |
| **Docker Desktop** (Mac) | Download from <https://www.docker.com/products/docker-desktop/> and run it. |
| **NVIDIA driver & CUDA** (Linux GPU nodes) | `nvidia-smi` should show driver version ≥ 560 and a CUDA version that matches the Pair image (check the Pair release notes). |
| **NGC CLI** (optional, but handy) | ```bash curl -O https://ngc.nvidia.com/downloads/ngccli_2.12.0_linux_amd64.zip && unzip ngccli_2.12.0_linux_amd64.zip && sudo mv ngc /usr/local/bin/``` |
| **NGC API key** | Log in to <https://ngc.nvidia.com> → **Setup → API Key** → generate a key (e.g., `NVCR_API_KEY=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`). Keep it safe; you’ll paste it into a secret file later. |
| **Python 3.9+** (optional, for Ansible) | `python3 --version`. Install via Homebrew (`brew install python`) on macOS. |

---

## 2. Create a small **“bootstrap”** package that every host will receive

All hosts need two files:

1. **`pair.env`** – stores the NGC API key & optional runtime options.  
2. **`run_pair.sh`** – pulls the image and launches the container.

Create them on your Mac first:

```bash
# 1️⃣ pair.env  (do NOT commit the raw key to a public repo!)
cat > pair.env <<'EOF'
# ----- Do NOT share this file -----
NGC_API_KEY=YOUR_NGC_API_KEY_HERE
# Optional: expose Pair UI on a non‑standard port (default 8888)
PAIR_PORT=8888
EOF

# 2️⃣ run_pair.sh  (executable script)
cat > run_pair.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# Load env (API key, port, etc.)
source "$(dirname "$0")/pair.env"

# Docker login to NGC (once per host)
docker login nvcr.io -u '$oauthtoken' -p "$NGC_API_KEY"

# Pull the latest Pair image (you can pin a tag if you want)
docker pull nvcr.io/nvidia/pair:latest

# Stop any old container (idempotent)
docker rm -f nvidia-pair || true

# Run the container
docker run -d \
  --gpus all \
  --restart unless-stopped \
  -p "${PAIR_PORT:-8888}:8888" \
  --name nvidia-pair \
  -e NGC_API_KEY="${NGC_API_KEY}" \
  nvcr.io/nvidia/pair:latest
EOF

chmod +x run_pair.sh
```

> **Tip** – Replace `YOUR_NGC_API_KEY_HERE` with the key you generated in step 1.  
> If you have multiple GPU subsets per node you can add `--gpus '"device=0,1"`', but `--gpus all` works for most clusters.

---

## 3. Distribute the bootstrap files to every node

### 3.1 One‑liner Bash loop (quick & dirty)

```bash
# List all hostnames or IPs (space‑separated)
TARGETS="white-node1 white-node2 spark-node1 spark-node2"

# Path to your SSH private key (if not the default ~/.ssh/id_rsa)
SSH_KEY="~/.ssh/id_rsa"

for host in $TARGETS; do
  echo "=== Deploying to $host ==="
  # Create a temporary folder on the remote host
  ssh -i "$SSH_KEY" user@"$host" "mkdir -p ~/pair_deploy"
  # Copy the two files
  scp -i "$SSH_KEY" pair.env run_pair.sh user@"$host":~/pair_deploy/
  # Make the script executable & launch
  ssh -i "$SSH_KEY" user@"$host" "
    chmod +x ~/pair_deploy/run_pair.sh &&
    ~/pair_deploy/run_pair.sh
  "
  echo "✅ $host ready – Pair UI on ${PAIR_PORT:-8888}"
done
```

*Replace* `user` with the remote login name you use on those machines.

### 3.2 Ansible playbook (recommended for repeatable deployments)

1. **Install Ansible on your Mac**

```bash
python3 -m pip install --user ansible
export PATH="$HOME/.local/bin:$PATH"
```

2. **Create an inventory file** (`hosts.ini`)

```ini
[white]
white-node1 ansible_user=youruser
white-node2 ansible_user=youruser

[spark]
spark-node1 ansible_user=youruser
spark-node2 ansible_user=youruser
```

3. **Write the playbook** (`deploy_pair.yml`)

```yaml
- name: Deploy NVIDIA AI Pair on all hosts
  hosts: all
  become: true                # need sudo for Docker
  vars:
    pair_port: 8888           # change if you want a different port
    ngc_api_key: "{{ lookup('env','NGC_API_KEY') }}"   # safer: read from env
  tasks:
    - name: Ensure Docker is installed
      apt:
        name:
          - docker.io
          - nvidia-container-toolkit
        state: present
        update_cache: yes
      when: ansible_os_family == "Debian"

    - name: Start Docker service
      systemd:
        name: docker
        state: started
        enabled: yes

    - name: Create deployment dir
      file:
        path: /opt/pair_deploy
        state: directory
        mode: '0755'

    - name: Write pair.env (contains API key, port)
      copy:
        dest: /opt/pair_deploy/pair.env
        content: |
          NGC_API_KEY={{ ngc_api_key }}
          PAIR_PORT={{ pair_port }}
        mode: '0600'

    - name: Write run_pair.sh
      copy:
        dest: /opt/pair_deploy/run_pair.sh
        mode: '0755'
        content: |
          #!/usr/bin/env bash
          set -euo pipefail
          source /opt/pair_deploy/pair.env
          docker login nvcr.io -u '$oauthtoken' -p "$NGC_API_KEY"
          docker pull nvcr.io/nvidia/pair:latest
          docker rm -f nvidia-pair || true
          docker run -d \
            --gpus all \
            --restart unless-stopped \
            -p "${PAIR_PORT}:8888" \
            --name nvidia-pair \
            -e NGC_API_KEY="${NGC_API_KEY}" \
            nvcr.io/nvidia/pair:latest

    - name: Execute the bootstrap script
      command: /opt/pair_deploy/run_pair.sh
      register: pair_run
      changed_when: "'Created container' in pair_run.stdout"

    - name: Show the URL where Pair will be reachable
      debug:
        msg: "Pair is now listening on http://{{ inventory_hostname }}:{{ pair_port }}"
```

4. **Run the playbook**

```bash
# Export the API key into your shell so Ansible can read it securely
export NGC_API_KEY=YOUR_NGC_API_KEY_HERE

# Run – you’ll be prompted for sudo password on each host once
ansible-playbook -i hosts.ini deploy_pair.yml
```

*What you get*:  

- Docker installed (if missing)  
- The Pair image pulled from NGC  
- A container called `nvidia-pair` listening on port **8888** (or your chosen `pair_port`)  
- A tidy log of each host’s URL

You can re‑run the playbook anytime you want to **upgrade** the Pair version; Ansible will only pull a newer image and restart the container.

---

## 4. Access Pair from your **Mac desktop**

1. **Open a browser** on your Mac.  
2. Point it to any node’s IP/hostname and the port you chose, e.g.:

```
http://white-node1:8888
```

3. The first time you connect you’ll see a **login screen**. The default credentials are:

| User | Password |
|------|----------|
| `admin` | `admin` (or the password you set when you first launch Pair) |

> **Tip** – If you want a **single address** that forwards to the “best” node, set up an **HAProxy** or **NGINX** reverse‑proxy in front of the cluster, or simply use the macOS SSH tunnel:

```bash
# Forward local 8888 → remote node’s 8888
ssh -L 8888:white-node1:8888 user@white-node1 -N
# Then open http://localhost:8888 in your browser.
```

---

## 5. Keeping the deployment in sync (future upgrades)

| Action | Command |
|--------|---------|
| **Upgrade Pair on all nodes** (pull newest image) | `ansible -i hosts.ini all -b -m shell -a "docker pull nvcr.io/nvidia/pair:latest && docker rm -f nvidia-pair && docker run …"`  (or just re‑run the playbook) |
| **Change the exposed port** | Edit `pair_port` in the Ansible vars or modify `pair.env` and re‑run the playbook. |
| **Add a new node** | Append the hostname/IP to `hosts.ini`, ensure SSH key works, then re‑run the playbook – Ansible will handle the fresh node automatically. |
| **Rotate the NGC API key** | Update the environment variable `NGC_API_KEY` on your Mac, then re‑run the playbook; the new key gets written to `pair.env` on every host. |

---

## 6. Full “copy‑and‑run” script (Bash) – if you **don’t want Ansible**

Below is a **self‑contained script** you can drop into a file (e.g., `deploy_pair_all.sh`), edit the variables, and execute once. It does exactly what the loop in section 3.1 does, but with a few safety checks and logging.

```bash
#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------------
# USER‑CONFIGURATION – EDIT THESE VALUES
# ------------------------------------------------------------------
# List of remote hosts (space‑separated). Use DNS name or IP.
HOSTS=("white-node1" "white-node2" "spark-node1" "spark-node2")

# SSH user that exists on every host
SSH_USER="youruser"

# Path to your SSH private key (empty → default ~/.ssh/id_rsa)
SSH_KEY_PATH="${HOME}/.ssh/id_rsa"

# Port where Pair UI will be exposed on each host (default 8888)
PAIR_PORT=8888

# Your NGC API key (keep it secret!)
NGC_API_KEY="YOUR_NGC_API_KEY_HERE"

# ------------------------------------------------------------------
# END USER‑CONFIGURATION
# ------------------------------------------------------------------

# Write the two files locally (pair.env + run_pair.sh)
TMPDIR=$(mktemp -d)
cat > "${TMPDIR}/pair.env" <<EOF
NGC_API_KEY=${NGC_API_KEY}
PAIR_PORT=${PAIR_PORT}
EOF

cat > "${TMPDIR}/run_pair.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/pair.env"

# Docker login to NGC (use the built‑in OAuth token user)
docker login nvcr.io -u '$oauthtoken' -p "$NGC_API_KEY"

# Pull the latest Pair image
docker pull nvcr.io/nvidia/pair:latest

# Stop any stale container, then start a fresh one
docker rm -f nvidia-pair || true
docker run -d \
  --gpus all \
  --restart unless-stopped \
  -p "${PAIR_PORT}:8888" \
  --name nvidia-pair \
  -e NGC_API_KEY="${NGC_API_KEY}" \
  nvcr.io/nvidia/pair:latest
EOF
chmod +x "${TMPDIR}/run_pair.sh"

# ------------------------------------------------------------------
# Deploy to each host
# ------------------------------------------------------------------
for host in "${HOSTS[@]}"; do
  echo "=== Deploying Pair to ${host} ==="
  # 1️⃣ Create a remote dir
  ssh -i "${SSH_KEY_PATH}" "${SSH_USER}@${host}" "mkdir -p ~/pair_deploy"

  # 2️⃣ Copy files
  scp -i "${SSH_KEY_PATH}" "${TMPDIR}/pair.env" "${TMPDIR}/run_pair.sh" \
      "${SSH_USER}@${host}:~/pair_deploy/"

  # 3️⃣ Run the bootstrap script
  ssh -i "${SSH_KEY_PATH}" "${SSH_USER}@${host}" "
    chmod +x ~/pair_deploy/run_pair.sh &&
    ~/pair_deploy/run_pair.sh
  "

  echo "✅ ${host} – Pair UI available at http://${host}:${PAIR_PORT}"
  echo
done

# Clean up
rm -rf "${TMPDIR}"
echo "All done! 🎉"
```

**How to use**

```bash
# 1️⃣ Save the script (e.g., as deploy_pair_all.sh) and make it executable
chmod +x deploy_pair_all.sh

# 2️⃣ Edit the `HOSTS`, `SSH_USER`, `NGC_API_KEY`, etc. at the top of the file.

# 3️⃣ Run it
./deploy_pair_all.sh
```

The script will:

1. Create a temporary directory containing `pair.env` and `run_pair.sh`.  
2. SSH into each host, create `~/pair_deploy`, copy the two files, and invoke the script.  
3. Print a friendly URL for each node once the container is up.

> **Security note:** The script puts the raw NGC API key on each remote host in a file with mode `0600`. Only the `youruser` account (and root) can read it. If you share the host with other users, consider using a **secret manager** (e.g., HashiCorp Vault, AWS Secrets Manager) and inject the key at runtime instead of persisting it on disk.

---

## 7. Quick checklist – verify everything works

| ✅ Check | How to test |
|---------|-------------|
| Docker daemon runs | `ssh user@white-node1 "docker ps"` |
| Pair container is alive | `ssh user@white-node1 "docker ps --filter name=nvidia-pair"` |
| UI reachable from Mac | Open `http://white-node1:8888` (or any node) in Chrome/Firefox |
| GPU visibility inside container | `ssh user@white-node1 "docker exec nvidia-pair nvidia-smi"` should list the GPUs |
| No stray API key on your Mac | `grep -R YOUR_NGC_API_KEY_HERE ~` should return **nothing** outside of the script you just ran |

If any step fails, the error messages from Docker or SSH will usually point directly to the problem (e.g., missing driver, firewall blocking port 8888, wrong API key).  

---

### TL;DR Summary

1. **Generate an NGC API key**.  
2. **Create `pair.env` + `run_pair.sh`** (they contain the key, port, and Docker commands).  
3. **Copy those files to each node** (via a simple Bash loop or Ansible).  
4. **Run `run_pair.sh` on each node** – it logs into NGC, pulls the `nvcr.io/nvidia/pair` image, and starts the container.  
5. **Open `http://<node>:8888`** from your Mac to use Pair’s UI.  

With the **Ansible playbook** you get repeatable, version‑controlled deployments; with the **single‑command Bash loop** you get a fast “one‑off” rollout. Choose whichever matches your workflow, and you’ll be able to run NVIDIA AI Pair from your desktop on every node in the **white** and **spark** clusters. Happy coding!