## Learning Objectives

!!! info "Learning Objectives"
    - Implement the sidecar pattern in Azure Container Instances (ACI).
    - Configure shared network communication via localhost.
    - Deploy multi-container groups using ARM templates.
    - Manage logs and observability for individual containers within a group.

## Overview

Azure Container Instances (ACI) allows the deployment of container groups, which are the smallest deployable units in ACI. A container group consists of one or more containers that are scheduled on the same host machine. 

Containers within a group share the same network namespace, meaning they can communicate with each other using `localhost`. They also share the same storage volumes and have a shared lifecycle; if one container in the group fails or is stopped, the entire group may be affected depending on the restart policy, and they are always started and stopped together. This model is specifically designed to support the sidecar pattern, where a primary application is augmented by helper containers.

## Core Sections

### The Container Group Model

The container group model in ACI differs from traditional orchestration like Kubernetes pods in its simplicity, but it shares the core concept of co-locating related containers. 

Because containers in a group share the same network interface, they share a single IP address assigned to the group. Communication between containers occurs over the loopback interface. For example, if a main application listens on port 8080 and a sidecar proxy listens on port 80, the proxy can forward traffic to `localhost:8080`.

Lifecycle management is atomic. When a container group is deployed, Azure starts all containers defined in the group. If the group is stopped or deleted, all containers are terminated. This ensures that the supporting sidecar is always present whenever the main application is running.

### The Sidecar Pattern

The sidecar pattern is an architectural approach where a secondary container (the sidecar) is attached to a primary application container to provide supporting features. This allows the primary application to remain focused on its core business logic while the sidecar handles cross-cutting concerns.

Common use cases for the sidecar pattern in ACI include:

- **Logging and Monitoring**: A sidecar container can tail log files produced by the main application and stream them to a centralized logging service like Azure Monitor or an external ELK stack.
- **Proxying and Networking**: A sidecar can act as a service mesh proxy or a secure tunnel (e.g., using Cloudflare Tunnel or an SSH tunnel), handling TLS termination or authentication before forwarding requests to the main app.
- **Configuration Management**: A sidecar can periodically poll a configuration provider and update shared volume files that the main application reads.
- **Health Checking**: A sidecar can perform complex health checks against the main application and signal the ACI infrastructure if the application is unresponsive.

### Implementation via ARM Templates

To deploy multi-container groups, Azure Resource Manager (ARM) templates are the most reliable method, as they provide a declarative way to define the group's configuration.

The resource type used is `Microsoft.ContainerInstance/containerGroups`. Within this resource, the `containers` array defines the individual containers to be deployed.

The following ARM template defines a group with two containers: a main web application (using `nginx`) and a sidecar container (using `alpine`) that performs a health check by curling the main application every 10 seconds.

```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "containerGroupName": {
      "type": "string",
      "defaultValue": "aci-sidecar-group"
    },
    "location": {
      "type": "string",
      "defaultValue": "[resourceGroup().location]"
    }
  },
  "resources": [
    {
      "type": "Microsoft.ContainerInstance/containerGroups",
      "apiVersion": "2021-10-01",
      "name": "[parameters('containerGroupName')]",
      "location": "[parameters('location')]",
      "properties": {
        "osType": "Linux",
        "ipAddress": {
          "type": "Public",
          "ports": [
            {
              "port": 80,
              "protocol": "TCP"
            }
          ]
        },
        "containers": [
          {
            "name": "main-app",
            "properties": {
              "image": "nginx",
              "resources": {
                "requests": {
                  "cpu": 1.0,
                  "memoryInGB": 1.5
                }
              },
              "ports": [
                {
                  "port": 80
                }
              ]
            }
          },
          {
            "name": "sidecar-monitor",
            "properties": {
              "image": "alpine",
              "command": [
                "sh",
                "-c",
                "while true; do wget -qO- localhost:80; sleep 10; done"
              ],
              "resources": {
                "requests": {
                  "cpu": 0.5,
                  "memoryInGB": 0.5
                }
              }
            }
          }
        ]
      }
    }
  ]
}
```

To deploy this template, save the JSON to a file named `azuredeploy.json` and execute the following command using the Azure CLI:

```bash
az deployment group create \
  --resource-group myResourceGroup \
  --template-file azuredeploy.json
```

### Observability in Multi-Container Groups

Monitoring multi-container groups requires specifying which container's logs are being requested, as the group shares a single resource name but contains multiple distinct stdout/stderr streams.

To retrieve logs for a specific container, use the `--container-name` flag:

```bash
az container logs \
  --resource-group myResourceGroup \
  --name aci-sidecar-group \
  --container-name sidecar-monitor
```

If the `--container-name` flag is omitted, the CLI typically returns logs from the first container defined in the group.

Port management is handled at the group level. The `ipAddress.ports` section of the ARM template defines which ports are open to the external network. However, internally, each container can listen on any port. To expose multiple services to the outside world, add multiple port entries to the `ipAddress.ports` array and ensure the corresponding container in the `containers` list is configured to use that port.

## Summary Checklist

- [ ] Define the primary application container and its resource requirements.
- [ ] Identify the supporting sidecar functionality (logging, proxying, etc.).
- [ ] Configure internal communication using `localhost` and non-conflicting ports.
- [ ] Define the `Microsoft.ContainerInstance/containerGroups` resource in an ARM template.
- [ ] Specify external ports in the `ipAddress.ports` section of the template.
- [ ] Deploy the group using `az deployment group create`.
- [ ] Verify individual container logs using `az container logs --container-name`.

## Assignments

!!! note "Assignment.1: Deploy a Multi-Container Health Monitor"
    Deploy an ACI container group containing a main web server (nginx) and a sidecar container (alpine). The sidecar must be configured to send an HTTP request to the main server every 30 seconds and log the response status to stdout.

    ??? tip "Solution: Deploy a Multi-Container Health Monitor"
        Create an ARM template with a `Microsoft.ContainerInstance/containerGroups` resource.
        
        Define the `main-app` container with the `nginx` image and port 80.
        
        Define the `monitor-sidecar` container with the `alpine` image and a command like:
        `["sh", "-c", "while true; do wget -qO- localhost:80; sleep 30; done"]`.
        
        Deploy using `az deployment group create` and verify logs for the `monitor-sidecar` container.

## References

- [Azure Container Instances documentation](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-overview)
- [Deploy multi-container groups in ACI](https://learn.microsoft.com/en-us/azure/container-instances/container-instances-deploy-multi-container)

## Self-Evaluation

??? note "How do containers in an ACI container group communicate with each other?"
    Containers in an ACI container group share the same network namespace and can communicate via `localhost` using the specific ports the services are listening on.

??? note "What happens to the sidecar container if the main application container crashes?"
    Because all containers in a group share the same lifecycle, they are started and stopped together. While the sidecar remains running as long as the group is active, the restart policy of the group determines if the entire group (including the sidecar) is restarted when a container fails.

??? note "How can you distinguish logs from different containers in a multi-container group?"
    By using the `--container-name` parameter with the `az container logs` command, you can isolate the stdout and stderr streams of a specific container within the group.
