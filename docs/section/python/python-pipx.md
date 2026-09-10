# Managing Python Environments with pipx and pyenv

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Differentiate between application-level and library-level Python installations.
    - Utilize `pipx` to install global command-line tools without inducing dependency conflicts.
    - Configure a stable development environment using `pyenv` and editable installations.
    - Resolve common dependency collisions in mixed-use Python environments.
    - Implement a workflow that allows simultaneous use of heavy CLI tools and custom project development.

In the Python ecosystem, managing dependencies is a critical operational challenge. When multiple tools share the same global environment, "dependency collision" often occurs—a state where two different packages require different versions of the same library. For example, a cloud management tool might require an older version of a cryptography library, while a modern AI framework requires a newer one. Installing both globally typically results in one package breaking the other.

Professional Python development requires a strategic separation of concerns. Instead of a single environment, engineers employ different isolation strategies based on whether the software is being used as a standalone application or developed as a library.

## Understanding Dependency Collisions

A dependency collision occurs when the Python package manager (`pip`) is forced to choose between conflicting version requirements for a shared dependency. In a global installation, only one version of a library can exist at a time.

### Application vs. Library Dependencies

There is a fundamental distinction between how tools are used:

1. **Applications**: These are standalone tools designed to be executed from the command line (e.g., the OpenStack CLI). They have a fixed set of dependencies required for the tool to function but are not intended to be imported into other Python scripts.
2. **Libraries**: These are packages intended to be imported into a project's code (e.g., `cloudmesh-ai-llm`). The developer must manage these dependencies carefully to ensure compatibility with other libraries in the project.

When an application like the OpenStack client is installed globally, its large and specific dependency tree (including packages like `oslo.config` and `keystoneauth1`) can force other libraries to downgrade, effectively breaking any development projects on the same machine.

## Application Isolation with pipx

`pipx` is a tool designed specifically for installing and running Python applications in isolated environments while keeping their binaries available globally.

### How pipx Works

Unlike `pip`, which installs packages into the current environment, `pipx` performs the following actions for every application:
1. Creates a dedicated, private virtual environment for the application.
2. Installs the application and its specific dependencies into that private environment.
3. Symlinks the application's binary (the executable) to a global path (e.g., `~/.local/bin`).

This ensures that the OpenStack CLI's dependencies never interact with the libraries used by other projects, eliminating the risk of collision.

## Development Environments with pyenv

While `pipx` is ideal for applications, it is unsuitable for development. When building a project like `cloudmesh-ai-llm`, developers need a flexible environment where they can modify code and immediately test the results.

### Version Management and Editable Installs

`pyenv` allows engineers to switch between different Python versions seamlessly, ensuring that the project runs on the exact version it was designed for. 

A critical feature of development environments is the "editable install" (using the `-e` flag). Instead of copying files to the `site-packages` directory, an editable install creates a link to the project's source code. Any change made to the `.py` files is reflected immediately in the environment without requiring a re-installation.

## Implementation Guide

The following steps provide a standardized workflow for setting up a machine to run the OpenStack CLI and develop `cloudmesh-ai-llm` simultaneously.

### Step 1: Install OpenStack via pipx

This process installs the OpenStack client as a global command while isolating its heavy dependencies.

```bash
# Install pipx via Homebrew
brew install pipx

# Ensure pipx binaries are in the system PATH
pipx ensurepath

# Install the OpenStack client globally
pipx install python-openstackclient
```

After execution, the `openstack` command is available in any terminal session, regardless of the active Python environment.

### Step 2: Clean the pyenv Environment

Before setting up the development project, it is necessary to remove any leftover package conflicts from previous global installation attempts.

```bash
# Replace 3.14.4 with your active pyenv version
rm -rf ~/.pyenv/versions/3.14.4/lib/python3.14/site-packages/~*
```

This step ensures a "clean slate" for the project dependencies, preventing legacy conflicts from interfering with the editable install.

### Step 3: Setup Cloudmesh-AI-LLM in pyenv

Navigate to the project root and install the package in editable mode.

```bash
# Navigate to the project directory
cd ~/work/cloudmesh-ai-llm

# Install the project and its dependencies in editable mode
pip install -e .
```

By using `-e .`, the `cloudmesh-ai-llm` package is linked to the current directory. Modifications to the source code will take effect instantly.

!!! tip "Summary Checklist"

    - [ ] Installed `pipx` and configured the system PATH.
    - [ ] Installed `python-openstackclient` using `pipx` to isolate dependencies.
    - [ ] Verified that the `openstack` command works globally.
    - [ ] Cleaned the `pyenv` site-packages directory to remove conflicts.
    - [ ] Performed an editable install (`pip install -e .`) for the development project.
    - [ ] Confirmed that code changes are reflected without re-installation.

!!! note "Exercise 1: Application Isolation"

    **Task**: Use `pipx` to install a common Python-based CLI tool (e.g., `black` or `httpie`). Verify that the tool is available globally but that its dependencies are not visible in your current `pyenv` or global `pip list`.
    **Goal**: Confirm the isolation mechanism of `pipx`.

!!! note "Exercise 2: OpenStack CLI Setup"

    **Task**: Install the `python-openstackclient` using the steps in this chapter. Run `openstack --version` to verify installation, then check if `oslo.config` is present in your project's `pip list`.
    **Goal**: Verify that the application is functional while remaining isolated from the development environment.

!!! note "Exercise 3: Editable Mode Verification"

    **Task**: In the `cloudmesh-ai-llm` project, add a simple print statement to one of the main functions. Execute the tool and verify the print statement appears without running `pip install` again.
    **Goal**: Demonstrate the efficiency of editable installs for rapid development.
