
Below is a **practical, production‑ready workflow** that lets you install **NVIDIA AI Pair** on every node in the *white* and *spark* clusters with only a few commands.  
The approach is built around three pillars:

| Pillar | What it does | Why it’s the “best” choice |
|--------|--------------|----------------------------|
| **Infrastructure as code (Ansible)** | One‑click, repeatable, idempotent installation on any number of hosts. | Guarantees the same exact software version and configuration on every node and makes future upgrades painless. |
| **Docker (NVIDIA container runtime)** | Runs Pair in an isolated container that already contains all dependencies. | Removes the “works on my machine” problem, matches the official NVIDIA distribution, and lets you upgrade by just pulling a newer image. |
| **Secure secret handling (Ansible Vault)** | Stores the NGC API key (needed to pull the private image) in an encrypted file. | Keeps your credential out of source control while still allowing the playbook to read it at runtime. |

---

## 1. High‑level overview of the steps

1. **Prep your Mac (the Ansible control node).**  
   Install Ansible, generate an SSH key, and add that key to every cluster node.  

2. **Create an inventory file** that lists all *white* and *spark* machines.  

3. **Store the NGC API key** in an encrypted vault (`vault.yml`).  

4. **Write a reusable Ansible role** (`nvidia_pair`) that:  
   * installs Docker + NVIDIA runtime,  
   * logs in to `nvcr.io`,  
   * pulls the `nvcr.io/nvidia/pair` image,  
   * writes a tiny `pair.env` file (holds the API key & port),  
   * installs a `systemd` unit that runs the container as a service.  

5. **Run the playbook** – one command brings Pair up on *every* node.  

6. **Optional – expose a single entry point** (HAProxy/NGINX or an SSH tunnel) so you can open the UI from your Mac with a single address.

The diagram below shows the data flow:

```
+------------------+          SSH          +-------------------+
|  Mac (Ansible)   |---------------------->|  white‑node1      |
|  - inventory    |                       |  - Docker         |
|  - vault (API)  |                       |  - Pair container |
+------------------+          ...          +-------------------+
          |
          |  (same for white‑node2, spark‑node1, …)
          v
   UI reachable at http://<node>:8888
```

---

## 2. One‑time setup on the **control machine** (your Mac)

```bash
# 1️⃣ Install Ansible (user‑level, no sudo required)
python3 -m pip install --user ansible

# Add the user‑local bin to PATH (add to ~/.zshrc / ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# 2️⃣ Verify
ansible --version   # should show ≥ 2.14

# 3️⃣ Generate an SSH key (if you don’t have one already)
ssh-keygen -t ed25519 -C "your‑email@example.com"

# 4️⃣ Copy the public key to every cluster node
# (replace USER and HOST with real values, repeat for all nodes)
for h in white-node1 white-node2 spark-node1 spark-node2; do
  ssh-copy-id USER@"$h"
done
```

> **Result:** password‑less SSH from your Mac to every node.

---

## 3. Create the **Ansible project** skeleton

```bash
mkdir -p pair‑ansible/{group_vars,host_vars,roles/nvidia_pair/{tasks,templates,files}}
cd pair-ansible
touch ansible.cfg inventory.ini group_vars/all.yml vault.yml site.yml
```

### `ansible.cfg`

```ini
[defaults]
inventory = inventory.ini
remote_user = USER            # <-- put the SSH login name you used above
host_key_checking = False
retry_files_enabled = False
vault_password_file = .vault_pass.txt
interpreter_python = auto_silent

[ssh_connection]
scp_if_ssh = True
```

> Replace `USER` with the account that exists on every node.

### `inventory.ini`

```ini
[white]
white-node1 ansible_host=10.0.1.11
white-node2 ansible_host=10.0.1.12

[spark]
spark-node1 ansible_host=10.0.2.21
spark-node2 ansible_host=10.0.2.22

[all_nodes:children]
white
spark
```

(If you prefer DNS names, use them in `ansible_host=`.)

### `group_vars/all.yml`

```yaml
# ---------- Docker ----------
docker_packages:
  - docker.io
  - nvidia-container-toolkit

docker_daemon_options:
  default-runtime: nvidia
  runtimes:
    nvidia:
      path: /usr/bin/nvidia-container-runtime
      runtimeArgs: []

# ---------- Pair ----------
pair_image: nvcr.io/nvidia/pair:latest   # pin a tag if you want reproducibility
pair_port: 8888                          # UI port on every host
pair_container_name: nvidia-pair
pair_service_name: nvidia-pair
```

---

