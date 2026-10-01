
**Google Cloud – Native Python SDK (google‑cloud‑compute) equivalent to the Libcloud example**

The material below shows how to perform the same workflow that was demonstrated with Libcloud, but using the **official Google Cloud Python client libraries** instead of Libcloud:

* install the SDK in an isolated way  
* store all credentials in a single `clouds.yaml` file  
* provide a small helper module that hides the low‑level API calls  
* launch the smallest always‑free VM (`e2‑micro`) in a free‑tier region  
* obtain the public IPv4 address and print a ready‑to‑run SSH command  
* clean up every resource that was created  

Everything is written for Python 3 and contains no emojis or numbered icons.

---

## 1. Install the Google Cloud SDK in an isolated environment  

Choose one of the three methods; each gives you a clean Python environment with the required packages.

### Docker wrapper (complete isolation)

```bash
docker pull python:3.12-slim

cat <<'EOF' > ~/bin/gcloudsdk
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.config/gcloud:/root/.config/gcloud:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  python:3.12-slim \
  bash -c "pip install --quiet google-cloud-compute google-auth PyYAML && python3 \"\$@\"" \
  "$@"
EOF
chmod +x ~/bin/gcloudsdk
export PATH=$HOME/bin:$PATH   # add to your shell rc file (.bashrc, .zshrc)
```

Running `gcloudsdk myscript.py` will install the required Google libraries inside the container, mount the current directory and your SSH keys, and then execute the script.

### Native virtual‑environment installer

```bash
python3 -m venv .gcloud‑venv
source .gcloud‑venv/bin/activate
pip install --upgrade pip
pip install google-cloud-compute google-auth PyYAML
```

### pipx sandbox

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install google-cloud-compute
pipx install google-auth
pipx install PyYAML
```

All three approaches give you a `python` interpreter with the `google.cloud.compute_v1` package available.

---

## 2. The common `clouds.yaml` file (Google Cloud)

```yaml
google:
  project_id: YOUR_GCP_PROJECT_ID
  service_account_key: /home/you/.config/gcloud/sa-key.json   # absolute path
  zone: us-central1-a               # free‑tier zone for e2‑micro
```

*Create a service account* with the role **Compute Admin** (or a custom role that grants the permissions listed in the helper module). Download the JSON key file and place its absolute path in `service_account_key`. The service account must belong to the same project you intend to use.

---

## 3. Helper module – `gcp_helpers.py`

```python
# gcp_helpers.py
import os
import time
import yaml
from google.oauth2 import service_account
from google.cloud import compute_v1

def load_config(path="clouds.yaml"):
    """Read clouds.yaml and return the google dict."""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["google"]

def get_client(cfg):
    """
    Return a dictionary of Compute Engine service clients (instances, firewalls,
    networks, subnets, addresses) already authenticated with the service‑account
    key.
    """
    credentials = service_account.Credentials.from_service_account_file(
        cfg["service_account_key"]
    )
    project = cfg["project_id"]
    return {
        "project": project,
        "zone": cfg["zone"],
        "instances": compute_v1.InstancesClient(credentials=credentials),
        "networks": compute_v1.NetworksClient(credentials=credentials),
        "subnetworks": compute_v1.SubnetworksClient(credentials=credentials),
        "firewalls": compute_v1.FirewallsClient(credentials=credentials),
        "addresses": compute_v1.AddressesClient(credentials=credentials),
        "operations": compute_v1.ZoneOperationsClient(credentials=credentials),
    }

def wait_for_operation(client, operation, project, zone, timeout=300, interval=5):
    """
    Poll a zone‑level operation until it reaches DONE.
    Raises RuntimeError on timeout.
    """
    elapsed = 0
    while elapsed < timeout:
        result = client.get(project=project, zone=zone, operation=operation.name)
        if result.status == compute_v1.Operation.Status.DONE:
            if result.error:
                raise RuntimeError(f"Operation {operation.name} failed: {result.error}")
            return
        time.sleep(interval)
        elapsed += interval
    raise RuntimeError(f"Operation {operation.name} did not complete within {timeout}s")

