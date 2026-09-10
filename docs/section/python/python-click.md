# Command Line Interfaces with Python Click

!!! info "Learning Objectives"
    - Install and configure the `click` library.
    - Create basic CLI commands using decorators.
    - Implement command-line options and arguments with type validation.
    - Build complex, nested CLI structures using `click.group`.
    - Implement an interactive shell for CLI commands using `click-shell`.
    - Generate automatic help pages for end users.

The Command Line Interface (CLI) remains a fundamental tool for system administrators, DevOps engineers, and developers. While graphical interfaces are useful for discovery, the CLI is superior for automation, scripting, and remote management. In Python, the standard way to handle command-line arguments is the `argparse` module. While functional, `argparse` requires a significant amount of boilerplate code to define arguments, handle types, and generate help text.

Click (Command Line Interface Creation Kit) is a package that allows for the creation of composable command-line interfaces. Instead of manually defining a parser object, Click uses a declarative approach based on Python decorators. This allows developers to wrap standard Python functions and transform them into full-fledged CLI commands with minimal overhead. By automating the generation of help pages and handling type conversion, Click allows the developer to focus on the business logic of the tool rather than the mechanics of argument parsing.

## Introduction to Click

Click is designed to be intuitive and highly composable. It replaces the imperative style of `argparse` with a declarative style.

### Installation

The `click` library can be installed via pip:

```bash
pip install click
```

### The Basic Command

The core of any Click application is the `@click.command()` decorator. This decorator tells Click that the following function should be treated as a command-line tool.

```python
import click

@click.command()
def hello():
    """A simple program that says hello."""
    click.echo("Hello, World!")

if __name__ == "__main__":
    hello()
```

In the example above, `click.echo` is used instead of the standard `print` function. `click.echo` is preferred because it ensures consistent output across different terminals and operating systems, handling character encoding and color formatting more reliably.

## Options and Arguments

Click distinguishes between "Arguments" and "Options". Understanding this distinction is key to designing a professional CLI.

### Arguments

Arguments are mandatory inputs that usually represent the "object" the command operates on, such as a filename or a URL.

```python
@click.command()
@click.argument('filename')
def read_file(filename):
    """Reads the content of a specified FILE."""
    click.echo(f"Reading file: {filename}")
```

### Options

Options are optional parameters that modify the behavior of the command. They are prefixed with dashes (e.g., `--count` or `-c`).

```python
@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet.')
def greet(count, name):
    """Greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo(f"Hello {name}!")
```

In this example:
- `default=1` provides a fallback value if the user does not specify the count.
- `prompt='Your name'` makes the CLI interactive; if the user forgets the `--name` option, Click will pause and ask for it.

### Type Validation

Click provides built-in type validation to ensure the inputs are correct before the function is even executed.

```python
@click.command()
@click.option('--port', type=int, default=8080, help='Port to listen on.')
@click.option('--mode', type=click.Choice(['debug', 'info', 'warn']), default='info')
def start_server(port, mode):
    """Starts a server on a specific PORT and MODE."""
    click.echo(f"Starting server on port {port} in {mode} mode.")
```

If a user provides a string for the `--port` option, Click will automatically generate an error message and the help page without the developer needing to write a single `try-except` block.

## Building Complex CLIs with Groups

Real-world tools, such as `git` or `docker`, do not have a single command. Instead, they have a primary entry point with many subcommands (e.g., `git commit`, `git push`). Click implements this through the `group` concept.

### Implementing a Group

A group is a special type of command that can have other commands attached to it.

```python
@click.group()
def cli():
    """My System Management Tool."""
    pass

@cli.command()
def status():
    """Check the system status."""
    click.echo("System is running normally.")

@cli.command()
@click.argument('name')
def restart(name):
    """Restart a specific service."""
    click.echo(f"Restarting service: {name}")

if __name__ == "__main__":
    cli()
```

The resulting CLI structure allows the user to run:
- `python tool.py status`
- `python tool.py restart nginx`
- `python tool.py --help` (shows all available subcommands)

## Interactive Shells with click-shell

For tools that require frequent interaction, restarting the Python process for every command is inefficient. The `click-shell` extension allows Click commands to be run within a persistent interactive shell.

### Installation

```bash
pip install click-shell
```

### Creating a Shell

To create a shell, use the `@shell` decorator instead of `@click.group()`.

```python
from click_shell import shell
import click

@shell(prompt='my-shell > ', intro='Starting the CLI shell...')
def my_shell():
    pass

@my_shell.command()
def hello():
    """Simple hello command."""
    click.echo("Hello from the shell!")

@my_shell.command()
@click.option('--name', prompt='Name')
def greet(name):
    """Greet a specific user."""
    click.echo(f"Hello, {name}!")

if __name__ == "__main__":
    my_shell()
```

Once launched, the user remains inside `my-shell >` and can execute `hello` or `greet` repeatedly without exiting the program.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] `click` library is installed.
    - [ ] Basic command created using the `@click.command()` decorator.
    - [ ] Difference between arguments (mandatory) and options (optional) is implemented.
    - [ ] Type validation (e.g., `type=int`, `click.Choice`) is used to sanitize input.
    - [ ] A nested command structure is built using `@click.group()`.
    - [ ] Help pages are automatically generated and verified via `--help`.
    - [ ] An interactive shell is implemented using `click-shell`.

## Practical Exercises

!!! note "Exercise 1: Basic Greeting Tool"
    Create a CLI tool called `greeter.py`. It should have one argument (`name`) and one option (`--formal`, a boolean flag). If `--formal` is present, the tool should output "Good day, [name]". Otherwise, it should output "Hi, [name]!".

!!! note "Exercise 2: Simple File Utility"
    Build a CLI with a group called `filetool`. Implement two subcommands:
    1. `write`: Takes a filename (argument) and text (argument) and writes the text to the file.
    2. `read`: Takes a filename (argument) and prints the content to the console.
    Ensure that the `read` command handles the case where the file does not exist.

!!! note "Exercise 3: System Monitor Shell"
    Using `click-shell`, create an interactive shell called `sysmon`. Implement two commands:
    1. `cpu`: Displays the current CPU usage (use the `psutil` library if available, or a mock value).
    2. `mem`: Displays the current memory usage.
    The shell should start with a custom intro message and a prompt like `sysmon >> `.

## Further Reading

- Click Official Documentation: http://click.pocoo.org/
- click-shell GitHub Repository: https://github.com/clarkperkins/click-shell
- Python Standard Library `argparse` (for comparison): https://docs.python.org/3/library/argparse.html
