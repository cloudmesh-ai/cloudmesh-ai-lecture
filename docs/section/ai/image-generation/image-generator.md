# Generating Images with Flux on NVIDIA DGX Spark via liteLLM

This tutorial explains how to deploy the **Flux.1 (black-forest-labs/flux-3-image-klein-base)** model on a headless **NVIDIA DGX Spark** and expose it via a **liteLLM proxy on your laptop**.

Since the DGX Spark and the laptop are on the same network, we use a direct IP connection for the fastest and simplest setup.

## Architecture Overview

**User/Claude** $\rightarrow$ **liteLLM Proxy (Laptop)** $\rightarrow$ **DGX Spark (GB10 Blackwell)** $\rightarrow$ **Flux Model (running in tmux)**

---

## 1. Backend Setup (DGX Spark)

The DGX Spark is typically run as a "headless" server (no monitor). You will manage it via SSH from your laptop.

### Environment Installation
SSH into your Spark and run:

```bash
# Create a virtual environment
python3 -m venv flux-env
source flux-env/bin/activate

# Install Blackwell-optimized PyTorch (CUDA 12.4+)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install core dependencies
pip install diffusers transformers accelerate sentencepiece
```

### Persistence with `tmux`
Because the Spark is headless, you must use `tmux` to keep your servers running after you disconnect your SSH session. Without `tmux`, the server will crash the moment you close your terminal.

1.  Start a new session: `tmux new -s flux-session`
2.  (Inside tmux) Run your chosen engine (see below).
3.  **Detach** from the session: Press `Ctrl + B`, then `D`.
    *   *Your server is now running in the background and will stay alive even if your laptop is turned off.*
4.  **Re-attach** later: `tmux attach -t flux-session`

### Monitoring Your Hardware (Observability)
As an educator and researcher, it is important to see what is happening inside the GPU during the generation process. You can monitor the **GB10 Blackwell** chip in real-time.

**1. The Standard View (`nvidia-smi`)**
Run this command to see a snapshot of your GPU state:
```bash
nvidia-smi
```
**What to look for:**
*   **Memory-Usage:** Check how much of the unified memory is occupied by the Flux model.
*   **GPU-Util:** Watch this percentage spike when you trigger an image generation; it shows how hard the Blackwell chip is working.

**2. The Visual View (`nvtop`)**
For a real-time, interactive graph (similar to `htop`), install and run `nvtop`:
```bash
sudo apt-get install nvtop
nvtop
```
`nvtop` is highly recommended for students because it provides a live visual representation of GPU load and memory pressure, making the "cost" of generation visible.

### Choice of Engines (Inside `tmux`)

#### Option A: The API Bridge (For liteLLM/Agents)
Install dependencies: `pip install fastapi uvicorn python-multipart`

Create `flux_server.py`:
```python
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import FluxPipeline
import base64
from io import BytesIO

app = FastAPI()

# Load Flux into GB10 Unified Memory (Full bfloat16 precision)
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/flux-3-image-klein-base", 
    torch_dtype=torch.bfloat16
).to("cuda")

class ImageRequest(BaseModel):
    prompt: str
    n: int = 1
    size: str = "1024x1024"

@app.post("/v1/images/generations")
async def generate_image(request: ImageRequest):
    try:
        width, height = map(int, request.size.split('x'))
        image = pipe(
            request.prompt,
            height=height,
            width=width,
            guidance_scale=3.5,
            num_inference_steps=50,
            max_sequence_length=512,
        ).images[0]
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return {"created": 0, "data": [{"b64_json": img_str}]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Bind to 0.0.0.0 to allow network access from your laptop
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
Run: `python flux_server.py`

#### Option B: ComfyUI (For Education and Creative Control)
Install:
```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt
```
Run: `python main.py --listen 0.0.0.0`

---

## 2. Proxy Setup (Your Laptop)

Configure liteLLM on your laptop to route requests to the DGX Spark via its network IP.

### Configuration (`config.yaml`)
Replace `<dgx-spark-ip>` with the actual IP address of your DGX Spark machine.

```yaml
model_list:
  - model_name: flux-spark
    litellm_params:
      model: openai/flux-spark 
      api_base: http://<dgx-spark-ip>:8000/v1
      api_key: "not-needed"
```

### Start the Proxy
```bash
pip install 'litellm[proxy]'
litellm --config config.yaml
```

---

## 3. Accessing Flux via Claude

### Using Claude Code (CLI)
Since the proxy is on your laptop, Claude can call it via `localhost`.

**Example Command:**
```bash
curl http://localhost:4000/v1/images/generations \
  -H "Content-Type: application/json" \
  -d '{
    "model": "flux-spark",
    "prompt": "A futuristic DGX Spark computer in a neon cyberpunk city",
    "size": "1024x1024"
  }' | jq -r '.data[0].b64_json' | base64 -d > output.png
```

### Using Claude Desktop (UI)
To enable a seamless "Generate Image" experience in the UI, implement an **MCP (Model Context Protocol)** tool on your laptop that calls the `flux-spark` model via your local liteLLM proxy.

---

## Hardware Performance Note
On the **DGX Spark (GB10)**, this pipeline runs in **full bfloat16 precision**. With 64GB-128GB of unified memory, you can run both the API bridge and ComfyUI simultaneously without needing 4-bit quantization or CPU offloading.
