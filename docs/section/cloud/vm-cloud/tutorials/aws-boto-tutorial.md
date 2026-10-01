
**AWS – Native Python SDK (boto3) equivalent to the Libcloud example**  

The following material shows how to perform the same sequence that was demonstrated with Libcloud, but using the **official AWS SDK for Python (boto3)**.  

It covers  

* isolated installation of boto3,  
* a single `clouds.yaml` file that holds the AWS credentials,  
* reusable helper functions that wrap the low‑level boto3 calls,  
* a script that creates the free‑tier resources (key pair, security group, EC2 t2.micro / t3.micro instance),  
* retrieval of the public IP address,  
* a ready‑to‑run SSH command, and  
* a clean‑up routine that removes every resource that was created.  

Everything is written in plain Python 3 and contains no emojis or numbered icons.

---

## 1. Install boto3 in an isolated environment  

You can keep the SDK separate from the rest of your system using any of the three methods below.

### Docker wrapper (complete isolation)

```bash
docker pull python:3.12-slim

cat <<'EOF' > ~/bin/boto3
#!/usr/bin/env bash
docker run --rm -it \
  -v "$HOME/.aws:/root/.aws:rw" \
  -v "$HOME/.ssh:/root/.ssh:ro" \
  -v "$(pwd):/workdir" \
  -w /workdir \
  python:3.12-slim \
  bash -c "pip install --quiet boto3 PyYAML && python3 \"\$@\"" \
  "$@"
EOF
chmod +x ~/bin/boto3
export PATH=$HOME/bin:$PATH   # add to your shell rc file (.bashrc, .zshrc)
```

Running `boto3 myscript.py` will install boto3 inside the container, mount your current directory and your SSH keys, and then execute the script.

### Native virtual‑environment installer

```bash
python3 -m venv .aws‑venv
source .aws‑venv/bin/activate
pip install --upgrade pip
pip install boto3 PyYAML
```

### pipx sandbox

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install boto3
pipx install PyYAML
```

All three approaches give you a `python` interpreter with the `boto3` and `yaml` packages available.

---

## 2. The common `clouds.yaml` file (AWS only)

```yaml
aws:
  key: YOUR_AWS_ACCESS_KEY_ID
  secret: YOUR_AWS_SECRET_ACCESS_KEY
  region: us-east-1                # any region that offers the free‑tier instance
```

Replace the placeholders with the values from the IAM user that you created in the *AWS* section of the previous tutorial.  
The file must be placed in the same directory as the Python script.

---

## 3. Helper module – `aws_helpers.py`

```python
# aws_helpers.py
import time
import boto3
import yaml
import os
from botocore.exceptions import ClientError


def load_config(path="clouds.yaml"):
    """Read clouds.yaml and return the aws dictionary."""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["aws"]


def get_session(cfg):
    """Create a boto3 Session from the yaml dictionary."""
    return boto3.Session(
        aws_access_key_id=cfg["key"],
        aws_secret_access_key=cfg["secret"],
        region_name=cfg["region"],
    )


def ensure_key_pair(ec2, key_name, key_path):
    """
    Create an EC2 key pair if it does not exist locally.
    The private key is written to ``key_path`` and the permissions are set to 400.
    """
    if os.path.isfile(key_path):
        return

    try:
        response = ec2.create_key_pair(KeyName=key_name)
    except ClientError as e:
        # If the key already exists in AWS we can simply download it
        if e.response["Error"]["Code"] == "InvalidKeyPair.Duplicate":
            raise RuntimeError(
                f"Key pair {key_name} already exists in AWS. "
                "Delete the existing key from the console or choose another name."
            )
        else:
            raise

    private_key = response["KeyMaterial"]
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(private_key)
    os.chmod(key_path, 0o400)


def ensure_security_group(ec2, sg_name):
    """
    Create a security group that allows inbound SSH (port 22) from anywhere.
    Returns the security group id.
    """
    try:
        response = ec2.create_security_group(
            GroupName=sg_name,
            Description="Free‑tier SG for SSH access",
        )
        sg_id = response["GroupId"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidGroup.Duplicate":
            # Retrieve the existing group id
            sg = ec2.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [sg_name]}]
            )
            sg_id = sg["SecurityGroups"][0]["GroupId"]
        else:
            raise

    # Authorize inbound SSH if not already present
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
            raise
    return sg_id


