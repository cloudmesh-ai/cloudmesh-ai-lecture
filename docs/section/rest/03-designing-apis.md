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
