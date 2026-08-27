
# Creating an OpenStack VM with the OpenStackSDK  
*A step‑by‑step tutorial*

---

<a name="overview"></a>
## 1. Overview

This tutorial shows how to create a virtual machine (VM) on an OpenStack cloud using the **openstacksdk** Python library.  
The script performs the following actions:

* Authenticates to the cloud (via environment variables, RC file, or `clouds.yaml`).  
* Looks up the required resources (image, flavor, network, keypair, security group).  
* Starts a server creation request.  
* Waits until the server reaches the **ACTIVE** state or fails.  
* Prints useful details (ID, status, IP addresses) for the newly created VM.

---

<a name="prerequisites"></a>
## 2. Prerequisites

| Item | How to obtain / install |
|------|--------------------------|
| **Python 3** | Most Linux/macOS installations already include it. Verify with `python3 --version`. |
| **openstacksdk** | `pip install --user openstacksdk` (or install inside a virtual environment). |
| **OpenStack credentials** | Either: <br>1. Source an *OpenStack RC file* (`source ~/my-openstack-rc.sh`). <br>2. Or create a `clouds.yaml` entry in `~/.config/openstack/clouds.yaml`. |
| **Existing resources** | The image, flavor, network, SSH keypair, and security group referenced in the script must already exist in the project/tenant you are authenticating to. |

---

<a name="configure-access-to-your-cloud"></a>
## 3. Configure Access to Your Cloud

### 3.1 Using an RC file (quick start)

```bash
# Example – download the RC file from the Horizon dashboard and source it
source ~/my-openstack-rc.sh
```

The RC file sets environment variables such as `OS_AUTH_URL`, `OS_USERNAME`, `OS_PASSWORD`, etc., which the SDK reads automatically.

### 3.2 Using a `clouds.yaml` file (recommended for scripts)

Create the directory if it does not exist:

```bash
mkdir -p ~/.config/openstack
```

Create (or edit) `~/.config/openstack/clouds.yaml`:

```yaml
clouds:
  chameleon:                     # <‑‑ name used in the script
    auth:
      auth_url: https://<auth-endpoint>/v3
      username: your_user
      password: your_password
      project_name: your_project
      user_domain_name: Default
      project_domain_name: Default
    region_name: RegionOne
    interface: public
    identity_api_version: 3
```

> **Note**: Replace the placeholder values with the information from your cloud provider.

---

<a name="full-python-script"></a>
## 4. Full Python Script

Save the following as `create_vm.py` (or any name you prefer):

