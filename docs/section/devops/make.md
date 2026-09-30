
---

# Makefiles and Cloud‑VM Management  


!!! info "Learning Objectives"

    By the end of this chapter you should be able to:

    1. **Describe** the purpose of a Makefile and explain how `make` decides which commands to run.  
    2. **Identify** the main components of a Makefile: targets, prerequisites, recipes, variables, and phony declarations.  
    3. **Write** a simple Makefile that builds a C program using pattern rules and automatic variables.  
    4. **Create** reusable variables and pattern rules to avoid duplication in larger projects.  
    5. **Apply** Makefile concepts to non‑compilation tasks, specifically to manage virtual machines with the Multipass CLI.  
    6. **Construct** a Makefile that drives OpenStack CLI commands for common VM lifecycle operations (create, start, stop, delete, status).  
    7. **Construct** a Makefile to manage WSL2 distributions, including lifecycle operations and snapshotting.
    8. **Employ** best‑practice techniques such as phony targets, safety guards for destructive actions, and clear documentation within the Makefile.  
    9. **Adapt** the Makefile to different environments by overriding variables on the command line.  
    10. **Organise** multiple, related Makefiles in a coherent directory hierarchy and drive them from a single top‑level Makefile.  


## 1. What a Makefile Is  

A **Makefile** is a plain‑text script interpreted by the `make` utility. Its purpose is to describe *what* must be built (the **targets**) and *how* to build it (the **recipes**). When `make` is invoked it:

1. Reads the dependency graph defined by targets and their prerequisites.  
2. Checks timestamps: a target is out‑of‑date if it does not exist or any prerequisite is newer.  
3. Executes the minimal set of recipes needed to bring the target up‑to‑date.

!!! info "Why this matters"
    In AI and Data Science, workflows often consist of a series of fragile, interdependent steps: downloading a dataset, preprocessing it, training a model, and then evaluating it. If the dataset is 100GB, you cannot afford to re-download it every time you tweak a hyperparameter. `make` provides a lightweight way to track these dependencies, ensuring that only the steps that *actually* need to change are re-run, saving hours of compute time and storage costs.

Although Make was devised for compiling C programs, the same model works for any repeatable command‑line workflow, making it a lightweight "task runner" for DevOps, documentation generation, container orchestration, and cloud‑VM management.

---

## 2. Core Syntax  

```
target : prerequisite‑1 prerequisite‑2 …
<TAB>recipe line 1
<TAB>recipe line 2
…
```

* **Target** – a file name or a symbolic name.  
* **Prerequisites** – files that must exist and be newer than the target; otherwise the recipe is run.  
* **Recipe** – one or more shell commands. **Each command line must start with a TAB**; using spaces will cause a syntax error.  

If a target does not correspond to a real file (e.g., `clean`), declare it **phony** (see § 4) so `make` never treats the name as an existing file.

---

## 3. Variables  

Variables avoid repetition and make the Makefile easy to adapt.

```make
CC      = gcc
CFLAGS  = -Wall -O2
SRC     = main.c utils.c
OBJ     = $(SRC:.c=.o)          # .c → .o substitution
TARGET  = myprog
```

Reference a variable with `$(NAME)`. By default variables are expanded **when the recipe runs** (lazy expansion). Use `:=` for immediate expansion if needed.

---

## 4. Phony Targets  

A **phony** target never represents an actual file. Declaring it as phony prevents `make` from skipping the recipe when a file of the same name exists.

```make
.PHONY: all clean test install
```

---

## 5. Pattern Rules and Automatic Variables  

Pattern rules let one recipe handle many similar targets.

```make
%.o : %.c
        $(CC) $(CFLAGS) -c $< -o $@
```

Automatic variables:

| Symbol | Meaning |
|--------|---------|
| `$@`   | Target name |
| `$<`   | First prerequisite |
| `$^`   | All prerequisites (space‑separated) |
| `$?`   | Prerequisites newer than the target |
| `$*`   | Stem matched by `%` |

