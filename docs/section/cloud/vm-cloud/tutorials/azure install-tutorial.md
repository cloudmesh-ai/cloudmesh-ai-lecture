
**Azure CLI – Free‑Tier Tutorial (plain text, no emojis or numbered icons)**  

The steps below show how to:

* Sign up for an Azure free account.  
* Install the Azure CLI in an isolated way (Docker, official installer, or pipx).  
* Create the minimum set of Azure resources needed to run a Linux virtual machine that you can SSH into, staying within the Azure free tier (B1s VM, 750 h / month).  
* Connect to the VM with SSH.  
* Clean up all resources so you are not charged after the demo.  

All commands assume the Azure CLI is available as `az`. If you use the Docker wrapper, prepend `az` with the wrapper script shown in the installation section.

---

## Get an Azure free account  

| Free‑tier offering (12 months) | Typical limits |
|--------------------------------|----------------|
| B1s Linux or Windows VM – 750 h / month (1 vCPU, 1 GiB RAM) | Only one B1s VM can be running at a time. |
| 5 GiB Azure Blob storage (Hot tier) | Good for file storage, static sites. |
| 250 GB managed SQL Database (General Purpose) | Optional. |
| 15 GiB outbound bandwidth per month | Mostly for egress traffic. |
| Various other services – free tier per month | Pay‑as‑you‑go beyond the free amount. |

### How to create the account  

1. Open <https://azure.microsoft.com/free/> and click **Start Free**.  
2. Sign in with a Microsoft account (or create one).  
3. Provide a credit‑card or debit‑card for identity verification. Azure will perform a small $0‑$1 authorization that is released immediately.  
4. Accept the terms and complete the registration.  
5. After the portal opens, you are logged in as the **subscription owner**.  

> **Tip:** Do not use this account for production workloads. Create a regular Azure AD user or a service principal for day‑to‑day work (see the “Authenticate the CLI” section).

---

## Install Azure CLI in an isolated environment  

Choose one of the three methods. All give you a working `az` binary without affecting the host system.

### Docker (complete isolation)

```bash
# Pull the official Azure CLI image (≈150 MiB)
docker pull mcr.microsoft.com/azure-cli

# Create a thin wrapper script so you can type “az” normally
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
export PATH=$HOME/bin:$PATH   # add to your shell rc file (.bashrc/.zshrc)
```

* `~/.azure` stores login tokens and CLI configuration.  
* `~/.ssh` is mounted read‑only so the container can use your private key for SSH later.

### Official installer (Linux/macOS/Windows)

| OS | Commands |
|----|----------|
| Linux (Debian/Ubuntu) | `curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash` |
| Linux (RHEL/CentOS)   | `sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc` followed by the script from <https://aka.ms/InstallAzureCLIRpm> |
| macOS (brew)          | `brew update && brew install azure-cli` |
| Windows (PowerShell)  | `Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -ArgumentList '/i AzureCLI.msi /quiet' -Wait` |

### pipx (Python sandbox)

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install azure-cli
```

Verify the installation:

```bash
az version
# Expected output: Azure CLI 2.x.x
```

---

## Authenticate the CLI  

The first time you run `az`, you must log in. Use the interactive device‑code flow (works inside Docker as well):

```bash
az login --use-device-code
```

A device code and URL will be displayed; open the URL in a browser, paste the code, and sign in with the account you created.

If you need a non‑interactive login for scripts, create a service principal with the minimal role required:

```bash
# Get the current subscription id
SUB_ID=$(az account show --query id -o tsv)

# Create the service principal and assign the Contributor role on the subscription
az ad sp create-for-rbac \
  --name "cli-free-sp" \
  --role Contributor \
  --scopes /subscriptions/$SUB_ID \
  --sdk-auth > sp-auth.json
```

`sp-auth.json` contains the credentials in JSON format. You can log in non‑interactively with:

```bash
az login --service-principal \
  --username "$(jq -r .clientId sp-auth.json)" \
  --password "$(jq -r .clientSecret sp-auth.json)" \
  --tenant   "$(jq -r .tenantId   sp-auth.json)"
```

For the remainder of this tutorial the interactive login is sufficient.

---

## Create the minimal free‑tier VM  

Azure resources are grouped in a **resource group**. The commands below create:

* a resource group (`rg-free-demo`) in the `eastus` region (a free‑tier region).  
* an SSH key pair (if you don’t already have one).  
* a virtual network and subnet.  
* a static public IP address.  
* a network security group (NSG) that allows inbound TCP 22 (SSH).  
* a network interface (NIC) attached to the above components.  
* a B1s Linux VM (Ubuntu 22.04 LTS) using a free‑tier eligible image.

All commands suppress JSON output (`--output none`) for brevity; remove that flag if you want to see the full response.

```bash
# -------------------------------------------------
# Variables – change only if you want different names
RG_NAME="rg-free-demo"
LOCATION="eastus"                 # free‑tier region
VM_NAME="freevm"
VNET_NAME="vnet-free"
SUBNET_NAME="subnet-free"
IP_NAME="ip-free"
NSG_NAME="nsg-free"
NIC_NAME="nic-free"
ADMIN_USERNAME="azureuser"
SSH_KEY_PATH="$HOME/.ssh/azure_free_key"
# -------------------------------------------------
# 1. Create a resource group
az group create \
  --name $RG_NAME \
  --location $LOCATION \
  --output none

# 2. Generate an SSH key pair (skip if you already have one)
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

# 6. Create a NIC and associate it with the subnet, public IP, and NSG
az network nic create \
  --resource-group $RG_NAME \
  --name $NIC_NAME \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME \
  --network-security-group $NSG_NAME \
  --public-ip-address $IP_NAME \
  --output none

