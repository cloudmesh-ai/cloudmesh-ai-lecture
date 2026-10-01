
**Oracle Cloud Infrastructure – Free‑Tier Tutorial (plain text, no emojis or numbered icons)**  

The guide below walks you through the entire process of using the Oracle Cloud **Always‑Free** tier:  

* creating a free Oracle Cloud account,  
* installing the OCI CLI in an isolated way,  
* provisioning the smallest always‑free compute instance,  
* connecting to it with SSH,  
* and cleaning up the resources when you are finished.  

All commands assume the CLI is available as `oci`. If you use the Docker wrapper, prepend `oci` with the wrapper script shown in the installation section.

---

## 1. Obtain an Oracle Cloud free account  

| Free‑tier benefit (always free) | Limits (per month) |
|--------------------------------|--------------------|
| **Compute** – two shapes: <br>• VM.Standard.A1.Flex (Arm) – up to 4 OCPU total, 24 GB RAM <br>• VM.Standard.E2.1.Micro (AMD) – 1 OCPU, 1 GB RAM | The shapes can run continuously (720 h / month). |
| **Block Volume** – 100 GB standard SSD | Persistent block storage attached to a VM. |
| **Object Storage** – 10 GB standard | Object storage for files, static sites, etc. |
| **Outbound Data Transfer** – 10 TB per month | Data egress to the internet. |
| **Autonomous Database** – 2 TB total storage (always‑free version) | Optional managed database. |
| **Load Balancer** – 1 TB data processing | Only the “always‑free” load balancer is covered. |

### Sign‑up steps  

1. Open <https://cloud.oracle.com/> and click **Start for free**.  
2. Sign in with an existing Oracle account or create a new one.  
3. Provide a credit‑card or debit‑card for identity verification; Oracle performs a $0‑$1 authorization that is released immediately.  
4. Accept the terms and complete the registration.  
5. After the console loads you are the **Administrator** of a tenancy that includes the always‑free resources.  

> **Important:** The free tier is **not time‑limited**. As long as you stay within the listed limits, you will not be charged.

---

## 2. Install the OCI CLI in an isolated environment  

Choose one of the three methods; each gives you a usable `oci` binary without touching your system Python or global packages.

### Docker (complete isolation)

```bash
# Pull the official OCI CLI image (≈300 MiB)
docker pull oraclelinux:8   # base image
docker pull ghcr.io/oracle/oci-cli:latest

# Create a small wrapper script so you can type “oci” directly
cat <<'EOF' > ~/bin/oci
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.oci:/root/.oci:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  ghcr.io/oracle/oci-cli:latest "$@"
EOF
chmod +x ~/bin/oci
export PATH=$HOME/bin:$PATH   # add to your shell rc file (.bashrc/.zshrc)
```

* `~/.oci` stores the configuration file (`config`) and the API key pair.  
* `~/.ssh` is mounted read‑only so the container can use the private key for later SSH connections.

### Official installer (Linux/macOS)

```bash
# Linux (bash)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)" \
  -- -b ~/bin

# macOS (Homebrew)
brew install oci-cli
```

The installer creates `~/bin/oci` and writes a `~/.oci/config` file the first time you run `oci setup config`.

### pipx (Python sandbox)

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install oci-cli
```

Verify the installation:

```bash
oci --version
# Expected output: Oracle Cloud Infrastructure CLI version X.Y.Z
```

---

## 3. Configure the CLI (API key authentication)

The OCI CLI uses an RSA key pair and a tenancy‑level API key. The following steps create the key pair, register it, and write the configuration file. The process works the same whether you are using the Docker wrapper or a native install.

```bash
# Create a directory for the OCI configuration if it does not exist
mkdir -p ~/.oci

# Generate an RSA key pair (2048‑bit) – do not use a passphrase for automation
openssl genrsa -out ~/.oci/oci_api_key.pem 2048
chmod 600 ~/.oci/oci_api_key.pem
openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem

# Log in to the OCI Console (https://cloud.oracle.com/) as the tenancy administrator.
# In the navigation menu go to **Identity → Users**, click your user name, then **API Keys → Add API Key**.
# Choose **Upload public key** and select the file `~/.oci/oci_api_key_public.pem`.
# After the key is added, click **Download .pem file** – this is the **private key** for the API key.
# Save the downloaded private key as `~/.oci/oci_api_key.pem` (overwrite the file created above if you wish).

