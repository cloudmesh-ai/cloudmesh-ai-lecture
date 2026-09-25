# Mermaid.js

!!! info "Learning Objectives"
    After completing this chapter, you will be able to:
    - Define Mermaid.js and its utility in technical documentation.
    - Create flowcharts, sequence diagrams, and Gantt charts using Mermaid syntax.
    - Integrate Mermaid.js into an MkDocs environment.

## Overview

Mermaid is a JavaScript-based charting and diagramming tool that renders Markdown-inspired text definitions to create and modify diagrams dynamically.

## Core Diagram Types

### Flowcharts

Flowcharts represent infrastructure workflows and request routing.

~~~
```mermaid
graph TD
    User((User)) --> LB[Load Balancer]
    LB --> Web1[Web Server 1]
    LB --> Web2[Web Server 2]
    Web1 --> DB[(Database)]
    Web2 --> DB
    DB --> Cache[Redis Cache]
```
~~~

```mermaid
graph TD
    User((User)) --> LB[Load Balancer]
    LB --> Web1[Web Server 1]
    LB --> Web2[Web Server 2]
    Web1 --> DB[(Database)]
    Web2 --> DB
    DB --> Cache[Redis Cache]
```

### Sequence Diagrams

Sequence diagrams illustrate how microservices interact within a cloud environment.

~~~
```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Gateway as API Gateway
    participant Auth as Auth Service
    participant Backend as Backend Service

    Client->>Gateway: Request Resource
    Gateway->>Auth: Validate Token
    Auth-->>Gateway: Token Valid
    Gateway->>Backend: Fetch Data
    Backend-->>Gateway: Resource Data
    Gateway-->>Client: HTTP 200 OK (Data)
```
~~~

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Gateway as API Gateway
    participant Auth as Auth Service
    participant Backend as Backend Service

    Client->>Gateway: Request Resource
    Gateway->>Auth: Validate Token
    Auth-->>Gateway: Token Valid
    Gateway->>Backend: Fetch Data
    Backend-->>Gateway: Resource Data
    Gateway-->>Client: HTTP 200 OK (Data)
```

### Gantt Charts

Gantt charts track project timelines, such as cloud migration or deployment phases.

~~~
```mermaid
gantt
    title Cloud Migration Project
    dateFormat  YYYY-MM-DD
    section Planning
    Infrastructure Audit    :a1, 2026-10-01, 3d
    Architecture Design     :a2, after a1, 5d
    section Execution
    Data Migration          :a3, after a2, 7d
    App Deployment          :a4, after a3, 3d
    section Validation
    UAT Testing             :a5, after a4, 3d
    Go-Live                 :a6, after a5, 1d
```
~~~

```mermaid
gantt
    title Cloud Migration Project
    dateFormat  YYYY-MM-DD
    section Planning
    Infrastructure Audit    :a1, 2026-10-01, 3d
    Architecture Design     :a2, after a1, 5d
    section Execution
    Data Migration          :a3, after a2, 7d
    App Deployment          :a4, after a3, 3d
    section Validation
    UAT Testing             :a5, after a4, 3d
    Go-Live                 :a6, after a5, 1d
```

## Integration and Configuration

Mermaid is supported by GitHub, GitLab, and various Markdown editors.

### MkDocs Configuration

To implement Mermaid diagrams in an MkDocs site, perform the following steps:

1. Install `pymdown-extensions`:

```bash
pip install pymdown-extensions
```

2. Update `mkdocs.yml` to enable the `superfences` extension:

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

3. Add the Mermaid JS library to `mkdocs.yml`:

```yaml
extra_javascript:
  - https://unpkg.com/mermaid/dist/mermaid.min.js
```

4. Initialize Mermaid via a custom JavaScript file:

```javascript
mermaid.initialize({ startOnLoad: true });
```

## Summary Checklist

- [ ] Define the purpose of Mermaid.js.
- [ ] Create a flowchart using `graph TD`.
- [ ] Create a sequence diagram using `sequenceDiagram`.
- [ ] Create a Gantt chart using `gantt`.
- [ ] Configure `mkdocs.yml` for Mermaid support.

## Assignments

!!! note "Assignment 1: Architecture Mapping"
    Create a Mermaid flowchart that represents a three-tier architecture: a Client, an Application Load Balancer, an Auto Scaling Group of EC2 instances, and an RDS Database.

!!! note "Assignment 2: Authentication Flow"
    Create a sequence diagram showing the OAuth2 Authorization Code flow between a User, a Client Application, an Authorization Server, and a Resource Server.

## Self-Evaluation

??? note "What is the primary advantage of using Mermaid over static image files for diagrams?"
    Diagrams are stored as text, allowing them to be managed via version control systems like Git, facilitating easier updates and tracking.

??? note "Which MkDocs extension is required to render custom Mermaid fences?"
    The `pymdownx.superfences` extension is required.

??? note "How is a database represented in a Mermaid flowchart?"
    Databases are typically represented using the `[(Database)]` cylinder shape syntax.
