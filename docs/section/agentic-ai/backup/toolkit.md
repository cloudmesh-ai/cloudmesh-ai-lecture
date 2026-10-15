# The Agent's Toolkit: Tool Use & Function Calling

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to:
    - Explain the multi-turn request-response cycle of LLM tool use.
    - Design precise tool definitions using JSON Schema and strict mode.
    - Implement architectural patterns for API integration, code execution, and Text-to-SQL.
    - Build robust error-handling loops that treat tool failures as feedback for self-correction.
    - Implement safety guards, including turn limits and network-level retries.

## Overview

Tool use, often referred to as function calling, is the mechanism that transforms a Large Language Model (LLM) from a passive text generator into an active agent. While an LLM can reason about a problem, it cannot natively check a database, send an email, or calculate a precise square root of a 10-digit number.

Tool use provides a standardized interface for the LLM to request that an external application perform a specific action. The LLM does not execute the code itself; instead, it generates a structured request (usually JSON) that the application interprets and executes.

![alt text](images/agent-toolkit-chatgpt.png)


### Why this matters
Without tools, agents are limited by their training cutoff and are prone to hallucinations when asked for precise, real-time, or private data. Tool use provides:
- **Grounding**: Access to a "source of truth" through APIs and databases.
- **Agency**: The ability to effect change in the real world (e.g., updating a Jira ticket).
- **Deterministic Computation**: Offloading math, data analysis, and logic to a programming language like Python.

## The Mechanics of Tool Use

### Function Calling & the Agentic Loop

Tool use is not a single API call, but a multi-turn conversation between the LLM and the application harness.

The process follows a deterministic loop:

1. **Tool Definition**: The application sends a list of tool schemas (names, descriptions, and parameter types) to the LLM.
2. **Model Decision**: The LLM analyzes the user's intent. If a tool is required, it returns a `tool_use` block containing the tool name and the generated arguments.
3. **Client Execution**: The application parses the JSON arguments, calls the actual function, and captures the output.
4. **Result Feeding**: The application sends a new request back to the LLM containing the original history and the `tool_result`.
5. **Final Synthesis**: The LLM interprets the tool result and generates a final natural-language response.

![The Tool Use Loop](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)

Figure 1: The Client-Side Tool Execution Loop.

!!! note "The Role of the Harness"
    The "harness" is the code you write that manages the loop. It is responsible for security (validating tool arguments), execution (calling the API), and state management (appending results to the conversation history).

### Tool Definition & Schema Design

The "prompt" for a tool is its name and description. Because the LLM uses these to decide *which* tool to call and *how* to format the arguments, precision is critical.

#### JSON Schema and Strict Mode

Tools are defined using JSON Schema. To ensure the model does not hallucinate arguments or omit required fields, use **Strict Mode**.

When `strict: true` is enabled:
- All properties in the schema must be listed in the `required` array.
- `additionalProperties` must be set to `false`.

This forces the model to adhere exactly to the provided schema, reducing parsing errors in the application.

#### Best Practices for Tool Descriptions

To maximize tool-calling accuracy, follow these guidelines:

- **Explicit Naming**: Use action-oriented names. `get_user_account_balance` is superior to `balance`.
- **Detailed Guidance**: Describe the purpose of each parameter. Instead of "Location", use "The city and state, e.g., 'San Francisco, CA'".
- **Input Constraints**: Specify formats explicitly (e.g., "Date must be in ISO 8601 format").
- **Keep it Lean**: Avoid "tool sprawl". Providing 50+ tools can confuse the model. Group tools into specialized sub-agents or use a tool-discovery pattern.

```python
# Example of a high-precision tool definition using the Anthropic SDK
search_tool = {
    "name": "search_knowledge_base",
    "description": "Searches the internal technical wiki for answers regarding API limits and security policies.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "The search query. Use keywords for better results."
            },
            "category": {
                "type": "string", 
                "enum": ["api", "billing", "security"], 
                "description": "The specific documentation category to filter by."
            }
        },
        "required": ["query", "category"],
        "additionalProperties": False
    },
    "strict": True
}
```

