
# Spot‑Pricing Guide – AWS, Azure, Google Cloud, Oracle Cloud  
**How to launch a 1 vCPU + 1 GiB Ubuntu 26.04 VM with spot (pre‑emptible) pricing**  
The guide is divided into three parts for each cloud provider:

1. **Command‑Line Interface (CLI)** – the provider’s native command‑line tools.  
2. **Libcloud** – a single Python library that works across clouds.  
3. **Native SDK** – the official Python SDK for the provider (boto3, azure‑mgmt, google‑cloud‑compute, oci).  

A single **`clouds.yaml`** file is shown at the end; the same file can be used by the Libcloud examples and by the native SDK scripts (the SDK sections read the file to obtain credentials and spot parameters).

---

## 1. Amazon Web Services (AWS)

### 1.1 CLI – `aws`  

```bash
# Create a spot instance (t3.micro, Ubuntu 26.04)
aws ec2 run-instances \
  --instance-type t3.micro \
  --image-id ami-0b2f6494ff0b07a0e      # Ubuntu 26.04 LTS in us-east-1 (example)
  --key-name my-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --instance-market-options MarketType=spot,SpotOptions={InstanceInterruptionBehavior=terminate} \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=spot-aws}]'
```

*Key options*

* `MarketType=spot` – requests spot capacity.  
* `InstanceInterruptionBehavior=terminate` – terminates the instance on interruption (alternatives: `stop`, `hibernate`).  
* No explicit max price is required; AWS uses the current spot price.  

### 1.2 Libcloud (Python)

```python
import yaml
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

# Load configuration
with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["aws"]

# Build driver (boto driver)
Driver = get_driver(Provider.EC2)
driver = Driver(
    key=cfg["key"],
    secret=cfg["secret"],
    region=cfg["region"]
)

# Choose the free‑tier compatible image (Ubuntu 26.04)
images = driver.list_images()
ubuntu = next(img for img in images if "ubuntu-26.04" in img.name.lower())

# Spot options are passed via the extra argument `ex_spot_price` (optional) and `ex_instance_market`
node = driver.create_node(
    name="spot-aws-libcloud",
    size=next(s for s in driver.list_sizes() if s.id == "t3.micro"),
    image=ubuntu,
    ex_instance_market="spot",          # request spot market
    # optional max price (in USD per hour); omit to use current spot price
    # ex_spot_price="0.0030",
    ex_keyname="my-key-pair",
    ex_security_group="default"
)

print("Instance ID:", node.id)
```

### 1.3 Native SDK – `boto3`

```python
import yaml
import boto3

# Load configuration
with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["aws"]

session = boto3.Session(
    aws_access_key_id=cfg["key"],
    aws_secret_access_key=cfg["secret"],
    region_name=cfg["region"]
)
ec2 = session.client("ec2")

# Spot launch request
response = ec2.run_instances(
    ImageId="ami-0b2f6494ff0b07a0e",   # Ubuntu 26.04 LTS
    InstanceType="t3.micro",
    MinCount=1,
    MaxCount=1,
    KeyName="my-key-pair",
    SecurityGroupIds=["sg-xxxxxxxx"],
    SubnetId="subnet-xxxxxxxx",
    InstanceMarketOptions={
        "MarketType": "spot",
        "SpotOptions": {
            "InstanceInterruptionBehavior": "terminate",
            # "MaxPrice": "0.0030",   # optional ceiling price
        }
    },
    TagSpecifications=[
        {
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "spot-aws-sdk"}],
        }
    ],
)

instance_id = response["Instances"][0]["InstanceId"]
print("Launched spot instance:", instance_id)
```

---

## 2. Microsoft Azure

### 2.1 CLI – `az`

```bash
# Spot VM (B1s, Ubuntu 26.04) in East US
az vm create \
  --resource-group my-rg \
  --name spot-azure \
  --image UbuntuLTS \
  --size Standard_B1s \
  --admin-username azureuser \
  --ssh-key-value @~/.ssh/id_rsa.pub \
  --priority Spot \
  --eviction-policy Deallocate \
  --max-price -1             # -1 = accept current spot price
```

*Key options*

* `--priority Spot` – tells Azure to use spot capacity.  
* `--eviction-policy Deallocate` – instance is deallocated (may be restarted later).  
* `--max-price -1` – no ceiling; Azure charges the current spot price.

### 2.2 Libcloud (Python)

