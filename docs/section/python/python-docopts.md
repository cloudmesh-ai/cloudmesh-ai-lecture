# Command-Line Interfaces with Docopt

!!! info "Learning Objectives"
    - Install and configure the `docopt` library.
    - Design command-line interfaces using standard POSIX-style usage patterns.
    - Translate usage documentation into functional Python argument dictionaries.
    - Handle optional and required arguments based on usage strings.
    - Implement a multi-command CLI using a single docstring.

When designing command-line interfaces (CLIs), developers typically spend significant time writing code to parse arguments and an equal amount of time writing the help message that explains how to use those arguments. This redundancy often leads to "documentation drift," where the help text and the actual implementation of the argument parser diverge over time.

Docopt takes a fundamentally different approach known as documentation-driven development. Instead of writing code to define a parser, the developer writes the help message first, following a standardized POSIX-style usage pattern. Docopt then parses this help message and automatically generates the argument parser. This ensures that the documentation and the implementation are always in perfect synchronization, as the documentation *is* the specification.

## Introduction to Docopt

Docopt is a library that implements the logic required to translate a usage string into a dictionary of arguments. Because it relies on a standardized format, the same usage patterns can be used across different programming languages, making it a useful tool for teams working in polyglot environments.

### Installation

The `docopt` library can be installed via pip:

```bash
pip install docopt
```

### How Docopt Works

In a typical Python application, the usage pattern is defined in the module's docstring (`__doc__`). The `docopt()` function then reads this string and parses the command-line input (`sys.argv`) against it.

```python
"""My Application
Usage:
  my_app.py <name>
  my_app.py (-h | --help)

Options:
  -h --help     Show this screen.
"""
from docopt import docopt

if __name__ == "__main__":
    arguments = docopt(__doc__)
    print(arguments)
```

If the user runs `python my_app.py Alice`, the resulting `arguments` dictionary will be `{'<name>': 'Alice', '--help': False}`. If the user provides invalid input, Docopt automatically prints the usage message and exits the program.

## Designing Usage Patterns

The power of Docopt lies in its adherence to POSIX usage conventions. By following these rules, you can define complex CLI behaviors without writing imperative parsing logic.

### Mandatory and Optional Arguments

- **Positional Arguments**: Defined in uppercase (e.g., `<name>` or `FILENAME`). These are mandatory unless specified otherwise.
- **Options**: Defined with a dash (e.g., `--verbose` or `-v`). These are optional by default.

### Short and Long Options

Docopt supports both short and long options, as well as the ability to group them together.

```text
Usage:
  my_tool.py [-v | --verbose] <input_file>
```

In this pattern, the user can provide either `-v` or `--verbose`, or neither.

### Multiple Usage Patterns

Many professional tools support different "modes" of operation. You can define multiple usage patterns on separate lines to support this.

```text
Usage:
  tool.py start <name> [--cloud=CLOUD]
  tool.py stop <name> [--cloud=CLOUD]
  tool.py set --cloud=CLOUD
  tool.py (-h | --help)
```

This definition tells Docopt that the tool has three distinct operational modes: starting a resource, stopping a resource, or setting a global configuration.

## Implementing the Parser

Once the usage string is defined, implementing the logic is a matter of accessing the values in the returned dictionary.

### Basic Implementation Example

The following example demonstrates a tool for managing virtual machines.

```python
"""VM Manager
Usage:
  vm_tool.py start <name> [--cloud=CLOUD]
  vm_tool.py stop <name> [--cloud=CLOUD]
  vm_tool.py -h | --help

Options:
  -h --help         Show this screen.
  --cloud=CLOUD     The name of the cloud provider [default: AWS].
"""
from docopt import docopt

def start_vm(name, cloud):
    print(f"Starting VM {name} on cloud {cloud}...")

def stop_vm(name, cloud):
    print(f"Stopping VM {name} on cloud {cloud}...")

if __name__ == "__main__":
    args = docopt(__doc__)

    cloud_provider = args['--cloud']
    
    if args['start']:
        start_vm(args['<name>'], cloud_provider)
    elif args['stop']:
        stop_vm(args['<name>'], cloud_provider)
```

### Handling Default Values

Default values can be specified directly in the Options section of the docstring using the `[default: value]` syntax. Docopt will automatically populate the dictionary with these values if the user does not provide the option.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] `docopt` library is installed via pip.
    - [ ] The module docstring contains a valid POSIX-style usage pattern.
    - [ ] Mandatory positional arguments are defined in uppercase (e.g., `<name>`).
    - [ ] Optional flags and parameters are correctly defined with dashes.
    - [ ] The `docopt(__doc__)` function is used to generate the arguments dictionary.
    - [ ] The program logic uses the dictionary keys to determine the execution path.
    - [ ] Default values are defined in the Options section of the docstring.

## Practical Exercises

!!! note "Exercise 1: Basic Input Parser"
    Create a CLI tool called `greet.py`. Design a usage string that requires a `<name>` argument and provides an optional `--formal` flag. If the flag is present, the output should be "Good day, [name]"; otherwise, "Hi, [name]!".

!!! note "Exercise 2: Resource Management Tool"
    Build a tool for managing a hypothetical "Cloud Storage" service. The usage string should support three patterns:
    1. `storage.py upload <file> <bucket>`
    2. `storage.py download <bucket> <file>`
    3. `storage.py list <bucket>`
    Implement the logic to print which action is being performed and which files/buckets are involved.

!!! note "Exercise 3: Advanced Option Handling"
    Implement a CLI that takes a mandatory `<filename>` and supports mutually exclusive options: `--encrypt` and `--decrypt`. Use the usage pattern `tool.py (--encrypt | --decrypt) <filename>`. Ensure the program prints an error if both or neither are provided (Docopt should handle this automatically).

## Further Reading

- Docopt Official GitHub: https://github.com/docopt/docopt
- Docopt Usage Guide: https://github.com/docopt/docopt#usage