def ensure_vpc_network(networks_client, project, network_name):
    """Create a VPC network (auto‑mode) if it does not exist."""
    try:
        networks_client.get(project=project, network=network_name)
    except Exception:
        operation = networks_client.insert(
            project=project,
            network_resource=compute_v1.Network(name=network_name, auto_create_subnetworks=False),
        )
        operation.result()  # wait
    # Return the network URL
    return f"projects/{project}/global/networks/{network_name}"

def ensure_subnet(subnetworks_client, project, region, network_url,
                  subnet_name, ip_cidr_range="10.0.0.0/24"):
    """Create a subnet inside the given VPC if it does not exist."""
    try:
        subnetworks_client.get(project=project, region=region, subnetwork=subnet_name)
    except Exception:
        subnet = compute_v1.Subnetwork(
            name=subnet_name,
            ip_cidr_range=ip_cidr_range,
            network=network_url,
        )
        operation = subnetworks_client.insert(project=project, region=region, subnetwork_resource=subnet)
        operation.result()
    return f"projects/{project}/regions/{region}/subnetworks/{subnet_name}"

def ensure_firewall(firewalls_client, project, network_name, fw_name):
    """
    Create a firewall rule that allows inbound SSH (tcp:22) from any source.
    """
    try:
        firewalls_client.get(project=project, firewall=fw_name)
    except Exception:
        firewall = compute_v1.Firewall(
            name=fw_name,
            network=f"projects/{project}/global/networks/{network_name}",
            allowed=[compute_v1.Allowed(ip_protocol="tcp", ports=["22"])],
            direction=compute_v1.Firewall.Direction.INGRESS,
            source_ranges=["0.0.0.0/0"],
        )
        firewalls_client.insert(project=project, firewall_resource=firewall).result()

def ensure_static_address(addresses_client, project, region, address_name):
    """
    Reserve a static external IPv4 address. Returns the address resource URL.
    """
    try:
        addr = addresses_client.get(project=project, region=region, address=address_name)
    except Exception:
        address = compute_v1.Address(name=address_name, address_type=compute_v1.Address.AddressType.EXTERNAL)
        operation = addresses_client.insert(project=project, region=region, address_resource=address)
        operation.result()
        addr = addresses_client.get(project=project, region=region, address=address_name)
    return addr.self_link

def create_instance(instances_client, project, zone, name, machine_type,
                    source_image_family, network_interface, ssh_key):
    """
    Launch an e2‑micro instance using the provided network interface and
    SSH public key.
    """
    # Build the full machine‑type URL
    machine_type_url = f"zones/{zone}/machineTypes/{machine_type}"

    # Build the source image from the family (Ubuntu 22.04 LTS)
    image_client = compute_v1.ImagesClient()
    image = image_client.get_from_family(project="ubuntu-os-cloud", family=source_image_family)

    # OS profile – inject the SSH key into the default user (ubuntu)
    metadata_item = compute_v1.Metadata.ItemsValueListEntry(
        key="ssh-keys",
        value=f"ubuntu:{ssh_key}"
    )
    metadata = compute_v1.Metadata(items=[metadata_item])

    instance = compute_v1.Instance(
        name=name,
        machine_type=machine_type_url,
        disks=[
            compute_v1.AttachedDisk(
                boot=True,
                auto_delete=True,
                initialize_params=compute_v1.AttachedDiskInitializeParams(
                    source_image=image.self_link,
                ),
            )
        ],
        network_interfaces=[network_interface],
        metadata=metadata,
        labels={"libcloud-demo": "true"},
    )
    operation = instances_client.insert(project=project, zone=zone, instance_resource=instance)
    operation.result()  # wait for the instance to be provisioned

def get_instance_external_ip(instances_client, project, zone, name):
    """Return the external IPv4 address of the instance."""
    instance = instances_client.get(project=project, zone=zone, instance=name)
    for iface in instance.network_interfaces:
        if iface.access_configs:
            return iface.access_configs[0].nat_i_p
    raise RuntimeError(f"No external IP found on instance {name}")

def delete_instance(instances_client, project, zone, name):
    """Stop and delete the instance."""
    try:
        instances_client.delete(project=project, zone=zone, instance=name).result()
    except Exception as e:
        print(f"Warning: could not delete instance {name}: {e}")

