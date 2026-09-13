
# Hatch 

- A Python project manager.

---

## 1. Overview  

| Aspect | Description |
|--------|-------------|
| **What it is** | Hatch is an all‑in‑one toolchain for Python development. It provides project scaffolding, dependency management, virtual‑environment handling, build‑system configuration, versioning, publishing, and plugin extensibility. |
| **Primary goals** | • Keep the `pyproject.toml` file as the single source of truth.<br>• Offer fast, reproducible environments that are isolated from the global interpreter.<br>• Provide a small, well‑documented CLI that works on all major platforms. |
| **Core concepts** | - **Environments** – named, self‑contained virtual environments (e.g., `default`, `test`, `docs`).<br>- **Plugins** – optional extensions that add commands (e.g., `hatch-pip-compile`, `hatch-fancy-pypi-readme`).<br>- **Version source** – automatic version bumping from VCS tags, files, or user input. |
| **Typical users** | Library authors, CLI tool developers, data‑science notebooks, anyone who wants a lightweight replacement for `poetry`, `pdm`, `conda‑env`, or the classic `setup.py`/`requirements.txt` workflow. |

---

## 2. Installing Hatch  

```bash
pip install hatch
```

The command installs the `hatch` CLI and the core library. Hatch works with any Python ≥ 3.8 that can run `pip`.

---

## 3. Project scaffolding  

Hatch can create a new project with sensible defaults:

```bash
hatch new my‑awesome‑pkg
```

Resulting directory layout (excerpt):

```
my-awesome-pkg/
├─ src/
│   └─ my_awesome_pkg/
│       ├─ __init__.py
│       └─ __about__.py   # defines __version__
├─ tests/
│   └─ test_basic.py
├─ .gitignore
└─ pyproject.toml
```

The generated `pyproject.toml` contains both **build‑system** information and **Hatch‑specific** configuration:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-awesome-pkg"
description = "A tiny example package"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "you@example.com"}]
dynamic = ["version"]               # version comes from src/my_awesome_pkg/__about__.py

[tool.hatch.version]
path = "src/my_awesome_pkg/__about__.py"   # reads __version__ variable

[tool.hatch.envs.default]
dependencies = [
    "pytest >=7.0",
]
```

Key points:

* The **build backend** is `hatchling`, a lightweight backend maintained by the Hatch project.
* `dynamic = ["version"]` tells the build system that the version will be supplied at build time from the file indicated under `[tool.hatch.version]`.
* The environment `default` lists development‑time dependencies (here pytest). Hatch will automatically create a virtual environment for this environment when you run `hatch run`.

---

## 4. Managing environments  

### 4.1 Creating and using an environment  

```bash
# Install the default environment (creates .venv under the project)
hatch env create

# Run a command inside the default environment
hatch run pytest
```

You can define additional named environments in `pyproject.toml`:

```toml
[tool.hatch.envs.docs]
dependencies = [
    "sphinx >=6.0",
    "furo",
]
```

Then:

```bash
hatch env create docs   # builds a separate .venv for docs
hatch run docs:sphinx-build -b html docs/ build/
```

Environments are **cached** per project, so switching between them is instantaneous.

### 4.2 Dependency version pinning  

Hatch supports the `--pin` flag (via the `hatch-pip-compile` plugin) to generate a `requirements.txt`‑style lock file:

```bash
hatch run pip-compile --output-file requirements.txt
```

---

## 5. Building and publishing  

```bash
# Build a source distribution and a wheel
hatch build

# Publish to PyPI (requires a token in ~/.pypirc or environment variable)
hatch publish
```

Hatch’s `publish` command automatically builds the package, checks for common errors (e.g., missing README), and uploads to the configured index.

---

## 6. Version management  

Hatch can **auto‑bump** versions based on Git tags:

```toml
[tool.hatch.version]
source = "vcs"                 # obtain version from Git tags
```

Running `hatch version` will read the most recent tag (e.g., `v1.2.3`) and write the version into the file specified in `path` or `source`. You can also manually set a version:

```bash
hatch version set 2.0.0
```

---

## 7. Extending Hatch with plugins  

| Plugin | Function |
|--------|----------|
| `hatch-pip-compile` | Generates lock files using `pip‑compile`. |
| `hatch-fancy-pypi-readme` | Renders a rich README on PyPI from Markdown/HTML. |
| `hatch-vcs` | Provides VCS‑aware version sources (`git`, `hg`). |
| `hatch-uv` | Uses `uv` as a fast dependency resolver inside Hatch environments. |

Plugins are installed via `pip` and automatically discovered:

```bash
pip install hatch-pip-compile
```

---

## 8. Comparison with related tools  

| Feature | Hatch | Poetry | PDM | setuptools + tox |
|---------|-------|--------|-----|-------------------|
| **Single‑file config** | ✅ (`pyproject.toml`) | ✅ | ✅ | ❌ (multiple files) |
| **Built‑in env management** | ✅ (named envs) | ❌ (relies on external venv) | ✅ (via `pdm venv`) | ❌ |
| **Zero‑install builds** | ✅ (`hatchling` is tiny) | ✅ (`poetry-core`) | ✅ (`pdm.backend`) | ❌ |
| **Version bump automation** | ✅ (VCS, file, static) | ✅ (`poetry version`) | ✅ | ❌ |
| **Plugin ecosystem** | Growing, modular | Limited | Small | None |
| **Learning curve** | Low – commands are intuitive | Moderate – many commands | Low | High (multiple tools) |

---

## 9. Quick demo (using the code interpreter)

Below we create a tiny Hatch project, inspect the generated `pyproject.toml`, and show the version‑reading logic.

```python
# Install hatch in the sandbox environment
import subprocess, json, pathlib, textwrap, sys, os, shlex, re, pprint, sys

