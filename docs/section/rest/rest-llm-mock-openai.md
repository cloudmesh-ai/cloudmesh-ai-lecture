# Mocking LLMs with OpenAI-Compatible REST Services

!!! info Learning Objectives
    - Understand the importance of mocking LLM APIs for development and testing.
    - Implement an OpenAI-compatible REST server using FastAPI.
    - Create streaming responses using Server-Sent Events (SSE).
    - Validate requests and responses using Pydantic models to match the OpenAI specification.

## Overview

Mocking LLM APIs is a practice in AI software engineering. By simulating the behavior of a provider like OpenAI, developers can:

- **Reduce Costs**: Avoid incurring API charges during iterative development and automated testing.
- **Increase Determinism**: Eliminate the stochastic nature of LLMs to ensure CI/CD pipelines have predictable outcomes.
- **Improve Speed**: Remove network latency and API rate limits from the development loop.
- **Enable Offline Development**: Work without requiring a constant internet connection to external providers.

## Implementation

Below is a complete implementation of a mock OpenAI server using FastAPI.

```python
import asyncio
import json
from typing import List, Optional, Union, AsyncGenerator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Mock OpenAI Server")

# --- Pydantic Models for OpenAI Specification ---

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[dict]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.7

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: dict
    finish_reason: str

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]

class Model(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "mock-org"

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[Model]

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str

class EmbeddingResponse(BaseModel):
    object: str = "embedding"
    data: List[dict]
    model: str
    usage: dict

# --- Mock Logic ---

MOCK_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
MOCK_RESPONSES = {
    "hello": "Hello! I am a mock LLM. How can I help you today?",
    "test": "This is a deterministic test response.",
    "default": "I am a mock assistant. You asked: "
}

def get_mock_text(prompt: str) -> str:
    prompt_lower = prompt.lower()
    for key, value in MOCK_RESPONSES.items():
        if key in prompt_lower:
            return value
    return f"{MOCK_RESPONSES['default']}{prompt}"

# --- Routes ---

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/v1/models", response_model=ModelListResponse)
async def list_models():
    return {
        "data": [Model(id=m, created=1677649420) for m in MOCK_MODELS]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    user_message = request.messages[-1]["content"] if request.messages else ""
    response_text = get_mock_text(user_message)
    
    if request.stream:
        return StreamingResponse(
            generate_stream(response_text, request.model),
            media_type="text/event-stream"
        )

    return ChatCompletionResponse(
        id="chatcmpl-mock-123",
        created=1677649420,
        model=request.model,
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message={"role": "assistant", "content": response_text},
                finish_reason="stop"
            )
        ]
    )

@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    inputs = [request.input] if isinstance(request.input, str) else request.input
    embeddings = [[0.1] * 1536 for _ in inputs]
    return {
        "data": [{"object": "embedding", "embedding": e, "index": i} for i, e in enumerate(embeddings)],
        "model": request.model,
        "usage": {"prompt_tokens": 10, "total_tokens": 10}
    }

async def generate_stream(text: str, model: str) -> AsyncGenerator[str, None]:
    chunk_id = "chatcmpl-stream-mock"
    for i in range(0, len(text), 4):
        chunk = text[i : i + 4]
        data = {
            "id": chunk_id,
            "object": "chat.completion.chunk",
            "created": 1677649420,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": chunk},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(0.1)
    yield "data: [DONE]\n\n"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Running the Example

1. **Install Dependencies**
   Install FastAPI and Uvicorn:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

2. **Start the Server**
   Run the script:
   ```bash
   python mock_openai.py
   ```

3. **Verify Connectivity**
   The server will be available at `http://localhost:8000`.

## Testing the API

Use the following `curl` commands to verify the mock routes.

**List Models**
```bash
curl http://localhost:8000/v1/models
```

**Chat Completion (Standard)**
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

**Chat Completion (Streaming)**
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Test streaming"}],
    "stream": true
  }'
```

**Embeddings**
```bash
curl http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "The food was delicious"
  }'
```

## Appendix: API Route Reference

Note that the example introduced earlier shows only a small example of route. 
Here is a core table of the primary **OpenAI API** routes, methods, and descriptions:

| Route | Method | Description |
| --- | --- | --- |
| `/v1/chat/completions` | `POST` | Creates a model response for the given chat conversation input. |
| `/v1/completions` | `POST` | Creates a completion for the provided prompt and parameters (Legacy). |
| `/v1/embeddings` | `POST` | Creates an embedding vector representing the input text. |
| `/v1/audio/transcriptions` | `POST` | Transcribes audio into the input language. |
| `/v1/audio/translations` | `POST` | Translates audio into English. |
| `/v1/audio/speech` | `POST` | Generates audio from the input text (Text-to-Speech). |
| `/v1/images/generations` | `POST` | Creates an image given a prompt. |
| `/v1/images/edits` | `POST` | Creates an edited or extended image given an original image and prompt. |
| `/v1/images/variations` | `POST` | Creates a variation of a given image. |
| `/v1/files` | `GET` | Returns a list of files that belong to the user's organization. |
| `/v1/files` | `POST` | Upload a file that can be used across various endpoints. |
| `/v1/files/{file_id}` | `DELETE` | Delete a specific file. |
| `/v1/models` | `GET` | Lists the currently available models and provides basic info about each. |
| `/v1/models/{model}` | `GET` | Retrieves a model instance, providing basic information about the model. |
| `/v1/moderations` | `POST` | Classifies if text violates OpenAI's content policies. |
| `/v1/fine_tuning/jobs` | `POST` | Creates a fine-tuning job which begins the process of training a new model. |
| `/v1/batches` | `POST` | Creates and executes a batch request for asynchronous processing. |

!!! note
    If we missed routes, please add them
    
## Summary Checklist

- [ ] Server implements `/v1/models` to list available mocks.
- [ ] `/v1/chat/completions` handles standard JSON responses.
- [ ] `/v1/chat/completions` implements SSE for streaming.
- [ ] `/v1/embeddings` returns simulated vector data.
- [ ] Pydantic models enforce OpenAI API schema.

!!! note Assignments
    - Modify the `get_mock_text` function to return specific responses based on a JSON configuration file.
    - Implement a simulated "latency" middleware that adds a random delay to responses to test client timeouts.
    - Add a `/v1/chat/completions` error handler that randomly returns a 429 (Too Many Requests) to test retry logic in your application.

??? note "Can I explain the difference between a standard REST response and a Server-Sent Event (SSE) stream?"
    A standard REST response sends the entire payload at once after the request is processed. An SSE stream sends data in small chunks as they become available, allowing the client to display text in real-time as it is "generated".

??? note "Do I understand why Pydantic models are used to mimic the OpenAI specification?"
    Pydantic models ensure that the request and response payloads exactly match the OpenAI API schema (keys, data types, and structures). This allows any client designed for OpenAI to interact with the mock server without modification.

??? note "Can I successfully integrate this mock server into a Python client using the `openai` library by changing the `base_url`?"
    Yes, by initializing the OpenAI client with `base_url="http://localhost:8000/v1"`, the library directs all requests to the mock server instead of the actual OpenAI endpoints.
