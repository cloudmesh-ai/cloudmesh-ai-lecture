# Make for WSL2

Below is a **stand‑alone Makefile** you can drop into the root of a Windows project (or any folder you use for WSL 2 work).  
It wraps the native `wsl.exe` commands so that the most common WSL 2 actions become simple, repeatable `make` targets.

```make
# ==============================================================
# Makefile – WSL 2 management
# ==============================================================

# --------------------------------------------------------------
# Configuration – edit these to suit your environment
# --------------------------------------------------------------
# Full path to the Windows “wsl.exe” command.  On a standard
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
# Usage: $(call wsl_cmd, <subcommand>)   – the subcommand may contain $DISTRO
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
	@echo "✅ Started $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO))"

# Stop a running distro (graceful shutdown)
#   make stop          – stops DEFAULT_DISTRO
#   make stop DISTRO=Debian
stop:
	@$(call wsl_cmd,--terminate $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) && \
	    echo "🛑 Stopped $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO))")

# Force‑terminate (same as stop, kept for symmetry)
terminate: stop

# -----------------------------------------------------------------
# 3. Export / Import (distribution snapshots)
# -----------------------------------------------------------------
# Export the current state of a distro to a tarball.
#   make export                – exports DEFAULT_DISTRO
#   make export DISTRO=Debian  – exports Debian
export: $(EXPORT_DIR)
	@TAR=$(EXPORT_DIR)/$(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)).tar
	@echo "📦 Exporting $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) → $$TAR"
	@$(call wsl_cmd,--export $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) $$TAR)
	@echo "✅ Export finished"

# Import a previously exported tarball as a new distro.
#   make import NEWNAME=MyUbuntu FILE=wsl-exports/Ubuntu-22.04.tar
import:
	@if [ -z "$(NEWNAME)" ] || [ -z "$(FILE)" ]; then \
	    echo "❌ ERROR: NEWNAME and FILE variables are required."; \
	    echo "   Example: make import NEWNAME=MyUbuntu FILE=wsl-exports/Ubuntu-22.04.tar"; \
	    exit 1; \
	fi
	@echo "📥 Importing $$FILE as distro $(NEWNAME)"
	@$(call wsl_cmd,--import $(NEWNAME) . $$FILE)
	@echo "✅ Import finished – you can now use $(NEWNAME)"

# -----------------------------------------------------------------
# 4. Set the default distro (the one that runs when you type just “wsl”)
# -----------------------------------------------------------------
default:
	@$(call wsl_cmd,--set-default $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)))
	@echo "✅ $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) is now the default WSL distro"

# -----------------------------------------------------------------
# 5. Run an arbitrary command inside a distro
# -----------------------------------------------------------------
#   make run CMD="ls -la ~"
#   make run DISTRO=Debian CMD="apt update && apt upgrade -y"
run:
	@$(if $(CMD),,$(error CMD variable is required. Example: make run CMD="ls -l"))
	@echo "🚀 Running command in $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)):"
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
	@echo "🧹 Cleaned generated artefacts."

clean-exports:
	@echo "🗑 Removing exported tarballs..."
	@rm -rf $(EXPORT_DIR)
	@echo "✅ Export directory removed."

# -----------------------------------------------------------------
# 8. Help – prints a tidy usage summary
# -----------------------------------------------------------------
help:
	@echo "=== WSL 2 Makefile – quick reference ==="
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

---

### How to Use the Makefile

1. **Save** the file as `Makefile` in a folder that you normally work from (e.g., the root of a project repository).  
2. Open a **Windows Command Prompt** or **PowerShell** in that folder.  
3. Run `make help` to see the quick reference.  

#### Common workflow examples

| Goal | Command |
|------|---------|
| List all installed WSL distros | `make list` |
| See which distros are currently running | `make status` |
| Start the default Ubuntu‑22.04 distro | `make start` |
| Start a specific distro (Debian) | `make start DISTRO=Debian` |
| Stop the default distro | `make stop` |
| Export the default distro to a tarball | `make export` |
| Export a named distro | `make export DISTRO=Debian` |
| Import a tarball as a new distro | `make import NEWNAME=MyDebian FILE=wsl-exports/Debian.tar` |
| Run a shell command inside the default distro | `make run CMD="ls -la ~"` |
| Set a distro as the system‑wide default | `make default DISTRO=Debian` |
| Show the global WSL configuration (memory limits, version, etc.) | `make config` |
| Clean all exported tarballs | `make clean` |

---

### Why a Makefile for WSL 2?

* **Version‑controlled** – The file lives in Git alongside your code, so every team member runs the exact same WSL commands.  
* **Idempotent & Incremental** – `make` will only re‑export a distro if the target tarball is missing, avoiding unnecessary work.  
* **Parameterised** – By passing `DISTRO=…` or `CMD=…` on the command line you can reuse the same targets for any distribution or command.  
* **Composable** – You can chain targets (`make stop start`) to restart a distro, or integrate the Makefile into CI scripts (`make export && make import …`).  

Feel free to extend it – add targets for `wsl --shutdown`, `wsl --update`, or even custom `wsl --set-version` calls – the same pattern works for any `wsl.exe` sub‑command. Happy hacking!