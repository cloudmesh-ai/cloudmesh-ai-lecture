# Python Project Configuration with pyproject.toml

!!! info "Learning Objectives"
    - Understand the purpose and history of `pyproject.toml` (PEP 518 and PEP 621).
    - Configure the build system for a Python project.
    - Define project metadata and dependencies using the standardized `[project]` table.
    - Centralize tool configurations for linters and test runners.
    - Create a production-ready configuration file for a Python library.

The Python packaging ecosystem has historically been fragmented. For years, `setup.py` was the primary way to define how a package should be built and installed. However, `setup.py` is an executable Python script, which created a "chicken-and-egg" problem: you needed to run the script to find out what dependencies were needed to run the script.

`pyproject.toml` solves this by providing a declarative, static configuration file. By separating the build requirements from the project metadata, it allows tools to determine how to build a project without executing arbitrary code. This shift ensures more reliable builds and a unified configuration experience across different build backends like setuptools, Poetry, and Flit.

## Understanding TOML

TOML (Tom's Obvious, Minimal Language) is designed to be easy to read and map directly to a hash table. It is the foundation of `pyproject.toml`.

Key TOML concepts include:
- Tables: Defined by `[section]`, these group related settings.
- Nested Tables: Defined by `[section.subsection]`.
- Arrays: List values enclosed in `[]`.
- Inline Tables: Compact key-value pairs enclosed in `{}`.

Example of a basic tool configuration in TOML:

```toml
[tool.black]
line-length = 88
target-version = ["py38"]
```

## The Build System

The `[build-system]` section is mandated by PEP 518. It tells the installer (like `pip`) exactly what is needed to build the package.

### Specifying the Backend

The `requires` key lists the packages needed to perform the build, while `build-backend` specifies the object that actually performs the build.

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

!!! tip "Why this matters"
    By declaring the build requirements here, `pip` can create an isolated temporary environment, install the listed requirements, and build your package without interfering with the user's global Python environment.

## Project Metadata

PEP 621 introduced a standardized way to define project metadata in `pyproject.toml`. This removes the need for tool-specific metadata formats.

### Core Metadata Fields

The `[project]` table contains the primary information about the package.

```toml
[project]
name = "weather-tools"
version = "0.1.0"
description = "Utilities for fetching and analysing weather data"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Apache-2.0"}
authors = [
    {name = "Alex Storm", email = "alex@example.org"}
]
keywords = ["weather", "api", "analysis"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent"
]
```

### Managing Dependencies

Dependencies are listed as an array of strings following PEP 508 specifiers.

```toml
dependencies = [
    "httpx>=0.24",
    "pandas>=2.0"
]
```

For optional dependencies (extras), use the `[project.optional-dependencies]` table.

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.3",
    "black>=23.1",
    "isort>=5.12"
]
docs = [
    "sphinx>=6.1",
    "furo>=2023.5"
]
```

!!! warning "Common Pitfall: Version Pinning"
    Avoid pinning exact versions (e.g., `httpx == 0.24.1`) in the `dependencies` list for libraries. This can cause dependency conflicts for users. Instead, use compatible ranges (e.g., `httpx >= 0.24`). Use a lock file (like `uv.lock` or `poetry.lock`) for exact environment reproduction in applications.

## Tool Configuration

One of the most convenient aspects of `pyproject.toml` is its ability to host configuration for various development tools under the `[tool]` table.

### Formatting with Black

Black is an uncompromising code formatter. Its configuration is simple and resides in the `[tool.black]` section.

```toml
[tool.black]
line-length = 88
target-version = ["py310"]
```

### Import Sorting with isort

isort ensures imports are sorted consistently. To avoid conflicts with Black, use the `black` profile.

```toml
[tool.isort]
profile = "black"
known_first_party = ["weather_tools"]
```

### Testing with pytest

Pytest allows you to move its `.ini` configuration directly into the TOML file.

```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q"
testpaths = ["tests"]
```

## Production-Ready Example

Below is a complete, minimal `pyproject.toml` that combines all the concepts discussed.

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "weather-tools"
version = "0.1.0"
description = "Utilities for fetching and analysing weather data"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Apache-2.0"}
authors = [
    {name = "Alex Storm", email = "alex@example.org"}
]
dependencies = [
    "httpx>=0.24",
    "pandas>=2.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.3",
    "black>=23.1"
]

[tool.black]
line-length = 88

[tool.isort]
profile = "black"
```

