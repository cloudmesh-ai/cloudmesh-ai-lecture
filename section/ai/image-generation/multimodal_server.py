import torch
import subprocess
import base64
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import FluxPipeline
from io import BytesIO

app = FastAPI()

# 1. Load Flux Model
print("Loading Flux model into GB10 Unified Memory...")
flux_pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/flux-3-image-klein-base",
    torch_dtype=torch.bfloat16
).to("cuda")

class GenerationRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"

# --- FLUX IMAGE GENERATION ---
@app.post("/v1/flux/generate")
async def gen_flux(request: GenerationRequest):
    image = flux_pipe(request.prompt, height=1024, width=1024).images[0]
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return {"data": [{"b64_json": base64.b64encode(buffered.getvalue()).decode()}]}

# --- MERMAID DIAGRAMS (Simple/Fast) ---
@app.post("/v1/mermaid/generate")
async def gen_mermaid(request: GenerationRequest):
    with open("temp.mmd", "w") as f:
        f.write(request.prompt)
    subprocess.run(["mmdc", "-i", "temp.mmd", "-o", "temp.png"], check=True)
    with open("temp.png", "rb") as f:
        return {"data": [{"b64_json": base64.b64encode(f.read()).decode()}]}

# --- D2 DIAGRAMS (Modern/Colorful) ---
@app.post("/v1/d2/generate")
async def gen_d2(request: GenerationRequest):
    with open("temp.d2", "w") as f:
        f.write(request.prompt)
    subprocess.run(["d2", "temp.d2", "temp.png"], check=True)
    with open("temp.png", "rb") as f:
        return {"data": [{"b64_json": base64.b64encode(f.read()).decode()}]}

# --- INFRA MAPS (Professional Icons/Architecture) ---
@app.post("/v1/infra/generate")
async def gen_infra(request: GenerationRequest):
    # The 'diagrams' library requires a python script to be executed
    with open("temp_diag.py", "w") as f:
        # Wrap the user prompt (which should be python code) in a basic script
        f.write("from diagrams import Cluster, Diagram\n")
        f.write(request.prompt)

    subprocess.run(["python3", "temp_diag.py"], check=True)
    # The 'diagrams' library saves the file based on the Diagram() class name
    # For simplicity, we assume the student names the diagram 'infra_map'
    with open("infra_map.png", "rb") as f:
        return {"data": [{"b64_json": base64.b64encode(f.read()).decode()}]}

# --- MARP SLIDES ---
@app.post("/v1/slides/generate")
async def gen_slides(request: GenerationRequest):
    with open("temp.md", "w") as f:
        f.write(request.prompt)
    subprocess.run(["marp", "temp.md", "-o", "temp.pdf"], check=True)
    with open("temp.pdf", "rb") as f:
        return {"data": [{"b64_json": base64.b64encode(f.read()).decode()}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