These make recipes concise and portable.

---

## 6. A Fully Working Build Example  

```make
# -------------------------------------------------
# Simple C program build
# -------------------------------------------------

# --- Variables -------------------------------------------------
CC      := gcc
CFLAGS  := -Wall -O2
SRC     := main.c foo.c bar.c
OBJ     := $(SRC:.c=.o)
TARGET  := myapp

# --- Default target --------------------------------------------
all: $(TARGET)

# --- Linking ----------------------------------------------------
$(TARGET): $(OBJ)
        $(CC) -o $@ $^

# --- Compilation (pattern rule) ---------------------------------
%.o: %.c
        $(CC) $(CFLAGS) -c $< -o $@

# --- Convenience targets ----------------------------------------
.PHONY: clean run
clean:
        rm -f $(OBJ) $(TARGET)

run: $(TARGET)
        ./$(TARGET)
```

`make` builds the binary, `make clean` removes generated files, and `make run` compiles (if necessary) and executes the program.

---

## 7. Managing Multipass VMs with Make  

**Multipass** is a lightweight VM manager for Ubuntu. A Makefile can wrap its CLI commands.

```make
# -------------------------------------------------
# Multipass VM lifecycle – Makefile
# -------------------------------------------------

# ---- Configuration -------------------------------------------------
INSTANCE ?= dev‑vm          # overridable on the command line
IMAGE    ?= 22.04           # Ubuntu LTS release
CPU      ?= 2
MEMORY   ?= 2G
DISK     ?= 20G

MP      = multipass        # shortcut

# ---- Phony targets -------------------------------------------------
.PHONY: list launch start stop delete status shell

list:
        @$(MP) list

launch:
        @$(MP) launch $(IMAGE) \
                --name $(INSTANCE) \
                --cpus $(CPU) \
                --mem $(MEMORY) \
                --disk $(DISK) && \
        echo "Instance $(INSTANCE) launched."

start:
        @$(MP) start $(INSTANCE) && \
        echo "Instance $(INSTANCE) started."

stop:
        @$(MP) stop $(INSTANCE) && \
        echo "Instance $(INSTANCE) stopped."

delete:
        @$(MP) delete $(INSTANCE) && \
        $(MP) purge && \
        echo "Instance $(INSTANCE) deleted and purged."

status:
        @$(MP) info $(INSTANCE)

shell:
        @$(MP) exec $(INSTANCE) -- bash
```

Typical usage:

| Command | Effect |
|---------|--------|
| `make list`   | Shows all Multipass instances. |
| `make launch` | Boots a fresh Ubuntu VM. |
| `make start`  | Starts a stopped VM. |
| `make stop`   | Stops a running VM. |
| `make delete` | Removes the VM and frees its resources. |
| `make status` | Prints IP, state, and resources. |
| `make shell`  | Opens an interactive shell inside the VM. |

Override variables on the command line, e.g. `make INSTANCE=test‑node CPU=4 MEMORY=8G launch`.

---

## 8. Controlling OpenStack VMs with Make  

Assumes an OpenStack RC file (`cloudrc.sh`) that exports the required `OS_` variables.

TODO: use clouds.yaml
    We should prefer using clouds.yaml. modify accordingly. it has jetsream: and openstack: in it 

