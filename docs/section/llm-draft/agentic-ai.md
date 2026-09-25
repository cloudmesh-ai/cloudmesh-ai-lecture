# Agentic AI: Autonomous Systems and Tool Integration

!!! info "Learning Objectives"
    - Differentiate between standard LLM chat interfaces and Agentic AI systems.
    - Implement the Reason-Act (ReAct) loop for autonomous problem solving.
    - Develop tool-use capabilities using function calling and API integration.
    - Design memory systems for agents to maintain state across complex tasks.
    - Architect multi-agent systems where specialized agents collaborate to achieve a goal.
    - Evaluate agentic reliability, loop termination, and safety guardrails.

The evolution of Large Language Models (LLMs) has moved from "Passive Generation" to "Agentic Action." A standard LLM is a predictor of the next token; it receives an input and generates a response. In contrast, Agentic AI is a system that uses the LLM as a reasoning engine to drive a loop of planning, tool execution, and self-correction.

An AI Agent is not just a model, but a system. It combines the LLM with external components—tools, memory, and a control loop—to interact with the real world, execute code, and manipulate cloud infrastructure without constant human intervention for every step.

## The Agentic Core: The Reasoning Loop

At the heart of any agent is a control loop. While a chatbot follows a linear path (Prompt $\rightarrow$ Response), an agent follows a cyclical path: **Perceive $\rightarrow$ Plan $\rightarrow$ Act $\rightarrow$ Observe**.

### The ReAct Pattern (Reason + Act)

One of the most effective patterns for agentic behavior is ReAct. Instead of just generating an answer, the agent is prompted to generate a "Thought," followed by an "Action," and then wait for an "Observation" from the environment.

**The ReAct Cycle:**
1.  **Thought**: The agent analyzes the current state and decides what to do.
2.  **Action**: The agent selects a tool to call and provides the necessary arguments.
3.  **Observation**: The system executes the tool and feeds the result back to the agent.
4.  **Repeat**: The agent uses the observation to update its thought process and repeat until the goal is achieved.

Example: A simplified ReAct loop implementation.

```python
import json

# Mock tools for the agent
def get_server_status(server_id):
    # In real life, this would be a CloudMesh API call
    status_map = {"srv-01": "Running", "srv-02": "Stopped", "srv-03": "Error"}
    return status_map.get(server_id, "Unknown")

def restart_server(server_id):
    return f"Server {server_id} has been restarted successfully."

tools = {
    "get_server_status": get_server_status,
    "restart_server": restart_server
}

def agent_loop(user_goal):
    context = f"Goal: {user_goal}\n"
    
    for i in range(5):  # Limit iterations to prevent infinite loops
        # 1. Reason & Act (Simulating LLM output)
        # In reality, this prompt goes to GPT-4/Claude
        if "srv-02" in context and "Stopped" not in context:
            thought = "I need to check the status of srv-02."
            action = "get_server_status(\"srv-02\")"
        elif "Stopped" in context:
            thought = "The server is stopped. I should restart it."
            action = "restart_server(\"srv-02\")"
        else:
            thought = "Task complete."
            action = "FINAL_ANSWER"

        print(f"Iteration {i+1}\nThought: {thought}\nAction: {action}")
        
        if action == "FINAL_ANSWER":
            return "Goal achieved."

        # 2. Observation (Executing the tool)
        tool_name = action.split("(")[0]
        arg = action.split('"')[1]
        observation = tools[tool_name](arg)
        
        print(f"Observation: {observation}\n")
        context += f"\nThought: {thought}\nAction: {action}\nObservation: {observation}"

# Execution
agent_loop("Ensure srv-02 is running")
```

## Tool Use and Function Calling

Tool use is what gives an agent "hands." Most modern LLMs support **Function Calling**, where the model does not execute the code itself but returns a structured JSON object indicating which function to call and with what arguments.

### Designing Tool Specifications

For an agent to use a tool reliably, the tool must have a clear, descriptive schema. This is the "documentation" the LLM reads to decide if the tool is appropriate.

Example: A professional tool definition for an LLM.

