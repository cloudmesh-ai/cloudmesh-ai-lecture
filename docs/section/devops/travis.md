# Testing and CI with Travis CI

!!! info "Learning Objectives"
    - Define Travis CI and its role in the open-source ecosystem.
    - Implement a `.travis.yml` configuration file.
    - Manage the build environment using the `install` and `env` phases.
    - Understand how to execute scripts and makefiles within a CI pipeline.

Travis CI is a hosted continuous integration service that became a staple of the open-source community due to its deep integration with GitHub. It allows developers to automatically test their code every time a commit is pushed, ensuring that new changes do not break existing functionality.

!!! info "Why this matters"
    Travis CI popularized the "Configuration as Code" approach for CI. By placing a `.travis.yml` file in the root of a repository, the build environment is defined by the code itself, not by a manual configuration in a web UI. This makes the build process transparent and reproducible for anyone who forks the project.

## The `.travis.yml` Configuration

Once Travis is activated for a GitHub project, it looks for a `.travis.yml` file. This file tells Travis which language to use, which versions of the OS to test against, and which commands to run.

### Key Configuration Sections

A typical Travis configuration is divided into several phases:

1.  **Language and Version**: Specifies the runtime (e.g., `language: python` or `language: node_js`) and the versions to be tested (e.g., `python: 3.8`).
2.  **Install Phase**: This is where you set up the environment. You can install system-level dependencies, update the OS, or install specific versions of tools (like `pandoc`).
3.  **Environment Variables (`env`)**: Used to define paths or configuration settings that the build scripts need to access.
4.  **Script Phase**: The core part of the build where the actual tests are executed. This often involves calling a `Makefile` or a test runner like `pytest`.

### Practical Example: The Book's Build Process

In the `cloudmesh-ai-lecture` project, the `.travis.yml` file is used to automate the generation of the book's documentation. 

**Key implementation details in our project:**
- **OS Updates**: Since some Travis environments may use older OS versions, the `install` phase is used to update the operating system and install the latest version of `pandoc`.
- **PATH Management**: The `env` section is used to ensure that custom executables are correctly located by the system.
- **Simplified Execution**: Because the project uses sophisticated `Makefiles`, the `script` section is kept simple, merely calling the appropriate `make` commands in the relevant directories.

# Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "How does Travis CI integrate with GitHub?"
    Travis CI integrates with GitHub by listening for events (like `git push` or `pull_request`). When a change is committed to a repository that has Travis CI activated, GitHub notifies Travis, which then automatically triggers a build based on the instructions in the repository's configuration file.

??? question "What is the purpose of the `.travis.yml` file?"
    The `.travis.yml` file is a \"Configuration as Code\" document. It defines the entire build environment—including the programming language, the specific OS versions to test against, any required system dependencies, and the exact shell commands needed to execute the test suite.

??? question "What is the difference between the `install` phase and the `script` phase?"
    The **Install phase** is used for environment preparation, such as updating the operating system, installing system-level libraries, or setting up a virtual environment. The **Script phase** is the core of the pipeline where the actual tests are executed (e.g., running `pytest` or calling a `Makefile`), and its exit code determines if the build passed or failed.

??? question "How do I use the `env` section to manage system paths or configuration?"
    The `env` section allows you to define environment variables that are made available to all subsequent steps in the pipeline. This is particularly useful for specifying custom `PATH` entries to locate executables, defining API endpoints, or setting configuration flags without hardcoding them into the build scripts.

??? question "Why can using a `Makefile` simplify a CI configuration?"
    A `Makefile` allows you to move complex, multi-line shell commands out of the `.travis.yml` file and into a version-controlled script within the repository. This simplifies the CI configuration to a few simple calls (e.g., `make test`), making the pipeline easier to read, maintain, and execute locally by developers.

!!! note "Assignment 1: Containerized Travis"
    Develop an alternative `.travis.yml` file that uses a preconfigured Docker container (e.g., for Ubuntu 18.04) instead of the default Travis environment. Explain the advantage of using a container for environment consistency.

!!! note "Assignment 2: Multi-OS Testing"
    Create a Travis configuration that tests a project across multiple operating systems (e.g., macOS and Ubuntu). Describe how Travis handles the "matrix" of different OS and language version combinations.

!!! note "Assignment 3: Custom Installation"
    Write a `.travis.yml` file for a project that requires a specific version of a system library (e.g., `libssl-dev`). Ensure the library is installed during the `install` phase and verify its installation in the `script` phase.

## Resources

- Travis CI Official Documentation: [docs.travis-ci.com](https://docs.travis-ci.com/)

---

## Appendix: Local Deployment with Travis CI

### 0. Clone the Repository
Before running the automation, clone the course repository to your local machine:

```bash
git clone https://github.com/cloudmesh-ai/cloudmesh-ai-lecture.git
cd cloudmesh-ai-lecture
```


Travis CI is primarily a cloud-based CI service, but its "Configuration as Code" philosophy using `.travis.yml` can be applied to standardize the deployment of the `cloudmesh-ai-lecture` site. By defining the environment and execution steps in a YAML file, we ensure that the site is served identically regardless of the environment.

### 1. The Travis Configuration
Create a `.travis.yml` file in the root of the project. This file defines the language, the installation phase for dependencies, and the script to launch the server.

```yaml
language: python
python:
  - "3.11"

# Install required MkDocs plugins and dependencies
install:
  - pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions

# Launch the server and open the browser
script:
  - nohup mkdocs serve -a 0.0.0.0:8000 > travis_mkdocs.log 2>&1 &
  - sleep 5 # Give the server a few seconds to start
  - open http://localhost:8000 || xdg-open http://localhost:8000
```

### 2. Execution
While Travis CI usually triggers on a Git push, you can simulate the `install` and `script` phases locally by running the commands defined in the `.travis.yml` file:

```bash
# Simulate 'install' phase
pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions

# Simulate 'script' phase
nohup mkdocs serve -a 0.0.0.0:8000 > travis_mkdocs.log 2>&1 &
open http://localhost:8000
```

### Why use Travis CI for this?
Travis CI's power lies in its **transparent build process**. By documenting the deployment in `.travis.yml`, any contributor to the `cloudmesh-ai-lecture` project can immediately see exactly which dependencies are required to run the site locally, eliminating the "it works on my machine" problem.
