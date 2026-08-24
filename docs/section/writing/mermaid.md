# Mermaid.js

Mermaid is a JavaScript-based charting and diagramming tool that renders Markdown-inspired text definitions to create and modify diagrams dynamically.

## Why use Mermaid?

- **Version Control**: Diagrams are stored as text, making them easy to track in Git.
- **Consistency**: Standardized styles across all diagrams.
- **Efficiency**: No need to use external drawing tools and export images.

## Common Diagram Types

### Flowcharts
Flowcharts are useful for representing infrastructure workflows and request routing, as shown in Figure 1.

```mermaid
graph TD
    User((User)) --> LB[Load Balancer]
    LB --> Web1[Web Server 1]
    LB --> Web2[Web Server 2]
    Web1 --> DB[(Database)]
    Web2 --> DB
    DB --> Cache[Redis Cache]
```
Figure 1: Infrastructure request routing flow

### Sequence Diagrams
Sequence diagrams show how microservices interact in a cloud environment (see Figure 2).

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
Figure 2: Microservices interaction for resource request

### Gantt Charts
Gantt charts are ideal for tracking cloud migration or deployment phases, as illustrated in Figure 3.

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
Figure 3: Cloud migration project timeline

## Integration

Mermaid is natively supported by GitHub, GitLab, and many Markdown editors (like Obsidian or VS Code with extensions).

## Using Mermaid in MkDocs

To use Mermaid diagrams in an MkDocs site, follow these steps:

1. **Install `pymdown-extensions`**:
   Ensure you have `pymdown-extensions` installed in your environment:
   ```bash
   pip install pymdown-extensions
   ```

2. **Update `mkdocs.yml`**:
   Enable the `superfences` extension in your configuration:
   ```yaml
   markdown_extensions:
     - pymdownx.superfences:
         custom_fences:
           - name: mermaid
             class: mermaid
             format: !!python/name:pymdownx.superfences.fence_code_format
   ```

3. **Add the Mermaid JS Library**:
   Include the Mermaid JS script in your `mkdocs.yml` under `extra_javascript`:
   ```yaml
   extra_javascript:
     - https://unpkg.com/mermaid/dist/mermaid.min.js
   ```

4. **Initialize Mermaid**:
   You may need a small snippet of JavaScript to initialize the diagrams on the page. This can be added to a custom JS file:
   ```javascript
   mermaid.initialize({ startOnLoad: true });
   ```