```make
# -------------------------------------------------
# OpenStack VM control – Makefile
# -------------------------------------------------

# ---- Configuration -------------------------------------------------
SERVER_NAME ?= demo‑vm                 # name or UUID
IMAGE       ?= ubuntu‑22.04
FLAVOR      ?= m1.small
NET         ?= private
RCFILE      ?= ~/.config/openstack/cloudrc.sh           # file that exports OS_ vars

# Helper: source RC before each command
OS_CMD = . $(RCFILE) &&

# ---- Phony targets -------------------------------------------------
.PHONY: status start stop delete create

status:
        @$(OS_CMD) openstack server show $(SERVER_NAME) -f value -c status \
        || echo "Server $(SERVER_NAME) not found."

start:
        @$(OS_CMD) openstack server start $(SERVER_NAME) && \
        echo "Start request sent for $(SERVER_NAME)."

stop:
        @$(OS_CMD) openstack server stop $(SERVER_NAME) && \
        echo "Stop request sent for $(SERVER_NAME)."

delete:
        @$(OS_CMD) openstack server delete $(SERVER_NAME) && \
        echo "Deletion request sent for $(SERVER_NAME)."

create:
        @$(OS_CMD) openstack server create \
                --image $(IMAGE) \
                --flavor $(FLAVOR) \
                --network $(NET) \
                $(SERVER_NAME) && \
        echo "Server $(SERVER_NAME) creation requested."
```

Typical usage:

| Command | Effect |
|---------|--------|
| `make status` | Prints current state (`ACTIVE`, `SHUTOFF`, …). |
| `make start`  | Starts the server. |
| `make stop`   | Stops the server. |
| `make delete` | Deletes the server. |
| `make create` | Boots a new instance with the supplied image, flavor, and network. |

Override variables on the CLI, e.g. `make SERVER_NAME=web‑01 start`.

---

## 9. Managing WSL2 Distributions with Make

!!! info "Learning Objectives"
    By the end of this section, you will be able to:
    * Understand the utility of using a Makefile to manage Windows Subsystem for Linux (WSL2) distributions.
    * Configure a Makefile to target specific WSL2 distributions.
    * Perform lifecycle operations including starting, stopping, exporting, and importing WSL2 instances.
    * Execute arbitrary shell commands within a WSL2 environment using standardized `make` targets.

Managing Windows Subsystem for Linux (WSL2) can be streamlined by wrapping `wsl.exe` commands in a Makefile. This allows for repeatable, version-controlled management of distribution lifecycles, including starting, stopping, exporting for backup, and executing arbitrary commands within specific distributions.

For a comprehensive guide and the complete management Makefile, see [Make for WSL2](/section/cloud/platforms/local/wsl2.md).

---

## 10. Detailed Use Case: Managing WSL2 Distributions with Make

Managing Windows Subsystem for Linux (WSL2) typically involves interacting with the `wsl.exe` binary via the command line. While the native toolset is capable, common operations—such as exporting a distribution for backup or running a specific command across different distros—often require long, repetitive flags.

A specialized Makefile can wrap `wsl.exe` commands. By defining these actions as `make` targets, WSL2 management becomes repeatable, version-controllable, and composable. This approach allows developers to keep their environment configuration alongside their source code, ensuring that all team members utilize the same distribution management patterns.

### Installation and Setup

To use the Makefile in a Windows environment:
1. **Save the File**: Create a file named `Makefile` (no extension) in your project root or a dedicated WSL management folder.
2. **Environment**: Open a Windows Command Prompt or PowerShell window in that directory.
3. **Execution**: Run `make help` to verify the installation and view the available targets.

### The WSL2 Management Makefile

The following Makefile provides a structured interface for the most frequent WSL2 operations.