## Integration Patterns

### API Orchestration

The most common integration pattern is using the agent as an orchestrator for REST or gRPC services.

**Scenario**: A "Customer Success Agent" that can check order status and issue refunds.
- **Tool 1**: `get_order_status(order_id)` -> Calls `GET /orders/{id}`.
- **Tool 2**: `issue_refund(order_id, amount)` -> Calls `POST /refunds`.

!!! warning "Security First"
    Never expose sensitive administrative APIs directly to an LLM. Use a middleware layer to enforce authentication, authorization, and rate limiting before the tool call reaches the backend service.

### The Code Execution Sandbox

A code interpreter gives the agent a secure environment to write and run code (typically Python) in real-time.

**Why this matters**: LLMs are notoriously poor at complex arithmetic, data visualization, and large-scale text manipulation. A sandbox allows the agent to solve these problems deterministically.

**The Sandbox Loop**:
1. **Generation**: The agent writes a Python script to solve the problem.
2. **Execution**: The script runs in a containerized environment.
3. **Observation**: The agent reads the `stdout` and `stderr`.
4. **Iteration**: If the code fails (e.g., a `KeyError`), the agent sees the traceback and rewrites the code.

```python
# Conceptual example of a code execution loop
import anthropic

client = anthropic.Anthropic()

# Define a tool that represents the Python sandbox
tools = [{
    "name": "execute_python",
    "description": "Runs Python code in a sandboxed environment. Use this for math and data analysis.",
    "input_schema": {
        "type": "object",
        "properties": {"code": {"type": "string", "description": "The Python code to execute."}},
        "required": ["code"],
        "additionalProperties": False
    },
    "strict": True
}]

# User asks for a complex calculation
messages = [{"role": "user", "content": "Calculate the compound interest on $10,000 at 5% over 10 years."}]

response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

# The model generates code like: 
# print(10000 * (1 + 0.05)**10)
```

![Code Interpreter Architecture](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)

Figure 2: The Code-Execution Sandbox Loop.

### Database Interaction via Text-to-SQL

Text-to-SQL allows agents to query structured data without requiring the user to know SQL.

**Implementation Pattern**:
1. **Schema Exposure**: The database schema (DDL) is provided in the system prompt.
2. **Query Generation**: The agent generates a read-only SQL query.
3. **Execution**: The application runs the query against a read-replica.
4. **Synthesis**: The agent transforms the resulting rows into a natural-language answer.

:::tip "Performance Optimization"
    Instead of passing the entire schema for 100+ tables, use a "Schema Discovery" tool. Let the agent first search for relevant table names, then request the DDL for only those specific tables.
:::

## Reliability & Error Handling

### The Feedback Loop: Error as Signal

The most critical mistake in tool implementation is treating a tool failure as an application crash. In agentic AI, **a tool error is a valuable signal to the model**.

If a tool fails, the application should return the error message as the `tool_result` with `is_error: true`.

**Comparison**:
- **Naive Approach**: The app throws a `500 Internal Server Error`. The agent crashes.
- **Agentic Approach**: The app returns `{"error": "Invalid Order ID. Must be 8 digits."}`. The agent sees this, realizes the mistake, and asks the user for the correct ID.

### Turn Limits & Infinite Loop Prevention

Agents can occasionally fall into "infinite loops," where they repeatedly call the same failing tool in an attempt to fix it.

**Implementation Guards**:
- **Max Turns**: Implement a hard limit on the number of tool calls per request (e.g., 10 turns).
- **Repeat Detection**: Track the history of tool calls. If the agent calls the same tool with the same arguments three times, force a stop and ask for human intervention.
- **Network Retries**: Differentiate between *tool errors* (returned to the LLM) and *network errors* (handled by exponential backoff in the harness).