```json
{
    "name": "update_cloud_firewall",
    "description": "Updates the firewall rules for a specific VPC to allow or block traffic.",
    "parameters": {
        "type": "object",
        "properties": {
            "vpc_id": {
                "type": "string",
                "description": "The unique identifier of the VPC (e.g., 'vpc-12345')."
            },
            "port": {
                "type": "integer",
                "description": "The TCP/UDP port to modify."
            },
            "action": {
                "type": "string",
                "enum": ["ALLOW", "BLOCK"],
                "description": "Whether to allow or block the traffic."
            }
        },
        "required": ["vpc_id", "port", "action"]
    }
}
```

## Agent Memory Systems

An agent without memory is stateless; it forgets the "Observation" as soon as the next prompt is sent. Professional agents implement two types of memory.

### Short-Term Memory (Context Window)
This is the immediate history of the current session (the conversation log). It is limited by the LLM's maximum token window. When the history becomes too long, agents use **Summarization Memory** to condense previous steps while keeping key facts.

### Long-Term Memory (RAG and Vector DBs)
For tasks requiring knowledge across days or months, agents use **Retrieval-Augmented Generation (RAG)**. They store previous experiences or documentation in a vector database (like ChromaDB or Pinecone) and query it when the current "Thought" indicates a need for historical data.

## Multi-Agent Systems (MAS)

Complex goals are often too large for a single agent. Multi-agent systems distribute tasks across specialized agents that collaborate.

### Agent Roles and Hierarchies

- **The Manager Agent**: Decomposes the high-level goal into a task list and assigns them to workers.
- **The Worker Agent**: A specialist (e.g., a "Security Agent" or a "Network Agent") that executes specific tools.
- **The Critic Agent**: Reviews the worker's output for errors or security vulnerabilities before the final answer is delivered.

Example Workflow:
1.  **User**: "Deploy a secure web server on AWS."
2.  **Manager**: 
    - Task 1: Provision EC2 $\rightarrow$ assigned to **Infrastructure Agent**.
    - Task 2: Configure Security Groups $\rightarrow$ assigned to **Security Agent**.
    - Task 3: Install Nginx $\rightarrow$ assigned to **DevOps Agent**.
3.  **Critic**: Verifies that the Security Agent didn't leave port 22 open to the world.

## Reliability and Guardrails

Agentic AI introduces "Non-Deterministic Execution." Because the agent decides the path, it can enter infinite loops or execute destructive commands.

### Key Guardrails

- **Human-in-the-Loop (HITL)**: Requiring a human to click "Approve" before the agent executes a "Write" operation (e.g., deleting a server).
- **Token Budgets / Step Limits**: Forcing the agent to terminate if it exceeds 10 iterations without reaching a final answer.
- **Output Validation**: Using Pydantic or JSON Schema to ensure the LLM's requested tool arguments are typed correctly before execution.

!!! tip "Summary Checklist"
    - Implemented a Reason-Act (ReAct) loop for autonomous decision making.
    - Defined tools using clear, descriptive JSON schemas for Function Calling.
    - Integrated short-term (context) and long-term (vector) memory.
    - Architected a multi-agent hierarchy with Manager, Worker, and Critic roles.
    - Implemented Human-in-the-Loop (HITL) for destructive actions.
    - Set strict iteration limits to prevent infinite loops.

!!! note "Assignment 1: Basic Tool-Use Agent"
    Implement a Python agent that can perform basic math (add, multiply) using tools. The agent should be able to solve a word problem like \"If I have 5 apples and buy 3 more, then double them, how many do I have?\" using a ReAct loop.

!!! note "Assignment 2: Cloud Resource Auditor"
    Design an agent that takes a list of server IDs, checks their status using a mock API, and generates a summary report. If any server is in an \"Error\" state, the agent must automatically call a `get_logs` tool for that server and include the logs in the report.

!!! note "Assignment 3: Multi-Agent Coding Team"
    Architect a system with two agents: a **Coder** and a **Reviewer**.
    1. The Coder writes a Python function based on a user requirement.
    2. The Reviewer tests the code and provides feedback.
    3. The Coder must iterate on the code based on feedback until the Reviewer gives a \"LGTM\" (Looks Good To Me) signal.
    4. Implement a mechanism to prevent the agents from looping more than 3 times.