```make
# -------------------------------------------------
# Makefile – WSL 2 management
# -------------------------------------------------

# ---- Configuration -------------------------------------------------
WSL            ?= wsl
DEFAULT_DISTRO ?= Ubuntu-22.04
EXPORT_DIR     ?= wsl-exports

# ---- Internal helpers ----------------------------------------------
$(EXPORT_DIR):
	@mkdir -p $@

define wsl_cmd
	$(WSL) $(1)
endef

# ---- Phony targets -------------------------------------------------
.PHONY: list start stop terminate default export import \
        run config clean clean-exports help

list:
	@echo "=== Installed WSL distributions ==="
	@$(call wsl_cmd,--list --verbose)

status:
	@echo "=== Running WSL instances ==="
	@$(call wsl_cmd,--list --running)

start:
	@$(call wsl_cmd,--distribution $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) --exec true)
	@echo "Started $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO))"

stop:
	@$(call wsl_cmd,--terminate $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) && \
	    echo "Stopped $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO))")

terminate: stop

export: $(EXPORT_DIR)
	@TAR=$(EXPORT_DIR)/$(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)).tar
	@echo "Exporting $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) -> $$TAR"
	@$(call wsl_cmd,--export $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) $$TAR)
	@echo "Export finished"

import:
	@if [ -z "$(NEWNAME)" ] || [ -z "$(FILE)" ]; then \
	    echo "ERROR: NEWNAME and FILE variables are required."; \
	    exit 1; \
	fi
	@echo "Importing $$FILE as distro $(NEWNAME)"
	@$(call wsl_cmd,--import $(NEWNAME) . $$FILE)
	@echo "Import finished"

default:
	@$(call wsl_cmd,--set-default $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)))
	@echo "$(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) is now the default WSL distro"

run:
	@$(if $(CMD),,$(error CMD variable is required. Example: make run CMD="ls -l"))
	@echo "Running command in $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)):"
	@$(call wsl_cmd,--distribution $(if $(DISTRO),$(DISTRO),$(DEFAULT_DISTRO)) --exec sh -c '$(CMD)')

config:
	@$(call wsl_cmd,--status)

clean: clean-exports
	@echo "Cleaned generated artefacts."

clean-exports:
	@rm -rf $(EXPORT_DIR)

help:
	@echo "=== WSL 2 Makefile – quick reference ==="
	@echo "Targets: list, status, start, stop, default, export, import, run, config, clean"
```

Typical usage:

| Command | Effect |
|---------|--------|
| `make list` | Lists all installed WSL distros. |
| `make start` | Starts the default or specified (`DISTRO=...`) distro. |
| `make stop` | Terminates the distro. |
| `make export` | Exports the distro to a tarball in `EXPORT_DIR`. |
| `make import` | Imports a tarball as a new distro (`NEWNAME=... FILE=...`). |
| `make run` | Executes a command inside the distro (`CMD="..."`). |
| `make default` | Sets the system-wide default distro. |
| `make config` | Displays the global WSL status and configuration. |

Override variables on the command line, e.g. `make DISTRO=Debian start` or `make run CMD="uname -a"`.

### Advantages of the Makefile Approach for WSL2

Using a Makefile for WSL2 management provides several technical advantages over raw CLI usage:
- **Version Control**: The Makefile can be stored in a Git repository, ensuring consistent environment management across a development team.
- **Idempotency**: By defining targets and dependencies, `make` prevents redundant operations.
- **Parameterization**: Command-line variable overrides (`DISTRO=...`) allow a single Makefile to manage multiple diverse distributions.
- **Composability**: Targets can be chained (e.g., `make stop start`) to perform complex sequences like restarting an environment in a single command.

---

## 11. Organising the Four Make‑Based Workflows in a Single Repository  

When a project contains several distinct automation domains—compiling source code, managing local VMs with Multipass, managing WSL2 distributions, and controlling cloud VMs with OpenStack—keep each domain in its **own directory with its own Makefile**. A **top‑level Makefile** can act as a façade, delegating to the appropriate sub‑Makefile.

### 10.1 Recommended Directory Layout  

```
project/
├─ Makefile                # top‑level entry point
├─ src/
│   ├─ Makefile            # builds the C program
│   ├─ main.c
│   ├─ foo.c
│   └─ bar.c
├─ vm/
│   ├─ multipass/
│   │   ├─ Makefile        # Multipass VM targets
│   │   └─ README.md
│   ├─ wsl2/
│   │   ├─ Makefile        # WSL2 distribution targets
│   │   └─ README.md
│   ├─ chameleon/
│   │   ├─ Makefile        # OpenStack VM targets
│   │   └─ README.md
│   └─ jetstream/
│       ├─ Makefile        # OpenStack VM targets
│       └─ README.md
└─ docs/
    └─ README.md           # overall project documentation
```