```python
import yaml
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["azure"]

Driver = get_driver(Provider.AZURE_ARM)
driver = Driver(
    tenant_id=cfg["tenant_id"],
    client_id=cfg["client_id"],
    client_secret=cfg["client_secret"],
    subscription_id=cfg["subscription_id"],
    region=cfg["location"]
)

# Azure images are identified by publisher/offer/sku/version
image = driver.get_image(
    publisher="Canonical",
    offer="UbuntuServer",
    sku="22_04-lts-gen2",   # Ubuntu 22.04 LTS, Ubuntu 26.04 not yet published – adjust accordingly
    version="latest"
)

size = next(s for s in driver.list_sizes() if s.id == "Standard_B1s")

node = driver.create_node(
    name="spot-azure-libcloud",
    size=size,
    image=image,
    ex_vm_priority="Spot",        # request spot
    ex_eviction_policy="Deallocate",
    ex_max_price=-1,              # accept current price
    ex_admin_username="azureuser",
    ex_ssh_key="~/.ssh/id_rsa.pub"
)

print("Azure spot VM ID:", node.id)
```

### 2.3 Native SDK – `azure-mgmt-compute`

```python
import yaml
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["azure"]

credential = ClientSecretCredential(
    tenant_id=cfg["tenant_id"],
    client_id=cfg["client_id"],
    client_secret=cfg["client_secret"]
)

subscription_id = cfg["subscription_id"]
resource_group = "my-rg"
location = cfg["location"]

compute = ComputeManagementClient(credential, subscription_id)
network = NetworkManagementClient(credential, subscription_id)
resource = ResourceManagementClient(credential, subscription_id)

# Assume a VNet, subnet, NSG, and public IP already exist.
subnet_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/myVnet/subnets/default".format(
    subscription_id, resource_group
)

nic_params = {
    "location": location,
    "ip_configurations": [{
        "name": "ipconfig1",
        "subnet": {"id": subnet_id},
        "public_ip_address": {
            "id": "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/publicIPAddresses/myPIP".format(
                subscription_id, resource_group
            )
        }
    }]
}
nic = network.network_interfaces.begin_create_or_update(
    resource_group,
    "spot-azure-nic",
    nic_params
).result()

vm_parameters = {
    "location": location,
    "hardware_profile": {"vm_size": "Standard_B1s"},
    "storage_profile": {
        "image_reference": {
            "publisher": "Canonical",
            "offer": "UbuntuServer",
            "sku": "22_04-lts-gen2",
            "version": "latest"
        }
    },
    "os_profile": {
        "computer_name": "spotazure",
        "admin_username": "azureuser",
        "linux_configuration": {
            "disable_password_authentication": True,
            "ssh": {"public_keys": [{
                "path": "/home/azureuser/.ssh/authorized_keys",
                "key_data": open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()
            }]}
        }
    },
    "network_profile": {"network_interfaces": [{"id": nic.id}]},
    "priority": "Spot",
    "eviction_policy": "Deallocate",
    "billing_profile": {"max_price": -1}   # -1 = accept current spot price
}

vm = compute.virtual_machines.begin_create_or_update(
    resource_group,
    "spot-azure-sdk",
    vm_parameters
).result()

print("Created Azure Spot VM:", vm.id)
```

---

## 3. Google Cloud Platform (GCP)

### 3.1 CLI – `gcloud`

```bash
# Spot (preemptible) VM – e2‑micro, Ubuntu 26.04
gcloud compute instances create spot-gcp \
  --machine-type=e2-micro \
  --image-family=ubuntu-2604 \
  --image-project=ubuntu-os-cloud \
  --metadata=ssh-keys="$(cat ~/.ssh/id_rsa.pub)" \
  --preemptible \
  --boot-disk-size=30GB
```

*Key flag*

* `--preemptible` – requests a spot VM (maximum lifetime 24 h). No price argument is needed; the price is fixed at the current discount.

### 3.2 Libcloud (Python)

```python
import yaml
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["gcp"]

Driver = get_driver(Provider.GCE)
driver = Driver(
    key=cfg["service_account_key"],
    project=cfg["project_id"],
    region=cfg["region"]
)

# GCE image (Ubuntu 26.04)
image = driver.get_image(
    project="ubuntu-os-cloud",
    name="ubuntu-2604-lts"
)

size = next(s for s in driver.list_sizes() if s.id == "e2-micro")

node = driver.create_node(
    name="spot-gcp-libcloud",
    size=size,
    image=image,
    ex_preemptible=True,               # spot request
    ex_tags=["ssh"],                  # optional network tag
    ex_metadata={"ssh-keys": open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()}
)

print("GCP spot instance ID:", node.id)
```

### 3.3 Native SDK – `google-cloud-compute`

