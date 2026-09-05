# Creating a VM with the OpenStack CLI

Below is a complete, step‑by‑step guide for provisioning a virtual machine with the
`openstack` command‑line client, including an example *rc* file, a full command
example, flag explanations, post‑creation steps, and troubleshooting tips.

---

## 1. Example OpenStack RC file

Save the following content as `myproject-openrc.sh` (or any name you prefer)
and keep it **private** – it contains your authentication credentials.

```bash
# ----------------------------------------------------------------------
# OpenStack RC file for the project "myproject"
# ----------------------------------------------------------------------
# Do NOT commit this file to a public repository.
# Restrict permissions: chmod 600 myproject-openrc.sh
# ----------------------------------------------------------------------
export OS_AUTH_URL="https://identity.cloud.example.com/v3"
export OS_PROJECT_ID="1234567890abcdef1234567890abcdef"
export OS_PROJECT_NAME="myproject"
export OS_USER_DOMAIN_NAME="Default"
export OS_USERNAME="myuser"
export OS_PASSWORD="my_secret_password"
export OS_REGION_NAME="RegionOne"
export OS_INTERFACE="public"
export OS_IDENTITY_API_VERSION="3"
```

Load the file in your shell before using any OpenStack commands:

```bash
source myproject-openrc.sh
```
!!! note 
    After sourcing the file the CLI is authenticated and the correct project is selected automatically.

---

## 2. Prerequisites

| Item | How to obtain / install |
|------|-------------------------|
| OpenStack CLI (`openstack`) | `pipx install python-openstackclient`  *(or the distro package)* |
| Registered SSH key pair | `openstack keypair list` (create one with `openstack keypair create …`) |
| Required resources (flavor, image, security group, network) | Use the `openstack … list` commands shown in the table below |

---

## 3. Command syntax

```bash
openstack server create \
  --flavor <flavor> \
  --image <image> \
  --key-name <keypair> \
  --security-group <sec‑group> \
  --nic net-id=<network-id-or-name> \
  <instance-name>
```

### 3.1 Example command

```bash
openstack server create \
  --flavor m1.small \
  --image CC-Ubuntu-22.04 \
  --key-name my-ssh-key \
  --security-group my-security-group \
  --nic net-id=6d4e1f2b-3c9a-4a83-9f2b-8d5e6f7a9b0c \
  my-test-vm
```

---

## 4. Flag breakdown

| Flag | Description | How to discover the value |
|------|-------------|---------------------------|
| `--flavor <flavor>` | Hardware profile (vCPU, RAM, disk). | `openstack flavor list` |
| `--image <image>` | OS image or appliance to boot from. | `openstack image list` |
| `--key-name <keypair>` | Name of the SSH key pair injected into the instance. | `openstack keypair list` |
| `--security-group <sec‑group>` | Firewall rules applied to the instance (can be repeated). | `openstack security group list` |
| `--nic net-id=<network-id-or-name>` | Connects the VM to a specific private or shared network. Accepts either the network’s UUID or its name. | `openstack network list` |
| `<instance-name>` | Desired name for the new VM (no spaces). | Any alphanumeric string you choose. |

---

## 5. Common post‑creation steps

1. **Allocate a floating IP (if external access is required)**  

   ```bash
   # Create a floating IP on the public network
   FLOATING_IP=$(openstack floating ip create public -f value -c floating_ip_address)

   # Associate it with the instance
   openstack server add floating ip my-test-vm $FLOATING_IP
   ```

2. **Verify the instance status**  

   ```bash
   openstack server show my-test-vm
   ```

3. **Connect via SSH**  

   ```bash
   ssh -i ~/.ssh/my-ssh-key.pem ubuntu@$FLOATING_IP
   ```

---

## 6. Troubleshooting tips

| Symptom | Possible cause | Remedy |
|---------|----------------|--------|
| Instance remains in `BUILD` | Insufficient quota or the chosen flavor is unavailable. | Check quotas with `openstack quota show` and list available flavors. |
| SSH connection refused | No floating IP attached, or the security group blocks port 22. | Allocate a floating IP (see §5.1) and ensure the security group allows inbound TCP 22. |
| “No matching image” error | Image name/ID typo or image not visible to the project. | Verify the image name/ID using `openstack image list`. |
| “Invalid network” error | Wrong network name/UUID, or the network is not shared with the project. | List networks with `openstack network list` and confirm you have access. |
| “Invalid password” after sourcing rc file | Typo in `OS_PASSWORD` or the RC file was not sourced. | Re‑source the file and double‑check the password value. |

---

## 7. References

- OpenStack CLI documentation – <https://docs.openstack.org/python-openstackclient/latest/>
- Managing key pairs – <https://docs.openstack.org/nova/latest/user/keypairs.html>
- Security groups guide – <https://docs.openstack.org/neutron/latest/admin/security-groups.html>
- Network concepts – <https://docs.openstack.org/neutron/latest/admin/networks.html>
