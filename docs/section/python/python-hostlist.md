# Python Hostlist

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Parse and manipulate Slurm-style hostlists using the `hostlist` library.
    - Expand compressed hostlists into individual hostnames, handling padding and suffixes.
    - Perform set-like operations on hostlists using methods and Python operators.
    - Use the Collection API for indexing, slicing, and filtering hosts.
    - Use the command-line interface for quick hostlist manipulation and pipeline integration.

`hostlist` is a fully-typed Python library designed for parsing and manipulating Slurm-style hostlists. It handles host groups compressed using brackets (e.g., `node[01-03,07]`), which is common in High Performance Computing (HPC) environments.

---

## Installation

Install the `hostlist` library using pip:

```bash
pip install hostlist
```

---

## Usage: Python API

The core of the library is the `Hostlist` class.

### Expansion

The `Hostlist.expand()` method converts a compressed string into a `Hostlist` object.

#### Basic and Mixed Expansion
Combine multiple ranges and individual hosts. The library handles numeric ranges and literal hostnames automatically.

```python
from hostlist import Hostlist

# Multiple ranges and individuals
hl = Hostlist.expand("node[01-03,07],gpu01")
# Result: ["gpu01", "node01", "node02", "node03", "node07"]

# Mixed hostnames
hl_mixed = Hostlist.expand("node[1-3],headnode")
# Result: ["headnode", "node1", "node2", "node3"]
```

#### Zero Padding and Suffixes
The library detects padding width to preserve leading zeros and maintains any suffixes.

```python
# Zero Padding
hl_pad = Hostlist.expand("node[001-002]")
# Result: ["node001", "node002"]

# Suffixes
hl_suf = Hostlist.expand("node[1-3].cluster.local")
# Result: ["node1.cluster.local", "node2.cluster.local", "node3.cluster.local"]
```

### Compression

The `.compact()` method converts a `Hostlist` object back into a compressed Slurm-style string.

```python
from hostlist import Hostlist

# Basic compression
hl = Hostlist.from_list(["node1", "node2", "node3"])
print(hl.compact()) # Output: "node[1-3]"

# Mixed compression (literals are kept separate)
hl_mixed = Hostlist.from_list(["node1", "node2", "node3", "headnode"])
print(hl_mixed.compact()) # Output: "headnode,node[1-3]"

# Uncompressed output (comma-separated list)
print(hl.compact(compress=False)) # Output: "node1,node2,node03"
```

### Set Operations

`hostlist` supports set operations using both method calls and Python operators.

| Operation | Method | Operator | Description |
| :--- | :--- | :---: | :--- |
| **Union** | `.union()` | `\|` | All hosts in either hostlist. |
| **Intersection** | `.intersect()` | `&` | Only hosts present in both hostlists. |
| **Difference** | `.diff()` | `-` | Hosts in the first list but not the second. |
| **Symmetric Diff** | `.xor()` | `^` | Hosts in either list, but not both. |

#### Example and Coercion
Set operations automatically coerce strings or lists into `Hostlist` objects.

```python
from hostlist import Hostlist

a = Hostlist.expand("node[1-5]")
b = Hostlist.expand("node[4-8]")

print((a | b).compact()) # Union: node[1-8]
print((a & b).compact()) # Intersection: node[4-5]
print((a - b).compact()) # Difference: node[1-3]
print((a ^ b).compact()) # Symmetric Difference: node[1-3,6-8]

# Coercion example: adding a simple string to a Hostlist
result = a | "node6" # Result: node[1-6]
```

### Collection API

A `Hostlist` object behaves like a read-only sequence of hostnames.

#### Indexing and Slicing
```python
hl = Hostlist.expand("node[1-10]")

# Access by index
print(hl[0]) # "node1"

# Slicing (returns a new Hostlist)
sub_hl = hl[0:3]
print(sub_hl.compact()) # "node[1-3]"
```

#### Search and Filtering
- `nth(n)`: Returns the $n$-th host (**1-based indexing**).
- `find(host)`: Returns the **1-based position** of a specific host.
- `size(N)`: Returns a new `Hostlist` containing at most $N$ hosts. Use negative numbers for the last $N$ hosts.
- `exclude(*hosts)`: Returns a new `Hostlist` with specified hosts removed.

