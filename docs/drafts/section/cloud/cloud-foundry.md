# Cloud Foundry: Open Source PaaS {#sec:cloud-foundry}

Cloud Foundry (CF) is an open-source Platform as a Service (PaaS) available through various private and public cloud distributions. Originally developed by VMware and later managed by Pivotal Software (a joint venture between EMC, VMware, and General Electric), it provides a robust framework for deploying and scaling applications.

Unlike many proprietary PaaS offerings, Cloud Foundry is open-source and highly flexible, allowing deep integration with external systems. It provides a full suite of PaaS capabilities—including scalable infrastructure, middleware, and development tools—while promoting the **12-Factor App** methodology. This methodology encourages a clear separation of concerns between front-end and back-end services and provides guidelines for source control, dependency management, and loosely coupled services [@twelve-factor-app].

To ensure an infrastructure-agnostic architecture, Cloud Foundry focuses on three main categories: **Clouds, Frameworks, and Services**.

## Core Categories

### 1. Clouds
Cloud Foundry can be deployed across public, private, or hybrid cloud environments. While public clouds offer speed and flexibility, private clouds provide total operational control. A hybrid approach allows organizations to balance scalability with data locality and regulatory requirements. Cloud Foundry can be hosted on top of major providers such as AWS, Azure, Google Cloud, and OpenStack.

### 2. Frameworks
Many cloud environments restrict the programming languages or frameworks they support. Cloud Foundry is designed to be generic and runtime-agnostic. Through the use of "Buildpacks," it supports a wide range of popular languages, including Java (Spring), Ruby, and Node.js.

### 3. Services
To avoid locking developers into specific vendor technologies, Cloud Foundry uses a decoupled service model. Out of the box, it supports various relational databases (MySQL, PostgreSQL), NoSQL stores (MongoDB), key-value stores (Redis), and messaging systems (RabbitMQ), while remaining extensible to allow third-party service integration.

## Key Components

Cloud Foundry utilizes a distributed architecture to ensure scalability and high availability.

### Router (Gorouter)
The router manages all external application-level traffic. It maintains a dynamic route table and directs incoming requests to the appropriate application instances. Implemented in Go for optimal performance, the router ensures efficient load balancing across the environment.

### UAA and Login Server
The **User Account and Authentication (UAA)** server handles identity management. It implements OAuth2 standards to provide token-based authentication and authorization, ensuring secure access to the platform.

### Cloud Controller (CC)
The Cloud Controller is the "brain" of the environment. It manages the entire application lifecycle, including:
*   **Deployment**: Handling the upload and staging of application code.
*   **Metadata**: Managing application configurations and state.
*   **Scaling**: Coordinating with the execution engine to scale instances.
CC manages user permissions through a hierarchy of Organizations, Spaces, and Roles.

### Execution and Storage (Diego/DEA)
The **Droplet Execution Agent (DEA)**, often part of the Diego cell architecture, is responsible for the runtime management of applications.
*   **Buildpacks**: Scripts that detect the application's runtime and install necessary dependencies.
*   **Droplets**: The final, executable unit containing the application and its environment.
*   **Containers**: Droplets are hosted in isolated containers (traditionally using Garden/Wardens) to ensure resource control and security.

### Service Brokers
Because application containers are ephemeral (non-persistent), they cannot host databases or message queues directly. **Service Brokers** allow applications to provision and bind to persistent services in a decoupled manner. This is often facilitated via the Open Service Broker API.

### Monitoring and Logging
To ensure operational stability, Cloud Foundry provides integrated monitoring tools:
*   **Health Manager**: Monitors the status of application instances.
*   **Metric Collector**: Gathers performance data from running instances.
*   **Log Aggregator**: Streams application logs to developers for real-time debugging and support.

## The Evolution of PaaS

While Cloud Foundry pioneered the "Buildpack" and "Push" model of deployment, the industry has shifted toward container orchestration. Modern PaaS offerings often leverage **Kubernetes** as the underlying engine to manage containers, combining the ease of use of a PaaS with the flexibility of K8s.

Developers today often choose between a traditional PaaS like Cloud Foundry for rapid deployment or a "Knative" or "Serverless" approach for finer control over scaling and resource utilization.

## Resources

*   [Official Cloud Foundry Documentation](https://docs.cloudfoundry.org/)
*   [The Twelve-Factor App](https://12factor.net/)
*   [Cloud Foundry GitHub Repository](https://github.com/cloudfoundry)