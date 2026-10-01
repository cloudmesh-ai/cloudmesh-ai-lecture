# AWS Native Python SDK (boto3)

!!! info "Learning Objectives"
    * Install the boto3 SDK in an isolated environment.
    * Configure AWS credentials using a standardized YAML file.
    * Develop helper functions to manage EC2 key pairs and security groups.
    * Implement an automated workflow to launch and terminate free-tier EC2 instances.
    * Extend the boto3 session to interact with other AWS services like S3 and DynamoDB.

## Overview

This chapter demonstrates how to perform cloud resource management using the official AWS SDK for Python (boto3). It provides a direct counterpart to the Libcloud examples, showing how to handle the full lifecycle of a virtual machine—from environment setup and credential management to instance deployment and resource cleanup—using native SDK calls.

## Core Sections

### Installation and Environment

You can keep the SDK separate from the rest of your system using any of the three methods below.

#### Docker wrapper (complete isolation)

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
export PATH=$HOME/bin:$PATH
```

Running `boto3 myscript.py` will install boto3 inside the container, mount your current directory and your SSH keys, and then execute the script.

#### Native virtual-environment installer

```bash
python3 -m venv .aws-venv
source .aws-venv/bin/activate
pip install --upgrade pip
pip install boto3 PyYAML
```

#### pipx sandbox

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install boto3
pipx install PyYAML
```

All three approaches provide a `python` interpreter with the `boto3` and `yaml` packages available.

### Configuration with clouds.yaml

To avoid hard-coding credentials, use a `clouds.yaml` file to store AWS access keys and the target region.

```yaml
aws:
    key: YOUR_AWS_ACCESS_KEY_ID
    secret: YOUR_AWS_SECRET_ACCESS_KEY
    region: us-east-1
```

Replace the placeholders with the values from the IAM user created in the AWS setup guide. The file must be placed in the same directory as the Python script.

### Implementing AWS Helpers