Each subdirectory holds only the files relevant to that concern. The `README.md` files can store environment‑specific instructions (e.g., required credentials, version constraints, or usage examples).


---

**Top‑level Makefile (facade)**  


## 12. Best Practices for Make‑Based Automation  

| Practice | Rationale |
|----------|-----------|
| **Declare every non‑file target as `.PHONY`** | Guarantees the recipe runs even if a file with the same name appears accidentally. |
| **Store configuration in variables** | Changing a value requires editing only one line, improving maintainability. |
| **Keep recipes short; outsource complex logic** | Makes the Makefile easy to read; external scripts can be unit‑tested separately. |
| **Add safety guards for destructive actions** (e.g., require `FORCE=1` for `delete`) | Prevents accidental data loss when a user runs `make` out of habit. |
| **Use `@` to silence the command line** when only the output matters | Produces cleaner console output, especially for status or info commands. |
| **Document each target with a comment header** | The Makefile becomes self‑documenting; newcomers can understand the workflow without external docs. |
| **Group related targets** (e.g., all Multipass tasks together) | Improves readability and makes future extensions straightforward. |

---

## Self-Assessment

## Self-Assessment

Test your knowledge by expanding the questions below.

??? question "Explain how `make` decides whether a target needs to be rebuilt. Which timestamps are compared?"
    `make` compares the timestamp of the target file with the timestamps of its prerequisites. If the target does not exist, or if any of its prerequisites have a newer timestamp than the target, `make` considers the target out-of-date and executes its recipe.

??? question "What is the purpose of the leading TAB character in a recipe line? What happens if you replace it with spaces?"
    The leading TAB is a syntax requirement of Makefiles to identify the lines that belong to a recipe. If you replace the TAB with spaces, `make` will fail to recognize the line as a command and will throw a "missing separator" error.

??? question "Given `SRC = a.c b.c c.c`, how do you create a variable `OBJ` containing the corresponding object file names?"
    You can use substitution references: `OBJ = $(SRC:.c=.o)`. This tells `make` to take the value of `SRC` and replace all occurrences of `.c` with `.o`.

??? question "In the pattern rule `%.o: %.c`, what do the automatic variables `$@` and `$<` expand to when building `foo.o`?"
    `$@` expands to the target name (`foo.o`), and `$<` expands to the name of the first prerequisite (`foo.c`).

??? question "Why must the `clean` target be declared `.PHONY`? What could go wrong if it is not?"
    The `clean` target is a symbolic action, not a file. If a file named `clean` were to be created in the directory, `make` would see that the "file" `clean` exists and has no prerequisites, thus concluding it is up-to-date and skipping the recipe. Declaring it `.PHONY` forces `make` to always run the recipe.

??? question "List the sequence of `make` commands to create a Multipass VM, start it, open a shell, and delete it."
    The sequence would be: `make launch`, `make start`, `make shell`, and finally `make delete`.

??? question "How would you launch an OpenStack server named `db-01` using image `centos-8` and flavor `m1.large` via the provided Makefile?"
    You would override the variables on the command line: `make SERVER_NAME=db-01 IMAGE=centos-8 FLAVOR=m1.large create`.

??? question "How can you modify a `delete` target to require an explicit `FORCE=1` flag?"
    You can add a shell check to the recipe:
    ```make
    delete:
            @if [ "$(FORCE)" != "1" ]; then echo "Error: Set FORCE=1 to delete"; exit 1; fi
            @$(OS_CMD) openstack server delete $(SERVER_NAME)
    ```