## 4. Secure the **NGC API key** with Ansible Vault

```bash
# 1️⃣ Create a simple vault‑password file (keep it 600‑protected)
echo "my‑strong‑vault‑pass" > .vault_pass.txt
chmod 600 .vault_pass.txt

# 2️⃣ Create the encrypted vault that stores the key
ansible-vault create vault.yml
```

When the editor opens, type **only** the following YAML, then save & quit:

```yaml
ngc_api_key: YOUR_NGC_API_KEY_GOES_HERE
```

> **Never** commit `vault.yml` or the plain key to a public repo. The vault file is encrypted; only someone with the password can decrypt it.

---

## 5. The **nvidia_pair** role  

#### `roles/nvidia_pair/tasks/main.yml`

```yaml
---
- name: Install Docker & NVIDIA container toolkit (Debian/Ubuntu)
  apt:
    name: "{{ docker_packages }}"
    state: present
    update_cache: yes
  become: true
  when: ansible_os_family == "Debian"

- name: Ensure Docker service is started & enabled
  systemd:
    name: docker
    state: started
    enabled: true
  become: true

- name: Write /etc/docker/daemon.json with NVIDIA runtime
  copy:
    dest: /etc/docker/daemon.json
    content: |
      {
        "default-runtime": "{{ docker_daemon_options.default-runtime }}",
        "runtimes": {
          "nvidia": {
            "path": "{{ docker_daemon_options.runtimes.nvidia.path }}",
            "runtimeArgs": []
          }
        }
      }
    mode: '0644'
  become: true
  notify: Restart Docker

- name: Log in to NGC registry
  community.docker.docker_login:
    registry_url: nvcr.io
    username: '$oauthtoken'
    password: "{{ ngc_api_key }}"
  become: true

- name: Pull the Pair container image
  community.docker.docker_image:
    name: "{{ pair_image }}"
    source: pull
  become: true

- name: Deploy pair.env (contains API key & port)
  template:
    src: pair.env.j2
    dest: /etc/pair.env
    mode: '0600'
  become: true

- name: Deploy systemd unit for the Pair container
  template:
    src: pair.service.j2
    dest: /etc/systemd/system/{{ pair_service_name }}.service
    mode: '0644'
  become: true
  notify: Reload systemd

- name: Enable & start the Pair service
  systemd:
    name: "{{ pair_service_name }}.service"
    enabled: true
    state: started
  become: true

# -----------------------------------------------------------------
# Handlers (run only when the notifying task reports a change)
# -----------------------------------------------------------------
- name: Restart Docker
  systemd:
    name: docker
    state: restarted
  become: true

- name: Reload systemd
  systemd:
    daemon_reload: true
  become: true
```

#### `roles/nvidia_pair/templates/pair.env.j2`

```jinja
# Auto‑generated – do NOT edit manually
NGC_API_KEY={{ ngc_api_key }}
PAIR_PORT={{ pair_port }}
```

#### `roles/nvidia_pair/templates/pair.service.j2`

```jinja
[Unit]
Description=NVIDIA AI Pair container
After=network.target docker.service
Requires=docker.service

[Service]
Restart=always
ExecStartPre=-/usr/bin/docker rm -f {{ pair_container_name }}
ExecStart=/usr/bin/docker run --rm \
  --gpus all \
  --name {{ pair_container_name }} \
  --env-file /etc/pair.env \
  -p {{ pair_port }}:8888 \
  {{ pair_image }}
ExecStop=/usr/bin/docker stop {{ pair_container_name }}

[Install]
WantedBy=multi-user.target
```

*Why a systemd unit?*  
- Guarantees the container restarts after a reboot.  
- Gives you standard `systemctl status nvidia-pair` diagnostics.  
- Keeps the host’s processes tidy (no dangling `docker run … &` commands).

---

## 6. Top‑level **playbook** – `site.yml`

```yaml
---
- name: Deploy NVIDIA AI Pair on every cluster node
  hosts: all_nodes
  become: true
  gather_facts: true

  roles:
    - nvidia_pair
```

---

## 7. Run the deployment (one command)

```bash
cd pair-ansible
ansible-playbook site.yml --diff
```

You will see a concise summary, e.g.:

```
PLAY RECAP *********************************************************************
white-node1                 : ok=14   changed=5    unreachable=0    failed=0
white-node2                 : ok=14   changed=5    unreachable=0    failed=0
spark-node1                 : ok=14   changed=5    unreachable=0    failed=0
spark-node2                 : ok=14   changed=5    unreachable=0    failed=0
```

