# Google Cloud Platform Instalation and Free Tier usage

## Learning Objectives

!!! info "Learning Objectives"
    * Sign up for a Google Cloud free account.
    * Install the Google Cloud SDK (gcloud) in an isolated environment.
    * Provision the minimum set of resources required to run a free-tier e2-micro Linux VM.
    * Connect to the VM using SSH.
    * Clean up all resources to avoid unexpected charges.

## Overview

This chapter provides a step-by-step guide to setting up a virtual machine on the Google Cloud Platform (GCP) using the free tier. The focus is on isolation during installation and the use of minimal resources to remain within the free usage limits.

## Core Sections

### Creating a Google Cloud Free Account

Google Cloud provides a free trial for new users, which includes credits and an "Always Free" tier for specific resources.

| Free-tier offering (12 months) | Typical limits |
|--------------------------------|----------------|
| **e2-micro** VM (Linux or Windows) – 720 hrs/month (1 vCPU, 0.5 GiB RAM) | Only one e2-micro instance can be running at a time. |
| 5 GiB Regional Cloud Storage (Standard) | Good for object storage, static sites. |
| 1 GiB Cloud Firestore (in-datastore mode) | Optional. |
| 1 TiB network egress from North America to all destinations (excluding China, Australia) | Mostly for outbound traffic. |
| Various other services – always-free tier (e.g., Cloud Run, Cloud Functions) | Pay-as-you-go beyond the free amount. |

To create the account:

1. Visit <https://cloud.google.com/free> and click **Get started for free**.
2. Sign in with a Google account (or create one).
3. Provide a credit-card or debit-card for identity verification. Google performs a small $0-$1 authorization that is released immediately.
4. Accept the terms and enable the "Free trial".
5. Once the console loads, you are logged in as the **project owner**.

!!! warning "Security Best Practice"
    Do not use the owner role for everyday work. Create a dedicated IAM service account with only the permissions you need.

### Installing the Google Cloud SDK

The Google Cloud SDK (gcloud) can be installed using several methods. To avoid altering the host system, isolation is recommended.

#### Docker (Complete Isolation)

This method runs the SDK inside a container, mounting only the necessary configuration and SSH directories.

```bash
# Pull the official Cloud SDK image (≈400 MiB)
docker pull google/cloud-sdk:latest

# Create a thin wrapper script so you can type "gcloud" normally
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
export PATH=$HOME/bin:$PATH
```

* `~/.config/gcloud` stores authentication tokens and configuration.
* `~/.ssh` is mounted read-only so the container can use your SSH private key.

#### Official Installer

For native installation on Linux, macOS, or Windows:

| OS | Commands |
|----|----------|
| Linux (bash) | `curl https://sdk.cloud.google.com | bash` then `exec -l $SHELL` |
| macOS (brew) | `brew install --cask google-cloud-sdk` |
| Windows (PowerShell) | `Invoke-WebRequest -Uri https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe -OutFile GoogleCloudSDKInstaller.exe; Start-Process .\GoogleCloudSDKInstaller.exe -Wait` |

After installation, run `gcloud init` to set up the configuration.

#### pipx (Python Sandbox)

pipx allows you to install the SDK in an isolated Python environment.

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install google-cloud-sdk
```

Verify the installation:

```bash
gcloud version
```

### SDK Authentication

The first time you run `gcloud`, you must authorize it for your Google account.

```bash
gcloud auth login
```

A browser window will open; choose the Google account used for the free trial.

For non-interactive use (scripts, CI/CD), create a service account with the minimal role needed:

```bash
# Choose the project that the free trial created
PROJECT_ID=$(gcloud config get-value project)

# Create a service account
gcloud iam service-accounts create gcloud-free-sa \
  --display-name "Free-tier service account" \
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

Use the key for non-interactive authentication:

```bash
gcloud auth activate-service-account \
  --key-file=~/gcloud-free-sa-key.json \
  --project $PROJECT_ID
```

### Configuring Project and Zone

Set the default project and compute zone to ensure resources are created in a free-tier eligible region.

```bash
# Replace with the project ID shown by `gcloud config list`
gcloud config set project $PROJECT_ID

# Choose a zone that supports the free-tier e2-micro (e.g., us-central1-a)
gcloud config set compute/zone us-central1-a
```

### Provisioning a Free-Tier VM

To deploy an e2-micro VM, you must create the supporting network infrastructure.

