# Oracle Cloud

## Learning Objectives

!!! info "Learning Objectives"
    * Create an Oracle Cloud free account.
    * Install the Oracle Cloud Infrastructure (OCI) CLI in an isolated environment.
    * Provision the minimum set of networking resources (VCN, Subnet, IGW, Route Table, Security List).
    * Launch an Always-Free compute instance.
    * Connect to the instance using SSH.
    * Clean up all resources to avoid potential charges.

## Overview

This chapter provides a comprehensive guide to using the Oracle Cloud Infrastructure (OCI) Always-Free tier. It covers the end-to-end process of setting up an account, installing the CLI tool in an isolated environment, and deploying a functional virtual machine without incurring costs.

## Core Sections

### Obtaining an Oracle Cloud Free Account

The Oracle Cloud Always-Free tier provides a generous set of resources that do not expire.

| Free-tier benefit (always free) | Limits (per month) |
|--------------------------------|--------------------|
| **Compute** – two shapes: <br>• VM.Standard.A1.Flex (Arm) – up to 4 OCPU total, 24 GB RAM <br>• VM.Standard.E2.1.Micro (AMD) – 1 OCPU, 1 GB RAM | The shapes can run continuously (720 h / month). |
| **Block Volume** – 100 GB standard SSD | Persistent block storage attached to a VM. |
| **Object Storage** – 10 GB standard | Object storage for files, static sites, etc. |
| **Outbound Data Transfer** – 10 TB per month | Data egress to the internet. |
| **Autonomous Database** – 2 TB total storage (always-free version) | Optional managed database. |
| **Load Balancer** – 1 TB data processing | Only the "always-free" load balancer is covered. |

To sign up:

1. Open <https://cloud.oracle.com/> and click **Start for free**.
2. Sign in with an existing Oracle account or create a new one.
3. Provide a credit-card or debit-card for identity verification. Oracle performs a $0-$1 authorization that is released immediately.
4. Accept the terms and complete the registration.
5. Once the console loads, you are the **Administrator** of a tenancy that includes the always-free resources.

!!! info "Free Tier Duration"
    The free tier is not time-limited. As long as you stay within the listed limits, you will not be charged.

### Installing the OCI CLI

The OCI CLI should be installed in an isolated environment to prevent interference with system-wide Python packages.

#### Docker (Complete Isolation)

This method uses a container to run the CLI, mounting the OCI configuration and SSH directories.

```bash
# Pull the official OCI CLI image (≈300 MiB)
docker pull oraclelinux:8
docker pull ghcr.io/oracle/oci-cli:latest

# Create a small wrapper script so you can type "oci" directly
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
export PATH=$HOME/bin:$PATH
```

* `~/.oci` stores the configuration file and the API key pair.
* `~/.ssh` is mounted read-only so the container can use the private key for SSH connections.

#### Official Installer

For native installation on Linux or macOS:

```bash
# Linux (bash)
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)" \
  -- -b ~/bin

# macOS (Homebrew)
brew install oci-cli
```

#### pipx (Python Sandbox)

For an isolated application-level installation:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install oci-cli
```

Verify the installation:

```bash
oci --version
```

### CLI Configuration

The OCI CLI requires an RSA key pair and a tenancy-level API key for authentication.

```bash
# Create a directory for the OCI configuration
mkdir -p ~/.oci

# Generate an RSA key pair (2048-bit)
openssl genrsa -out ~/.oci/oci_api_key.pem 2048
chmod 600 ~/.oci/oci_api_key.pem
openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem

# Configuration steps in the OCI Console:
# 1. Go to Identity -> Users, select your user, then API Keys -> Add API Key.
# 2. Upload the public key (~/.oci/oci_api_key_public.pem).
# 3. Save the downloaded private key as ~/.oci/oci_api_key.pem.

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

Test the configuration:

```bash
oci os ns get
```

### Provisioning Networking Resources

The free tier requires a custom VCN and associated components to allow SSH access.

```bash
# Variables
COMPARTMENT_ID=$(oci iam compartment list --query "data[?\"name\"=='Default'].id" -c raw-output)
VCN_NAME="free-vcn"
SUBNET_NAME="free-subnet"
IGW_NAME="free-igw"
RT_NAME="free-rt"
SL_NAME="free-sl"
CIDR_BLOCK="10.0.0.0/16"
SUBNET_CIDR="10.0.0.0/24"

# 1. Create a VCN
VCN_ID=$(oci network vcn create \
  --compartment-id $COMPARTMENT_ID \
  --display-name $VCN_NAME \
  --cidr-block $CIDR_BLOCK \
  --query "data.id" \
  --raw-output)

# 2. Create a subnet
SUBNET_ID=$(oci network subnet create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $SUBNET_NAME \
  --cidr-block $SUBNET_CIDR \
  --query "data.id" \
  --raw-output)

# 3. Create an Internet Gateway
IGW_ID=$(oci network internet-gateway create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $IGW_NAME \
  --is-enabled true \
  --query "data.id" \
  --raw-output)

# 4. Create a Route Table directing 0.0.0.0/0 traffic to the IGW
RT_ID=$(oci network route-table create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $RT_NAME \
  --route-rules '[{"cidr":"0.0.0.0/0","networkEntityId":"'"$IGW_ID"'"}]' \
  --query "data.id" \
  --raw-output)

# Associate the Route Table with the subnet
oci network subnet update \
  --subnet-id $SUBNET_ID \
  --route-table-id $RT_ID

# 5. Create a Security List allowing inbound SSH (port 22)
SL_ID=$(oci network security-list create \
  --compartment-id $COMPARTMENT_ID \
  --vcn-id $VCN_ID \
  --display-name $SL_NAME \
  --egress-security-rules '[{"destination":"0.0.0.0/0","protocol":"6","isStateless":false,"tcpOptions":{"destinationPortRange":{"max":65535,"min":1}}}]' \
  --ingress-security-rules '[{"source":"0.0.0.0/0","protocol":"6","isStateless":false,"tcpOptions":{"destinationPortRange":{"max":22,"min":22}}}]' \
  --query "data.id" \
  --raw-output)

# Associate the Security List with the subnet
oci network subnet update \
  --subnet-id $SUBNET_ID \
  --security-list-ids '["'"$SL_ID"'"]'
```

