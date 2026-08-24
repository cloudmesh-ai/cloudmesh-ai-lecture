---
title: "Interactive Python"
---

!!! info "Learning Outcomes"
    - Execute and navigate the interactive Python Read-Eval-Print Loop (REPL) environment to test commands and inspect data types.
    - Utilize built-in diagnostic tools like `type()` and `help()` to query object attributes and documentation.
    - Transition from interactive experimentation to running structured script files from the command line.
    
Python can be used interactively. You can enter the interactive mode by executing the following command:

``` bash
$ python
```

You will see something like the following:

``` python
$ python
Python 3.12.9 (main, Jan 18 2026, 10:10:24) [GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

The `>>>` is the prompt used by the interpreter. This is similar to bash where commonly `$` is used.

Sometimes it is convenient to show the prompt when illustrating an example. This is to provide some context for what we are doing. If you are following along you will not need to type in the prompt.

This interactive Python process does the following:

- *read* your input commands
- *evaluate* your command
- *print* the result of the evaluation
- *loop* back to the beginning.

This is why you may see the interactive loop referred to as a **REPL**: **R**ead-**E**valuate-**P**rint-**L**oop.

## REPL (Read Eval Print Loop)

There are many different types beyond what we have seen so far, such as **dictionaries**, **lists**, and **sets**. One handy way of using interactive Python is to get the type of a value using type():

``` python
>>> type(42)
<type 'int'>
>>> type('hello')
<type 'str'>
>>> type(3.14)
<type 'float'>
```

You can also ask for help about something using help():

``` python
>>> help(int)
>>> help(list)
>>> help(str)
```

Using help() opens up a help message within a pager. To navigate, you can use the spacebar to go down a page, 'w' to go up a page, the arrow keys to go up/down line-by-line, or 'q' to exit.

## Interpreter

Although the interactive mode provides a convenient tool to test things out, you will quickly see that for our class we want to use the Python interpreter from the command line. Let us assume the program is called `prg.py`. Once you have written it in that file you simply can call it with

``` bash
$ python prg.py
```

It is important to name the program with meaningful names.