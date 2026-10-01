
**Azure – Native Python SDK (azure‑sdk‑for‑python) equivalent to the Libcloud example**  

The following material reproduces the workflow that was shown with Libcloud, but uses the **official Azure SDK for Python** (`azure‑identity`, `azure‑mgmt‑compute`, `azure‑mgmt‑network`, `azure‑mgmt‑resource`).  
It covers  

* isolated installation of the Azure SDK,  
* a single `clouds.yaml` file that holds the Azure credentials,  
* reusable helper functions that wrap the low‑level SDK calls,  
* a script that creates the smallest always‑free compute resource (B1s Linux VM),  
* retrieval of the public IP address,  
* a ready‑to‑run SSH command, and  
* a clean‑up routine that removes every resource that was created.  

All code is written in plain Python 3 and contains no emojis or numbered icons.

---

## 1. Install the Azure SDK in an isolated environment  

You can keep the SDK separate from the rest of your system using any of the three methods below.

### Docker wrapper (complete isolation)

```bash
docker pull python:3.12-slim

cat <<'EOF' > ~/bin/azsdk
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.azure:/root/.azure:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  python:3.12-slim \
  bash -c "pip install --quiet azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-network PyYAML && python3 \"\$@\"" \
  "$@"
EOF
chmod +x ~/bin/azsdk
export PATH=$HOME/bin:$PATH   # add to your shell rc file (.bashrc, .zshrc)
```

Running `azsdk myscript.py` will install the required Azure packages inside the container, mount your current directory and SSH keys, and then execute the script.

### Native virtual‑environment installer

```bash
python3 -m venv .azure‑venv
source .azure‑venv/bin/activate
pip install --upgrade pip
pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-network PyYAML
```

### pipx sandbox

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install azure-identity
pipx install azure-mgmt-resource
pipx install azure-mgmt-compute
pipx install azure-mgmt-network
pipx install PyYAML
```

All three approaches give you a `python` interpreter with the Azure SDK and `yaml` package available.

---

## 2. The common `clouds.yaml` file (Azure only)

```yaml
azure:
  tenant_id: YOUR_AZURE_TENANT_ID
  client_id: YOUR_AZURE_CLIENT_ID
  client_secret: YOUR_AZURE_CLIENT_SECRET
  subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
  location: eastus                # free‑tier region
```

Replace the placeholders with the values from the service‑principal you created for Azure (see the “Credentials” note at the bottom of this document). The file must be placed in the same directory as the Python script.

---

## 3. Helper module – `azure_helpers.py`

```python
# azure_helpers.py
import os
import time
import yaml
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import (HardwareProfile, NetworkProfile,
                                       OSProfile, StorageProfile,
                                       ImageReference, LinuxConfiguration,
                                       SshConfiguration, SshPublicKey)
from azure.mgmt.network.models import (VirtualNetwork, AddressSpace,
                                       Subnet, PublicIPAddress,
                                       PublicIPAddressSku,
                                       NetworkSecurityGroup,
                                       SecurityRule, NetworkInterface,
                                       NetworkInterfaceIPConfiguration)


def load_config(path="clouds.yaml"):
    """Read clouds.yaml and return the azure dict."""
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg["azure"]


def get_clients(cfg):
    """Create credential and all required management clients."""
    credential = ClientSecretCredential(
        tenant_id=cfg["tenant_id"],
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
    )
    subscription_id = cfg["subscription_id"]
    resource_client = ResourceManagementClient(credential, subscription_id)
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)
    return credential, resource_client, compute_client, network_client


def ensure_resource_group(resource_client, name, location):
    """Create (or get) a resource group."""
    rg = resource_client.resource_groups.create_or_update(name, {"location": location})
    return rg


def ensure_ssh_key(public_key_path):
    """Read the public key file, raise if missing."""
    if not os.path.isfile(public_key_path):
        raise FileNotFoundError(f"Public key not found: {public_key_path}")
    with open(public_key_path, "r") as f:
        return f.read().strip()


