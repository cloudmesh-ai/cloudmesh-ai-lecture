# 7. Security & Best Practices

!!! info "Learning Objectives"
    - Implement secure authentication and authorization.
    - Protect your API from abuse using Rate Limiting and CORS.
    - Manage API evolution through Versioning.

---

## Authentication & Authorization

Since REST is stateless, the server does not "remember" who the client is. Every request must prove the client's identity.

### Common Methods
- **API Keys**: A simple unique string passed in the header. Easy to use but less secure.
- **JWT (JSON Web Tokens)**: A signed token containing user claims. The server verifies the signature without needing to query a database.
- **OAuth 2.0**: The industry standard for delegated authorization (e.g., "Login with Google").

**Security Tip**: Always use **HTTPS** (TLS). Without encryption, tokens and keys are sent in plain text and can be stolen via "man-in-the-middle" attacks.

---

## Protecting Your API

### 1. Rate Limiting
To prevent Denial of Service (DoS) attacks or abuse, implement rate limits. This restricts the number of requests a client can make in a given timeframe (e.g., 100 requests per minute).
- **Tool**: `Flask-Limiter` for Python apps.

### 2. CORS (Cross-Origin Resource Sharing)
By default, browsers block scripts from one domain from calling an API on another domain for security reasons.
- Use **CORS headers** to explicitly whitelist the origins (domains) that are allowed to access your API.
- Avoid using `*` (allow all) in production environments.

---

## API Evolution & Maintenance

### Versioning
APIs change over time. To avoid breaking existing clients, you must version your API.

- **URL Versioning**: `/v1/users`, `/v2/users` (Most common, easiest to cache).
- **Header Versioning**: `Accept: application/vnd.myapi.v1+json`.

### Documentation
A REST API is only as good as its documentation.
- **Keep it Automated**: Use OpenAPI specs to keep documentation in sync with the code.
- **Provide Examples**: Always include request and response examples for every endpoint.

### Logging & Monitoring
Implement centralized logging (e.g., ELK stack) to track:
- **Request IDs**: To trace a single request across multiple microservices.
- **Response Times**: To identify bottlenecks.
- **Error Rates**: To catch bugs before users report them.


## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "Why is HTTPS mandatory for APIs using JWT or API Keys?"
    Without HTTPS (TLS encryption), tokens and keys are sent in plain text. This makes them vulnerable to "man-in-the-middle" attacks, where an attacker can intercept the network traffic and steal the credentials to impersonate the user.

??? question "Contrast API Keys with JWTs in terms of how the server verifies the client's identity."
    **API Keys** are typically stored in a database, and the server must query the database for every request to verify the key. **JWTs (JSON Web Tokens)** are digitally signed; the server only needs the secret key to verify the signature, eliminating the need for a database lookup for every request.

??? question "What is the purpose of CORS, and why should you avoid using `*` in production?"
    CORS (Cross-Origin Resource Sharing) is a security mechanism that prevents a website on one domain from making requests to an API on another domain. Using `*` allows any domain to access the API, which increases the risk of Cross-Site Request Forgery (CSRF) and other security vulnerabilities.

??? question "Explain the difference between URL versioning and Header versioning."
    **URL Versioning** includes the version in the path (e.g., `/v1/users`), which is easy to implement and cache. **Header Versioning** uses a custom HTTP header (e.g., `Accept: application/vnd.myapi.v1+json`), which keeps URIs clean but is harder to test in a browser and more complex to cache.

??? question "Why is rate limiting important for protecting a public REST API?"
    Rate limiting prevents a single client from overwhelming the server with too many requests, which protects the API from Denial of Service (DoS) attacks, prevents resource exhaustion, and ensures fair usage across all users.