# 7. Create the Linux VM (Ubuntu LTS) – B1s size is free‑tier eligible
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

# 8. Get the public IP address of the VM
PUBLIC_IP=$(az network public-ip show \
  --resource-group $RG_NAME \
  --name $IP_NAME \
  --query ipAddress -o tsv)

echo "VM is ready. Public IP: $PUBLIC_IP"
```

**Important notes**

* The **B1s** size (`Standard_B1s`) is the free‑tier eligible VM type. Keeping the VM stopped for the rest of the month stays within the 750 h free allowance.  
* The NSG rule above opens port 22 from any source (`*`). For tighter security replace `*` with your public IP address or a CIDR range.  
* The public IP is static; if you prefer a dynamic IP, change `--allocation-method Dynamic`.

---

## SSH into the VM  

```bash
ssh -i "$SSH_KEY_PATH" ${ADMIN_USERNAME}@${PUBLIC_IP}
```

You should see a prompt similar to:

```
azureuser@<hostname>:~$
```

You are now logged into the free‑tier Azure VM and can run any Linux commands you need.

---

## Useful starter commands (free‑tier safe)

| Goal | Azure CLI command | Description |
|------|-------------------|-------------|
| List VMs in the resource group | `az vm list -g $RG_NAME -d -o table` | Shows name, power state, public IP, size |
| Stop the VM (no compute charges while stopped) | `az vm stop -g $RG_NAME -n $VM_NAME --no-wait` | Deallocates the VM |
| Start the VM again | `az vm start -g $RG_NAME -n $VM_NAME` | Powers the VM back on |
| Deallocate (release compute resources) | `az vm deallocate -g $RG_NAME -n $VM_NAME` | Same as `stop` but frees the underlying hardware |
| Delete the VM (remove compute) | `az vm delete -g $RG_NAME -n $VM_NAME --yes` | Destroys the VM but leaves other resources |
| Delete the entire resource group (clean‑up all resources at once) | `az group delete -n $RG_NAME --yes --no-wait` | Removes every resource created above |
| Show current month’s free‑tier usage (preview) | `az consumption usage list --subscription $(az account show --query id -o tsv) --start-date $(date +%Y-%m-01) --end-date $(date +%Y-%m-%d) -o table` | Lists usage per meter; filter for “Virtual Machines B-series” to see remaining free hours |

---

## Clean‑up – Ensure no ongoing charges  

The simplest way is to delete the whole resource group:

```bash
az group delete \
  --name $RG_NAME \
  --yes \
  --no-wait
```

If you prefer a more granular approach:

```bash
# Deallocate the VM (stops compute charges)
az vm deallocate -g $RG_NAME -n $VM_NAME --no-wait

# Delete the VM (keeps NIC, IP, etc.)
az vm delete -g $RG_NAME -n $VM_NAME --yes

# Delete networking resources
az network nic delete -g $RG_NAME -n $NIC_NAME --yes
az network public-ip delete -g $RG_NAME -n $IP_NAME --yes
az network nsg delete -g $RG_NAME -n $NSG_NAME --yes
az network vnet delete -g $RG_NAME -n $VNET_NAME --yes

# Finally delete the resource group (removes any leftover tags, disks, etc.)
az group delete -n $RG_NAME --yes
```

After the deletion completes, verify in the Azure portal that no resources remain. The free‑tier subscription will not accrue any further charges.

---

## Quick reference cheat sheet (copy‑paste)

```bash
# -------------------------------------------------
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
export PATH=$HOME/bin:$PATH   # add to your shell rc file

# -------------------------------------------------
# 2. Log in interactively (device code flow works inside Docker)
az login --use-device-code

# -------------------------------------------------
# 3. Define reusable variables
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

# -------------------------------------------------
# 4. Create resource group
az group create -n $RG -l $LOC --output none

# -------------------------------------------------
# 5. Create SSH key pair (if missing)
if [ ! -f "$SSH_KEY" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY -N "" -C "azure_free_key"
fi

# -------------------------------------------------
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

# -------------------------------------------------
# 7. Create the free‑tier B1s VM (Ubuntu LTS)
az vm create \
  -g $RG -n $VM \
  --nics $NIC \
  --image UbuntuLTS \
  --size Standard_B1s \
  --admin-username $ADMIN \
  --ssh-key-values "$SSH_KEY.pub" \
  --generate-ssh-keys false \
  --output none

# -------------------------------------------------
# 8. Get public IP and SSH
PUBLIC_IP=$(az network public-ip show -g $RG -n $IP --query ipAddress -o tsv)
echo "VM public IP: $PUBLIC_IP"
ssh -i "$SSH_KEY" ${ADMIN}@${PUBLIC_IP}

# -------------------------------------------------
# 9. Clean up when finished (delete whole resource group)
az group delete -n $RG --yes --no-wait
```

Run the sections sequentially (or place the whole block into a script) to provision a free‑tier Azure Linux VM, SSH into it, and then remove all resources afterward.

---

## Further reading  

| Resource | What you’ll find |
|----------|------------------|
| Azure CLI reference | <https://learn.microsoft.com/cli/azure/> |
| Azure free account details | <https://azure.microsoft.com/free/> |
| B‑series (free‑tier) VM documentation | <https://learn.microsoft.com/azure/virtual-machines/b-series-burstable> |
| Azure role‑based access control (RBAC) best practices | <https://learn.microsoft.com/azure/role-based-access-control/best-practices> |
| Azure Cloud Shell (browser‑based CLI, no installation) | <https://learn.microsoft.com/azure/cloud-shell/> |

You now have a complete, plain‑text workflow for obtaining an Azure free account, installing the CLI safely, provisioning a free‑tier Ubuntu VM, connecting via SSH, and cleaning up afterwards. Happy cloud experimenting!