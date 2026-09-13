# 3. Designing a RESTful API

!!! info "Learning Objectives"
    - Apply resource modeling rules to design clean APIs.
    - Select appropriate HTTP methods for business logic.
    - Design meaningful error payloads and status codes.

---

## Resource Modeling

Designing a RESTful API begins with identifying your resources. The goal is to create a predictable and intuitive interface.

### Golden Rules for URIs
1.  **Nouns, not verbs**: Endpoints represent resources, not actions.
    - ❌ `/api/getAllUsers` $\rightarrow$ ✅ `/api/users`
    - ❌ `/api/updateOrder` $\rightarrow$ ✅ `/api/orders/{id}`
2.  **Use Plurals**: Keep collections plural for consistency.
    - ❌ `/api/user` $\rightarrow$ ✅ `/api/users`
3.  **Hierarchy via Nesting**: Use nesting to show containment.
    - Example: `/users/42/orders` (Orders belonging to user 42).
4.  **Avoid Deep Nesting**: Limit nesting to 2-3 levels. If it gets deeper, consider making the nested resource a top-level resource with a filter.
    - ❌ `/users/42/orders/10/items/5/details` $\rightarrow$ ✅ `/order-items/5/details`

---

## Choosing HTTP Methods

Selecting the correct method ensures your API behaves according to the expectations of the HTTP protocol.

| Business Action | Method | Logic |
|-----------------|--------|-------|
| **Fetch a list or item** | `GET` | Read-only; must be safe and idempotent. |
| **Create a new record** | `POST` | Create a subordinate resource; non-idempotent. |
| **Overwrite a record** | `PUT` | Full replacement; idempotent. |
| **Update specific fields**| `PATCH` | Partial update; non-idempotent. |
| **Remove a record** | `DELETE` | Removal; idempotent. |

---

## Status Codes & Error Payloads

A professional API doesn't just return `200 OK` or `500 Error`. It uses the full range of HTTP status codes to communicate precisely what happened.

### Common Status Codes for REST APIs

| Code | Meaning | Use Case |
|------|---------|----------|
| **200** | OK | Successful `GET`, `PUT`, or `PATCH`. |
| **201** | Created | Successful `POST` that created a new resource. |
| **204** | No Content | Successful `DELETE` or an update with no return body. |
| **400** | Bad Request | Validation errors, malformed JSON. |
| **401** | Unauthorized | Missing or invalid authentication token. |
| **403** | Forbidden | Authenticated, but does not have permission for the resource. |
| **404** | Not Found | The requested URI does not exist. |
| **409** | Conflict | Duplicate resource or version conflict. |
| **429** | Too Many Requests | Rate-limit exceeded. |

### Designing Error Payloads
When returning a `4xx` or `5xx` error, always provide a JSON body that helps the developer debug the issue.

**Example Error Response:**
```json
{
  "error": "Invalid Request",
  "message": "The 'email' field is required.",
  "code": 400,
  "details": {
    "email": "Field cannot be null"
  }
}
```


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "What are the 'Golden Rules' for designing URIs in a RESTful API?"
    1. **Nouns, not verbs**: Endpoints represent resources (e.g., `/users`), not actions (e.g., `/getAllUsers`).
    2. **Use Plurals**: Maintain consistency by using plural nouns for collections (e.g., `/users` instead of `/user`).
    3. **Hierarchy via Nesting**: Use nesting to show containment (e.g., `/users/42/orders`).
    4. **Avoid Deep Nesting**: Keep nesting to 2-3 levels; otherwise, flatten the resource.

??? question "Why should you avoid deep nesting in your URI hierarchy?"
    Deep nesting (e.g., `/users/42/orders/10/items/5/details`) makes URIs overly complex, hard to read, and fragile. It is better to promote deeply nested resources to top-level resources and use filters.

??? question "Which HTTP status code is most appropriate for a successful `POST` request that creates a new resource?"
    The `201 Created` status code is most appropriate, as it explicitly indicates that the request was successful and a new resource was created.

??? question "Contrast the use of `401 Unauthorized` vs. `403 Forbidden`."
    `401 Unauthorized` means the user is not authenticated (they need to log in). `403 Forbidden` means the user is authenticated but does not have the necessary permissions to access that specific resource.

??? question "What elements should be included in a professional JSON error payload to help developers debug?"
    A professional payload should include a human-readable `error` title, a descriptive `message`, the numeric HTTP `code`, and a `details` object specifying which fields failed validation and why.

