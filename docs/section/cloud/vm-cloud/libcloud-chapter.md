## Learning Objectives

!!! info "Learning Objectives"
    * Install Apache Libcloud in an isolated environment to avoid dependency conflicts.
    * Configure a centralized `clouds.yaml` file to manage credentials for multiple cloud providers.
    * Develop Python helper functions to abstract provider-specific driver instantiation and node readiness polling.
    * Provision free-tier virtual machines across AWS, Azure, GCP, and OCI using a unified API.
    * Implement a basic multi-cloud cleanup routine to prevent orphaned resources and unexpected costs.

## Overview

This chapter demonstrates how to use Apache Libcloud, a Python library that provides a standardized API for interacting with multiple cloud providers. By using Libcloud, developers can manage resources across AWS, Azure, Google Cloud, and Oracle Cloud without having to learn the distinct SDKs and CLI tools for each platform.

The focus of this chapter is the deployment and management of "Always-Free" virtual machines, ensuring that the process is automated, reproducible, and provider-agnostic.

## Core Sections

### Installing Libcloud

To prevent conflicts with system-level Python packages, Libcloud should be installed in an isolated environment. Three methods are recommended:

#### Docker Wrapper (Complete Isolation)

This method uses a slim Python container to run scripts, mounting local directories and SSH keys into the container.

```bash
docker pull python:3.12-slim

cat <<'EOF' > ~/bin/libcloud
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  -v "$HOME/.config:/root/.config" \
  python:3.12-slim \
  bash -c "pip install --quiet libcloud && python3 \"\$@\"" \
  "$@"
EOF
chmod +x ~/bin/libcloud
export PATH=$HOME/bin:$PATH
```

#### Virtual Environment (Native)

A standard Python virtual environment provides isolation on the local host.

```bash
python3 -m venv .libcloud-venv
source .libcloud-venv/bin/activate
pip install --upgrade pip
pip install libcloud
```

#### pipx (Sandboxed Applications)

`pipx` is ideal for installing Libcloud as a standalone tool in its own virtual environment.

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install libcloud
```

### Configuration with clouds.yaml

Libcloud can utilize a YAML configuration file to map logical cloud names to their respective drivers and credentials. This approach separates secrets from the application logic.

Below is a standardized `clouds.yaml` template. Replace the placeholders with actual identifiers obtained from your cloud consoles.

```yaml
# clouds.yaml - centralized configuration for all providers
aws:
  driver: libcloud.compute.providers.EC2
  key: YOUR_AWS_ACCESS_KEY_ID
  secret: YOUR_AWS_SECRET_ACCESS_KEY
  region: us-east-1

azure:
  driver: libcloud.compute.providers.AZURE_ARM
  tenant_id: YOUR_AZURE_TENANT_ID
  client_id: YOUR_AZURE_CLIENT_ID
  client_secret: YOUR_AZURE_CLIENT_SECRET
  subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
  location: eastus

gcp:
  driver: libcloud.compute.providers.GCE
  project: YOUR_GCP_PROJECT_ID
  service_account_key: /path/to/gcp-service-account.json
  zone: us-central1-a

oci:
  driver: libcloud.compute.providers.OCI
  tenancy: YOUR_OCI_TENANCY_OCID
  user: YOUR_OCI_USER_OCID
  fingerprint: YOUR_OCI_API_KEY_FINGERPRINT
  key_file: /home/you/.oci/oci_api_key.pem
  region: us-ashburn-1
```

#### Driver Mapping Reference

Libcloud drivers are accessed via specific class paths. The following table summarizes the mapping for the major providers:

| Provider | Libcloud Driver Class | Short Name (Internal) |
|----------|-----------------------|-----------------------|
| AWS      | `libcloud.compute.providers.EC2` | `ec2` |
| Azure    | `libcloud.compute.providers.AZURE_ARM` | `azure_arm` |
| GCP      | `libcloud.compute.providers.GCE` | `gce` |
| OCI      | `libcloud.compute.providers.OCI` | `oci` |

### Implementation Helpers

To avoid redundant code, create a helper module named `libcloud_helpers.py`. This module handles configuration loading, driver instantiation, and the polling logic required to wait for a VM to become reachable.

```python
# libcloud_helpers.py
import time
import yaml
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def load_clouds_yaml(path="clouds.yaml"):
    """Read clouds.yaml and return the dictionary."""
    with open(path, "r") as f:
        return yaml.safe_load(f)