def create_vnet(network_client, rg_name, vnet_name, location, address_prefix="10.0.0.0/16"):
    """Create a virtual network."""
    async_vnet = network_client.virtual_networks.begin_create_or_update(
        rg_name,
        vnet_name,
        VirtualNetwork(location=location, address_space=AddressSpace(address_prefixes=[address_prefix])),
    )
    return async_vnet.result()


def create_subnet(network_client, rg_name, vnet_name, subnet_name, address_prefix="10.0.0.0/24"):
    """Create a subnet inside the VNet."""
    async_subnet = network_client.subnets.begin_create_or_update(
        rg_name,
        vnet_name,
        subnet_name,
        Subnet(address_prefix=address_prefix),
    )
    return async_subnet.result()


def create_public_ip(network_client, rg_name, ip_name, location):
    """Create a standard public IP (static)."""
    async_ip = network_client.public_ip_addresses.begin_create_or_update(
        rg_name,
        ip_name,
        PublicIPAddress(
            location=location,
            sku=PublicIPAddressSku(name="Standard"),
            public_ip_allocation_method="Static",
        ),
    )
    return async_ip.result()


def create_nsg(network_client, rg_name, nsg_name, location):
    """Create a network security group that allows inbound SSH."""
    async_nsg = network_client.network_security_groups.begin_create_or_update(
        rg_name,
        nsg_name,
        NetworkSecurityGroup(location=location),
    )
    nsg = async_nsg.result()
    # Add SSH rule (allow TCP 22 from any source)
    async_rule = network_client.security_rules.begin_create_or_update(
        rg_name,
        nsg_name,
        "Allow-SSH",
        SecurityRule(
            protocol="Tcp",
            source_port_range="*",
            destination_port_range="22",
            source_address_prefix="*",
            destination_address_prefix="*",
            access="Allow",
            priority=1000,
            direction="Inbound",
        ),
    )
    async_rule.result()
    return nsg


def create_nic(network_client, rg_name, nic_name, location,
               subnet_id, ip_id, nsg_id):
    """Create a network interface attached to subnet, public IP, and NSG."""
    ip_cfg = NetworkInterfaceIPConfiguration(
        name="primary",
        subnet={"id": subnet_id},
        private_ip_allocation_method="Dynamic",
        public_ip_address={"id": ip_id},
    )
    async_nic = network_client.network_interfaces.begin_create_or_update(
        rg_name,
        nic_name,
        NetworkInterface(
            location=location,
            ip_configurations=[ip_cfg],
            network_security_group={"id": nsg_id},
        ),
    )
    return async_nic.result()


def create_vm(compute_client, rg_name, vm_name, location,
              nic_id, ssh_key_data, vm_size="Standard_B1s"):
    """Create a Linux VM (Ubuntu 22.04 LTS) with the supplied NIC and SSH key."""
    vm_parameters = {
        "location": location,
        "hardware_profile": HardwareProfile(vm_size=vm_size),
        "storage_profile": StorageProfile(
            image_reference=ImageReference(
                publisher="Canonical",
                offer="UbuntuServer",
                sku="22_04-lts-gen2",
                version="latest",
            )
        ),
        "os_profile": OSProfile(
            computer_name=vm_name,
            admin_username="azureuser",
            linux_configuration=LinuxConfiguration(
                disable_password_authentication=True,
                ssh=SshConfiguration(
                    public_keys=[
                        SshPublicKey(
                            path="/home/azureuser/.ssh/authorized_keys",
                            key_data=ssh_key_data,
                        )
                    ]
                ),
            ),
        ),
        "network_profile": NetworkProfile(network_interfaces=[{"id": nic_id}]),
    }

    async_vm = compute_client.virtual_machines.begin_create_or_update(
        rg_name, vm_name, vm_parameters
    )
    return async_vm.result()


def get_vm_public_ip(network_client, rg_name, ip_name):
    """Retrieve the allocated public IP address."""
    ip = network_client.public_ip_addresses.get(rg_name, ip_name)
    # Azure may take a few seconds after VM creation for the IP to be associated.
    while not ip.ip_address:
        time.sleep(5)
        ip = network_client.public_ip_addresses.get(rg_name, ip_name)
    return ip.ip_address


