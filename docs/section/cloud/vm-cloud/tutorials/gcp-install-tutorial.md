
**Google Cloud Platform – Free‑Tier Tutorial (plain text, no emojis or numbered icons)**  

The following document shows how to:

* Sign up for a Google Cloud free account.  
* Install the Google Cloud SDK (gcloud) in an isolated way (Docker, official installer, or pipx).  
* Provision the minimum set of resources required to run a free‑tier e2‑micro Linux VM that you can SSH into.  
* Connect to the VM with SSH.  
* Clean up all resources so you are not charged after the demo.  

All commands assume the SDK is accessible as `gcloud`. If you use the Docker wrapper, prepend `gcloud` with the wrapper script shown in the installation section.

---

## Google Cloud free account  

| Free‑tier offering (12 months) | Typical limits |
|--------------------------------|----------------|
| **e2‑micro** VM (Linux or Windows) – 720 hrs/month (1 vCPU, 0.5 GiB RAM) | Only one e2‑micro instance can be running at a time. |
| 5 GiB Regional Cloud Storage (Standard) | Good for object storage, static sites. |
| 1 GiB Cloud Firestore (in‑datastore mode) | Optional. |
| 1 TiB network egress from North America to all destinations (excluding China, Australia) | Mostly for outbound traffic. |
| Various other services – always‑free tier (e.g., Cloud Run, Cloud Functions) | Pay‑as‑you‑go beyond the free amount. |

### How to create the account  

* Visit <https://cloud.google.com/free> and click **Get started for free**.  
* Sign in with a Google account (or create one).  
* Provide a credit‑card or debit‑card for identity verification. Google performs a small $0‑$1 authorization that is released immediately.  
* Accept the terms and enable the “Free trial”.  
* After the console loads you are logged in as the **project owner**.  

> **Tip:** Do not use the owner role for everyday work. Create a dedicated IAM service account with only the permissions you need (see the “Create a service account” step below).

---

## Install Google Cloud SDK in an isolated environment  

You can pick any of the three methods. All give you a working `gcloud` binary without altering the host system.

### Docker (complete isolation)

```bash
# Pull the official Cloud SDK image (≈400 MiB)
docker pull google/cloud-sdk:latest

# Create a thin wrapper script so you can type “gcloud” normally
cat <<'EOF' > ~/bin/gcloud
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.config/gcloud:/root/.config/gcloud:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  google/cloud-sdk:latest "$@"
EOF
chmod +x ~/bin/gcloud
export PATH=$HOME/bin:$PATH   # add to your shell rc file (.bashrc/.zshrc)
```

* `~/.config/gcloud` stores authentication tokens and configuration.  
* `~/.ssh` is mounted read‑only so the container can use your SSH private key.

### Official installer (Linux/macOS/Windows)

| OS | Commands |
|----|----------|
| Linux (bash) | `curl https://sdk.cloud.google.com | bash` then `exec -l $SHELL` |
| macOS (brew) | `brew install --cask google-cloud-sdk` |
| Windows (PowerShell) | `Invoke-WebRequest -Uri https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe -OutFile GoogleCloudSDKInstaller.exe; Start-Process .\GoogleCloudSDKInstaller.exe -Wait` |

After installation run `gcloud init` to set up the configuration.

### pipx (Python sandbox)

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install google-cloud-sdk
```

Verify the installation:

```bash
gcloud version
# Expected output: Google Cloud SDK <version>
```

---

## Authenticate the SDK  

The first time you run `gcloud` you must authorize it for the Google account you created.

```bash
gcloud auth login
# A browser window opens; choose the Google account used for the free trial.
```

For non‑interactive use (scripts, CI/CD) create a service account with the minimal role needed:

```bash
# Choose the project that the free trial created (or a new one you prefer)
PROJECT_ID=$(gcloud config get-value project)

# Create a service account
gcloud iam service-accounts create gcloud-free-sa \
  --display-name "Free‑tier service account" \
  --project $PROJECT_ID

# Grant the service account the roles required for VM operations
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:gcloud-free-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/compute.instanceAdmin.v1"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member "serviceAccount:gcloud-free-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role "roles/iam.serviceAccountUser"

# Generate a JSON key file for the service account
gcloud iam service-accounts keys create ~/gcloud-free-sa-key.json \
  --iam-account gcloud-free-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --project $PROJECT_ID