```python
import yaml
import time
from google.oauth2 import service_account
from google.cloud import compute_v1

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["gcp"]

credentials = service_account.Credentials.from_service_account_file(
    cfg["service_account_key"]
)
project = cfg["project_id"]
zone = cfg["zone"]          # e.g. "us-central1-a"

instances_client = compute_v1.InstancesClient(credentials=credentials)

# Choose the Ubuntu 26.04 image (use list_images to find the OCID)
image_response = compute_v1.ImagesClient(credentials=credentials).list(
    project="ubuntu-os-cloud",
    filter='name eq "ubuntu-2604-lts.*"'
)
image = next(image_response)   # first result
image_link = image.self_link

instance = compute_v1.Instance(
    name="spot-gcp-sdk",
    machine_type=f"zones/{zone}/machineTypes/e2-micro",
    disks=[
        compute_v1.AttachedDisk(
            boot=True,
            auto_delete=True,
            initialize_params=compute_v1.AttachedDiskInitializeParams(
                source_image=image_link,
                disk_size_gb=30
            )
        )
    ],
    network_interfaces=[
        compute_v1.NetworkInterface(
            name="nic0",
            access_configs=[
                compute_v1.AccessConfig(
                    name="External NAT",
                    type_=compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT
                )
            ]
        )
    ],
    scheduling=compute_v1.Scheduling(
        preemptible=True,
        on_host_maintenance="TERMINATE"
    ),
    metadata=compute_v1.Metadata(
        items=[compute_v1.Items(
            key="ssh-keys",
            value=open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()
        )]
    )
)

operation = instances_client.insert(
    project=project,
    zone=zone,
    instance_resource=instance
)

# Wait for operation to finish
while not operation.done():
    time.sleep(2)
    operation = instances_client.wait(project=project, zone=zone, operation=operation.name)

print("Launched GCP preemptible VM")
```

---

## 4. Oracle Cloud Infrastructure (OCI)

### 4.1 CLI – `oci`

```bash
# Spot instance (VM.Standard.E2.1.Micro, Ubuntu 26.04)
oci compute instance launch \
  --availability-domain <AD> \
  --compartment-id <COMPARTMENT_OCID> \
  --shape VM.Standard.E2.1.Micro \
  --display-name spot-oci \
  --source-details '{"sourceType":"image","imageId":"<UBUNTU_IMAGE_OCID>"}' \
  --metadata '{"ssh_authorized_keys":"'"$(cat ~/.ssh/id_rsa.pub)"'"}' \
  --capacity-reservation-type SPOT \
  --capacity-reservation-max-price 0.0030    # optional ceiling price (USD/hour)
```

*Key flags*

* `--capacity-reservation-type SPOT` – requests spot capacity.  
* `--capacity-reservation-max-price` – optional max price (omit to accept current market price).  

### 4.2 Libcloud (Python)

```python
import yaml
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["oci"]

Driver = get_driver(Provider.OCI)
driver = Driver(
    tenant=cfg["tenancy"],
    user=cfg["user"],
    fingerprint=cfg["fingerprint"],
    key_file=cfg["key_file"],
    region=cfg["region"]
)

# OCI image for Ubuntu 26.04 (replace with a real OCID)
image = driver.get_image("<UBUNTU_IMAGE_OCID>")

size = next(s for s in driver.list_sizes() if s.id == "VM.Standard.E2.1.Micro")

node = driver.create_node(
    name="spot-oci-libcloud",
    size=size,
    image=image,
    ex_spot=True,                         # request spot capacity
    ex_spot_price="0.0030",               # optional max price
    ex_authorized_keys=open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()
)

print("OCI spot instance OCID:", node.id)
```

### 4.3 Native SDK – `oci`

```python
import yaml
import oci
import time

with open("clouds.yaml") as f:
    cfg = yaml.safe_load(f)["oci"]

config = oci.config.from_dict({
    "user": cfg["user"],
    "fingerprint": cfg["fingerprint"],
    "key_file": cfg["key_file"],
    "tenancy": cfg["tenancy"],
    "region": cfg["region"]
})

compute = oci.core.ComputeClient(config)

# Replace with an actual Ubuntu 26.04 image OCID in the chosen region
ubuntu_image_id = "<UBUNTU_IMAGE_OCID>"

launch_details = oci.core.models.LaunchInstanceDetails(
    compartment_id=cfg["tenancy"],
    display_name="spot-oci-sdk",
    shape="VM.Standard.E2.1.Micro",
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        image_id=ubuntu_image_id,
        source_type="image"
    ),
    create_vnic_details=oci.core.models.CreateVnicDetails(
        assign_public_ip=True,
        subnet_id="<SUBNET_OCID>"
    ),
    metadata={"ssh_authorized_keys": open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()},
    capacity_reservation_type="SPOT",                # request spot
    capacity_reservation_max_price=0.0030            # optional max price
)

response = compute.launch_instance(launch_details)
instance = response.data

# Wait until RUNNING
while True:
    inst = compute.get_instance(instance.id).data
    if inst.lifecycle_state == "RUNNING":
        break
    time.sleep(5)

print("OCI spot instance launched:", instance.id)
```