!!! tip "Summary Checklist"
    - [ ] Created a `pyproject.toml` file in the project root.
    - [ ] Defined the `[build-system]` with a valid backend.
    - [ ] Added project metadata (name, version, authors) in the `[project]` table.
    - [ ] Listed runtime dependencies using PEP 508 strings.
    - [ ] Configured development tools under the `[tool]` section.
    - [ ] Verified the configuration using `pip install .` or a tool like `uv`.

!!! note "Exercise 1: Basic Setup"
    Create a new directory for a project. Initialize a `pyproject.toml` file that defines a project named "my-first-lib", version "0.1.0", and uses `setuptools` as the build backend.

!!! note "Exercise 2: Adding Metadata and Dependencies"
    Extend your `pyproject.toml` from Exercise 1. Add a description, specify that it requires Python 3.9 or higher, and add `requests` as a dependency.

!!! note "Exercise 3: Tool Integration"
    Add a configuration section for `black` that sets the `line-length` to 100. Add a `dev` optional dependency group that includes `pytest`.


## Appendix: Advanced Versioning  

### Why avoid a hard‑coded version in `pyproject.toml`?  

Hard‑coding the version string in the `pyproject.toml` file creates a second source of truth. When the version is also stored in the package’s `__init__.py`, a `__about__.py` file, or a VCS tag, the three locations can easily diverge – a situation known as **version drift**.  
Dynamic versioning eliminates the drift by letting the build backend obtain the version from a **single** place at build time.

---

## 1. Declaring a Dynamic Version (PEP 621)

```toml
[project]
name = "weather-tools"
dynamic = ["version"]          # tells the builder that the version will be supplied later
```

With `dynamic = ["version"]` the backend looks for a provider‑specific configuration under a `tool.<backend>` table.

---

## 2. File‑Based Versioning with Hatch  

Hatch (via the `hatchling` backend) can read the version from a plain‑text file. This is the most straightforward approach for CI pipelines, shell scripts, or non‑Python tools that need to query the current version.

### 2.1 Minimal configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "weather-tools"
dynamic = ["version"]

[tool.hatch.version]
path = "VERSION"               # file must contain only the version string, e.g. 0.1.0
```

### 2.2 Requirements  

| Requirement | Detail |
|-------------|--------|
| **Backend** | `hatchling` (declared in `[build-system]`). |
| **Version source** | A file named `VERSION` at the project root. The file must contain a single line, e.g. `0.1.0`. |
| **Runtime access** | If the package itself needs to expose the version, you can read the file in Python (`import pathlib; __version__ = pathlib.Path(__file__).with_name("VERSION").read_text().strip()`). |

### 2.3 Example `VERSION` file  

```
0.1.0
```

---

## 3. Attribute‑Based Versioning with Setuptools  

Setuptools can retrieve the version from a Python module (the classic “single‑source of truth” pattern). The module must expose a string variable, usually called `__version__`.

### 3.1 Minimal configuration

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "weather-tools"
dynamic = ["version"]

[tool.setuptools.dynamic]
version = {attr = "weather_tools.__version__"}   # refers to a variable in the code base
```

### 3.2 Requirements  

| Requirement | Detail |
|-------------|--------|
| **Backend** | `setuptools` (declared in `[build-system]`). |
| **Version source** | A Python attribute, typically defined in `src/weather_tools/__init__.py` or `src/weather_tools/__about__.py`. |
| **Runtime access** | The version is already importable as `weather_tools.__version__`. No extra file I/O is needed. |

### 3.3 Example `src/weather_tools/__init__.py`

```python
"""Top‑level package for weather‑tools."""
__all__ = ["__version__"]
__version__ = "0.1.0"
```

---

### 3.4. File‑Based Versioning with Setuptools (alternative)