```

Use the key for non‑interactive authentication:

```bash
gcloud auth activate-service-account \
  --key-file=~/gcloud-free-sa-key.json \
  --project $PROJECT_ID
```

For the remainder of this guide the interactive `gcloud auth login` is sufficient.

---

## Set default project and compute zone  

```bash
# Replace with the project ID shown by `gcloud config list`
gcloud config set project $PROJECT_ID
# Choose a zone that supports the free‑tier e2‑micro (e.g., us-central1-a)
gcloud config set compute/zone us-central1-a
```

---

## Provision a free‑tier e2‑micro VM  

The steps below create:

* a VPC network and subnet (the default network can also be used, but a custom one is shown for clarity).  
* a firewall rule that allows inbound TCP 22 (SSH).  
* an SSH key pair (if you don’t already have one).  
* an e2‑micro VM running Ubuntu 22.04 LTS (free‑tier eligible).  

```bash
# -------------------------------------------------
# Variables – feel free to change names
NETWORK_NAME="free-vpc"
SUBNET_NAME="free-subnet"
FIREWALL_NAME="allow-ssh"
INSTANCE_NAME="free-vm"
MACHINE_TYPE="e2-micro"          # free‑tier eligible
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
SSH_KEY_PATH="$HOME/.ssh/gcloud_free_key"
# -------------------------------------------------
# Create a VPC network
gcloud compute networks create $NETWORK_NAME \
  --subnet-mode=custom \
  --bgp-routing-mode=regional \
  --quiet

# Create a subnet in the same region as the default zone
gcloud compute networks subnets create $SUBNET_NAME \
  --network=$NETWORK_NAME \
  --range=10.128.0.0/20 \
  --quiet

# Create a firewall rule to allow SSH from anywhere (replace * with your IP for tighter security)
gcloud compute firewall-rules create $FIREWALL_NAME \
  --network=$NETWORK_NAME \
  --allow=tcp:22 \
  --source-ranges=0.0.0.0/0 \
  --quiet

