## Learning Objectives

!!! info "Learning Objectives"
    * Install the Oracle Cloud Infrastructure (OCI) Python SDK in an isolated environment.
    * Configure authentication using a `clouds.yaml` file and OCI API keys.
    * Develop a helper module to abstract OCI networking and compute API calls.
    * Implement a Python script to provision an Always-Free compute instance.
    * Retrieve the public IPv4 address of the provisioned instance.
    * Clean up all created resources to avoid potential charges.

## Overview

This chapter demonstrates how to automate the provisioning of an Oracle Cloud Infrastructure (OCI) virtual machine using the official OCI Python SDK (`oci`). This programmatic approach enables the creation of reproducible infrastructure and integrates directly with Python-based orchestration workflows.

## Core Sections

### Installing the OCI SDK

To avoid dependency conflicts, the OCI SDK should be installed in an isolated environment.

#### Docker Wrapper (Complete Isolation)

This method runs the SDK inside a container, mounting the OCI configuration and SSH directories.

```bash
docker pull python:3.12-slim

cat <<'EOF' > ~/bin/oci_python
#!/usr/bin/env bash
docker run --rm -it \
    -v "$HOME/.oci:/root/.oci:rw" \
    -v "$HOME/.ssh:/root/.ssh:ro" \
    -v "$(pwd):/workdir" \
    -w /workdir \
    python:3.12-slim \
    bash -c "pip install --quiet oci PyYAML && python3 \"\$@\"" \
    "$@"
EOF
chmod +x ~/bin/oci_python
export PATH=$HOME/bin:$PATH
```

Running `oci_python script.py` installs the SDK inside the container and executes the script.

#### Native Virtual Environment

For a local installation using a virtual environment:

```bash
python3 -m venv .oci-venv
source .oci-venv/bin/activate
pip install --upgrade pip
pip install oci PyYAML
```

#### pipx Sandbox

For an isolated application-level installation:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install oci
pipx install PyYAML
```

### Configuration with clouds.yaml

OCI requires specific identity markers (OCIDs) and an API key for authentication. These are stored in a `clouds.yaml` file.

```yaml
oci:
    tenancy: ocid1.tenancy.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    user: ocid1.user.oc1..bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    fingerprint: 12:34:56:78:9a:bc:de:f0:12:34:56:78:9a:bc:de:f0
    key_file: /home/you/.oci/oci_api_key.pem
    region: us-ashburn-1
```

To obtain these values:
1. Create a user in the OCI console under **Identity** $\rightarrow$ **Users**.
2. Generate an API key pair. Upload the public key and save the **fingerprint**.
3. Download the private key as a PEM file.
4. Retrieve the **Tenancy OCID** and **User OCID** from their respective detail pages.

### Building the Helper Module

The `oci_helpers.py` module provides high-level functions to manage VCNs, subnets, and compute instances, reducing the boilerplate required by the OCI SDK.

```python
# oci_helpers.py
import time
import yaml
import oci
from oci.core.models import (CreateVcnDetails, CreateSubnetDetails,
                            CreateInternetGatewayDetails,
                            CreateRouteTableDetails, RouteRule,
                            CreateSecurityListDetails, SecurityRule,
                            CreatePublicIpDetails,
                            CreateNetworkSecurityGroupDetails,
                            CreateNetworkSecurityGroupSecurityRuleDetails,
                            CreateVnicDetails, LaunchInstanceDetails)

def load_config(path="clouds.yaml"):
"""Read clouds.yaml and return the OCI dictionary."""
with open(path, "r") as f:
    cfg = yaml.safe_load(f)
return cfg["oci"]

def make_config_dict(cfg):
"""Transform the yaml dict into the form expected by oci.config.from_dict."""
return {
    "user": cfg["user"],
    "fingerprint": cfg["fingerprint"],
    "key_file": cfg["key_file"],
    "tenancy": cfg["tenancy"],
    "region": cfg["region"],
}

def get_clients(cfg):
"""Return a dict with the three core service clients (VCN, Compute, Network)."""
config = oci.config.from_dict(make_config_dict(cfg))
compute_client = oci.core.ComputeClient(config)
vcn_client     = oci.core.VirtualNetworkClient(config)
return {"config": config, "compute": compute_client, "vcn": vcn_client}

def ensure_vcn(vcn_client, compartment_id, display_name, cidr, dns_label):
"""Create a VCN if it does not exist, otherwise return its OCID."""
vcn_list = vcn_client.list_vcns(compartment_id).data
for v in vcn_list:
    if v.display_name == display_name:
        return v.id