Setuptools also supports reading a version directly from a file, similar to Hatch, using the `file` key:

```toml
[tool.setuptools.dynamic]
version = {file = ["VERSION"]}
```

> **Note:** When using the `file` option, the `VERSION` file must be present **before** the build starts (e.g., checked into the repository). The same file can be read by the package at runtime if you prefer.

---

### 3.5. Comparative Summary  

| Feature | Hatch (file) | Setuptools (attribute) | Setuptools (file) |
|---------|--------------|------------------------|-------------------|
| **Ease of setup** | Very high (just a file and `hatchling`) | High (add a variable in code) | High |
| **Source of truth** | Plain‑text file | Python module variable | Plain‑text file |
| **Access from non‑Python tools** | Immediate (`cat VERSION`) | Requires importing the package (or exposing via script) | Immediate |
| **Access from Python code** | Must read the file manually | Direct (`import weather_tools; weather_tools.__version__`) | Must read the file manually (or expose via a helper) |
| **Build backend** | `hatchling` | `setuptools` | `setuptools` |
| **Ideal for CI/CD scripts** | ✔︎ (no Python needed) | ✖︎ (needs Python import) | ✔︎ |
| **PEP 621 compliance** | ✔︎ (dynamic version) | ✔︎ (dynamic version) | ✔︎ (dynamic version) |

### Verdict  

* **Choose Hatch** when you need a **raw `VERSION` file** that can be consumed by shell scripts, CI pipelines, Docker builds, or any language that can read a text file without importing Python.  
* **Choose Setuptools attribute‑based versioning** when the version must be **readable from within the package** without extra I/O and you want a single source that lives alongside the code.  
* **Setuptools file‑based** is a middle ground: you keep the simple file but stay on the more widely‑adopted `setuptools` backend.

For this last reason often setuptools is prefered.

---

### 3.6. Practical Tips  

1. **Keep the version file in version control.**  
   ```bash
   echo "0.1.0" > VERSION
   git add VERSION
   ```
2. **Synchronise the version in CI.**  
   ```bash
   VERSION=$(cat VERSION)
   echo "Building release $VERSION"
   hatch version bump  # for Hatch‑managed projects
   ```
3. **Expose the version programmatically (Hatch example).**  
   ```python
   # src/weather_tools/__init__.py
   from pathlib import Path

   _version_file = Path(__file__).with_name("VERSION")
   __version__ = _version_file.read_text().strip()
   ```
   This gives you the best of both worlds: a plain file for external tools and an importable `__version__` for Python code.

4. **Avoid mixing approaches.**  
   Do not declare both `tool.hatch.version.path` **and** `tool.setuptools.dynamic.version.attr` in the same project; it leads to ambiguous source selection.

5. **Validate the version at build time.**  
   Add a small pre‑build hook (Hatch or setuptools entry point) that checks the version string conforms to PEP 440.

---

### 3.7. Quick Demonstration (reading the `VERSION` file at runtime)

Below is a tiny snippet that shows how a package can obtain its version from the `VERSION` file without any external dependencies:

```python
# Demonstration: read version from VERSION file
from pathlib import Path

def get_version() -> str:
    """Return the version defined in the top‑level VERSION file."""
    version_file = Path(__file__).with_name("VERSION")
    try:
        return version_file.read_text().strip()
    except FileNotFoundError:
        raise RuntimeError("VERSION file not found – ensure it exists at project root.")

if __name__ == "__main__":
    print("Package version:", get_version())
```

Running this script (e.g., `python -m weather_tools.version`) prints the current version, confirming that the same file used by Hatch during the build can also be used by the package itself.

---

### Bottom Line  

Dynamic versioning, whether file‑based (Hatch) or attribute‑based (Setuptools), guarantees a **single source of truth** and eliminates the risk of version drift. Choose the strategy that aligns with your workflow and the tooling ecosystem surrounding your project.


## Further Reading

- [PEP 518 – Specifying Minimum Build System Requirements](https://peps.python.org/pep-0518/)
- [PEP 621 – Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [TOML Specification](https://toml.io/en/v1.0.0)
- [Setuptools Migration Guide](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
