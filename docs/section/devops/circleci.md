# Continuous Integration with CircleCI

!!! info "Learning Objectives"
    - Define CircleCI and its place in the DevOps toolchain.
    - Understand the structure and purpose of the `.circleci/config.yml` file.
    - Implement a basic automated build and test pipeline.
    - Explore the concept of "Orbs" for reusable configuration.

In the quest for faster delivery cycles, managing your own CI server (like Jenkins) can sometimes become a project in itself. CircleCI is a hosted Continuous Integration and Continuous Deployment platform that removes the overhead of server maintenance, allowing teams to focus entirely on their code and delivery pipelines.

!!! info "Why this matters"
    For many teams, the "time to first green build" is a critical metric. Because CircleCI is a managed service with deep integration into GitHub and Bitbucket, you can move from a raw repository to a fully automated test suite in minutes. This "zero-infrastructure" approach reduces the barrier to entry for implementing rigorous testing practices.

## The CircleCI Configuration

At the heart of every CircleCI project is the `.circleci/config.yml` file. This file defines the entire automation process in a declarative YAML format.

### The Pipeline Structure

A typical CircleCI configuration is broken down into three main components:

1.  **Orbs**: Reusable snippets of configuration shared by the community or vendors (e.g., an AWS orb to handle S3 uploads).
2.  **Jobs**: The actual work to be done. A job might be "run unit tests," "lint code," or "deploy to staging." Each job runs in its own isolated container.
3.  **Workflows**: The orchestration layer that defines the order in which jobs run. Workflows can be simple sequences or complex directed acyclic graphs (DAGs) where jobs run in parallel.

### Example: A Basic Pipeline

```yaml
version: 2.1
orbs:
  nodejs: circleci/nodejs@5.0

jobs:
  build:
    docker:
      - image: cimg/node:16.10
    steps:
      - checkout
      - nodejs/install-packages
      - run: npm test

workflows:
  sample:
    jobs:
      - build
```

## Building Your First Pipeline

Implementing CircleCI generally follows these steps:

1.  **Connect your Repository**: Grant CircleCI access to your GitHub/Bitbucket account.
2.  **Define the Config**: Create the `.circleci/config.yml` file in your project root.
3.  **Trigger the Build**: Push the config file to your main branch. CircleCI will automatically detect the change and start the pipeline.
4.  **Iterate**: Use the CircleCI dashboard to view logs, identify failures, and optimize your build times using caching.

# Self-Assessment

!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the difference between a hosted CI (CircleCI) and a self-hosted CI (Jenkins)?"
    A hosted CI like CircleCI is a managed service (SaaS), meaning the platform provider handles the infrastructure, updates, and maintenance, allowing teams to focus on their pipelines. A self-hosted CI like Jenkins requires the user to provision, secure, and maintain the build servers, offering more control but increasing operational overhead.

??? question "What is the role of the .circleci/config.yml file?"
    The `.circleci/config.yml` file is the heart of a CircleCI project. It is a declarative YAML document that defines the entire automation process, including the environment (Docker images), the specific steps to be executed (Jobs), and the order in which they run (Workflows).

??? question "What is the difference between a Job and a Workflow in CircleCI?"
    A **Job** is a collection of steps that run in a single isolated container (e.g., "run unit tests"). A **Workflow** is the orchestration layer that manages how these jobs are executed—whether they run in a linear sequence, in parallel, or as a complex graph (DAG) where some jobs depend on others.

??? question "How do 'Orbs' help reduce configuration duplication?"
    Orbs are reusable, shareable snippets of configuration created by CircleCI or third-party vendors. Instead of writing complex YAML for common tasks (like deploying to AWS or sending a Slack notification), you can simply "import" an Orb and call its predefined commands, which drastically simplifies the `config.yml` file.

??? question "How do I trigger a build in CircleCI?"
    Builds in CircleCI are typically triggered automatically by events in the connected source control provider (e.g., a `git push` to any branch or a `pull_request` event). Once the `.circleci/config.yml` is pushed to the repository, CircleCI detects the change and initiates the pipeline.

!!! note "Assignment 1: Project Framework"
    Develop a CircleCI framework for your current project. Define at least two jobs (e.g., `lint` and `test`) and organize them into a workflow where the `test` job only runs if the `lint` job succeeds.

!!! note "Assignment 2: Optimizing with Caching"
    Research CircleCI's `save_cache` and `restore_cache` steps. Modify your configuration to cache your project's dependencies (e.g., `node_modules` or `venv`), and measure the difference in build time before and after adding the cache.

!!! note "Assignment 3: Deploying to a Cloud Provider"
    Use an official Orb (e.g., the AWS or Azure orb) to add a `deploy` job to your workflow. Configure the job to run only when changes are pushed to the `main` branch, ensuring that only stable code reaches production.

---

## Appendix: Local Deployment with CircleCI

### 0. Clone the Repository
Before running the automation, clone the course repository to your local machine:

```bash
git clone https://github.com/cloudmesh-ai/cloudmesh-ai-lecture.git
cd cloudmesh-ai-lecture
```


CircleCI is a hosted platform, but you can simulate the deployment process locally using a **CircleCI Runner**. This allows you to test your CI configuration on your own machine before pushing it to GitHub.

### 1. The Configuration
Create a `.circleci/config.yml` file in your project root. This configuration defines a job that prepares the environment and launches the site.

```yaml
version: 2.1

jobs:
  deploy_local:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install Dependencies
          command: pip install mkdocs-material mkdocs-video mkdocs-slides mkdocs-caption mkdocs-blog pymdown-extensions
      - run:
          name: Serve Site
          command: |
            nohup mkdocs serve -a 0.0.0.0:8000 > circleci_mkdocs.log 2>&1 &
            echo "Site is serving at http://localhost:8000"
      - run:
          name: Open Browser
          command: open http://localhost:8000 || xdg-open http://localhost:8000

workflows:
  local_dev:
    jobs:
      - deploy_local
```

### 2. Execution with Local Runner
To execute this locally, you would use the CircleCI local CLI:

```bash
circleci local execute --job deploy_local
```

### Why use CircleCI for this?
CircleCI's strength is its **container-first approach**. By defining your deployment in a `config.yml`, you ensure that the environment (OS, Python version, and plugins) is identical regardless of whether the site is being served on your laptop or in a cloud-based preview environment.
