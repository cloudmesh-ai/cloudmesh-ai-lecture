# Azure CLI Installation and Free-Tier Setup

!!! info "Learning Objectives"
    * Create and configure a free Azure account.
    * Install the Azure CLI using isolated methods to avoid host system conflicts.
    * Authenticate the CLI using both interactive device-code and non-interactive service principal flows.
    * Provision essential Azure networking resources, including Resource Groups, Virtual Networks, and Network Security Groups.
    * Deploy a free-tier B1s Linux virtual machine.
    * Establish a secure SSH connection to the deployed VM.
    * Implement a comprehensive cleanup strategy to ensure no unexpected charges.

## Overview

This chapter provides a comprehensive guide to deploying a virtual machine on Microsoft Azure using the Azure CLI. It covers the entire process from account acquisition to resource termination, focusing on the Azure Free Tier and isolated tool installation to maintain a clean workstation environment.

## Core Sections

### Account Setup

To begin using Azure services, you must first establish a subscription and an identity.

#### Azure Free Tier Offerings

The Azure free account provides various resources for 12 months. Notable offerings include:

| Resource | Limit | Usage Note |
|----------|-------|-------------|
| B1s Linux/Windows VM | 750 hours/month | One B1s VM at a time |
| Azure Blob Storage | 5 GB (Hot tier) | File storage and static sites |
| Managed SQL Database | 250 GB (General Purpose) | Optional database usage |
| Outbound Bandwidth | 15 GB per month | Data egress traffic |

To create an account:
1. Visit <https://azure.microsoft.com/free/> and select **Start Free**.
2. Sign in with or create a Microsoft account.
3. Provide billing information for identity verification (a small temporary authorization may occur).
4. Accept the terms and complete the registration process.

#### Identity Management

Once the account is created, you are logged in as the subscription owner. For production or daily operations, it is recommended to use Azure Active Directory (Azure AD) users or service principals instead of the owner account.

### Azure CLI Installation

To maintain system stability, use one of the following isolated installation methods.

#### Docker Isolation

This method runs the CLI in a container, mounting the necessary configuration and SSH directories.

```bash
# Pull the official Azure CLI image
docker pull mcr.microsoft.com/azure-cli

# Create a wrapper script for direct 'az' command access
cat <<'EOF' > ~/bin/az
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.azure:/root/.azure:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  mcr.microsoft.com/azure-cli "$@"
EOF
chmod +x ~/bin/az
export PATH=$HOME/bin:$PATH
```

#### Native Installer

The Azure CLI is available for multiple operating systems via official scripts or package managers.

| OS | Installation Command |
|----|----------------------|
| Linux (Debian/Ubuntu) | `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash` |
| Linux (RHEL/CentOS) | `sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc` then run script from <https://aka.ms/InstallAzureCLIRpm> |
| macOS | `brew update && brew install azure-cli` |
| Windows | Use the MSI installer from <https://aka.ms/installazurecliwindows> |

#### pipx Sandbox

Install the CLI in an isolated Python environment using `pipx`.

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install azure-cli
```

Verify the installation by running `az version`.

### CLI Authentication

Before executing resource commands, you must authenticate your session.

#### Interactive Login

The device-code flow is the simplest method and works well within Docker containers.

```bash
az login --use-device-code
```

Follow the instructions provided in the terminal: open the specified URL in a browser and enter the displayed code.

#### Non-Interactive Login (Service Principal)

For automation scripts, create a service principal with the Contributor role.

```bash
# Retrieve the current subscription ID
SUB_ID=$(az account show --query id -o tsv)

# Create the service principal
az ad sp create-for-rbac \
  --name "cli-free-sp" \
  --role Contributor \
  --scopes /subscriptions/$SUB_ID \
  --sdk-auth > sp-auth.json
```

To authenticate using the generated `sp-auth.json` file:

```bash
az login --service-principal \
  --username "$(jq -r .clientId sp-auth.json)" \
  --password "$(jq -r .clientSecret sp-auth.json)" \
  --tenant   "$(jq -r .tenantId   sp-auth.json)"
```

### Provisioning the Free-Tier VM

Azure resources are organized into **Resource Groups**. The following workflow creates the minimum necessary infrastructure for a functional Linux VM.

#### Infrastructure Deployment

```bash
# Variables
RG_NAME="rg-free-demo"
LOCATION="eastus"
VM_NAME="freevm"
VNET_NAME="vnet-free"
SUBNET_NAME="subnet-free"
IP_NAME="ip-free"
NSG_NAME="nsg-free"
NIC_NAME="nic-free"
ADMIN_USERNAME="azureuser"
SSH_KEY_PATH="$HOME/.ssh/azure_free_key"