```python
import anthropic
import json

client = anthropic.Anthropic()

def get_weather(location):
    if "fail" in location.lower():
        return {"error": "Location not found in database."}
    return {"temp": "22C", "condition": "Sunny"}

tools = [{
    "name": "get_weather",
    "description": "Get current weather",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
        "additionalProperties": False
    },
    "strict": True
}]

messages = [{"role": "user", "content": "What's the weather in FailCity?"}]
max_turns = 5

for turn in range(max_turns):
    response = client.messages.create(
        model="claude-opus-5-5",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    
    messages.append({"role": "assistant", "content": response.content})
    
    if response.stop_reason != "tool_use":
        break
        
    for block in response.content:
        if block.type == "tool_use":
            result = get_weather(block.input["location"])
            
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                    "is_error": "error" in result
                }]
            })

# Final response reflects the model's attempt to handle the error
print(messages[-1]["content"][0].text if isinstance(messages[-1]["content"], list) else messages[-1]["content"])
```

## Summary Checklist

- [ ] Tool definitions use clear, action-oriented names.
- [ ] `strict: true` is enabled with `additionalProperties: false` and all required fields defined.
- [ ] Tool descriptions provide explicit guidance on input formats (e.g., ISO 8601).
- [ ] Tool failures are returned to the LLM as `tool_result` with `is_error: true`.
- [ ] A `max_turns` limit is implemented to prevent infinite loops.
- [ ] Database tools use read-only users on read-replicas.
- [ ] API tools are wrapped in a security middleware layer.

## Assignments

!!! note "The Weather Agent"
    Implement a tool-using agent that can retrieve weather data for a city.
    - Define a `get_weather` tool with `strict: true`.
    - Implement a loop that handles `tool_use` and `tool_result`.
    - Test it with a city that exists and one that doesn't to verify error handling.

    ??? question "Solution"
        The solution should use a `while` loop that checks `response.stop_reason == "tool_use"`. The `get_weather` function should return a JSON string, and the `tool_result` block should be appended to the `messages` list before the next API call.
        
!!! note "The SQL Schema Designer"
    Design a tool definition for a `query_customer_data` tool.
    - The tool should take a `sql_query` string.
    - Include a description that warns the model to only use `SELECT` statements.
    - Ensure the schema is compliant with strict mode.

    ??? question "Solution"
        The tool definition should include `strict: true`, `additionalProperties: False`, and a detailed description in the `input_schema` for the `sql_query` property, explicitly stating that only read-only queries are permitted.

!!! note "The Infinite Loop Guard"
    Modify the provided `Robust Tool Loop` code to detect when a model is repeating the same tool call.
    - Maintain a set of `(tool_name, arguments)` pairs.
    - If a pair is repeated more than twice, break the loop and return a message: "The agent is stuck in a loop."

    ??? question "Solution"
        Inside the loop, create a `seen_calls = set()`. Before executing a tool, hash the `block.name` and `json.dumps(block.input, sort_keys=True)`. If the hash is already in the set, increment a counter; if the counter exceeds 2, break.

## References

- [Anthropic Tool Use Documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [OpenAI Function Calling Guide](https://developers.openai.com/api/docs/guides/function-calling)
- [Model Context Protocol (MCP) Specification](https://modelcontextprotocol.io/)

## Self-Evaluation

??? note "What is the difference between a client tool and a server tool?"
    Client tools are executed by the application harness (the developer's code), while server tools are executed on the LLM provider's infrastructure (e.g., Anthropic's web search).

??? note "Why is 'strict mode' important for tool arguments?"
    Strict mode guarantees that the LLM's generated JSON matches the schema exactly, preventing application-side parsing errors caused by missing required fields or hallucinated parameters.

??? note "How should a harness handle a tool that returns a 404 Not Found error?"
    The harness should return the error as a `tool_result` block with `is_error: true` and a descriptive message. This allows the LLM to recognize the failure and potentially try a different search term or inform the user.

??? note "What is the risk of providing an LLM with a Text-to-SQL tool?"
    The primary risk is SQL injection or accidental data modification. This is mitigated by using read-only database users and executing queries against a read-replica.

??? note "What is the purpose of a 'max turns' limit in an agentic loop?"
    A max turns limit prevents the agent from entering an infinite loop of tool calls, which would consume excessive tokens and cause high latency without reaching a final answer.
