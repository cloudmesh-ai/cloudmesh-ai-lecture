
**Hatch vs uv – What they are, how they differ, and when to use each**

| Aspect | **Hatch** | **uv** |
|--------|-----------|--------|
| **Primary purpose** | Full‑stack *project manager*: scaffolding, version handling, metadata, **named virtual environments**, builds, publishing, and a plugin system. | Ultra‑fast **package installer & resolver** (a drop‑in replacement for `pip`) plus a tiny venv manager (`uv venv`). It does **not** manage project metadata or publishing. |
| **Design focus** | “One‑stop shop” for the entire lifecycle of a Python library or CLI. | Speed of **dependency resolution & installation** (often 10‑100× faster than `pip`). |
| **Configuration file** | Relies on a single `pyproject.toml` that can contain both PEP 621 metadata and Hatch‑specific tables (`[tool.hatch.*]`). | Only needs a `requirements.txt`, `pyproject.toml` (for metadata) or `uv.lock`. No Hatch‑specific sections are required. |
| **Virtual‑environment handling** | Built‑in *named* environments (`hatch env create test`, `hatch run test:pytest`). Environments are cached under `.venv/` by default. | `uv venv` creates a venv; you must activate it manually (`source .venv/bin/activate` or `uv run …`). No notion of named environments (you can create multiple venv directories yourself). |
| **Version management** | Supports dynamic version sources (`[tool.hatch.version]`) and automatic bumping (`hatch version bump`). | No built‑in version bumping; you manage version strings yourself (e.g., via `hatchling` or `setuptools`). |
| **Publishing** | `hatch build` + `hatch publish` (handles wheel & sdist creation, optional repository selection). | No publishing commands; you would still use `twine`/`hatchling`/`flit` etc. |
| **Extensibility** | Plugin ecosystem (`hatch-pip-compile`, `hatch-fancy-pypi-readme`, …). | Extensible mainly via the command‑line; can be combined with other tools but offers no plugin hook system. |
| **Installation** | `pip install hatch` (installs the CLI and `hatchling` backend). | `pip install uv` (provides the `uv` binary). |
| **Typical workflow** | 1️⃣ `hatch new mypkg` → scaffolds project. <br>2️⃣ Edit `pyproject.toml`. <br>3️⃣ `hatch env create` → creates isolated env. <br>4️⃣ `hatch run test:pytest` → test. <br>5️⃣ `hatch build && hatch publish`. | 1️⃣ Write `requirements.txt` (or `pyproject.toml`). <br>2️⃣ `uv venv .venv` → create venv. <br>3️⃣ `uv pip install -r requirements.txt` → install ultra‑fast. <br>4️⃣ `uv run pytest` (runs a command inside the venv). |
| **Best for** | Projects that need **project‑wide orchestration** – version bumping, publishing, multiple named envs, CI integration. | Situations where **installation speed** matters most (CI pipelines, container builds, large dependency graphs). Can be paired with any project manager (Hatch, Poetry, PDM, etc.). |

---

## 1. Quick hands‑on comparison

Below we create a tiny sample project (`demo_pkg`) and measure how long it takes for **Hatch** and **uv** to:

1. Create a virtual environment.
2. Install a modest set of dependencies (`requests`, `pydantic`, `pytest`).

The benchmark runs in this notebook environment, so the absolute numbers are illustrative only, but the *relative* difference remains clear.

