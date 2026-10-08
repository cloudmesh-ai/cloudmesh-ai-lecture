## Learning Objectives

!!! info "Learning Objectives"
    - Configure Docker contexts for Azure.
    - Deploy ACI containers using `docker run`.
    - Manage ACI lifecycle via Docker CLI.

## Overview

Azure Container Instances (ACI) allow for the deployment of containers without managing the underlying virtual machines. The integration with the Docker CLI enables developers to use familiar Docker commands to deploy and manage these containers directly in Azure. This removes the need to learn new Azure-specific CLI tools for basic container operations and allows a seamless transition from local development to cloud hosting.

## Core Sections

### Prerequisites

To use the Docker-ACI integration, one of the following must be installed:

- Docker Desktop for Windows or macOS.
- Docker ACI Integration CLI for Linux.

### Authentication and Context

Before deploying to ACI, the Docker CLI must be authenticated with Azure. This is achieved using the `docker login azure` command.

```bash
docker login azure
```

Upon execution, this command prompts for the Azure tenant ID and opens a browser window for OAuth2 authentication.

Once authenticated, a Docker context must be created to target ACI. A context is a set of configurations that tells the Docker CLI how to connect to a specific engine.

```bash
docker context create aci my-aci-context
```

The context creation process associates the Docker CLI with a specific Azure subscription and resource group. The user is prompted to select the target subscription and provide the name of the resource group where the ACI instances will be deployed.

### Container Deployment

By default, the Docker CLI targets the local Docker engine. To deploy to Azure, the user must switch the active context.

```bash
docker context use my-aci-context
```

With the ACI context active, `docker run` commands are translated into ACI deployment requests. For example, to deploy a simple hello-world application:

```bash
docker run -d -p 80:80 --name hello-aci mcr.microsoft.com/azuredocs/aci-helloworld
```

In this command, `-d` runs the container in detached mode, `-p 80:80` maps port 80 of the container to port 80 of the ACI instance, and `--name` assigns a name to the instance. ACI automatically assigns a public IP address to the container.

### Observability and Lifecycle

Managing ACI instances follows the same pattern as managing local containers. To retrieve the public IP address and verify the status of the running container, use `docker ps`.

```bash
docker ps
```

The output displays the container ID, image, and the assigned public IP address in the PORTS column.

To inspect the logs of a running ACI instance, use the `docker logs` command.

```bash
docker logs hello-aci
```

To stop and remove the ACI instance, use `docker rm`.

```bash
docker rm -f hello-aci
```

The `-f` flag forces the removal of a running container.

## Summary Checklist

- [ ] Docker Desktop or ACI Integration CLI installed.
- [ ] Azure authentication completed via `docker login azure`.
- [ ] ACI context created and associated with a resource group.
- [ ] Active context switched to ACI.
- [ ] Container deployed using `docker run`.
- [ ] Public IP verified via `docker ps`.
- [ ] Resources cleaned up via `docker rm`.

## Assignments

!!! note "Assignment.1: Deploy a Hello World Container"
    Deploy the `mcr.microsoft.com/azuredocs/aci-helloworld` image to ACI and verify its accessibility via the public IP.

    ??? tip "Solution: Deploy a Hello World Container"
        ```bash
        docker context use my-aci-context
        docker run -d -p 80:80 --name hello-aci mcr.microsoft.com/azuredocs/aci-helloworld
        docker ps
        ```

!!! note "Assignment.2: Custom Image Deployment"
    Push a custom image to Azure Container Registry (ACR) or Docker Hub, and deploy it to ACI using the Docker CLI.

    ??? tip "Solution: Custom Image Deployment"
        ```bash
        docker run -d -p 80:80 --name custom-aci <your-registry>/<your-image>:latest
        ```

## References

- [Azure Container Instances Docker integration](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-docker)
- [Docker Contexts Documentation](https://docs.docker.com/engine/context/cli/)

## Self-Evaluation

??? note "What is the purpose of `docker context create aci`?"
    It creates a configuration that allows the Docker CLI to communicate with Azure Container Instances, mapping the commands to a specific Azure subscription and resource group.

??? note "How do you identify the public IP of a container running in ACI using the Docker CLI?"
    Run `docker ps`, and the public IP will be listed in the PORTS column of the output.

??? note "Which command is used to authenticate the Docker CLI with an Azure account?"
    The `docker login azure` command is used to initiate the OAuth2 authentication flow.
