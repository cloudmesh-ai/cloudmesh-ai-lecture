
# Libcloud Chapter – Managing “Always‑Free” VMs on the Major Public Clouds  

This chapter shows how to use **Apache Libcloud** (a Python library that provides a single API for many cloud providers) to:

* read a single **clouds.yaml** file that contains the credentials for AWS, Azure, Google Cloud and Oracle Cloud,
* instantiate a driver for each provider,
* launch the smallest free‑tier virtual machine that each platform offers,
* obtain the public IP address,
* SSH into the instance, and
* clean the resources up again.

All code is written in plain Python 3 and can be run from a terminal (or inside a Docker container) without any emojis or numbered icons.



---  

## 1. Install Libcloud in an Isolated Way  

Choose one of the three installation methods that keep your host environment untouched.

### Docker wrapper (complete isolation)

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
export PATH=$HOME/bin:$PATH   # add to .bashrc/.zshrc
```

Running `libcloud myscript.py` will install Libcloud inside the container, mount the current directory and your SSH keys, and then execute the script.

### Official installer (native)  

```bash
python3 -m venv .libcloud‑venv
source .libcloud‑venv/bin/activate
pip install --upgrade pip
pip install libcloud
```

### pipx (sandbox)

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install libcloud
```

All three approaches give you a `python` interpreter with the `libcloud` package available. The examples below assume the virtual environment or Docker wrapper is active, so you can run `python myscript.py` (or `libcloud myscript.py` when using the Docker wrapper).

---  

## 2. The common **clouds.yaml** file  

Libcloud can read a YAML configuration that maps a logical name to a driver class and the credentials required by that driver.  
Below is a single `clouds.yaml` that works for the four major providers. The values are placeholders – replace them with the actual IDs and keys that you obtain from each cloud console (see the “Credentials” subsections).

```yaml
# clouds.yaml – one file for all providers
aws:
  driver: libcloud.compute.providers.DigitalOcean # (the driver name for EC2)
  key: YOUR_AWS_ACCESS_KEY_ID
  secret: YOUR_AWS_SECRET_ACCESS_KEY
  region: us-east-1            # free‑tier region

azure:
  driver: libcloud.compute.providers.AZURE_ARM
  tenant_id: YOUR_AZURE_TENANT_ID
  client_id: YOUR_AZURE_CLIENT_ID
  client_secret: YOUR_AZURE_CLIENT_SECRET
  subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
  location: eastus             # free‑tier region

gcp:
  driver: libcloud.compute.providers.GCE
  project: YOUR_GCP_PROJECT_ID
  service_account_key: /path/to/gcp-service-account.json
  zone: us-central1-a          # free‑tier zone for e2‑micro

oci:
  driver: libcloud.compute.providers.OCI
  tenancy: YOUR_OCI_TENANCY_OCID
  user: YOUR_OCI_USER_OCID
  fingerprint: YOUR_OCI_API_KEY_FINGERPRINT
  key_file: /home/you/.oci/oci_api_key.pem
  region: us-ashburn-1         # free‑tier region
```

**Note** – The driver names used by Libcloud differ from the provider names in the documentation. The mapping is:

| Provider | Libcloud driver class (import path) |
|----------|--------------------------------------|
| AWS      | `libcloud.compute.providers.EC2`     |
| Azure    | `libcloud.compute.providers.AZURE_ARM` |
| GCP      | `libcloud.compute.providers.GCE`     |
| OCI      | `libcloud.compute.providers.OCI`     |

If you prefer the short name syntax (`ec2`, `azure_arm`, `gce`, `oci`) you can also write the YAML as:

```yaml
aws:
  driver: ec2
  key: ...
  secret: ...
  region: us-east-1
...
```

Libcloud resolves the short name internally to the full class path.

---  

## 3. Helper functions – load config, pick driver, wait for an IP  

Create a small Python module (`libcloud_helpers.py`) that contains reusable code used by all providers.

```python
# libcloud_helpers.py
import time
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import yaml


def load_clouds_yaml(path="clouds.yaml"):
    """Read clouds.yaml and return the dictionary."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_driver_for(name, config):
    """
    Return an instantiated Libcloud driver for the given logical name.
    ``config`` is the dict returned by ``load_clouds_yaml``.
    """
    cloud_cfg = config[name]
    driver_name = cloud_cfg.pop("driver")
    if driver_name in ("ec2", "azure_arm", "gce", "oci"):
        # short names – map to Provider enum
        mapping = {
            "ec2": Provider.EC2,
            "azure_arm": Provider.AZURE_ARM,
            "gce": Provider.GCE,
            "oci": Provider.OCI,
        }
        driver_cls = get_driver(mapping[driver_name])
    else:
        # full import path given
        module_path, cls_name = driver_name.rsplit(".", 1)
        module = __import__(module_path, fromlist=[cls_name])
        driver_cls = getattr(module, cls_name)

    # The driver constructor signatures differ; we unpack the dict.
    return driver_cls(**cloud_cfg)


def wait_for_node(node, driver, timeout=300, poll_interval=5):
    """
    Poll the node until it reaches the RUNNING state and has a public IP.
    Returns the node once ready.
    """
    elapsed = 0
    while elapsed < timeout:
        node = driver.ex_get_node_details(node)  # refresh data
        if node.state == node.RUNNING:
            # Look for a public IP in the node's extra metadata
            for ip in node.public_ips:
                return node, ip
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise RuntimeError(f"Node {node.id} did not become ready within {timeout}s")
```

