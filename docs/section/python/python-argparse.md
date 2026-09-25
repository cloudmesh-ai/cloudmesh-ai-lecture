
# Command Line Interfaces with Python **argparse**

!!! info "Learning Objectives"

    - Understand the role of `argparse` in the Python standard library.  
    - Build a basic CLI parser using `ArgumentParser`.  
    - Define positional arguments and optional flags with type conversion and default values.  
    - Create mutually‑exclusive groups and sub‑commands (via `add_subparsers`).  
    - Generate automatic, user‑friendly help pages and error messages.  
    - Add simple interactive prompts when required options are missing.  

The Command Line Interface (CLI) remains a fundamental tool for system administrators, DevOps engineers, and developers. While many third‑party packages (e.g., Click, Typer) provide a more “declarative” feel, `argparse` is the **built‑in** way to parse command‑line arguments in Python. Because it ships with the interpreter, you never need to add a dependency, and it offers a complete feature set: positional arguments, optional flags, type validation, sub‑commands, mutually‑exclusive groups, automatic help, and even builtin tab‑completion via `argcomplete`.

---

## Introduction to `argparse`

`argparse` replaces the older `optparse` module and is part of the 
Python standard library since version 3.2. Its design follows the classic 
*imperative* style: you create a parser object, call methods to declare arguments, 
then ask it to parse `sys.argv`. While the API is a bit more verbose than decorator‑based libraries, the explicitness makes the flow easy to follow, especially for newcomers to CLI programming.

### No installation required

```bash
# `argparse` ships with Python – there is nothing to install.
python -c "import argparse; print(argparse.__version__ or 'built‑in')"
```

---

## The Basic `ArgumentParser`

The smallest usable CLI with `argparse` looks like this:

```python
import argparse

def main():
    # Create the top‑level parser
    parser = argparse.ArgumentParser(
        prog="hello",
        description="A minimal example that greets the world."
    )
    # No arguments are defined – just a plain script
    args = parser.parse_args()
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

Running `python hello.py -h` produces:

```
usage: hello [-h]

A minimal example that greets the world.

optional arguments:

  -h, --help  show this help message and exit
```

`argparse` automatically adds the `-h/--help` flag and formats the usage string for you.

---

## Positional Arguments

Positional arguments are required values that appear in a fixed order.

```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="readfile",
        description="Read and print the contents of a file."
    )
    parser.add_argument(
        "filename",
        help="Path to the file that should be displayed."
    )
    args = parser.parse_args()
    with open(args.filename, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    main()
```

```
$ python readfile.py example.txt
```

If the user omits the filename, `argparse` prints an error and the usage message automatically.

---

## Optional Flags / Options
Optional arguments start with one or two hyphens (`-` or `--`). They can have defaults, types, and help strings.

```python
import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="greet",
        description="Greet a person a configurable number of times."
    )
    parser.add_argument(
        "-n", "--name",
        default="World",
        help="Name of the person to greet."
    )
    parser.add_argument(
        "-c", "--count",
        type=int,
        default=1,
        help="How many greetings to print."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output."
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"[DEBUG] name={args.name!r}, count={args.count}")

    for _ in range(args.count):
        print(f"Hello, {args.name}!")

if __name__ == "__main__":
    main()
```

Typical help output:

```
$ python greet.py -h
usage: greet [-h] [-n NAME] [-c COUNT] [-v]

Greet a person a configurable number of times.

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Name of the person to greet. (default: World)
  -c COUNT, --count COUNT
                        How many greetings to print. (default: 1)
  -v, --verbose         Enable verbose output.
```

### Type Validation
`argparse` validates the type you declare (`type=int`, `type=float`, `type=Path`, …) *before* your code runs. Supplying an invalid value yields a clear error:

```
$ python greet.py --count abc
usage: greet [-h] [-n NAME] [-c COUNT] [-v]
greet: error: argument -c/--count: invalid int value: 'abc'
```

---

## Mutually Exclusive Groups
Sometimes two options cannot be used together (e.g., `--quiet` vs `--verbose`). `argparse` lets you declare such constraints:

```python
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-q", "--quiet", action="store_true", help="Suppress output.")
group.add_argument("-v", "--verbose", action="store_true", help="Show detailed output.")
```

If a user provides both flags, `argparse` reports the conflict automatically.

---

## Sub‑Commands with `add_subparsers`
Large tools (think `git` or `docker`) consist of a top‑level command followed by many sub‑commands. `argparse` supports this pattern via *subparsers*.

```python
import argparse

def cmd_status(_):
    print("System status: OK")

def cmd_restart(args):
    print(f"Restarting service {args.service!r}")

def main():
    parser = argparse.ArgumentParser(
        prog="sysctl",
        description="Simple system control utility."
    )
    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid sub‑commands",
        dest="command",
        required=True   # Python 3.7+; forces a sub‑command
    )

    # `status` sub‑command – no extra arguments
    parser_status = subparsers.add_parser(
        "status",
        help="Show a brief system health summary."
    )
    parser_status.set_defaults(func=cmd_status)

    # `restart` sub‑command – requires a service name
    parser_restart = subparsers.add_parser(
        "restart",
        help="Restart a named service."
    )
    parser_restart.add_argument(
        "service",
        help="Name of the service to restart."
    )
    parser_restart.set_defaults(func=cmd_restart)

    args = parser.parse_args()
    # Dispatch to the appropriate function
    args.func(args)

