# Automated Testing with pytest in a DevOps Workflow

!!! info "Learning Objectives"
    - Implement unit tests using `pytest` fixtures and parametrization.
    - Design an automated testing strategy covering unit, integration, and E2E levels.
    - Integrate `pytest` into CI/CD pipelines for GitHub Actions, GitLab CI, and Azure Pipelines.
    - Apply advanced `pytest` patterns like parallel execution and markers to optimize pipeline speed.
    - Identify and mitigate common testing pitfalls in DevOps environments.

In a DevOps organization, the delivery pipeline is expected to move code from a developer's workstation to production many times per day. Each change must be verified automatically before it is allowed to proceed to the next stage (build, integration, deployment). While infrastructure-as-code, containerization, and continuous delivery tools receive a lot of attention, automated testing is the non-negotiable foundation that guarantees the quality of every commit.

`pytest` is the de-facto standard testing framework for Python. Its rich feature set, extensibility, and native support for fixtures make it suitable for unit, integration, and end-to-end (E2E) tests, all of which can be expressed in a single, consistent syntax.

!!! info "Why this matters"
    Without an automated test suite, a single regression can silently propagate through the pipeline, causing outages, data corruption, or security breaches once the code reaches production. The cost of fixing a defect discovered in production is an order of magnitude higher than fixing it during the test phase.

## Levels of Automated Testing

A robust DevOps strategy employs multiple levels of testing to balance speed and confidence.

| Test type | Goal | Typical scope | Where pytest fits |
|-----------|------|---------------|-------------------|
| **Unit** | Verify the behavior of a single function or class in isolation. | Mocked dependencies, fast execution (< 0.1s per test). | Core `pytest` usage with fixtures and parametrization. |
| **Integration** | Validate interaction between two or more components (e.g., database, external API). | Real or sandboxed services, may involve network I/O. | `pytest` with `pytest-asyncio`, `pytest-django`, `pytest-mock`, Docker-compose fixtures, etc. |
| **End-to-End (E2E)** | Exercise the whole system through its public interface (HTTP, CLI, UI). | Full stack, possibly in a test environment that mirrors production. | `pytest` + Selenium, Playwright, or `requests` for API calls; can be orchestrated from CI pipelines. |

Each layer provides a safety net: unit tests catch logic errors early, integration tests expose contract mismatches, and E2E tests ensure the user-facing behavior remains correct.

!!! info "Why this matters"
    Following the "Testing Pyramid" (many unit tests, fewer integration tests, and even fewer E2E tests) ensures that the test suite remains fast enough for developers to run locally while still providing high confidence in the overall system stability.

## Getting Started with pytest

### Installation

To get started, install `pytest` via pip:

```bash
pip install pytest
```

For a professional DevOps pipeline, the following extensions are recommended:

```bash
pip install pytest-cov          # Code-coverage reporting
pip install pytest-mock         # Simple mocking utilities
pip install pytest-asyncio      # Async test support
pip install pytest-xdist        # Parallel test execution
```

All extensions are pure Python and should be locked in `requirements-dev.txt` or a `pyproject.toml` file to ensure environment consistency across the team and CI agents.

### Project Layout

A conventional layout ensures that `pytest` can automatically discover tests and that the production code is correctly packaged.

```
my_service/
├─ src/
│  └─ my_service/
│     ├─ __init__.py
│     └─ calculator.py
├─ tests/
│  ├─ __init__.py
│  └─ test_calculator.py
├─ pyproject.toml
└─ requirements.txt
```

- `src/` contains the production code, imported as a package.
- `tests/` stores all test modules; any file that matches `test_*.py` or `*_test.py` is automatically discovered.

!!! info "Why this matters"
    A standardized project layout prevents "import hell" in CI pipelines and allows the testing framework to find tests without requiring complex configuration files.

## Creating Effective Tests

Effective tests should be isolated, deterministic, and concise. We can demonstrate this using a simple calculator module.

### Production Code

The following code in `src/my_service/calculator.py` provides basic arithmetic operations.

```python
def add(a: int, b: int) -> int:
    """Return the sum of two integers."""
    return a + b


def divide(numerator: int, denominator: int) -> float:
    """Return the division of two integers, raising ZeroDivisionError on a zero denominator."""
    return numerator / denominator
```

### Basic Tests and Fixtures

Instead of hard-coding data in every test, `pytest` uses fixtures to provide a reliable baseline of data or state.

```python
import pytest
from my_service.calculator import add, divide


@pytest.fixture
def sample_numbers():
    """Provide a set of numbers for arithmetic tests."""
    return (3, 7)


def test_add_basic(sample_numbers):
    a, b = sample_numbers
    assert add(a, b) == 10
```

!!! info "Why this matters"
    Fixtures decouple the test logic from the test data. If the data source changes (e.g., switching from a hard-coded tuple to a database record), you only need to update the fixture, not every individual test.

### Data-Driven Testing with Parametrization

To test multiple scenarios without writing multiple functions, use `@pytest.mark.parametrize`.

```python
@pytest.mark.parametrize(
    "num, den, expected",
    [
        (10, 2, 5.0),
        (9, 3, 3.0),
        (5, -1, -5.0),
    ],
)
def test_divide_various(num, den, expected):
    assert divide(num, den) == expected
```

!!! info "Why this matters"
    Parametrization increases test coverage significantly while reducing code duplication. Each tuple in the list is treated as a separate test case, making it easy to identify exactly which input caused a failure.

### Handling Exceptions

Testing for failure is as important as testing for success. Use `pytest.raises` to verify that the code fails under the correct conditions.

```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
```

## Running and Orchestrating Tests

### Local Execution

Developers should run tests locally before pushing code. Use the `-q` (quiet) flag to reduce noise.

```bash
# From the project root
pytest -q
```