The helper abstracts away the provider‑specific details of driver construction and of waiting for a node to be reachable.

---  

## 4. Free‑tier VM definitions per provider  

Each provider has a different name for the free‑tier shape/image. The code below shows the minimal parameters required to launch a free instance on each cloud. The same high‑level flow is used:

1. pick a driver,
2. choose a **size** (instance type) and an **image**,
3. launch the node,
4. wait for it to become reachable,
5. print the public IP.

```python
# launch_free_vm.py
import sys
from libcloud_helpers import load_clouds_yaml, get_driver_for, wait_for_node

# ----------------------------------------------------------------------
# 1. Load configuration
# ----------------------------------------------------------------------
cfg = load_clouds_yaml()

# ----------------------------------------------------------------------
# 2. AWS – EC2 t2.micro (or t3.micro) in us‑east‑1
# ----------------------------------------------------------------------
aws_drv = get_driver_for("aws", cfg)
aws_image = aws_drv.get_image("ami-0b2f6494ff0b07a0e")   # Amazon Linux 2, us‑east‑1
aws_size = [s for s in aws_drv.list_sizes() if s.id == "t2.micro"][0]
aws_node = aws_drv.create_node(
    name="libcloud-aws-free",
    image=aws_image,
    size=aws_size,
    ex_keyname="libcloud-key",          # you must have uploaded a key beforehand
    ex_security_groups=["default"],     # default SG allows SSH from anywhere
)
aws_node, aws_ip = wait_for_node(aws_node, aws_drv)
print(f"AWS free instance ready – IP: {aws_ip}")

# ----------------------------------------------------------------------
# 3. Azure – B1s VM (Linux) in eastus
# ----------------------------------------------------------------------
azure_drv = get_driver_for("azure", cfg)
# Azure expects a location and a size name; the image is identified by
# publisher/offer/skus/version.
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
    ex_network="default",               # uses the default VNet/subnet
    ex_location="eastus",
    ex_ssh_key="~/.ssh/azure_free_key.pub",
)
azure_node, azure_ip = wait_for_node(azure_node, azure_drv)
print(f"Azure free instance ready – IP: {azure_ip}")

# ----------------------------------------------------------------------
# 4. GCP – e2‑micro in us-central1-a
# ----------------------------------------------------------------------
gcp_drv = get_driver_for("gcp", cfg)
gcp_image = gcp_drv.get_image(
    project="ubuntu-os-cloud",
    name="ubuntu-2204-jammy-v20241003",   # latest e2‑micro compatible image
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
    ex_metadata={},
)
gcp_node, gcp_ip = wait_for_node(gcp_node, gcp_drv)
print(f"GCP free instance ready – IP: {gcp_ip}")

# ----------------------------------------------------------------------
# 5. OCI – VM.Standard.E2.1.Micro (AMD) in us-ashburn-1
# ----------------------------------------------------------------------
oci_drv = get_driver_for("oci", cfg)
# OCI driver needs an image OCID. The latest Oracle Linux 8 image can be
# discovered with `oci compute image list`. For brevity we hard‑code a
# known public image that is free‑tier eligible.
oci_image_ocid = "ocid1.image.oc1..aaaaaaaabbbbbbbbbccccccccdddddddeeeeeeeee"
oci_image = oci_drv.get_image(oci_image_ocid)
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
print(f"OCI free instance ready – IP: {oci_ip}")

# ----------------------------------------------------------------------
# 6. SSH – one‑liner for each VM (outside of Python)
# ----------------------------------------------------------------------
print("\n=== SSH commands ===")
print(f"ssh -i ~/.ssh/aws_free_key.pem ec2-user@{aws_ip}")
print(f"ssh -i ~/.ssh/azure_free_key.pem azureuser@{azure_ip}")
print(f"ssh -i ~/.ssh/gcp_free_key.pem ubuntu@{gcp_ip}")
print(f"ssh -i ~/.ssh/oci_free_key.pem opc@{oci_ip}")

# ----------------------------------------------------------------------
# 7. Cleanup helper (optional)
# ----------------------------------------------------------------------
def destroy_all():
    for name, driver in [("aws", aws_drv), ("azure", azure_drv),
                         ("gcp", gcp_drv), ("oci", oci_drv)]:
        nodes = driver.list_nodes()
        for n in nodes:
            if n.name.startswith("libcloud-"):
                print(f"Destroying {name} node {n.name}")
                driver.destroy_node(n)

if "--destroy" in sys.argv:
    destroy_all()
```

