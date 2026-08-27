import openstack

# 1. Connect to OpenStack
# This automatically reads credentials from environment variables 
# or your clouds.yaml file (e.g., located in ~/.config/openstack/clouds.yaml)
conn = openstack.connect(cloud="chameleon") # Replace "chameleon" with your cloud name if different

# Define your resource names or UUIDs
server_name = "my-test-vm"
image_name = "CC-Ubuntu-22.04"
flavor_name = "m1.small"
network_name = "sharednet1"
key_name = "my-ssh-key"
security_group_name = "default"

print(f"Initializing creation of VM: {server_name}...")

# 2. Retrieve required resource IDs
image = conn.compute.find_image(image_name)
flavor = conn.compute.find_flavor(flavor_name)
network = conn.network.find_network(network_name)

if not all([image, flavor, network]):
    raise ValueError("Could not find one or more required resources (image, flavor, or network).")

# 3. Create the Server Instance
server = conn.compute.create_server(
    name=server_name,
    image_id=image.id,
    flavor_id=flavor.id,
    networks=[{"uuid": network.id}],
    key_name=key_name,
    security_groups=[{"name": security_group_name}]
)

# 4. Wait for the server to finish building
print("Waiting for server to build...")
server = conn.compute.wait_for_server(server)

print(f"Success! Server {server.name} is now running.")
print(f"ID: {server.id}")
print(f"Status: {server.status}")
Prerequisites to run this script:
Install the SDK:

Bash
pip install openstacksdk
Cloud Configuration (clouds.yaml):
Ensure you have your OpenStack RC file sourced or a valid clouds.yaml file configured in ~/.config/openstack/ so openstack.connect() knows how to authenticate.