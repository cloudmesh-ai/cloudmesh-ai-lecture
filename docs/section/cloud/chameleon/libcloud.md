# Libcloud and OpenStack  

Apache Libcloud abstracts multiple cloud providers into a unified interface using its **OPENSTACK** compute driver.  
Below is a complete Python script (`libcloud_create_vm.py`) that:

1. Instantiates an OpenStack connection.  
2. Fetches the desired image and flavor.  
3. Specifies the network, security group, and SSH key pair.  
4. Provisions a virtual machine.

---

### Python script (`libcloud_create_vm.py`)

```python
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider

# ----------------------------------------------------------------------
# 1. Initialize the OpenStack driver
# ----------------------------------------------------------------------
OpenStack = get_driver(Provider.OPENSTACK)
driver = OpenStack(
    key="your_username",
    secret="your_password",
    ex_force_auth_url="https://identity.cloud.example.com/v3",
    ex_force_auth_version="3.x_password",   # Keystone v3 (password auth)
    ex_tenant_name="your_project_name",
    ex_domain_name="Default",                # Required for Keystone v3
)

# ----------------------------------------------------------------------
# 2. Fetch target image and size (flavor)
# ----------------------------------------------------------------------
image_id = "YOUR_IMAGE_UUID"
flavor_id = "YOUR_FLAVOR_UUID"

image = driver.get_image(image_id)

# Find the flavor that matches the UUID
size = next(s for s in driver.list_sizes() if s.id == flavor_id)

# ----------------------------------------------------------------------
# 3. Define network, security group, and key‑pair
# ----------------------------------------------------------------------
network_id = "YOUR_NETWORK_UUID"
security_group_name = "default"
key_pair_name = "my-ssh-key"

print("Provisioning VM on OpenStack via Libcloud...")

# ----------------------------------------------------------------------
# 4. Create the node (VM)
# ----------------------------------------------------------------------
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
```

---

### Key considerations  

- **Dependencies**  
  ```bash
  pip install apache-libcloud
  ```

- **Authentication version**  
  - Use `ex_force_auth_version="3.x_password"` for modern OpenStack clouds that expose Keystone **v3** APIs.  
  - For older clouds, switch to `"2.0_password"` (or another appropriate version) and adjust the auth URL accordingly.

- **Naming / IDs**  
  - Replace placeholders (`YOUR_IMAGE_UUID`, `YOUR_FLAVOR_UUID`, `YOUR_NETWORK_UUID`, etc.) with the actual IDs from your OpenStack project.  
  - Ensure the security group and SSH key pair already exist in the project, or create them beforehand via the OpenStack dashboard / CLI.

- **Network handling**  
  - `ex_networks` expects a list of **network UUIDs**. If you need to attach several networks, simply add more IDs to the list.

- **Error handling (optional)**  
  ```python
  try:
      node = driver.create_node(...)
  except Exception as exc:
      print(f"Failed to create VM: {exc}")
  ```

Feel free to copy the script, replace the placeholders with your environment’s values, and run it to spin up a VM on OpenStack via Libcloud!