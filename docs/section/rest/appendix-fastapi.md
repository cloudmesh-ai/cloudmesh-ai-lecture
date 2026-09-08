# Appendix: Modernizing with FastAPI

!!! info "Context"
    In the previous chapters, we explored the traditional "Design-First" approach (OpenAPI $\rightarrow$ Connexion) and the "Resource-Based" approach (Flask-RESTful). In the modern Python ecosystem, **FastAPI** has emerged as one of the most popular choices for building REST APIs.

---

## What is FastAPI?

**FastAPI** is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.

### The "Magic" of FastAPI
FastAPI's primary advantage is that it integrates the specification and the implementation into a single source of truth: your Python code.

- **Automatic OpenAPI Generation**: You don't write a YAML file; FastAPI generates it automatically based on your function signatures and type hints.
- **Automatic Documentation**: Because it has the OpenAPI spec, it provides **Swagger UI** and **ReDoc** out-of-the-box at `/docs` and `/redoc`.
- **Data Validation**: Using **Pydantic**, FastAPI validates incoming request bodies automatically. If a user sends a string where an integer is expected, FastAPI returns a clear `422 Unprocessable Entity` error without you writing a single line of validation code.
- **Asynchronous Support**: Built on `Starlette` and `pydantic`, it natively supports `async` and `await`, making it significantly faster for I/O-bound operations compared to Flask.

---

## FastAPI vs. Flask-RESTful: A Code Comparison

Let's look at how the "Computer" resource from Chapter 5 would be implemented in FastAPI.

### The FastAPI Implementation
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Pydantic model for data validation
class Computer(BaseModel):
    processor: str

# In-memory data store
computers: Dict[str, Computer] = {
    "computer1": Computer(processor="iCore7"),
    "computer2": Computer(processor="iCore5"),
}

@app.get("/computers/{computer_id}")
async def get_computer(computer_id: str):
    if computer_id not in computers:
        raise HTTPException(status_code=404, detail="Computer not found")
    return computers[computer_id]

@app.post("/computers/{computer_id}", status_code=201)
async def create_computer(computer_id: str, computer: Computer):
    computers[computer_id] = computer
    return computer
```

### Key Differences:
1.  **Validation**: In Flask-RESTful, we used `reqparse`. In FastAPI, we use a `Pydantic` model (`Computer`). The validation happens automatically.
2.  **Documentation**: In Flask, you'd need to write a separate `openapi.yaml` or use a plugin. In FastAPI, you just run the app and visit `/docs`.
3.  **Types**: FastAPI uses Python type hints (`computer_id: str`) to determine how to parse and validate the URL parameters.

---

## The Great Comparison: Which approach to choose?

| Feature | Flask-RESTful | Connexion (OpenAPI-First) | FastAPI (Code-First) |
|---------|----------------|-----------------------------|-----------------------|
| **Workflow** | Code $\rightarrow$ API | Spec (YAML) $\rightarrow$ Code | Code $\rightarrow$ Spec (Auto) |
| **Validation** | Manual (`reqparse`) | Automatic (via Spec) | Automatic (via Pydantic) |
| **Documentation**| Manual/Plugin | Automatic (from Spec) | Automatic (built-in) |
| **Performance** | Standard (WSGI) | Standard (WSGI) | High (ASGI/Async) |
| **Best For...** | Small, simple APIs | Large teams, "Contract-First" design | High performance, rapid dev, modern stacks |

### Summary: When to use what?

- **Use Connexion/OpenAPI-First** when you are in a large organization where the API contract must be agreed upon by stakeholders *before* any code is written.
- **Use Flask-RESTful** when you are maintaining legacy Flask applications or need a very simple, class-based structure without the overhead of async.
- **Use FastAPI** for almost all new Python projects. It provides the best developer experience, the highest performance, and eliminates the need to manually synchronize your code with your documentation.