vcn_details = CreateVcnDetails(
    cidr_block=cidr,
    display_name=display_name,
    dns_label=dns_label,
)
vcn = vcn_client.create_vcn(compartment_id, vcn_details).data
oci.wait_until(vcn_client, vcn_client.get_vcn(vcn.id), "lifecycle_state", "AVAILABLE")
return vcn.id

def ensure_subnet(vcn_client, compartment_id, vcn_id, display_name,
                cidr, dns_label, route_table_id=None):
"""Create a subnet (or return the existing one)."""
subnets = vcn_client.list_subnets(compartment_id, vcn_id).data
for s in subnets:
    if s.display_name == display_name:
        return s.id
subnet_details = CreateSubnetDetails(
    cidr_block=cidr,
    display_name=display_name,
    dns_label=dns_label,
    route_table_id=route_table_id,
    vcn_id=vcn_id,
)
subnet = vcn_client.create_subnet(compartment_id, subnet_details).data
oci.wait_until(vcn_client, vcn_client.get_subnet(subnet.id), "lifecycle_state", "AVAILABLE")
return subnet.id

def ensure_internet_gateway(vcn_client, compartment_id, vcn_id, display_name):
igws = vcn_client.list_internet_gateways(compartment_id, vcn_id).data
for igw in igws:
    if igw.display_name == display_name:
        return igw.id
igw_details = CreateInternetGatewayDetails(
    is_enabled=True,
    display_name=display_name,
)
igw = vcn_client.create_internet_gateway(compartment_id, vcn_id, igw_details).data
oci.wait_until(vcn_client, vcn_client.get_internet_gateway(igw.id), "lifecycle_state", "AVAILABLE")
return igw.id

def ensure_route_table(vcn_client, compartment_id, vcn_id, display_name, igw_id):
rts = vcn_client.list_route_tables(compartment_id, vcn_id).data
for rt in rts:
    if rt.display_name == display_name:
        return rt.id
rt_details = CreateRouteTableDetails(
    display_name=display_name,
    route_rules=[
        RouteRule(
            cidr_block="0.0.0.0/0",
            network_entity_id=igw_id,
        )
    ],
)
rt = vcn_client.create_route_table(compartment_id, vcn_id, rt_details).data
oci.wait_until(vcn_client, vcn_client.get_route_table(rt.id), "lifecycle_state", "AVAILABLE")
return rt.id

def ensure_security_list(vcn_client, compartment_id, vcn_id, display_name, cidr):
"""Create a security list that allows inbound SSH (TCP 22) from anywhere."""
sls = vcn_client.list_security_lists(compartment_id, vcn_id).data
for sl in sls:
    if sl.display_name == display_name:
        return sl.id
sl_details = CreateSecurityListDetails(
    display_name=display_name,
    egress_security_rules=[
        SecurityRule(
            destination="0.0.0.0/0",
            protocol="6",
            is_stateless=False,
            tcp_options=oci.core.models.TcpOptions(destination_port_range=oci.core.models.PortRange(min=1, max=65535)),
        )
    ],
    ingress_security_rules=[
        SecurityRule(
            source="0.0.0.0/0",
            protocol="6",
            is_stateless=False,
            tcp_options=oci.core.models.TcpOptions(source_port_range=oci.core.models.PortRange(min=22, max=22),
                                                    destination_port_range=oci.core.models.PortRange(min=22, max=22)),
        )
    ],
    vcn_id=vcn_id,
)
sl = vcn_client.create_security_list(compartment_id, vcn_id, sl_details).data
oci.wait_until(vcn_client, vcn_client.get_security_list(sl.id), "lifecycle_state", "AVAILABLE")
return sl.id

def launch_instance(compute_client, compartment_id, display_name,
                shape, subnet_id, ssh_public_key, availability_domain=None):
"""Launch a free-tier VM with the provided SSH key."""
# Placeholder image OCID - replace with actual regional Ubuntu image OCID
image_id = "ocid1.image.oc1..aaaaaaaaxxxxxxxxxyyyyyyyyyzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"