**All nodes now run a Docker container called `nvidia-pair` exposing the UI on port 8888.**  
Open a browser on your Mac:

```
http://white-node1:8888
http://spark-node2:8888
```

The first login uses the default `admin / admin` credentials (change them from inside the container if you wish).

---

## 8. Quick‑and‑dirty alternative (single‑line Bash loop)

If you need a **one‑off** test and don’t want to maintain an Ansible repo, the following Bash snippet does the same thing:

```bash
TARGETS="white-node1 white-node2 spark-node1 spark-node2"
NGC_KEY="YOUR_NGC_API_KEY"
PAIR_PORT=8888
SSH_USER="USER"
SSH_KEY="~/.ssh/id_ed25519"

for h in $TARGETS; do
  echo "=== Deploying to $h ==="
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "sudo apt-get update && sudo apt-get install -y docker.io nvidia-container-toolkit"
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "echo '{\"default-runtime\":\"nvidia\",\"runtimes\":{\"nvidia\":{\"path\":\"/usr/bin/nvidia-container-runtime\",\"runtimeArgs\":[]}}}' | sudo tee /etc/docker/daemon.json"
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "sudo systemctl restart docker"
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "docker login nvcr.io -u \$oauthtoken -p $NGC_KEY"
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "docker pull nvcr.io/nvidia/pair:latest"
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "docker rm -f nvidia-pair || true"
  ssh -i "$SSH_KEY" "${SSH_USER}@${h}" "docker run -d --gpus all --name nvidia-pair -e NGC_API_KEY=$NGC_KEY -p $PAIR_PORT:8888 nvcr.io/nvidia/pair:latest"
  echo "✅ $h ready – UI at http://$h:$PAIR_PORT"
done
```

*Pros*: runs in seconds, no extra tools.  
*Cons*: not idempotent, hard to maintain, no secret‑management, no upgrade path.

---

## 9. Best‑practice checklist (what to verify after the playbook)

| ✅ What to check | How to verify |
|------------------|---------------|
| Docker daemon is running | `ansible all_nodes -m shell -a "systemctl is-active docker"` |
| Pair container is alive | `ansible all_nodes -m shell -a "docker ps --filter name=nvidia-pair"` |
| GPU visibility inside the container | `ansible all_nodes -m shell -a "docker exec nvidia-pair nvidia-smi"` |
| UI reachable from Mac | Open `http://<node>:8888` in a browser; you should see the Pair login page. |
| No plain‑text API key on the host | `ansible all_nodes -m shell -a "grep -R YOUR_NGC_API_KEY /etc" -o` should return nothing. |

If any check fails, the relevant `ansible -m shell` command will give you the exact error message for quick troubleshooting.

---

## 10. Upgrading / re‑deploying later

*Pin a tag* in `group_vars/all.yml` (e.g., `pair_image: nvcr.io/nvidia/pair:1.3.0`).  
When NVIDIA releases a newer image:

```bash
# Change the tag in group_vars/all.yml (or just leave it as :latest)
ansible-playbook site.yml   # re‑runs the pull & restarts the service
```

If you only want to pull a newer image without touching any other task, add a **tag** to the `docker_image` task (see the “pull_image” snippet in the previous answer) and run:

```bash
ansible-playbook site.yml --tags pull_image
```

---

## 11. Optional: a single front‑end address

If you don’t want to remember multiple hostnames, spin up a tiny **HAProxy** or **NGINX** reverse‑proxy on a bastion node (or on your Mac via SSH tunnel) that forwards `http://pair‑gateway:8888` to the first healthy node in the cluster.  

Example **SSH tunnel** (no extra software required):

```bash
ssh -L 8888:white-node1:8888 USER@white-node1 -N
# Now open http://localhost:8888 on your Mac – it tunnels to white‑node1.
```

You can script the tunnel to pick the node with the lowest latency, or use `autossh` for a persistent tunnel.

---

## 12. TL;DR – “What to copy‑paste”

1. Install Ansible & set up password‑less SSH.  
2. Create the directory layout shown above (or clone the repo if you prefer).  
3. Store the NGC API key in `vault.yml` (encrypted with a vault‑password file).  
4. Fill `inventory.ini` with your node hostnames/IPs.  
5. Run:

```bash
cd pair-ansible
ansible-playbook site.yml --diff
```

6. Open `http://<node>:8888` from your Mac – Pair is ready.  

That is the **most reliable, repeatable, and secure** way to install NVIDIA AI Pair across the *white* and *spark* clusters while keeping the UI accessible from your desktop. Happy experimenting!
