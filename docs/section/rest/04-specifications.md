# 4. API Specifications & OpenAPI

!!! info "Learning Objectives"
    - Understand why API specifications are necessary.
    - Master the basics of OpenAPI 3.0 (OAS).
    - Explore the Swagger ecosystem and tools like Connexion.

---

## The Role of Specifications

A REST API specification is a contract between the server and the client. Instead of relying on manually written (and often outdated) documentation, specifications provide a machine-readable definition of the API.

### Benefits of Specifications:
- **Consistency**: Ensures the implementation matches the design.
- **Automation**: Allows for the automatic generation of documentation and client SDKs.
- **Testing**: Enables tools to validate requests and responses against the spec.
- **Parallel Development**: Clients can build mocks based on the spec before the server is even implemented.

---

## OpenAPI 3.0 (OAS)

The **OpenAPI Specification** (formerly known as Swagger) is the industry standard for defining REST APIs.

### Key Components of an OAS 3.0 Document
An OpenAPI spec is typically written in **YAML** or **JSON**. Its main sections include:

1.  **`openapi`**: The version of the specification (e.g., `3.0.2`).
2.  **`info`**: Metadata about the API (title, version, description, license).
3.  **`servers`**: The base URLs for the API (production, staging, local).
4.  **`paths`**: The core of the API. Defines endpoints, methods, parameters, and responses.
5.  **`components`**: Reusable objects, such as schemas (data models), security schemes, and parameters.

### Example OAS 3.0 Snippet
```yaml
openapi: 3.0.2
info:
  title: CPU Info Service
  version: 1.0.0
servers:
  - url: http://localhost:8080/cloudmesh
paths:
  /cpu:
    get:
      summary: Returns CPU information
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/cpu'
components:
  schemas:
    cpu:
      type: object
      required: [model]
      properties:
        model:
          type: string
```

---

## The Swagger Ecosystem

"Swagger" refers to the set of tools built around the OpenAPI specification:

- **Swagger Editor**: A browser-based editor for writing and validating OAS specs.
- **Swagger UI**: Turns an OAS spec into an interactive web page where developers can test endpoints directly in the browser.
- **Swagger Codegen**: Generates server stubs and client libraries in multiple languages (Java, Python, Go, etc.) from a spec.

---

## From Spec to Code: Connexion

In the Python ecosystem, **Connexion** is a powerful framework that bridges the gap between OpenAPI and implementation.

Instead of defining routes in code, you define them in an OpenAPI YAML file. Connexion then automatically:
1.  Handles the routing based on the spec.
2.  Validates incoming request parameters and bodies against the spec.
3.  Maps the operation to a specific Python function via the `operationId`.

**Example Mapping:**
Spec: `operationId: cpu.get_processor_name` $\rightarrow$ Python: `def get_processor_name(): ...`
