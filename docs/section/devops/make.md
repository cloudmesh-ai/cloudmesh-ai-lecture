
---

# Makefiles and Cloud‑VM Management  


!!! Learning Objectives

    By the end of this chapter you should be able to:

    1. **Describe** the purpose of a Makefile and explain how `make` decides which commands to run.  
    2. **Identify** the main components of a Makefile: targets, prerequisites, recipes, variables, and phony declarations.  
    3. **Write** a simple Makefile that builds a C program using pattern rules and automatic variables.  
    4. **Create** reusable variables and pattern rules to avoid duplication in larger projects.  
    5. **Apply** Makefile concepts to non‑compilation tasks, specifically to manage virtual machines with the Multipass CLI.  
    6. **Construct** a Makefile that drives OpenStack CLI commands for common VM lifecycle operations (create, start, stop, delete, status).  
    7. **Employ** best‑practice techniques such as phony targets, safety guards for destructive actions, and clear documentation within the Makefile.  
    8. **Adapt** the Makefile to different environments by overriding variables on the command line.  
    9. **Organise** multiple, related Makefiles in a coherent directory hierarchy and drive them from a single top‑level Makefile.  


## 1. What a Makefile Is  

A **Makefile** is a plain‑text script interpreted by the `make` utility. Its purpose is to describe *what* must be built (the **targets**) and *how* to build it (the **recipes**). When `make` is invoked it:

1. Reads the dependency graph defined by targets and their prerequisites.  
2. Checks timestamps: a target is out‑of‑date if it does not exist or any prerequisite is newer.  
3. Executes the minimal set of recipes needed to bring the target up‑to‑date.

Although Make was devised for compiling C programs, the same model works for any repeatable command‑line workflow, making it a lightweight “task runner” for DevOps, documentation generation, container orchestration, and cloud‑VM management.

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

## 9. Organising the Three Make‑Based Workflows in a Single Repository  

When a project contains several distinct automation domains—compiling source code, managing local VMs with Multipass, and controlling cloud VMs with OpenStack—keep each domain in its **own directory with its own Makefile**. A **top‑level Makefile** can act as a façade, delegating to the appropriate sub‑Makefile.

### 9.1 Recommended Directory Layout  

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



## 10. Best Practices for Make‑Based Automation  

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

### Self‑Assessment Questions  

1. **Conceptual** – Explain how `make` decides whether a target needs to be rebuilt. Which timestamps are compared?  
2. **Syntax** – What is the purpose of the leading TAB character in a recipe line? What happens if you replace it with spaces?  
3. **Variables** – Given `SRC = a.c b.c c.c`, write a Makefile line that creates the variable `OBJ` containing the corresponding object file names.  
4. **Pattern Rules** – In the rule `%.o: %.c`, what do the automatic variables `$@` and `$<` expand to when building `foo.o`?  
5. **Phony Targets** – Why must the `clean` target be declared `.PHONY`? What could go wrong if it is not?  
6. **Multipass** – List the sequence of `make` commands you would run to (a) create a VM, (b) start it, (c) open a shell inside it, and (d) finally delete it.  
7. **OpenStack** – If you want to launch a server named `db‑01` using the image `centos‑8` and flavor `m1.large`, write the exact `make` command you would issue (assume the OpenStack Makefile shown above).  
8. **Safety** – Propose a simple modification to the OpenStack `delete` target that requires an explicit `FORCE=1` flag before the deletion is executed. Write the modified rule.  
9. **Extensibility** – Sketch a target that waits until an OpenStack VM reaches the `ACTIVE` state before proceeding to the next step. Provide the target name and a brief description of the recipe (full code not required).  
10. **Best Practices** – Identify three best‑practice items from the table in § 10 and explain why each improves the reliability of a Makefile used for cloud automation.  

---  

# Appendix - Are Makefiles DevOps



**Short answer:**  
Yes, a Makefile is a core DevOps tool. It isn’t limited to compiling C programs; it’s a lightweight, language‑agnostic task runner that can automate any command‑line workflow – building artifacts, running tests, creating Docker images, provisioning cloud resources, orchestrating CI/CD pipelines, and much more. Because DevOps is all about **repeatable, version‑controlled automation**, Makefiles fit naturally into that mindset.

---

## How Makefiles Align with DevOps Principles  

| DevOps Principle | How a Makefile Helps |
|------------------|----------------------|
| **Infrastructure as Code** | The build steps, container builds, VM lifecycle commands (e.g., `multipass`, `openstack`) are stored as plain‑text in a Makefile. They can be version‑controlled, reviewed, and rolled back just like any other source file. |
| **Automation & Repeatability** | `make` re‑evaluates dependencies and executes only the commands needed to bring the system to the desired state, guaranteeing the same result every time. |
| **Idempotence** | By expressing the desired state as targets and prerequisites, `make` avoids re‑running work that is already up‑to‑date (e.g., it won’t rebuild a binary if the source hasn’t changed). |
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
| **Local Development Environments** | `vm‑launch`, `vm‑stop`, `vm‑shell` | Use `multipass` or `vagrant` to spin up disposable VMs. |
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

## Checklist – “Is Makefile a DevOps Tool for My Project?”

- [ ] **Automation needed?** – If you have repeatable shell commands, a Makefile can orchestrate them.  
- [ ] **Version‑controlled workflow?** – Makefiles live comfortably in Git.  
- [ ] **Incremental execution desirable?** – `make` only runs what’s out‑of‑date.  
- [ ] **Toolchain already includes `make`?** – Most dev boxes, containers, and CI runners have it.  
- [ ] **Complex state management required?** – Consider Terraform/Ansible for that; otherwise use Make.  

If the answer is *yes* to the first three, a Makefile is an excellent, low‑overhead DevOps asset. It pairs nicely with other DevOps tools, acting as the glue that ties source builds, container images, infrastructure provisioning, and deployment steps together in a single, auditable script.