# 1. Create a resource group
az group create \
  --name $RG_NAME \
  --location $LOCATION \
  --output none

# 2. Generate an SSH key pair (if missing)
if [ ! -f "$SSH_KEY_PATH" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY_PATH -N "" -C "azure_free_key"
fi

# 3. Create a virtual network and subnet
az network vnet create \
  --resource-group $RG_NAME \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.0.0/24 \
  --output none

# 4. Create a static public IP address
az network public-ip create \
  --resource-group $RG_NAME \
  --name $IP_NAME \
  --sku Standard \
  --allocation-method Static \
  --output none

# 5. Create a network security group and allow inbound SSH (port 22)
az network nsg create \
  --resource-group $RG_NAME \
  --name $NSG_NAME \
  --output none

az network nsg rule create \
  --resource-group $RG_NAME \
  --nsg-name $NSG_NAME \
  --name Allow-SSH \
  --priority 1000 \
  --protocol Tcp \
  --direction Inbound \
  --source-address-prefixes "*" \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 22 \
  --access Allow \
  --output none

# 6. Create a NIC and associate it with the network components
az network nic create \
  --resource-group $RG_NAME \
  --name $NIC_NAME \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME \
  --network-security-group $NSG_NAME \
  --public-ip-address $IP_NAME \
  --output none

# 7. Create the B1s Linux VM (Ubuntu LTS)
az vm create \
  --resource-group $RG_NAME \
  --name $VM_NAME \
  --nics $NIC_NAME \
  --image UbuntuLTS \
  --size Standard_B1s \
  --admin-username $ADMIN_USERNAME \
  --ssh-key-values "$SSH_KEY_PATH.pub" \
  --generate-ssh-keys false \
  --output none
```

#### Fetching the Public IP

```bash
PUBLIC_IP=$(az network public-ip show \
  --resource-group $RG_NAME \
  --name $IP_NAME \
  --query ipAddress -o tsv)

echo "VM is ready. Public IP: $PUBLIC_IP"
```

### Connectivity and Management

Once the VM is running, connect using the private key created during provisioning.

#### SSH Connection

```bash
ssh -i "$SSH_KEY_PATH" ${ADMIN_USERNAME}@${PUBLIC_IP}
```

#### Management Commands

| Goal | Azure CLI Command | Description |
|------|-------------------|-------------|
| List VMs | `az vm list -g $RG_NAME -d -o table` | Shows power state and public IP |
| Stop VM | `az vm stop -g $RG_NAME -n $VM_NAME --no-wait` | Deallocates compute resources |
| Start VM | `az vm start -g $RG_NAME -n $VM_NAME` | Powers the VM back on |
| Delete VM | `az vm delete -g $RG_NAME -n $VM_NAME --yes` | Removes the VM only |
| Delete RG | `az group delete -n $RG_NAME --yes --no-wait` | Removes all resources in the group |
| Check Usage | `az consumption usage list --subscription $(az account show --query id -o tsv) --start-date $(date +%Y-%m-01) --end-date $(date +%Y-%m-%d) -o table` | Lists monthly usage |

### Resource Cleanup

To prevent charges, it is critical to remove all resources. The most efficient method is deleting the entire resource group.

#### Group-Level Deletion

```bash
az group delete \
  --name $RG_NAME \
  --yes \
  --no-wait
```

#### Granular Deletion

If only specific resources should be removed:

```bash
# Deallocate and delete the VM
az vm deallocate -g $RG_NAME -n $VM_NAME --no-wait
az vm delete -g $RG_NAME -n $VM_NAME --yes

# Delete networking resources
az network nic delete -g $RG_NAME -n $NIC_NAME --yes
az network public-ip delete -g $RG_NAME -n $IP_NAME --yes
az network nsg delete -g $RG_NAME -n $NSG_NAME --yes
az network vnet delete -g $RG_NAME -n $VNET_NAME --yes

# Final cleanup of the resource group
az group delete -n $RG_NAME --yes
```

### Deployment Cheat Sheet

This consolidated block provides the full workflow in one sequence.

```bash
# 1. Install isolated Azure CLI (Docker wrapper)
cat <<'EOF' > ~/bin/az
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.azure:/root/.azure:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  mcr.microsoft.com/azure-cli "$@"
EOF
chmod +x ~/bin/az
export PATH=$HOME/bin:$PATH

# 2. Log in interactively
az login --use-device-code

# 3. Define variables
RG="rg-free-demo"
LOC="eastus"
VM="freevm"
VNET="vnet-free"
SUBNET="subnet-free"
IP="ip-free"
NSG="nsg-free"
NIC="nic-free"
ADMIN="azureuser"
SSH_KEY="$HOME/.ssh/azure_free_key"

# 4. Create resource group
az group create -n $RG -l $LOC --output none

# 5. Create SSH key pair
if [ ! -f "$SSH_KEY" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY -N "" -C "azure_free_key"
fi

# 6. Networking components
az network vnet create -g $RG -n $VNET --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET --subnet-prefix 10.0.0.0/24 --output none

az network public-ip create -g $RG -n $IP --sku Standard --allocation-method Static --output none

az network nsg create -g $RG -n $NSG --output none
az network nsg rule create -g $RG --nsg-name $NSG -n Allow-SSH \
  --priority 1000 --protocol Tcp --direction Inbound \
  --source-address-prefixes "*" --source-port-ranges "*" \
  --destination-address-prefixes "*" --destination-port-ranges 22 \
  --access Allow --output none

az network nic create -g $RG -n $NIC \
  --vnet-name $VNET --subnet $SUBNET \
  --network-security-group $NSG \
  --public-ip-address $IP \
  --output none

# 7. Create the free-tier B1s VM
az vm create \
  -g $RG -n $VM \
  --nics $NIC \
  --image UbuntuLTS \
  --size Standard_B1s \
  --admin-username $ADMIN \
  --ssh-key-values "$SSH_KEY.pub" \
  --generate-ssh-keys false \
  --output none

# 8. Get public IP and SSH
PUBLIC_IP=$(az network public-ip show -g $RG -n $IP --query ipAddress -o tsv)
echo "VM public IP: $PUBLIC_IP"
ssh -i "$SSH_KEY" ${ADMIN}@${PUBLIC_IP}

# 9. Clean up (delete whole resource group)
az group delete -n $RG --yes --no-wait
```

## Summary Checklist

* [ ] Azure free account created and verified.
* [ ] Azure CLI installed via an isolated method.
* [ ] CLI authenticated via device-code or service principal.
* [ ] Resource group and network components provisioned.
* [ ] B1s VM deployed and reachable via SSH.
* [ ] All resources deleted to prevent charges.

## Assignments

!!! note "Assignment.1: End-to-End Provisioning"
    Complete the full deployment pipeline: install the CLI, authenticate, and launch a B1s instance. Verify connectivity by executing `lsb_release -a` on the remote machine.

    ??? tip "Solution: End-to-End Provisioning"
        Follow the "Deployment Cheat Sheet" section. Ensure you use the correct private key and that the VM size is exactly `Standard_B1s` to remain in the free tier.

!!! note "Assignment.2: Automation Identity"
    Create a service principal and use it to log in to the Azure CLI. Use this identity to list the resource groups in your subscription.

    ??? tip "Solution: Automation Identity"
        Use the `az ad sp create-for-rbac` command provided in the authentication section, save the output to a file, and use `az login --service-principal` with the corresponding fields.

!!! note "Assignment.3: Network Hardening"
    Modify the Network Security Group (NSG) rule created in this chapter. Change the `source-address-prefixes` from `*` to your current public IP address, then verify that SSH access is still possible from your machine but blocked from others.

    ??? tip "Solution: Network Hardening"
        Use `az network nsg rule update` or delete and recreate the rule, replacing `*` with your public IP (which you can find via `curl ifconfig.me`).

  ## References

  | Resource | Description |
  |----------|-------------|
  | Azure CLI Reference | <https://learn.microsoft.com/cli/azure/> |
  | Azure Free Account | <https://azure.microsoft.com/free/> |
  | B-series VM Docs | <https://learn.microsoft.com/azure/virtual-machines/b-series-burstable> |
  | Azure RBAC Best Practices | <https://learn.microsoft.com/azure/role-based-access-control/best-practices> |
  | Azure Cloud Shell | <https://learn.microsoft.com/azure/cloud-shell/> |

  ## Self-Evaluation

??? note "What is the primary purpose of a Resource Group in Azure?"
    A Resource Group is a logical container that allows you to group and manage related Azure resources (e.g., VM, VNet, Disk) as a single entity. This simplifies management and allows for the simultaneous deletion of all resources associated with a specific project or environment.

??? note "What is the significance of the Standard_B1s VM size?"
    The `Standard_B1s` size is specifically designated as free-tier eligible for the first 12 months of a new Azure account. Using larger sizes will result in immediate charges to the subscription.

??? note "Why is deallocating a VM different from simply stopping it?"
    In Azure, simply stopping a VM from within the guest OS still keeps the compute resources allocated to the VM, meaning you may still be charged. Deallocating the VM (via `az vm deallocate` or the portal) releases the compute hardware, stopping the compute charges completely.
