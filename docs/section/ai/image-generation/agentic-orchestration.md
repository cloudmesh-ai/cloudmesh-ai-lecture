# Agentic Orchestration: Primary Model & Specialist Tools on DGX Spark

This document describes the **Agentic Orchestration** architecture used to leverage the full power of the NVIDIA DGX Spark. Instead of using a single model for everything, we use a "Brain and Specialists" pattern.

## 1. The Orchestration Concept

In this architecture, we distinguish between the **Reasoning Model (The Brain)** and the **Execution Models (The Specialists)**.

### The Brain (Primary Model)
The primary model (e.g., **Gemma 4**, **Claude 3.5**, or **GPT-4**) is the interface you interact with. Its job is not to generate the final asset, but to:
1.  Understand the user's intent.
2.  Plan the necessary steps.
3.  Decide which **Specialist Tool** is required for each step.
4.  Review the output from the specialist and present it to the user.

### The Specialists (Tool Models)
Specialists are models optimized for a specific task. They are hosted on the **DGX Spark** and accessed via **liteLLM**.
*   **Flux:** Specialist for high-fidelity image generation.
*   **Mermaid/Marp:** Specialists for structural data (diagrams and slides).
*   **Specialized LLMs:** (Optional) Small, fine-tuned models for specific tasks like code review or security auditing.

---

## 2. The Technical Pipeline

The flow of a request follows this path:

**User** $\rightarrow$ **Primary Model (Brain)** $\rightarrow$ **MCP Tool (Connector)** $\rightarrow$ **liteLLM (Switchboard)** $\rightarrow$ **DGX Spark (Specialist)** $\rightarrow$ **Final Asset**

### Component Roles:
| Component | Role | Location | Responsibility |
| :--- | :--- | :--- | :--- |
| **Primary Model** | Orchestrator | Cloud/Local | Reasoning, Planning, Tool Selection |
| **MCP Server** | Translator | Laptop | Translates "Tool Calls" into API requests |
| **liteLLM** | Router | Laptop | Routes requests to the correct model endpoint |
| **DGX Spark** | Inference | Remote | Heavy lifting (Blackwell GPU computation) |

---

## 3. Configuration Guide

### Step A: The Switchboard (`liteLLM config.yaml`)
Define your specialists in the liteLLM configuration. This allows the brain to see them as distinct "models."

```yaml
model_list:
  # Specialist: Image Generation
  - model_name: flux-spark
    litellm_params:
      model: openai/flux-spark
      api_base: http://<dgx-spark-ip>:8000/v1/flux
      api_key: "not-needed"

  # Specialist: Diagram Generation
  - model_name: diagram-spark
    litellm_params:
      model: openai/diagram-spark
      api_base: http://<dgx-spark-ip>:8000/v1/diagram
      api_key: "not-needed"

  # Specialist: Slide Generation
  - model_name: slide-spark
    litellm_params:
      model: openai/slide-spark
      api_base: http://<dgx-spark-ip>:8000/v1/slides
      api_key: "not-needed"
```

### Step B: The Connector (`dgx_spark_mcp.py`)
The MCP server creates the tools that the Primary Model can "see." Each tool maps a natural language action to a specialist model in liteLLM.

```python
@mcp.tool()
def generate_image(prompt: str):
    # Maps to 'flux-spark' in liteLLM
    return call_litellm("flux-spark", prompt)

@mcp.tool()
def generate_diagram(mermaid_code: str):
    # Maps to 'diagram-spark' in liteLLM
    return call_litellm("diagram-spark", mermaid_code)
```

---

## 4. Practical Example: The Multimodal Workflow

When you give a complex prompt, the Primary Model orchestrates multiple specialists:

**User Prompt:** *"I need a technical overview of the GB10 Blackwell chip. Give me a summary, a diagram of the memory architecture, and a a set of slides for my students."*

**The Orchestration Process:**
1.  **Primary Model** generates the text summary.
2.  **Primary Model** calls `generate_diagram(mermaid_code)` $\rightarrow$ **liteLLM** $\rightarrow$ **DGX Spark** $\rightarrow$ `architecture.png`.
3.  **Primary Model** calls `generate_slides(marp_markdown)` $\rightarrow$ **liteLLM** $\rightarrow$ **DGX Spark** $\rightarrow$ `slides.pdf`.
4.  **Primary Model** summarizes the result: *"I've generated the summary, the architecture diagram, and the slide deck for you."*

---

## 5. Summary of Benefits
*   **Efficiency:** The Primary Model doesn't need to be "good" at drawing or formatting; it only needs to be good at **planning**.
*   **Hardware Optimization:** Each specialist can be optimized for the Blackwell architecture independently.
*   **Flexibility:** You can swap the "Brain" (e.g., switch from Gemma 4 to Claude 3.5) without changing any of your DGX Spark backend code.
