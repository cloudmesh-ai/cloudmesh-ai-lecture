# Libcloud and OpenStack

Apache Libcloud abstracts multiple cloud providers into a unified interface. Here we show how to use its **OPENSTACK** compute driver.

Below is a complete Python script (`libcloud_create_vm.py`) that:

1. Instantiates an OpenStack connection.  
2. Fetches the desired image and flavor.  
3. Specifies the network, security group, and SSH key pair.  
4. Provisions a virtual machine.

---  

## Python script (`libcloud_create_vm.py`)


The script reads connection parameters from environment variables,
accepts image/flavor/network identifiers as command‑line arguments,
and logs progress using the standard logging facility.

```python
"""Create an OpenStack VM using Apache Libcloud."""

import os
import sys
import logging
import argparse
from typing import List

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider
from libcloud.compute.base import Node, NodeSize, NodeImage

# ----------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)

def build_driver() -> "OpenStackNodeDriver":
    """Instantiate the OpenStack driver using environment variables."""
    driver_cls = get_driver(Provider.OPENSTACK)
    return driver_cls(
        key=os.getenv("OS_USERNAME"),
        secret=os.getenv("OS_PASSWORD"),
        ex_force_auth_url=os.getenv("OS_AUTH_URL"),
        ex_force_auth_version=os.getenv("OS_AUTH_VERSION", "3.x_password"),
        ex_tenant_name=os.getenv("OS_PROJECT_NAME"),
        ex_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
    )

def resolve_image(driver, image_id: str) -> NodeImage:
    img = driver.get_image(image_id)
    if img is None:
        raise ValueError(f"Image with ID '{image_id}' not found.")
    return img

def resolve_size(driver, flavor_id: str) -> NodeSize:
    try:
        return next(s for s in driver.list_sizes() if s.id == flavor_id)
    except StopIteration:
        raise ValueError(f"Flavor with ID '{flavor_id}' not found.")

def create_node(
    driver,
    name: str,
    image: NodeImage,
    size: NodeSize,
    network_ids: List[str],
    security_groups: List[str],
    key_name: str,
) -> Node:
    """Create a VM and return the resulting Node object."""
    return driver.create_node(
        name=name,
        image=image,
        size=size,
        ex_keyname=key_name,
        ex_security_groups=security_groups,
        ex_networks=network_ids,
    )

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provision an OpenStack VM via Libcloud."
    )
    parser.add_argument("--name", required=True, help="Name of the new VM.")
    parser.add_argument("--image-id", required=True, help="UUID of the image to use.")
    parser.add_argument("--flavor-id", required=True, help="UUID of the flavor to use.")
    parser.add_argument(
        "--network-id",
        required=True,
        action="append",
        help="UUID of a network to attach (repeatable).",
    )
    parser.add_argument(
        "--security-group",
        default="default",
        action="append",
        help="Name of a security group to attach (default: %(default)s).",
    )
    parser.add_argument("--key-name", required=True, help="Name of the SSH key pair.")
    args = parser.parse_args()

    driver = build_driver()

    try:
        img = resolve_image(driver, args.image_id)
        sz = resolve_size(driver, args.flavor_id)

        log.info("Provisioning VM '%s'...", args.name)
        node = create_node(
            driver,
            name=args.name,
            image=img,
            size=sz,
            network_ids=args.network_id,
            security_groups=args.security_group,
            key_name=args.key_name,
        )
    except Exception as exc:   # pragma: no cover
        log.error("Failed to create VM: %s", exc)
        sys.exit(1)

    log.info("Success! Node %s status: %s", node.name, node.extra.get("status"))
    ip_list = ", ".join(node.public_ips + node.private_ips)
    log.info("IP addresses assigned: %s", ip_list)


if __name__ == "__main__":
    main()
```

---  

## Key considerations

- **Dependencies**  

  ```bash
  pip install "apache-libcloud>=3.6.0,<4.0"
  ```

- **Authentication version**  

  - Use `ex_force_auth_version="3.x_password"` for modern OpenStack clouds that expose Keystone **v3** APIs.  
  - For older clouds, switch to `"2.0_password"` (or another appropriate version) and adjust the authentication URL accordingly.

- **Naming / IDs**  

  - Replace the placeholders (`OS_USERNAME`, `OS_PASSWORD`, `OS_AUTH_URL`, etc.) with real values in your environment variables.  
  - Replace the command‑line arguments (`--image-id`, `--flavor-id`, `--network-id`, etc.) with the actual UUIDs from your OpenStack project.  
  - Ensure the security group and SSH key pair already exist in the project, or create them beforehand via the OpenStack dashboard or CLI.

- **Network handling**  

  - `ex_networks` expects a list of **network UUIDs**. To attach several networks, repeat the `--network-id` argument.

- **Error handling (optional)**  

  The script already wraps the creation call in a `try/except` block and logs any exception before exiting.

---  

## Usage example

```bash
export OS_USERNAME="my_user"
export OS_PASSWORD="my_secret"
export OS_AUTH_URL="https://identity.cloud.example.com/v3"
export OS_PROJECT_NAME="my_project"
export OS_USER_DOMAIN_NAME="Default"

python libcloud_create_vm.py \
    --name my-test-vm \
    --image-id a1b2c3d4-5678-90ab-cdef-1234567890ab \
    --flavor-id 1234abcd-12ab-34cd-56ef-1234567890ab \
    --network-id 9876fedc-54ba-32dc-10fe-0987654321ab \
    --security-group default \
    --key-name my-ssh-key
```

The script will log progress, report success, and display the assigned public and private IP addresses.  

---  

**Example 2 – Read OpenStack credentials from a *.env* file**