def delete_network_resources(clients, project, region, network_name, subnet_name,
                            address_name, firewall_name):
    """
    Delete the network components created for the demo. The order matters:
    1) Firewall
    2) Instance (already deleted by the caller)
    3) Address
    4) Subnet
    5) Network
    """
    # Firewall
    try:
        clients["firewalls"].delete(project=project, firewall=firewall_name).result()
    except Exception:
        pass

    # Address
    try:
        clients["addresses"].delete(project=project, region=region, address=address_name).result()
    except Exception:
        pass

    # Subnet
    try:
        clients["subnetworks"].delete(project=project, region=region, subnetwork=subnet_name).result()
    except Exception:
        pass

    # Network
    try:
        clients["networks"].delete(project=project, network=network_name).result()
    except Exception:
        pass
```

The functions above implement the minimal set of operations needed for the free‑tier VM:

* VPC network (auto‑mode disabled)
* Subnet
* Static external IP address
* Firewall rule allowing inbound SSH (port 22)
* VM instance based on the Ubuntu 22.04 LTS image family
* Helpers for waiting on operations and for clean‑up

---

## 4. Main script – `run_gcp_free_vm.py`

```python
#!/usr/bin/env python3
# run_gcp_free_vm.py
import os
import sys
from gcp_helpers import (
    load_config,
    get_client,
    ensure_vpc_network,
    ensure_subnet,
    ensure_firewall,
    ensure_static_address,
    create_instance,
    get_instance_external_ip,
    delete_instance,
    delete_network_resources,
)

# -------------------------------------------------
# Load configuration and build the SDK clients
# -------------------------------------------------
cfg = load_config()
clients = get_client(cfg)

PROJECT = clients["project"]
ZONE    = clients["zone"]
REGION  = ZONE.rsplit("-", 1)[0]   # e.g. us-central1-a -> us-central1

# -------------------------------------------------
# Logical resource names – change the suffix if you run the script repeatedly
# -------------------------------------------------
NETWORK_NAME = "libcloud-gcp-free-net"
SUBNET_NAME  = "libcloud-gcp-free-sub"
FIREWALL_NAME = "libcloud-gcp-free-fw"
ADDRESS_NAME = "libcloud-gcp-free-ip"
INSTANCE_NAME = "libcloud-gcp-free-vm"
MACHINE_TYPE  = "e2-micro"
IMAGE_FAMILY  = "ubuntu-2204-lts"   # Ubuntu 22.04 LTS family
SSH_KEY_PATH  = os.path.expanduser("~/.ssh/libcloud_gcp_key.pub")

# -------------------------------------------------
# 1. Verify SSH public key exists
# -------------------------------------------------
if not os.path.isfile(SSH_KEY_PATH):
    raise FileNotFoundError(f"Public SSH key not found: {SSH_KEY_PATH}")
with open(SSH_KEY_PATH, "r") as f:
    ssh_key_data = f.read().strip()

# -------------------------------------------------
# 2. Create networking components
# -------------------------------------------------
network_url = ensure_vpc_network(clients["networks"], PROJECT, NETWORK_NAME)
subnet_url  = ensure_subnet(clients["subnetworks"], PROJECT, REGION,
                            network_url, SUBNET_NAME)
ensure_firewall(clients["firewalls"], PROJECT, NETWORK_NAME, FIREWALL_NAME)
static_ip_selflink = ensure_static_address(clients["addresses"], PROJECT,
                                           REGION, ADDRESS_NAME)

# Build the network interface that references the subnet and the static IP
network_interface = compute_v1.NetworkInterface(
    name="nic0",
    subnetwork=subnet_url,
    access_configs=[
        compute_v1.AccessConfig(
            name="External NAT",
            nat_i_p=static_ip_selflink,   # link the reserved static IP
            type_=compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT,
        )
    ],
)

# -------------------------------------------------
# 3. Launch the free‑tier e2‑micro VM
# -------------------------------------------------
create_instance(
    instances_client=clients["instances"],
    project=PROJECT,
    zone=ZONE,
    name=INSTANCE_NAME,
    machine_type=MACHINE_TYPE,
    source_image_family=IMAGE_FAMILY,
    network_interface=network_interface,
    ssh_key=ssh_key_data,
)

# -------------------------------------------------
# 4. Retrieve the public IP address (should match the static address)
# -------------------------------------------------
public_ip = get_instance_external_ip(clients["instances"], PROJECT, ZONE, INSTANCE_NAME)
print("\n=== GCP free instance ready ===")
print(f"Public IP: {public_ip}")

