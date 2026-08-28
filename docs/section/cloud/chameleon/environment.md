# Chameleon Cloud – Unified Environment Configuration

This document describes a single YAML configuration file that can be used by all
example workflows (python‑chi, OpenStack CLI, Libcloud, and openstacksdk).  
All secrets are stored only in the YAML file; no passwords or project IDs are
hard‑coded in any script.

## 1. YAML file layout (`env.yaml`)

The file must be placed in **`~/.config/chameleon/env.yaml`** (the leading `~`
expands to the user’s home directory).

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
  client that reads `clouds.yaml` will work unchanged.
* **`runtime`** – holds parameters that differ per execution (image, flavor,
  network, key pair, security group, floating network, etc.).
* **`reservation`** – minimal fields needed to create a Chameleon reservation
  (name, start offset, duration, optional lease).

!!! warning "Security note"

    Keep this file private:  
    ```bash
    chmod 600 ~/.config/chameleon/env.yaml
    ```  
    Add it to `.gitignore` so it never gets committed.

## 2. Loader module (`config_loader.py`)

All scripts should import this module *before* any OpenStack‑related SDK is
imported. The loader reads the YAML file, injects the required `OS_…` environment
variables, and returns the full configuration dictionary. It also exports
reservation fields as ordinary environment variables.

```python
"""
Load `env.yaml`, expose its values as environment variables,
and return the parsed dictionary for the caller.
"""

import os
import yaml
import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

def load_configuration(
    path: str = "~/.config/chameleon/env.yaml"
) -> dict:
    """
    Read the YAML file, set OS_… variables and return the full config.
    """
    cfg_path = Path(path).expanduser().resolve()
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {cfg_path}")

    with cfg_path.open("rt") as f:
        cfg = yaml.safe_load(f) or {}

    # ----- inject the cloud authentication values as OS_… variables -----
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

    # ----- export reservation fields (if present) -----
    reservation = cfg.get("reservation", {})
    if reservation:
        os.environ["RESERVATION_NAME"] = str(reservation.get("name", ""))
        os.environ["RESERVATION_OFFSET"] = str(reservation.get("start_offset_minutes", ""))
        os.environ["RESERVATION_DURATION"] = str(reservation.get("duration", ""))
        # optionally expose the whole block as JSON
        os.environ["RESERVATION_JSON"] = json.dumps(reservation)

    return cfg
```

The function mirrors the loader shown in the original `python‑chi` guide and
the generic loader from the “Managing Cloud Parameters” guide, but points to
the new `~/.config/chameleon/env.yaml` location and adds reservation exports.

## 3. Using the configuration in the different workflows

Every script includes the same two lines:

```python
from config_loader import load_configuration
cfg = load_configuration()   # loads the default location and sets OS_… vars
rt = cfg["runtime"]
```

The dictionary `rt` provides all mutable values (image, flavor, network, key
pair, etc.). Below are concise examples for each workflow.

### 3.1 python‑chi (`launch_kvm_vm.py`)

```python
#!/usr/bin/env python3
import sys
from config_loader import load_configuration

# Load configuration – this also sets OS_… variables for the chi SDK
cfg = load_configuration()
rt = cfg["runtime"]

# Import after the environment is ready
import chi
from chi import context, server, network, lease

# Choose project and site
context.choose_project(rt["project_name"])
context.choose_site(rt["site_name"])

# Create the VM
instance = server.create_server(
    name=rt["server_name"],
    image=rt["image_name"],
    flavor=rt["flavor_name"],
    network=rt["network_name"],
    key_name=rt["ssh_key_name"],
    security_groups=rt["security_groups"],
)

# Allocate and attach a floating IP
floating_ip = network.create_floating_ip(rt["floating_network"])
network.associate_floating_ip(instance.id, floating_ip.ip)

print(f"SSH: ssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}")
```

### 3.2 OpenStack CLI

Create a tiny helper that turns the YAML into `export` statements and source it:

```bash
#!/usr/bin/env bash
# load_chameleon_env.sh – source this script before using the CLI
python3 - <<'PY'
import os, yaml
cfg = yaml.safe_load(open(os.path.expanduser('~/.config/chameleon/env.yaml')))
# Set OS_… vars
for k, v in cfg.get('clouds', {}).get('chameleon', {}).get('auth', {}).items():
    print(f'export OS_{k.upper()}={v}')
# Export reservation vars
res = cfg.get('reservation', {})
if res:
    print(f'export RESERVATION_NAME={res.get("name","")}')
    print(f'export RESERVATION_OFFSET={res.get("start_offset_minutes","")}')
    print(f'export RESERVATION_DURATION={res.get("duration","")}')
PY
```

```bash
# In your terminal
source load_chameleon_env.sh
```

Now the CLI command is clean and readable:

```bash
openstack server create \
  --flavor "$(openstack flavor list -f value -c Name | grep m1.small)" \
  --image "$(openstack image list -f value -c Name | grep CC-Ubuntu-22.04)" \
  --key-name "$(openstack keypair list -f value -c Name | head -n1)" \
  --security-group default \
  --nic net-id="$(openstack network list -f value -c ID -c Name | grep sharednet1 | awk '{print $1}')" \
  my-test-vm
```