def get_driver_for(name, config):
    """
    Return an instantiated Libcloud driver for the given logical name.
    """
    cloud_cfg = config[name].copy()
    driver_name = cloud_cfg.pop("driver")
    
    if driver_name in ("ec2", "azure_arm", "gce", "oci"):
        mapping = {
            "ec2": Provider.EC2,
            "azure_arm": Provider.AZURE_ARM,
            "gce": Provider.GCE,
            "oci": Provider.OCI,
        }
        driver_cls = get_driver(mapping[driver_name])
    else:
        module_path, cls_name = driver_name.rsplit(".", 1)
        module = __import__(module_path, fromlist=[cls_name])
        driver_cls = getattr(module, cls_name)

    return driver_cls(**cloud_cfg)

def wait_for_node(node, driver, timeout=300, poll_interval=5):
    """
    Poll the node until it reaches the RUNNING state and has a public IP.
    """
    elapsed = 0
    while elapsed < timeout:
        node = driver.ex_get_node_details(node)
        if node.state == node.RUNNING:
            for ip in node.public_ips:
                return node, ip
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise RuntimeError(f"Node {node.id} did not become ready within {timeout}s")
```

### Launching Free-Tier VMs

The following script, `launch_free_vm.py`, demonstrates the unified workflow: picking a driver, selecting the free-tier size and image, launching the node, and waiting for the public IP.

```python
# launch_free_vm.py
import sys
from libcloud_helpers import load_clouds_yaml, get_driver_for, wait_for_node

cfg = load_clouds_yaml()

# AWS - EC2 t2.micro
aws_drv = get_driver_for("aws", cfg)
aws_image = aws_drv.get_image("ami-0b2f6494ff0b07a0e")
aws_size = [s for s in aws_drv.list_sizes() if s.id == "t2.micro"][0]
aws_node = aws_drv.create_node(
    name="libcloud-aws-free",
    image=aws_image,
    size=aws_size,
    ex_keyname="libcloud-key",
    ex_security_groups=["default"],
)
aws_node, aws_ip = wait_for_node(aws_node, aws_drv)
print(f"AWS free instance ready - IP: {aws_ip}")

# Azure - B1s
azure_drv = get_driver_for("azure", cfg)
azure_image = azure_drv.get_image(
    publisher="Canonical",
    offer="UbuntuServer",
    sku="18_04-lts-gen2",
    version="latest",
)
azure_size = [s for s in azure_drv.list_sizes() if s.id == "Standard_B1s"][0]
azure_node = azure_drv.create_node(
    name="libcloud-azure-free",
    size=azure_size,
    image=azure_image,
    ex_network="default",
    ex_location="eastus",
    ex_ssh_key="~/.ssh/azure_free_key.pub",
)
azure_node, azure_ip = wait_for_node(azure_node, azure_drv)
print(f"Azure free instance ready - IP: {azure_ip}")

# GCP - e2-micro
gcp_drv = get_driver_for("gcp", cfg)
gcp_image = gcp_drv.get_image(
    project="ubuntu-os-cloud",
    name="ubuntu-2204-jammy-v20241003",
)
gcp_size = [s for s in gcp_drv.list_sizes() if s.id == "e2-micro"][0]
gcp_node = gcp_drv.create_node(
    name="libcloud-gcp-free",
    size=gcp_size,
    image=gcp_image,
    ex_external_ip="ephemeral",
    ex_network="default",
    ex_subnetwork="default",
    ex_tags=["ssh"],
)
gcp_node, gcp_ip = wait_for_node(gcp_node, gcp_drv)
print(f"GCP free instance ready - IP: {gcp_ip}")

# OCI - VM.Standard.E2.1.Micro
oci_drv = get_driver_for("oci", cfg)
oci_image = oci_drv.get_image("ocid1.image.oc1..aaaaaaaabbbbbbbbbccccccccdddddddeeeeeeeee")
oci_size = [s for s in oci_drv.list_sizes() if s.id == "VM.Standard.E2.1.Micro"][0]
oci_node = oci_drv.create_node(
    name="libcloud-oci-free",
    size=oci_size,
    image=oci_image,
    ex_subnet_id="ocid1.subnet.oc1..your-subnet-ocid",
    ex_public_ip=True,
    ex_ssh_authorized_keys=open(f"{cfg['oci']['key_file']}.pub").read(),
)
oci_node, oci_ip = wait_for_node(oci_node, oci_drv)
print(f"OCI free instance ready - IP: {oci_ip}")

if "--destroy" in sys.argv:
    for name, driver in [("aws", aws_drv), ("azure", azure_drv), ("gcp", gcp_drv), ("oci", oci_drv)]:
        nodes = driver.list_nodes()
        for n in nodes:
            if n.name.startswith("libcloud-"):
                print(f"Destroying {name} node {n.name}")
                driver.destroy_node(n)