### Continuous Integration

In a DevOps workflow, tests are executed automatically on every push. The goal is to "shift-left" the detection of bugs by catching them as early as possible in the pipeline.

#### GitHub Actions

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
```

#### GitLab CI

```yaml
stages:
  - test

pytest:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
    - pytest --cov=src --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
    paths:
      - coverage.xml
```

#### Azure Pipelines

```yaml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.12'

- script: |
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    pytest --cov=src --junitxml=results.xml
  displayName: 'Run pytest with coverage'

- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'results.xml'
    testRunTitle: 'pytest results'
```

!!! info "Why this matters"
    Integrating tests into the CI/CD pipeline ensures that no code reaches production without passing the quality gate. Generating JUnit XML and coverage reports allows teams to track quality trends over time via dashboards.

## Advanced DevOps Testing Patterns

As a test suite grows, execution time can become a bottleneck. Advanced patterns help maintain pipeline speed.

| Practice | Description | Benefit |
|----------|-------------|---------|
| **Parallel execution (`-n`)** | `pytest -n auto` runs tests in multiple processes. | Reduces total test time, speeding up the pipeline. |
| **Test selection (`-m`)** | Use custom markers (`@pytest.mark.integration`) and run `pytest -m integration`. | Allows separating fast unit tests from slower integration/E2E tests. |
| **Environment isolation** | Run tests inside Docker containers or use `pytest-docker`. | Guarantees that external services have a known state. |
| **Fail-fast (`-x`)** | Stop the suite after the first failure. | Gives immediate feedback on broken builds, saving CI resources. |
| **Reporting plugins** | `pytest-html`, `pytest-metadata`, `pytest-allure`. | Produce rich HTML reports for auditing and debugging. |
| **Static analysis** | Combine `pytest` with `ruff` or `flake8` via `pre-commit`. | Enforces code style and type correctness in one stage. |

## Common Pitfalls

Avoiding these common mistakes prevents "flaky" tests and pipeline bottlenecks.

!!! warning "Pipeline Bottlenecks"
    Running the full integration/E2E suite on every push can dramatically increase CI duration.
    
    *Solution*: Tag slower tests with `@pytest.mark.slow` and configure CI to execute them only on a scheduled nightly run or on `main` merges.

!!! warning "Secret Leakage"
    Hard-coding credentials or endpoints inside tests exposes sensitive data in the version control system.
    
    *Solution*: Use `pytest` fixtures that read from environment variables or a secret manager.

!!! warning "Order Dependence"
    Tests that depend on the execution order of other tests are non-deterministic and hard to debug.
    
    *Solution*: Ensure each test is idempotent. Avoid shared mutable state between tests. If shared state is unavoidable, reset it in a fixture with `scope="function"` or `autouse=True`.

## End-to-End Testing in Containers

E2E tests verify the system as a whole. In a DevOps environment, this typically involves orchestrating a real service using Docker Compose.

```python
import subprocess
import time
import requests
import pytest


@pytest.fixture(scope="session")
def docker_service():
    """Start the Docker-Compose stack for the duration of the test session."""
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    # Wait for the service to become healthy (simple polling)
    for _ in range(30):
        try:
            r = requests.get("http://localhost:8000/health")
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        pytest.fail("Service did not become healthy in time")
    yield
    subprocess.run(["docker", "compose", "down"], check=True)


def test_api_add(docker_service):
    payload = {"a": 4, "b": 6}
    resp = requests.post("http://localhost:8000/add", json=payload)
    assert resp.status_code == 200
    assert resp.json() == {"result": 10}
```

The `scope="session"` setting on the `docker_service` fixture is critical; it ensures the Docker stack is started once for the entire test run rather than for every single test, which would be prohibitively slow.

!!! tip "Summary Checklist"
    - [ ] I can write a basic `pytest` test file with assertions and fixtures.
    - [ ] I understand how to parametrize tests to cover multiple input combinations.
    - [ ] I know how to integrate `pytest` into GitHub Actions, GitLab CI, and Azure Pipelines.
    - [ ] I can configure parallel execution and selective test runs using markers.
    - [ ] I am aware of common pitfalls (test order dependence, hard-coded secrets) and how to mitigate them.
    - [ ] I can extend the suite to include integration and end-to-end tests that run inside Docker containers.

!!! note "Assignment 1: Basic Unit Tests"


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What is the \"Testing Pyramid\" and why is it important for a DevOps pipeline?"
    It is a strategy that recommends having many fast unit tests, fewer integration tests, and very few slow E2E tests. This balances comprehensive coverage with a fast feedback loop for developers.

??? question "How do `pytest` fixtures improve test maintainability?"
    Fixtures allow for the definition of reusable setup and teardown logic (e.g., initializing a database) that can be shared across multiple tests and scoped to the function, class, module, or session.

??? question "Why is it dangerous to hard-code credentials in tests, and what is the recommended alternative?"
    Hard-coding secrets exposes them in version control. The alternative is to use fixtures that retrieve credentials from environment variables or a secure secret manager at runtime.

    Create a simple Python module `math_utils.py` with functions for `multiply` and `power`. Write a corresponding `test_math_utils.py` using `pytest` to verify the correct output for basic positive and negative integers.

!!! note "Assignment 2: Parametrized Testing"
    Expand your `math_utils.py` to include a function that checks if a number is prime. Use `@pytest.mark.parametrize` to test this function with at least 10 different inputs, including prime numbers, composite numbers, and edge cases (e.g., 0, 1, and negative numbers).

!!! note "Assignment 3: Mocking and Integration"
    Create a function that fetches data from a public API (e.g., JSONPlaceholder). Write a test using `pytest-mock` to mock the `requests.get` call, simulating both a successful 200 OK response and a 404 Not Found error to verify your function's error handling.
