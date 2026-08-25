---
title: "Python SSL/TLS"
---

!!! info "Learning Outcomes"
    - Understand the basics of SSL/TLS for securing data in transit.
    - Implement secure socket connections using Python's `ssl` module.
    - Configure SSL contexts to validate certificates and prevent man-in-the-middle attacks.

In cloud computing, almost all communication between your management scripts and the cloud provider's API happens over HTTPS, which is HTTP over SSL/TLS. Understanding how to manage these secure connections is critical for protecting sensitive credentials and API keys.

Python's `ssl` module provides a wrapper around the OpenSSL library, allowing you to secure network connections.

## Creating a Secure SSL Client

When connecting to a secure cloud service, you must ensure that the server's certificate is valid and trusted. The `SSLContext` object is used to define the security settings for the connection.

``` python
import socket
import ssl

# The hostname of the secure service (e.g., a cloud API endpoint)
hostname = 'www.google.com'
port = 443

# Create a default SSL context for client use
# This automatically loads system CA certificates and enables hostname verification
context = ssl.create_default_context()

# Create a standard TCP socket
with socket.create_connection((hostname, port)) as sock:
    # Wrap the socket with SSL
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(f"Connected using {ssock.version()}")
        
        # Send a basic HTTP request
        request = f"GET / HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
        ssock.sendall(request.encode())
        
        # Read the response
        response = ssock.recv(1024)
        print(response.decode())
```

### Key Concepts
- **`ssl.create_default_context()`**: The recommended way to create a context. It enables secure defaults, such as certificate validation and hostname checking.
- **`wrap_socket()`**: Transforms a plain TCP socket into a secure SSL socket.
- **Certificate Validation**: The process of verifying that the server's certificate was signed by a trusted Certificate Authority (CA).

!!! assignment "SSL Certificate Explorer"
    Write a Python script that:
    1. Connects to three different cloud provider endpoints (e.g., `aws.amazon.com`, `azure.microsoft.com`, `cloud.google.com`) using `ssl`.
    2. Extracts and prints the SSL version and the cipher suite being used for each connection.
    3. Handles `ssl.SSLError` exceptions gracefully if a connection fails.