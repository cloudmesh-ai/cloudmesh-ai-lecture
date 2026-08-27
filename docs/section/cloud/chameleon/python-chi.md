
# Launch a KVM@TACC Virtual Machine with the **python‑chi** Library  

If you prefer scripting over the Horizon web UI, the same workflow can be performed from Python.  
The example below shows how to:

* select a project and the KVM@TACC site  
* choose (or create) an SSH key pair and a private network  
* create a virtual‑machine (server) instance  
* attach a floating (public) IP  
* print an SSH command you can use to connect  

It also includes a complete guide to **managing the credentials** required by the Chameleon SDK.

---  

## Step 1 – Initialise the library and choose a context  

```python
# Standard imports from the python‑chi SDK
import chi
from chi import lease, server, network, context

# ----------------------------------------------------------------------
# Choose the project you want to bill to.
# Replace the placeholder with the actual name or ID of your project.
# ----------------------------------------------------------------------
PROJECT_NAME = "my-project"          # <-- replace with your project

context.choose_project(PROJECT_NAME)

# ----------------------------------------------------------------------
# Select the KVM@TACC site.
# ----------------------------------------------------------------------
context.choose_site("KVM@TACC")
```

---  

## Step 2 – Prepare the SSH key‑pair and private network  

```python
# ----------------------------------------------------------------------
# SSH key – the key must already be uploaded to the site.
# ----------------------------------------------------------------------
key_name = "my-ssh-key"               # <-- name of the uploaded public key

# ----------------------------------------------------------------------
# Private network – either reuse an existing one or create a new one.
# ----------------------------------------------------------------------
net_name = "sharednet1"               # <-- existing private network name

# If you need to create a new network, uncomment the following lines:
# net_name = network.create_network(
#     name="my-private-net",
#     router="external-router-id",   # replace with your router ID
#     is_shared=False
# )
```

---  

## Step 3 – (Optional) Create a lease and launch the VM  

> For most KVM VMs a lease is not required, but the call is shown for completeness.

```python
# ----------------------------------------------------------------------
# Server details – adjust the image and flavor to match your needs.
# ----------------------------------------------------------------------
server_name  = "my-kvm-vm"
image_name   = "CC-Ubuntu-22.04"   # change if you want a different image
flavor_name  = "m1.small"          # choose an appropriate size

# ----------------------------------------------------------------------
# Optional: create a lease if you need exclusive resources.
# ----------------------------------------------------------------------
# lease_id = lease.create_lease(
#     name="my-lease",
#     start="2024-09-01T00:00:00Z",
#     end="2024-09-07T00:00:00Z",
#     project=PROJECT_NAME,
# )
# print(f"Lease created: {lease_id}")

# ----------------------------------------------------------------------
# Launch the server instance
# ----------------------------------------------------------------------
instance = server.create_server(
    name=server_name,
    image=image_name,
    flavor=flavor_name,
    network=net_name,
    key_name=key_name,
    security_groups=["default"],   # add additional groups if required
    # lease_id=lease_id,           # uncomment if you created a lease
)

print(f"Server '{server_name}' is being launched (ID: {instance.id}) …")
```

---  

## Step 4 – Allocate a floating IP and attach it  

```python
# ----------------------------------------------------------------------
# Grab a floating IP from the external network (usually called "ext-net")
# ----------------------------------------------------------------------
floating_ip = network.create_floating_ip("ext-net")
network.associate_floating_ip(instance.id, floating_ip.ip)

print("\nFloating IP attached:")
print(f"    {floating_ip.ip}")

# ----------------------------------------------------------------------
# Show the SSH command you can use to connect
# ----------------------------------------------------------------------
ssh_command = f"ssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}"
print("\nConnect to your VM with:")
print(f"    {ssh_command}")
```

---  

## Managing Credentials for Accessing Chameleon from Python  

The **python‑chi** library (and the underlying OpenStack SDK) obtains authentication information from one of the following sources, in order:

1. Explicit arguments passed to the SDK  
2. Environment variables  
3. `~/.config/openstack/clouds.yaml` (or `~/.clouds.yaml`)  
4. `~/.netrc` (for password authentication)  
5. X.509 proxy (for VOMS‑authenticated users)  

Below are the most common approaches.

### 1. Use an X.509 proxy (default for many Chameleon users)

1. Obtain a proxy on a machine that has a valid X.509 certificate  

   ```bash
   voms-proxy-init --voms chameleon
   ```

2. Export the proxy location for the current shell (the SDK looks for `X509_USER_PROXY`)  

   ```bash
   export X509_USER_PROXY=$HOME/.globus/proxy
   ```

3. Run your Python script in the same environment; the SDK will automatically read the proxy and acquire a token.

### 2. Use password‑based OpenStack authentication  

Set the standard OpenStack environment variables before running Python:

```bash
export OS_AUTH_URL=https://keystone.tacc.chameleoncloud.org:5000/v3
export OS_USERNAME=your-username
export OS_PASSWORD=your-password
export OS_PROJECT_NAME=your-project
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_REGION_NAME=KVM@TACC
export OS_INTERFACE=public
export OS_IDENTITY_API_VERSION=3
```

If you prefer not to expose the password in the shell, place the variables in a file and source it only when needed:

```bash
# file: chameleon_env.sh
export OS_AUTH_URL=https://keystone.tacc.chameleoncloud.org:5000/v3
export OS_USERNAME=your-username
export OS_PASSWORD=your-password
export OS_PROJECT_NAME=your-project
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_DOMAIN_NAME=Default
export OS_REGION_NAME=KVM@TACC
export OS_INTERFACE=public
export OS_IDENTITY_API_VERSION=3
```

```bash
source chameleon_env.sh
python launch_vm.py
```

### 3. Use an OpenStack `clouds.yaml` file (recommended for reproducibility)

Create a `clouds.yaml` file (default locations are `~/.config/openstack/clouds.yaml` or `~/.clouds.yaml`):

```yaml
# ~/.config/openstack/clouds.yaml
clouds:
  chameleon:
    auth:
      auth_url: https://keystone.tacc.chameleoncloud.org:5000/v3
      username: your-username
      password: your-password
      project_name: your-project
      user_domain_name: Default
      project_domain_name: Default
    region_name: KVM@TACC
    interface: public
    identity_api_version: 3
```

Tell the SDK which cloud to use:

```python
import openstack

# The OpenStack SDK reads clouds.yaml automatically.
conn = openstack.connect(cloud="chameleon")

# If you need the raw token (for debugging):
token = conn.authorize()
print("Obtained token:", token)
```

When you use the `chi` library, it internally creates a temporary OpenStack connection using the same environment, so you do **not** need to pass the `conn` object explicitly. Just ensure the environment variables or `clouds.yaml` are in place before importing `chi`.

### 4. Programmatic authentication with the `chi` SDK  

If you want to supply credentials directly in code (e.g., for CI pipelines), you can use the `chi.auth` helper:

```python
from chi import auth, context

auth_params = {
    "auth_url": "https://keystone.tacc.chameleoncloud.org:5000/v3",
    "username": "your-username",
    "password": "your-password",
    "project_name": "your-project",
    "user_domain_name": "Default",
    "project_domain_name": "Default",
    "region_name": "KVM@TACC",
    "interface": "public",
    "identity_api_version": "3",
}

# Authenticate and store the token internally.
auth.authenticate(**auth_params)

# Continue with the normal workflow.
context.choose_project("your-project")
context.choose_site("KVM@TACC")
```

> **Security note** – Never hard‑code passwords or tokens in a script that is stored in a public repository. Use environment variables, a secrets manager, or a protected configuration file with restrictive permissions (`chmod 600`).

### 5. Storing credentials securely with `keyring` (optional)

```python
import keyring
from chi import auth, context

username = keyring.get_password("chameleon", "username")
password = keyring.get_password("chameleon", "password")
project  = keyring.get_password("chameleon", "project")

auth_params = {
    "auth_url": "https://keystone.tacc.chameleoncloud.org:5000/v3",
    "username": username,
    "password": password,
    "project_name": project,
    "user_domain_name": "Default",
    "project_domain_name": "Default",
    "region_name": "KVM@TACC",
    "interface": "public",
    "identity_api_version": "3",
}

auth.authenticate(**auth_params)

context.choose_project(project)
context.choose_site("KVM@TACC")
```

---  

## Quick copy‑paste version  

You can copy the four code blocks below into a single Python script (or a Jupyter notebook) and run them in order.

```markdown
### Step 1 – Choose project and site
```python
import chi
from chi import lease, server, network, context

PROJECT_NAME = "my-project"          # <-- replace
context.choose_project(PROJECT_NAME)
context.choose_site("KVM@TACC")
```

### Step 2 – SSH key and network
```python
key_name = "my-ssh-key"
net_name = "sharednet1"               # <-- existing private net
```

### Step 3 – (Optional) lease and launch VM
```python
server_name  = "my-kvm-vm"
image_name   = "CC-Ubuntu-22.04"
flavor_name  = "m1.small"

instance = server.create_server(
    name=server_name,
    image=image_name,
    flavor=flavor_name,
    network=net_name,
    key_name=key_name,
    security_groups=["default"],
)

print(f"Server '{server_name}' launching …")
```

### Step 4 – Floating IP
```python
floating_ip = network.create_floating_ip("ext-net")
network.associate_floating_ip(instance.id, floating_ip.ip)

print(f"ssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}")
```
```

---  

## Tips & Common Issues  

| Problem | Resolution |
|---------|------------|
| **SSH key not found** | Upload the public key via Horizon → *Compute → Key Pairs* or use `chi.keypair.upload()` before running the script. |
| **Network name not recognized** | List available networks with `network.list_networks()` and use one of the returned names. |
| **Requested flavor unavailable** | View available flavors using `server.list_flavors()` and select a valid one. |
| **No floating IPs left** | Ask site administrators for additional floating IPs or release any that are no longer needed. |
| **Authentication timeout** | Ensure you have a valid X.509 proxy (`export X509_USER_PROXY=~/.globus/...`) or a current password‑based token before importing `chi`. |
| **Credential leakage** | Prefer environment variables, `clouds.yaml`, or a secrets manager over hard‑coding passwords in source files. |

---  

With the steps above you can provision and access a KVM virtual machine on TACC entirely programmatically, and you have several secure options for handling the required credentials. Happy scripting!