
## Virtual Machine with the `python‑chi`

The workflow is the same as the original guide, but **all mutable values and credentials are stored in a YAML configuration file** (or supplied via environment variables). No passwords, tokens, or project identifiers are hard‑coded in the Python source.

---  

## 1. Configuration file.

Place the configuration file in `~/.config/chameleon/chameleon_config.yaml`.

All values that may change between runs or environments are placed in the `runtime` section. The `cloud` section contains the authentication data that the OpenStack SDK expects as `OS_…` environment variables.


!!! warning
    Do <u>**NOT**</u> commit this file to a public repository.    Restrict access to the owner only:
    ```bash
    chmod 600 ~/.config/chameleon/chameleon_config.yaml
    ```
--


```yaml
cloud:
  name:                 chameleon            # identifier used by the SDK
  auth_url:             https://keystone.tacc.chameleoncloud.org:5000/v3
  username:             YOUR_USERNAME
  password:             YOUR_PASSWORD
  project_name:         YOUR_PROJECT
  user_domain_name:     Default
  project_domain_name:  Default
  region_name:          KVM@TACC
  interface:            public
  identity_api_version: 3

runtime:
  project_name:         YOUR_PROJECT          # project that will be billed
  site_name:            KVM@TACC
  ssh_key_name:         my-ssh-key
  network_name:         sharednet1            # existing private network
  image_name:           CC-Ubuntu-22.04
  flavor_name:          m1.small
  server_name:          my-kvm-vm
  security_groups:      [default]             # list – add more if required
  floating_network:     ext-net               # name of the external network
```

---  

## 2. Install the required Python packages  

```bash
pip install "python-chi>=0.7" "pyyaml>=6.0" "python-openstackclient>=6.0"
```

!!! tip
    If you prefer to load variables from a `.env` file, also install `python-dotenv`.

---  

## 3. Helper module – `config_loader.py`

Utility to load the Chameleon configuration and expose `OS_… variables`.

```python
from pathlib import Path
import yaml
import os

DEFAULT_CFG_PATH = Path.home() / ".config" / "chameleon" / "chameleon_config.yaml"


def load_config(path: Path = DEFAULT_CFG_PATH) -> dict:
    """Read the YAML config and return a plain dict.

    The function also populates the OS_… environment variables required by the
    OpenStack SDK before any SDK import occurs.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("rt") as f:
        cfg = yaml.safe_load(f)

    cloud = cfg.get("cloud", {})
    for key, value in cloud.items():
        env_var = f"OS_{key.upper()}"
        os.environ[env_var] = str(value)

    return cfg
```

*Calling `load_config()` sets the environment variables (`OS_AUTH_URL`, `OS_USERNAME`, …) that the `chi`/OpenStack SDK reads automatically.*

---  

## 4. Main script – `launch_kvm_vm.py`

Launch a VM using python‑chi, with all secrets read from a YAML file. The script has the following key characteristics.

| What the script does | How it avoids hard‑coded secrets |
|----------------------|----------------------------------|
| Reads passwords, usernames, project IDs | All values are loaded from `chameleon_config.yaml`; the helper writes them to `OS_…` variables for the SDK |
| Chooses project/site, launches VM, attaches floating IP | No literal strings like `"my-project"` or `"my-ssh-key"` appear in the source – they come from the config |
| Optional lease creation | Lease parameters can also be added under a `lease` key in the YAML file if required |


```python
#!/usr/bin/env python3

import sys
from config_loader import load_config

# ----------------------------------------------------------------------
# 1️.  Load configuration (sets OS_… env vars for the SDK)
# ----------------------------------------------------------------------
try:
    cfg = load_config()                     # uses the default location
except Exception as exc:
    sys.stderr.write(f"Configuration error: {exc}\n")
    sys.exit(1)

# ----------------------------------------------------------------------
# 2️. Import the chi SDK *after* the environment is prepared
# ----------------------------------------------------------------------
import chi
from chi import lease, server, network, context

# ----------------------------------------------------------------------
# 3️. Runtime parameters – taken from the YAML file for easy tweaking
# ----------------------------------------------------------------------
rt = cfg["runtime"]
PROJECT_NAME = rt["project_name"]
SITE_NAME    = rt["site_name"]
KEY_NAME     = rt["ssh_key_name"]
NET_NAME     = rt["network_name"]
IMG_NAME     = rt["image_name"]
FLV_NAME     = rt["flavor_name"]
SRV_NAME     = rt["server_name"]
SEC_GROUPS   = rt["security_groups"]
FLOAT_NET    = rt["floating_network"]

# ----------------------------------------------------------------------
# 4️. Choose project and site (billing context)
# ----------------------------------------------------------------------
context.choose_project(PROJECT_NAME)
context.choose_site(SITE_NAME)

# ----------------------------------------------------------------------
# 5️. (Optional) Create a lease – uncomment if exclusive resources are needed
# ----------------------------------------------------------------------
# lease_id = lease.create_lease(
#     name="my-lease",
#     start="2024-09-01T00:00:00Z",
#     end="2024-09-07T00:00:00Z",
#     project=PROJECT_NAME,
# )
# print(f"Lease created: {lease_id}")

# ----------------------------------------------------------------------
# 6️. Create the VM
# ----------------------------------------------------------------------
instance = server.create_server(
    name=SRV_NAME,
    image=IMG_NAME,
    flavor=FLV_NAME,
    network=NET_NAME,
    key_name=KEY_NAME,
    security_groups=SEC_GROUPS,
    # lease_id=lease_id,          # uncomment when a lease is used
)

print(f"Server '{SRV_NAME}' launched – ID: {instance.id}")

# ----------------------------------------------------------------------
# 7️. Allocate a floating IP and attach it
# ----------------------------------------------------------------------
floating_ip = network.create_floating_ip(FLOAT_NET)
network.associate_floating_ip(instance.id, floating_ip.ip)

print("\nFloating IP attached:")
print(f"    {floating_ip.ip}")

# ----------------------------------------------------------------------
# 8️. Show the SSH command the user can run
# ----------------------------------------------------------------------
ssh_cmd = f"ssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}"
print("\nConnect to the VM with:")
print(f"    {ssh_cmd}")
```

