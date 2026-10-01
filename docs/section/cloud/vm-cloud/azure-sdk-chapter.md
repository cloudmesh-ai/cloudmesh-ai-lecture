# Azure Native Python SDK

!!! info "Learning Objectives"
    * Install the Azure SDK for Python in an isolated environment.
    * Configure Azure credentials using a standardized YAML file.
    * Develop helper functions to manage Resource Groups, Virtual Networks, and Network Security Groups.
    * Implement an automated workflow to launch and terminate free-tier B1s virtual machines.
    * Retrieve the public IP address and establish a secure SSH connection.
    * Automate the removal of all provisioned Azure resources.

## Overview

This chapter demonstrates how to manage Azure resources using the official Azure SDK for Python. It provides a direct counterpart to the Libcloud examples, showing how to handle the full lifecycle of a virtual machine—from environment setup and credential management to instance deployment and resource cleanup—using native SDK calls.

## Core Sections

### Installation and Environment

You can keep the SDK separate from the rest of your system using any of the three methods below.

#### Docker wrapper (complete isolation)

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
export PATH=$HOME/bin:$PATH
```

Running `azsdk myscript.py` will install the required Azure packages inside the container, mount your current directory and SSH keys, and then execute the script.

#### Native virtual-environment installer

```bash
python3 -m venv .azure-venv
source .azure-venv/bin/activate
pip install --upgrade pip
pip install azure-identity azure-mgmt-resource azure-mgmt-compute azure-mgmt-network PyYAML
```

#### pipx sandbox

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install azure-identity
pipx install azure-mgmt-resource
pipx install azure-mgmt-compute
pipx install azure-mgmt-network
pipx install PyYAML
```

All three approaches provide a `python` interpreter with the Azure SDK and `yaml` package available.

### Configuration with clouds.yaml

To avoid hard-coding credentials, use a `clouds.yaml` file to store Azure service principal details and the target region.

```yaml
azure:
    tenant_id: YOUR_AZURE_TENANT_ID
    client_id: YOUR_AZURE_CLIENT_ID
    client_secret: YOUR_AZURE_CLIENT_SECRET
    subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
    location: eastus
```

Replace the placeholders with the values from the service principal created for Azure. The file must be placed in the same directory as the Python script.

### Implementing Azure Helpers

The following helper module, `azure_helpers.py`, wraps low-level SDK calls into reusable functions for managing the Azure infrastructure.

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
while not ip.ip_address:
    time.sleep(5)
    ip = network_client.public_ip_addresses.get(rg_name, ip_name)
return ip.ip_address


def delete_resource_group(resource_client, rg_name):
"""Delete the whole resource group - this removes every child resource."""
async_delete = resource_client.resource_groups.begin_delete(rg_name)
async_delete.wait()
```

### Orchestrating the B1s VM with run_azure_free_vm.py

The main orchestration script uses the helper module to deploy a free-tier instance and provide the SSH connection string.

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

# Load configuration and create SDK clients
cfg = load_config()
credential, resource_client, compute_client, network_client = get_clients(cfg)

# Logical names
RG_NAME   = "libcloud-azure-free-rg"
VNET_NAME = "libcloud-azure-free-vnet"
SUBNET_NAME = "libcloud-azure-free-subnet"
IP_NAME   = "libcloud-azure-free-pip"
NSG_NAME  = "libcloud-azure-free-nsg"
NIC_NAME  = "libcloud-azure-free-nic"
VM_NAME   = "libcloud-azure-free-vm"
LOCATION  = cfg["location"]
SSH_KEY_PATH = os.path.expanduser("~/.ssh/libcloud_azure_key.pub")

# 1. Resource group
ensure_resource_group(resource_client, RG_NAME, LOCATION)

# 2. SSH public key
ssh_key_data = ensure_ssh_key(SSH_KEY_PATH)

# 3. Networking - VNet, Subnet, Public IP, NSG, NIC
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

# 4. VM - B1s size (always-free) with the NIC and SSH key
create_vm(
compute_client,
RG_NAME,
VM_NAME,
LOCATION,
nic.id,
ssh_key_data,
vm_size="Standard_B1s",
)

# 5. Wait for the public IP to be associated and display SSH command
ip_address = get_vm_public_ip(network_client, RG_NAME, IP_NAME)
print("\n=== Azure free instance ready ===")
print(f"Public IP: {ip_address}")
print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_azure_key azureuser@{ip_address}")

# 6. Optional clean-up
if "--destroy" in sys.argv:
print("\nCleaning up - deleting the resource group ...")
delete_resource_group(resource_client, RG_NAME)
try:
    os.remove(os.path.expanduser("~/.ssh/libcloud_azure_key"))
except OSError:
    pass
print("All Azure resources removed.")
```

#### How to run the script

```bash
# Using the Docker wrapper
azsdk run_azure_free_vm.py
azsdk run_azure_free_vm.py --destroy

# Using native virtual-environment
python run_azure_free_vm.py
python run_azure_free_vm.py --destroy
```

### Operational Summary

The deployment workflow follows these logical steps:

* Read Azure credentials from `clouds.yaml`.
* Create a `ClientSecretCredential` and three management clients for resources, compute, and network.
* Ensure a resource group exists in a free-tier location (e.g., `eastus`).
* Load a public SSH key from `~/.ssh/libcloud_azure_key.pub`.
* Build a virtual network and subnet.
* Allocate a standard static public IP address.
* Create a network security group with an inbound rule for TCP port 22.
* Attach the subnet, public IP, and NSG to a network interface.
* Launch a `Standard_B1s` Linux VM using the NIC and the SSH public key.
* Poll for the public IP and output the SSH command.
* If `--destroy` is passed, delete the entire resource group and the local private key.