```bash
# Variables
NETWORK_NAME="free-vpc"
SUBNET_NAME="free-subnet"
FIREWALL_NAME="allow-ssh"
INSTANCE_NAME="free-vm"
MACHINE_TYPE="e2-micro"
IMAGE_FAMILY="ubuntu-2204-lts"
IMAGE_PROJECT="ubuntu-os-cloud"
SSH_KEY_PATH="$HOME/.ssh/gcloud_free_key"

# Create a VPC network
gcloud compute networks create $NETWORK_NAME \
  --subnet-mode=custom \
  --bgp-routing-mode=regional \
  --quiet

# Create a subnet
gcloud compute networks subnets create $SUBNET_NAME \
  --network=$NETWORK_NAME \
  --range=10.128.0.0/20 \
  --quiet

# Create a firewall rule to allow SSH
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

!!! note "Important Deployment Details"
    * **e2-micro** is the free-tier eligible machine type (720 hours per month).
    * The firewall rule opens port 22 to the world. Replace `0.0.0.0/0` with your public IP for tighter security.
    * The `ssh-keys` metadata entry adds the public key to the default user.

### Connecting via SSH

Once the VM is running, connect using the generated SSH key.

```bash
ssh -i "$SSH_KEY_PATH" $(whoami)@$EXTERNAL_IP
```

The prompt should appear as:
```
$(whoami)@free-vm:~$
```

### Managing VM Resources

The following commands are useful for maintaining a free-tier instance.

| Goal | gcloud command | Description |
|------|----------------|-------------|
| List all instances | `gcloud compute instances list` | Shows name, zone, status, external IP |
| Stop the VM | `gcloud compute instances stop $INSTANCE_NAME` | Deallocates the VM to avoid compute charges |
| Start the VM | `gcloud compute instances start $INSTANCE_NAME` | Powers the VM back on |
| Delete the VM | `gcloud compute instances delete $INSTANCE_NAME --quiet` | Destroys the VM, keeps network resources |
| Delete the network | `gcloud compute networks delete $NETWORK_NAME --quiet` | Removes all networking created above |
| List firewall rules | `gcloud compute firewall-rules list` | Verify that only intended ports are open |

### Resource Clean-up

To ensure no ongoing charges, remove all created resources. The most efficient method is to delete the entire project.

```bash
# WARNING: This permanently deletes the project and all its resources.
gcloud projects delete $PROJECT_ID --quiet
```

Alternatively, delete resources individually:

```bash
# Stop and delete the VM
gcloud compute instances delete $INSTANCE_NAME --quiet

# Delete the firewall rule
gcloud compute firewall-rules delete $FIREWALL_NAME --quiet

# Delete the subnet
gcloud compute networks subnets delete $SUBNET_NAME --quiet

# Delete the VPC network
gcloud compute networks delete $NETWORK_NAME --quiet

# Remove the service-account key file
rm -f ~/gcloud-free-sa-key.json
```

## Summary Checklist

- [ ] Google Cloud free account created and verified.
- [ ] Google Cloud SDK installed in an isolated environment.
- [ ] SDK authenticated via `gcloud auth login` or service account.
- [ ] Default project and zone (`us-central1-a`) configured.
- [ ] VPC, Subnet, and Firewall rule created.
- [ ] SSH key generated and injected into the VM metadata.
- [ ] e2-micro VM instance provisioned and accessible via SSH.
- [ ] Resources deleted or project removed to prevent charges.

## Assignments

!!! note "Assignment.1: Isolated SDK Setup"
    Install the Google Cloud SDK using the Docker wrapper method. Verify the installation by running `gcloud version`.

!!! note "Assignment.2: Free-Tier Provisioning"
    Provision a free-tier e2-micro VM in the `us-central1-a` zone. Ensure that you can SSH into the instance using a custom SSH key.

    ??? tip "Solution: Assignment.2"
        Follow the "Provisioning a Free-Tier VM" section. Use the `gcloud compute instances create` command with `--machine-type=e2-micro` and ensure the subnet and firewall rules are correctly applied.

!!! note "Assignment.3: Resource Audit"
    List all compute instances and firewall rules in your project. Verify that only one e2-micro instance is running and that only port 22 is open.

    ??? tip "Solution: Assignment.3"
        Use `gcloud compute instances list` and `gcloud compute firewall-rules list`.

## References

| Resource | Description |
|----------|-------------|
| Google Cloud SDK documentation | <https://cloud.google.com/sdk/docs> |
| Free-tier overview | <https://cloud.google.com/free> |
| e2-micro VM details | <https://cloud.google.com/compute/docs/machine-types> |
| IAM best practices | <https://cloud.google.com/iam/docs/best-practices> |
| Cloud Shell | <https://cloud.google.com/shell> |

## Self-Evaluation

??? note "Which machine type is eligible for the Google Cloud Always Free tier for compute instances?"
    The `e2-micro` machine type is eligible for the always-free tier, providing 720 hours of usage per month.

??? note "Why is it recommended to use a wrapper script for the Docker-based SDK installation?"
    A wrapper script allows the user to execute `gcloud` commands directly from the host shell while the actual execution happens inside an isolated container, preserving host system cleanliness.

??? note "What is the purpose of the `ssh-keys` metadata when creating a GCP instance?"
    The `ssh-keys` metadata is used to inject the user's public SSH key into the VM's `authorized_keys` file for the specified user, enabling secure passwordless authentication.