??? question "How would you implement a target that waits for an OpenStack VM to become `ACTIVE`?"
    You could create a target (e.g., `wait-active`) with a recipe that uses a `while` loop to poll the `openstack server show` command until the status field equals `ACTIVE`, using `sleep` between checks.

??? question "What is the purpose of the DISTRO variable in the WSL2 Makefile?"
    The `DISTRO` variable allows the user to override the `DEFAULT_DISTRO` on the command line, enabling the same `make` targets to operate on different WSL2 distributions.

??? question "How does the `make export` target handle the storage of the WSL2 distribution snapshot?"
    It ensures the `EXPORT_DIR` exists and saves the distribution as a `.tar` file named after the distribution being exported.

??? question "How can you execute a specific Linux command, such as `uname -a`, inside a WSL2 distro without entering the shell interactively?"
    By using the `run` target with the `CMD` variable: `make run CMD="uname -a"`.

??? question "Which best practices improve the reliability of cloud automation Makefiles?"
    1. **`.PHONY` declarations**: Prevents accidental skipping of tasks.
    2. **Configuration Variables**: Ensures consistency and makes it easy to target different environments (dev vs prod).
    3. **Safety Guards**: Prevents catastrophic accidental deletions in cloud environments.

---

## Assignments

!!! note "Assignment 1: Basic Build System"
    Create a small project with three `.c` files and a `main.c`. Write a Makefile that uses variables for the compiler and flags, implements a pattern rule for object files, and provides `all`, `run`, and `clean` targets.
    ??? tip "Local Setup"
        Depending on your OS, you may need to install `make`:
        - **macOS**: Install via Homebrew (`brew install make`) or use the built-in version.
        - **Linux/WSL2**: Install via package manager (`sudo apt install build-essential` or `make`).
        - **Windows**: Use WSL2 (recommended) or install via Chocolatey (`choco install make`).

!!! note "Assignment 2: Local VM Automation"
    Using Multipass, create a Makefile that allows you to launch a VM with a specific name, CPU count, and memory limit. Add a target that automatically installs `git` and `curl` inside the VM using `multipass exec`.

!!! note "Assignment 3: WSL2 Distribution Management"
    Save the provided WSL2 Makefile and execute `make help` from a Windows terminal to verify the targets. Start the default distribution, verify it is running using `make status`, and then terminate it using `make stop`. Additionally, export the current default distribution to a tarball and import that tarball as a new distribution named `WSL-Backup`.

!!! note "Assignment 4: Cloud VM Automation"
    Expand the OpenStack Makefile to include a `snapshot` target that creates an image of the current server and a `resize` target that changes the server's flavor.

!!! note "Assignment 5: The Façade Pattern"
    Organize your work into the directory structure described in §10. Create a top-level Makefile that can drive the build process in `src/` and the VM management in `vm/multipass/`, `vm/wsl2/`, and `vm/chameleon/` using the `-C` flag (e.g., `make -C src all`).

---  

## References & Further Reading