def launch_instance(ec2, ami_id, instance_type, key_name, security_group_id, tag_name):
    """
    Launch an EC2 instance and return the Instance object.
    """
    instances = ec2.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [{"Key": "Name", "Value": tag_name}],
            }
        ],
    )
    return instances["Instances"][0]


def wait_for_instance(ec2, instance_id, timeout=300, interval=5):
    """
    Poll the instance until it is in the 'running' state and has a public IPv4 address.
    Returns the public IP address.
    """
    elapsed = 0
    while elapsed < timeout:
        resp = ec2.describe_instances(InstanceIds=[instance_id])
        state = resp["Reservations"][0]["Instances"][0]["State"]["Name"]
        if state == "running":
            ip = resp["Reservations"][0]["Instances"][0].get("PublicIpAddress")
            if ip:
                return ip
        time.sleep(interval)
        elapsed += interval
    raise RuntimeError(f"Instance {instance_id} did not become ready within {timeout}s")


def terminate_instance(ec2, instance_id):
    """Stop and terminate the instance."""
    ec2.stop_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter("instance_stopped")
    waiter.wait(InstanceIds=[instance_id])
    ec2.terminate_instances(InstanceIds=[instance_id])
    waiter = ec2.get_waiter("instance_terminated")
    waiter.wait(InstanceIds=[instance_id])
```

The helper functions hide all the provider‑specific API details (key‑pair creation, security‑group handling, instance lifecycle) while keeping the public interface simple.

---

## 4. Main script – `run_aws_free_vm.py`

```python
#!/usr/bin/env python3
# run_aws_free_vm.py
import os
import sys
from aws_helpers import (
    load_config,
    get_session,
    ensure_key_pair,
    ensure_security_group,
    launch_instance,
    wait_for_instance,
    terminate_instance,
)

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
CFG = load_config()
SESSION = get_session(CFG)
EC2 = SESSION.client("ec2")

# ----------------------------------------------------------------------
# Resource names (adjust if you run the script multiple times)
# ----------------------------------------------------------------------
KEY_NAME = "libcloud-aws-free"
KEY_PATH = os.path.expanduser(f"~/.ssh/{KEY_NAME}.pem")
SG_NAME = "libcloud-aws-free-sg"
INSTANCE_TAG = "libcloud-aws-free"

# ----------------------------------------------------------------------
# 1. Key pair
# ----------------------------------------------------------------------
ensure_key_pair(EC2, KEY_NAME, KEY_PATH)

# ----------------------------------------------------------------------
# 2. Security group
# ----------------------------------------------------------------------
sg_id = ensure_security_group(EC2, SG_NAME)

# ----------------------------------------------------------------------
# 3. AMI – Amazon Linux 2 (free‑tier) for us-east-1
# ----------------------------------------------------------------------
# This AMI id is static as of 2024‑10. If you want the latest automatically,
# you can query the SSM parameter store instead.
AMI_ID = "ami-0b2f6494ff0b07a0e"

# ----------------------------------------------------------------------
# 4. Instance type – t2.micro (free tier)
# ----------------------------------------------------------------------
INSTANCE_TYPE = "t2.micro"

# ----------------------------------------------------------------------
# 5. Launch the instance
# ----------------------------------------------------------------------
instance = launch_instance(
    EC2,
    ami_id=AMI_ID,
    instance_type=INSTANCE_TYPE,
    key_name=KEY_NAME,
    security_group_id=sg_id,
    tag_name=INSTANCE_TAG,
)
instance_id = instance["InstanceId"]
print(f"Instance launched – ID: {instance_id}")

# ----------------------------------------------------------------------
# 6. Wait for the instance to become reachable
# ----------------------------------------------------------------------
public_ip = wait_for_instance(EC2, instance_id)
print(f"Instance is running – public IP: {public_ip}")

# ----------------------------------------------------------------------
# 7. Print SSH command
# ----------------------------------------------------------------------
print("\n=== SSH command ===")
print(f"ssh -i \"{KEY_PATH}\" ec2-user@{public_ip}")

