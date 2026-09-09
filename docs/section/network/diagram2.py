# Hands‑On: Generate a Visual Diagram  

The script below uses **Graphviz** (a Python wrapper) to draw a simple diagram of the architecture. It saves a PNG file (`cloud_network.png`) that you can open locally or embed in documentation.

> **How to run it**  
> 1. Copy the entire block into a Jupyter notebook cell, a Python REPL, or the **Code Interpreter** tool in this chat.  
> 2. Execute the cell. The image will be saved to `/mnt/data/cloud_network.png`.  
> 3. The script prints the file path; you can view the image directly in the notebook or open it from the file system.

```python
# Install the required library (run once)
!pip -q install graphviz

import graphviz, os

# -------------------------------------------------------
#  1. Define the diagram
# -------------------------------------------------------
dot = graphviz.Digraph(comment='Cloud Networking Overview', format='png')
dot.attr(rankdir='LR', splines='ortho')   # Left‑to‑right layout, orthogonal edges

# Nodes – shapes/colors help differentiate roles
dot.node('Internet', 'Internet', shape='cloud', style='filled', fillcolor='#e6e6fa')
dot.node('IGW', 'Internet\nGateway', shape='cloud', style='filled', fillcolor='#d0e0ff')
dot.node('LB', 'Load Balancer\n(public)', shape='box', style='filled', fillcolor='#cfe2f3')
dot.node('Bastion', 'Bastion Host\n(public)', shape='box', style='filled', fillcolor='#e2efda')
dot.node('NAT', 'NAT Gateway', shape='box', style='filled', fillcolor='#fff2cc')
dot.node('App', 'App Servers\n(private)', shape='box', style='filled', fillcolor='#f4cccc')
dot.node('DB', 'Database\n(private)', shape='cylinder', style='filled', fillcolor='#d9ead3')

# -------------------------------------------------------
# 2. Connect the nodes (edges) with meaningful labels
# -------------------------------------------------------
dot.edge('Internet', 'IGW', label='0.0.0.0/0')
dot.edge('IGW', 'LB', label='Public Subnet')
dot.edge('IGW', 'Bastion', label='Public Subnet')
dot.edge('LB', 'App', label='HTTP/HTTPS (80/443)')
dot.edge('App', 'DB', label='SQL (3306)', style='dashed')
dot.edge('App', 'NAT', label='Outbound', dir='both')
dot.edge('NAT', 'IGW', label='Outbound to Internet')
dot.edge('Bastion', 'App', label='SSH (22)', style='dotted')

# -------------------------------------------------------
# 3. Render the diagram to a PNG file
# -------------------------------------------------------
output_path = "/mnt/data/cloud_network.png"
dot.render(filename=output_path, cleanup=True)   # cleanup removes the intermediate .dot file

print(f"Diagram saved to: {output_path}")
```