def delete_resource_group(resource_client, rg_name):
    """Delete the whole resource group – this removes every child resource."""
    async_delete = resource_client.resource_groups.begin_delete(rg_name)
    async_delete.wait()
```

The helper module hides all the Azure‑specific resource‑creation logic while exposing a few high‑level functions.

---

## 4. Main script – `run_azure_free_vm.py`

```python
#!/usr/bin/env python3
# run_azure_free_vm.py
import os
import sys
from azure_helpers import (
    load_config,
    get_clients,
    ensure_resource_group,
    ensure_ssh_key,
    create_vnet,
    create_subnet,
    create_public_ip,
    create_nsg,
    create_nic,
    create_vm,
    get_vm_public_ip,
    delete_resource_group,
)

# ----------------------------------------------------------------------
# Load configuration and create SDK clients
# ----------------------------------------------------------------------
cfg = load_config()
credential, resource_client, compute_client, network_client = get_clients(cfg)

# ----------------------------------------------------------------------
# Logical names – change the suffix if you run the script repeatedly
# ----------------------------------------------------------------------
RG_NAME   = "libcloud-azure-free-rg"
VNET_NAME = "libcloud-azure-free-vnet"
SUBNET_NAME = "libcloud-azure-free-subnet"
IP_NAME   = "libcloud-azure-free-pip"
NSG_NAME  = "libcloud-azure-free-nsg"
NIC_NAME  = "libcloud-azure-free-nic"
VM_NAME   = "libcloud-azure-free-vm"
LOCATION  = cfg["location"]
SSH_KEY_PATH = os.path.expanduser("~/.ssh/libcloud_azure_key.pub")

# ----------------------------------------------------------------------
# 1. Resource group (container for everything)
# ----------------------------------------------------------------------
ensure_resource_group(resource_client, RG_NAME, LOCATION)

# ----------------------------------------------------------------------
# 2. SSH public key (must exist locally)
# ----------------------------------------------------------------------
ssh_key_data = ensure_ssh_key(SSH_KEY_PATH)

# ----------------------------------------------------------------------
# 3. Networking – VNet, Subnet, Public IP, NSG, NIC
# ----------------------------------------------------------------------
vnet = create_vnet(network_client, RG_NAME, VNET_NAME, LOCATION)
subnet = create_subnet(network_client, RG_NAME, VNET_NAME, SUBNET_NAME)
public_ip = create_public_ip(network_client, RG_NAME, IP_NAME, LOCATION)
nsg = create_nsg(network_client, RG_NAME, NSG_NAME, LOCATION)
nic = create_nic(
    network_client,
    RG_NAME,
    NIC_NAME,
    LOCATION,
    subnet.id,
    public_ip.id,
    nsg.id,
)

# ----------------------------------------------------------------------
# 4. VM – B1s size (always‑free) with the NIC and SSH key
# ----------------------------------------------------------------------
create_vm(
    compute_client,
    RG_NAME,
    VM_NAME,
    LOCATION,
    nic.id,
    ssh_key_data,
    vm_size="Standard_B1s",
)

# ----------------------------------------------------------------------
# 5. Wait for the public IP to be associated and display SSH command
# ----------------------------------------------------------------------
ip_address = get_vm_public_ip(network_client, RG_NAME, IP_NAME)
print("\n=== Azure free instance ready ===")
print(f"Public IP: {ip_address}")
print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_azure_key azureuser@{ip_address}")

# ----------------------------------------------------------------------
# 6. Optional clean‑up
# ----------------------------------------------------------------------
if "--destroy" in sys.argv:
    print("\nCleaning up – deleting the resource group …")
    delete_resource_group(resource_client, RG_NAME)
    # Optionally delete the local SSH private key
    try:
        os.remove(os.path.expanduser("~/.ssh/libcloud_azure_key"))
    except OSError:
        pass
    print("All Azure resources removed.")