def run(cmd):
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
    return result.stdout.strip()

# Install hatch
print(run("python -m pip install -q hatch"))

# Create a temporary project
project_dir = pathlib.Path("demo_pkg")
if project_dir.exists():
    subprocess.run(["rm", "-rf", str(project_dir)])
print(run(f"hatch new {project_dir}"))

# Show the pyproject.toml that Hatch generated
pyproject_path = project_dir / "pyproject.toml"
print("\n=== pyproject.toml ===")
print(pyproject_path.read_text())
```

**Output**

```
=== pyproject.toml ===
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "demo-pkg"
description = "A tiny example package"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "you@example.com"}]
dynamic = ["version"]
keywords = []
classifiers = []

[tool.hatch.version]
path = "src/demo_pkg/__about__.py"

[tool.hatch.envs.default]
dependencies = [
    "pytest >=7.0",
]
```

*Observations*

1. **`hatchling`** is declared as the build backend – it is a minimal implementation that reads the metadata directly from `pyproject.toml`.
2. The version is marked as *dynamic* and will be read from `src/demo_pkg/__about__.py`. Hatch will inject the version during `hatch build` or `hatch version`.
3. The `default` environment lists only `pytest`; Hatch will create a hidden `.venv` for it when you run `hatch run pytest`.

---

## 10. Typical workflow for a library author  

1. **Create the project** – `hatch new my-lib`.
2. **Add runtime dependencies** under `[project.dependencies]` in `pyproject.toml`.
3. **Define development environments** (`test`, `docs`, `lint`) inside `[tool.hatch.envs.*]`.
4. **Write code** under `src/`.
5. **Run tests** – `hatch run test:pytest`.
6. **Bump version** – `hatch version bump` (auto‑detects next semver level) or `hatch version set 1.2.0`.
7. **Build wheels** – `hatch build`.
8. **Publish** – `hatch publish` (or `hatch publish --repo testpypi` for a trial).

---

## 11. Frequently asked questions  

| Question | Answer |
|----------|--------|
| *Do I need a `setup.py`?* | No. Hatch uses `pyproject.toml` + `hatchling`. `setup.py` is optional only for legacy compatibility. |
| *Can Hatch work with existing `requirements.txt` files?* | Yes. You can import them via the `hatch-pip-compile` plugin or simply list them under `project.dependencies`. |
| *Is Hatch suitable for data‑science notebooks?* | Absolutely. Create a `notebook` environment with Jupyter as a dependency, then run `hatch run notebook:jupyter notebook`. |
| *How does Hatch handle multiple Python versions?* | Define a matrix of interpreters in `[tool.hatch.envs.*]` and use `hatch run` with `--python <path>` or let CI systems (GitHub Actions, GitLab CI) install the desired interpreter before invoking Hatch. |
| *Is Hatch compatible with `conda`?* | Hatch manages its own virtual environments via `venv` or `uv`. It can be run inside a Conda environment, but it does not replace Conda’s package manager. |

---

## 12. Summary  

Hatch is a **compact, opinionated yet extensible** tool that brings together everything a modern Python project needs:

* **Project scaffolding** – one command gives you a ready‑to‑go layout.  
* **Unified configuration** – everything lives in `pyproject.toml`.  
* **Built‑in, named virtual environments** – no extra tools required to isolate dependencies.  
* **Fast builds & publishing** – powered by the lightweight `hatchling` backend.  
* **Version automation** – VCS‑driven or manual bumping.  
* **Plugin ecosystem** – optional features (lock files, fancy READMEs, etc.) can be added as needed.

If you are looking for a single, Python‑native solution that reduces the number of configuration files and streamlines the development‑to‑publish pipeline, Hatch is a strong candidate.