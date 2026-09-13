
Below is a **complete, ready‑to‑run Ansible workflow** that will:

1. **Install Docker (and the NVIDIA container runtime) on every node** in the *white* and *spark* clusters.  
2. **Pull the private NVIDIA AI Pair image from NGC** using your API key (kept safely with Ansible Vault).  
3. **Run the Pair container as a systemd service** so it survives reboots and can be upgraded with a single play‑book run.  
4. **Expose the UI on the same port on every host** (default 8888) so you can open `http://<node>:8888` from your Mac.

The whole thing lives in a **single Git‑compatible directory** that you can version‑control, clone on any new laptop, or hand to a teammate.  

---  

## 1. Prerequisites on the **control machine** (your Mac)

| Item | Install command |
|------|-----------------|
| **Python 3** (built‑in on macOS ≥ 12) | — |
| **pip** (if missing) | `python3 -m ensurepip --upgrade` |
| **Ansible ≥ 2.14** | `python3 -m pip install --user ansible` |
| **Ansible collections** (docker, amazon‑aws, etc.) | `ansible-galaxy collection install community.docker` |
| **SSH key** that can log in to every node without a password | `ssh-keygen -t ed25519 -C "your‑email"` → copy `~/.ssh/id_ed25519.pub` to `~/.ssh/authorized_keys` on each node. |
| **NGC API key** (private) | Grab it from <https://ngc.nvidia.com> → **Setup → API Key**. Keep it handy – we will store it in an encrypted vault file. |

> **Tip** – Add `~/.local/bin` (or `$HOME/Library/Python/3.x/bin`) to your `$PATH` so the `ansible` executable is found.

```bash
# Verify the install
ansible --version
# Example output: ansible 2.14.5 Python 3.11.9
```

---  

## 2. Directory layout

```
pair‑ansible/
├─ ansible.cfg                # configuration for this project
├─ inventory.ini              # hosts and groups
├─ group_vars/
│  ├─ all.yml                 # variables common to every host
│  ├─ white.yml               # optional per‑group overrides
│  └─ spark.yml
├─ host_vars/                 # (empty for now – you can add per‑host vars)
├─ vault.yml                  # encrypted file that holds the NGC API key
├─ roles/
│  └─ nvidia_pair/
│     ├─ tasks/
│     │   └─ main.yml
│     ├─ templates/
│     │   └─ pair.service.j2
│     └─ files/
│         └─ pair.env.j2
└─ site.yml                    # top‑level playbook
```

You can create the skeleton with the following one‑liner (run from the directory where you want the repo):

```bash
mkdir -p pair-ansible/{group_vars,host_vars,roles/nvidia_pair/{tasks,templates,files}} && \
touch pair-ansible/{ansible.cfg,inventory.ini,group_vars/all.yml,vault.yml,site.yml}
```

---  

## 3. `ansible.cfg` – make life easier

```ini
[defaults]
inventory = inventory.ini
remote_user = <YOUR_SSH_USER>          # e.g. ubuntu, centos, ec2-user …
host_key_checking = False
retry_files_enabled = False
vault_password_file = .vault_pass.txt   # see step 5
interpreter_python = auto_silent

[ssh_connection]
scp_if_ssh = True
```

*Replace `<YOUR_SSH_USER>` with the login name that exists on every cluster node.*

If you **don’t want to store the vault password in a file**, delete the `vault_password_file` line – Ansible will then prompt you each time.

---  

## 4. Inventory – “white” and “spark”

Edit `inventory.ini` with the hostnames or IP addresses that your laptop can reach.

```ini
[white]
white-node1 ansible_host=10.0.1.11
white-node2 ansible_host=10.0.1.12
# add more white nodes here ...

[spark]
spark-node1 ansible_host=10.0.2.21
spark-node2 ansible_host=10.0.2.22
# add more spark nodes here ...

# optional: a group that contains *all* nodes (useful for ad‑hoc commands)
[all_nodes:children]
white
spark
```

If you prefer to use DNS names instead of IPs, just set `ansible_host=` to the FQDN.

---  

## 5. Secure the **NGC API key** with Ansible Vault  

1. **Create a vault password file** (only readable by you).  

```bash
# Inside the repo root:
echo "my‑strong‑vault‑pass" > .vault_pass.txt
chmod 600 .vault_pass.txt
```

2. **Create the encrypted vault file** that will store the key.

```bash
ansible-vault create vault.yml
```

The editor that pops up (by default `vim`) should contain **only** the following YAML:

```yaml
ngc_api_key: YOUR_NGC_API_KEY_GOES_HERE
```

Replace `YOUR_NGC_API_KEY_GOES_HERE` with the key you generated on NGC, **save & quit**. The file on disk is now encrypted.

> **Why Vault?**  
> The API key never appears in plain‑text in the repository, but the playbook can still read it at runtime (`{{ ngc_api_key }}`).

---  

## 6. Variables shared by all hosts (`group_vars/all.yml`)

```yaml
# ---------- Docker ----------
docker_packages:
  - docker.io
  - nvidia-container-toolkit   # pulls in the NVIDIA runtime

docker_daemon_options:
  # Ensure the NVIDIA runtime is listed first (NVIDIA recommends)
  default-runtime: nvidia
  runtimes:
    nvidia:
      path: /usr/bin/nvidia-container-runtime
      runtimeArgs: []

# ---------- Pair ----------
pair_image: nvcr.io/nvidia/pair:latest   # or pin a specific tag, e.g. nvcr.io/nvidia/pair:1.2.3
pair_port: 8888                           # UI port on the host
pair_container_name: nvidia-pair
pair_service_name: nvidia-pair
```

If you ever need a different port for a specific cluster, add a `pair_port` entry in `group_vars/white.yml` or `group_vars/spark.yml`.

---  

## 7. The **role** – `roles/nvidia_pair`

### 7.1 `tasks/main.yml`

```yaml
---
- name: Install required OS packages (Docker + NVIDIA runtime)
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

- name: Create /etc/docker/daemon.json with NVIDIA runtime
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

- name: Log in to NGC registry (once per host)
  community.docker.docker_login:
    registry_url: nvcr.io
    username: '$oauthtoken'               # special NGC username
    password: "{{ ngc_api_key }}"
  become: true

- name: Pull the Pair container image
  community.docker.docker_image:
    name: "{{ pair_image }}"
    source: pull
  become: true

- name: Deploy the environment file (pair.env)
  template:
    src: pair.env.j2
    dest: /etc/pair.env
    mode: '0600'
  become: true

- name: Deploy the systemd service unit for Pair
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
# Handlers (run only when the notified task changes)
# -----------------------------------------------------------------
- name: Restart Docker
  systemd:
    name: docker
    state: restarted
  become: true
  when: docker_daemon_options is defined

- name: Reload systemd
  systemd:
    daemon_reload: true
  become: true
```

### 7.2 `templates/pair.env.j2`

```jinja
# ------------------------------------------------------------------
# Auto‑generated by Ansible – do NOT edit manually
# ------------------------------------------------------------------
NGC_API_KEY={{ ngc_api_key }}
PAIR_PORT={{ pair_port }}
```

> The file lives at **/etc/pair.env** (protected with mode 0600). The container will read it via an environment file mount.

### 7.3 `templates/pair.service.j2`

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

*Explanation*  

* `ExecStartPre` removes a stale container (idempotent).  
* `--env-file /etc/pair.env` passes the API key **inside the container** without exposing it on the host command line.  
* `-p {{ pair_port }}:8888` publishes the UI on the same port for every host.  

---  

## 8. Top‑level playbook – `site.yml`

```yaml
---
- name: Deploy NVIDIA AI Pair on all cluster nodes
  hosts: all_nodes
  become: true
  gather_facts: true

  roles:
    - nvidia_pair
```

That’s it – the playbook just calls the role we defined.

---  

## 9. Run the deployment

```bash
# From the repository root:
ansible-playbook site.yml --diff
```

*What happens*  

1. Ansible connects via SSH to each host (using the SSH key you already configured).  
2. It installs Docker and the NVIDIA runtime (if they are missing).  
3. It creates `/etc/docker/daemon.json` with the NVIDIA runtime, restarts Docker.  
4. It logs in to `nvcr.io` using the vault‑protected API key.  
5. It pulls the **latest** `nvcr.io/nvidia/pair` image.  
6. It writes the sealed `pair.env` file and the systemd unit.  
7. It starts the Pair container as a **systemd‑managed service**.

After the run finishes you should see a short summary like:

```
PLAY RECAP *********************************************************************
white-node1                 : ok=12   changed=5    unreachable=0    failed=0
white-node2                 : ok=12   changed=5    unreachable=0    failed=0
spark-node1                 : ok=12   changed=5    unreachable=0    failed=0
spark-node2                 : ok=12   changed=5    unreachable=0    failed=0
```

---  

## 10. Verify from your Mac

