---
title: "DocOpts {#s-python-docopts}"
---

!!! info "Learning Outcomes"
    - Use the `docopt` library to automatically generate a command-line argument parser from a help message.
    - Design command-line interfaces by writing clear, standard POSIX-style usage patterns.
    - Implement Python programs that seamlessly translate usage documentation into functional argument dictionaries.

When designing command-line arguments for Python programs, there are many available libraries. Because our approach emphasizes creating documentation first, `docopt` is an excellent choice for Python. The source code is available at:

- <https://github.com/docopt/docopt>

It can be installed via `pip`:

``` bash
$ pip install docopt
```

You can find sample programs here:

- <https://github.com/docopt/docopt/blob/master/examples/options_example.py>

The following example demonstrates how to use `docopt` for VM management:

``` python
"""Cloudmesh VM management

Usage:
  cm-go vm start NAME [--cloud=CLOUD]
  cm-go vm stop NAME [--cloud=CLOUD]
  cm-go set --cloud=CLOUD
  cm-go -h | --help
  cm-go --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --cloud=CLOUD  The name of the cloud.

ARGUMENTS:
  NAME     The name of the VM
"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0.0rc2')
    print(arguments)
```

A significant advantage of using `docopt` is that the same verbal description can be used across different programming languages, as showcased throughout this book.
