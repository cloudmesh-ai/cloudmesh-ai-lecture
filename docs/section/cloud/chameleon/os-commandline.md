
# The Openstack Command

To create a virtual machine using the openstack command-line client with a specific SSH key, security group, and network, use the openstack server create command combined with their respective flags.  
SCS - Sovereign Cloud Stack

The Command

```Bash
openstack server create \
  --flavor m1.small \
  --image CC-Ubuntu-22.04 \
  --key-name my-ssh-key \
  --security-group my-security-group \
  --nic net-id=UUID_OR_NAME_OF_NETWORK \
  my-test-vm
 ```

Breakdown of the Flags

* --flavor <flavor>: The hardware profile (CPU, RAM, disk size). You can find available options using openstack flavor list.

* --image <image>: The OS boot image or appliance (e.g., Ubuntu, CentOS). Find options using openstack image list.

* --key-name <key>: The name of your registered SSH key pair for logging into the VM. (Generate or view keys via openstack keypair list).  
OpenStack Docs

* --security-group <group>: The firewall security group to apply. You can specify this flag multiple times if you want to attach more than one group. (View groups via openstack security group list).  
SCS - Sovereign Cloud Stack

* --nic net-id=<network>: Connects the VM to a specific private or shared network (supply either the network's name or its UUID). View available networks via openstack network list.

* my-test-vm: The final positional argument is the name you want to give to your new virtual machine instance.