# Create the CLI configuration file
cat <<EOF > ~/.oci/config
[DEFAULT]
user=ocid1.user.oc1..YOUR_USER_OCID
fingerprint=YOUR_KEY_FINGERPRINT
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..YOUR_TENANCY_OCID
region=us-ashburn-1
EOF
```

*You can obtain the OCIDs and the key fingerprint from the OCI Console under **Identity → Users → (your user) → API Keys**.*

Test the configuration:

```bash
oci os ns get   # should return the Object Storage namespace of your tenancy
```

If the command returns a namespace value, the CLI is correctly authenticated.

---

## 4. Create the networking components required for a VM

The free tier does not include a default VCN that allows SSH, so we create a custom VCN, subnet, internet gateway, route table, and security list.

```bash
# -------------------------------------------------
# Variables – adjust if you prefer different names
COMPARTMENT_ID=$(oci iam compartment list --query "data[?\"name\"=='$COMPARTMENT_NAME'].id | [0]" --raw-output 2>/dev/null || echo "ocid1.compartment.oc1..default")
VCN_NAME="free-vcn"
SUBNET_NAME="free-subnet"
IGW_NAME="free-igw"
RT_NAME="free-rt"
SL_NAME="free-sl"
CIDR_BLOCK="10.0.0.0/16"
SUBNET_CIDR="10.0.0.0/24"
# -------------------------------------------------
# 1️⃣ Create a VCN
VCN_ID=$(oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --display-name $VCN_NAME \
  --cidr-block $CIDR_BLOCK \
  --query "data.id" \
  --raw-output)

# 2️⃣ Create a subnet
SUBNET_ID=$(oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $SUBNET_NAME \
  --cidr-block $SUBNET_CIDR \
  --query "data.id" \
  --raw-output)

# 3️⃣ Create an Internet Gateway
IGW_ID=$(oci network internet-gateway create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $IGW_NAME \
  --is-enabled true \
  --query "data.id" \
  --raw-output)

# 4️⃣ Create a Route Table that sends 0.0.0.0/0 traffic to the Internet Gateway
RT_ID=$(oci network route-table create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $RT_NAME \
  --route-rules '[{"cidr":"0.0.0.0/0","networkEntityId":"'"$IGW_ID"'"}]' \
  --query "data.id" \
  --raw-output)

# 5️⃣ Associate the Route Table with the subnet
oci network subnet update \
  --subnet-id $SUBNET_ID \
  --route-table-id $RT_ID

# 6️⃣ Create a Security List that allows inbound SSH (port 22) from anywhere
SL_ID=$(oci network security-list create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $SL_NAME \
  --egress-security-rules '[{"destination":"0.0.0.0/0","protocol":"6","isStateless":false,"tcpOptions":{"destinationPortRange":{"max":65535,"min":1}}}]' \
  --ingress-security-rules '[{"source":"0.0.0.0/0","protocol":"6","isStateless":false,"tcpOptions":{"destinationPortRange":{"max":22,"min":22}}}]' \
  --query "data.id" \
  --raw-output)

# 7️⃣ Associate the Security List with the subnet (replaces the default one)
oci network subnet update \
  --subnet-id $SUBNET_ID \
  --security-list-ids '["'"$SL_ID"'"]'