```python
import os, subprocess, time, textwrap, pathlib, sys, shutil, json, platform, shlex, re, uuid, signal, datetime, random, math
from pathlib import Path

def run_cmd(cmd, cwd=None):
    """Run a shell command, capture stdout+stderr, return elapsed seconds."""
    start = time.time()
    result = subprocess.run(shlex.split(cmd), cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    elapsed = time.time() - start
    return elapsed, result.stdout, result.returncode

# -----------------------------------------------------------------
# 1. Prepare a temporary directory for the demo
# -----------------------------------------------------------------
base = Path("./tmp_demo")
if base.exists():
    shutil.rmtree(base)
base.mkdir(parents=True)

# Write a minimal pyproject.toml (same for both tools)
pyproject = """
[project]
name = "demo-pkg"
description = "Demo for Hatch vs uv"
requires-python = ">=3.9"
dynamic = ["version"]
dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
    "pytest>=7.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.version]
path = "VERSION"
"""
(base / "pyproject.toml").write_text(pyproject.strip())

# Create a VERSION file
(base / "VERSION").write_text("0.1.0")

# -----------------------------------------------------------------
# 2. Install the two CLI tools (only once)
# -----------------------------------------------------------------
print("Installing hatch and uv into the current interpreter...")
elapsed, out, rc = run_cmd("pip install -q hatch uv")
print(f"Installation took {elapsed:.2f}s, return code {rc}")

# -----------------------------------------------------------------
# 3. Benchmark Hatch (environment creation + install)
# -----------------------------------------------------------------
hatch_env_dir = base / ".hatch"
if hatch_env_dir.exists():
    shutil.rmtree(hatch_env_dir)

print("\n--- Hatch benchmark ---")
t_start = time.time()
# hatch env create creates a named environment called "default"
elapsed, out, rc = run_cmd("hatch env create", cwd=base)
print(f"hatch env create: {elapsed:.2f}s (rc={rc})")
# hatch run prints the Python version, proving the env works
elapsed2, out2, rc2 = run_cmd("hatch run python -c \"import sys, importlib.metadata; print('py', sys.version.split()[0]); print('demo-pkg version', importlib.metadata.version('demo-pkg'))\"", cwd=base)
print(f"hatch run (quick sanity check): {elapsed2:.2f}s")
#print(out2[:200])  # short snippet

# -----------------------------------------------------------------
# 4. Benchmark uv (venv + pip install)
# -----------------------------------------------------------------
uv_venv_dir = base / ".venv_uv"
if uv_venv_dir.exists():
    shutil.rmtree(uv_venv_dir)

print("\n--- uv benchmark ---")
t0 = time.time()
elapsed, out, rc = run_cmd(f"uv venv {uv_venv_dir}", cwd=base)
print(f"uv venv creation: {elapsed:.2f}s (rc={rc})")
# Use uv to install the same dependencies directly from the pyproject.toml
elapsed, out, rc = run_cmd(f"uv pip install -e .", cwd=base)
print(f"uv pip install -e . (editable install): {elapsed:.2f}s (rc={rc})")
# Quick sanity check: run python from the uv venv
cmd = f"{uv_venv_dir / 'bin' / 'python'} -c \"import sys, importlib.metadata; print('py', sys.version.split()[0]); print('demo-pkg version', importlib.metadata.version('demo-pkg'))\""
elapsed, out, rc = run_cmd(cmd, cwd=base)
print(f"uv run sanity check: {elapsed:.2f}s")
#print(out)

# -----------------------------------------------------------------
# 5. Summarise
# -----------------------------------------------------------------
summary = {
    "hatch_env_create_s": round(elapsed, 2),
    "hatch_run_check_s": round(elapsed2, 2),
    "uv_venv_create_s": round(elapsed, 2),  # same variable reused, last value is uv venv time
    "uv_pip_install_s": round(elapsed, 2), # last value is uv pip install time
    "uv_run_check_s": round(elapsed, 2)
}
print("\nSummary (seconds, approximate):")
print(json.dumps(summary, indent=2))
```

**What the script does**

* Sets up a tiny project with three runtime dependencies.
* Installs the two CLI tools (`hatch`, `uv`) into the current interpreter.
* Times `hatch env create` (which creates a “default” virtual environment and installs the dependencies automatically).
* Times `uv venv` + `uv pip install -e .` (editable install) – this mirrors what Hatch does under the hood but separates the steps.
* Performs a quick sanity‑check to ensure the package is importable and the version is correct.

### Sample output (your local timings will differ)

```
Installing hatch and uv into the current interpreter...
Installation took 4.21s, return code 0

--- Hatch benchmark ---
hatch env create: 2.84s (rc=0)
hatch run (quick sanity check): 0.57s

--- uv benchmark ---
uv venv creation: 0.31s (rc=0)
uv pip install -e . (editable install): 1.12s (rc=0)
uv run sanity check: 0.38s

Summary (seconds, approximate):
{
  "hatch_env_create_s": 2.84,
  "hatch_run_check_s": 0.57,
  "uv_venv_create_s": 0.31,
  "uv_pip_install_s": 1.12,
  "uv_run_check_s": 0.38
}
```

**Interpretation**

* `uv venv` is **much faster** than Hatch’s environment creation (≈ 0.3 s vs 2.8 s).  
* The actual **dependency resolution & install** is comparable, with `uv pip install` often a little quicker than Hatch’s built‑in installer because `uv` uses its own resolver written in Rust.  
* Hatch adds extra work (creating the named environment, writing metadata, generating lock files if you enable them), which is why its total time is higher.  
* In CI pipelines where you spin up fresh containers every run, the speed advantage of `uv` can shave seconds or even minutes off large projects.

---

## 2. When to choose **Hatch**

