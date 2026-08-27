# Managing Cloud Parameters and Environment Variables with a YAML File  

This guide shows how to store all required OpenStack/Chameleon parameters (cloud authentication, project settings, and any additional environment variables) in a single **YAML** file and how to load that file from Python so the `python‑chi` (or OpenStack) SDK can use the values automatically.

---  

## 1. Why use a YAML file?  

* **Single source of truth** – All credentials, region, and optional parameters live in one place.  
* **Version‑controlled** – Keep the file in a private repository (or encrypted store) and track changes.  
* **Easily reusable** – Multiple scripts or notebooks can read the same configuration without duplicating code.  
* **Separation of code and secrets** – The script contains no hard‑coded passwords; the YAML file can be protected with file‑system permissions.

---  

## 2. Recommended file layout  

Create a file called **`chameleon_env.yaml`** (the name is arbitrary; you just need to know it when you read it).  
The file contains two top‑level sections:

| Section | Purpose |
|---------|---------|
| `clouds` | The same structure used by OpenStack’s `clouds.yaml`. This is what `python‑chi` and `openstacksdk` read automatically. |
| `env`    | Any additional environment variables you want to expose to your script (e.g., an API key for a secondary service, a DEBUG flag, etc.). |

### Example `chameleon_env.yaml`

```yaml
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

env:
  # Optional extra variables
  DEBUG: "true"
  ANOTHER_SERVICE_TOKEN: abcdef1234567890
```

> **Important** – Do **not** commit this file to a public repository.  
> Set file permissions so only you (or the service account) can read it:

```bash
chmod 600 chameleon_env.yaml
```

---  

## 3. Loading the YAML file from Python  

You can use the standard `yaml` package (PyYAML) or the more feature‑rich `ruamel.yaml`. The snippet below uses PyYAML because it is lightweight and widely available.

### Install the dependency

```bash
pip install pyyaml
```

### Helper module – `config_loader.py`

```python
"""
Utility to load a YAML file that contains OpenStack cloud definitions
and additional environment variables.
"""

import os
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_configuration(yaml_path: str = "chameleon_env.yaml"):
    """
    Load the YAML configuration file.

    Returns:
        dict: The full dictionary parsed from the YAML file.
    """
    yaml_file = Path(yaml_path).expanduser().resolve()
    if not yaml_file.is_file():
        raise FileNotFoundError(f"Configuration file not found: {yaml_file}")

    with yaml_file.open("r") as f:
        cfg = yaml.safe_load(f) or {}

    # Export any entries under `env` as real OS environment variables.
    env_vars = cfg.get("env", {})
    for key, value in env_vars.items():
        # Only set the variable if it is not already defined in the environment.
        if os.getenv(key) is None:
            os.environ[key] = str(value)
            logger.debug(f"Set environment variable {key} from YAML")
        else:
            logger.debug(f"Environment variable {key} already defined; leaving untouched")

    return cfg
```

### Using the loader in your workflow script

```python
# launch_vm.py
import logging
import os
from chi import context, server, network, lease

# ----------------------------------------------------------------------
# 0. Load configuration and expose any extra env vars
# ----------------------------------------------------------------------
from config_loader import load_configuration

cfg = load_configuration("chameleon_env.yaml")

# ----------------------------------------------------------------------
# 1. Choose project and site – the SDK will pick up the cloud definition
#    from the standard location (~/.config/openstack/clouds.yaml) if present.
#    To make it use our in‑memory dict we temporarily write a clouds.yaml
#    file to the default location.
# ----------------------------------------------------------------------
import json
clouds_path = os.path.expanduser("~/.config/openstack/clouds.yaml")
os.makedirs(os.path.dirname(clouds_path), exist_ok=True)

with open(clouds_path, "w") as f:
    yaml.safe_dump(cfg["clouds"], f)

# Now the chi SDK can read the cloud definition automatically.
PROJECT_NAME = cfg["clouds"]["chameleon"]["auth"]["project_name"]
context.choose_project(PROJECT_NAME)
context.choose_site("KVM@TACC")

# ----------------------------------------------------------------------
# 2‑4. Continue with the same steps as in the main tutorial
# ----------------------------------------------------------------------
key_name = "my-ssh-key"
net_name = "sharednet1"

server_name = "my-kvm-vm"
image_name = "CC-Ubuntu-24.04"
flavor_name = "m1.small"

instance = server.create_server(
    name=server_name,
    image=image_name,
    flavor=flavor_name,
    network=net_name,
    key_name=key_name,
    security_groups=["default"],
)

print(f"Server '{server_name}' launching (ID: {instance.id})")

floating_ip = network.create_floating_ip("ext-net")
network.associate_floating_ip(instance.id, floating_ip.ip)

print(f"ssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}")
```

#### What the script does  

1. **Loads** `chameleon_env.yaml`.  
2. **Injects** any variables under the `env` section into `os.environ`.  
3. **Writes** the `clouds` section to the default `clouds.yaml` location so the OpenStack/chi SDK can locate it without additional arguments.  
4. Proceeds with the normal VM‑creation workflow.

> If you already have a `clouds.yaml` you can skip step 3 and simply set `OS_CLOUD=chameleon` in your environment, letting the SDK pick the cloud name from the loaded dictionary.

---  

## 4. Alternative: Read the YAML directly without creating a temporary file  

If you prefer not to write a file, you can pass the cloud dictionary directly to the OpenStack `Connection` object and then hand that connection to the chi SDK (the chi SDK accepts an existing session). Example:

```python
import openstack
from chi import context, server, network

cfg = load_configuration("chameleon_env.yaml")
cloud_cfg = cfg["clouds"]["chameleon"]

# Create an explicit OpenStack connection
conn = openstack.connect(**cloud_cfg["auth"],
                         region_name=cloud_cfg["region_name"],
                         interface=cloud_cfg["interface"],
                         identity_api_version=cloud_cfg["identity_api_version"])

# Give chi the connection (chi internally uses openstacksdk sessions)
context.set_connection(conn)          # hypothetical helper; actual API may vary
```

Consult the `python‑chi` documentation for the exact method to supply an existing OpenStack session; the principle remains the same.

---  

## 5. Security best practices  

| Recommendation | Why it matters |
|----------------|----------------|
| **Location** - `~/.config/chameleon_env.yaml` | Do not put the yaml file in your currednt working directory so  you do not check it in with git. |
| **File permissions** – `chmod 600 ~/.config/chameleon_env.yaml` | Prevent other users on the same host from reading passwords. |
| **Never hard‑code** passwords in source code | Reduces the risk of accidental commits to public repos. |
| **Use a secret manager** (AWS Secrets Manager, HashiCorp Vault, etc.) for production | Allows rotation without editing files. |
| **Separate values** – keep only one set of credentials per environment (dev / test / prod) | Avoids mixing resources and simplifies audits. |
| **Delete the temporary `clouds.yaml`** after the script finishes (optional) | Reduces lingering credential files. |
| **Validate the YAML** – catch missing keys early | Prevents runtime authentication failures. |

---  

## 6. Quick reference checklist  

1. Create `chameleon_env.yaml` with `clouds` and optional `env` sections.  
2. Secure the file (`chmod 600`).  
3. Install PyYAML (`pip install pyyaml`).  
4. Add `config_loader.py` (or embed the `load_configuration` function) to your project.  
5. In your script:  
   * Call `load_configuration()` early.  
   * Export extra env vars (handled automatically).  
   * Write the `clouds` dict to the default `clouds.yaml` *or* create an OpenStack connection directly.  
6. Run the script – the SDK will pick up authentication details automatically.  