# ----------------------------------------------------------------------
# 8. Optional clean‑up
# ----------------------------------------------------------------------
if "--destroy" in sys.argv:
    print("\nCleaning up resources …")
    terminate_instance(EC2, instance_id)

    # Delete the key pair from AWS (keep the local private key if you want to reuse it)
    EC2.delete_key_pair(KeyName=KEY_NAME)

    # Delete the security group
    EC2.delete_security_group(GroupId=sg_id)

    # Optionally remove the local key file
    try:
        os.remove(KEY_PATH)
    except OSError:
        pass

    print("All resources removed.")
```

### How to run the script

```bash
# Using the Docker wrapper created in section 1
boto3 run_aws_free_vm.py          # creates the VM and prints the SSH command
boto3 run_aws_free_vm.py --destroy   # terminates the VM and removes the SG/key pair
```

If you installed boto3 in a native virtual‑environment, simply run:

```bash
python run_aws_free_vm.py
python run_aws_free_vm.py --destroy
```

The script follows the exact same logical steps that were shown for Libcloud, but now uses **boto3** directly.

---

## 5. What the script does – step‑by‑step summary (no numbering icons)

* Reads the AWS access key, secret, and region from `clouds.yaml`.  
* Creates a boto3 session and an EC2 client.  
* Generates an EC2 key pair named `libcloud-aws-free` if it does not already exist locally; the private key is written to `~/.ssh/libcloud-aws-free.pem`.  
* Creates a security group that permits inbound TCP 22 from any address.  
* Looks up a public Amazon Linux 2 AMI that is free‑tier eligible (hard‑coded for `us-east-1`).  
* Launches a `t2.micro` instance using the key pair and security group.  
* Polls the instance until it reaches the **running** state and a public IPv4 address is allocated.  
* Prints a ready‑to‑run SSH command that uses the generated private key.  
* If the `--destroy` flag is supplied, the script stops and terminates the instance, deletes the key pair from AWS, removes the security group, and optionally deletes the local private key file.

All resources created by the script are covered by the **AWS Free Tier** (t2.micro – 750 hours/month, 1 GB of EBS storage, 5 GB of S3, etc.). As long as you keep the instance running for fewer than 750 hours per month and do not attach additional paid resources, you will not incur any charges.

---

## 6. Common pitfalls and how to avoid them

* **Incorrect AMI ID** – The AMI identifier is region specific. If you switch `region` in `clouds.yaml` you must also change `AMI_ID` to a matching Amazon Linux 2 image for that region.  
* **Existing key pair with the same name** – AWS does not allow two key pairs with identical names. Either delete the existing key from the console or give the script a different `KEY_NAME`.  
* **Security‑group limits** – AWS permits a maximum of 500 security groups per VPC. The helper checks for an existing group before creating a new one, so rerunning the script does not create duplicates.  
* **Instance type unavailable in the chosen region** – The free‑tier instance type (`t2.micro` or `t3.micro`) is only available in certain regions. If you receive a `InvalidParameterValue` error, verify that the selected region supports the free‑tier shape.  
* **Rate‑limit errors** – Boto3 automatically retries on throttling, but if you launch many instances in a short period you may still hit the limit. Insert a short `time.sleep()` between operations if needed.  

---

## 7. Extending the script to other AWS services

Because the script already establishes a `boto3.Session`, you can reuse the session object to interact with other free‑tier services (S3, DynamoDB, Lambda, etc.) without adding any additional configuration files. Example snippets:

```python
# S3 – create a bucket (free‑tier up to 5 GB)
s3 = SESSION.resource("s3")
bucket_name = f"libcloud-demo-{SESSION.region_name}"
s3.create_bucket(Bucket=bucket_name,
                 CreateBucketConfiguration={"LocationConstraint": SESSION.region_name})

# DynamoDB – create a table (free‑tier 25 GB)
dynamodb = SESSION.client("dynamodb")
dynamodb.create_table(
    TableName="libcloud-demo",
    AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
    KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
    BillingMode="PAY_PER_REQUEST",
)
```

These calls respect the same free‑tier quotas that are documented on the AWS Free Tier page.

---

## 8. Full cheat‑sheet (single file)

Below is a compact version of the full workflow that you can copy directly into a file called `aws_free_vm_onefile.py`. It contains the helpers inline, reads `clouds.yaml`, launches the VM, prints the SSH command, and deletes everything when `--destroy` is supplied.

```python
#!/usr/bin/env python3
import os, sys, time, yaml, boto3
from botocore.exceptions import ClientError

def load_cfg():
    with open("clouds.yaml") as f:
        return yaml.safe_load(f)["aws"]