```bash
# Simple check – list the running container on any node
ansible all_nodes -m shell -a "docker ps --filter name=nvidia-pair --format '{{{{.Names}}}} {{{{.Ports}}}}'" -o
```

Or open a browser:

```
http://white-node1:8888
http://spark-node2:8888
```

You should see the Pair UI login screen. The first login uses the default `admin/admin` credentials; you can change the password from inside the container later if you wish.

---  

## 11. Common troubleshooting checklist

| Symptom | Likely cause | Fix |
|--------|--------------|-----|
| **Cannot SSH** | SSH key not installed on the node, or firewall blocks port 22. | `ssh user@host` manually, fix key or open port. |
| **`docker: command not found`** | Docker package not installed (maybe wrong OS family). | Ensure the target OS is Debian/Ubuntu; modify the playbook for RHEL (`yum`/`dnf`). |
| **`nvidia-smi` not found inside container** | Host driver version too old for the Pair image. | Upgrade NVIDIA driver to ≥ 560 (or the version listed in Pair release notes). |
| **401 Unauthorized when pulling image** | Wrong NGC API key or not logged in. | Re‑run `ansible-vault edit vault.yml` to correct the key, then re‑run the playbook. |
| **Port 8888 already in use** | Another service (perhaps an older Pair container) still bound. | `docker rm -f nvidia-pair` on the host, then re‑run the playbook. |
| **Container crashes immediately** | Missing GPU driver, insufficient memory, or mismatched CUDA version. | Check `docker logs nvidia-pair` on the host for the exact error. |

You can get the logs from any node with an ad‑hoc command:

```bash
ansible all_nodes -m shell -a "docker logs nvidia-pair" -o
```

---  

## 12. Upgrading / redeploying later

When a new Pair version appears (or you simply want to force a fresh pull):

```bash
ansible-playbook site.yml --tags pull_image
```

Add a tag to the `docker_image` task in `roles/nvidia_pair/tasks/main.yml`:

```yaml
- name: Pull the Pair container image
  community.docker.docker_image:
    name: "{{ pair_image }}"
    source: pull
  become: true
  tags: pull_image
```

Now the playbook will only re‑pull the image when you run with `--tags pull_image`, leaving the rest of the host untouched.

If you need to **change the UI port** (say to 9090) just edit `group_vars/all.yml` (or a specific group’s file) and re‑run the whole playbook – the systemd unit will be regenerated and the service restarted automatically.

---  

## 13. Full‑copy‑paste starter (if you want everything generated automatically)

If you want to bootstrap the whole directory in one go, run the following script on your Mac **once** (adjust the `SSH_USER`, hosts, and NGC key as needed):

