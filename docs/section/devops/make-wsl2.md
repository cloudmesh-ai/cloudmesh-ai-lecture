# Make for WSL2

## Learning Objectives

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    * Understand the utility of using a Makefile to manage Windows Subsystem for Linux (WSL2) distributions.
    * Configure a Makefile to target specific WSL2 distributions.
    * Perform lifecycle operations including starting, stopping, exporting, and importing WSL2 instances.
    * Execute arbitrary shell commands within a WSL2 environment using standardized `make` targets.

## Overview

Managing Windows Subsystem for Linux (WSL2) typically involves interacting with the `wsl.exe` binary via the command line. While the native toolset is capable, common operations—such as exporting a distribution for backup or running a specific command across different distros—often require long, repetitive flags.

This chapter introduces a specialized Makefile designed to wrap `wsl.exe` commands. By defining these actions as `make` targets, WSL2 management becomes repeatable, version-controllable, and composable. This approach allows developers to keep their environment configuration alongside their source code, ensuring that all team members utilize the same distribution management patterns.

## The WSL2 Management Makefile

The following Makefile provides a structured interface for the most frequent WSL2 operations.

```make
# ==============================================================
# Makefile – WSL 2 management
# ==============================================================

# --------------------------------------------------------------
# Configuration – edit these to suit your environment
# --------------------------------------------------------------
# Full path to the Windows "wsl.exe" command. On a standard
# installation the shortcut works, but on some systems you may
# need to point to the real binary (e.g. C:\Windows\System32\wsl.exe)
WSL        ?= wsl

# The default distribution to operate on when a target does not
# receive an explicit DISTRO argument.
# You can discover the available names with `make list`.
DEFAULT_DISTRO ?= Ubuntu-22.04

# Where you keep exported *.tar files (used by import/export)
EXPORT_DIR ?= wsl-exports

# --------------------------------------------------------------
# Internal helpers
# --------------------------------------------------------------
# Ensure the export directory exists before we try to write files.
$(EXPORT_DIR):
	@mkdir -p $@

# Wrapper to call wsl.exe with the correct distro (if provided)
# Usage: $(call wsl_cmd, <subcommand>) – the subcommand may contain $DISTRO
define wsl_cmd
	$(WSL) $(1)
endef

# --------------------------------------------------------------
# Public (phony) targets
# --------------------------------------------------------------
.PHONY: list start stop terminate default export import \
        run config clean clean-exports help

# -----------------------------------------------------------------
# 1. Basic inspection
# -----------------------------------------------------------------
list:
	@echo "=== Installed WSL distributions ==="
	@$(call wsl_cmd,--list --verbose)

status:
	@echo "=== Running WSL instances ==="
	@$(call wsl_cmd,--list --running)

# -----------------------------------------------------------------
# 2. Lifecycle control
# -----------------------------------------------------------------
# Start a distro (or the default one)
#   make start          – starts DEFAULT_DISTRO
#   make start DISTRO=Debian
start:
	@$(call wsl_cmd,--distribution $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) --exec true)
	@echo "Started $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO))"

# Stop a running distro (graceful shutdown)
#   make stop          – stops DEFAULT_DISTRO
#   make stop DISTRO=Debian
stop:
	@$(call wsl_cmd,--terminate $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) && \
	    echo "Stopped $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO))")

# Force-terminate (same as stop, kept for symmetry)
terminate: stop

# -----------------------------------------------------------------
# 3. Export / Import (distribution snapshots)
# -----------------------------------------------------------------
# Export the current state of a distro to a tarball.
#   make export                – exports DEFAULT_DISTRO
#   make export DISTRO=Debian  – exports Debian
export: $(EXPORT_DIR)
	@TAR=$(EXPORT_DIR)/$(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)).tar
	@echo "Exporting $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) -> $$TAR"
	@$(call wsl_cmd,--export $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) $$TAR)
	@echo "Export finished"

# Import a previously exported tarball as a new distro.
#   make import NEWNAME=MyUbuntu FILE=wsl-exports/Ubuntu-22.04.tar
import:
	@if [ -z "$(NEWNAME)" ] || [ -z "$(FILE)" ]; then \
	    echo "ERROR: NEWNAME and FILE variables are required."; \
	    echo "   Example: make import NEWNAME=MyUbuntu FILE=wsl-exports/Ubuntu-22.04.tar"; \
	    exit 1; \
	fi
	@echo "Importing $$FILE as distro $(NEWNAME)"
	@$(call wsl_cmd,--import $(NEWNAME) . $$FILE)
	@echo "Import finished – you can now use $(NEWNAME)"

# -----------------------------------------------------------------
# 4. Set the default distro (the one that runs when you type just "wsl")
# -----------------------------------------------------------------
default:
	@$(call wsl_cmd,--set-default $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)))
	@echo "$(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) is now the default WSL distro"

# -----------------------------------------------------------------
# 5. Run an arbitrary command inside a distro
# -----------------------------------------------------------------
#   make run CMD="ls -la ~"
#   make run DISTRO=Debian CMD="apt update && apt upgrade -y"
run:
	@$(if $(CMD),,$(error CMD variable is required. Example: make run CMD="ls -l"))
	@echo "Running command in $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)):"
	@$(call wsl_cmd,--distribution $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) --exec sh -c '$(CMD)')

# -----------------------------------------------------------------
# 6. Show current WSL configuration (global options)
# -----------------------------------------------------------------
config:
	@$(call wsl_cmd,--status)

# -----------------------------------------------------------------
# 7. Housekeeping
# -----------------------------------------------------------------
clean: clean-exports
	@echo "Cleaned generated artefacts."

clean-exports:
	@echo "Removing exported tarballs..."
	@rm -rf $(EXPORT_DIR)
	@echo "Export directory removed."

# -----------------------------------------------------------------
# 8. Help – prints a tidy usage summary
# -----------------------------------------------------------------
help:
	@echo "=== WSL 2 Makefile – quick reference ==="
	@echo ""
	@echo "Variables (override on the command line):"
	@echo "  DISTRO          – target distribution name (default: $(DEFAULT_DISTRO))"
	@echo "  CMD             – command string for the 'run' target"
	@echo "  NEWNAME         – name for a new imported distro (import target)"
	@echo "  FILE            – path to a .tar file to import (import target)"
	@echo "  EXPORT_DIR      – directory where exports are stored (default: $(EXPORT_DIR))"
	@echo ""
	@echo "Targets:"
	@echo "  make list               – list all installed WSL distros"
	@echo "  make status             – show which distros are currently running"
	@echo "  make start [DISTRO=...] – start a distro (default: $(DEFAULT_DISTRO))"
	@echo "  make stop  [DISTRO=...] – stop a running distro"
	@echo "  make default [DISTRO=...] – set the default distro"
	@echo "  make export [DISTRO=...] – export distro to $(EXPORT_DIR)/<name>.tar"
	@echo "  make import NEWNAME=... FILE=... – import a tarball as a new distro"
	@echo "  make run DISTRO=... CMD=\"...\" – run an arbitrary command inside a distro"
	@echo "  make config             – show global WSL configuration"
	@echo "  make clean              – delete exported tarballs"
	@echo "  make help               – display this help"
	@echo ""
	@echo "Examples:"
	@echo "  make start                     # starts the default distro"
	@echo "  make start DISTRO=Debian       # starts Debian"
	@echo "  make export DISTRO=Ubuntu-22.04"
	@echo "  make import NEWNAME=MyUbuntu FILE=wsl-exports/Ubuntu-22.04.tar"
	@echo "  make run CMD=\"uname -a\"       # runs inside the default distro"
	@echo ""
	@echo "Tip: combine targets in a single invocation, e.g."
	@echo "  make stop start                # restarts the default distro"
```

