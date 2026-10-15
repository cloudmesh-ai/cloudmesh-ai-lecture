# CloudMesh AI CMM: The Mock LLM Provider

!!! info "Learning Objectives"
    * Install and run the `cloudmesh-ai-cmm` (CMM) mock server.
    * Configure LLM-integrated applications to use CMM via OpenAI-compatible API endpoints.
    * Use the `cmm` CLI to manage providers and test prompts.
    * Simulate different LLM provider behaviors to test application robustness.
    * Integrate CMM into CI/CD pipelines to eliminate GPU dependencies and API costs.

## Overview

Integrating Large Language Models (LLMs) into a software development lifecycle often introduces significant friction. Real LLMs require expensive GPU infrastructure, incur per-token API costs, and introduce non-determinism that makes automated testing unreliable.

`cloudmesh-ai-cmm` (CMM) is a lightweight, OpenAI-compatible mock LLM service. Instead of performing actual inference, it simulates the interface and behavior of popular LLM providers. This allows developers to build, test, and deploy AI-integrated applications in an environment that is fast, free, and entirely deterministic.

![alt text](images/chat-ui.png)

## OpenAI API Compatibility

The primary strength of CMM is its strict adherence to the OpenAI REST API specification. This allows it to act as a drop-in replacement for any service that uses the OpenAI SDK or compatible libraries.

### Supported Endpoints

CMM implements the most critical endpoints required for modern AI applications:

* `/v1/chat/completions`: The standard endpoint for chat-based interactions.
* `/v1/completions`: Used for legacy text completion tasks.
* `/v1/embeddings`: Used for simulating the conversion of text into vector embeddings.

### The api_base Swap

Because CMM is OpenAI-compatible, you do not need to rewrite your application logic to use it. Most LLM clients allow you to specify an `api_base` or `base_url`.

!!! tip "Professional Shortcut"
    When switching from a production LLM to CMM, only change the environment variable for your API base. This ensures that your code remains identical between development and production environments.

Example configuration change in Python:

```python
import openai

# Production configuration:
# client = openai.OpenAI(api_key="sk-...", base_url="https://api.openai.com/v1")

# Development configuration using CMM:
client = openai.OpenAI(
    api_key="mock-key", # CMM does not validate keys
    base_url="http://localhost:8888/v1"
)

# The code remains identical regardless of the backend
response = client.chat.completions.create(
    model="ollama-llama3",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## Multi-Provider Simulation

Different LLM providers have different operational characteristics. CMM simulates these differences to help developers test how their applications handle various provider personalities.

### Simulated Behaviors

CMM allows you to switch between different mock provider behaviors:

1. Ollama Simulation: Mimics a local-first LLM experience, focusing on models like `llama3` and `mistral`.
2. vLLM Simulation: Mimics a high-throughput, production-grade inference server.

### Why this matters

Testing against a single mock response is often insufficient. By simulating different providers, you can verify that your application handles different model naming conventions and simulates different latency patterns.

## Tooling and Interface

CMM provides multiple ways to interact with the mock service, catering to different developer needs.

### The Mock Server and GUI

The server is powered by FastAPI, providing high performance and automatic documentation.

* Swagger UI: Available at `http://localhost:8888/docs`, allowing you to test API endpoints directly from the browser.
* User GUI: A polished chat interface featuring real-time markdown rendering and a live latency monitor to visualize simulated server delays.

### The cmm CLI

The `cmm` command-line tool is the primary way to manage the mock environment.

```bash
# Start the mock server on port 8888
cmm serve --port 8888

# Send a quick test prompt
cmm prompt "Explain the purpose of a mock LLM"

# Change the active provider to vLLM
cmm provider set vllm

# List all models available for the current provider
cmm list
```

!!! warning "Common Pitfall"
    Ensure that no other service is occupying the port (default 8888) before starting the server, as CMM will fail to bind to the port if it is already in use.

## Technical Architecture

CMM uses a decoupled architecture to separate the API delivery layer from the simulated logic.

### The Provider Pattern

At the heart of CMM is the `BaseProvider` abstract base class. Every simulated provider (e.g., `OllamaProvider`, `VllmProvider`) must implement this interface.

```python
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def prompt(self, prompt_text: str) -> str:
        """Return a deterministic mock response for the given prompt."""
        pass

    @abstractmethod
    def list_models(self) -> list:
        """Return a list of models simulated by this provider."""
        pass
```

### Dynamic Dispatch

When a request hits the `/v1/chat/completions` endpoint, CMM uses a factory to determine which provider to use based on the `model` parameter in the JSON request. If the model starts with `ollama-`, the `OllamaProvider` is dispatched; otherwise, it defaults to the currently set active provider.

### Request Lifecycle

