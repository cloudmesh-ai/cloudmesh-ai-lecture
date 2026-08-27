 you prefer working programmatically or via the command line rather than using the Horizon web GUI, you can perform the exact same workflow on the KVM@TACC site using Chameleon's Python library (python-chi).  Here is how you can set up and launch a virtual machine instance on KVM@TACC using Python:1. Initialize and Connect to KVM@TACCFirst, set your site context to KVM@TACC and select your project:  Pythonimport chi
from chi import lease, server, network, context

# Choose your project and target the KVM site
context.choose_project()
context.choose_site("KVM@TACC")
2. Configure Key Pairs and NetworksEnsure your SSH key is registered and your private network/router are mapped:Python# Import or check your key pair (assumes public key is uploaded)
key_name = "my-ssh-key"

# Retrieve or create a private network connected to an external router
net_name = "sharednet1" # Or your custom private net
3. Create a Lease (If Required) and Launch the InstanceUnlike bare-metal nodes, virtual machines on KVM@TACC can often be launched directly, but you can also manage resources programmatically:  Pythonserver_name = "my-kvm-vm"
image_name = "CC-Ubuntu-22.04"  # Or your chosen standard image/appliance
flavor_name = "m1.small"          # Choose your virtual hardware size

# Launch the server instance
instance = server.create_server(
    server_name,
    image_name=image_name,
    flavor_name=flavor_name,
    network_name=net_name,
    key_name=key_name,
    security_groups=["default"]
)

print(f"Server {server_name} is launching...")
4. Associate a Floating IP and ConnectOnce the instance is active, assign a public IP and print out the SSH command:Python# Associate a floating IP
floating_ip = network.create_floating_ip("ext-net")
network.associate_floating_ip(instance.id, floating_ip.ip)

print(f"Connect via terminal:\nssh -i ~/.ssh/id_rsa cc@{floating_ip.ip}")