## Learning Objectives

!!! info "Learning Objectives"
    * Install the Google Cloud Python client libraries in an isolated environment.
    * Configure credentials using a `clouds.yaml` file.
    * Develop a helper module to abstract low-level Compute Engine API calls.
    * Implement a Python script to provision an e2-micro VM.
    * Retrieve the public IPv4 address of the provisioned instance.
    * Clean up all created resources to avoid costs.

    ## Overview

    This chapter demonstrates how to automate the provisioning of a Google Cloud Platform (GCP) virtual machine using the official Python SDK (`google-cloud-compute`). This approach provides a programmatic alternative to using the `gcloud` CLI or the Cloud Console, enabling the creation of reproducible infrastructure as code.

    ## Core Sections

    ### Installing the SDK

    To avoid dependency conflicts on the host system, the SDK should be installed in an isolated environment.

    #### Docker Wrapper (Complete Isolation)

    The following method uses a Docker container to run the Python script, mounting the necessary configuration and SSH directories.

    ```bash
    docker pull python:3.12-slim

    cat <<'EOF' > ~/bin/gcloudsdk
    #!/usr/bin/env bash
    docker run --rm -it \
      -v "$HOME/.config/gcloud:/root/.config/gcloud:rw" \
      -v "$HOME/.ssh:/root/.ssh:ro" \
      -v "$(pwd):/workdir" \
      -w /workdir \
      python:3.12-slim \
      bash -c "pip install --quiet google-cloud-compute google-auth PyYAML && python3 \"\$@\"" \
      "$@"
    EOF
    chmod +x ~/bin/gcloudsdk
    export PATH=$HOME/bin:$PATH
    ```

    Running `gcloudsdk myscript.py` installs the required libraries inside the container and executes the script.

    #### Native Virtual Environment

    For a local installation using a virtual environment:

    ```bash
    python3 -m venv .gcloud-venv
    source .gcloud-venv/bin/activate
    pip install --upgrade pip
    pip install google-cloud-compute google-auth PyYAML
    ```

    #### pipx Sandbox

    For an isolated application-level installation:

    ```bash
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    pipx install google-cloud-compute
    pipx install google-auth
    pipx install PyYAML
    ```

    ### Configuration with clouds.yaml

    To keep credentials separate from the code, use a `clouds.yaml` file.

    ```yaml
    google:
      project_id: YOUR_GCP_PROJECT_ID
      service_account_key: /home/you/.config/gcloud/sa-key.json
      zone: us-central1-a
    ```

    A service account with the **Compute Admin** role is required. Download the JSON key file and provide its absolute path in the `service_account_key` field.

    ### Building the Helper Module

    The `gcp_helpers.py` module abstracts the complexity of the `google-cloud-compute` library, providing simple functions for resource management.

    ```python
    # gcp_helpers.py
    import os
    import time
    import yaml
    from google.oauth2 import service_account
    from google.cloud import compute_v1

    def load_config(path="clouds.yaml"):
    """Read clouds.yaml and return the google dict."""
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg["google"]

    def get_client(cfg):
    """Return a dictionary of Compute Engine service clients."""
    credentials = service_account.Credentials.from_service_account_file(
        cfg["service_account_key"]
    )
    project = cfg["project_id"]
    return {
        "project": project,
        "zone": cfg["zone"],
        "instances": compute_v1.InstancesClient(credentials=credentials),
        "networks": compute_v1.NetworksClient(credentials=credentials),
        "subnetworks": compute_v1.SubnetworksClient(credentials=credentials),
        "firewalls": compute_v1.FirewallsClient(credentials=credentials),
        "addresses": compute_v1.AddressesClient(credentials=credentials),
        "operations": compute_v1.ZoneOperationsClient(credentials=credentials),
    }

    def wait_for_operation(client, operation, project, zone, timeout=300, interval=5):
    """Poll a zone-level operation until it reaches DONE."""
    elapsed = 0
    while elapsed < timeout:
        result = client.get(project=project, zone=zone, operation=operation.name)
        if result.status == compute_v1.Operation.Status.DONE:
            if result.error:
                raise RuntimeError(f"Operation {operation.name} failed: {result.error}")
            return
        time.sleep(interval)
        elapsed += interval
    raise RuntimeError(f"Operation {operation.name} did not complete within {timeout}s")

    def ensure_vpc_network(networks_client, project, network_name):
    """Create a VPC network (auto-mode disabled) if it does not exist."""
    try:
        networks_client.get(project=project, network=network_name)
    except Exception:
        operation = networks_client.insert(
            project=project,
            network_resource=compute_v1.Network(name=network_name, auto_create_subnetworks=False),
        )
        operation.result()
    return f"projects/{project}/global/networks/{network_name}"

    def ensure_subnet(subnetworks_client, project, region, network_url,
                  subnet_name, ip_cidr_range="10.0.0.0/24"):
    """Create a subnet inside the given VPC if it does not exist."""
    try:
        subnetworks_client.get(project=project, region=region, subnetwork=subnet_name)
    except Exception:
        subnet = compute_v1.Subnetwork(
            name=subnet_name,
            ip_cidr_range=ip_cidr_range,
            network=network_url,
        )
        operation = subnetworks_client.insert(project=project, region=region, subnetwork_resource=subnet)
        operation.result()
    return f"projects/{project}/regions/{region}/subnetworks/{subnet_name}"

    def ensure_firewall(firewalls_client, project, network_name, fw_name):
    """Create a firewall rule that allows inbound SSH (tcp:22) from any source."""
    try:
        firewalls_client.get(project=project, firewall=fw_name)
    except Exception:
        firewall = compute_v1.Firewall(
            name=fw_name,
            network=f"projects/{project}/global/networks/{network_name}",
            allowed=[compute_v1.Allowed(ip_protocol="tcp", ports=["22"])],
            direction=compute_v1.Firewall.Direction.INGRESS,
            source_ranges=["0.0.0.0/0"],
        )
        firewalls_client.insert(project=project, firewall_resource=firewall).result()

    def ensure_static_address(addresses_client, project, region, address_name):
    """Reserve a static external IPv4 address."""
    try:
        addr = addresses_client.get(project=project, region=region, address=address_name)
    except Exception:
        address = compute_v1.Address(name=address_name, address_type=compute_v1.Address.AddressType.EXTERNAL)
        operation = addresses_client.insert(project=project, region=region, address_resource=address)
        operation.result()
        addr = addresses_client.get(project=project, region=region, address=address_name)
    return addr.self_link

    def create_instance(instances_client, project, zone, name, machine_type,
                    source_image_family, network_interface, ssh_key):
    """Launch an e2-micro instance using the provided network interface and SSH public key."""
    machine_type_url = f"zones/{zone}/machineTypes/{machine_type}"
    image_client = compute_v1.ImagesClient()
    image = image_client.get_from_family(project="ubuntu-os-cloud", family=source_image_family)

    metadata_item = compute_v1.Metadata.ItemsValueListEntry(
        key="ssh-keys",
        value=f"ubuntu:{ssh_key}"
    )
    metadata = compute_v1.Metadata(items=[metadata_item])

    instance = compute_v1.Instance(
        name=name,
        machine_type=machine_type_url,
        disks=[
            compute_v1.AttachedDisk(
                boot=True,
                auto_delete=True,
                initialize_params=compute_v1.AttachedDiskInitializeParams(
                    source_image=image.self_link,
                ),
            )
        ],
        network_interfaces=[network_interface],
        metadata=metadata,
        labels={"libcloud-demo": "true"},
    )
    operation = instances_client.insert(project=project, zone=zone, instance_resource=instance)
    operation.result()

    def get_instance_external_ip(instances_client, project, zone, name):
    """Return the external IPv4 address of the instance."""
    instance = instances_client.get(project=project, zone=zone, instance=name)
    for iface in instance.network_interfaces:
        if iface.access_configs:
            return iface.access_configs[0].nat_i_p
    raise RuntimeError(f"No external IP found on instance {name}")

    def delete_instance(instances_client, project, zone, name):
    """Stop and delete the instance."""
    try:
        instances_client.delete(project=project, zone=zone, instance=name).result()
    except Exception as e:
        print(f"Warning: could not delete instance {name}: {e}")

    def delete_network_resources(clients, project, region, network_name, subnet_name,
                            address_name, firewall_name):
    """Delete network components in the correct order."""
    try:
        clients["firewalls"].delete(project=project, firewall=firewall_name).result()
    except Exception:
        pass
    try:
        clients["addresses"].delete(project=project, region=region, address=address_name).result()
    except Exception:
        pass
    try:
        clients["subnetworks"].delete(project=project, region=region, subnetwork=subnet_name).result()
    except Exception:
        pass
    try:
        clients["networks"].delete(project=project, network=network_name).result()
    except Exception:
        pass
    ```

    ### Implementing the Main Script

    The `run_gcp_free_vm.py` script orchestrates the creation of networking resources and the VM instance.

    ```python
    #!/usr/bin/env python3
    # run_gcp_free_vm.py
    import os
    import sys
    from gcp_helpers import (
    load_config,
    get_client,
    ensure_vpc_network,
    ensure_subnet,
    ensure_firewall,
    ensure_static_address,
    create_instance,
    get_instance_external_ip,
    delete_instance,
    delete_network_resources,
    )

    cfg = load_config()
    clients = get_client(cfg)

    PROJECT = clients["project"]
    ZONE    = clients["zone"]
    REGION  = ZONE.rsplit("-", 1)[0]

    NETWORK_NAME = "libcloud-gcp-free-net"
    SUBNET_NAME  = "libcloud-gcp-free-sub"
    FIREWALL_NAME = "libcloud-gcp-free-fw"
    ADDRESS_NAME = "libcloud-gcp-free-ip"
    INSTANCE_NAME = "libcloud-gcp-free-vm"
    MACHINE_TYPE  = "e2-micro"
    IMAGE_FAMILY  = "ubuntu-2204-lts"
    SSH_KEY_PATH  = os.path.expanduser("~/.ssh/libcloud_gcp_key.pub")

    if not os.path.isfile(SSH_KEY_PATH):
    raise FileNotFoundError(f"Public SSH key not found: {SSH_KEY_PATH}")
    with open(SSH_KEY_PATH, "r") as f:
    ssh_key_data = f.read().strip()

    network_url = ensure_vpc_network(clients["networks"], PROJECT, NETWORK_NAME)
    subnet_url  = ensure_subnet(clients["subnetworks"], PROJECT, REGION,
                            network_url, SUBNET_NAME)
    ensure_firewall(clients["firewalls"], PROJECT, NETWORK_NAME, FIREWALL_NAME)
    static_ip_selflink = ensure_static_address(clients["addresses"], PROJECT,
                                           REGION, ADDRESS_NAME)

    from google.cloud import compute_v1
    network_interface = compute_v1.NetworkInterface(
    name="nic0",
    subnetwork=subnet_url,
    access_configs=[
        compute_v1.AccessConfig(
            name="External NAT",
            nat_i_p=static_ip_selflink,
            type_=compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT,
        )
    ],
    )

    create_instance(
    instances_client=clients["instances"],
    project=PROJECT,
    zone=ZONE,
    name=INSTANCE_NAME,
    machine_type=MACHINE_TYPE,
    source_image_family=IMAGE_FAMILY,
    network_interface=network_interface,
    ssh_key=ssh_key_data,
    )

    public_ip = get_instance_external_ip(clients["instances"], PROJECT, ZONE, INSTANCE_NAME)
    print("\n=== GCP free instance ready ===")
    print(f"Public IP: {public_ip}")
    print("\nSSH command:")
    print(f"ssh -i ~/.ssh/libcloud_gcp_key ubuntu@{public_ip}")

    if "--destroy" in sys.argv:
    print("\nCleaning up resources ...")
    delete_instance(clients["instances"], PROJECT, ZONE, INSTANCE_NAME)
    delete_network_resources(
        clients,
        project=PROJECT,
        region=REGION,
        network_name=NETWORK_NAME,
        subnet_name=SUBNET_NAME,
        address_name=ADDRESS_NAME,
        firewall_name=FIREWALL_NAME,
    )
    try:
        os.remove(os.path.expanduser("~/.ssh/libcloud_gcp_key"))
    except OSError:
        pass
    print("All GCP resources removed.")
    ```

    #### Execution and Usage

    To run the script using the Docker wrapper:

    ```bash
    gcloudsdk run_gcp_free_vm.py          # creates the VM
    gcloudsdk run_gcp_free_vm.py --destroy   # removes resources
    ```

    ### Internal Workflow Analysis

    The script executes the following sequence:

    1. **Configuration**: Reads project ID and service account details from `clouds.yaml`.
    2. **Authentication**: Establishes a session using `service_account.Credentials`.
    3. **Networking**: Creates a VPC network, a /24 subnet, a static external IPv4 address, and a firewall rule allowing TCP port 22.
    4. **Provisioning**: Launches an `e2-micro` instance based on Ubuntu 22.04 LTS and injects the public SSH key.
    5. **Output**: Fetches the public IP and prints the SSH command.
    6. **Cleanup**: If the `--destroy` flag is passed, it removes the instance and network components in reverse order.

    ### Obtaining Credentials

    To configure `clouds.yaml`, you must create a service account:

    1. Create the account:
       ```bash
       gcloud iam service-accounts create libcloud-gcp-sa --display-name "Libcloud demo service account"
       ```
    2. Grant the **Compute Admin** role:
       ```bash
       gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID \
       --member="serviceAccount:libcloud-gcp-sa@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/compute.admin"
       ```
    3. Download the JSON key:
       ```bash
       gcloud iam service-accounts keys create ~/config/sa-key.json \
       --iam-account libcloud-gcp-sa@YOUR_GCP_PROJECT_ID.iam.gserviceaccount.com
       ```

    ### Troubleshooting and Pitfalls

    * **Zone Mismatch**: `e2-micro` is only free in specific zones (e.g., `us-central1-a`). Using other zones will result in an `INVALID_ARGUMENT` error.
    * **Static IP Collisions**: If an address with the chosen name already exists and is attached to another resource, VM creation will fail.
    * **Quota Limits**: The free tier allows only one `e2-micro` VM per region. Stop existing instances before re-running the script.
    * **Credential Access**: Ensure the JSON key file is readable by the user executing the script to avoid `DefaultCredentialsError`.

    ### Single-File Implementation

    For simplicity, the following script combines the helper functions and the main workflow into one file (`gcp_free_vm_onefile.py`).

    ```python
    #!/usr/bin/env python3
    import os, sys, time, yaml
    from google.oauth2 import service_account
    from google.cloud import compute_v1

    def load_cfg():
    with open("clouds.yaml") as f:
        return yaml.safe_load(f)["google"]

    cfg = load_cfg()
    credentials = service_account.Credentials.from_service_account_file(
    cfg["service_account_key"]
    )
    PROJECT = cfg["project_id"]
    ZONE    = cfg["zone"]
    REGION  = ZONE.rsplit("-", 1)[0]

    instances  = compute_v1.InstancesClient(credentials=credentials)
    networks  = compute_v1.NetworksClient(credentials=credentials)
    subnetworks = compute_v1.SubnetworksClient(credentials=credentials)
    firewalls = compute_v1.FirewallsClient(credentials=credentials)
    addresses = compute_v1.AddressesClient(credentials=credentials)

    def wait_op(op):
    while op.status != compute_v1.Operation.Status.DONE:
        time.sleep(3)
        op = compute_v1.ZoneOperationsClient(credentials=credentials).get(
            project=PROJECT, zone=ZONE, operation=op.name
        )
    if op.error:
        raise RuntimeError(op.error)

    def ensure_network(name):
    try:
        networks.get(project=PROJECT, network=name)
    except Exception:
        op = networks.insert(
            project=PROJECT,
            network_resource=compute_v1.Network(name=name, auto_create_subnetworks=False),
        )
        wait_op(op)
    return f"projects/{PROJECT}/global/networks/{name}"

    def ensure_subnet(name, net_url):
    try:
        subnetworks.get(project=PROJECT, region=REGION, subnetwork=name)
    except Exception:
        sub = compute_v1.Subnetwork(
            name=name,
            ip_cidr_range="10.0.0.0/24",
            network=net_url,
        )
        op = subnetworks.insert(project=PROJECT, region=REGION, subnetwork_resource=sub)
        wait_op(op)

    def ensure_firewall(name, net_name):
    try:
        firewalls.get(project=PROJECT, firewall=name)
    except Exception:
        fw = compute_v1.Firewall(
            name=name,
            network=f"projects/{PROJECT}/global/networks/{net_name}",
            allowed=[compute_v1.Allowed(ip_protocol="tcp", ports=["22"])],
            direction=compute_v1.Firewall.Direction.INGRESS,
            source_ranges=["0.0.0.0/0"],
        )
        firewalls.insert(project=PROJECT, firewall_resource=fw).result()

    def ensure_address(name):
    try:
        addr = addresses.get(project=PROJECT, region=REGION, address=name)
    except Exception:
        a = compute_v1.Address(name=name, address_type=compute_v1.Address.AddressType.EXTERNAL)
        op = addresses.insert(project=PROJECT, region=REGION, address_resource=a)
        wait_op(op)
        addr = addresses.get(project=PROJECT, region=REGION, address=name)
    return addr.self_link

    def create_vm(name, machine_type, img_family, nic, ssh_key):
    mt_url = f"zones/{ZONE}/machineTypes/{machine_type}"
    img_client = compute_v1.ImagesClient()
    img = img_client.get_from_family(project="ubuntu-os-cloud", family=img_family)

    metadata = compute_v1.Metadata(
        items=[compute_v1.Metadata.ItemsValueListEntry(
            key="ssh-keys",
            value=f"ubuntu:{ssh_key}"
        )]
    )

    instance = compute_v1.Instance(
        name=name,
        machine_type=mt_url,
        disks=[compute_v1.AttachedDisk(
            boot=True,
            auto_delete=True,
            initialize_params=compute_v1.AttachedDiskInitializeParams(source_image=img.self_link)
        )],
        network_interfaces=[nic],
        metadata=metadata,
        labels={"libcloud-demo": "true"},
    )
    op = instances.insert(project=PROJECT, zone=ZONE, instance_resource=instance)
    wait_op(op)

    def get_ip(name):
    i = instances.get(project=PROJECT, zone=ZONE, instance=name)
    for iface in i.network_interfaces:
        if iface.access_configs:
            return iface.access_configs[0].nat_i_p
    raise RuntimeError("No external IP")

    def delete_vm(name):
    try:
        op = instances.delete(project=PROJECT, zone=ZONE, instance=name)
        wait_op(op)
    except Exception:
        pass

    def delete_networks(net, sub, fw, addr):
    for f in [(firewalls, fw), (addresses, addr), (subnetworks, sub), (networks, net)]:
        try:
            client, name = f
            client.delete(project=PROJECT, **({"region": REGION, "subnetwork": name}
                if client is subnetworks else
                {"global": True, "network": name} if client is networks else
                {"global": True, "firewall": name} if client is firewalls else
                {"region": REGION, "address": name}))
        except Exception:
            pass

    NETWORK_NAME   = "gcp-free-net"
    SUBNET_NAME    = "gcp-free-sub"
    FIREWALL_NAME  = "gcp-free-fw"
    ADDRESS_NAME   = "gcp-free-ip"
    VM_NAME        = "gcp-free-vm"
    MACHINE_TYPE   = "e2-micro"
    IMAGE_FAMILY   = "ubuntu-2204-lts"
    SSH_KEY_PATH   = os.path.expanduser("~/.ssh/libcloud_gcp_key.pub")

    if not os.path.isfile(SSH_KEY_PATH):
    raise FileNotFoundError(SSH_KEY_PATH)
    with open(SSH_KEY_PATH) as f:
    ssh_key = f.read().strip()

    net_url = ensure_network(NETWORK_NAME)
    ensure_subnet(SUBNET_NAME, net_url)
    ensure_firewall(FIREWALL_NAME, NETWORK_NAME)
    addr_url = ensure_address(ADDRESS_NAME)

    nic = compute_v1.NetworkInterface(
    name="nic0",
    subnetwork=f"projects/{PROJECT}/regions/{REGION}/subnetworks/{SUBNET_NAME}",
    access_configs=[compute_v1.AccessConfig(
        name="External NAT",
        nat_i_p=addr_url,
        type_=compute_v1.AccessConfig.Type.ONE_TO_ONE_NAT,
    )],
    )

    create_vm(VM_NAME, MACHINE_TYPE, IMAGE_FAMILY, nic, ssh_key)
    public_ip = get_ip(VM_NAME)

    print("\n=== GCP free VM ready ===")
    print(f"Public IP: {public_ip}")
    print("\nSSH command:")
    print(f"ssh -i ~/.ssh/libcloud_gcp_key ubuntu@{public_ip}")

    if "--destroy" in sys.argv:
    print("\nCleaning up ...")
    delete_vm(VM_NAME)
    delete_networks(NETWORK_NAME, SUBNET_NAME, FIREWALL_NAME, ADDRESS_NAME)
    try:
        os.remove(os.path.expanduser("~/.ssh/libcloud_gcp_key"))
    except OSError:
        pass
    print("All resources removed.")
    ```

    ## Summary Checklist

    - [ ] Python SDK installed in an isolated environment.
    - [ ] Service account created with **Compute Admin** role.
    - [ ] `clouds.yaml` configured with project ID, zone, and JSON key path.
    - [ ] `gcp_helpers.py` and `run_gcp_free_vm.py` implemented.
    - [ ] Public SSH key generated and available at `~/.ssh/libcloud_gcp_key.pub`.
    - [ ] VPC network, subnet, and firewall rule provisioned.
    - [ ] e2-micro VM launched and external IP retrieved.
    - [ ] Successful SSH connection established.
    - [ ] Resources deleted using the `--destroy` flag.

    ## Assignments

