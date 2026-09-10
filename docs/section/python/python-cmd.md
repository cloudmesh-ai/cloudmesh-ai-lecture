# Interactive Shells with Python cmd

!!! info "Learning Objectives"
    - Implement an interactive command-line interpreter using the `cmd.Cmd` base class.
    - Create custom command handlers using the `do_` method pattern.
    - Manage the shell lifecycle, including handling EOF (Ctrl-D) and graceful exits.
    - Customize the user experience with custom prompts and welcome messages.
    - Implement a built-in help system for custom commands.

Most command-line tools operate on a "one-shot" basis: the user provides arguments, the program executes a task, and the process terminates. However, many professional tools—such as database consoles (e.g., `psql` or `mysql`), network switches, and debuggers—operate as persistent interactive shells. This pattern is known as a REPL (Read-Eval-Print Loop).

The Python `cmd` module provides a framework for building these line-oriented command processors. By providing a base class that handles the loop, input reading, and basic command dispatching, `cmd` allows developers to focus on implementing the actual logic of the commands rather than the mechanics of the shell. While libraries like `click` are ideal for one-off CLI tools, `cmd` is the standard choice for building a dedicated interactive console.

## Fundamentals of the `cmd` Module

The core of any `cmd` application is a subclass of `cmd.Cmd`. This class defines the behavior of the shell, including the commands it recognizes and how it interacts with the user.

### The `do_` Method Pattern

The `cmd` module uses a naming convention to identify commands. Any method defined in the subclass that starts with the prefix `do_` is automatically recognized as a command. For example, a method named `do_greet` creates a command that the user can trigger by typing `greet` at the prompt.

### Minimal Implementation Example

The following example demonstrates a basic shell that greets the user.

```python
import cmd

class GreetingShell(cmd.Cmd):
    """A simple command processor example."""

    def do_greet(self, line):
        """Greet the user. Usage: greet [name]"""
        if line.strip():
            print(f"Hello, {line.strip().title()}!")
        else:
            print("Hello!")

    def do_EOF(self, line):
        """Handle Ctrl-D to exit the shell."""
        print("\nExiting shell... Goodbye!")
        return True

if __name__ == "__main__":
    GreetingShell().cmdloop()
```

In this implementation:
- `do_greet(self, line)`: The `line` argument contains everything the user typed after the command name.
- `do_EOF(self, line)`: This is a special method triggered when the user presses `Ctrl-D`.
- `cmdloop()`: This method starts the infinite loop that reads input and dispatches it to the corresponding `do_` method.

## Managing the Shell Lifecycle

A professional interactive shell requires more than just command handling; it needs a defined lifecycle and a user-friendly interface.

### Exiting the Shell

In the `cmd` module, the shell continues to run until a command method returns `True`. In the example above, `do_EOF` returns `True`, which signals `cmdloop()` to terminate and exit the program.

### Customizing the Interface

The `cmd.Cmd` class provides several attributes that can be overridden to change the look and feel of the shell.

- `prompt`: A string that is displayed before every input line.
- `intro`: A string displayed once when the shell starts.

```python
class MyCustomShell(cmd.Cmd):
    prompt = "my-shell >> "
    intro = "Welcome to the Custom Shell. Type 'help' for a list of commands."

    def do_quit(self, line):
        """Exit the shell."""
        return True
```

## Command Arguments and Parsing

Since the `cmd` module only provides the raw input string (`line`) to the `do_` methods, the developer is responsible for parsing that string.

### Basic Argument Parsing

For simple tools, using `split()` is often sufficient to separate the command arguments.

```python
class CalculatorShell(cmd.Cmd):
    prompt = "calc >>> "

    def do_add(self, line):
        """Add numbers together. Usage: add 1 2 3"""
        try:
            args = line.split()
            total = sum(float(arg) for arg in args)
            print(f"Total: {total}")
        except ValueError:
            print("Error: Please provide only numbers.")

    def do_subtract(self, line):
        """Subtract numbers from the first argument. Usage: subtract 10 2 3"""
        try:
            args = line.split()
            if not args:
                print("Error: No numbers provided.")
                return
            total = float(args[0])
            for arg in args[1:]:
                total -= float(arg)
            print(f"Total: {total}")
        except ValueError:
            print("Error: Please provide only numbers.")

    def do_EOF(self, line):
        return True
```

### Advanced Parsing

For more complex argument requirements (such as flags or optional parameters), the `line` string can be passed to a separate parser, such as `argparse` or `shlex`.

## Implementing the Help System

One of the most useful features of the `cmd` module is the automatic help system. By default, typing `help` lists all available commands.

### Documented vs. Undocumented Commands

The `cmd` module distinguishes between documented and undocumented commands:
- **Undocumented**: Any `do_` method.
- **Documented**: Any `do_` method that has a corresponding `help_` method.

### Creating Help Methods

To document a command, create a method with the prefix `help_` followed by the command name.

```python
class DocumentedShell(cmd.Cmd):
    def do_status(self, line):
        """Check system status."""
        print("System is operational.")

    def help_status(self):
        print("status")
        print("  Displays the current operational status of the system.")

    def do_EOF(self, line):
        return True
```

When the user types `help status`, the `help_status` method is executed, providing the user with specific instructions.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] `cmd.Cmd` is subclassed to create the shell.
    - [ ] Command logic is implemented using the `do_` prefix.
    - [ ] `cmdloop()` is called to initiate the interactive session.
    - [ ] `do_EOF` is defined to allow the user to exit via Ctrl-D.
    - [ ] `prompt` and `intro` are customized for the target audience.
    - [ ] Input `line` is correctly parsed using `split()` or a parsing library.
    - [ ] `help_` methods are implemented for all public-facing commands.

## Practical Exercises

!!! note "Exercise 1: Basic Shell Setup"
    Create a shell called `SimpleShell`. Implement two commands: `hello` (which prints a greeting) and `exit` (which closes the shell). Ensure the shell has a custom prompt like `(Simple) > `.

!!! note "Exercise 2: Interactive Task Manager"
    Build a task management shell. Implement the following commands:
    1. `add [task]`: Adds a task to a Python list.
    2. `list`: Displays all current tasks with their index.
    3. `done [index]`: Removes a task from the list by its index.
    Include a `help_` method for each command to explain the usage.

!!! note "Exercise 3: Virtual Storage Simulator"
    Create a shell that simulates a key-value store. Use a dictionary to store data. Implement:
    1. `set [key] [value]`: Stores a value associated with a key.
    2. `get [key]`: Retrieves the value for a given key.
    3. `delete [key]`: Removes the key from the store.
    Handle cases where the user tries to `get` or `delete` a key that does not exist by printing a clear error message.

## Further Reading

- Python Official `cmd` Documentation: https://docs.python.org/3/library/cmd.html
- Python Module of the Week (PyMOTW) - `cmd`: https://pymotw.com/3/cmd/
