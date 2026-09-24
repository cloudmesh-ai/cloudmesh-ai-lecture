# Exposing Cline Skills via Web API: JetStream Integration

!!! info "Learning Objectives"
    - Understand the OpenAI Chat Completion API schema required by JetStream and other OpenAI-compatible UIs.
    - Implement a FastAPI wrapper to bridge local CLI skills and HTTP endpoints.
    - Configure custom endpoints for skill execution within a web-based LLM interface.
    - Implement function-calling (tool) definitions for per-conversation skill integration.
    - Map unstructured prompt text to structured CLI arguments for skill execution.

Local skills developed for Cline are designed for command-line execution. However, there is often a need to expose these capabilities to a wider audience or integrate them into web-based LLM interfaces, such as the JetStream LLM playground. 

The primary challenge is the interface mismatch: CLI skills expect command-line arguments and emit stdout, while web interfaces expect an HTTP API that follows a specific request and response schema. To bridge this gap, a wrapper service is required to act as a gateway, translating OpenAI-compatible API calls into local script executions and wrapping the results back into the expected JSON format.

## The OpenAI Compatibility Layer

Most modern LLM web interfaces, including JetStream, are built to communicate with the OpenAI Chat Completion API. To make a local skill appear as a "model" in these interfaces, the wrapper must strictly adhere to this protocol.

### Request Schema

JetStream sends a `POST` request to the `/v1/chat/completions` endpoint with a body similar to the following:

```json
{
  "model": "lecture_builder",
  "messages": [
    {
      "role": "user",
      "content": "topic=\"Intro to Python\" audience=\"beginners\" duration=45 depth=hands-on"
    }
  ],
  "max_tokens": 500,
  "temperature": 0.0
}
```

### Response Schema

The wrapper must return a response that matches the OpenAI `chat.completion` object. If the response shape is incorrect, the UI will fail to render the output.

```json
{
  "id": "chatcmpl-unique-id",
  "object": "chat.completion",
  "created": 1725000000,
  "model": "lecture_builder",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "... skill output here ..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

## Implementing the FastAPI Wrapper

FastAPI is the preferred framework for this wrapper due to its lightweight nature, automatic OpenAPI documentation, and native support for asynchronous execution.

### Wrapper Architecture

The wrapper follows a linear processing pipeline:
1. **Request Reception**: Accept the OpenAI-formatted JSON payload.
2. **Argument Extraction**: Parse the `content` field of the last user message to extract CLI arguments.
3. **Skill Execution**: Execute the target Python skill using a subprocess.
4. **Response Formatting**: Wrap the skill's stdout into the OpenAI response schema.

### Complete Implementation

The following code implements a robust wrapper for the `lecture_builder` skill.

```python
import os
import json
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

def run_skill(skill_name: str, user_content: str) -> str:
    """
    Executes a Cline skill by mapping the user content 
    directly as command-line arguments.
    """
    # In a production environment, you would implement a parser 
    # to convert "topic=X audience=Y" into a list of flags.
    # For this example, we assume the user provides the flags directly.
    
    try:
        result = subprocess.run(
            ["./skills/" + skill_name + ".py"] + user_content.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return json.dumps({"error": e.stderr})
    except FileNotFoundError:
        return json.dumps({"error": f"Skill {skill_name} not found."})

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    # Extract the last user message as the arguments for the skill
    user_message = request.messages[-1].content
    skill_name = request.model

    # Execute the skill
    skill_output = run_skill(skill_name, user_message)

    # Construct OpenAI-compatible response
    return {
        "id": "chatcmpl-wrapper",
        "object": "chat.completion",
        "created": 1725000000,
        "model": skill_name,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": skill_output
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Integrating with JetStream

Once the wrapper is deployed to an HTTPS-enabled endpoint, it can be integrated into JetStream via two primary methods.

### Method 1: Custom Endpoint Configuration

This method registers the wrapper as a global model in the JetStream settings.

1. Navigate to **Settings** $\rightarrow$ **API Settings**.
2. Locate the **Custom Endpoint** section.
3. Enter the URL of the wrapper (e.g., `https://my-skill-gateway.com/v1`).
4. In the chat interface, select the model name that matches the `model` field in your wrapper (e.g., `lecture_builder`).

### Method 2: Tool/Function Calling (Per-Conversation)

For users without administrative access to global settings, the function-calling mechanism allows for conversation-level integration.

1. **Define the Tool**: Use the **+ Tool** button in JetStream to provide a JSON schema for the skill.

```json
{
  "name": "lecture_builder",
  "description": "Generates a lecture outline",
  "parameters": {
    "type": "object",
    "properties": {
      "topic": { "type": "string" },
      "audience": { "type": "string" },
      "duration": { "type": "integer" },
      "depth": { "type": "string", "enum": ["overview", "hands-on", "deep-dive"] }
    },
    "required": ["topic", "audience", "duration", "depth"]
  }
}
```

2. **Implement the Function Endpoint**: Create a specific route in your FastAPI app to handle function calls.

```python
@app.post("/function/lecture_builder")
async def lecture_builder_fn(payload: dict):
    args = payload["arguments"]
    # Convert dict to CLI arguments: --topic "X" --audience "Y" ...
    cli_args = " ".join([f"--{k} \"{v}\"" for k, v in args.items()])
    result = run_skill("lecture_builder", cli_args)
    return {"result": json.loads(result)}
```

3. **Execute**: Click the **Run tool** button next to the user prompt in the UI. JetStream will send the structured arguments to the function endpoint and display the result.

## Deployment and Verification

To ensure the wrapper is functioning correctly before integrating with the UI, verify the endpoint using `curl`.

```bash
curl -X POST https://your-endpoint.com/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "lecture_builder",
       "messages": [{"role": "user", "content": "--topic \"Git\" --audience \"Beginners\" --duration 30 --depth overview"}]
     }'
```

A successful response should return a JSON object containing the skill output within the `choices[0].message.content` field.

!!! tip "Summary Checklist"
    - [ ] OpenAI request and response schemas implemented.
    - [ ] FastAPI wrapper deployed to an HTTPS endpoint.
    - [ ] Skill execution logic mapped to the `/v1/chat/completions` route.
    - [ ] Integration verified via Custom Endpoint or Tool calling.
    - [ ] End-to-end flow from Web UI to local skill verified via `curl`.

## Practical Exercises

!!! note "Exercise 1: Basic Wrapper Deployment"
    Deploy the provided FastAPI wrapper for an existing skill (e.g., `lecture_builder`). Use `curl` to send a request and verify that the output is wrapped in the correct OpenAI response schema.

!!! note "Exercise 2: Multi-Skill Dispatcher"
    Modify the `chat_completions` route in the FastAPI app to handle multiple skills. Use the `model` field in the request to determine which script in the `skills/` directory should be executed.

!!! note "Exercise 3: Full Tool Integration"
    Define a custom tool in JetStream using a JSON schema. Implement the corresponding `/function/` endpoint in your FastAPI app and verify that clicking "Run tool" in the UI generates the correct lecture outline.

## Further Reading

- OpenAI API Reference (Chat Completions): https://platform.openai.com/docs/api-reference/chat
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Python `subprocess` Module: https://docs.python.org/3/library/subprocess.html