launch_details = LaunchInstanceDetails(
    availability_domain=availability_domain,
    compartment_id=compartment_id,
    shape=shape,
    display_name=display_name,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        image_id=image_id,
        source_type="image",
    ),
    create_vnic_details=CreateVnicDetails(
        subnet_id=subnet_id,
        assign_public_ip=True,
        display_name=f"{display_name}-vnic",
        hostname_label=display_name.replace("_", "-"),
        skip_source_dest_check=False,
    ),
    metadata={
        "ssh_authorized_keys": ssh_public_key,
    },
)
resp = compute_client.launch_instance(launch_details)
instance = resp.data
oci.wait_until(compute_client, compute_client.get_instance(instance.id), "lifecycle_state", "RUNNING")
return instance.id

def get_instance_public_ip(compute_client, instance_id):
"""Return the public IP address attached to the instance."""
details = compute_client.get_instance(instance_id).data
for vnic in details.vnics:
    vnic_details = compute_client.get_vnic(vnic.id).data
    if vnic_details.public_ip:
        return vnic_details.public_ip
raise RuntimeError("Public IP not found for instance")

def terminate_instance(compute_client, instance_id):
"""Terminate (delete) the instance."""
compute_client.terminate_instance(instance_id)
oci.wait_until(compute_client, compute_client.get_instance(instance_id), "lifecycle_state", "TERMINATED", succeed_on_not_found=True)

def delete_vcn(vcn_client, compartment_id, vcn_id):
"""Delete the VCN and its dependent resources."""
vcn_client.delete_vcn(vcn_id)
while True:
    try:
        vcn_client.get_vcn(vcn_id)
        time.sleep(5)
    except oci.exceptions.ServiceError as e:
        if e.status == 404:
            break
        raise
```

### Implementing the Main Script

The `run_oci_free_vm.py` script integrates the helper functions to provision the full environment.

```python
#!/usr/bin/env python3
# run_oci_free_vm.py
import os
import sys
import time
from oci_helpers import (
load_config,
get_clients,
ensure_vcn,
ensure_subnet,
ensure_internet_gateway,
ensure_route_table,
ensure_security_list,
launch_instance,
get_instance_public_ip,
terminate_instance,
delete_vcn,
)

cfg = load_config()
clients = get_clients(cfg)

compute = clients["compute"]
vcn     = clients["vcn"]
compartment_id = cfg["tenancy"]

VCN_NAME        = "libcloud-oci-free-vcn"
SUBNET_NAME     = "libcloud-oci-free-subnet"
IGW_NAME        = "libcloud-oci-free-igw"
RT_NAME         = "libcloud-oci-free-rt"
SL_NAME         = "libcloud-oci-free-sl"
INSTANCE_NAME   = "libcloud-oci-free-vm"
SHAPE           = "VM.Standard.E2.1.Micro"
CIDR_BLOCK      = "10.0.0.0/16"
SUBNET_CIDR     = "10.0.0.0/24"
DNS_LABEL_VCN   = "libcloudvcn"
DNS_LABEL_SUB   = "libcloudsub"
SSH_KEY_PATH    = os.path.expanduser("~/.ssh/libcloud_oci_key.pub")

if not os.path.isfile(SSH_KEY_PATH):
raise FileNotFoundError(f"Public SSH key not found: {SSH_KEY_PATH}")
with open(SSH_KEY_PATH, "r") as f:
ssh_pub_key = f.read().strip()

vcn_id = ensure_vcn(
vcn_client=vcn,
compartment_id=compartment_id,
display_name=VCN_NAME,
cidr=CIDR_BLOCK,
dns_label=DNS_LABEL_VCN,
)

igw_id = ensure_internet_gateway(
vcn_client=vcn,
compartment_id=compartment_id,
vcn_id=vcn_id,
display_name=IGW_NAME,
)

rt_id = ensure_route_table(
vcn_client=vcn,
compartment_id=compartment_id,
vcn_id=vcn_id,
display_name=RT_NAME,
igw_id=igw_id,
)

sl_id = ensure_security_list(
vcn_client=vcn,
compartment_id=compartment_id,
vcn_id=vcn_id,
display_name=SL_NAME,
cidr=SUBNET_CIDR,
)

subnet_id = ensure_subnet(
vcn_client=vcn,
compartment_id=compartment_id,
vcn_id=vcn_id,
display_name=SUBNET_NAME,
cidr=SUBNET_CIDR,
dns_label=DNS_LABEL_SUB,
route_table_id=rt_id,
)

instance_id = launch_instance(
compute_client=compute,
compartment_id=compartment_id,
display_name=INSTANCE_NAME,
shape=SHAPE,
subnet_id=subnet_id,
ssh_public_key=ssh_pub_key,
)

