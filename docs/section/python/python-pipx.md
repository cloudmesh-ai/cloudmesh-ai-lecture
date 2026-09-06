# Managing OpenStack and Cloudmesh AI Environments

This guide explains how to run the OpenStack CLI and develop `cloudmesh-ai-llm` on the same machine without causing dependency conflicts.

---

## Why use both `pipx` and `pyenv`?

You might wonder why we don't just install everything into one environment. The reason is **dependency collision**.

### 1. `pipx` for OpenStack CLI
OpenStack's command-line tools are "applications," not libraries you import into your own code. They have a very large and specific set of dependencies (like `oslo.config`, `keystoneauth1`, and specific versions of `cryptography`). If you install these globally or in your dev environment, they often force other packages to downgrade or upgrade, breaking your own project. 

`pipx` solves this by installing each application in its own private virtual environment while still making the command (e.g., `openstack`) available globally.

### 2. `pyenv` for Cloudmesh-AI-LLM
Since you are developing `cloudmesh-ai-llm`, you need a **development environment**. This requires a specific Python version and the ability to install your project in "editable mode" (`pip install -e .`). This allows you to change the code and see the results immediately without reinstalling. 

A `pyenv` environment (or a standard `venv`) is the industry standard for this because it keeps your project's specific library requirements isolated from the rest of the system.

By splitting them, you get the best of both worlds: a globally available OpenStack tool and a clean, stable development workspace for your AI project.

---

## Installation Guide

Follow these steps to set up your environment correctly.

### Step 1: Install OpenStack Globally via `pipx`
This installs the OpenStack client as a global command while keeping its heavy dependencies completely isolated.

```bash
# Install pipx (if you haven't already)
brew install pipx
pipx ensurepath

# Install the OpenStack client globally
pipx install python-openstackclient
```
*Now, the `openstack` command will work globally in any terminal window.*

### Step 2: Clean Your Pyenv Environment
Clear out any leftover package conflicts from previous attempts in your default pyenv environment:

```bash
# Replace 3.14.4 with your current pyenv version if different
rm -rf ~/.pyenv/versions/3.14.4/lib/python3.14/site-packages/~*
```

### Step 3: Setup Cloudmesh-AI-LLM in Pyenv
Navigate to your project directory and install your package in editable mode:

```bash
# Go to your project folder
cd ~/work/cloudmesh-ai-llm

# Ensure your pyproject.toml has the textual fix we made earlier, then install:
pip install -e .
```

---

## You're All Set!

* **OpenStack** is now available anywhere in your terminal just by typing `openstack`.
* **Cloudmesh** runs locally inside your `pyenv` setup, and any code changes you make will instantly apply via editable mode (`-e .`).
