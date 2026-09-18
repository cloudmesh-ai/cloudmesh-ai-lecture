Dictionaries

### Dotdict

For complex configuration or status dictionaries, we can simplify the notation using `.` instead of `[]`. This is achieved with `dotdict`:

```         
from cloudmesh.ai.common.dotdict import dotdict

data = {
    "host": "login-01",
    "status": "active"
}

node = dotdict(data)
```

Now you can access the attributes using either syntax:

```         
node["status"]
# or
node.status
```

This is particularly useful in conditional logic for improved readability:

```         
if node.status == "active":
    print("Node is ready for jobs")
```
### FlatDict

When dealing with nested hardware specifications (e.g., CPU or GPU details within a node), `FlatDict` can flatten the hierarchy into a single level.

```         
from cloudmesh.ai.common.FlatDict import FlatDict

node_data = {
    "host": "compute-001",
    "specs": {
        "cores": 128,
        "memory": "512GB"
    }
}

flat = FlatDict(node_data, sep=".")
```

The resulting structure will use the separator to represent the nesting:

```         
{
    "host": "compute-001",
    "specs.cores": 128,
    "specs.memory": "512GB"
}
```

------------------------------------------------------------------------

### Printing Dicts

To visualize a cluster's state or a list of nodes, the `Printer` class handles various formats including YAML, JSON, Table, and CSV. It can also automatically flatten nested data for table output.

```         
from cloudmesh.ai.common.Printer import Printer

cluster = [
    {
        "host": "cpu-01",
        "hardware": {
            "arch": "x86_64",
            "os": "RHEL"
        }
    },
    {
        "host": "gpu-01",
        "hardware": {
            "arch": "aarch64",
            "os": "Ubuntu"
        }
    }
]

# Print as a formatted table
table = Printer.flatwrite(cluster,
                          sort_keys=["host"],
                          order=["host", "hardware.arch", "hardware.os"],
                          header=["Node", "Architecture", "OS"],
                          output='table')

print(table)
```