---  

## 5. Alternative credential sources  

| Source | When to use | How to enable |
|--------|-------------|----------------|
| **X.509 proxy** (default for many Chameleon users) | You already have a VOMS proxy | Export `X509_USER_PROXY=$HOME/.globus/proxy` before running the script. The SDK will pick it up automatically. |
| **`clouds.yaml`** (OpenStack native format) | You prefer the OpenStack SDK’s built‑in config handling | Create `~/.config/openstack/clouds.yaml` with the same `cloud` block as in the YAML file; the SDK loads it automatically. |
| **`keyring`** (CI pipelines) | You want to avoid storing secrets on disk | Store credentials with `keyring set chameleon username`, etc., and modify `config_loader.py` to read them from `keyring`. |
| **`.env` file** | Quick local testing | Install `python-dotenv` and add `from dotenv import load_dotenv; load_dotenv()` at the top of `config_loader.py`. Keep the `.env` file out of version control. |

**Security reminder** – Never commit the configuration file (or any file containing passwords) to a public repository. Add the following to `.gitignore`:

```.gitignore
# Sensitive configuration
*.yaml
*.env
```

---  

## 6. Cleanup and common pitfalls  

| Symptom | Likely cause | Remedy |
|---------|--------------|--------|
| `Authentication failed` | Incorrect username/password in the YAML file | Verify the values, then `chmod 600` the file to ensure only you can read it. |
| `No floating IPs left` | All public IPs are already allocated | Release unused floating IPs (`openstack floating ip delete <IP>`) or request additional IPs from the site administrator. |
| `Network not found` | The name in `network_name` does not exist or is not shared with the project | List networks with `network.list_networks()` and update the config accordingly. |
| `Instance stays in BUILD` | Insufficient quota for the selected flavor | Check quota with `openstack quota show` and choose a smaller flavor, or request a quota increase. |
| `Key not found` | The SSH key name does not exist in the project | Upload the public key via Horizon **Compute → Key Pairs** or use `chi.keypair.upload()` before launching. |
| `Credential leakage` | Passwords appear in shell history or logs | Prefer environment variables, `clouds.yaml`, or a secrets manager; never echo passwords in scripts. |

---  

## 7. Minimal copy‑paste version (four logical blocks)  

If you prefer a notebook or want to keep everything in separate cells, the same logic can be split into four sections. Each block assumes that `config_loader.py` is available on the Python path.

```markdown
### 1️. Load configuration and choose context
```python
from config_loader import load_config
cfg = load_config()                     # populates OS_… env vars
import chi
from chi import lease, server, network, context

rt = cfg["runtime"]
context.choose_project(rt["project_name"])
context.choose_site(rt["site_name"])
```

### 2️. Define key and network (no hard‑coded values)
```python
KEY_NAME = rt["ssh_key_name"]
NET_NAME = rt["network_name"]
```

### 3️. Launch the VM
```python
instance = server.create_server(
    name=rt["server_name"],
    image=rt["image_name"],
    flavor=rt["flavor_name"],
    network=NET_NAME,
    key_name=KEY_NAME,
    security_groups=rt["security_groups"],
)
print(f"Server '{rt['server_name']}' launched – ID: {instance.id}")
```

### 4️. Allocate a floating IP and show the SSH command
```python
floating_ip = network.create_floating_ip(rt["floating_network"])
network.associate_floating_ip(instance.id, floating_ip.ip)

print("\nFloating IP attached:")
print(f"    {floating_ip.ip}")

ssh_cmd = f"ssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}"
print("\nConnect to the VM with:")
print(f"    {ssh_cmd}")
```
```

---  

## 8. Summary  

* All mutable values—including credentials—are stored in a **protected YAML file** (`~/.config/chameleon/chameleon_config.yaml`).  
* The `config_loader` module injects the required `OS_…` environment variables **before** any `chi` import, allowing the SDK to operate exactly as documented while keeping secrets out of source code.  
* The main script (`launch_kvm_vm.py`) is a single, reusable file that can be version‑controlled safely.  
* Multiple credential back‑ends (X.509 proxy, `clouds.yaml`, `keyring`, `.env`) are supported for flexibility.  

You now have a clean, secure, and maintainable workflow for provisioning VMs from Python. Happy scripting!