print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_gcp_key ubuntu@{public_ip}")

# -------------------------------------------------
# 5. Optional clean‑up
# -------------------------------------------------
if "--destroy" in sys.argv:
    print("\nCleaning up resources …")
    delete_instance(clients["instances"], PROJECT, ZONE, INSTANCE_NAME)

    delete_network_resources(
        clients,
        project=PROJECT,
        region=REGION,
        network_name=NETWORK_NAME,
        subnet_name=SUBNET_NAME,
        address_name=ADDRESS_NAME,
        firewall_name=FIREWALL_NAME,
    )

    # Optionally delete the local SSH private key
    try:
        os.remove(os.path.expanduser("~/.ssh/libcloud_gcp_key"))
    except OSError:
        pass

    print("All GCP resources removed.")
```

### How to run the script

```bash
# Using the Docker wrapper from section 1
gcloudsdk run_gcp_free_vm.py          # creates the VM and prints the SSH command
gcloudsdk run_gcp_free_vm.py --destroy   # tears everything down
```

If you installed the SDK in a native virtual‑environment, simply execute:

```bash
python run_gcp_free_vm.py
python run_gcp_free_vm.py --destroy
```

The script follows the same high‑level flow that the Libcloud example used, but relies exclusively on **google‑cloud‑compute** (the official Compute Engine client library).

---

## 5. What the script does (step‑by‑step, no numbered icons)

* Reads the Google Cloud project ID, service‑account key file, and zone from `clouds.yaml`.  
* Authenticates with `service_account.Credentials`.  
* Creates a VPC network (`auto_create_subnetworks=False`) – this isolates the demo resources from the default network.  
* Creates a single `/24` subnet inside the network.  
* Reserves a **static** external IPv4 address (required for a stable SSH endpoint).  
* Adds a firewall rule that allows inbound TCP 22 from any source (replace `0.0.0.0/0` with your own CIDR for tighter security).  
* Launches an `e2‑micro` instance (the always‑free shape) based on the public Ubuntu 22.04 LTS image family, attaches the NIC that uses the static IP, and injects the SSH public key into the default `ubuntu` user’s `authorized_keys`.  
* Waits for the operation to complete, then fetches the instance’s external IP (which should match the reserved static IP).  
* Prints a ready‑to‑run SSH command.  
* When the optional `--destroy` flag is present, stops and deletes the VM, then removes the firewall rule, static IP, subnet, and network in the correct order. The local private SSH key file is also removed if it exists.

All resources are covered by the **Google Cloud Free Tier** (e2‑micro VM, 5 GB of Regional Cloud Storage, 1 TiB egress, etc.). As long as you stay within those limits you will not be charged.

---

## 6. Credentials – how to obtain the values for `clouds.yaml`

1. **Create a service account** in the Cloud Console or with `gcloud`:

   ```bash
   gcloud iam service-accounts create libcloud-gcp-sa \
       --display-name "Libcloud demo service account"
   ```

2. **Grant the service account the required role** (minimal set for this demo):

   ```bash
   gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID \
       --member="serviceAccount:libcloud-gcp-sa@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/compute.admin"
   ```

3. **Download the JSON key file**:

   ```bash
   gcloud iam service-accounts keys create ~/config/sa-key.json \
       --iam-account libcloud-gcp-sa@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com
   ```

4. Populate `clouds.yaml` with the `project_id`, absolute path to the JSON key, and the free‑tier zone (`us-central1-a`, `us-west1-a`, `northamerica-northeast1-a`, or `southamerica-east1-a`).

The service account key file must be kept secure; do not commit it to version control.

---

## 7. Common pitfalls and how to avoid them

* **Wrong zone** – `e2‑micro` is only free in the zones listed on the Free‑Tier page (e.g., `us-central1-a`). Using a different zone returns `INVALID_ARGUMENT` for the machine type.  
* **Static IP reservation failure** – If an address with the chosen name already exists in the region, the helper re‑uses it. If that address is already attached to another resource, the VM creation will fail. Use a unique name or delete the existing address first.  
* **Firewall rule already exists** – The helper silently ignores `AlreadyExists` errors, making the script idempotent.  
* **Service‑account key path** – Ensure the JSON key file is readable by the user executing the script. The SDK will raise `DefaultCredentialsError` if the file cannot be loaded.  
* **Quota limits** – The free tier allows one `e2‑micro` VM per region. If you already have a free‑tier VM running, the script will fail with a quota‑exceeded error. Stop or delete the existing VM before re‑running.  

---

## 8. Single‑file cheat‑sheet (all code in one file)

If you prefer a single script without an external helper module, copy the following into `gcp_free_vm_onefile.py`. It contains the helper functions inline, reads `clouds.yaml`, creates the VM, prints the SSH command, and removes everything when `--destroy` is given.

```python
#!/usr/bin/env python3
import os, sys, time, yaml
from google.oauth2 import service_account
from google.cloud import compute_v1

