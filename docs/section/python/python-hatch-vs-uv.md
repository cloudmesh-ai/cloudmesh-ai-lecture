# Hatch vs uv: Project Management and Dependency Installation

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Distinguish between a project manager (Hatch) and a package installer (uv).
    - Evaluate when to use Hatch for project orchestration and publishing.
    - Implement `uv` to accelerate dependency resolution and virtual environment creation in CI/CD.
    - Configure a hybrid workflow using Hatch for orchestration and `uv` for installation speed.

Choosing between Hatch and `uv` depends on whether you need full-lifecycle project orchestration or high-performance dependency management.

---

## Comparison Overview

| Aspect | Hatch | uv |
|--------|-----------|--------|
| **Primary purpose** | Full-stack project manager: scaffolding, version handling, metadata, named virtual environments, builds, and publishing. | Ultra-fast package installer and resolver (pip replacement) plus a minimal venv manager. |
| **Design focus** | One-stop shop for the entire lifecycle of a Python library or CLI. | Speed of dependency resolution and installation. |
| **Configuration** | Single `pyproject.toml` with PEP 621 metadata and Hatch-specific tables. | `requirements.txt`, `pyproject.toml`, or `uv.lock`. |
| **Venv handling** | Built-in named environments (e.g., `hatch run test:pytest`). | Single venv via `uv venv`; requires manual activation or `uv run`. |
| **Version management** | Supports dynamic version sources and automatic bumping. | No built-in version bumping. |
| **Publishing** | Integrated `hatch build` and `hatch publish`. | No publishing commands; requires external tools like `twine`. |
| **Extensibility** | Robust plugin ecosystem. | CLI-based; can be combined with other tools but lacks a plugin system. |
| **Typical workflow** | Scaffold $\rightarrow$ Edit $\rightarrow$ Env Create $\rightarrow$ Run $\rightarrow$ Build $\rightarrow$ Publish. | Define requirements $\rightarrow$ Create venv $\rightarrow$ Install $\rightarrow$ Run. |
| **Best for** | Projects requiring wide orchestration, versioning, and publishing. | CI pipelines, container builds, and large dependency graphs where speed is critical. |

---

## Performance Comparison

In a benchmark creating a virtual environment and installing a modest set of dependencies (`requests`, `pydantic`, `pytest`), the relative difference in speed is significant.

### Benchmark Results (Illustrative)

| Step | Hatch | uv |
| :--- | :--- | :--- |
| **Env Creation** | $\approx$ 2.8s | $\approx$ 0.3s |
| **Dependency Install** | Included in Env Create | $\approx$ 1.1s |
| **Sanity Check** | $\approx$ 0.6s | $\approx$ 0.4s |

### Interpretation

- **Venv Speed**: `uv venv` is significantly faster than Hatch's environment creation.
- **Resolution**: `uv` uses a Rust-based resolver, making dependency installation typically faster than standard pip-based tools.
- **Overhead**: Hatch performs additional project-level orchestration (metadata validation, named environment setup), which adds to the total execution time.
- **CI Impact**: In CI pipelines where environments are recreated every run, `uv` can significantly reduce build times.

---

## When to Choose Hatch

Use Hatch when your project requires a cohesive, all-in-one workflow.

| Scenario | Advantage |
|----------|------------------|
| **All-in-one workflow** | Bundles scaffolding, versioning, and publishing. |
| **Multiple Dev Envs** | Named environments (e.g., `test`, `docs`, `lint`) stay isolated and easily switchable. |
| **Dynamic Versioning** | Simple configuration via `[tool.hatch.version]`. |
| **Plugin Ecosystem** | Easy access to community plugins for README generation or requirement exports. |
| **Metadata Consistency** | Guarantees PEP 621 compliance via `pyproject.toml`. |

### Minimal Hatch Workflow

```bash
# 1. Scaffold project
hatch new my-cli

# 2. Create development environment
hatch env create

# 3. Run tests inside the environment
hatch run test:pytest

# 4. Bump version and publish
hatch version bump
hatch build
hatch publish
```

---

## When to Choose uv

Use `uv` when installation speed and a lightweight footprint are the primary concerns.

| Scenario | Advantage |
|----------|----------------|
| **Critical Speed** | Rust-based resolver is orders of magnitude faster than pip. |
| **Complementary Tool** | Acts as a drop-in replacement for `pip install` regardless of the project manager. |
| **Lightweight Footprint** | Single binary with no complex configuration tables. |
| **One-off Scripts** | `uv run` creates a temporary venv, installs deps, and runs the script in one step. |
| **Deterministic Builds** | `uv lock` produces a reproducible `uv.lock` file. |

### Minimal uv Workflow

```bash
# 1. Create virtual environment
uv venv .venv

# 2. Install dependencies fast
uv pip install -r requirements.txt

# 3. Run command without manual activation
uv run pytest

# 4. Generate reproducible lock file
uv lock
uv sync
```

---

## Combining Hatch and uv

Many teams use both tools to get the orchestration of Hatch and the speed of `uv`.

**Strategy**: Configure Hatch to use `uv` as the installer inside its environments.

```toml
[tool.hatch.envs.default]
# Use uv for installing dependencies instead of the default pip
scripts = { install = "uv pip install -r requirements.txt" }
```

By delegating the installation step to `uv`, `hatch env create` becomes significantly faster while retaining Hatch's project management features.

---

## Decision Guide

| Need | Recommended Tool/Combo |
|------|------------------------------|
| Full project lifecycle (scaffold $\rightarrow$ publish) | **Hatch** |
| Multiple named dev environments | **Hatch** |
| Ultra-fast installs in CI/CD or Docker | **uv** |
| Already using a manager but want speed | **uv** (drop-in) |
| Both orchestration and speed | **Hatch + uv** |

---

## Assignments

!!! note "Assignment: Tooling Migration"
    1. **Project Setup**: Initialize a new project using `hatch new`.
    2. **Dependency Management**: Add three common libraries to `pyproject.toml`.
    3. **Speed Test**: Compare the time taken by `hatch env create` versus creating a venv with `uv venv` and installing the same dependencies via `uv pip install`.
    4. **Hybrid Config**: Implement the hybrid configuration in `pyproject.toml` to use `uv` as the installer for Hatch.
    5. **Verification**: Run `hatch env prune` and then `hatch env create` to verify the speed increase.

---

## Self-Evaluation

??? note "If you need to manage project metadata and publishing, why is Hatch a better choice than uv?"
    Hatch is a full project manager that handles scaffolding, versioning, and publishing to PyPI. `uv` is primarily a high-performance package installer and resolver; it does not manage project metadata or the publishing lifecycle.

??? note "How can you achieve both orchestration (Hatch) and installation speed (uv) in the same project?"
    By configuring Hatch to use `uv` as the internal installer. This can be done by defining a custom script in `pyproject.toml` that invokes `uv pip install` instead of the default pip.

??? note "When is `uv run` more advantageous than traditional virtual environment activation?"
    `uv run` allows executing a script within an environment without manually activating it. It is especially powerful for one-off scripts because it can create a temporary environment, install dependencies, and run the code in a single step.