def session(cfg):
    return boto3.Session(
        aws_access_key_id=cfg["key"],
        aws_secret_access_key=cfg["secret"],
        region_name=cfg["region"],
    )

def key_pair(ec2, name, path):
    if not os.path.isfile(path):
        kp = ec2.create_key_pair(KeyName=name)
        with open(path, "w") as f:
            f.write(kp["KeyMaterial"])
        os.chmod(path, 0o400)

def security_group(ec2, name):
    try:
        resp = ec2.create_security_group(
            GroupName=name, Description="Free‑tier SSH SG"
        )
        sg_id = resp["GroupId"]
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidGroup.Duplicate":
            sg = ec2.describe_security_groups(
                Filters=[{"Name": "group-name", "Values": [name]}]
            )
            sg_id = sg["SecurityGroups"][0]["GroupId"]
        else:
            raise
    try:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidPermission.Duplicate":
            raise
    return sg_id

def launch(ec2, ami, itype, key, sg, tag):
    ins = ec2.run_instances(
        ImageId=ami,
        InstanceType=itype,
        MinCount=1,
        MaxCount=1,
        KeyName=key,
        SecurityGroupIds=[sg],
        TagSpecifications=[{
            "ResourceType":"instance",
            "Tags":[{"Key":"Name","Value":tag}]
        }],
    )
    return ins["Instances"][0]["InstanceId"]

def wait_ip(ec2, iid, timeout=300, step=5):
    elapsed = 0
    while elapsed < timeout:
        resp = ec2.describe_instances(InstanceIds=[iid])
        state = resp["Reservations"][0]["Instances"][0]["State"]["Name"]
        if state == "running":
            ip = resp["Reservations"][0]["Instances"][0].get("PublicIpAddress")
            if ip:
                return ip
        time.sleep(step)
        elapsed += step
    raise RuntimeError("Timeout waiting for public IP")

def cleanup(ec2, iid, key, sg):
    ec2.stop_instances(InstanceIds=[iid])
    ec2.get_waiter("instance_stopped").wait(InstanceIds=[iid])
    ec2.terminate_instances(InstanceIds=[iid])
    ec2.get_waiter("instance_terminated").wait(InstanceIds=[iid])
    ec2.delete_key_pair(KeyName=key)
    ec2.delete_security_group(GroupId=sg)

# -------------------- main --------------------
cfg = load_cfg()
sess = session(cfg)
ec2 = sess.client("ec2")

KEY_NAME = "libcloud-aws-free"
KEY_PATH = os.path.expanduser(f"~/.ssh/{KEY_NAME}.pem")
SG_NAME  = "libcloud-aws-free-sg"
TAG_NAME = "libcloud-aws-free"

key_pair(ec2, KEY_NAME, KEY_PATH)
sg_id = security_group(ec2, SG_NAME)

# Amazon Linux 2 AMI for us-east-1 (change if you use another region)
AMI_ID = "ami-0b2f6494ff0b07a0e"
INSTANCE_TYPE = "t2.micro"

instance_id = launch(ec2, AMI_ID, INSTANCE_TYPE, KEY_NAME, sg_id, TAG_NAME)
public_ip   = wait_ip(ec2, instance_id)

print("\nInstance ready – public IP:", public_ip)
print(f"\nSSH command:\nssh -i \"{KEY_PATH}\" ec2-user@{public_ip}")

if "--destroy" in sys.argv:
    print("\nDestroying resources …")
    cleanup(ec2, instance_id, KEY_NAME, sg_id)
    try:
        os.remove(KEY_PATH)
    except OSError:
        pass
    print("All resources removed.")
```

Save this file next to `clouds.yaml`, make it executable (`chmod +x aws_free_vm_onefile.py`) and run:

```bash
./aws_free_vm_onefile.py          # start instance
./aws_free_vm_onefile.py --destroy  # stop and delete everything
```

---

## 9. References  

* boto3 documentation – <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>  
* AWS Free Tier – <https://aws.amazon.com/free/>  
* EC2 API reference – <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_Operations.html>  
* IAM user‑access‑key creation – <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html>  

With this script you have a **native‑SDK** counterpart to the Libcloud example, allowing you to manage the AWS free‑tier EC2 instance (and, by extension, any other AWS service) using pure `boto3` calls while keeping the code and configuration consistent across clouds. Happy scripting!