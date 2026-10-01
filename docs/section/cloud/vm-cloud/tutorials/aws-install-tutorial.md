
**AWS CLI – Free‑Tier Tutorial (plain text, no icons or numbered headings)**  

Below is a complete, step‑by‑step guide that takes you from a brand‑new AWS account to a running EC2 instance that you can SSH into, while staying inside the AWS Free Tier. The instructions use an isolated installation of the AWS CLI so that nothing on your workstation is modified outside the CLI itself.

---

## Create a Free AWS Account  

| What you receive (12‑month free tier) | Limits |
|---------------------------------------|--------|
| t2.micro / t3.micro Linux or Windows instance (1 vCPU, 1 GiB RAM) – 750 hrs/month | Only one such instance at a time |
| Amazon S3 – 5 GiB Standard storage, 20 k GET, 2 k PUT | Good for backups, static sites |
| Amazon RDS – 750 hrs of db.t2.micro (MySQL, PostgreSQL, etc.) | Optional |
| AWS Lambda – 1 M free requests & 400 k GB‑seconds | Optional |
| Other services (IAM, CloudWatch, etc.) – pay‑as‑you‑go | No cost if usage stays within free‑tier limits |

### Steps to create the account  

1. Open <https://aws.amazon.com/> and click **Create a Free Account**.  
2. Supply an email address, password, and account name.  
3. Provide billing information (credit or debit card). AWS will perform a small $1‑type authorization that is released immediately.  
4. Choose **Basic Support** (the free tier).  
5. Complete phone verification and sign in as the **root user**.

> **Important:** Do not use the root user for routine tasks. Create an IAM user with limited permissions in the next section.

---

## Create an IAM User for CLI Access  

1. Log in to the AWS Console as the root user.  
2. Open the **IAM** console: <https://console.aws.amazon.com/iam/>  
3. Choose **Users → Add user**.  
   * **User name:** choose a name you like (e.g., `mycli-user`).  
   * **Access type:** tick **Programmatic access** (creates an Access Key ID and Secret Access Key).  
4. Click **Next: Permissions**.  
   * Choose **Attach policies directly**.  
   * Search for and attach **AmazonEC2FullAccess** (or a custom, more‑restricted policy).  
   * Optionally also attach **IAMReadOnlyAccess** so you can list users, roles, etc.  
5. Review and click **Create user**.  
6. Download the generated *.csv* file – it contains the Access Key ID, Secret Access Key, and the console login URL.

### Store the credentials locally  

```bash
aws configure --profile free
# You will be prompted for:
#   AWS Access Key ID      (paste from CSV)
#   AWS Secret Access Key  (paste from CSV)
#   Default region name    (e.g., us-east-1)
#   Default output format json
```

The command writes `~/.aws/credentials` that now contains a `[free]` profile with your keys. All future CLI commands can be run with `--profile free` (or by setting `export AWS_PROFILE=free`).

---

## Install the AWS CLI in an Isolated Way  

You may pick any of the three methods below; each gives you a working `aws` binary without affecting your system Python or other tools.

### Docker (complete isolation)

```bash
# Pull the official image (≈100 MiB)
docker pull amazon/aws-cli

# Create a wrapper script so you can type “aws” directly
cat <<'EOF' > ~/bin/aws
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.aws:/root/.aws:ro" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/aws" \
  amazon/aws-cli "$@"
EOF
chmod +x ~/bin/aws
export PATH=$HOME/bin:$PATH   # add to your shell rc file (~/.bashrc, ~/.zshrc)
```

The script mounts your credential directory (`~/.aws`) and SSH keys (`~/.ssh`) into the container each time you run a command.

### Official bundle installer (Linux/macOS)

```bash
# Linux (x86_64) example
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --install-dir /opt/aws-cli --bin-dir /usr/local/bin
# macOS – same URL but with -darwin-, or simply:
brew install awscli
```

### pipx (Python sandbox)

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install awscli
```

Verify the installation:

```bash
aws --version
# Expected output: aws-cli/2.xx.xx Python/3.xx.xx <OS>
```

---

## Prepare Resources for SSH Access  

You need three objects:

* **Key pair** – private key used for SSH.  
* **Security group** – inbound rule permitting port 22 (SSH).  
* **EC2 instance** – the virtual machine you will connect to.

### Create a key pair

```bash
KEY_PATH=~/.ssh/free-key.pem
aws ec2 create-key-pair \
  --key-name free-key \
  --query "KeyMaterial" \
  --output text \
  --profile free > $KEY_PATH
chmod 400 $KEY_PATH
```

### Create a security group (allow SSH)

```bash
# Find the default VPC ID
VPC_ID=$(aws ec2 describe-vpcs \
  --query "Vpcs[0].VpcId" \
  --output text \
  --profile free)

# Create the security group
SG_ID=$(aws ec2 create-security-group \
  --group-name free-sg \
  --description "Free‑tier SG (SSH)" \
  --vpc-id $VPC_ID \
  --profile free \
  --output text)

# Open port 22 to the world (adjust CIDR if you prefer tighter security)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0 \
  --profile free

# (Optional) Open port 80 for a quick web test
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --profile free
```

### Launch a t2.micro (Free‑Tier) Amazon Linux 2 instance

```bash
# Retrieve the latest Amazon Linux 2 AMI ID for your region
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-2.0.*-x86_64-gp2" "Name=state,Values=available" \
  --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
  --output text \
  --profile free)

# Run the instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name free-key \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=free-demo}]' \
  --query "Instances[0].InstanceId" \
  --output text \
  --profile free)