public_ip = get_instance_public_ip(compute, instance_id)
print("\n=== OCI free-tier instance ready ===")
print(f"Public IP : {public_ip}")
print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_oci_key ubuntu@{public_ip}")

if "--destroy" in sys.argv:
print("\nCleaning up resources ...")
terminate_instance(compute, instance_id)
delete_vcn(vcn, compartment_id, vcn_id)
try:
    os.remove(os.path.expanduser("~/.ssh/libcloud_oci_key"))
except OSError:
    pass
print("All OCI resources removed.")
```

#### Execution and Usage

To run the script using the Docker wrapper:

```bash
oci_python run_oci_free_vm.py          # creates the VM
oci_python run_oci_free_vm.py --destroy   # removes resources
```

### Internal Workflow Analysis

The script follows a strict dependency chain for resource creation:

1. **Authentication**: Loads identity and key details from `clouds.yaml`.
2. **VCN Creation**: Establishes the Virtual Cloud Network.
3. **Internet Gateway**: Creates an IGW and attaches it to the VCN to allow external traffic.
4. **Routing**: Creates a route table directing all `0.0.0.0/0` traffic to the IGW.
5. **Security**: Creates a security list allowing TCP port 22.
6. **Subnetting**: Creates a subnet and associates it with the route table and security list.
7. **Compute**: Launches a `VM.Standard.E2.1.Micro` instance, assigning a public IP and injecting the SSH key.
8. **Verification**: Polls the instance state until `RUNNING` and fetches the public IP.

### Managing Image OCIDs

Unlike some providers, OCI image IDs (OCIDs) can vary by region. To obtain a valid Ubuntu 22.04 OCID, use the OCI CLI:

```bash
oci compute image list \
    --compartment-id <YOUR_TENANCY_OCID> \
    --operating-system Ubuntu \
    --operating-system-version "22.04" \
    --query "data[?\"display-name\" && contains(\"display-name\", `Ubuntu-22.04`)].id | [0]" \
    --output text
```

### Troubleshooting and Pitfalls

* **Region Mismatch**: The free-tier shape `VM.Standard.E2.1.Micro` is only available in specific regions (e.g., `us-ashburn-1`, `us-phx-1`).
* **Quota Limits**: OCI allows only one always-free instance per tenancy. Existing instances must be terminated before re-running.
* **Public IP Propagation**: The public IP may take a few seconds to appear after the instance reaches the `RUNNING` state.
* **Image OCID Validity**: Using a placeholder or an incorrect OCID will result in a `BadRequest` error.

### Single-File Implementation

The following script combines the helper functions and the main workflow into one file (`oci_free_vm_onefile.py`).

```python
#!/usr/bin/env python3
import os, sys, time, yaml, oci
from oci.core.models import (CreateVcnDetails, CreateSubnetDetails,
                            CreateInternetGatewayDetails, CreateRouteTableDetails,
                            RouteRule, CreateSecurityListDetails, SecurityRule,
                            LaunchInstanceDetails, CreateVnicDetails)

def load_cfg():
with open("clouds.yaml") as f:
    return yaml.safe_load(f)["oci"]

cfg = load_cfg()
config = oci.config.from_dict({
"user": cfg["user"],
"fingerprint": cfg["fingerprint"],
"key_file": cfg["key_file"],
"tenancy": cfg["tenancy"],
"region": cfg["region"],
})

compute = oci.core.ComputeClient(config)
vcn     = oci.core.VirtualNetworkClient(config)
comp_id = cfg["tenancy"]

def wait_until(fn, attr, value, timeout=300, interval=5):
elapsed = 0
while elapsed < timeout:
    res = fn()
    if getattr(res, attr) == value:
        return res
    time.sleep(interval)
    elapsed += interval
raise RuntimeError(f"Timeout waiting for {attr} == {value}")

def ensure_vcn(name, cidr, dns_label):
for v in vcn.list_vcns(comp_id).data:
    if v.display_name == name:
        return v.id
spec = CreateVcnDetails(cidr_block=cidr, display_name=name, dns_label=dns_label)
v = vcn.create_vcn(comp_id, spec).data
wait_until(lambda: vcn.get_vcn(v.id).data, "lifecycle_state", "AVAILABLE")
return v.id