### Installation and Setup

To use the Makefile in a Windows environment:

1. **Save the File**: Create a file named `Makefile` (no extension) in your project root or a dedicated WSL management folder.
2. **Environment**: Open a Windows Command Prompt or PowerShell window in that directory.
3. **Execution**: Run `make help` to verify the installation and view the available targets.

### Using the Makefile

The Makefile organizes WSL2 operations into logical groups.

#### Basic Inspection
The `list` and `status` targets provide visibility into the installed distributions and their current state.
* `make list`: Shows all installed distributions and their version.
* `make status`: Shows which distributions are currently running.

#### Lifecycle Control
Use `start` and `stop` to manage the execution state of your instances.
* `make start`: Launches the distribution defined in `DEFAULT_DISTRO`.
* `make stop`: Terminates the running instance.
* Overriding: Use `DISTRO=Name` to target a specific instance (e.g., `make stop DISTRO=Debian`).

#### Distribution Snapshots
The `export` and `import` targets facilitate backups and environment cloning.
* `make export`: Saves the current state of a distribution to a `.tar` file in the `EXPORT_DIR`.
* `make import`: Creates a new distribution from an existing tarball using `NEWNAME` and `FILE` variables.

#### Configuration and Execution
* `make default`: Sets the specified distribution as the system-wide default for the `wsl` command.
* `make run`: Executes a specific shell command inside the distribution using the `CMD` variable.
* `make config`: Displays the global WSL status and configuration.