# Generate an SSH key pair if it does not exist
if [ ! -f "$SSH_KEY_PATH" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY_PATH -N "" -C "gcloud_free_key"
fi

# Create the VM
gcloud compute instances create $INSTANCE_NAME \
  --machine-type=$MACHINE_TYPE \
  --subnet=$SUBNET_NAME \
  --network=$NETWORK_NAME \
  --tags=ssh \
  --image-family=$IMAGE_FAMILY \
  --image-project=$IMAGE_PROJECT \
  --metadata=ssh-keys="$(whoami):$(cat $SSH_KEY_PATH.pub)" \
  --quiet

# Obtain the external IP address
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "VM created. External IP: $EXTERNAL_IP"
```

**Important notes**

* **e2‑micro** is the free‑tier eligible machine type (720 hours per month).  
* The firewall rule opens port 22 to the world. Replace `0.0.0.0/0` with your public IP or CIDR range for a more restrictive rule.  
* The `ssh-keys` metadata entry adds the public key to the default `gcloud` user (`$(whoami)`). You can also use a custom username by editing the metadata value accordingly.

---

## SSH into the VM  

```bash
ssh -i "$SSH_KEY_PATH" $(whoami)@$EXTERNAL_IP
```

You should see a prompt similar to:

```
$(whoami)@free-vm:~$
```

You are now connected to the free‑tier Google Cloud VM.

---

## Frequently used commands (free‑tier safe)

| Goal | gcloud command | Description |
|------|----------------|-------------|
| List all instances in the project | `gcloud compute instances list` | Shows name, zone, status, external IP |
| Stop the VM (no compute charges while stopped) | `gcloud compute instances stop $INSTANCE_NAME` | Deallocates the VM |
| Start the VM again | `gcloud compute instances start $INSTANCE_NAME` | Powers the VM back on |
| Delete the VM (removes the compute resource) | `gcloud compute instances delete $INSTANCE_NAME --quiet` | Destroys the VM, keeps network resources |
| Delete the whole network (including firewall, subnet) | `gcloud compute networks delete $NETWORK_NAME --quiet` | Removes all networking created above |
| Show current month’s free‑tier usage (preview) | `gcloud beta billing accounts list` then `gcloud beta billing budgets list --billing-account <ACCOUNT_ID>` | Billing APIs are still in preview; alternatively view usage in the Cloud Console under **Billing → Reports** |
| List firewall rules | `gcloud compute firewall-rules list` | Verify that only the intended ports are open |

---

## Clean‑up – Ensure no ongoing charges  

The simplest clean‑up is to delete the entire project you created for the demo. This removes every resource (VMs, disks, networking, IAM policies).

```bash
# WARNING: This permanently deletes the project and all its resources.
gcloud projects delete $PROJECT_ID --quiet
```

If you prefer to keep the project and only delete the demo resources:

```bash
# Stop and delete the VM
gcloud compute instances delete $INSTANCE_NAME --quiet

# Delete the firewall rule
gcloud compute firewall-rules delete $FIREWALL_NAME --quiet

# Delete the subnet
gcloud compute networks subnets delete $SUBNET_NAME --quiet

# Delete the VPC network
gcloud compute networks delete $NETWORK_NAME --quiet

# (Optional) Remove the service‑account key file
rm -f ~/gcloud-free-sa-key.json
```

After the deletions complete, verify in the Cloud Console that no resources remain. The free‑tier subscription will no longer accrue charges.

---

## Quick reference cheat sheet (copy‑paste)

```bash
# -------------------------------------------------
# 1. Install isolated Google Cloud SDK (Docker wrapper)
cat <<'EOF' > ~/bin/gcloud
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.config/gcloud:/root/.config/gcloud:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  google/cloud-sdk:latest "$@"
EOF
chmod +x ~/bin/gcloud
export PATH=$HOME/bin:$PATH   # add to your shell rc file

# -------------------------------------------------
# 2. Authenticate interactively (device flow works inside Docker)
gcloud auth login

# -------------------------------------------------
# 3. Set default project and zone
PROJECT_ID=$(gcloud config get-value project)
gcloud config set compute/zone us-central1-a --quiet

# -------------------------------------------------
# 4. Define variables
NETWORK="free-vpc"
SUBNET="free-subnet"
FIREWALL="allow-ssh"
INSTANCE="free-vm"
MACHINE="e2-micro"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
SSH_KEY="$HOME/.ssh/gcloud_free_key"

# -------------------------------------------------
# 5. Create networking
gcloud compute networks create $NETWORK --subnet-mode=custom --quiet
gcloud compute networks subnets create $SUBNET --network=$NETWORK --range=10.128.0.0/20 --quiet
gcloud compute firewall-rules create $FIREWALL --network=$NETWORK --allow=tcp:22 --source-ranges=0.0.0.0/0 --quiet

# -------------------------------------------------
# 6. Create SSH key if missing
if [ ! -f "$SSH_KEY" ]; then
  ssh-keygen -t rsa -b 2048 -f $SSH_KEY -N "" -C "gcloud_free_key"
fi

# -------------------------------------------------
# 7. Create the e2-micro VM (free‑tier)
gcloud compute instances create $INSTANCE \
  --machine-type=$MACHINE \
  --subnet=$SUBNET \
  --network=$NETWORK \
  --metadata=ssh-keys="$(whoami):$(cat $SSH_KEY.pub)" \
  --image-family=$IMAGE_FAMILY \
  --image-project=$IMAGE_PROJECT \
  --quiet

# -------------------------------------------------
# 8. Get external IP and SSH
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE \
  --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
echo "External IP: $EXTERNAL_IP"
ssh -i "$SSH_KEY" $(whoami)@$EXTERNAL_IP

# -------------------------------------------------
# 9. Clean up when finished (delete whole project)
#   Uncomment the line below only if you really want to delete the project.
# gcloud projects delete $PROJECT_ID --quiet
```

Run the sections in order (or place the entire block into a script) to provision a free‑tier Google Cloud VM, SSH into it, and then clean up afterwards.

---

## Additional resources  

| Resource | What you’ll find |
|----------|------------------|
| Google Cloud SDK documentation | <https://cloud.google.com/sdk/docs> |
| Free‑tier overview | <https://cloud.google.com/free> |
| e2‑micro (always‑free) VM details | <https://cloud.google.com/compute/docs/machine-types> |
| IAM best practices for service accounts | <https://cloud.google.com/iam/docs/best-practices> |
| Cloud Shell (browser‑based, no installation) | <https://cloud.google.com/shell> |

You now have a complete, plain‑text workflow for obtaining a Google Cloud free account, installing the CLI safely, creating an always‑free e2‑micro VM, connecting via SSH, and cleaning up afterward. Happy cloud experimentation!