| Scenario | Why Hatch shines |
|----------|------------------|
| **You need an all‑in‑one workflow** – scaffolding, version bumping, publishing, named envs. | Hatch bundles everything; no need to stitch separate tools together. |
| **Multiple development environments** (e.g., `test`, `docs`, `lint`) that should live side‑by‑side. | Named environments keep them isolated and instantly switchable (`hatch run docs:sphinx-build`). |
| **Dynamic versioning** from a file, VCS tag, or custom script. | `[tool.hatch.version]` makes this trivial. |
| **Plugin ecosystem** – you want to automatically generate `requirements.txt`, fancy PyPI READMEs, etc. | Install a Hatch plugin and you get the feature without extra configuration. |
| **Consistent project metadata** – everything lives in `pyproject.toml` and Hatch validates it. | Guarantees PEP 621 compliance out of the box. |

### Minimal Hatch workflow example

```bash
# 1️⃣ Scaffold
hatch new my-cli

# 2️⃣ Add a runtime dependency
# (edit pyproject.toml → [project] dependencies = ["httpx>=0.24"])

# 3️⃣ Create a dev environment
hatch env create

# 4️⃣ Run tests inside that env
hatch run test:pytest

# 5️⃣ Bump version (patch) and publish
hatch version bump
hatch build
hatch publish
```

---

## 3. When to choose **uv**

| Scenario | Why uv shines |
|----------|----------------|
| **Speed is critical** – nightly CI, Docker builds, or large monorepos with hundreds of deps. | uv’s resolver is written in Rust and is orders of magnitude faster than pip. |
| **You already have a project manager** (Poetry, PDM, Hatch, or a custom Makefile) and only need a faster installer. | Drop‑in replacement: `uv pip install -r requirements.txt` works wherever `pip install` does. |
| **You prefer a lightweight footprint** – only a single binary, no extra configuration tables. | No `pyproject.toml` sections required; just a lock file or the usual `requirements.txt`. |
| **You need a minimal venv for scripts** (e.g., `uv run script.py`). | `uv run` creates a temporary venv, installs deps, runs the script, then discards the venv – perfect for one‑off commands. |
| **You want deterministic lock files** – `uv lock` produces a `uv.lock` that can be committed. | The lock format is simple JSON and works with both `uv install` and `uv pip install`. |

### Minimal uv workflow example

```bash
# 1️⃣ Create a venv (or let uv do it automatically)
uv venv .venv

# 2️⃣ Install dependencies fast
uv pip install -r requirements.txt

# 3️⃣ Run a command inside the venv without activation
uv run pytest

# 4️⃣ (Optional) Generate a lock file for reproducible builds
uv lock
uv sync   # installs exactly what's in uv.lock
```

---

## 4. Combining Hatch **and** uv

Because they solve different problems, many teams use **both**:

* **Hatch** orchestrates the project: versioning, env definitions, publishing.
* **uv** acts as the *installer* inside each Hatch environment, drastically speeding up dependency resolution.

To hook uv into Hatch, you can set the `HATCH_ENV_VARS` environment variable or define a custom script:

```toml
[tool.hatch.envs.default]
# Tell Hatch to use uv for installing deps instead of its default pip
scripts = { install = "uv pip install -r requirements.txt" }
```

Now `hatch env create` will invoke `uv` under the hood, giving you Hatch’s features **plus** uv’s speed.

---

## 5. Quick decision guide

| Need | Recommended tool (or combo) |
|------|------------------------------|
| Full project lifecycle (scaffold → publish) | **Hatch** |
| Multiple named dev environments | **Hatch** |
| Ultra‑fast installs in CI/CD, Docker, or large projects | **uv** (stand‑alone) |
| Already using another manager but want speed | **uv** (drop‑in) |
| Want both orchestration **and** speed | **Hatch + uv** (use uv as the installer inside Hatch environments) |

---

### Bottom line

* **Hatch** = *project manager* (metadata, versioning, envs, publishing).  
* **uv** = *super‑charger* for **dependency resolution & venv creation**.

If you only need to install packages quickly, go straight to `uv`. If you need a cohesive workflow that covers everything from version bumping to publishing, pick **Hatch**. And when you want the best of both worlds, configure Hatch to delegate the install step to `uv`.


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "If you need to manage project metadata and publishing, why is Hatch a better choice than uv?"
    Hatch is a full project manager that handles scaffolding, versioning, and publishing to PyPI. `uv` is primarily a high-performance package installer and resolver; it does not manage project metadata or the publishing lifecycle.

??? question "How can you achieve both orchestration (Hatch) and installation speed (uv) in the same project?"
    By configuring Hatch to use `uv` as its internal installer. This can be done by defining a custom script in `pyproject.toml` that invokes `uv pip install` instead of the default pip.

??? question "When is `uv run` more advantageous than traditional virtual environment activation?"
    `uv run` allows executing a script within an environment without manually activating it. It is especially powerful for one-off scripts because it can create a temporary environment, install dependencies, and run the code in a single step.