### Generating SSH Keys

If a key pair does not already exist, generate one to be injected into the VM.

```bash
SSH_KEY="$HOME/.ssh/oci_free_key"
if [ ! -f "$SSH_KEY" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY -N "" -C "oci_free_key"
fi
chmod 600 "$SSH_KEY"
```

### Launching an Always-Free Compute Instance

The `VM.Standard.E2.1.Micro` (AMD) shape is the standard free-tier choice.

```bash
# Variables
INSTANCE_NAME="free-instance"
SHAPE="VM.Standard.E2.1.Micro"
IMAGE_OCID=$(oci compute image list \
  --compartment-id $COMPARTMENT_ID \
  --operating-system "Oracle Linux" \
  --operating-system-version "8" \
  --query "data[?\"displayName\"=='Oracle-Linux-8.9-2024.04.09-0'] | [0].id" \
  --raw-output)

# Launch the instance
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

# Retrieve the public IP address
PUBLIC_IP=$(oci compute instance list-vnics \
  --instance-id $INSTANCE_ID \
  --query "data[0].\"public-ip\"" \
  --raw-output)

echo "Instance public IP: $PUBLIC_IP"
```

### Connecting via SSH

Connect to the instance using the default user for the chosen image.

```bash
ssh -i "$SSH_KEY" opc@$PUBLIC_IP
```

* The default user for Oracle Linux is **opc**.
* For Ubuntu images, the user is **ubuntu**.

### Managing VM Resources

The following commands help manage an always-free tenancy.

| Goal | OCI CLI command | Description |
|------|-----------------|-------------|
| List compute instances | `oci compute instance list --compartment-id $COMPARTMENT_ID -c table` | Shows name, shape, and state. |
| Stop the instance | `oci compute instance action --instance-id $INSTANCE_ID --action STOP` | Deallocates compute; boot volume remains. |
| Start the instance | `oci compute instance action --instance-id $INSTANCE_ID --action START` | Powers the VM back on. |
| Terminate instance | `oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false --force` | Removes VM and boot volume. |
| Create block volume | `oci bv volume create --availability-domain ... --size-in-gbs 50` | Adds persistent storage (free up to 100 GB). |
| Delete VCN | `oci network vcn delete --vcn-id $VCN_ID --force` | Removes all networking resources. |

### Resource Clean-up

To ensure no charges are incurred, terminate the compute instance and delete the VCN.

```bash
# Terminate the instance
oci compute instance action --instance-id $INSTANCE_ID --action STOP
oci compute instance terminate --instance-id $INSTANCE_ID --preserve-boot-volume false --force

# Delete the VCN
oci network vcn delete --vcn-id $VCN_ID --force
```

## Summary Checklist

- [ ] Oracle Cloud free account created and verified.
- [ ] OCI CLI installed in an isolated environment (Docker or venv).
- [ ] API keys generated and registered in the OCI Console.
- [ ] `~/.oci/config` configured with correct OCIDs and fingerprint.
- [ ] VCN, Subnet, Internet Gateway, Route Table, and Security List provisioned.
- [ ] SSH key pair generated locally.
- [ ] Always-Free VM instance launched and public IP retrieved.
- [ ] Successful SSH connection established.
- [ ] Resources deleted to prevent future charges.

## Assignments

!!! note "Assignment.1: CLI Isolation"
    Install the OCI CLI using the Docker wrapper method. Verify the setup by running `oci --version`.

!!! note "Assignment.2: Network Provisioning"
    Provision a custom VCN and subnet that allows inbound SSH traffic. Verify the security list configuration.

!!! note "Assignment.3: VM Deployment"
    Launch a `VM.Standard.E2.1.Micro` instance and connect to it via SSH using a custom key.

    ??? tip "Solution: Assignment.3"
        Follow the "Launching an Always-Free Compute Instance" section. Ensure the `--assign-public-ip true` flag is used.

## References

| Resource | Description |
|----------|-------------|
| OCI CLI reference | <https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm> |
| Oracle Cloud Free Tier details | <https://www.oracle.com/cloud/free/> |
| Always-Free compute shapes | <https://www.oracle.com/cloud/free/always-free/> |
| IAM API keys guide | <https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingcredentials.htm> |
| OCI Cloud Shell | <https://docs.oracle.com/en-us/iaas/Content/Compute/References/cloudshell.htm> |

## Self-Evaluation

??? note "What is the difference between the Arm (A1.Flex) and AMD (E2.1.Micro) free shapes?"
    The Arm-based `VM.Standard.A1.Flex` shape offers significantly more resources (up to 4 OCPUs and 24 GB RAM) compared to the AMD-based `VM.Standard.E2.1.Micro` (1 OCPU, 1 GB RAM).

??? note "Why is a custom VCN required instead of using a default one?"
    The default VCN may not have the necessary security lists or route tables configured to allow inbound SSH traffic from the public internet.

??? note "What is the effect of setting `--preserve-boot-volume false` during instance termination?"
    Setting this to `false` ensures that the boot volume is deleted along with the instance, preventing "orphaned" volumes from consuming the free-tier storage quota.
