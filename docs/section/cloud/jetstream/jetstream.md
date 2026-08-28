# Jetstream2 Cloud Guide

Jetstream2 provides as one of its services a cloud computing environment offering zero-cost, always-on infrastructure to researchers and educators through the ACCESS ecosystem located at <https://access-ci.org/>.

## 1. Getting an Account (Allocation)

To use Jetstream2, you must first obtain an allocation through the 

* [ACCESS Login](https://cilogon.org/authorize?client_id=cilogon:/client_id/2839765bdb5cabfdae0daa43a6614b13&scope=email%20openid%20profile%20org.cilogon.userinfo&redirect_uri=https://access-ci.org&response_type=code&state=asdfghjklkjhgfdsa)

portal.

For detailed instructions on how to apply for an allocation and how to manage users within an existing allocation, please refer to the [ACCESS CI Guide](access-ci.md).

## 2. Using Cloud Resources via GUI

Jetstream2 provides multiple graphical user interfaces depending on your needs:

### Exosphere

!!! warning
    we do not recommend or using Exosphere for this class. No assignment should be using Exosphere. 

Exosphere is a streamlined, simplified interface designed for the most common tasks.

- **Best for:** Quickly launching instances, basic management, and users who want a simpler experience.
- **Workflow:** Log in $\rightarrow$ Click "Create Instance" $\rightarrow$ Select 
Image/Flavor $\rightarrow$ Launch.
- **Not for:** This class.

### Horizon

The documentation for jetstream for horizon is provided at 

* <https://docs.jetstream-cloud.org/ui/horizon/intro/>

Horizon is the standard OpenStack dashboard and provides complete control over the cloud environment.


- **Best for:** Advanced networking, managing security groups, creating volumes, and detailed instance configuration.
- **Key Features:**
    - **Security Groups:** Define firewall rules (e.g., open port 22 for SSH, port 80 for HTTP).
    - **Volume Management:** Create and attach persistent block storage.
    - **Network Configuration:** Manage floating IPs and private networks.

### General GUI Workflow

1. **Log In:** Use your ACCESS credentials to access either Exosphere or Horizon.
2. **Create Instance:**
    - **Image:** Choose an operating system (e.g., Ubuntu, CentOS).
    - **Flavor:** Select the amount of CPU and RAM needed.
    - **Key Pair:** Upload or generate an SSH public key for secure access.
    - **Network/Security:** Assign a security group that allows SSH traffic.
3. **Access:** Once the instance is \"Active,\" copy the Floating IP address and SSH into the machine:
   `ssh -i /path/to/your/key.pem username@floating-ip`

## 3. Using Cloud Resources via Command Line (CLI)

For users who prefer automation or a terminal interface, Jetstream2 supports the OpenStack CLI.

### Setup
1. **Install the OpenStack Client:**
   ```bash
   pip install openstackclient
   ```
2. **Authentication:**
   - Log in to the Horizon dashboard.
   - Navigate to the project/tenant section and download the **OpenRC** file.
   - Source the file in your terminal:
     ```bash
     source project-openrc.sh
     ```

### Common CLI Commands
- **List Instances:**
  ```bash
  openstack server list
  ```
- **Create a New Instance:**
  ```bash
  openstack server create --flavor <flavor_id> --image <image_id> --key-name <key_name> --nic net-id=<network_id> my-instance
  ```
- **Delete an Instance:**
  ```bash
  openstack server delete <instance_id>
  ```

For a full list of commands, refer to the [Jetstream2 CLI Documentation](https://docs.jetstream-cloud.org/).


## 2. Using Cloud Resources via GUI

Jetstream2 provides multiple graphical user interfaces depending on your needs:

### Exosphere (Recommended for Beginners)
Exosphere is a streamlined, simplified interface designed for the most common tasks.
- **Best for:** Quickly launching instances, basic management, and users who want a simpler experience.
- **Workflow:** Log in $\rightarrow$ Click "Create Instance" $\rightarrow$ Select Image/Flavor $\rightarrow$ Launch.

### Horizon (Full-Featured)
Horizon is the standard OpenStack dashboard and provides complete control over the cloud environment.
- **Best for:** Advanced networking, managing security groups, creating volumes, and detailed instance configuration.
- **Key Features:**
    - **Security Groups:** Define firewall rules (e.g., open port 22 for SSH, port 80 for HTTP).
    - **Volume Management:** Create and attach persistent block storage.
    - **Network Configuration:** Manage floating IPs and private networks.

### General GUI Workflow
1. **Log In:** Use your ACCESS credentials to access either Exosphere or Horizon.
2. **Create Instance:**
    - **Image:** Choose an operating system (e.g., Ubuntu, CentOS).
    - **Flavor:** Select the amount of CPU and RAM needed.
    - **Key Pair:** Upload or generate an SSH public key for secure access.
    - **Network/Security:** Assign a security group that allows SSH traffic.
3. **Access:** Once the instance is "Active," copy the Floating IP address and SSH into the machine:
   `ssh -i /path/to/your/key.pem username@floating-ip`

## 3. Using Cloud Resources via Command Line (CLI)

For users who prefer automation or a terminal interface, Jetstream2 supports the OpenStack CLI.

### Setup
1. **Install the OpenStack Client:**
   ```bash
   pip install openstackclient
   ```
2. **Authentication:**
   - Log in to the Horizon dashboard.
   - Navigate to the project/tenant section and download the **OpenRC** file.
   - Source the file in your terminal:
     ```bash
     source project-openrc.sh
     ```

### Common CLI Commands
- **List Instances:**
  ```bash
  openstack server list
  ```
- **Create a New Instance:**
  ```bash
  openstack server create --flavor <flavor_id> --image <image_id> --key-name <key_name> --nic net-id=<network_id> my-instance
  ```
- **Delete an Instance:**
  ```bash
  openstack server delete <instance_id>
  ```

For a full list of commands, refer to the [Jetstream2 CLI Documentation](https://docs.jetstream-cloud.org/).