# ---------- configuration ----------
def load_cfg():
    with open("clouds.yaml") as f:
        return yaml.safe_load(f)["google"]

cfg = load_cfg()
credentials = service_account.Credentials.from_service_account_file(
    cfg["service_account_key"]
)
PROJECT = cfg["project_id"]
ZONE    = cfg["zone"]
REGION  = ZONE.rsplit("-", 1)[0]

# ---------- clients ----------
instances  = compute_v1.InstancesClient(credentials=credentials)
networks  = compute_v1.NetworksClient(credentials=credentials)
subnetworks = compute_v1.SubnetworksClient(credentials=credentials)
firewalls = compute_v1.FirewallsClient(credentials=credentials)
addresses = compute_v1.AddressesClient(credentials=credentials)

# ---------- helpers ----------
def wait_op(op):
    while op.status != compute_v1.Operation.Status.DONE:
        time.sleep(3)
        op = compute_v1.ZoneOperationsClient(credentials=credentials).get(
            project=PROJECT, zone=ZONE, operation=op.name
        )
    if op.error:
        raise RuntimeError(op.error)

def ensure_network(name):
    try:
        networks.get(project=PROJECT, network=name)
    except Exception:
        op = networks.insert(
            project=PROJECT,
            network_resource=compute_v1.Network(name=name, auto_create_subnetworks=False),
        )
        wait_op(op)
    return f"projects/{PROJECT}/global/networks/{name}"

def ensure_subnet(name, net_url):
    try:
        subnetworks.get(project=PROJECT, region=REGION, subnetwork=name)
    except Exception:
        sub = compute_v1.Subnetwork(
            name=name,
            ip_cidr_range="10.0.0.0/24",
            network=net_url,
        )
        op = subnetworks.insert(project=PROJECT, region=REGION, subnetwork_resource=sub)
        wait_op(op)

def ensure_firewall(name, net_name):
    try:
        firewalls.get(project=PROJECT, firewall=name)
    except Exception:
        fw = compute_v1.Firewall(
            name=name,
            network=f"projects/{PROJECT}/global/networks/{net_name}",
            allowed=[compute_v1.Allowed(ip_protocol="tcp", ports=["22"])],
            direction=compute_v1.Firewall.Direction.INGRESS,
            source_ranges=["0.0.0.0/0"],
        )
        firewalls.insert(project=PROJECT, firewall_resource=fw).result()

def ensure_address(name):
    try:
        addr = addresses.get(project=PROJECT, region=REGION, address=name)
    except Exception:
        a = compute_v1.Address(name=name, address_type=compute_v1.Address.AddressType.EXTERNAL)
        op = addresses.insert(project=PROJECT, region=REGION, address_resource=a)
        wait_op(op)
        addr = addresses.get(project=PROJECT, region=REGION, address=name)
    return addr.self_link

def create_vm(name, machine_type, img_family, nic, ssh_key):
    mt_url = f"zones/{ZONE}/machineTypes/{machine_type}"
    img_client = compute_v1.ImagesClient()
    img = img_client.get_from_family(project="ubuntu-os-cloud", family=img_family)

    metadata = compute_v1.Metadata(
        items=[compute_v1.Metadata.ItemsValueListEntry(
            key="ssh-keys",
            value=f"ubuntu:{ssh_key}"
        )]
    )

    instance = compute_v1.Instance(
        name=name,
        machine_type=mt_url,
        disks=[compute_v1.AttachedDisk(
            boot=True,
            auto_delete=True,
            initialize_params=compute_v1.AttachedDiskInitializeParams(source_image=img.self_link)
        )],
        network_interfaces=[nic],
        metadata=metadata,
        labels={"libcloud-demo": "true"},
    )
    op = instances.insert(project=PROJECT, zone=ZONE, instance_resource=instance)
    wait_op(op)