```python
hl = Hostlist.expand("node[1-10]")

print(hl.nth(2))           # "node2"
print(hl.find("node2"))    # 2
print(hl.size(3).compact())   # "node[1-3]"
print(hl.size(-2).compact())  # "node[9-10]"
print(hl.exclude("node1").compact()) # "node[2-10]"
```

#### Iteration and Length
```python
hl = Hostlist.expand("node[1-3]")
print(len(hl)) # 3
for host in hl:
    print(host)
```

### Template Formatting

The `.format()` method generates strings based on a template containing the `{host}` placeholder.

```python
from hostlist import Hostlist

hl = Hostlist.expand("node[1-3]")

# Generate SSH commands
commands = hl.format("ssh {host} 'uptime'")
# Result: ["ssh node1 'uptime'", "ssh node2 'uptime'", "ssh node3 'uptime'"]

# Generate tool arguments
targets = hl.format("--node {host} ")
# Result: ["--node node1 ", "--node node2 ", "--node node3 "]
```

---

## Command Line Interface

The `hostlist` CLI provides terminal access to these tools.

### Expanding Hostlists
```bash
# Basic expansion
hostlist expand "node[01-03,07]" # Output: node01,node02,node03,node07

# Quiet output (comma-separated)
hostlist expand "node[1-3]" --quiet # Output: node1,node2,node3

# Formatted output
hostlist expand "node[1-3]" --format "ssh {host} uptime"
# Output:
# ssh node1 uptime
# ssh node2 uptime
# ssh node3 uptime
```

### Compacting Hostlists
```bash
hostlist compact "node1,node2,node3,node7" # Output: node[1-3,7]
```

### Pipeline Support
The CLI can read from `stdin`, making it ideal for shell pipelines:
```bash
echo "node[1-3]" | hostlist expand
```

---

## Assignments

!!! note "Assignment: HPC Inventory Manager"
    1. **Parsing**: Expand a complex hostlist containing multiple ranges, zero-padding, and a domain suffix (e.g., `compute[001-005,010].cluster.local`).
    2. **Filtering**: Use the `exclude()` method to remove a specific set of "maintenance" nodes from your expanded list.
    3. **Command Generation**: Use `.format()` to create a list of `ping` commands for the remaining healthy nodes.
    4. **CLI Integration**: Use the `hostlist` CLI in a bash script to compact a list of active nodes provided by an external command.

---

## Self-Evaluation

??? note "How does the `hostlist` library handle zero-padding in compressed lists?"
    The library automatically detects the padding width of the numeric range in the compressed string and preserves leading zeros when expanding the list into individual hostnames.

??? note "What is the difference between `nth()` and standard Python indexing (e.g., `hl[0]`)?"
    The `nth()` method uses 1-based indexing, whereas standard Python indexing (`hl[0]`) uses 0-based indexing.

??? note "Which set operators are supported by the `Hostlist` class for combining host groups?"
    The `Hostlist` class supports Union (`|`), Intersection (`&`), Difference (`-`), and Symmetric Difference (`^`).

---

## Summary Table

| Function / Method | Description | Example |
| :--- | :--- | :--- |
| `expand(spec)` | Parses a Slurm-style string into a `Hostlist` | `Hostlist.expand("node[1-3]")` |
| `compact(compress=True)` | Returns compressed string (or comma-list if `False`) | `hl.compact()` |
| `union() / \|` | Combines two hostlists | `hl_a \| hl_b` |
| `intersect() / &` | Finds common hosts | `hl_a & hl_b` |
| `diff() / -` | Finds hosts in first but not second | `hl_a - hl_b` |
| `xor() / ^` | Finds hosts in either but not both | `hl_a ^ hl_b` |
| `nth(n)` | Returns $n$-th host (1-based) | `hl.nth(1)` |
| `find(host)` | Returns 1-based position of host | `hl.find("node1")` |
| `size(N)` | Returns first (or last) $N$ hosts | `hl.size(5)` |
| `exclude(*hosts)` | Removes specific hosts | `hl.exclude("node1")` |
| `format(tpl)` | Generates strings using `{host}` template | `hl.format("ping {host}")` |