---

## 5. Consolidated `clouds.yaml`

The single YAML file below supplies credentials and a **common spot‑price block** for all four clouds. Use the same file for the Libcloud scripts and the native‑SDK examples (CLI tools read their own configuration files, so the YAML is only needed for the programmatic paths).

```yaml
aws:
  key: YOUR_AWS_ACCESS_KEY_ID
  secret: YOUR_AWS_SECRET_ACCESS_KEY
  region: us-east-1
  spot:
    max_price: ""          # empty = accept current market price (recommended)

azure:
  tenant_id: YOUR_AZURE_TENANT_ID
  client_id: YOUR_AZURE_CLIENT_ID
  client_secret: YOUR_AZURE_CLIENT_SECRET
  subscription_id: YOUR_AZURE_SUBSCRIPTION_ID
  location: eastus
  spot:
    max_price: -1          # -1 = accept current spot price

gcp:
  project_id: YOUR_GCP_PROJECT_ID
  service_account_key: /home/you/.config/gcloud/sa-key.json
  zone: us-central1-a
  spot:
    # GCP spot (preemptible) price is fixed; no parameter needed.
    # The block is kept for symmetry.
    enabled: true

oci:
  tenancy: ocid1.tenancy.oc1..YOUR_TENANCY_OCID
  user: ocid1.user.oc1..YOUR_USER_OCID
  fingerprint: 12:34:56:78:9a:bc:de:f0:12:34:56:78:9a:bc:de:f0
  key_file: /home/you/.oci/oci_api_key.pem
  region: us-ashburn-1
  spot:
    max_price: ""          # empty = accept current spot price
```

**Notes on the file**

* The *spot* block mirrors the parameters used by each provider’s SDK.  
* For AWS and OCI the empty string (`""`) tells the script to omit the `MaxPrice` field, which results in “pay the current spot price”.  
* Azure uses `-1` to indicate “no ceiling price”.  
* GCP does not require a price – the `enabled` flag is kept for readability.  

When writing Libcloud or native‑SDK scripts you can read `cfg["spot"]["max_price"]` and apply the appropriate option per provider (as shown in the code snippets).

---

## 6. Quick Reference Table – Spot Launch Commands

| Cloud | CLI command | Libcloud class | Native SDK entry point |
|-------|-------------|----------------|------------------------|
| AWS   | `aws ec2 run-instances … --instance-market-options MarketType=spot` | `Provider.EC2` – `ex_instance_market="spot"` | `client.run_instances(…, InstanceMarketOptions={…})` |
| Azure | `az vm create … --priority Spot --max-price -1` | `Provider.AZURE_ARM` – `ex_vm_priority="Spot"` | `compute_client.virtual_machines.begin_create_or_update(..., {"priority":"Spot", …})` |
| GCP   | `gcloud compute instances create … --preemptible` | `Provider.GCE` – `ex_preemptible=True` | `instance.scheduling.preemptible = True` |
| OCI   | `oci compute instance launch … --capacity-reservation-type SPOT` | `Provider.OCI` – `ex_spot=True` | `launch_details.capacity_reservation_type = "SPOT"` |

---

## 7. Best Practices for Spot Workloads

1. **Graceful shutdown** – poll the provider‑specific termination‑notice endpoint and checkpoint state.  
2. **Use persistent disks** – attach block storage that survives instance termination (EBS, Managed Disk, PD, OCI Block Volume).  
3. **Mix Spot with on‑demand** – in auto‑scaling groups configure a base of on‑demand capacity and an overflow of spot capacity to reduce cost while keeping a minimum guaranteed number of instances.  
4. **Monitor price fluctuations** – spot prices change frequently. Automate price checks (e.g., `aws ec2 describe-spot-price-history`, Azure `az vm list-skus`, GCP `gcloud compute prices list`) if you need to enforce a ceiling.  
5. **Region selection** – spot availability and price vary by region; test multiple regions if you have flexibility.  

---

### End of Document

All the examples above assume you have already created an SSH key pair (`~/.ssh/id_rsa` / `id_rsa.pub`) and have the appropriate networking resources (VPC, subnet, security groups) in place. Adjust IDs, names, and image OCIDs as required for your environment. The same `clouds.yaml` file can be reused across the Libcloud and native‑SDK scripts, giving a single source of truth for credentials and spot‑price preferences.