The following helper module, `aws_helpers.py`, wraps low-level boto3 calls into reusable functions for managing keys, security groups, and instances.

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
The private key is written to key_path and the permissions are set to 400.
"""
if os.path.isfile(key_path):
    return

try:
    response = ec2.create_key_pair(KeyName=key_name)
except ClientError as e:
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
        Description="Free-tier SG for SSH access",
    )
    sg_id = response["GroupId"]
except ClientError as e:
    if e.response["Error"]["Code"] == "InvalidGroup.Duplicate":
        sg = ec2.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [sg_name]}]
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

### Orchestrating EC2 with run_aws_free_vm.py

The main orchestration script uses the helper module to deploy a free-tier instance and provide the SSH connection string.

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

# Configuration
CFG = load_config()
SESSION = get_session(CFG)
EC2 = SESSION.client("ec2")

# Resource names
KEY_NAME = "libcloud-aws-free"
KEY_PATH = os.path.expanduser(f"~/.ssh/{KEY_NAME}.pem")
SG_NAME = "libcloud-aws-free-sg"
INSTANCE_TAG = "libcloud-aws-free"

# 1. Key pair
ensure_key_pair(EC2, KEY_NAME, KEY_PATH)

# 2. Security group
sg_id = ensure_security_group(EC2, SG_NAME)

# 3. AMI - Amazon Linux 2 (free-tier) for us-east-1
AMI_ID = "ami-0b2f6494ff0b07a0e"

# 4. Instance type - t2.micro (free tier)
INSTANCE_TYPE = "t2.micro"

# 5. Launch the instance
instance = launch_instance(
EC2,
ami_id=AMI_ID,
instance_type=INSTANCE_TYPE,
key_name=KEY_NAME,
security_group_id=sg_id,
tag_name=INSTANCE_TAG,
)
instance_id = instance["InstanceId"]
print(f"Instance launched - ID: {instance_id}")

# 6. Wait for the instance to become reachable
public_ip = wait_for_instance(EC2, instance_id)
print(f"Instance is running - public IP: {public_ip}")

# 7. Print SSH command
print("\n=== SSH command ===")
print(f"ssh -i \"{KEY_PATH}\" ec2-user@{public_ip}")

# 8. Optional clean-up
if "--destroy" in sys.argv:
print("\nCleaning up resources ...")
terminate_instance(EC2, instance_id)

EC2.delete_key_pair(KeyName=KEY_NAME)
EC2.delete_security_group(GroupId=sg_id)

try:
    os.remove(KEY_PATH)
except OSError:
    pass
print("All resources removed.")
```

#### How to run the script

```bash
# Using the Docker wrapper
boto3 run_aws_free_vm.py
boto3 run_aws_free_vm.py --destroy

# Using native virtual-environment
python run_aws_free_vm.py
python run_aws_free_vm.py --destroy
```

### Operational Summary

The deployment workflow follows these logical steps:

* Read AWS credentials and region from `clouds.yaml`.
* Initialize a boto3 session and an EC2 client.
* Generate an EC2 key pair named `libcloud-aws-free` and save the private key locally to `~/.ssh/libcloud-aws-free.pem`.
* Create a security group permitting inbound TCP port 22 from any address.
* Launch a `t2.micro` instance using a free-tier eligible Amazon Linux 2 AMI.
* Poll the instance until it reaches the running state and receives a public IPv4 address.
* Output a ready-to-use SSH command.
* If `--destroy` is passed, terminate the instance and remove the associated security group and key pair.

All resources used in this workflow are covered by the AWS Free Tier (t2.micro, 1 GB EBS storage), provided the usage remains within the monthly limits.

### Pitfalls and Troubleshooting

* **AMI Region Mismatch**: AMI identifiers are region-specific. If the `region` in `clouds.yaml` is changed, the `AMI_ID` must be updated to match a valid image for that region.
* **Key Pair Duplication**: AWS prevents multiple key pairs from sharing the same name. If a naming conflict occurs, delete the existing key via the AWS Console or modify `KEY_NAME` in the script.
* **Security Group Limits**: While AWS allows many security groups per VPC, the script prevents duplication by checking for the existing group name before creation.
* **Instance Availability**: Free-tier types like `t2.micro` may be unavailable in certain regions. If an `InvalidParameterValue` error is received, verify regional support for the instance type.
* **API Throttling**: High-frequency API calls may trigger rate limits. Although boto3 includes automatic retries, inserting `time.sleep()` between operations can mitigate this in large-scale deployments.

### Extending to other AWS Services

A `boto3.Session` can be reused to interact with other free-tier services without additional configuration.

```python
# S3 - create a bucket (free-tier up to 5 GB)
s3 = SESSION.resource("s3")
bucket_name = f"libcloud-demo-{SESSION.region_name}"
s3.create_bucket(Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": SESSION.region_name})

# DynamoDB - create a table (free-tier 25 GB)
dynamodb = SESSION.client("dynamodb")
dynamodb.create_table(
TableName="libcloud-demo",
AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
BillingMode="PAY_PER_REQUEST",
)
```

### Consolidated Implementation

For a single-file deployment, the following consolidated script includes all helpers and orchestration logic.

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
        GroupName=name, Description="Free-tier SSH SG"
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

cfg = load_cfg()
sess = session(cfg)
ec2 = sess.client("ec2")

KEY_NAME = "libcloud-aws-free"
KEY_PATH = os.path.expanduser(f"~/.ssh/{KEY_NAME}.pem")
SG_NAME  = "libcloud-aws-free-sg"
TAG_NAME = "libcloud-aws-free"

key_pair(ec2, KEY_NAME, KEY_PATH)
sg_id = security_group(ec2, SG_NAME)

AMI_ID = "ami-0b2f6494ff0b07a0e"
INSTANCE_TYPE = "t2.micro"

instance_id = launch(ec2, AMI_ID, INSTANCE_TYPE, KEY_NAME, sg_id, TAG_NAME)
public_ip   = wait_ip(ec2, instance_id)

print("\nInstance ready - public IP:", public_ip)
print(f"\nSSH command:\nssh -i \"{KEY_PATH}\" ec2-user@{public_ip}")

if "--destroy" in sys.argv:
print("\nDestroying resources ...")
cleanup(ec2, instance_id, KEY_NAME, sg_id)
try:
    os.remove(KEY_PATH)
except OSError:
    pass
print("All resources removed.")
```

## Summary Checklist

* [ ] Install `boto3` and `PyYAML` using a virtual environment or Docker.
* [ ] Create a `clouds.yaml` file with valid AWS IAM credentials.
* [ ] Implement helper functions for key pair and security group management.
* [ ] Run the orchestration script to launch a `t2.micro` instance.
* [ ] Verify SSH connectivity to the public IP address.
* [ ] Run the script with the `--destroy` flag to clean up all AWS resources.

## Assignments

!!! note "Assignment.1: Native Deployment"
    Set up an isolated Python environment, configure `clouds.yaml`, and run the provided orchestration script to launch a free-tier EC2 instance. Verify you can SSH into the machine.

    ??? tip "Solution: Native Deployment"
        Follow the installation steps in the Environment section. Ensure your IAM user has `AmazonEC2FullAccess`. Run `python run_aws_free_vm.py` and use the printed SSH command.

!!! note "Assignment.2: Regional Migration"
    Modify the script to launch the instance in a different AWS region (e.g., `us-west-2`). You will need to find a valid free-tier Amazon Linux 2 AMI ID for that specific region.

    ??? tip "Solution: Regional Migration"
        Update the `region` in `clouds.yaml` to `us-west-2`. Search the AWS AMI Catalog for the Amazon Linux 2 AMI ID for `us-west-2` and update `AMI_ID` in the script.

!!! note "Assignment.3: Multi-Service Orchestration"
    Extend the script to create an S3 bucket with a unique name after the EC2 instance is launched. Ensure the bucket is also created in the region specified in `clouds.yaml`.

    ??? tip "Solution: Multi-Service Orchestration"
        Add the S3 creation snippet from the "Extending to other AWS Services" section to the main loop of `run_aws_free_vm.py` after the `wait_for_instance` call.

## References

* boto3 documentation - <https://boto3.amazonaws.com/v1/documentation/api/latest/index.html>
* AWS Free Tier - <https://aws.amazon.com/free/>
* EC2 API reference - <https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_Operations.html>
* IAM user-access-key creation - <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html>

## Self-Evaluation

??? note "How does boto3 handle credentials when a session is created manually?"
    When using `boto3.Session(aws_access_key_id=..., aws_secret_access_key=...)`, the session explicitly uses the provided keys, bypassing the default credential search order (environment variables, ~/.aws/credentials).

??? note "Why is it necessary to poll the instance state after the run_instances call?"
    The `run_instances` call is asynchronous; it returns as soon as the request is accepted. The instance takes several seconds to initialize and be assigned a public IP address, so the script must poll `describe_instances` until the state is 'running' and the IP is available.

??? note "What is the risk of using 0.0.0.0/0 in a security group?"
    Using `0.0.0.0/0` allows any IP address on the internet to attempt a connection to port 22 (SSH). In production, this should be restricted to a specific trusted IP address or range to prevent brute-force attacks.
