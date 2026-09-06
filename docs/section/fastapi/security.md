# Progressive Tutorial: Securing FastAPI Services (From Localhost to Multi-Layered Production & 2FA)

This tutorial guides you through securing a FastAPI service across incremental stages: starting from an open local development setup, scaling up authentication mechanisms, configuring configuration-file-driven multi-user support, and hardening the stack for production using reverse proxies and 2FA.

---

## Stage 1: Core Authentication Patterns

### Step A: No Security (Localhost Only)

For initial local development, authentication can be bypassed by binding the server strictly to the loopback interface (`127.0.0.1`), ensuring access is restricted to the local machine.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome! This service is open, but running locally only."}

```

* **Execution:** `uvicorn main:app --host 127.0.0.1 --port 8000 --reload`
* **Security Level:** Network isolation via loopback interface.

---

### Step B: Password Protected (HTTP Basic Auth)

For lightweight user validation (e.g., internal dashboards), FastAPI’s built-in `HTTPBasic` utility provides native credential prompts using constant-time string comparisons to prevent timing attacks.

```python
import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

@app.get("/secure-data")
def get_secure_data(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "supersecret")
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"message": "Access granted via Password!"}

```

---

### Step C: Key Protected (API Key Header)

For server-to-server communications or external clients, API keys passed through custom headers are preferred over passwords via `APIKeyHeader`.

```python
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN

app = FastAPI()

API_KEY = "my-super-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, 
        detail="Invalid or missing API Key"
    )

@app.get("/api/data")
def get_api_data(api_key: str = Depends(get_api_key)):
    return {"message": "Access granted via API Key!"}

```

---

### Step D: Two-Factor Authentication (2FA)

Two-Factor Authentication combines primary password validation with a time-based one-time password (TOTP) generator using the `pyotp` library.

```python
import pyotp
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import yaml
import secrets

app = FastAPI()

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
USER_DB = config.get("users", {})

class LoginRequest(BaseModel):
    username: str
    password: str
    otp_code: str

@app.post("/login-2fa")
def login_with_2fa(payload: LoginRequest):
    user_info = USER_DB.get(payload.username)
    
    if not user_info or not secrets.compare_digest(payload.password, user_info["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid username or password"
        )
    
    totp = pyotp.TOTP(user_info["totp_secret"])
    if not totp.verify(payload.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid Two-Factor Authentication code"
        )
        
    return {
        "message": f"Welcome, {payload.username}! 2FA verification successful.",
        "role": user_info["role"],
        "token": "mock-jwt-session-token"
    }

```

---

## Stage 2: Scaling with Configuration Files (YAML)

To manage multiple users or roles cleanly without spinning up a full database, store user profiles in an external YAML configuration file.

### 1. Create `config.yaml`

```yaml
users:
  admin:
    password: "password123"
    totp_secret: "JBSWY3DPEHPK3PXP"
    role: "admin"
  developer:
    password: "securepassword456"
    totp_secret: "GEZDGNBVGY3TQOJQ"
    role: "dev"

```

### 2. Multi-User HTTP Basic Application (`main.py`)

```python
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import yaml
import secrets

app = FastAPI()
security = HTTPBasic()

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
USER_DB = config.get("users", {})

def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    user_info = USER_DB.get(credentials.username)
    
    if not user_info or not secrets.compare_digest(credentials.password, user_info["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": credentials.username, "role": user_info["role"]}

@app.get("/dashboard")
def get_dashboard(current_user: dict = Depends(verify_user)):
    return {
        "message": f"Welcome back, {current_user['username']}!",
        "your_role": current_user['role']
    }

```

---

## Stage 3: Production Hardening (HTTPS & Reverse Proxy)

In production, applications should run behind a reverse proxy to manage TLS termination (HTTPS) while binding Uvicorn strictly to localhost.

### Option A: Caddy (Recommended)

Create a `Caddyfile` in your project root:

```text
yourdomain.com {
    reverse_proxy api:8000
}

```

### Option B: Nginx

Configure a server block to proxy internal requests:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

```

---

## Stage 4: Containerization with Docker Compose

Containerize the entire stack to ensure consistent deployments.

### 1. `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```

### 2. `docker-compose.yml`

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: fastapi_app
    restart: always
    volumes:
      - ./config.yaml:/app/config.yaml
    networks:
      - app-net

  caddy:
    image: caddy:latest
    container_name: caddy_proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - app-net

networks:
  app-net:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:

```

To support your progressive workflow, here is how you can containerize your FastAPI service at each major stage of development—from a simple local container to a full production-ready multi-container stack.

---

## Dockerizing Stage 1 & Stage 2: Standalone FastAPI Container

During early development or when testing basic/API-key/2FA auth locally, you only need a single container running your FastAPI app and its configuration file.

### 1. `Dockerfile`

Create this file in your project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and configs
COPY . .

EXPOSE 8000

# Bind to all interfaces inside the container network
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

```

### 2. `requirements.txt`

Make sure your dependencies match your chosen stage (e.g., including `pyyaml` and `pyotp` if using configuration files or 2FA):

```text
fastapi
uvicorn
pyyaml
pyotp

```

### 3. Build & Run Locally

```bash
# Build the image
docker build -t fastapi-security-app .

# Run the container (mounting your config file live if using YAML/2FA)
docker run -d \
  --name fastapi-dev \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  fastapi-security-app

```

---

## Dockerizing Stage 3 & Stage 4: Production Stack (FastAPI + Caddy Reverse Proxy)

For production deployment, you containerize both the FastAPI backend and the Caddy reverse proxy using **Docker Compose**. This ensures your application is shielded behind an internal network and exposed only via secure HTTPS.

### 1. Project Directory Structure

```text
my-fastapi-app/
├── Dockerfile
├── docker-compose.yml
├── config.yaml
├── main.yaml (or main.py)
├── requirements.txt
└── Caddyfile

```

### 2. `Caddyfile`

```text
# Replace localhost with your domain name in production
localhost {
    reverse_proxy api:8000
}

```

### 3. `docker-compose.yml`

```yaml
services:
  api:
    build: .
    container_name: fastapi_app
    restart: always
    volumes:
      - ./config.yaml:/app/config.yaml
    networks:
      - app-net

  caddy:
    image: caddy:latest
    container_name: caddy_proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    networks:
      - app-net

networks:
  app-net:
    driver: bridge

volumes:
  caddy_data:
  caddy_config:

```

### 4. Launch the Production Stack

```bash
# Build and start all services in the background
docker compose up --build -d

```

* **Security Benefit:** The FastAPI `api` container has **no open ports** exposed to the host machine. All external traffic must pass through Caddy, which handles SSL certificates and proxies requests safely over the internal `app-net` bridge network.