### How the script works  

* **Configuration** – One call to `load_clouds_yaml` reads the file created in section 2.  
* **Driver creation** – `get_driver_for` hides the provider‑specific constructor signatures; it receives the `key`, `secret`, `region`, `tenant_id`, etc., directly from the YAML.  
* **Image/size lookup** – For each provider we fetch the *free‑tier* shape (`t2.micro`, `Standard_B1s`, `e2-micro`, `VM.Standard.E2.1.Micro`) and a compatible public image.  
* **Node creation** – `create_node` is the Libcloud‑standard method; provider‑specific flags start with `ex_`.  
* **Waiting** – `wait_for_node` polls until the node reports **RUNNING** and a public IP is present.  
* **SSH** – The script prints a ready‑to‑run SSH command for each instance.  

Running the script:

```bash
python launch_free_vm.py          # create VMs
python launch_free_vm.py --destroy   # delete VMs created by the script
```

When using the Docker wrapper from section 1, replace `python` with `libcloud`:

```bash
libcloud launch_free_vm.py
```

---  

## 5. Provider‑specific credential notes  

Below is a short reminder of how to retrieve the values used in `clouds.yaml`.

| Cloud | Required fields | Where to obtain them |
|-------|----------------|----------------------|
| **AWS** | `key`, `secret`, `region` | IAM → Users → (your user) → **Security credentials**. Create an access key. |
| **Azure** | `tenant_id`, `client_id`, `client_secret`, `subscription_id`, `location` | Azure Portal → **Azure Active Directory** → **App registrations** → New registration → copy *Application (client) ID* and *Directory (tenant) ID*. Generate a *client secret* under **Certificates & secrets**. Subscription ID is under **Subscriptions**. |
| **GCP** | `project`, `service_account_key`, `zone` | Create a service account in the Cloud Console, grant **Project → Owner** (or at least **Compute Admin**). Download the JSON key and point `service_account_key` to that file. |
| **OCI** | `tenancy`, `user`, `fingerprint`, `key_file`, `region` | IAM → Users → (your user) → **API Keys** → *Add API Key*. Upload the public key; the console shows the OCID for the tenancy and the user, as well as the fingerprint. Save the private key to the path referenced by `key_file`. |

All four providers support **environment‑variable** overrides (e.g. `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`). If you prefer not to store secrets in a file, set the variables before invoking the Python script; Libcloud will read them automatically.

---  

## 6. Common pitfalls and how to avoid them  

* **Region / zone mismatches** – The free‑tier shapes are only available in certain regions (e.g., `us-east-1` for AWS, `eastus` for Azure, `us-central1-a` for GCP, `us-ashburn-1` for OCI). Using a different region will result in a `ProviderError` indicating that the size is unavailable.  
* **Missing SSH key** – The `ex_keyname` (AWS) or `ex_ssh_key` (Azure, OCI) must reference a key that already exists in the cloud console. Upload your public key first, then reference its name. For GCP the driver automatically creates a temporary key if `ex_metadata` contains `ssh-keys`.  
* **Default security groups** – Some providers (Azure, OCI) require an explicit rule that allows inbound TCP 22. The helper functions above create a permissive rule; tighten it later by editing the SG or security list manually.  
* **API rate limits** – Libcloud makes a small number of API calls per node launch. If you run the script repeatedly in rapid succession you may hit provider‑specific rate limits. Insert a `time.sleep(2)` between each `create_node` if necessary.  
* **Deletion order** – OCI networking resources (subnet, IGW, security list) must be detached before the VCN can be removed. The `--destroy` flag in the sample script simply calls `destroy_node`; networking cleanup for OCI must be performed manually or via additional Libcloud calls (`ex_delete_vcn`).  

---  

## 7. Full cheat‑sheet for a “single‑file” workflow  

You can condense the entire process into one Python file (`free_vm_libcloud.py`) that contains the helpers, configuration loader, and the per‑provider launch logic. The only external requirement is the `clouds.yaml` file in the same directory.