```

### Managing Credentials

To successfully authenticate, ensure the following fields are correctly configured in your `clouds.yaml` or environment variables.

| Cloud | Required Fields | Source |
|-------|-----------------|--------|
| **AWS** | `key`, `secret`, `region` | IAM -> Users -> Security credentials. |
| **Azure** | `tenant_id`, `client_id`, `client_secret`, `subscription_id`, `location` | Azure AD -> App registrations. |
| **GCP** | `project`, `service_account_key`, `zone` | IAM & Admin -> Service Accounts (JSON key). |
| **OCI** | `tenancy`, `user`, `fingerprint`, `key_file`, `region` | IAM -> Users -> API Keys. |

### Troubleshooting and Pitfalls

When using Libcloud for multi-cloud provisioning, be aware of these common issues:

* **Region/Zone Mismatches**: Free-tier shapes are region-specific. Launching a `t2.micro` in a non-eligible region will result in a `ProviderError`.
* **SSH Key Management**: Keys must exist in the cloud console before they can be referenced in the script (e.g., `ex_keyname` for AWS).
* **Security Groups**: Ensure that inbound TCP port 22 is open in the default security groups of the target cloud to allow SSH access.
* **API Rate Limits**: Rapidly creating and destroying nodes can trigger rate limits. Use `time.sleep()` between requests if necessary.
* **OCI Networking Cleanup**: Destroying a node does not automatically remove the associated VCN or Subnet. These must be deleted manually or via separate Libcloud calls.

### Unified Workflow Cheat-sheet

The following code combines the helpers and launch logic into a single file, `free_vm_libcloud.py`.

```python
#!/usr/bin/env python3
import time, yaml, sys
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

def load_cfg(p="clouds.yaml"):
    with open(p) as f:
        return yaml.safe_load(f)

def driver(name, cfg):
    d = cfg[name].copy()
    drv_name = d.pop("driver")
    mapping = {"ec2": Provider.EC2, "azure_arm": Provider.AZURE_ARM, "gce": Provider.GCE, "oci": Provider.OCI}
    cls = get_driver(mapping[drv_name]) if drv_name in mapping else \
          getattr(__import__(drv_name.rsplit(".", 1)[0], fromlist=[drv_name.rsplit(".", 1)[1]]), drv_name.rsplit(".", 1)[1])
    return cls(**d)

def wait(node, drv, timeout=300):
    elapsed = 0
    while elapsed < timeout:
        node = drv.ex_get_node_details(node)
        if node.state == node.RUNNING and node.public_ips:
            return node, node.public_ips[0]
        time.sleep(5)
        elapsed += 5
    raise RuntimeError("Timeout waiting for node")

cfg = load_cfg()
results = {}

for cloud in ["aws", "azure", "gcp", "oci"]:
    try:
        drv = driver(cloud, cfg)
        # Simplified launch logic for the cheat-sheet
        # (Actual image/size IDs omitted for brevity; use launch_free_vm.py for full details)
        print(f"Provisioning {cloud}...")
        # node = drv.create_node(...)
        # node, ip = wait(node, drv)
        # results[cloud] = ip
    except Exception as e:
        print(f"Error provisioning {cloud}: {e}")

print("\n=== Public IPs ===")
for cloud, ip in results.items():
    print(f"{cloud.upper()}: {ip}")

if "--destroy" in sys.argv:
    # Implementation of destroy_all() as seen in launch_free_vm.py
    pass
```

## Summary Checklist

* [ ] Libcloud installed in an isolated Python environment (venv or Docker).
* [ ] `clouds.yaml` created with valid credentials for at least two providers.
* [ ] `libcloud_helpers.py` implemented to manage drivers and node polling.
* [ ] Successfully launched a free-tier VM on at least one cloud platform.
* [ ] Verified SSH connectivity to the provisioned instances.

## Assignments

!!! note "Assignment.1: Multi-Cloud Provisioning"
    Write a script using Libcloud that launches a free-tier VM on two different cloud providers (e.g., AWS and OCI) and prints both public IP addresses.

??? tip "Solution: Multi-Cloud Provisioning"
    The solution involves iterating over a list of cloud names in `clouds.yaml`, calling `get_driver_for` for each, and using the `create_node` and `wait_for_node` functions.

!!! note "Assignment.2: Automated Resource Cleanup"
    Extend the `destroy_all` function to not only destroy the nodes but also list all remaining nodes in the account to ensure no resources were leaked.

??? tip "Solution: Automated Resource Cleanup"
    Use `driver.list_nodes()` to fetch all instances and `driver.destroy_node(n)` for those matching a specific naming convention (e.g., names starting with "libcloud-").

## References

* Apache Libcloud Documentation: <https://libcloud.readthedocs.io/>
* AWS EC2 Driver: `libcloud.compute.drivers.ec2`
* Azure ARM Driver: `libcloud.compute.drivers.azure_arm`
* Google Compute Engine Driver: `libcloud.compute.drivers.gce`
* Oracle Cloud Infrastructure Driver: `libcloud.compute.drivers.oci`
