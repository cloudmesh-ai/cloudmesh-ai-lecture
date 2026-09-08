# 2. Core Building Blocks

!!! info "Learning Objectives"
    - Identify and define REST Resources.
    - Understand the role of URIs in resource identification.
    - Master the use of HTTP methods for CRUD operations.
    - Understand Media Types and Status Codes.

---

## Resources and URIs

At the heart of REST is the concept of a **Resource**. A resource is any entity that can be named and manipulated. Examples include a user, an order, a photo, or a piece of hardware information.

### The URI (Uniform Resource Identifier)
A resource is identified by a **URI**. A well-designed URI should be intuitive and represent the resource, not the action.

- **Bad**: `http://api.example.com/getUser?id=42` (Uses a verb)
- **Good**: `http://api.example.com/users/42` (Identifies the resource)

### Collections vs. Single Resources
REST distinguishes between a collection of resources and a specific item within that collection.

- **Collection URI**: `http://.../resources/`
- **Single Resource URI**: `http://.../resources/item42`

---

## HTTP Methods (The Verbs)

REST leverages the existing HTTP methods to perform **CRUD** (Create, Read, Update, Delete) operations.

| CRUD Operation | HTTP Method | Collection URI (`/users`) | Single Resource URI (`/users/42`) |
|----------------|-------------|---------------------------|----------------------------------|
| **Create**      | `POST`      | Create a new user          | Not typically used                |
| **Read**        | `GET`       | List all users             | Retrieve user 42                  |
| **Update**      | `PUT`       | Replace entire collection  | Replace user 42                   |
| **Update**      | `PATCH`     | Not typically used         | Partially update user 42          |
| **Delete**      | `DELETE`    | Delete entire collection   | Delete user 42                    |

### Key Method Properties
- **Safe Methods**: Methods that do not modify the state of the server (e.g., `GET`).
- **Idempotent Methods**: Methods that can be called multiple times with the same result as a single call (e.g., `GET`, `PUT`, `DELETE`). `POST` is **not** idempotent because calling it twice creates two resources.

---

## Media Types and Content Negotiation

Since REST is about "Representational State Transfer", a resource can have multiple **representations**.

- **JSON** (`application/json`): The industry standard for most APIs.
- **XML** (`application/xml`): Common in legacy or enterprise systems.
- **Plain Text** (`text/plain`): Used for simple messages.

The client and server use the `Accept` and `Content-Type` HTTP headers to negotiate which media type to use.

---

## Status Codes

HTTP status codes tell the client the outcome of their request.

| Range | Category | Example | Meaning |
|-------|----------|---------|---------|
| **2xx** | Success | `200 OK`, `201 Created` | The request was successful. |
| **3xx** | Redirection | `304 Not Modified` | Resource has moved or is cached. |
| **4xx** | Client Error | `400 Bad Request`, `404 Not Found` | The client sent something wrong. |
| **5xx** | Server Error | `500 Internal Server Error` | The server failed to process the request. |