def ensure_subnet(vcn_id, name, cidr, dns_label, rt_id=None):
for s in vcn.list_subnets(comp_id, vcn_id).data:
    if s.display_name == name:
        return s.id
spec = CreateSubnetDetails(cidr_block=cidr, display_name=name,
                            dns_label=dns_label, route_table_id=rt_id, vcn_id=vcn_id)
s = vcn.create_subnet(comp_id, spec).data
wait_until(lambda: vcn.get_subnet(s.id).data, "lifecycle_state", "AVAILABLE")
return s.id

def ensure_igw(vcn_id, name):
for i in vcn.list_internet_gateways(comp_id, vcn_id).data:
    if i.display_name == name:
        return i.id
spec = CreateInternetGatewayDetails(is_enabled=True, display_name=name)
i = vcn.create_internet_gateway(comp_id, vcn_id, spec).data
wait_until(lambda: vcn.get_internet_gateway(i.id).data, "lifecycle_state", "AVAILABLE")
return i.id

def ensure_rt(vcn_id, name, igw_id):
for r in vcn.list_route_tables(comp_id, vcn_id).data:
    if r.display_name == name:
        return r.id
spec = CreateRouteTableDetails(display_name=name,
                                route_rules=[RouteRule(cidr_block="0.0.0.0/0",
                                                        network_entity_id=igw_id)])
r = vcn.create_route_table(comp_id, vcn_id, spec).data
wait_until(lambda: vcn.get_route_table(r.id).data, "lifecycle_state", "AVAILABLE")
return r.id

def ensure_sl(vcn_id, name):
for s in vcn.list_security_lists(comp_id, vcn_id).data:
    if s.display_name == name:
        return s.id
sl = CreateSecurityListDetails(
    display_name=name,
    egress_security_rules=[
        SecurityRule(protocol="6",
                        tcp_options=oci.core.models.TcpOptions(destination_port_range=oci.core.models.PortRange(min=1, max=65535)),
                        destination="0.0.0.0/0")
    ],
    ingress_security_rules=[
        SecurityRule(protocol="6",
                        tcp_options=oci.core.models.TcpOptions(destination_port_range=oci.core.models.PortRange(min=22, max=22)),
                        source="0.0.0.0/0")
    ],
    vcn_id=vcn_id,
)
s = vcn.create_security_list(comp_id, vcn_id, sl).data
wait_until(lambda: vcn.get_security_list(s.id).data, "lifecycle_state", "AVAILABLE")
return s.id

def launch_vm(name, shape, subnet_id, ssh_key, image_ocid):
launch = LaunchInstanceDetails(
    compartment_id=comp_id,
    display_name=name,
    shape=shape,
    source_details=oci.core.models.InstanceSourceViaImageDetails(
        image_id=image_ocid,
        source_type="image"
    ),
    create_vnic_details=CreateVnicDetails(
        subnet_id=subnet_id,
        assign_public_ip=True,
        display_name=f"{name}-vnic"
    ),
    metadata={"ssh_authorized_keys": ssh_key}
)
resp = compute.launch_instance(launch)
instance = resp.data
wait_until(lambda: compute.get_instance(instance.id).data,
            "lifecycle_state", "RUNNING")
return instance.id

def get_public_ip(instance_id):
inst = compute.get_instance(instance_id).data
for vnic in inst.vnics:
    vnic_det = compute.get_vnic(vnic.id).data
    if vnic_det.public_ip:
        return vnic_det.public_ip
raise RuntimeError("Public IP not found")

def terminate_instance(instance_id):
compute.terminate_instance(instance_id)
wait_until(lambda: compute.get_instance(instance_id).data,
            "lifecycle_state", "TERMINATED", succeed_on_not_found=True)

def delete_vcn(vcn_id):
vcn.delete_vcn(vcn_id)
while True:
    try:
        vcn.get_vcn(vcn_id)
        time.sleep(5)
    except oci.exceptions.ServiceError as e:
        if e.status == 404:
            break
        raise

VCN_NAME      = "oci-free-vcn"
SUBNET_NAME   = "oci-free-subnet"
IGW_NAME      = "oci-free-igw"
RT_NAME       = "oci-free-rt"
SL_NAME       = "oci-free-sl"
INSTANCE_NAME = "oci-free-vm"
SHAPE         = "VM.Standard.E2.1.Micro"
CIDR_VCN      = "10.0.0.0/16"
CIDR_SUBNET   = "10.0.0.0/24"
DNS_LABEL_VCN = "ocifreevcn"
DNS_LABEL_SUB = "ocifreesub"
SSH_KEY_PATH  = os.path.expanduser("~/.ssh/libcloud_oci_key.pub")