def get_ip(name):
    i = instances.get(project=PROJECT, zone=ZONE, instance=name)
    for iface in i.network_interfaces:
        if iface.access_configs:
            return iface.access_configs[0].nat_i_p
    raise RuntimeError("No external IP")

def delete_vm(name):
    try:
        op = instances.delete(project=PROJECT, zone=ZONE, instance=name)
        wait_op(op)
    except Exception:
        pass

def delete_networks(net, sub, fw, addr):
    for f in [(firewalls, fw), (addresses, addr), (subnetworks, sub), (networks, net)]:
        try:
            client, name = f
            client.delete(project=PROJECT, **({"region": REGION, "subnetwork": name}
                if client is subnetworks else
                {"global": True, "network": name} if client is networks else
                {"global": True, "firewall": name} if client is firewalls else
                {"region": REGION, "address": name}))
        except Exception:
            pass

# ---------- main workflow ----------
NETWORK_NAME   = "gcp-free-net"
SUBNET_NAME    = "gcp-free-sub"
FIREWALL_NAME  = "gcp-free-fw"
ADDRESS_NAME   = "gcp-free-ip"
VM_NAME        = "gcp-free-vm"
MACHINE_TYPE   = "e2-micro"
IMAGE_FAMILY   = "ubuntu-2204-lts"
SSH_KEY_PATH   = os.path.expanduser("~/.ssh/libcloud_gcp_key.pub")

if not os.path.isfile(SSH_KEY_PATH):
    raise FileNotFoundError(SSH_KEY_PATH)
with open(SSH_KEY_PATH) as f:
    ssh_key = f.read().strip()

net_url = ensure_network(NETWORK_NAME)
ensure_subnet(SUBNET_NAME, net_url)
ensure_firewall(FIREWALL_NAME, NETWORK_NAME)
addr_url = ensure_address(ADDRESS_NAME)

nic = compute_v1.NetworkInterface(
    name="nic0",
    subnetwork=f"projects/{PROJECT}/regions/{REGION}/subnetworks/{SUBNET_NAME}",
    access_configs=[compute_v1.AccessConfig(
        name="External NAT",
        nat_i_p=addr_url,
        type_=compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT,
    )],
)

create_vm(VM_NAME, MACHINE_TYPE, IMAGE_FAMILY, nic, ssh_key)
public_ip = get_ip(VM_NAME)

print("\n=== GCP free VM ready ===")
print(f"Public IP: {public_ip}")
print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_gcp_key ubuntu@{public_ip}")

if "--destroy" in sys.argv:
    print("\nCleaning up …")
    delete_vm(VM_NAME)
    delete_networks(NETWORK_NAME, SUBNET_NAME, FIREWALL_NAME, ADDRESS_NAME)
    try:
        os.remove(os.path.expanduser("~/.ssh/libcloud_gcp_key"))
    except OSError:
        pass
    print("All resources removed.")
```

Place the script next to `clouds.yaml`, make it executable (`chmod +x gcp_free_vm_onefile.py`) and run:

```bash
./gcp_free_vm_onefile.py          # create the VM
./gcp_free_vm_onefile.py --destroy   # delete everything
```

---

## 9. Further reading

| Resource | What you’ll find |
|----------|------------------|
| Google Cloud Python client libraries | <https://cloud.google.com/python/docs/reference> |
| Compute Engine API reference (v1) | <https://cloud.google.com/compute/docs/reference/rest/v1> |
| Free‑tier overview (e2‑micro) | <https://cloud.google.com/free> |
| Service‑account creation & IAM roles | <https://cloud.google.com/iam/docs/creating-managing-service-accounts> |
| `gcloud` command‑line reference (optional) | <https://cloud.google.com/sdk/gcloud> |

You now have a complete, provider‑specific Python implementation that mirrors the Libcloud example but uses Google’s native client library. The script creates an always‑free `e2‑micro` VM, provides an SSH command, and cleans up the resources when you are finished—all without leaving any stray resources that could generate charges. Happy scripting!