### 3.3 Libcloud

```python
#!/usr/bin/env python3
import os, logging
from config_loader import load_configuration
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

cfg = load_configuration()
rt = cfg["runtime"]

driver = get_driver(Provider.OPENSTACK)(
    key=os.getenv("OS_USERNAME"),
    secret=os.getenv("OS_PASSWORD"),
    ex_force_auth_url=os.getenv("OS_AUTH_URL"),
    ex_force_auth_version="3.x_password",
    ex_tenant_name=os.getenv("OS_PROJECT_NAME"),
    ex_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
)

node = driver.create_node(
    name=rt["server_name"],
    image=driver.get_image(rt["image_name"]),
    size=next(s for s in driver.list_sizes() if s.id == rt["flavor_name"]),
    ex_keyname=rt["ssh_key_name"],
    ex_security_groups=rt["security_groups"],
    ex_networks=[rt["network_name"]],
)

logging.info("Node created – public IPs: %s", ", ".join(node.public_ips))
```

### 3.4 openstacksdk

```python
#!/usr/bin/env python3
import logging, sys
from config_loader import load_configuration
import openstack

cfg = load_configuration()
rt = cfg["runtime"]

# The loader already set OS_… vars; the SDK can read the clouds.yaml entry
conn = openstack.connect(cloud="chameleon")

image   = conn.compute.find_image(rt["image_name"])
flavor  = conn.compute.find_flavor(rt["flavor_name"])
network = conn.network.find_network(rt["network_name"])
keypair = conn.compute.find_keypair(rt["ssh_key_name"])
secgrp  = conn.network.find_security_group(rt["security_groups"][0])

server = conn.compute.create_server(
    name=rt["server_name"],
    image_id=image.id,
    flavor_id=flavor.id,
    networks=[{"uuid": network.id}],
    key_name=keypair.name,
    security_groups=[{"name": secgrp.name}],
)

server = conn.compute.wait_for_server(server)

floating_ip = conn.network.create_ip(floating_network_id=rt["floating_network"])
conn.compute.add_floating_ip_to_server(server, floating_ip.floating_ip_address)

print(f"SSH: ssh -i ~/.ssh/id_rsa cc@{floating_ip.floating_ip_address}")
```

## 4. Reservation support

If the `reservation` block exists, any workflow can create a reservation (and an
optional lease) before launching the VM.

### 4.1 python‑chi example

```python
if cfg.get("reservation"):
    r = cfg["reservation"]
    from datetime import datetime, timedelta

    start = (datetime.utcnow() +
             timedelta(minutes=r["start_offset_minutes"])
             ).isoformat() + "Z"

    lease_id = None
    if r.get("lease_name"):
        lease_id = lease.create_lease(
            name=r["lease_name"],
            start=start,
            end=(datetime.fromisoformat(start.rstrip("Z")) +
                 timedelta(hours=1)).isoformat() + "Z",
            project=rt["project_name"],
        )

    reservation_id = lease.create_reservation(
        name=r["name"],
        start=start,
        end=r["duration"],          # ISO‑8601 duration string
        lease_id=lease_id,
        project=rt["project_name"],
        site=rt["site_name"],
    )
    print(f"Reservation created: {reservation_id}")
```

### 4.2 CLI equivalent (after sourcing the environment)

```bash
openstack reservation create \
  --name "$RESERVATION_NAME" \
  --project "$OS_PROJECT_NAME" \
  --site   "$OS_REGION_NAME" \
  --flavor "$(openstack flavor list -f value -c Name | grep m1.small)" \
  --image  "$(openstack image list -f value -c Name | grep CC-Ubuntu-22.04)" \
  --network "$(openstack network list -f value -c ID -c Name | grep sharednet1 | awk '{print $1}')" \
  --start "$(date -u -d "+${RESERVATION_OFFSET:-1} minute" +%Y-%m-%dT%H:%M:%SZ)" \
  --duration "${RESERVATION_DURATION:-1h}"
```

All reservation parameters are therefore **data‑driven**, not hard‑coded.

## 5. Checklist for a uniform workflow

| Step | Action |
|------|--------|
| 1 | Store a single `env.yaml` file under `~/.config/chameleon/` as shown above. |
| 2 | Protect the file: `chmod 600 ~/.config/chameleon/env.yaml`. |
| 3 | Add `config_loader.py` to every repository that contains a script. |
| 4 | In every script, call `load_configuration()` **before** importing any OpenStack/Chi SDK. |
| 5 | Use `cfg["runtime"]` for image, flavor, network, key‑pair, security‑group, floating‑network, etc. |
| 6 | If a reservation is required, read `cfg["reservation"]` and invoke the appropriate API or CLI command. |
| 7 | Never hard‑code passwords, tokens, or project IDs in source code; keep them only in the YAML file or a secret manager. |
| 8 | List `env.yaml` in `.gitignore` to avoid accidental commits. |

---

*This markdown file provides the complete description of the unified
environment configuration that can be used across all the examples, now
pointing to `~/.config/chameleon/env.yaml` and with a simplified `--name`
parameter for reservation creation.*