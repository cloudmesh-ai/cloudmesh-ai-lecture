# Exploring Python via the Interactive Shell

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Launch and navigate the Python Read-Eval-Print Loop (REPL) environment.
    - Utilize built-in introspection tools such as `type()`, `dir()`, and `help()` to examine objects and documentation.
    - Differentiate between interactive mode and script mode.
    - Transition from interactive experimentation to executing structured Python scripts from the command line.

For many developers, the most efficient way to learn a new library or test a small snippet of logic is through interactive experimentation. Rather than writing a full program, saving it to a file, and executing it, Python provides a built-in interactive shell that allows for immediate feedback.

This environment is known as a REPL, which stands for Read-Eval-Print Loop. This cycle enables a rapid prototyping workflow where an engineer can test an assumption, observe the result, and refine the code in real-time. This approach is particularly useful when exploring complex data structures or debugging a specific function call before integrating it into a larger codebase.

## The Python Interactive Shell (REPL)

To enter the interactive mode, execute the `python` command from your terminal:

```bash
$ python
```

Upon execution, the interpreter initializes and displays a header containing the Python version and build information, followed by the interactive prompt:

```python
Python 3.12.9 (main, Jan 18 2026, 10:10:24) [GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

The `>>>` symbol is the Python prompt, indicating that the interpreter is ready to receive a command. This is analogous to the `$` or `#` prompts found in Unix shells like Bash.

### The REPL Cycle

The interactive process operates in a continuous loop:

1. **Read**: The interpreter reads the input provided by the user.
2. **Evaluate**: The interpreter parses and executes the command.
3. **Print**: The result of the evaluation is printed to the screen.
4. **Loop**: The interpreter returns to the prompt, awaiting the next input.

## Introspection and Discovery Tools

One of the most powerful aspects of the REPL is the ability to perform "introspection"—the process of examining an object at runtime to determine its type and available capabilities.

### Identifying Object Types with `type()`

Python is dynamically typed, meaning a variable's type is determined by the value it holds. The `type()` function allows you to identify the class of any object.

```python
>>> type(42)
<class 'int'>
>>> type("hello")
<class 'str'>
>>> type(3.14)
<class 'float'>
```

### Discovering Attributes with `dir()`

While `type()` tells you what an object is, `dir()` tells you what the object can do. The `dir()` function returns a sorted list of strings containing the names of the attributes and methods available for that object.

```python
>>> my_list = [1, 2, 3]
>>> dir(my_list)
['__add__', '__class__', ..., 'append', 'clear', 'copy', 'count', 'extend', 'index', 'insert', 'pop', 'remove', 'reverse', 'sort']
```

By combining `dir()` with `type()`, you can quickly map out the API of any object without consulting external documentation.

### Accessing Documentation with `help()`

For detailed information about a function, class, or module, Python provides the `help()` utility. When called on an object, it opens a pager containing the official docstring.

```python
>>> help(int)
>>> help(list)
>>> help(str)
```

The `help()` interface uses a pager for navigation:
- **Spacebar**: Move down one page.
- **Arrow Keys**: Move up or down line-by-line.
- **'q'**: Exit the help pager and return to the `>>>` prompt.

## Transitioning to Script Mode

While the REPL is excellent for testing, it is not suitable for creating reusable software because the code is not persisted once the session ends. For production applications, code must be written into a script file.

### Creating and Running Scripts

A Python script is a plain text file with a `.py` extension. Once the code is written to a file, it can be executed by passing the filename as an argument to the Python interpreter.

Assuming a program is saved as `prg.py`, it is executed as follows:

```bash
$ python prg.py
```

### Naming Conventions

In professional development, scripts should be named using meaningful, descriptive identifiers. Avoid generic names like `test.py` or `script1.py`. Instead, use names that reflect the script's purpose, such as `backup_database.py` or `analyze_logs.py`. This ensures that other engineers can understand the function of the file without having to read the source code.

!!! tip "Summary Checklist"

    - [ ] Successfully launched the Python REPL from the terminal.
    - [ ] Understands the Read-Eval-Print-Loop (REPL) cycle.
    - [ ] Used `type()` to identify the class of various data types.
    - [ ] Used `dir()` to list the available methods and attributes of an object.
    - [ ] Navigated the `help()` documentation using the pager controls.
    - [ ] Created a `.py` file and executed it via the command line.

!!! note "Exercise 1: Basic REPL Operations"

    **Task**: Start the Python interactive shell. Perform three different arithmetic operations (addition, multiplication, and exponentiation) and verify the results.
    **Goal**: Familiarize yourself with the basic REPL input/output flow.

!!! note "Exercise 2: Object Exploration"

    **Task**: Create a dictionary in the REPL (e.g., `user = {"name": "Alice", "id": 1}`). Use `type()` to verify it is a dictionary, then use `dir()` to find the method used to remove an item from a dictionary. Finally, use `help()` on that specific method to understand its arguments.
    **Goal**: Practice the introspection workflow (`type` $\rightarrow$ `dir` $\rightarrow$ `help`).

!!! note "Exercise 3: Script Execution"

    **Task**: Write a Python script named `system_info.py` that prints the current date and time (using the `datetime` module). Execute the script from the terminal and verify the output.
    **Goal**: Transition from interactive experimentation to a persistent script file.