1. Request: Client sends a POST request to `/v1/chat/completions`.
2. Validation: FastAPI/Pydantic validates the JSON structure against the OpenAI spec.
3. Dispatch: The Provider Factory selects the correct `BaseProvider` implementation.
4. Simulation: The provider returns a deterministic string based on the mock logic.
5. Formatting: The response is wrapped in the standard OpenAI JSON envelope.

## Deployment and Orchestration

CMM can be deployed as a local process or as a containerized service.

### Local Installation

```bash
# Clone the repository
git clone https://github.com/cloudmesh-ai/cloudmesh-ai-cmm.git
cd cloudmesh-ai-cmm

# Install the package in editable mode
pip install -e .
```

### Docker Deployment

For CI/CD pipelines, Docker is the preferred method. CMM includes a `docker-compose.yml` for rapid deployment.

```bash
# Start the mock server in the background
docker-compose up -d

# Stop the mock server
docker-compose down
```

!!! note "Persistence"
    When running in Docker, CMM persists its configuration to the host machine via a volume mount to `~/.config/cloudmesh/`. This ensures that provider settings survive container restarts.

## Summary Checklist

!!! tip "Summary Checklist"
    * [ ] CMM is installed and the server is running.
    * [ ] The application `api_base` is pointed to `http://localhost:8888/v1`.
    * [ ] The `cmm` CLI is used to switch between Ollama and vLLM providers.
    * [ ] API requests are validated against the OpenAI specification.
    * [ ] The mock server is integrated into the CI/CD pipeline via Docker.

## Assignments

!!! note "Basic: Setup and First Prompt"
    Install `cloudmesh-ai-cmm` and start the server. Use the `cmm prompt` command to send three different questions to the mock LLM. Verify that the server is responding on port 8888.
    ??? question "Solution"
        1. `git clone https://github.com/cloudmesh-ai/cloudmesh-ai-cmm.git`
        2. `cd cloudmesh-ai-cmm && pip install -e .`
        3. `cmm serve --port 8888` (in one terminal)
        4. `cmm prompt "What is 2+2?"` (in another terminal)

!!! note "Intermediate: Client Integration"
    Write a small Python script using the `openai` library. Configure it to use the CMM server as the `base_url`. Send a chat completion request and print the result.
    ??? question "Solution"
        ```python
        from openai import OpenAI

        # Configure client to use CMM mock server
        client = OpenAI(api_key="mock", base_url="http://localhost:8888/v1")

        # Create a completion request
        res = client.chat.completions.create(
            model="ollama-llama3",
            messages=[{"role": "user", "content": "Test"}]
        )
        print(res.choices[0].message.content)
        ```

!!! note "Advanced: CI/CD Mock Test"
    Create a bash script that starts the CMM server in the background, sends a `curl` request to the `/v1/chat/completions` endpoint, and checks if the response contains the expected mock JSON structure. The script should exit with code 0 if successful and 1 otherwise.
    ??? question "Solution"
        ```bash
        #!/bin/bash

        # Start server in background
        cmm serve --port 8888 &
        SERVER_PID=$!
        sleep 2

        # Test the endpoint
        RESPONSE=$(curl -s http://localhost:8888/v1/chat/completions -H "Content-Type: application/json" -d '{"model": "ollama-llama3", "messages": [{"role": "user", "content": "Hi"}]}')

        # Cleanup
        kill $SERVER_PID

        # Verify the result contains OpenAI expected keys
        if echo "$RESPONSE" | grep -q "choices"; then
            echo "Test Passed"
            exit 0
        else
            echo "Test Failed"
            exit 1
        fi
        ```

## References

* [CloudMesh AI CMM Repository](https://github.com/cloudmesh-ai/cloudmesh-ai-cmm)
* [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
* [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Self-Evaluation

??? note "What is the primary purpose of CloudMesh AI CMM?"
    CMM is a mock LLM provider that simulates OpenAI-compatible APIs to allow developers to test AI applications without needing real GPUs or paying for API credits.

??? note "How does CMM achieve 'zero code changes' when replacing a real LLM?"
    It implements the standard OpenAI REST API, allowing developers to simply change the `api_base` or `base_url` in their existing LLM client configuration.

??? note "What is the difference between the Ollama and vLLM simulations in CMM?"
    They simulate different provider personalities, including different available model lists and response behaviors, to test application robustness across different backends.

??? note "Which Python design pattern is used to implement the different mock providers?"
    The Provider Pattern, utilizing a `BaseProvider` abstract base class that concrete providers (like `OllamaProvider`) implement.

??? note "How can CMM be used to ensure that an AI application's deployment is stable?"
    By integrating CMM into CI/CD pipelines via Docker, developers can run automated tests against a deterministic mock API, ensuring that the application logic is correct before deploying to production LLMs.
