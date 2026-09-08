# 1. Introduction to REST

!!! info "Learning Objectives"
    - Understand the core definition of REST.
    - Differentiate between REST and traditional SOAP-based web services.
    - Understand why REST has become the de-facto standard for modern APIs.

---

![FatAPI Landscape](images/fastapi-chatgpt.png)

## What is REST?

**REST** stands for **RE**presentational **S**tate **T**ransfer. It is not a protocol or a standard, but an **architectural style** for designing networked applications. 

Introduced by Roy Fielding in his 2000 doctoral dissertation, REST is based on a stateless, client-server, cacheable communications protocol. While it is not strictly bound to HTTP, in almost all practical implementations, the HTTP protocol is used.

### Key Characteristics of REST

- **Statelessness**: Each request from a client to a server must contain all the information necessary to understand and complete the request. The server does not store any session context between calls.
- **Client-Server Architecture**: The client (user interface) and the server (data storage/business logic) are separate, allowing them to evolve independently.
- **Cacheability**: Responses must define themselves as cacheable or not to improve network efficiency.
- **Uniform Interface**: A consistent way of interacting with the server, regardless of the resource being accessed.

---

## REST vs. Traditional Web Services (SOAP)

Historically, "Web Services" often referred to **SOAP** (Simple Object Access Protocol). While both allow systems to communicate over a network, they differ fundamentally in philosophy and implementation.

### Comparison Table

| Aspect | REST | SOAP / Traditional Web Services |
|---------|------|-----------------------------------|
| **Protocol** | Purely HTTP (or HTTPS) | Can use HTTP, SMTP, TCP, JMS, etc. |
| **Message Format** | Lightweight (JSON, XML, Text) | Rigid XML envelope (SOAP spec) |
| **Coupling** | Loosely‑coupled | Tightly‑coupled (WSDL contracts) |
| **Ease of Use** | Simple CRUD mapping; browser-friendly | Requires SOAP libraries and client stubs |
| **Performance** | High performance, low latency | Heavier payloads, higher latency |
| **Caching** | Native HTTP caching | Generally non‑cacheable |
| **Security** | HTTPS, OAuth 2.0, JWT | WS‑Security (Complex XML encryption) |

### Why REST Dominates the Landscape

REST has largely replaced SOAP for public APIs and microservices for several key reasons:

1.  **Simplicity**: A single HTTP request with a clean URI is all that's needed. There's no need for complex SOAP envelopes or WSDL files.
2.  **Lightweight Payloads**: JSON is significantly smaller than SOAP XML, which is critical for mobile apps and high-traffic services.
3.  **Native Web Compatibility**: Browsers speak HTTP and JSON natively. You can call a REST API directly from JavaScript using `fetch()` without any plugins.
4.  **Scalability**: The stateless nature of REST makes horizontal scaling (using load balancers and containers) straightforward.
5.  **Rich Ecosystem**: Every modern framework (Flask, Express, Spring Boot, ASP.NET Core) provides first-class support for REST.

---

## Bottom Line

- **REST** = The modern, web-native way to expose services. It is the standard for public APIs, cloud-native microservices, and mobile back-ends.
- **SOAP** = A powerful but heavyweight tool still used in legacy enterprise environments, highly regulated industries (finance), or where complex transactional guarantees (WS-*) are required.