echo "Instance launched: $INSTANCE_ID"
```

### Wait for the instance to be running and fetch its public IP

```bash
aws ec2 wait instance-running \
  --instance-ids $INSTANCE_ID \
  --profile free

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text \
  --profile free)

echo "Public IP: $PUBLIC_IP"
```

---

## Connect via SSH  

```bash
ssh -i ~/.ssh/free-key.pem ec2-user@$PUBLIC_IP
```

* The default username for Amazon Linux 2 is **ec2‑user**.  
* For Ubuntu AMIs use **ubuntu**.  
* For Amazon Linux 2023 also use **ec2‑user**.

You should see a prompt similar to:

```
[ec2-user@ip-xx-xx-xx-xx ~]$
```

You are now logged into the remote instance and can run any commands you need.

---

## Useful Starter Commands (Free‑Tier safe)

| Goal | Command | Description |
|------|---------|-------------|
| List all instances | `aws ec2 describe-instances --profile free --output table` | Shows instance ID, state, public IP, tags |
| Stop the instance (no compute charges) | `aws ec2 stop-instances --instance-ids $INSTANCE_ID --profile free` | Moves the instance to **stopped** |
| Start a stopped instance | `aws ec2 start-instances --instance-ids $INSTANCE_ID --profile free` | Brings it back up |
| Terminate (delete) the instance | `aws ec2 terminate-instances --instance-ids $INSTANCE_ID --profile free` | Ends the billable resource |
| Delete the key pair from AWS | `aws ec2 delete-key-pair --key-name free-key --profile free` | Removes the public key from AWS |
| Delete the security group (must be detached) | `aws ec2 delete-security-group --group-id $SG_ID --profile free` | Clean‑up |
| Show current month’s spend (should be $0‑$0.50 in free tier) | `aws ce get-cost-and-usage --time-period Start=$(date -d 'first day of month' +%Y-%m-%d),End=$(date +%Y-%m-%d) --granularity MONTHLY --metrics UnblendedCost --profile free` | Quick cost check |

`aws ec2 wait <state>` (e.g., `instance-running`, `instance-stopped`) is useful for scripts that need to pause until AWS reports the desired state.

---

## Clean‑Up Checklist (Avoid Unexpected Charges)

```bash
# Terminate the instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID --profile free
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID --profile free

# Delete the key pair (optional) and remove the private key locally
aws ec2 delete-key-pair --key-name free-key --profile free
rm -f ~/.ssh/free-key.pem

# Delete the security group
aws ec2 delete-security-group --group-id $SG_ID --profile free
```

Running these commands removes all running resources, guaranteeing that no further charges accrue.

---

## One‑Line Cheat Sheet (Copy‑Paste Ready)

```bash
# -------------------------------------------------
# 1️⃣ Install isolated CLI (Docker)
cat <<'EOF' > ~/bin/aws
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.aws:/root/.aws:ro" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/aws" \
  amazon/aws-cli "$@"
EOF
chmod +x ~/bin/aws
export PATH=$HOME/bin:$PATH   # add to your shell rc file

# -------------------------------------------------
# 2️⃣ Configure IAM profile (free tier)
aws configure --profile free
# → paste Access Key ID, Secret Access Key, region (e.g., us-east-1), output (json)

# -------------------------------------------------
# 3️⃣ Create key pair and security group
KEY=~/.ssh/free-key.pem
aws ec2 create-key-pair --key-name free-key --query "KeyMaterial" --output text > $KEY && chmod 400 $KEY

VPC_ID=$(aws ec2 describe-vpcs --query "Vpcs[0].VpcId" --output text --profile free)
SG_ID=$(aws ec2 create-security-group \
  --group-name free-sg \
  --description "Free tier SG" \
  --vpc-id $VPC_ID \
  --profile free \
  --output text)

aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --profile free

# -------------------------------------------------
# 4️⃣ Launch t2.micro (Amazon Linux 2)
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-2.0.*-x86_64-gp2" "Name=state,Values=available" \
  --query "Images | sort_by(@, &CreationDate) | [-1].ImageId" \
  --output text \
  --profile free)

INSTANCE_ID=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name free-key \
  --security-group-ids $SG_ID \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=free-demo}]' \
  --query "Instances[0].InstanceId" \
  --output text \
  --profile free)

aws ec2 wait instance-running --instance-ids $INSTANCE_ID --profile free
PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicIpAddress" --output text --profile free)

echo "Instance $INSTANCE_ID ready → $PUBLIC_IP"

# -------------------------------------------------
# 5️⃣ SSH into the instance
ssh -i $KEY ec2-user@$PUBLIC_IP

# -------------------------------------------------
# 6️⃣ Clean up when finished
aws ec2 terminate-instances --instance-ids $INSTANCE_ID --profile free
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID --profile free
aws ec2 delete-security-group --group-id $SG_ID --profile free
aws ec2 delete-key-pair --key-name free-key --profile free
rm -f $KEY
```

Execute the sections in order (or place the whole block into a script) to provision a free‑tier EC2 instance, connect via SSH, and clean up afterwards.

---

### Further Reading  

* **AWS CLI Reference** – <https://docs.aws.amazon.com/cli/latest/reference/>  
* **AWS Free Tier Details** – <https://aws.amazon.com/free/>  
* **Amazon Linux 2 User Guide** – <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/amazon-linux-ami-basics.html>  
* **IAM Best Practices** – <https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html>  
* **EC2 Instance Connect** (browser‑based SSH) – <https://aws.amazon.com/ec2/instance-connect/>

You now have a complete, plain‑text workflow for creating a free AWS account, installing the CLI in isolation, launching an EC2 instance, SSH’ing into it, and cleaning up afterward.