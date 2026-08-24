---
title: "Editors"
---

!!! info "Learning Outcomes"
    - Evaluate popular Python editing tools and IDEs, including PyCharm and VS Code, to select the best environment for your development workflow.
    - Review core installation methods for setting up development environments on local machines or virtual servers.
    - Leverage supplemental video guides and tutorials to accelerate your proficiency with Python programming and IDE navigation.

This section is meant to give an overview of the Python editing tools needed for completing this course. There are many other alternatives; however, we do recommend using PyCharm.

We summarize some of their features in a table.

|  |  |  |  |  |
|----|----|----|----|----|
| **Feature** | **PyCharm** | **VS Code** | **Vim (Neovim)** | **Emacs** |
| **Category** | Full-Featured IDE | Extensible Editor | Modal Text Editor | "Operating System" |
| **Best For** | Professional Python/Web | General Purpose / Polyglot | Remote / Fast Editing | Infinite Customization |
| **Setup Time** | Instant (Out-of-the-box) | Quick (Extension-based) | High (Config-heavy) | High (Script-heavy) |
| **Learning Curve** | Gentle | Moderate | Steep (Modal) | Very Steep (Lisp-based) |
| **Resource Usage** | High (RAM hungry) | Moderate | Very Low | Moderate to High |
| **Key Strength** | Deep Code Analysis | Massive Ecosystem | Keyboard Efficiency | Workflow Integration |
| **Price** | Free (Comm) / Paid (Pro) | Free (Open Source core) | Free / Open Source | Free / Open Source |

## VS Code

As of 2026, we recommend using VS Code. We do not have a tutorial for it, but if you like to contribute one, let us know.

## PyCharm

PyCharm is an Integrated Development Environment (IDE) used for programming in Python. It provides code analysis, a graphical debugger, an integrated unit tester, and integration with git.

[![Video](../../assets/images/video.png) Python 8:56 PyCharm](https://youtu.be/X8ZpbZweJcw)

## Python in 45 minutes

Next is an additional community YouTube video about the Python programming language. Naturally, there are many alternatives to this video, but it is probably a good start. It also uses PyCharm which we recommend.

[![Video](../../assets/images/video.png) Python 43:16 PyCharm](https://www.youtube.com/watch?v=N4mEzFDjqtA) (Link to an external presentation from Derek Banas)

How much you want to understand Python is a bit up to you. While it is good to know classes and inheritance, you may be able to get away without using it for this class. However, we do recommend that you learn it.

PyCharm Installation:

Method 1: Download and install it from the PyCharm website. This is easy and if no automated install is required we recommend this method. Students and teachers can apply for a free professional version. Please note that Jupyter notebooks can only be viewed in the professional version.

Method 2: PyCharm Installation on Ubuntu using umake

``` bash
$ sudo add-apt-repository ppa:ubuntu-desktop/ubuntu-make
$ sudo apt-get update
$ sudo apt-get install ubuntu-make
```

Once the `umake` command is installed, use the next command to install PyCharm Community Edition:

``` bash
$ umake ide pycharm
```

If you want to remove PyCharm installed using the umake command, use this:

``` bash
$ umake -r ide pycharm
```

Method 2: PyCharm installation on Ubuntu using PPA

``` bash
$ sudo add-apt-repository ppa:mystic-mirage/pycharm
$ sudo apt-get update
$ sudo apt-get install pycharm-community
```

PyCharm also has a Professional (paid) version that can be installed using the following command:

``` bash
$ sudo apt-get install pycharm
```

Once installed, go to your VM dashboard and search for PyCharm.