if not os.path.isfile(SSH_KEY_PATH):
raise FileNotFoundError(f"SSH public key missing: {SSH_KEY_PATH}")
with open(SSH_KEY_PATH) as f:
ssh_pub = f.read().strip()

vcn_id = ensure_vcn(VCN_NAME, CIDR_VCN, DNS_LABEL_VCN)
igw_id = ensure_igw(vcn_id, IGW_NAME)
rt_id  = ensure_rt(vcn_id, RT_NAME, igw_id)
sl_id  = ensure_sl(vcn_id, SL_NAME)
subnet_id = ensure_subnet(vcn_id, SUBNET_NAME, CIDR_SUBNET, DNS_LABEL_SUB, rt_id)

# Replace with a valid regional OCID
UBUNTU_IMAGE_OCID = "ocid1.image.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
instance_id = launch_vm(INSTANCE_NAME, SHAPE, subnet_id, ssh_pub, UBUNTU_IMAGE_OCID)
public_ip = get_public_ip(instance_id)

print("\n=== OCI free-tier instance ready ===")
print(f"Public IP : {public_ip}")
print("\nSSH command:")
print(f"ssh -i ~/.ssh/libcloud_oci_key ubuntu@{public_ip}")

if "--destroy" in sys.argv:
print("\nCleaning up ...")
terminate_instance(instance_id)
delete_vcn(vcn_id)
try:
    os.remove(os.path.expanduser("~/.ssh/libcloud_oci_key"))
except OSError:
    pass
print("All resources removed.")
```

## Summary Checklist

- [ ] OCI Python SDK installed in an isolated environment.
- [ ] API key pair generated and registered in the OCI Console.
- [ ] `clouds.yaml` configured with tenancy, user OCIDs, and fingerprint.
- [ ] `oci_helpers.py` and `run_oci_free_vm.py` implemented.
- [ ] Public SSH key available at `~/.ssh/libcloud_oci_key.pub`.
- [ ] VCN, Subnet, Internet Gateway, and Route Table provisioned.
- [ ] VM.Standard.E2.1.Micro instance launched.
- [ ] Successful SSH connection established using the public IP.
- [ ] Resources removed using the `--destroy` flag.

## Assignments

!!! note "Assignment.1: SDK Isolation"
    Set up the OCI SDK using the Docker wrapper method. Verify the setup by running a Python script that imports the `oci` module.

!!! note "Assignment.2: Automated Provisioning"
    Execute `run_oci_free_vm.py` to deploy a free-tier instance. Verify that the instance is in the `RUNNING` state.

    ??? tip "Solution: Assignment.2"
        Run `oci_python run_oci_free_vm.py`. Check the OCI Console under Compute > Instances to verify the status and shape.

!!! note "Assignment.3: Resource Cleanup"
    Run the cleanup process using the `--destroy` flag and verify that the VCN and instance have been removed.

    ??? tip "Solution: Assignment.3"
        Run `oci_python run_oci_free_vm.py --destroy`.

## References

| Resource | Description |
|----------|-------------|
| OCI Python SDK documentation | <https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/> |
| OCI Always-Free tier details | <https://www.oracle.com/cloud/free/> |
| Compute shapes (Free-tier) | <https://docs.oracle.com/en-us/iaas/Content/Compute/References/computeshapes.htm> |
| Service-principal and API keys | <https://docs.oracle.com/en-us/iaas/Content/Identity/Tasks/managingcredentials.htm> |
| OCI CLI reference | <https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm> |

## Self-Evaluation

??? note "What is the purpose of the Internet Gateway and Route Table in an OCI VCN?"
    The Internet Gateway provides a path for network traffic between the VCN and the internet. The Route Table defines the routing rules, such as directing all outbound traffic (`0.0.0.0/0`) to the Internet Gateway.

??? note "Why must the user provide a specific Image OCID when launching an instance?"
    OCI images are region-specific. An OCID for an Ubuntu image in one region will not work in another, requiring the user to retrieve the correct ID for their chosen region.

??? note "What happens if a user tries to launch a second Always-Free instance?"
    OCI typically allows only one Always-Free compute instance per tenancy for certain shapes. Attempting to launch another will result in an `InstanceLimitExceeded` or quota-exceeded error.