!!! note "Assignment.1: SDK Isolation"
    Set up the Google Cloud SDK using the Docker wrapper method. Verify the setup by running a simple Python script that imports `google.cloud.compute_v1`.

!!! note "Assignment.2: Automated Provisioning"
    Execute `run_gcp_free_vm.py` to deploy a free-tier instance. Verify that the VM is running in the `us-central1-a` zone.

??? tip "Solution: Assignment.2"
    Run `gcloudsdk run_gcp_free_vm.py`. Check the GCP Console under Compute Engine > VM Instances to verify the zone and machine type.

!!! note "Assignment.3: Resource Lifecycle"
    Run the cleanup process using the `--destroy` flag and verify in the Cloud Console that the VPC and VM have been removed.

??? tip "Solution: Assignment.3"
    Run `gcloudsdk run_gcp_free_vm.py --destroy`.

    ## References

    | Resource | Description |
    |----------|-------------|
    | Google Cloud Python client libraries | <https://cloud.google.com/python/docs/reference> |
    | Compute Engine API reference (v1) | <https://cloud.google.com/compute/docs/reference/rest/v1> |
    | Free-tier overview (e2-micro) | <https://cloud.google.com/free> |
    | Service-account creation & IAM roles | <https://cloud.google.com/iam/docs/creating-managing-service-accounts> |
    | gcloud command-line reference | <https://cloud.google.com/sdk/gcloud> |

    ## Self-Evaluation

??? note "What is the primary advantage of using the Python SDK over the gcloud CLI for VM provisioning?"
    The Python SDK allows for deeper integration into application logic and enables the creation of complex, conditional infrastructure workflows that are harder to maintain in shell scripts.

??? note "Which role is minimum required for a service account to manage Compute Engine resources?"
    The `roles/compute.admin` role provides the necessary permissions to create, modify, and delete compute instances and network resources.

??? note "Why is the order of deletion critical when cleaning up network resources?"
    Network resources have dependencies. For example, a VPC network cannot be deleted until all its subnets and firewall rules have been removed.