### Official Documentation
* **GNU Make Manual**: The definitive reference for all `make` features and syntax. [Read here](https://www.gnu.org/software/make/manual/)
* **Microsoft WSL Documentation**: Detailed guides on using WSL2 and interacting with Windows. [Read here](https://learn.microsoft.com/en-us/windows/wsl/)

### Interactive Guides & Cheatsheets
* **The Makefile Guide**: A modern, interactive tutorial and reference for writing Makefiles. [Visit makefile.guide](https://makefile.guide/)
* **DevHints Make Cheat Sheet**: A concise, single-page reference for common `make` syntax and variables. [View on devhints.io](https://devhints.io/make)

---

# Appendix - Are Makefiles DevOps


**Short answer:**  
Yes, a Makefile is a core DevOps tool. It isn't limited to compiling C programs; it's a lightweight, language‑agnostic task runner that can automate any command‑line workflow – building artifacts, running tests, creating Docker images, provisioning cloud resources, orchestrating CI/CD pipelines, and much more. Because DevOps is all about **repeatable, version‑controlled automation**, Makefiles fit naturally into that mindset.

---

## How Makefiles Align with DevOps Principles  

| DevOps Principle | How a Makefile Helps |
|------------------|----------------------|
| **Infrastructure as Code** | The build steps, container builds, VM lifecycle commands (e.g., `multipass`, `openstack`) are stored as plain‑text in a Makefile. They can be version‑controlled, reviewed, and rolled back just like any other source file. |
| **Automation & Repeatability** | `make` re‑evaluates dependencies and executes only the commands needed to bring the system to the desired state, guaranteeing the same result every time. |
| **Idempotence** | By expressing the desired state as targets and prerequisites, `make` avoids re‑running work that is already up‑to‑date (e.g., it won't rebuild a binary if the source hasn't changed). |
| **Speed & Incremental Builds** | Only the out‑of‑date parts are rebuilt, which speeds up local development cycles and CI jobs. |
| **Transparency & Documentation** | A Makefile is self‑documenting: each target name describes the action, and comments can explain the intent. New team members can read the file to understand the workflow. |
| **Portability** | `make` exists on virtually every Unix‑like system (Linux, macOS, BSD) and even on Windows via MSYS2, Cygwin, or WSL, so the same file works across environments. |
| **Integration with CI/CD** | Most CI systems (GitHub Actions, GitLab CI, Jenkins, Azure Pipelines, etc.) can invoke `make` directly, letting you reuse the exact same build scripts locally and in the pipeline. |
| **Extensibility** | Make can call any CLI tool—Docker, kubectl, Terraform, Ansible, Helm, etc.—so you can stitch together complex pipelines without adding another language or framework. |

---

## Typical DevOps Use‑Cases for Makefiles  

| Use‑Case | Example Target(s) | What the Recipe Might Do |
|----------|-------------------|--------------------------|
| **Compile & Package** | `build`, `test`, `package` | Compile source, run unit tests, create tarballs or Docker images. |
| **Container Image Build** | `docker-build`, `docker-push` | `docker build -t myapp:$(VERSION) .` and `docker push myrepo/myapp:$(VERSION)`. |
| **Infrastructure Provisioning** | `infra‑apply`, `infra‑destroy` | Call `terraform apply -auto-approve` or `pulumi up`. |
| **Deployments** | `deploy‑staging`, `deploy‑prod` | Run `kubectl apply -f k8s/` or `helm upgrade`. |
| **Database Migrations** | `migrate‑up`, `migrate‑down` | Execute `alembic upgrade head` or `flyway migrate`. |
| **Local Development Environments** | `vm‑launch`, `vm‑stop`, `vm‑shell` | Use `multipass`, `wsl`, or `vagrant` to spin up disposable VMs. |
| **Cloud‑VM Lifecycle (OpenStack, AWS, GCP)** | `os‑start`, `os‑stop`, `os‑delete` | Wrap `openstack server start …` or `aws ec2 start-instances`. |
| **Testing & Linting** | `lint`, `format`, `integration‑test` | Run `flake8`, `black`, or a test suite against a staging environment. |
| **Cleaning & Resetting** | `clean`, `reset` | Delete build artifacts, stop containers, remove temporary files. |

---

## Minimal DevOps‑Style Makefile (Illustrative)

```make
# -------------------------------------------------
# Project‑wide DevOps Makefile
# -------------------------------------------------

# ---- Global variables -------------------------------------------------
VERSION ?= $(shell git describe --tags --always --dirty)
DOCKER_REPO ?= myregistry.example.com/myapp

# ---- Phony targets ----------------------------------------------------
.PHONY: all build test docker-build docker-push deploy clean

# ---- Default (build + test) -------------------------------------------
all: build test

# ---- Build the binary (or any artifact) ---------------------------------
build:
        @echo "Building version $(VERSION)..."
        @./gradlew assemble               # could be gcc, go build, npm, etc.

# ---- Run unit tests ------------------------------------------------------
test:
        @echo "Running unit tests..."
        @./gradlew test

# ---- Build Docker image ---------------------------------------------------
docker-build:
        @echo "Building Docker image $(DOCKER_REPO):$(VERSION)"
        @docker build -t $(DOCKER_REPO):$(VERSION) .

# ---- Push Docker image ----------------------------------------------------
docker-push: docker-build
        @echo "Pushing Docker image to registry..."
        @docker push $(DOCKER_REPO):$(VERSION)

# ---- Deploy to Kubernetes (example) ---------------------------------------
deploy: docker-push
        @echo "Deploying $(DOCKER_REPO):$(VERSION) to k8s..."
        @kubectl set image deployment/myapp myapp=$(DOCKER_REPO):$(VERSION) \
                --record

# ---- Clean up build artifacts ---------------------------------------------
clean:
        @echo "Cleaning workspace..."
        @./gradlew clean
        @docker rmi $(DOCKER_REPO):$(VERSION) || true
```

Running `make` locally gives you the same steps that a CI job would perform, and each target can be invoked independently (`make docker-push`, `make deploy`, etc.).

---

## Putting Makefiles in a DevOps Toolchain  

1. **Version Control** – Store every Makefile under Git (or your preferred VCS).  
2. **CI Integration** – In your CI pipeline, a single step like `make all` can replace a long list of script commands.  
3. **Artifact Storage** – Use Make variables to inject build numbers, commit hashes, or timestamps, ensuring traceability of produced images or binaries.  
4. **Environment‑Specific Overrides** – Pass variables from CI secrets or environment files, e.g., `make deploy ENV=prod`.  
5. **Modularisation** – Split large Makefiles into logical directories (as shown in the previous chapter) and include them with `include path/to/Other.mk`.  

---

## When to Prefer a Makefile Over Other Tools  

| Situation | Makefile shines | Alternatives may be better |
|-----------|----------------|----------------------------|
| **Simple command sequencing** (few steps, no complex branching) | Very lightweight; no extra dependencies. | None needed. |
| **Cross‑platform CI pipelines** | Works on Linux/macOS out‑of‑the‑box; Windows via `make` ports. |  There are versions of Make that work directly on Windows. Instalation is requiered |
| **Highly dynamic logic** (loops, conditionals, complex data structures) | Possible but gets messy; use a scripting language (Python, Bash, Go) for readability. | Python scripts, Ansible playbooks, Terraform modules. |
| **Infrastructure as Code with state tracking** | Make can express state via file timestamps, but not a full state model. | Terraform, Pulumi, CloudFormation. |
| **Large collaboration with many contributors** | Simple syntax is easy to learn, but large Makefiles can become hard to maintain. | Dedicated CI/CD pipelines (GitHub Actions, GitLab CI) with separate YAML files. |

---

## Checklist – "Is Makefile a DevOps Tool for My Project?"

- [ ] **Automation needed?** – If you have repeatable shell commands, a Makefile can orchestrate them.  
- [ ] **Version‑controlled workflow?** – Makefiles live comfortably in Git.  
- [ ] **Incremental execution desirable?** – `make` only runs what's out‑of‑date.  
- [ ] **Toolchain already includes `make`?** – Most dev boxes, containers, and CI runners have it.  
- [ ] **Complex state management required?** – Consider Terraform/Ansible for that; otherwise use Make.  

If the answer is *yes* to the first three, a Makefile is an excellent, low‑overhead DevOps asset. It pairs nicely with other DevOps tools, acting as the glue that ties source builds, container images, infrastructure provisioning, and deployment steps together in a single, auditable script.

---

## What's Next?

With a powerful local automation tool in your arsenal, you're ready to move your workflows into the cloud. Explore **Automating the Software Lifecycle with GitHub Actions** to see how event-driven automation can transform your delivery pipeline.
