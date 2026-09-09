# diagram.py
# -------------------------------------------------
# Generates a simple cloud‑network diagram with Graphviz.
# -------------------------------------------------

# Install the Python wrapper if needed (uncomment the next line once)
# !pip install -q graphviz

import pathlib
import graphviz

# ------------------------------------------------------------------
# 1️⃣ Define the diagram (the same layout you saw in the tutorial)
# ------------------------------------------------------------------
dot = graphviz.Digraph(comment='Cloud Networking Overview', format='png')
dot.attr(rankdir='LR', splines='ortho')   # left‑to‑right, orthogonal edges

# Nodes – colour‑coded for quick visual grouping
dot.node('Internet', 'Internet', shape='cloud', style='filled', fillcolor='#e6e6fa')
dot.node('IGW', 'Internet\nGateway', shape='cloud', style='filled', fillcolor='#d0e0ff')
dot.node('LB', 'Load Balancer\n(public subnet)', shape='box', style='filled', fillcolor='#cfe2f3')
dot.node('Bastion', 'Bastion Host\n(public subnet)', shape='box', style='filled', fillcolor='#e2efda')
dot.node('NAT', 'NAT Gateway', shape='box', style='filled', fillcolor='#fff2cc')
dot.node('App', 'App Servers\n(private subnet)', shape='box', style='filled', fillcolor='#f4cccc')
dot.node('DB', 'Database\n(private subnet)', shape='cylinder', style='filled', fillcolor='#d9ead3')

# ------------------------------------------------------------------
# 2️⃣ Connect the nodes (edges) – add helpful labels
# ------------------------------------------------------------------
dot.edge('Internet', 'IGW', label='0.0.0.0/0')
dot.edge('IGW', 'LB', label='Public Subnet')
dot.edge('IGW', 'Bastion', label='Public Subnet')
dot.edge('LB', 'App', label='HTTP/HTTPS (80/443)')
dot.edge('App', 'DB', label='SQL (3306)', style='dashed')
dot.edge('App', 'NAT', label='Outbound', dir='both')
dot.edge('NAT', 'IGW', label='Outbound to Internet')
dot.edge('Bastion', 'App', label='SSH (22)', style='dotted')

# ------------------------------------------------------------------
# 3️⃣ Render the diagram to a **writable** location
# ------------------------------------------------------------------
# Use the script’s folder – this is always writable
output_dir = pathlib.Path(__file__).parent
output_path = output_dir / "cloud_network.png"

dot.render(filename=str(output_path), cleanup=True)   # `cleanup` removes the temporary .dot file

print(f"✅ Diagram generated: {output_path.resolve()}")