### Common Workflow Examples

| Goal | Command |
|------|---------|
| List all installed WSL distros | `make list` |
| See which distros are currently running | `make status` |
| Start the default Ubuntu-22.04 distro | `make start` |
| Start a specific distro (Debian) | `make start DISTRO=Debian` |
| Stop the default distro | `make stop` |
| Export the default distro to a tarball | `make export` |
| Export a named distro | `make export DISTRO=Debian` |
| Import a tarball as a new distro | `make import NEWNAME=MyDebian FILE=wsl-exports/Debian.tar` |
| Run a shell command inside the default distro | `make run CMD="ls -la ~"` |
| Set a distro as the system-wide default | `make default DISTRO=Debian` |
| Show the global WSL configuration | `make config` |
| Clean all exported tarballs | `make clean` |

### Advantages of the Makefile Approach

Using a Makefile for WSL2 management provides several technical advantages over raw CLI usage:

* **Version Control**: The Makefile can be stored in a Git repository, ensuring consistent environment management across a development team.
* **Idempotency**: By defining targets and dependencies, `make` prevents redundant operations.
* **Parameterization**: Command-line variable overrides (`DISTRO=...`) allow a single Makefile to manage multiple diverse distributions.
* **Composability**: Targets can be chained (e.g., `make stop start`) to perform complex sequences like restarting an environment in a single command.

## Summary Checklist

* [ ] Successfully saved the Makefile in a project root.
* [ ] Listed installed WSL distributions using `make list`.
* [ ] Started and stopped a specific distribution.
* [ ] Exported a distribution to a tarball.
* [ ] Ran a shell command using `make run`.

## Assignments

!!! note "Assignment.1: Basic Setup"
    Save the provided Makefile in a new directory and execute `make help` from a Windows terminal to verify the targets.
    ??? tip "Solution: Basic Setup"
        The output should display the "WSL 2 Makefile – quick reference" section with a list of variables and targets.

!!! note "Assignment.2: Distribution Management"
    Start the default distribution, verify it is running using `make status`, and then terminate it using `make stop`.
    ??? tip "Solution: Distribution Management"
        Sequence: `make start` $\rightarrow$ `make status` $\rightarrow$ `make stop`.

!!! note "Assignment.3: Snapshotting"
    Export the current default distribution to a tarball, then import that tarball as a new distribution named `WSL-Backup`.
    ??? tip "Solution: Snapshotting"
        Sequence: `make export` $\rightarrow$ `make import NEWNAME=WSL-Backup FILE=wsl-exports/<distro-name>.tar`.

## References

* Microsoft WSL Documentation: https://learn.microsoft.com/en-us/windows/wsl/
* GNU Make Manual: https://www.gnu.org/software/make/manual/

## Self-Evaluation

??? note "What is the purpose of the DISTRO variable in the Makefile?"
    The `DISTRO` variable allows the user to override the `DEFAULT_DISTRO` on the command line, enabling the same `make` targets to operate on different WSL2 distributions.

??? note "How does the `make export` target handle the storage of the distribution snapshot?"
    It ensures the `EXPORT_DIR` exists and saves the distribution as a `.tar` file named after the distribution being exported.

??? note "How can you execute a specific Linux command, such as `uname -a`, without entering the WSL shell interactively?"
    By using the `run` target with the `CMD` variable: `make run CMD="uname -a"`.