if __name__ == "__main__":
    main()
```

Resulting usage:

```
$ python sysctl.py -h
usage: sysctl [-h] {status,restart} ...

Simple system control utility.

positional arguments:
  {status,restart}   valid sub‑commands
    status           Show a brief system health summary.
    restart          Restart a named service.

optional arguments:
  -h, --help         show this help message and exit
```

Running a sub‑command:

```
$ python sysctl.py restart nginx
Restarting service 'nginx'
```

---

## Prompting for Missing Required Options
`argparse` itself does **not** provide interactive prompts, but a small wrapper can achieve the same effect without pulling in a full‑featured library.

```python
import argparse

def prompt_missing(value, prompt_msg):
    """Return the value if present; otherwise ask the user."""
    if value is not None:
        return value
    return input(prompt_msg)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--username",
        help="Login name."
    )
    parser.add_argument(
        "-p", "--password",
        help="Password (will be prompted if omitted)."
    )
    args = parser.parse_args()

    args.username = prompt_missing(args.username, "Username: ")
    args.password = prompt_missing(args.password, "Password: ")

    print(f"Logging in as {args.username!r} ...")
    # (authentication logic goes here)

if __name__ == "__main__":
    main()
```

When the user omits `--password`, the script asks for it interactively, keeping the CLI experience smooth.

---

## Automatic Help & Error Messages
All of the examples above benefit from two core features that `argparse` supplies out of the box:

| Feature | What `argparse` does |
|---------|-----------------------|
| **Help page** | Generates a nicely formatted usage/description block, including defaults and choices. |
| **Error handling** | Detects missing required args, unknown flags, type mismatches, and prints a concise error plus the usage line. |
| **Formatting** | Aligns options, wraps text to the terminal width, and can be customised via `formatter_class`. |

You can further tweak the appearance:

```python
parser = argparse.ArgumentParser(
    prog="mytool",
    description="Demo with a custom formatter.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter  # shows defaults automatically
)
```

---

## Self Assessment

??? question "Self Assessment"
    Test your knowledge by answering the questions below.

    ??? question "What is the primary advantage of using `argparse` over writing your own `sys.argv` parsing logic?"
        `argparse` automatically handles type conversion, default values, help generation, and clear error messages, removing the need for repetitive boilerplate code.

    ??? question "How do you declare an optional flag that does **not** take a value but merely toggles a Boolean?"
        Use `action='store_true'` (or `action='store_false'`) in `add_argument`. Example: `parser.add_argument('-v', '--verbose', action='store_true')`.

    ??? question "Explain how sub‑commands are created with `argparse`. What method is used, and how do you bind a function to a sub‑command?"
        Call `parser.add_subparsers()` to obtain a sub‑parser object, then `add_parser()` for each sub‑command. Use `set_defaults(func=callback)` on each sub‑parser; after parsing, call `args.func(args)`.

    ??? question "What happens when a user supplies an invalid value for an argument that has `type=int`?"
        `argparse` catches the `ValueError`, prints an error like `argument -c/--count: invalid int value: 'abc'`, shows the usage line, and exits with status 2.

    ??? question "How can you ensure that two optional arguments cannot be used together?"
        Place them in a mutually exclusive group via `parser.add_mutually_exclusive_group()` and add the arguments to that group.

---

## Assignments

!!! note "Assignment 1 – Simple Greeter"
    Write a script `greeter.py` that:

    - Accepts a **positional** `name`.
    - Has an optional `--formal` flag (`action='store_true'`).
    - Prints `"Good day, <name>"` when `--formal` is present, otherwise `"Hi, <name>!"`.

!!! note "Assignment 2 – File Utility with Sub‑Commands"
    Build a CLI called `filetool.py` with a **sub‑command group**:

    1. `write <filename> <text>` – writes `text` to `filename`.
    2. `read <filename>` – prints the file contents, handling `FileNotFoundError` gracefully and exiting with a user‑friendly message.

!!! note "Assignment 3 – System Monitor with Prompted Credentials"
    Create `monitor.py` that:

    - Requires `--user` (username) and `--pass` (password) options.
    - If either is omitted, prompt the user interactively.
    - Prints a placeholder message: `"Authenticated as <user>"`.
    - Bonus: add a `--quiet` flag that suppresses the final message.

---

## Further Reading

- **Python Docs – argparse**: https://docs.python.org/3/library/argparse.html  
- **Real‑world argparse patterns**: https://docs.python.org/3/howto/argparse.html#argparse‑example  
- **argcomplete (tab‑completion for argparse)**: https://github.com/kislyuk/argcomplete  
- **PEP 383 – Improving the Unicode Support in the Python 2.x Command‑Line** (historical context on why `argparse` was created).  

