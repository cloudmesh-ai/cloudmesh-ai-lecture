# Getting Started with CloudMesh AI LLM Mock

!!! info "Learning Objectives"
    - Clone the `cloudmesh-ai-llm-mock` repository using SSH or HTTPS.
    - Set up the project in the recommended working directory.
    - Launch the mock LLM server using the provided automation tools.
    - Navigate and utilize the documentation, admin, and chat interfaces.

## Overview

When developing applications that integrate with Large Language Models (LLMs), relying solely on live APIs can be expensive, slow, and non-deterministic. The `cloudmesh-ai-llm-mock` project provides a local, controllable environment that simulates LLM behavior.

This tool is critical for architectural testing because it allows developers to simulate various edge cases, such as API timeouts or specific error responses, without needing to manipulate a live production environment. By using a mock server, you can ensure your application's error handling and orchestration logic are robust before deploying to a cloud provider.

## Installation

To begin using the mock server, you must first clone the repository to your local machine.

### Cloning the Repository

Depending on your authentication setup, use one of the following methods:

**Using SSH**

```bash
git clone git@github.com:cloudmesh-ai/cloudmesh-ai-llm-mock.git
```

**Using HTTPS**

```bash
git clone https://github.com/cloudmesh-ai/cloudmesh-ai-llm-mock.git
```

### Environment Setup

For the scripts and makefiles to function correctly, ensure the project is located in the expected directory.

```bash
# Create the work directory if it does not exist
mkdir -p ~/work

# Move the cloned repository to the required path
mv cloudmesh-ai-llm-mock ~/work/cloudmesh-ai-llm-mock

# Navigate to the project root
cd ~/work/cloudmesh-ai-llm-mock
```

!!! warning "Directory Requirement"
    The `cmm` tool and associated makefiles expect the source to be at `~/work/cloudmesh-ai-llm-mock`. Placing the project elsewhere may result in path errors during execution.

## Running the Mock Server

The project includes a `Makefile` that simplifies the process of starting the server and opening the required browser tabs.

### Using the Automated Launcher

The simplest way to start the environment is by running the `view` target:

```bash
make view
```

This command executes a sequence that starts the server in the background and opens the user interfaces.

### Understanding the Execution Chain

If you need to start the server manually or debug the launch process, the underlying command is:

```bash
nohup cmm serve > /dev/null 2>&1 & \
    until curl -s http://localhost:8888/docs > /dev/null; do sleep 0.5; done && \
    open http://localhost:8888/docs && \
    open http://localhost:8888/admin && \
    open http://localhost:8888/chat
```

**Breakdown of the command:**

1. `nohup cmm serve > /dev/null 2>&1 &`: Starts the CloudMesh Mock (cmm) server in the background and suppresses output.
2. `until curl...`: A polling loop that waits for the server to become responsive on port 8888.
3. `open ...`: Launches the three primary web interfaces in the default browser.

!!! tip "Process Management"
    To stop the mock server, find the process ID using `pgrep cmm` and terminate it with `kill`.

## Exploring the Interfaces

Once the server is running, you have access to three distinct portals:

1. **Documentation** (`http://localhost:8888/docs`): Provides the API reference and configuration guides for the mock server.
2. **Admin Console** (`http://localhost:8888/admin`): Allows you to configure mock responses, manage state, and simulate different model behaviors.
3. **Chat Interface** (`http://localhost:8888/chat`): A frontend for interacting with the mock LLM to verify that responses are being returned as expected.

## Summary Checklist

!!! tip "Summary Checklist"
    - [ ] Repository cloned to `~/work/cloudmesh-ai-llm-mock`.
    - [ ] Mock server started via `make view` or `cmm serve`.
    - [ ] Verified connectivity via `curl` or browser.
    - [ ] Accessed `/docs`, `/admin`, and `/chat` endpoints.

## Assignments

!!! note "Clone and Launch"
    Clone the `cloudmesh-ai-llm-mock` repository and successfully launch the server using `make view`. Verify that the chat interface opens in your browser.

    ??? question "Solution"
        1. Run `git clone https://github.com/cloudmesh-ai/cloudmesh-ai-llm-mock.git`.
        2. Move the folder to `~/work/cloudmesh-ai-llm-mock`.
        3. Run `make view`.

!!! note "Admin Configuration"
    Access the Admin Console and identify the section used to modify the default mock response.

    ??? question "Solution"
        Navigate to `http://localhost:8888/admin` and locate the response templates or configuration settings.

!!! note "Customizing Responses"
    Configure the mock server to return a specific string (e.g., "Hello from the Mock!") when a request is sent to the chat interface.

    ??? question "Solution"
        Use the Admin Console to edit the mock response template, save the changes, and verify the output in the Chat interface.

## References

- Documentation: [https://cloudmesh-ai.github.io/cloudmesh-ai-llm-mock/](https://cloudmesh-ai.github.io/cloudmesh-ai-llm-mock/)
- Source Code: [https://github.com/cloudmesh-ai/cloudmesh-ai-llm-mock](https://github.com/cloudmesh-ai/cloudmesh-ai-llm-mock)

## Self-Evaluation

??? note "What is the primary purpose of the `cloudmesh-ai-llm-mock` project?"
    It provides a local simulation of LLM APIs to allow for cost-effective, deterministic, and offline development and testing.

??? note "Why is it recommended to place the project in `~/work/cloudmesh-ai-llm-mock`?"
    The project's internal scripts and makefiles use hardcoded or relative paths that assume this specific directory structure.

??? note "What does the `until curl...` part of the launch command achieve?"
    It prevents the browser tabs from opening before the server is fully initialized and ready to handle requests.

??? note "Which interface should you use to change how the mock LLM responds?"
    The Admin Console (`/admin`).

??? note "How can you stop the mock server if it was started with `nohup`?"
    By finding the process ID using `pgrep cmm` and executing `kill <PID>`.