```python
#!/usr/bin/env python3
"""
Create a VM on an OpenStack cloud using the openstacksdk.

Prerequisites
-------------
* pip install openstacksdk
* Either
  - source an OpenStack RC file (exporting OS_AUTH_URL, OS_USERNAME, …) OR
  - have a clouds.yaml entry in ~/.config/openstack/clouds.yaml
* The referenced resources (image, flavor, network, keypair, security group)
  must already exist in the target project/tenant.
"""

import sys
import logging

# ------------------------------------------------------------
# 1. Logging – makes debugging a lot easier
# ------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("create_vm")

# ------------------------------------------------------------
# 2. Configuration – edit these variables to suit your environment
# ------------------------------------------------------------
CLOUD_NAME          = "chameleon"          # Change if your clouds.yaml uses a different name
SERVER_NAME         = "my-test-vm"
IMAGE_NAME          = "CC-Ubuntu-22.04"
FLAVOR_NAME         = "m1.small"
NETWORK_NAME        = "sharednet1"
KEYPAIR_NAME        = "my-ssh-key"
SECURITY_GROUP_NAME = "default"

# ------------------------------------------------------------
# 3. Connect to the cloud
# ------------------------------------------------------------
try:
    import openstack
    conn = openstack.connect(cloud=CLOUD_NAME)   # reads clouds.yaml / env vars automatically
    log.info("Successfully authenticated to cloud %s", CLOUD_NAME)
except Exception as exc:
    log.error("Failed to authenticate: %s", exc)
    sys.exit(1)

# ------------------------------------------------------------
# 4. Helper to fetch a resource or abort with a clear message
# ------------------------------------------------------------
def get_or_die(find_func, name, resource_type):
    """Wrap openstacksdk find_* helpers with a nice error message."""
    obj = find_func(name)
    if obj is None:
        log.error("Could not find %s named %r – aborting", resource_type, name)
        sys.exit(1)
    log.info("Found %s: %s (id=%s)", resource_type, obj.name, obj.id)
    return obj

# ------------------------------------------------------------
# 5. Resolve all required resources
# ------------------------------------------------------------
image   = get_or_die(conn.compute.find_image,      IMAGE_NAME,      "image")
flavor  = get_or_die(conn.compute.find_flavor,     FLAVOR_NAME,     "flavor")
network = get_or_die(conn.network.find_network,    NETWORK_NAME,    "network")
keypair = get_or_die(conn.compute.find_keypair,    KEYPAIR_NAME,    "keypair")
secgrp  = get_or_die(conn.network.find_security_group,
                     SECURITY_GROUP_NAME, "security group")

# ------------------------------------------------------------
# 6. Build the server creation payload
# ------------------------------------------------------------
server_data = {
    "name": SERVER_NAME,
    "image_id": image.id,
    "flavor_id": flavor.id,
    "networks": [{"uuid": network.id}],      # list of dicts; each can contain uuid or port
    "key_name": keypair.name,
    "security_groups": [{"name": secgrp.name}],  # list of dicts, each with a single key “name”
}

log.info("Creating server %s …", SERVER_NAME)
try:
    server = conn.compute.create_server(**server_data)
except Exception as exc:
    log.error("Failed to start server creation: %s", exc)
    sys.exit(1)

# ------------------------------------------------------------
# 7. Wait until the server becomes ACTIVE (or fails)
# ------------------------------------------------------------
log.info("Waiting for server %s to become ACTIVE …", SERVER_NAME)

try:
    # The SDK polls until the server reaches the desired state (default ACTIVE)
    # or a failure state (ERROR).  Interval and total timeout are configurable.
    server = conn.compute.wait_for_server(
        server,
        status="ACTIVE",
        failures=["ERROR"],
        interval=5,   # seconds between polls
        wait=600,     # total timeout in seconds (10 min)
    )
except openstack.exceptions.ResourceTimeout as exc:
    log.error("Timed out waiting for server to become ACTIVE: %s", exc)
    sys.exit(1)
except openstack.exceptions.SDKException as exc:
    log.error("Server entered a failure state: %s", exc)
    sys.exit(1)

# ------------------------------------------------------------
# 8. Success – print the useful details
# ------------------------------------------------------------
log.info("Server %s is now ACTIVE!", server.name)
print("\n=== Server details ===")
print(f"Name   : {server.name}")
print(f"ID     : {server.id}")
print(f"Status : {server.status}")
print(f"Flavor : {flavor.name}")
print(f"Image  : {image.name}")
print(f"Network: {network.name}")
print(
    "Fixed IPs:",
    [addr["addr"]
     for net in server.addresses.values()
     for addr in net
     if addr.get("OS-EXT-IPS:type") == "fixed"]
)

print("\nYou can now SSH into the instance (assuming the security group allows port 22):")
print(f"  ssh -i /path/to/your/private/key {KEYPAIR_NAME}@<floating-or-fixed-IP>")
```

Make the script executable:

```bash
chmod +x create_vm.py
```

---

<a name="explanation-of-the-script"></a>
## 5. Explanation of the Script

Below is a line‑by‑line walk‑through of the important parts.  
Numbers correspond to the comments inside the script.

### 5.1 1. Logging

```python
logging.basicConfig(...)
log = logging.getLogger("create_vm")
```

* Provides timestamps and severity levels.  
* Helps you see exactly where a failure occurs.

### 5.2 2. Configuration Variables

```python
CLOUD_NAME          = "chameleon"
SERVER_NAME         = "my-test-vm"
...
```

* Central place to adjust the VM name, image, flavor, network, etc.  
* Changing a single variable updates the whole script.

### 5.3 3. Connecting to the Cloud

```python
conn = openstack.connect(cloud=CLOUD_NAME)
```

* `openstacksdk` reads credentials from environment variables, an RC file, **or** a `clouds.yaml` entry matching `CLOUD_NAME`.  
* The `try/except` block aborts with a clear error if authentication fails.

### 5.4 4. Helper Function `get_or_die`

```python
def get_or_die(find_func, name, resource_type):
    ...
```

* Wraps the SDK’s `find_*` helpers (`find_image`, `find_flavor`, etc.).  
* If the resource cannot be located, the script prints an informative message and exits.

### 5.5 5. Resolving Required Resources

```python
image   = get_or_die(conn.compute.find_image, IMAGE_NAME, "image")
...
```

* Retrieves the actual OpenStack objects (which contain the UUIDs needed for creation).  
* Validates that every required resource exists before proceeding.

### 5.6 6. Building the Server Payload

```python
server_data = {
    "name": SERVER_NAME,
    "image_id": image.id,
    "flavor_id": flavor.id,
    "networks": [{"uuid": network.id}],
    "key_name": keypair.name,
    "security_groups": [{"name": secgrp.name}],
}
```

* The dictionary follows the OpenStack **create server** API.  
* Network is expressed as a list of dictionaries; each dict can contain `uuid`, `port`, etc.  
* Security groups are a list of dicts with a single key `name`.

