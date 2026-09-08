# 5. Practical Implementation

!!! info "Learning Objectives"
    - Learn how to build a REST API using Python and Flask.
    - Implement the Flask-RESTful extension for class-based resources.
    - Explore modern API development with FastAPI.
    - Create a complete CRUD service using both frameworks.

---

## Option A: Building with Flask and Flask-RESTful

**Flask** is a micro-framework for Python that is ideal for building REST APIs due to its simplicity and flexibility. While you can build APIs with standard Flask routes, the **Flask-RESTful** extension provides a more structured, class-based approach.

### Why Flask-RESTful?
- **Resource-Based**: It encourages you to think in terms of "Resources" rather than "URL routes".
- **Cleaner Code**: Groups all methods for a single resource (GET, POST, etc.) into one class.
- **Automatic Parsing**: Simplifies request argument parsing.

### Example: A Computer Inventory Service (Flask)

```python
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

# In-memory data store
COMPUTERS = {
    'computer1': {'processor': 'iCore7'},
    'computer2': {'processor': 'iCore5'},
    'computer3': {'processor': 'iCore3'},
}

# Helper for error handling
def abort_if_computer_doesnt_exist(computer_id):
    if computer_id not in COMPUTERS:
        abort(404, message="Computer {} does not exist".format(computer_id))

# Request parser for input validation
parser = reqparse.RequestParser()
parser.add_argument('processor')

class Computer(Resource):
    ''' Handles operations on a single computer resource '''
    def get(self, computer_id):
        abort_if_computer_doesnt_exist(computer_id)
        return COMPUTERS[computer_id]

    def delete(self, computer_id):
        abort_if_computer_doesnt_exist(computer_id)
        del COMPUTERS[computer_id]
        return '', 204

    def put(self, computer_id):
        args = parser.parse_args()
        processor = {'processor': args['processor']}
        COMPUTERS[computer_id] = processor
        return processor, 201

class ComputerList(Resource):
    ''' Handles operations on the collection of computers '''
    def get(self):
        return COMPUTERS

    def post(self):
        args = parser.parse_args()
        # Simple logic to generate a new ID
        computer_id = f"computer{len(COMPUTERS) + 1}"
        COMPUTERS[computer_id] = {'processor': args['processor']}
        return COMPUTERS[computer_id], 201

# Routing
api.add_resource(ComputerList, '/computers')
api.add_resource(Computer, '/computers/<string:computer_id>')

if __name__ == '__main__':
    app.run(debug=True)
```

### Breakdown of the Implementation
1.  **`Resource` Classes**: `Computer` and `ComputerList` inherit from `Resource`. The methods inside (`get`, `post`, etc.) map directly to HTTP methods.
2.  **`api.add_resource`**: This tells Flask which URL corresponds to which resource class.
3.  **`reqparse`**: Used to ensure that the incoming `POST` or `PUT` requests contain the required `processor` field.
4.  **`abort`**: Returns a specific HTTP status code (e.g., 404) and a custom error message.

---

## Option B: Building with FastAPI

**FastAPI** is a modern, high-performance framework based on standard Python type hints. Unlike Flask-RESTful, which uses a class-based approach, FastAPI uses a functional approach with powerful decorators and automatic data validation via **Pydantic**.

### Why FastAPI?
- **Automatic Documentation**: No need to write a separate spec; visit `/docs` to see your interactive Swagger UI.
- **Type Safety**: Uses Python type hints to validate data automatically.
- **Async by Default**: Built for high performance using `async` and `await`.

### Example: A Computer Inventory Service (FastAPI)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# Pydantic model for data validation (Replaces reqparse)
class ComputerModel(BaseModel):
    processor: str

# In-memory data store
COMPUTERS: Dict[str, ComputerModel] = {
    "computer1": ComputerModel(processor="iCore7"),
    "computer2": ComputerModel(processor="iCore5"),
}

@app.get("/computers")
async def get_all_computers():
    ''' Returns the collection of computers '''
    return COMPUTERS

@app.get("/computers/{computer_id}")
async def get_computer(computer_id: str):
    ''' Returns a single computer '''
    if computer_id not in COMPUTERS:
        raise HTTPException(status_code=404, detail="Computer not found")
    return COMPUTERS[computer_id]

@app.post("/computers/{computer_id}", status_code=201)
async def create_computer(computer_id: str, computer: ComputerModel):
    ''' Creates or updates a computer '''
    COMPUTERS[computer_id] = computer
    return computer

@app.delete("/computers/{computer_id}", status_code=204)
async def delete_computer(computer_id: str):
    ''' Deletes a computer '''
    if computer_id not in COMPUTERS:
        raise HTTPException(status_code=404, detail="Computer not found")
    del COMPUTERS[computer_id]
    return None

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Comparison of the Two Approaches

| Feature | Flask-RESTful | FastAPI |
|---------|----------------|-----------|
| **Programming Style** | Class-based Resources | Function-based with Decorators |
| **Validation** | Manual `reqparse` | Automatic via Pydantic Models |
| **Doc Generation** | Separate / Plugin | Built-in (OpenAPI/Swagger) |
| **Concurrency** | Synchronous (WSGI) | Asynchronous (ASGI) |
| **Execution** | `python app.py` | `uvicorn main:app` |

---

## 🧭 Decision Guide: Which Framework Should You Use?

Choosing the right tool depends on your project requirements, team expertise, and performance needs. Use the following scenarios to guide your decision.

### 1. Use FastAPI if...
- **Performance is critical**: You are building a high-traffic service and need the benefits of `async/await`.
- **You want rapid development**: You want the framework to handle validation and documentation (Swagger) automatically.
- **You are starting a new project**: FastAPI is the modern standard for Python APIs.
- **You love type hints**: You prefer using Python's typing system to define your data models.

### 2. Use Flask-RESTful if...
- **You are working with a legacy codebase**: The project is already built on Flask, and you need to add REST resources without changing the entire architecture.
- **You prefer the Resource Class pattern**: You like the strict separation of a resource into a class with `get`, `post`, `put`, and `delete` methods.
- **You need a very simple, synchronous service**: You don't need async capabilities and prefer a "minimalist" approach.

### 3. Use Connexion (OpenAPI-First) if...
- **The API is a "Contract"**: You are in a large organization where the API design must be approved by multiple stakeholders *before* any code is written.
- **Cross-language teams**: The API spec is the same for the Python backend, a Java microservice, and a TypeScript frontend.
- **Strict Validation**: You want the framework to reject requests that don't strictly adhere to the OpenAPI YAML file.

### Quick Selection Matrix

| If your priority is... | Recommended Choice | Why? |
|-----------------------|-------------------|--------|
| **Speed of Execution** | **FastAPI** | ASGI/Async support. |
| **Speed of Development**| **FastAPI** | Auto-docs and auto-validation. |
| **Strict Contract** | **Connexion** | Spec-driven development. |
| **Legacy Integration** | **Flask-RESTful** | Easy fit into existing Flask apps. |
| **Developer Experience**| **FastAPI** | Best-in-class tooling and type safety. |