All resources are covered by the Azure Free Tier (B1s VM, 5 GB Blob storage), provided usage stays within the monthly limits.

### Obtaining Credentials

The Azure SDK prefers service principals over interactive logins for automation scripts.

1. **Create a service principal**:
    ```bash
    az ad sp create-for-rbac \
    --name libcloud-azure-sp \
    --role Contributor \
    --scopes /subscriptions/<SUBSCRIPTION_ID>
    ```
    The command returns a JSON object containing the `appId` (client_id), `password` (client_secret), and `tenant` (tenant_id).

2. **Retrieve the subscription ID**:
    ```bash
    az account show --query id -o tsv
    ```

3. **Populate clouds.yaml** with these values and the target location. The service principal must have **Contributor** rights on the subscription.

### Pitfalls and Mitigation

* **Missing SSH Key Pair**: The script requires a public key file at `~/.ssh/libcloud_azure_key.pub`. Generate a pair first using `ssh-keygen -t rsa -b 2048 -f ~/.ssh/libcloud_azure_key`.
* **Location Mismatch**: The B1s size is only available in specific regions (e.g., `eastus`, `westus2`, `westeurope`). Using an unsupported location will trigger a `CloudError`.
* **Resource Group Collision**: If a group with the same name exists and contains conflicting resources, the script will fail. Use a unique suffix or delete the existing group.
* **Quota Limits**: The free tier typically allows a single B1s VM per region. If another B1s VM is running, the `create_vm` call will fail with a quota exceeded error.
* **Network Rule Idempotency**: The helper module handles duplicate rule errors, ensuring that rerunning the script does not create redundant security rules.

### Consolidated Implementation

For a single-file deployment, the following consolidated script includes all helpers and orchestration logic.

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
print("\nDeleting resource group ...")
delete_rg(rg_client, RG_NAME)
try:
    os.remove(os.path.expanduser("~/.ssh/libcloud_azure_key"))
except OSError:
    pass
print("All resources removed.")
```

## Summary Checklist

* [ ] Install the Azure SDK using a virtual environment or Docker.
* [ ] Create a service principal and populate `clouds.yaml` with the credentials.
* [ ] Generate a local SSH key pair.
* [ ] Run the orchestration script to deploy the B1s instance.
* [ ] Verify SSH connectivity using the printed command.
* [ ] Run the script with the `--destroy` flag to remove all resources.

## Assignments

!!! note "Assignment.1: Native SDK Deployment"
    Configure your `clouds.yaml` file and use the provided SDK scripts to deploy a free-tier B1s VM in your chosen Azure region. Confirm the deployment by SSHing into the instance and checking the OS version.

    ??? tip "Solution: Native SDK Deployment"
        Follow the installation steps. Ensure your service principal has the Contributor role. Run `python run_azure_free_vm.py` and use the resulting SSH command.

!!! note "Assignment.2: Regional Validation"
    Modify the `location` in `clouds.yaml` to a different free-tier eligible region (e.g., `westus2`). Run the script and verify that the VM is still deployed successfully under the free tier.

    ??? tip "Solution: Regional Validation"
        Change `location: eastus` to `location: westus2` in `clouds.yaml`. Rerun the script; since the helper functions handle regional parameters, no other changes should be necessary.

!!! note "Assignment.3: SDK Extension"
    Add a function to `azure_helpers.py` that lists all virtual machines within the current resource group, printing their name and current power state.

    ??? tip "Solution: SDK Extension"
        Use `compute_client.virtual_machines.list(rg_name)` to get a list of VM objects, then call `compute_client.virtual_machines.get(rg_name, vm_name, expand='instanceView')` for each VM to access the `power_state` in the `instance_view` attribute.

## References

* Azure SDK for Python documentation - <https://learn.microsoft.com/python/azure/>
* `azure-identity` (service-principal authentication) - <https://learn.microsoft.com/python/api/azure-identity/azure.identity.clientsecretcredential>
* `azure-mgmt-resource` - resource-group management - <https://learn.microsoft.com/python/api/azure-mgmt-resource/azure.mgmt.resource.resourcemanagementclient>
* `azure-mgmt-network` - VNet, subnet, public IP, NSG, NIC - <https://learn.microsoft.com/python/api/azure-mgmt-network/>
* `azure-mgmt-compute` - VM creation - <https://learn.microsoft.com/python/api/azure-mgmt-compute/>
* Azure Free Tier details - <https://azure.microsoft.com/free/>
* Creating a service principal - <https://learn.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal>

## Self-Evaluation

??? note "Why is a service principal preferred over interactive login for SDK scripts?"
    Interactive login requires a browser and user intervention, which is impossible in automated pipelines or headless environments. A service principal provides a set of credentials (Client ID and Secret) that the SDK can use to authenticate autonomously.

??? note "What is the importance of the Standard_B1s VM size in this workflow?"
    The `Standard_B1s` size is the specific VM tier that is free-tier eligible for new Azure accounts for the first 12 months. Using any other size would incur immediate costs.

??? note "How does the Azure SDK manage asynchronous resource creation?"
    Many Azure SDK operations (like creating a VM or a VNet) return a poller object (e.g., `begin_create_or_update`). The script must call `.result()` on this poller to block execution until the resource is fully provisioned in the Azure cloud.
