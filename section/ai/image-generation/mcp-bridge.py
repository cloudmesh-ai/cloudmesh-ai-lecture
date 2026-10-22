from mcp.server.fastmcp import FastMCP
import requests
import base64
import os
from datetime import datetime

# Initialize FastMCP server
mcp = FastMCP("DGX-Spark-Multimodal")

# Configuration: Point this to your local liteLLM proxy
LITELLM_PROXY_URL = "http://localhost:4000/v1/images/generations"
OUTPUT_DIR = "ai_outputs"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_base64_file(b64_string, extension):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output_{timestamp}.{extension}"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64_string))
    return os.path.abspath(filepath)

@mcp.tool()
def generate_flux_image(prompt: str) -> str:
    """Generates a photorealistic image using Flux. Best for art, concepts, and realism."""
    payload = {"model": "flux-spark", "prompt": prompt, "size": "1024x1024"}
    try:
        response = requests.post(LITELLM_PROXY_URL, json=payload, timeout=120)
        response.raise_for_status()
        path = save_base64_file(response.json()["data"][0]["b64_json"], "png")
        return f"✅ Flux Image saved to: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
def generate_simple_diagram(mermaid_code: str) -> str:
    """Generates a simple, fast flowchart or sequence diagram using Mermaid.js."""
    payload = {"model": "mermaid-spark", "prompt": mermaid_code}
    try:
        response = requests.post(LITELLM_PROXY_URL, json=payload, timeout=60)
        response.raise_for_status()
        path = save_base64_file(response.json()["data"][0]["b64_json"], "png")
        return f"✅ Mermaid Diagram saved to: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
def generate_colorful_diagram(d2_code: str) -> str:
    """Generates a modern, colorful, and professional conceptual diagram using D2."""
    payload = {"model": "d2-spark", "prompt": d2_code}
    try:
        response = requests.post(LITELLM_PROXY_URL, json=payload, timeout=60)
        response.raise_for_status()
        path = save_base64_file(response.json()["data"][0]["b64_json"], "png")
        return f"✅ D2 Diagram saved to: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
def generate_infra_map(python_code: str) -> str:
    """Generates a professional cloud architecture map with official icons using the 'diagrams' library.
    Expects valid Python code using the 'diagrams' library."""
    payload = {"model": "infra-spark", "prompt": python_code}
    try:
        response = requests.post(LITELLM_PROXY_URL, json=payload, timeout=60)
        response.raise_for_status()
        path = save_base64_file(response.json()["data"][0]["b64_json"], "png")
        return f"✅ Infra Map saved to: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@mcp.tool()
def generate_slides(marp_markdown: str) -> str:
    """Generates a professional slide deck using Marp (PDF)."""
    payload = {"model": "slide-spark", "prompt": marp_markdown}
    try:
        response = requests.post(LITELLM_PROXY_URL, json=payload, timeout=120)
        response.raise_for_status()
        path = save_base64_file(response.json()["data"][0]["b64_json"], "pdf")
        return f"✅ Slides saved to: {path}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
