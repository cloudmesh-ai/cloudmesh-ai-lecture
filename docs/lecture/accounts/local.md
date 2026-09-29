# Local VM and Container Setup

This section focuses on establishing a local development environment using virtualization and containerization tools to test code safely and avoid cloud costs. It provides an overview of frameworks like Multipass and VirtualBox, along with instructions for setting up Docker.

!!! info "Learning Objectives"
    By the end of this section, you will be able to:
    - Implement local-first development practices to test code safely and avoid unexpected cloud costs.
    - Install and configure a local virtualization framework.
    - Deploy and verify local containers using Docker.

## Overview

Before deploying any resources to a public cloud, it is critical to develop and test scripts, containers, and configurations on a local machine. Cloud resources, even within free tiers, can incur costs if misconfigured or if limits are exceeded. Local development ensures functional correctness and stability before transitioning to a production or cloud environment.

## Local Virtualization

Virtual machines (VMs) provide a full operating system environment, allowing for the testing of kernel-level configurations and OS-specific behavior.

### Choosing a Framework

Selecting a virtualization tool depends on the host operating system and the required level of isolation:

- **Multipass**: A lightweight tool for deploying Ubuntu VMs quickly. It is supported on Linux, macOS, and Windows.
- **VirtualBox**: A robust, open-source hypervisor suitable for various operating systems and image types.
- **VMware**: An enterprise-grade virtualization platform often used in corporate environments.

## Local Containerization

Containers offer a more lightweight alternative to VMs by sharing the host system's kernel, which results in faster startup times and lower resource overhead.

### Docker

Docker is the industry standard for containerization. It allows developers to package an application and its dependencies into a single image, ensuring consistency across different environments.

## Summary Checklist

- [ ] Virtualization framework (e.g., Multipass, VirtualBox) installed and verified.
- [ ] Docker installed and daemon running.
- [ ] Local administrative rights confirmed for resource management.
- [ ] "Hello World" VM successfully deployed.
- [ ] "Hello World" container successfully deployed.

## Assignments

!!! note "Assignment.1: Local Virtual Machines"
    **Goal**: Establish a working local virtualization environment.

    **Tasks**:
    1. Install a virtualization tool (Multipass, VirtualBox, VMware, or equivalent).
    2. Deploy a simple "Hello World" VM to verify the installation.
    3. Verify that you possess the administrative rights necessary to manage VM resources.

    ??? tip "Solution: Local Virtual Machines"
        For a fast start on macOS or Windows, Multipass is recommended: `multipass launch --name test-vm`. Once launched, use `multipass shell test-vm` to verify access.

!!! note "Assignment.2: Local Containers"
    **Goal**: Establish a working local container environment.

    **Tasks**:
    1. Install Docker on the local machine.
    2. Execute a "Hello World" container to verify the installation.
    3. Verify that you possess the administrative rights necessary to manage Docker resources.

    ??? tip "Solution: Local Containers"
        Run `docker run hello-world` in the terminal. If the command returns a "Hello from Docker!" message, the installation is successful.

## References

- [Multipass Documentation](https://multipass.run/)
- [VirtualBox User Manual](https://www.virtualbox.org/manual/)
- [Docker Get Started Guide](https://docs.docker.com/get-started/)

## Self-Assessment
Test your knowledge by expanding the questions below.
??? question "Why is it recommended to test scripts and containers locally before deploying to the cloud?"
    Local testing ensures that code is functionally correct and prevents unexpected costs resulting from misconfigurations or the exhaustion of free tier limits in cloud environments.

??? question "What are the primary tools used for local virtualization and containerization?"
    Virtualization tools include Multipass, VirtualBox, and VMware. For containerization, Docker is the primary tool.

??? question "What are the general goals of local-first development practices?"
    The primary goals are to enable safe code testing, eliminate unnecessary cloud expenditure during the development phase, and ensure environment stability before production deployment.
