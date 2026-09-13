# 6. REST Tooling

!!! info "Learning Objectives"
    - Choose the right tool for the task (debugging, testing, or documenting).
    - Use CLI tools for lightweight testing.
    - Leverage GUI clients for complex API workflows.

---

## The REST Tooling Landscape

Depending on whether you are a developer, a tester, or a DevOps engineer, you will need different tools to interact with a REST API.

### 1. Command Line Interface (CLI) Tools
CLI tools are lightweight, fast, and can be easily integrated into shell scripts or CI/CD pipelines.

| Tool | Best For | Key Advantage |
|------|----------|---------------|
| `curl` | Quick checks, CI/CD | Installed by default on almost every OS. |
| `HTTPie` | Human-readable testing | Auto-pretty JSON, intuitive syntax. |

**Example using `curl`:**
```bash
curl -X GET http://localhost:8080/computers/computer1
```

**Example using `HTTPie`:**
```bash
http GET localhost:8080/computers/computer1
```

### 2. GUI API Clients
GUI clients are essential for complex testing, maintaining collections of requests, and collaborating with teams.

| Tool | Best For | Key Features |
|------|----------|---------------|
| **Postman** | Full API lifecycle | Collections, Environment variables, Automated testing, Monitoring. |
| **Insomnia** | Simple, clean experience | Lightweight, great for rapid prototyping. |

### 3. Documentation & Playground Tools
These tools allow you to "try" the API without writing any code.

- **Swagger UI**: Generated from an OpenAPI spec. It provides a visual list of all endpoints and allows you to send real requests and see the responses.
- **ReDoc**: Focuses on creating high-quality, clean, and readable documentation from OpenAPI specs.

---

## Summary: Which Tool to Use?

| If you need... | Recommended Tool |
|---------------|------------------|
| **To quickly check an endpoint** | `curl` or `HTTPie` |
| **To build a test suite for a team** | Postman |
| **To document your API for external developers** | OpenAPI Spec $\rightarrow$ Swagger UI |
| **To automate API tests in Jenkins/GitHub Actions** | `curl` or Postman CLI (Newman) |


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "When is a CLI tool like `curl` preferred over a GUI client like Postman?"
    `curl` is preferred for quick checks, lightweight testing, and especially when integrating API calls into shell scripts or CI/CD pipelines where a graphical interface is not available.

??? question "What is the primary advantage of `HTTPie` over `curl` for manual testing?"
    `HTTPie` provides a more intuitive, human-readable syntax and automatically pretty-prints JSON responses, making it significantly faster and easier for developers to read and write requests manually.

??? question "How do tools like Swagger UI facilitate 'trying out' an API without writing code?"
    Swagger UI reads the OpenAPI specification to present a visual list of all endpoints. It allows developers to enter parameters and click a "Try it out" button to send real HTTP requests to the server and see the live responses instantly.

??? question "In a CI/CD pipeline, which tool is most likely to be used for automated API smoke tests?"
    `curl` or a CLI-based tool like Postman's Newman are most likely to be used, as they can be easily executed in headless environments and their output can be parsed by the pipeline for success/failure.

??? question "Contrast the focus of Swagger UI with that of ReDoc."
    **Swagger UI** focuses on interactivity and testing, providing a "playground" for developers. **ReDoc** focuses on presentation, creating clean, high-quality, and readable documentation optimized for consumption rather than experimentation.