The script below is the same as the first example, but the OpenStack credentials are loaded from a file called **`.env`** instead of being exported in the shell.  
It uses the **`python‑dotenv`** package, which reads “KEY=VALUE” pairs and injects them into `os.environ` at runtime.

---

### 1. Create the *.env* file

Save the file in the same directory as `libcloud_create_vm.py` (or give the full path to it).

```text
# .env – keep this file private, never commit it to a public repository
OS_USERNAME=my_user
OS_PASSWORD=my_secret_password
OS_AUTH_URL=https://identity.cloud.example.com/v3
OS_PROJECT_NAME=my_project
OS_USER_DOMAIN_NAME=Default
```

> **Security note** – Restrict the file permissions so that only the owner can read it:  
> ```bash
> chmod 600 .env
> ```

---

### 2. Install the extra dependency

```bash
pip install "python-dotenv>=1.0"
```

---

### 3. Updated script (`libcloud_create_vm.py`)

```python
"""Create an OpenStack VM using Apache Libcloud.

Credentials are read from a .env file (via python‑dotenv) and environment
variables, allowing you to keep secrets out of the source code.
"""

import os
import sys
import logging
import argparse
from typing import List

# Load variables from .env (if present) before any other imports that may use them
from dotenv import load_dotenv
load_dotenv()                        # defaults to a file named ".env" in CWD

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider
from libcloud.compute.base import Node, NodeSize, NodeImage

# ----------------------------------------------------------------------
# Logging configuration
# ----------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)


def build_driver() -> "OpenStackNodeDriver":
    """Instantiate the OpenStack driver using environment variables loaded from .env."""
    driver_cls = get_driver(Provider.OPENSTACK)
    return driver_cls(
        key=os.getenv("OS_USERNAME"),
        secret=os.getenv("OS_PASSWORD"),
        ex_force_auth_url=os.getenv("OS_AUTH_URL"),
        ex_force_auth_version=os.getenv("OS_AUTH_VERSION", "3.x_password"),
        ex_tenant_name=os.getenv("OS_PROJECT_NAME"),
        ex_domain_name=os.getenv("OS_USER_DOMAIN_NAME", "Default"),
    )


def resolve_image(driver, image_id: str) -> NodeImage:
    img = driver.get_image(image_id)
    if img is None:
        raise ValueError(f"Image with ID '{image_id}' not found.")
    return img


def resolve_size(driver, flavor_id: str) -> NodeSize:
    try:
        return next(s for s in driver.list_sizes() if s.id == flavor_id)
    except StopIteration:
        raise ValueError(f"Flavor with ID '{flavor_id}' not found.")


def create_node(
    driver,
    name: str,
    image: NodeImage,
    size: NodeSize,
    network_ids: List[str],
    security_groups: List[str],
    key_name: str,
) -> Node:
    """Create a VM and return the resulting Node object."""
    return driver.create_node(
        name=name,
        image=image,
        size=size,
        ex_keyname=key_name,
        ex_security_groups=security_groups,
        ex_networks=network_ids,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provision an OpenStack VM via Libcloud (credentials from .env)."
    )
    parser.add_argument("--name", required=True, help="Name of the new VM.")
    parser.add_argument("--image-id", required=True, help="UUID of the image to use.")
    parser.add_argument("--flavor-id", required=True, help="UUID of the flavor to use.")
    parser.add_argument(
        "--network-id",
        required=True,
        action="append",
        help="UUID of a network to attach (repeatable).",
    )
    parser.add_argument(
        "--security-group",
        default="default",
        action="append",
        help="Name of a security group to attach (default: %(default)s).",
    )
    parser.add_argument("--key-name", required=True, help="Name of the SSH key pair.")
    args = parser.parse_args()

    driver = build_driver()

    try:
        img = resolve_image(driver, args.image_id)
        sz = resolve_size(driver, args.flavor_id)

        log.info("Provisioning VM '%s'...", args.name)
        node = create_node(
            driver,
            name=args.name,
            image=img,
            size=sz,
            network_ids=args.network_id,
            security_groups=args.security_group,
            key_name=args.key_name,
        )
    except Exception as exc:   # pragma: no cover
        log.error("Failed to create VM: %s", exc)
        sys.exit(1)

    log.info(
        "Success! Node %s status: %s",
        node.name,
        node.extra.get("status", "unknown"),
    )
    ip_list = ", ".join(node.public_ips + node.private_ips)
    log.info("IP addresses assigned: %s", ip_list)


if __name__ == "__main__":
    main()
```

---

### 4. Run the script

```bash
python libcloud_create_vm.py \
    --name my-test-vm \
    --image-id a1b2c3d4-5678-90ab-cdef-1234567890ab \
    --flavor-id 1234abcd-12ab-34cd-56ef-1234567890ab \
    --network-id 9876fedc-54ba-32dc-10fe-0987654321ab \
    --security-group default \
    --key-name my-ssh-key
```

The script will:

1. Load the OpenStack credentials from `.env`.  
2. Connect to the cloud using Libcloud.  
3. Resolve the supplied image and flavor IDs.  
4. Create the VM with the requested network, security group, and SSH key.  
5. Log the result, including the assigned public and private IP addresses.

---

### 5. Why this approach is useful

* **Separation of secrets from code** – The password never appears in the source file or in command‑line history.  
* **Version‑control safety** – `.env` can be listed in `.gitignore`, preventing accidental commits of credentials.  
* **Portability** – The same script works in CI pipelines where environment variables are injected, or locally where a developer prefers a `.env` file.

---

*Last updated: 2026‑08‑28 (v1.4‑example‑2)*