### 5.7 7. Waiting for the Server to Become ACTIVE

```python
server = conn.compute.wait_for_server(
    server,
    status="ACTIVE",
    failures=["ERROR"],
    interval=5,
    wait=600,
)
```

* Polls the server every **5 seconds** until it reaches **ACTIVE** or **ERROR**.  
* Times out after **10 minutes** (`wait=600`). Adjust as needed for larger images/flavors.

### 5.8 8. Printing Result Details

```python
print("\n=== Server details ===")
print(f"Name   : {server.name}")
...
print(
    "Fixed IPs:",
    [addr["addr"] for net in server.addresses.values()
                    for addr in net
                    if addr.get("OS-EXT-IPS:type") == "fixed"]
)
```

* Shows the newly created VM’s ID, status, flavor, image, and any fixed IPs returned by OpenStack.  
* The final line gives a template `ssh` command (replace the placeholder with a real floating or fixed IP).

---

<a name="running-the-tutorial"></a>
## 6. Running the Tutorial

```bash
# (Optional) create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the SDK if you haven’t already
pip install openstacksdk

# Ensure you are authenticated – either source an RC file or have clouds.yaml configured
source ~/my-openstack-rc.sh   # or rely on clouds.yaml

# Edit create_vm.py if you need to change any of the configuration variables

# Execute the script
./create_vm.py
```

When successful, you will see log lines similar to:

```
2026-08-27 14:22:01,123 INFO  create_vm Successfully authenticated to cloud chameleon
2026-08-27 14:22:01,456 INFO  create_vm Found image: CC-Ubuntu-22.04 (id=1b2c3d4e-…)
2026-08-27 14:22:01,589 INFO  create_vm Creating server my-test-vm …
2026-08-27 14:22:07,401 INFO  create_vm Waiting for server my-test-vm to become ACTIVE …
2026-08-27 14:22:45,892 INFO  create_vm Server my-test-vm is now ACTIVE!

=== Server details ===
Name   : my-test-vm
ID     : a1b2c3d4‑e5f6‑7g8h‑9i0j‑k1l2m3n4o5p6
Status : ACTIVE
Flavor : m1.small
Image  : CC-Ubuntu-22.04
Network: sharednet1
Fixed IPs: ['192.168.10.42']

You can now SSH into the instance (assuming the security group allows port 22):
  ssh -i /path/to/your/private/key my-ssh-key@<floating-or-fixed-IP>
```

---

<a name="common-issues--troubleshooting"></a>
## 7. Common Issues & Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `Failed to authenticate` | Missing or incorrect credentials | Verify that the RC file is sourced **or** that `clouds.yaml` contains the correct section name (`CLOUD_NAME`). |
| `Could not find image named 'CC-Ubuntu-22.04'` | Image name typo or image not visible to the project | List images with `openstack image list` or adjust `IMAGE_NAME`. |
| `Server entered a failure state` or status becomes `ERROR` | Incompatible flavor/network, quota exceeded, or missing SSH key | Check the OpenStack dashboard for the server’s error details, ensure your quota is sufficient, and confirm the keypair exists. |
| No IP address printed | The network is a private only network without a floating IP | Allocate a floating IP and associate it (see *Optional Extensions*). |
| `ResourceTimeout` after 10 min | Very large image or slow backend; timeout too short | Increase `wait=` parameter in `wait_for_server`. |

---

<a name="optional-extensions"></a>
## 8. Optional Extensions

| Feature | Code snippet |
|---------|--------------|
| **Allocate and attach a floating IP** | ```python\n# after server is ACTIVE\nfip = conn.network.create_ip(floating_network_id='<public-net-id>')\nconn.compute.add_floating_ip_to_server(server, fip.floating_ip_address)\nprint(f\"Floating IP attached: {fip.floating_ip_address}\")\n``` |
| **Inject cloud‑init userdata** | Add `user_data=open('cloud-init.yaml').read()` to the `server_data` dictionary. |
| **Automatic cleanup on failure** | Wrap the creation/wait block in `try/except` and call `conn.compute.delete_server(server, ignore_missing=True)` in the `except` clause. |
| **Create multiple VMs in parallel** | Use `concurrent.futures.ThreadPoolExecutor` and submit the entire creation routine for each server definition. The SDK client is thread‑safe. |
| **Verbose SDK logging** | Add `logging.getLogger('openstack').setLevel(logging.DEBUG)` after the basic logging configuration. |

---

### End of Tutorial

You now have a complete, reusable Python script and a step‑by‑step guide for launching OpenStack VMs programmatically. Adjust the configuration variables to match your environment, run the script, and you’ll have a running instance ready for SSH or further automation. Happy building!