```python
#!/usr/bin/env python3
# free_vm_libcloud.py
import time, yaml, sys
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

# ---------- helpers ----------
def load_cfg(p="clouds.yaml"):
    with open(p) as f:
        return yaml.safe_load(f)

def driver(name, cfg):
    d = cfg[name]
    drv_name = d.pop("driver")
    mapping = {
        "ec2": Provider.EC2,
        "azure_arm": Provider.AZURE_ARM,
        "gce": Provider.GCE,
        "oci": Provider.OCI,
    }
    if drv_name in mapping:
        cls = get_driver(mapping[drv_name])
    else:
        mod, cls_name = drv_name.rsplit(".", 1)
        cls = getattr(__import__(mod, fromlist=[cls_name]), cls_name)
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

# ---------- main ----------
cfg = load_cfg()

# AWS
aws = driver("aws", cfg)
aws_img = aws.get_image("ami-0b2f6494ff0b07a0e")
aws_sz  = [s for s in aws.list_sizes() if s.id == "t2.micro"][0]
aws_node = aws.create_node(name="lc-aws-free", image=aws_img,
                           size=aws_sz, ex_keyname="libcloud-key")
aws_node, aws_ip = wait(aws_node, aws)

# Azure
az = driver("azure", cfg)
az_img = az.get_image(publisher="Canonical", offer="UbuntuServer",
                      sku="18_04-lts-gen2", version="latest")
az_sz  = [s for s in az.list_sizes() if s.id == "Standard_B1s"][0]
az_node = az.create_node(name="lc-az-free", size=az_sz,
                         image=az_img, ex_ssh_key="~/.ssh/az.pub")
az_node, az_ip = wait(az_node, az)

# GCP
gcp = driver("gcp", cfg)
gcp_img = gcp.get_image(project="ubuntu-os-cloud",
                        name="ubuntu-2204-jammy-v20241003")
gcp_sz  = [s for s in gcp.list_sizes() if s.id == "e2-micro"][0]
gcp_node = gcp.create_node(name="lc-gcp-free", size=gcp_sz,
                           image=gcp_img, ex_external_ip="ephemeral")
gcp_node, gcp_ip = wait(gcp_node, gcp)

# OCI
oci = driver("oci", cfg)
oci_img = oci.get_image("ocid1.image.oc1..aaaaaaaaaaaaaaaabbbbbbbbbccccccccdddddddd")
oci_sz  = [s for s in oci.list_sizes() if s.id == "VM.Standard.E2.1.Micro"][0]
oci_node = oci.create_node(name="lc-oci-free", size=oci_sz,
                           image=oci_img,
                           ex_subnet_id="ocid1.subnet.oc1..your-subnet",
                           ex_public_ip=True,
                           ex_ssh_authorized_keys=open(f"{cfg['oci']['key_file']}.pub").read())
oci_node, oci_ip = wait(oci_node, oci)

# output
print("\n=== Public IPs ===")
print(f"AWS  : {aws_ip}")
print(f"Azure: {az_ip}")
print(f"GCP  : {gcp_ip}")
print(f"OCI  : {oci_ip}")

print("\n=== SSH commands ===")
print(f"ssh -i ~/.ssh/aws_free_key.pem ec2-user@{aws_ip}")
print(f"ssh -i ~/.ssh/azure_free_key.pem azureuser@{az_ip}")
print(f"ssh -i ~/.ssh/gcp_free_key.pem ubuntu@{gcp_ip}")
print(f"ssh -i ~/.ssh/oci_free_key.pem opc@{oci_ip}")

# optional destroy
if "--destroy" in sys.argv:
    for drv, name in [(aws, "AWS"), (az, "Azure"),
                      (gcp, "GCP"), (oci, "OCI")]:
        for n in drv.list_nodes():
            if n.name.startswith("lc-"):
                print(f"Destroying {name} node {n.name}")
                drv.destroy_node(n)
```

Save this file next to `clouds.yaml`, make it executable (`chmod +x free_vm_libcloud.py`) and run:

```bash
./free_vm_libcloud.py          # launches VMs
./free_vm_libcloud.py --destroy   # tears them down
```

All four VMs are started with the same logical flow, demonstrating how Libcloud provides a **common, provider‑agnostic API** for provisioning always‑free compute resources.

---  

## 8. References  

* Libcloud documentation – <https://libcloud.readthedocs.io/>  
* AWS EC2 driver – `libcloud.compute.drivers.ec2`  
* Azure ARM driver – `libcloud.compute.drivers.azure_arm`  
* Google Compute Engine driver – `libcloud.compute.drivers.gce`  
* Oracle Cloud Infrastructure driver – `libcloud.compute.drivers.oci`  
* Free‑tier specifications (AWS, Azure, GCP, OCI) – official provider web sites, linked in the previous chapters.

With the code and configuration shown above you can manage the free‑tier VMs on all four major clouds using a single, uniform Python interface. This makes it easy to write scripts, CI pipelines, or teaching material that works across clouds without learning each provider’s native CLI. Happy scripting!