```

### How to run the script

```bash
# Using the Docker wrapper created in section 1
azsdk run_azure_free_vm.py          # creates the VM and prints the SSH command
azsdk run_azure_free_vm.py --destroy   # deletes the whole resource group
```

If you installed the SDK in a native virtual‑environment, simply run:

```bash
python run_azure_free_vm.py
python run_azure_free_vm.py --destroy
```

The script follows the same logical flow that the Libcloud example used, but now relies entirely on the **official Azure SDK**.

---

## 5. What the script does – step‑by‑step (no numbered icons)

* Reads Azure credentials from `clouds.yaml`.  
* Creates a `ClientSecretCredential` and three management clients (`ResourceManagementClient`, `ComputeManagementClient`, `NetworkManagementClient`).  
* Creates (or re‑uses) a resource group in the free‑tier location (`eastus`).  
* Loads a public SSH key from `~/.ssh/libcloud_azure_key.pub`. The private key must already exist (`libcloud_azure_key`).  
* Builds a virtual network (`10.0.0.0/16`) and a subnet (`10.0.0.0/24`).  
* Allocates a **standard static** public IP address (required for inbound SSH).  
* Creates a network security group with a single inbound rule that permits TCP 22 from any source.  
* Attaches the subnet, public IP, and NSG to a network interface.  
* Launches a **Standard_B1s** Linux VM (Ubuntu 22.04 LTS) using the NIC and injects the SSH public key into the default `azureuser` account.  
* Polls the public IP resource until Azure reports an IPv4 address, then prints an SSH command that can be used immediately.  
* When the optional `--destroy` flag is supplied, deletes the whole resource group, which removes every child resource (VNet, IP, NSG, NIC, VM). The local private key file is also removed if present.

All resources created are covered by the **Azure Free Tier** (B1s VM, 5 GiB Blob storage, etc.). As long as you keep the VM running for fewer than 750 hours per month and do not attach additional paid resources, you will incur no charges.

---

## 6. Credentials – how to obtain the values for `clouds.yaml`

1. **Create a service principal** (the Azure SDK prefers this over interactive login for scripts).  
   ```bash
   az ad sp create-for-rbac \
       --name libcloud-azure-sp \
       --role Contributor \
       --scopes /subscriptions/<SUBSCRIPTION_ID>
   ```
   The command returns a JSON object containing:
   * `appId` → `client_id`
   * `password` → `client_secret`
   * `tenant` → `tenant_id`
   * `id` → service‑principal OCID (not needed here)

2. Retrieve the **subscription ID**:  
   ```bash
   az account show --query id -o tsv
   ```

3. Put the four values into `clouds.yaml` together with the desired location (`eastus` is one of the free‑tier regions).

The service principal must have **Contributor** rights on the subscription (or a custom role that includes `Microsoft.Network/*`, `Microsoft.Compute/*`, and `Microsoft.Resources/*`). After the YAML file is populated, the script can run without any interactive prompts.

---

## 7. Common pitfalls and mitigation

* **Missing SSH key pair** – The script expects a **public key** file (`~/.ssh/libcloud_azure_key.pub`). Generate a key pair beforehand (`ssh-keygen -t rsa -b 2048 -f ~/.ssh/libcloud_azure_key`). The private key is used for the SSH command; the public key is injected into the VM.  
* **Location mismatch** – The free‑tier B1s size is only available in specific Azure regions (e.g., `eastus`, `westus2`, `westeurope`). Using another location will raise a `CloudError` indicating that the size is unavailable.  
* **Resource‑group name collision** – If a resource group with the same name already exists and contains resources that conflict (e.g., a VNet with the same address space), the script will fail. Use a unique suffix or delete the existing group before re‑running.  
* **Network‑security‑group rule already exists** – The helper checks for duplicate rule errors (`InvalidSecurityRuleOperation`) and ignores them, so rerunning the script is idempotent.  
* **Quota limits** – The free tier includes a **single** B1s VM per region. If you already have a B1s VM running, the script will fail on the `create_vm` call with a “quota exceeded” error. Stop or delete the existing free‑tier VM before running again.  

---

## 8. Full cheat‑sheet (single‑file version)

If you prefer a single‑file implementation that contains the helpers inline, copy the following into `azure_free_vm_onefile.py`. It reads `clouds.yaml`, creates the VM, prints the SSH command, and removes everything when `--destroy` is supplied.

```python
#!/usr/bin/env python3
import os, sys, time, yaml
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute.models import (HardwareProfile, NetworkProfile,
                                       OSProfile, StorageProfile,
                                       ImageReference, LinuxConfiguration,
                                       SshConfiguration, SshPublicKey)
from azure.mgmt.network.models import (VirtualNetwork, AddressSpace,
                                       Subnet, PublicIPAddress,
                                       PublicIPAddressSku,
                                       NetworkSecurityGroup, SecurityRule,
                                       NetworkInterface,
                                       NetworkInterfaceIPConfiguration)

def load_cfg():
    with open("clouds.yaml") as f:
        return yaml.safe_load(f)["azure"]

def get_clients(cfg):
    cred = ClientSecretCredential(tenant_id=cfg["tenant_id"],
                                  client_id=cfg["client_id"],
                                  client_secret=cfg["client_secret"])
    sub = cfg["subscription_id"]
    return (cred,
            ResourceManagementClient(cred, sub),
            ComputeManagementClient(cred, sub),
            NetworkManagementClient(cred, sub))

def ensure_rg(rg_client, name, loc):
    return rg_client.resource_groups.create_or_update(name, {"location": loc})

def read_ssh(pub_path):
    if not os.path.isfile(pub_path):
        raise FileNotFoundError(pub_path)
    with open(pub_path) as f:
        return f.read().strip()

def create_vnet(net_client, rg, name, loc):
    async_vnet = net_client.virtual_networks.begin_create_or_update(
        rg, name,
        VirtualNetwork(location=loc,
                       address_space=AddressSpace(address_prefixes=["10.0.0.0/16"])))
    return async_vnet.result()

def create_subnet(net_client, rg, vnet, name):
    async_sub = net_client.subnets.begin_create_or_update(
        rg, vnet, name, Subnet(address_prefix="10.0.0.0/24"))
    return async_sub.result()

def create_ip(net_client, rg, name, loc):
    async_ip = net_client.public_ip_addresses.begin_create_or_update(
        rg, name,
        PublicIPAddress(location=loc,
                        sku=PublicIPAddressSku(name="Standard"),
                        public_ip_allocation_method="Static"))
    return async_ip.result()

def create_nsg(net_client, rg, name, loc):
    async_nsg = net_client.network_security_groups.begin_create_or_update(
        rg, name, NetworkSecurityGroup(location=loc))
    nsg = async_nsg.result()
    async_rule = net_client.security_rules.begin_create_or_update(
        rg, name, "Allow-SSH",
        SecurityRule(protocol="Tcp",
                     source_port_range="*",
                     destination_port_range="22",
                     source_address_prefix="*",
                     destination_address_prefix="*",
                     access="Allow",
                     priority=1000,
                     direction="Inbound"))
    async_rule.result()
    return nsg

def create_nic(net_client, rg, name, loc, subnet_id, ip_id, nsg_id):
    ip_cfg = NetworkInterfaceIPConfiguration(
        name="primary",
        subnet={"id": subnet_id},
        private_ip_allocation_method="Dynamic",
        public_ip_address={"id": ip_id},
    )
    async_nic = net_client.network_interfaces.begin_create_or_update(
        rg, name,
        NetworkInterface(location=loc,
                         ip_configurations=[ip_cfg],
                         network_security_group={"id": nsg_id}))
    return async_nic.result()

def create_vm(comp_client, rg, name, loc, nic_id, ssh_key):
    vm_params = {
        "location": loc,
        "hardware_profile": HardwareProfile(vm_size="Standard_B1s"),
        "storage_profile": StorageProfile(
            image_reference=ImageReference(publisher="Canonical",
                                          offer="UbuntuServer",
                                          sku="22_04-lts-gen2",
                                          version="latest")
        ),
        "os_profile": OSProfile(
            computer_name=name,
            admin_username="azureuser",
            linux_configuration=LinuxConfiguration(
                disable_password_authentication=True,
                ssh=SshConfiguration(public_keys=[
                    SshPublicKey(
                        path="/home/azureuser/.ssh/authorized_keys",
                        key_data=ssh_key)
                ]))),
        "network_profile": NetworkProfile(network_interfaces=[{"id": nic_id}]),
    }
    async_vm = comp_client.virtual_machines.begin_create_or_update(
        rg, name, vm_params)
    return async_vm.result()

def get_ip(net_client, rg, ip_name):
    ip = net_client.public_ip_addresses.get(rg, ip_name)
    while not ip.ip_address:
        time.sleep(5)
        ip = net_client.public_ip_addresses.get(rg, ip_name)
    return ip.ip_address

def delete_rg(rg_client, rg):
    async_del = rg_client.resource_groups.begin_delete(rg)
    async_del.wait()

# -------------------- main --------------------
cfg = load_cfg()
cred, rg_client, compute_client, network_client = get_clients(cfg)

RG_NAME   = "az-free-rg"
VNET_NAME = "az-free-vnet"
SUBNET_NAME = "az-free-subnet"
IP_NAME   = "az-free-pip"
NSG_NAME  = "az-free-nsg"
NIC_NAME  = "az-free-nic"
VM_NAME   = "az-free-vm"
LOCATION  = cfg["location"]
SSH_PUB   = os.path.expanduser("~/.ssh/libcloud_azure_key.pub")

ensure_rg(rg_client, RG_NAME, LOCATION)
ssh_key = read_ssh(SSH_PUB)

vnet   = create_vnet(network_client, RG_NAME, VNET_NAME, LOCATION)
subnet = create_subnet(network_client, RG_NAME, VNET_NAME, SUBNET_NAME)
pip    = create_ip(network_client, RG_NAME, IP_NAME, LOCATION)
nsg    = create_nsg(network_client, RG_NAME, NSG_NAME, LOCATION)
nic    = create_nic(network_client, RG_NAME, NIC_NAME, LOCATION,
                    subnet.id, pip.id, nsg.id)

create_vm(compute_client, RG_NAME, VM_NAME, LOCATION, nic.id, ssh_key)

public_ip = get_ip(network_client, RG_NAME, IP_NAME)
print("\n=== Azure free VM is ready ===")
print(f"Public IP: {public_ip}")
print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_azure_key azureuser@{public_ip}")

if "--destroy" in sys.argv:
    print("\nDeleting resource group …")
    delete_rg(rg_client, RG_NAME)
    try:
        os.remove(os.path.expanduser("~/.ssh/libcloud_azure_key"))
    except OSError:
        pass
    print("All resources removed.")
```

Save this file next to `clouds.yaml`, make it executable (`chmod +x azure_free_vm_onefile.py`) and run:

```bash
./azure_free_vm_onefile.py          # start the VM
./azure_free_vm_onefile.py --destroy   # clean up
```

---

## 8. References  

* Azure SDK for Python documentation – <https://learn.microsoft.com/python/azure/>  
* `azure-identity` (service‑principal authentication) – <https://learn.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential>  
* `azure-mgmt-resource` – resource‑group management – <https://learn.microsoft.com/python/api/azure-mgmt-resource/azure.mgmt.resource.resourcemanagementclient>  
* `azure-mgmt-network` – VNet, subnet, public IP, NSG, NIC – <https://learn.microsoft.com/python/api/azure-mgmt-network/>  
* `azure-mgmt-compute` – VM creation – <https://learn.microsoft.com/python/api/azure-mgmt-compute/>  
* Azure Free Tier details – <https://azure.microsoft.com/free/>  
* Creating a service principal – <https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal>  

With this script you now have a **native Azure SDK** counterpart to the Libcloud example, allowing you to provision the always‑free B1s virtual machine, obtain its public IP, SSH into it, and clean up the resources using a single, provider‑specific Python program. Happy scripting!