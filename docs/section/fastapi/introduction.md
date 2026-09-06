FastAPI is a modern, high-performance Python web framework for building APIs. It relies on standard Python type hints, making it fast to code and extremely beginner-friendly.

---

## 1. Core Tools You Need

* **FastAPI:** The main framework package that handles routing, request handling, and application logic.
* **Uvicorn:** An ASGI (Asynchronous Server Gateway Interface) server used to run your FastAPI application.
* **Pydantic:** The underlying library FastAPI uses for data validation and settings management using Python type annotations.

---

## 2. Quick Setup & Code Example

You can install FastAPI and the standard toolset (including Uvicorn) via pip:

```bash
pip install "fastapi[standard]"

```

Create a file named `main.py` and add this simple code:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
  return {"message": "Hello, FastAPI!"}

```

### Running the App

Start your server locally with auto-reload enabled using the FastAPI CLI or Uvicorn:

```bash
fastapi dev main.py

```

*(Or via Uvicorn directly: `uvicorn main:app --reload`)*

---

## 3. Self-Documentation URLs

One of FastAPI's best features is that it automatically generates interactive API documentation out of the box using the OpenAPI standard.

Once your local server is running (`[http://127.0.0.1:8000](http://127.0.0.1:8000)`), you can instantly access two documentation UIs:

* **Swagger UI (Interactive Docs):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
*Allows you to view all your endpoints, inspect parameters, and click "Try it out" to send live requests right from your browser.*
* **ReDoc (Alternative Docs):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
*Provides a clean, clean-styled alternative documentation layout.*

---

[Python FastAPI Tutorial (Part 1): Getting Started - Web App + REST API](https://www.youtube.com/watch?v=7AMjmCTumuo)

This video provides a helpful visual walkthrough of installing FastAPI, writing your first routes, and exploring the automatic documentation interface.

## Appendix Install options

When installing FastAPI, the text inside the brackets (`[standard]`) represents **optional dependency groups** (extras).

Depending on your project's needs, you have three primary installation options:

---

### 1. `pip install fastapi` (The Minimalist Core)

* **What it installs:** Only the strict framework essentials (`fastapi`, `pydantic`, and `starlette`).
* **What it leaves out:** It does **not** include an ASGI server (like Uvicorn) or standard CLI tools.
* **Best for:** Advanced developers who want to tightly control their environment, use a custom ASGI server (like Hypercorn or Granian), or build lean Docker containers where every megabyte counts.
* *Note:* If you use this, running `uvicorn` out of the box will throw a "command not found" error unless you install Uvicorn separately.

### 2. `pip install "fastapi[standard]"` (The Recommended Default)

* **What it installs:** The core framework **plus** the officially curated bundle of tools required for robust production and local development. This includes:
* **Uvicorn** (the actual web server that runs your code)
* **FastAPI CLI** (for commands like `fastapi dev`)
* **Pydantic-extra-types** and **pydantic-settings** (for managing configurations and extra data types)
* **Email-validator** (for validating email fields)
* **Jinja2** (if you want to render HTML templates)


* **Best for:** 95% of use cases, tutorials, and standard web applications.

### 3. `pip install "fastapi[all]"` (The Kitchen Sink)

* **What it installs:** Everything in `[standard]` plus a wider array of optional, specialized libraries that FastAPI can interface with.
* **Best for:** Rapid prototyping or specific local workflows where you don't want to worry about missing an extra package.
* **Downside:** It can cause heavier Docker images and bloated dependency trees ("dependency hell") for production apps.

---

### Summary Recommendation

Stick with **`"fastapi[standard]"`** unless you are building a custom, highly optimized micro-container (where you would use bare `fastapi`).

## Appendix Production

**Yes, you can use Uvicorn in production**, but **how** you run it matters heavily.

Running a single Uvicorn process (`uvicorn main:app`) is fine for low-traffic apps or development, but it will only use **a single CPU core**, leaving your multi-core server underutilized and vulnerable to crashing without an auto-restart mechanism.

Depending on your infrastructure, there are two primary ways to set up Uvicorn safely for production:

---

### Option 1: Using Uvicorn with Multiple Workers (Simplest)

If you are running on a standard Linux server, container, or cloud host, you can let Uvicorn manage multiple worker processes directly to leverage all CPU cores.

Instead of using `uvicorn main:app --reload` (which is for development), use the production command:

```bash
fastapi run main.py --workers 4

```

*(Or using Uvicorn directly: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`)*

* **Why this works:** It spins up a master process that oversees multiple worker processes (typically matched to your number of CPU cores), distributing incoming traffic among them.

---

### Option 2: Gunicorn + Uvicorn Workers (Industry Standard)

For large-scale, high-traffic applications, the most battle-tested production pattern is using **Gunicorn** as the process manager combined with **Uvicorn worker classes**.

Gunicorn excels at managing worker lifecycles, gracefully restarting memory leaks, and handling unexpected crashes, while Uvicorn handles the high-performance async web traffic.

#### 1. Install both packages:

```bash
pip install "fastapi[standard]" gunicorn

```

#### 2. Run Gunicorn:

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

```

* **`--workers 4`**: Spawns 4 parallel processes.
* **`--worker-class uvicorn.workers.UvicornWorker`**: Tells Gunicorn to use Uvicorn's asynchronous engine under the hood so FastAPI can process async requests efficiently.
* *Crucial Rule:* **Never** use `uvicorn.run()` inside your Python code when using Gunicorn, as it will accidentally multiply your workers and overload your server CPU.

---

### Option 3: Modern Containerized / Kubernetes Setups

If you are deploying your app inside **Docker** or **Kubernetes**:

* You generally **do not** need Gunicorn or multi-worker flags.
* Instead, you run a **single** Uvicorn process per container (`fastapi run main.py` or `uvicorn main:app --host 0.0.0.0 --port 80`).
* You scale horizontally by spinning up **multiple Docker containers** or Kubernetes pods, letting the container orchestrator handle load balancing, restarts, and scaling.

---

### Summary Checklist for Production

1. **Never use `--reload**` in production.
2. Put a **reverse proxy** like **Nginx** or a cloud load balancer in front of your server to handle SSL certificates (HTTPS) and security headers.
3. Use multiple workers (either via `fastapi run --workers` or Gunicorn) to utilize all available CPU cores.

Are you planning to deploy your app using a traditional cloud VPS (like Ubuntu/AWS EC2) or via Docker/Containers?

## Appendix Containerization

Using Docker or Kubernetes completely changes how you handle Uvicorn.

When you use container orchestration, **you generally run a single Uvicorn process per container**. You scale horizontally by launching more containers (pods) or letting Kubernetes handle replication, rather than managing multiple workers inside a single container.

---

### Step 1: Create a Production `Dockerfile`

Create a file named `Dockerfile` in your project root. This uses an official, lightweight Python slim image, installs your dependencies, and runs Uvicorn using the recommended **exec form** (`CMD`) so your container stops gracefully:

```dockerfile
# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirement definitions and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Run Uvicorn via FastAPI CLI (Single process per container)
# --proxy-headers is crucial if you sit behind Nginx, ALB, or an Ingress controller
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

```

*(Make sure your `requirements.txt` contains `fastapi[standard]`)*

---

### Step 2: Build and Run with Docker

Build your local image:

```bash
docker build -t my-fastapi-app .

```

Run your container, mapping port 8000 on your machine to port 8000 inside the container:

```bash
docker run -d -p 8000:8000 --name fastapi-container my-fastapi-app

```

Your app is now live, and you can visit `http://localhost:8000/docs` to see your self-documenting Swagger UI.

---

### Step 3: Scaling with Kubernetes

If you deploy this to Kubernetes, you don't need complex multi-worker process managers like Gunicorn. Kubernetes handles the scaling natively.

You define a simple **Deployment** manifest (`deployment.yaml`) that specifies how many replicas (pods) you want:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-deployment
spec:
  replicas: 3 # Kubernetes will run 3 isolated pods of your app
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
  containers:
  - name: fastapi
    image: your-docker-registry/my-fastapi-app:latest
    ports:
    - containerPort: 8000

```

* **Why this is ideal:** If traffic spikes, Kubernetes spins up more pods. If a container crashes, Kubernetes kills it and replaces it automatically.

Would you like an example of how to tie multiple containers together locally using **Docker Compose** (for example, adding a PostgreSQL database alongside your FastAPI app)?