```

The subnet now has a route to the internet and a security list that permits inbound SSH from any IP address. For tighter security replace `0.0.0.0/0` with your own public IP CIDR.

---

## 5. Generate an SSH key pair (if you don’t have one)

```bash
SSH_KEY="$HOME/.ssh/oci_free_key"
if [ ! -f "$SSH_KEY" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY -N "" -C "oci_free_key"
fi
chmod 600 "$SSH_KEY"
```

The public key (`$SSH_KEY.pub`) will be injected into the VM during launch.

---

## 6. Launch an always‑free compute instance  

We will use the **VM.Standard.E2.1.Micro** shape (AMD) because it is included in the free tier and requires only 1 OCPU and 1 GB RAM. The Arm‑based `VM.Standard.A1.Flex` shape is also free, but it needs explicit OCPU count and memory specifications.

```bash
# -------------------------------------------------
# Variables for the instance
INSTANCE_NAME="free-instance"
SHAPE="VM.Standard.E2.1.Micro"
IMAGE_OCID=$(oci compute image list \
  --compartment-id $COMPARTMENT_ID \
  --operating-system "Oracle Linux" \
  --operating-system-version "8" \
  --query "data[?\"displayName\"=='Oracle-Linux-8.9-2024.04.09-0'] | [0].id" \
  --raw-output)   # Adjust the display name if a newer image exists

# Create the instance
INSTANCE_ID=$(oci compute instance launch \
  --compartment-id $COMPARTMENT_ID \
  --display-name $INSTANCE_NAME \
  --availability-domain $(oci iam availability-domain list --query "data[0].name" --raw-output) \
  --shape $SHAPE \
  --subnet-id $SUBNET_ID \
  --image-id $IMAGE_OCID \
  --ssh-authorized-keys-file "$SSH_KEY.pub" \
  --assign-public-ip true \
  --query "data.id" \
  --raw-output)

echo "Instance launched with OCID: $INSTANCE_ID"
```

**Note:** The `--assign-public-ip true` flag creates a public IPv4 address automatically.

### Retrieve the public IP address

```bash
PUBLIC_IP=$(oci compute instance list-vnics \
  --instance-id $INSTANCE_ID \
  --query "data[0].\"public-ip\"" \
  --raw-output)

echo "Instance public IP: $PUBLIC_IP"
```

---

## 7. SSH into the instance  

```bash
ssh -i "$SSH_KEY" opc@$PUBLIC_IP
```

* The default user for Oracle Linux images is **opc**.  
* For Ubuntu images the user would be **ubuntu**, for CentOS **centos**, etc.  

You should see a shell prompt similar to:

```
[opc@instance-1 ~]$
```

You are now connected to a running always‑free Oracle Cloud compute instance.

---

## 8. Useful always‑free commands  

| Goal | OCI CLI command | Description |
|------|-----------------|-------------|
| List all compute instances in the compartment | `oci compute instance list --compartment-id $COMPARTMENT_ID -c table` | Shows name, shape, lifecycle state, public IP (if any). |
| Stop the instance (no compute charges while stopped) | `oci compute instance action --instance-id $INSTANCE_ID --action STOP` | Deallocates the VM; you still keep the attached block volume. |
| Start the instance again | `oci compute instance action --instance-id $INSTANCE_ID --action START` | Powers the VM back on. |
| Terminate (delete) the instance | `oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false --force` | Removes the VM and any attached boot volume. |
| Create an additional block volume (still free up to 100 GB) | `oci bv volume create --availability-domain $(oci iam availability-domain list --query "data[0].name" --raw-output) --compartment-id $COMPARTMENT_ID --size-in-gbs 50 --display-name my-volume` | Creates a 50 GB volume; you can attach it later. |
| List current month’s free‑tier usage (preview) | `oci usage api-request list --tenant-id $(oci iam tenancy get --query "data.id" -c raw-output) --start-date $(date -d "$(date +%Y-%m-01)" +%Y-%m-%d) --end-date $(date +%Y-%m-%d) --query "data[?resourceName=='Compute'].{service:serviceName,usage:usageAmount}" -c table` | Shows usage for the Compute service; compare against the 720 h free limit. |
| Delete the whole VCN (including subnet, IGW, route table, security list) | `oci network vcn delete --vcn-id $VCN_ID --force` | Removes all networking resources in one step. |

---

## 9. Clean‑up – ensure no further charges  

The simplest way is to terminate the compute instance and then delete the VCN that contains the networking resources.

```bash
# Stop and terminate the instance
oci compute instance action --instance-id $INSTANCE_ID --action STOP
oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false --force

# Delete the VCN (this also deletes the subnet, IGW, route table, and security list)
oci network vcn delete --vcn-id $VCN_ID --force
```

If you created any extra block volumes, object storage buckets, or other resources, delete them as well:

```bash
# Example: delete a block volume
oci bv volume delete --volume-id <volume-ocid> --force
# Example: delete an Object Storage bucket
oci os bucket delete --namespace <your-namespace> --name <bucket-name> --force
```

After the deletions complete, verify in the OCI Console that no resources remain under **Compute**, **Block Volume**, **Networking**, or **Object Storage**. With no resources left, the tenancy will not generate any further charges.

---

## 10. One‑line cheat sheet (copy‑paste ready)

```bash
# -------------------------------------------------
# 1. Docker wrapper for OCI CLI (optional)
cat <<'EOF' > ~/bin/oci
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.oci:/root/.oci:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  ghcr.io/oracle/oci-cli:latest "$@"
EOF
chmod +x ~/bin/oci
export PATH=$HOME/bin:$PATH   # add to shell rc file

# -------------------------------------------------
# 2. Authenticate (run once)
#   - Generate RSA key pair, upload public key in the Console, download private key as ~/.oci/oci_api_key.pem
#   - Fill in ~/.oci/config with user OCID, tenancy OCID, fingerprint, region
# Test:
oci os ns get

# -------------------------------------------------
# 3. Setup variables
COMPARTMENT_ID=$(oci iam compartment list --query "data[?\"name\"=='Default'].id" -c raw-output)
VCN_NAME="free-vcn"
SUBNET_NAME="free-subnet"
CIDR_BLOCK="10.0.0.0/16"
SUBNET_CIDR="10.0.0.0/24"
SSH_KEY="$HOME/.ssh/oci_free_key"
if [ ! -f "$SSH_KEY" ]; then ssh-keygen -t rsa -b 2048 -f $SSH_KEY -N "" -C "oci_free_key"; fi

# -------------------------------------------------
# 4. Create networking
VCN_ID=$(oci network vcn create --compartment-id $COMPARTMENT_ID --display-name $VCN_NAME --cidr-block $CIDR_BLOCK --query "data.id" -c raw-output)
SUBNET_ID=$(oci network subnet create --compartment-id $COMPARTMENT_ID --vcn-id $VCN_ID --display-name $SUBNET_NAME --cidr-block $SUBNET_CIDR --query "data.id" -c raw-output)
IGW_ID=$(oci network internet-gateway create --compartment-id $COMPARTMENT_ID --vcn-id $VCN_ID --display-name free-igw --is-enabled true --query "data.id" -c raw-output)
RT_ID=$(oci network route-table create --compartment-id $COMPARTMENT_ID --vcn-id $VCN_ID --display-name free-rt --route-rules '[{"cidr":"0.0.0.0/0","networkEntityId":"'"$IGW_ID"'"}]' --query "data.id" -c raw-output)
oci network subnet update --subnet-id $SUBNET_ID --route-table-id $RT_ID
SL_ID=$(oci network security-list create --compartment-id $COMPARTMENT_ID --vcn-id $VCN_ID --display-name free-sl --ingress-security-rules '[{"source":"0.0.0.0/0","protocol":"6","tcpOptions":{"destinationPortRange":{"max":22,"min":22}}}]' --egress-security-rules '[{"destination":"0.0.0.0/0","protocol":"6","tcpOptions":{"destinationPortRange":{"max":65535,"min":1}}}]' --query "data.id" -c raw-output)
oci network subnet update --subnet-id $SUBNET_ID --security-list-ids '["'"$SL_ID"'"]'

# -------------------------------------------------
# 5. Launch always‑free VM (E2.1.Micro)
IMAGE_OCID=$(oci compute image list --compartment-id $COMPARTMENT_ID --operating-system "Oracle Linux" --operating-system-version "8" --query "data[0].id" -c raw-output)
INSTANCE_ID=$(oci compute instance launch --compartment-id $COMPARTMENT_ID --display-name free-instance --shape VM.Standard.E2.1.Micro --subnet-id $SUBNET_ID --image-id $IMAGE_OCID --ssh-authorized-keys-file "$SSH_KEY.pub" --assign-public-ip true --query "data.id" -c raw-output)
PUBLIC_IP=$(oci compute instance list-vnics --instance-id $INSTANCE_ID --query "data[0].\"public-ip\"" -c raw-output)
echo "Instance ready – IP: $PUBLIC_IP"

# -------------------------------------------------
# 6. SSH into the instance
ssh -i "$SSH_KEY" opc@$PUBLIC_IP

# -------------------------------------------------
# 7. Clean up (terminate instance and delete VCN)
oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false --force
oci network vcn delete --vcn-id $VCN_ID --force
```

Run the sections in order (or copy the whole block into a script) to provision an always‑free Oracle Cloud VM, SSH into it, and then clean up everything afterwards.

---

## 11. Further reading  

| Resource | What you’ll find |
|----------|------------------|
| OCI CLI reference | <https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm> |
| Oracle Cloud Free Tier details | <https://www.oracle.com/cloud/free/> |
| Always‑Free compute shapes | <https://www.oracle.com/cloud/free/always-free/> |
| IAM best practices for API keys | <https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingcredentials.htm> |
| OCI Cloud Shell (browser‑based, no install) | <https://docs.oracle.com/en-us/iaas/Content/Compute/References/cloudshell.htm> |

You now have a complete, plain‑text workflow for using Oracle Cloud’s always‑free resources: from account creation, through isolated CLI setup, to a running VM that you can SSH into, and finally the clean‑up steps that keep your tenancy cost‑free. Happy cloud experimentation!