```bash
#!/usr/bin/env bash
set -euo pipefail
# --------------------------------------------------------------
# PARAMETERS – EDIT THESE
# --------------------------------------------------------------
SSH_USER="yoursshuser"

# Hosts (space‑separated). Use IPs or hostnames that resolve.
WHITE=("white-node1" "white-node2")
SPARK=("spark-node1" "spark-node2")

NGC_KEY="YOUR_NGC_API_KEY_HERE"
VAULT_PASS="my‑strong‑vault‑pass"
PAIR_PORT=8888
# --------------------------------------------------------------

BASE=$(pwd)/pair-ansible
mkdir -p "$BASE"/{group_vars,host_vars,roles/nvidia_pair/{tasks,templates,files}}
cat >"$BASE"/ansible.cfg <<EOF
[defaults]
inventory = inventory.ini
remote_user = $SSH_USER
host_key_checking = False
retry_files_enabled = False
vault_password_file = .vault_pass.txt
interpreter_python = auto_silent

[ssh_connection]
scp_if_ssh = True
EOF

cat >"$BASE"/inventory.ini <<EOF
[white]
$(printf "%s ansible_host=%s\n" "${WHITE[@]}" "$(dig +short ${WHITE[@]})")
[spark]
$(printf "%s ansible_host=%s\n" "${SPARK[@]}" "$(dig +short ${SPARK[@]})")
[all_nodes:children]
white
spark
EOF

cat >"$BASE"/group_vars/all.yml <<'EOF'
docker_packages:
  - docker.io
  - nvidia-container-toolkit
docker_daemon_options:
  default-runtime: nvidia
  runtimes:
    nvidia:
      path: /usr/bin/nvidia-container-runtime
      runtimeArgs: []

pair_image: nvcr.io/nvidia/pair:latest
pair_port: 8888
pair_container_name: nvidia-pair
pair_service_name: nvidia-pair
EOF

# Optional per‑group overrides – create empty files for now
touch "$BASE"/group_vars/white.yml "$BASE"/group_vars/spark.yml

cat >"$BASE"/roles/nvidia_pair/tasks/main.yml <<'EOF'
---
- name: Install required OS packages (Docker + NVIDIA runtime)
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

- name: Create /etc/docker/daemon.json with NVIDIA runtime
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

- name: Deploy the environment file (pair.env)
  template:
    src: pair.env.j2
    dest: /etc/pair.env
    mode: '0600'
  become: true

- name: Deploy the systemd service unit for Pair
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
# Handlers
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
EOF

cat >"$BASE"/roles/nvidia_pair/templates/pair.env.j2 <<'EOF'
# Auto‑generated – do NOT edit
NGC_API_KEY={{ ngc_api_key }}
PAIR_PORT={{ pair_port }}
EOF

cat >"$BASE"/roles/nvidia_pair/templates/pair.service.j2 <<'EOF'
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
EOF

cat >"$BASE"/site.yml <<'EOF'
---
- name: Deploy NVIDIA AI Pair on all cluster nodes
  hosts: all_nodes
  become: true
  gather_facts: true

  roles:
    - nvidia_pair
EOF

# Write vault password file
echo "$VAULT_PASS" > "$BASE"/.vault_pass.txt
chmod 600 "$BASE"/.vault_pass.txt

# Create the encrypted vault with the API key
printf "ngc_api_key: %s\n" "$NGC_KEY" > "$BASE"/tmp_vault.yml
ansible-vault encrypt "$BASE"/tmp_vault.yml --output "$BASE"/vault.yml --vault-pass-file "$BASE"/.vault_pass.txt
rm "$BASE"/tmp_vault.yml

echo "✅ Repository ready at $BASE"
echo "Next steps:"
echo "  1️⃣ cd $BASE"
echo "  2️⃣ ansible-playbook site.yml --diff"
EOF
```

Run the script, then `cd pair-ansible && ansible-playbook site.yml --diff`. All hosts will be brought up in minutes.

---  

## 14. TL;DR – What you needed to do

| Step | Command (run once) |
|------|--------------------|
| **Install Ansible** | `python3 -m pip install --user ansible && ansible-galaxy collection install community.docker` |
| **Create vault file** | `ansible-vault create vault.yml` (store `ngc_api_key`) |
| **Write inventory** | Edit `inventory.ini` with your node hostnames/IPs |
| **Put variables** | Edit `group_vars/all.yml` (ports, image…) |
| **Add the role** | Use the files in `roles/nvidia_pair/…` (tasks, templates) |
| **Run the playbook** | `ansible-playbook site.yml` |
| **Open UI** | `http://<node>:8888` from your Mac |

Once the playbook has run, the Pair container is **managed by systemd**, so a reboot of a node automatically restarts it. To roll out a new version, just run the same playbook again – Ansible will pull the latest image and restart the service.

That’s the full Ansible‑based, production‑ready way to **deploy NVIDIA AI Pair on every “white” and “spark” machine** and use it from your desktop Mac. Happy hacking!


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the purpose of `ansible-vault` in this workflow?"
    `ansible-vault` is used to encrypt sensitive data, such as the NGC API key. This allows the key to be stored securely in a version-controlled repository without exposing the secret in plain text.

??? question "Why is it better to use a `template` (e.g., `pair.service.j2`) instead of a static file for the systemd unit?"
    Templates allow the use of variables (like `{{ pair_port }}` or `{{ pair_image }}`). This makes the deployment flexible, as the same template can be used for different environments or updated globally by changing a single variable in `group_vars`.

??? question "What does `host_key_checking = False` in `ansible.cfg` do, and why might it be used in a lab environment?"
    It disables the prompt that asks the user to verify the SSH fingerprint of a new host. While not recommended for high-security production environments, it is very useful in lab settings where VMs are frequently destroyed and recreated with new fingerprints.

??? question "In the `site.yml` playbook, what does `gather_facts: true` accomplish?"
    It tells Ansible to run the "setup" module first, which collects system information (facts) from the target hosts (e.g., OS version, IP addresses, CPU architecture). These facts can then be used as variables in subsequent tasks.

??? question "Why is the AI Pair container managed by `systemd` rather than just being run with `docker run` manually?"
    Managing the container via `systemd` ensures that the service is automatically started upon boot, can be easily restarted if it crashes, and can be managed using standard Linux service commands (`systemctl start/stop/status`), making it "production-ready."
