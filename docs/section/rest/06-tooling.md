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
