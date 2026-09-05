# Chameleon Cloud – Unified Environment Configuration

This file describes a single YAML configuration that can be used by all of the
example workflows (python‑chi, OpenStack CLI, Libcloud, and openstacksdk).  
It stores **only data** – no secrets are hard‑coded in any script.  

## 1. YAML file layout (`chameleon_env.yaml`)

```yaml
# ---------------------------------------------------------
# Cloud definition – compatible with OpenStack `clouds.yaml`
# ---------------------------------------------------------
clouds:
  chameleon:
    auth:
      auth_url: https://keystone.tacc.chameleoncloud.org:5000/v3
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
      project_name: YOUR_PROJECT
      user_domain_name: Default
      project_domain_name: Default
    region_name: KVM@TACC
    interface: public
    identity_api_version: 3

# ---------------------------------------------------------
# Runtime parameters – values that change between runs
# ---------------------------------------------------------
runtime:
  project_name: YOUR_PROJECT            # billed project
  site_name: KVM@TACC
  ssh_key_name: my-ssh-key
  network_name: sharednet1
  image_name: CC-Ubuntu-22.04
  flavor_name: m1.small
  server_name: my-kvm-vm
  security_groups: [default]
  floating_network: ext-net

# ---------------------------------------------------------
# Optional reservation block – used when a reservation is required
# ---------------------------------------------------------
reservation:
  name: demo-reservation
  start_offset_minutes: 1               # start = now + offset
  duration: 1h                          # ISO‑8601 duration string
  lease_name: my-lease                  # optional lease for exclusive nodes
```

* **`clouds`** – follows the standard OpenStack `clouds.yaml` format, so any
  client that reads `clouds.yaml` (python‑chi, openstacksdk, CLI, etc.) will work
  without modification.
* **`runtime`** – holds parameters that differ per execution: image, flavor,
  network, key pair, security group, floating network, etc.
* **`reservation`** – minimal fields needed to create a Chameleon reservation
  (name, start offset, duration, optional lease).

!!! Warning "Security note"
    Keep this file private (`chmod 600 /.config/chameleon/env.yaml`) and add it to `.gitignore` so it never gets committed.
    Also place it in a directory other then your code such as 
    `~/.config/chameleon/env.yaml`

## 2. Loader module (`config_loader.py`)

```python
"""
Load `chameleon_env.yaml`, expose its values as environment variables,
and return the parsed dictionary for the caller.
"""

import os
import yaml
import logging
from pathlib import Path

log = logging.getLogger(__name__)

def load_configuration(path: str = "~/.config/chameleon/chameleon_env.yaml"):
    """Read the YAML file, set OS_… vars and return the full config."""
    cfg_path = Path(path).expanduser().resolve()
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")

    with cfg_path.open("rt") as f:
        cfg = yaml.safe_load(f) or {}

    # ----- inject the cloud authentication values as OS_… vars -----
    cloud = cfg.get("clouds", {}).get("chameleon", {})
    auth = cloud.get("auth", {})
    for key, value in auth.items():
        env_name = f"OS_{key.upper()}"
        os.environ[env_name] = str(value)
        log.debug("Set %s from YAML", env_name)

    # ----- expose any extra env vars the user may have added -----
    for key, value in cfg.get("env", {}).items():
        if os.getenv(key) is None:
            os.environ[key] = str(value)

    return cfg
```

* The loader reads the YAML file, writes the required `OS_…` variables so that
  any OpenStack‑compatible SDK picks up the credentials automatically, and returns
  the entire configuration dictionary for the script to use.

## 3. Using the configuration in the various examples

All scripts should start with:

```python
from config_loader import load_configuration
cfg = load_configuration()   # loads default location and sets OS_… vars
rt = cfg["runtime"]
```

Then use `rt["..."]` for image, flavor, network, key name, etc.  
The same approach works for:

* **python‑chi** – see `launch_kvm_vm.py` in the original guide.
* **OpenStack CLI** – export the variables (or source a small helper that runs the loader).
* **Libcloud** – read credentials from `os.getenv("OS_USERNAME")`, etc.
* **openstacksdk** – call `openstack.connect(cloud="chameleon")` after the loader has written the `clouds.yaml` file if needed.

## 4. Reservation support

If the `reservation` block is present, the script can create a reservation or
lease before launching the VM. Example (python‑chi):

```python
if cfg.get("reservation"):
    r = cfg["reservation"]
    from datetime import datetime, timedelta
    start = (datetime.utcnow() + timedelta(minutes=r["start_offset_minutes"])).isoformat() + "Z"

    lease_id = None
    if r.get("lease_name"):
        lease_id = lease.create_lease(
            name=r["lease_name"],
            start=start,
            end=(datetime.fromisoformat(start.rstrip("Z")) + timedelta(hours=1)).isoformat() + "Z",
            project=rt["project_name"],
        )

    reservation_id = lease.create_reservation(
        name=r["name"],
        start=start,
        end=r["duration"],
        lease_id=lease_id,
        project=rt["project_name"],
        site=rt["site_name"],
    )
    print(f"Reservation created: {reservation_id}")
```

The same values can be interpolated into the OpenStack CLI `openstack reservation
create …` command.

## 5. Checklist for a uniform workflow

| Step | Action |
|------|--------|
| 1 | Place the single `chameleon_env.yaml` (as shown above) under `~/.config/chameleon/`. |
| 2 | Protect the file: `chmod 600 ~/.config/chameleon/chameleon_env.yaml`. |
| 3 | Add `config_loader.py` to every repository containing a script. |
| 4 | In every script, call `load_configuration()` **before** importing any OpenStack/Chi SDK. |
| 5 | Use `cfg["runtime"]` for all mutable parameters (image, flavor, network, etc.). |
| 6 | If a reservation is needed, read `cfg["reservation"]` and invoke the appropriate API/CLI. |
| 7 | Never hard‑code passwords, tokens, or project IDs in source code. |
| 8 | List the YAML file in `.gitignore` to avoid accidental commits. |

---

*This markdown file provides the complete description of the unified
environment configuration that can be used across all the examples.*

&&&&&

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
pip install "python-chi>=0.7" "pyyaml>=6.0"
pipx install python-openstackclient
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