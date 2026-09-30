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

## Implementing a CI Pipeline

In a real-world scenario, a CI pipeline doesn't just run a single script; it ensures code quality and model performance through a series of gated stages.

### Python Testing Pipeline

This pipeline installs dependencies, runs a linter, and executes tests.

```yaml
version: 2.1
jobs:
  test:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install Dependencies
          command: |
            pip install flake8 pytest
            pip install -r requirements.txt
      - run:
          name: Lint
          command: flake8 .
      - run:
          name: Run Tests
          command: pytest
```

### AI/ML Pipeline with GPU Acceleration

For AI/ML workloads, standard containers are often insufficient. CircleCI provides **GPU Resource Classes** that allow you to execute training jobs on machines equipped with NVIDIA GPUs.

```yaml
version: 2.1
jobs:
  train-model:
    docker:
      - image: nvidia/cuda:11.8.0-base-ubuntu22.04
    resource_class: gpu.medium # Request a GPU-enabled runner
    steps:
      - checkout
      - run:
          name: Train Model
          command: python train.py --epochs 10
      - run:
          name: Model Validation
          command: |
            ACCURACY=$(python evaluate.py)
            echo "Model Accuracy: $ACCURACY"
            if (( $(echo "$ACCURACY < 0.85" | bc -l) )); then
              echo "Accuracy too low! Failing build."
              exit 1
            fi
```

!!! info "MLOps Best Practice"
    Integrating a **Model Validation** stage directly into your CI pipeline prevents "model regression," ensuring that no model with degraded performance ever reaches your production registry.

!!! tip "Try it in the Lab"
    You can simulate these pipeline patterns using the [Local Lab](/section/devops/local-lab.md) to understand how resource requests and containerized builds function.

## Self-Assessment

## Self-Assessment

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

## Assignments

!!! note "Assignment 1: Project Framework"
    Develop a CircleCI framework for your current project. Define at least two jobs (e.g., `lint` and `test`) and organize them into a workflow where the `test` job only runs if the `lint` job succeeds.

!!! note "Assignment 2: Optimizing with Caching"
    Research CircleCI's `save_cache` and `restore_cache` steps. Modify your configuration to cache your project's dependencies (e.g., `node_modules` or `venv`), and measure the difference in build time before and after adding the cache.

!!! note "Assignment 3: Deploying to a Cloud Provider"
    Use an official Orb (e.g., the AWS or Azure orb) to add a `deploy` job to your workflow. Configure the job to run only when changes are pushed to the `main` branch, ensuring that only stable code reaches production.

---

## What's Next?

CircleCI provides a high-velocity, managed experience for modern teams. To complete your understanding of the CI landscape, explore **Travis CI**, the open-source pioneer that set the stage for the hosted CI movement.

Visit the [Local Lab](/section/devops/local-lab.md) for instructions on how to run CircleCI locally.
