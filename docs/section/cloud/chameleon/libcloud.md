Apache Libcloud abstracts multiple cloud providers into a unified interface using its OPENSTACK compute driver.  Below is a complete Python script using Libcloud to instantiate an OpenStack connection and provision a virtual machine specifying an image, hardware size, network, security group, and SSH key pair.  Python Script (libcloud_create_vm.py)Pythonfrom libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

# 1. Initialize the OpenStack Driver
OpenStack = get_driver(Provider.OPENSTACK)

driver = OpenStack(
    key="your_username",
    secret="your_password",
    ex_force_auth_url="https://identity.cloud.example.com/v3",
    ex_force_auth_version="3.x_password",
    ex_tenant_name="your_project_name",
    ex_domain_name="Default",  # Required for Keystone v3
)

# 2. Fetch target Image and Size (Flavor)
image_id = "YOUR_IMAGE_UUID"
flavor_id = "YOUR_FLAVOR_UUID"

image = driver.get_image(image_id)
size = [s for s in driver.list_sizes() if s.id == flavor_id][0]

# 3. Define network, security group, and key pair names/IDs
network_id = "YOUR_NETWORK_UUID"
security_group_name = "default"
key_pair_name = "my-ssh-key"

print(f"Provisioning VM on OpenStack via Libcloud...")

# 4. Create the Node (VM)
node = driver.create_node(
    name="my-test-vm",
    image=image,
    size=size,
    ex_keyname=key_pair_name,
    ex_security_groups=[security_group_name],
    ex_networks=[network_id],
)

print(f"Success! Node {node.name} status: {node.extra.get('status')}")
print(f"IP Addresses assigned: {node.public_ips + node.private_ips}")
Key Considerations:Dependencies: Install Libcloud via pip install apache-libcloud.Authentication Versions: Ensure your ex_force_auth_version matches your OpenStack Keystone endpoint configuration (e.g., "3.x_password" for modern Identity v3 APIs vs "2.0_password" for older clouds).  