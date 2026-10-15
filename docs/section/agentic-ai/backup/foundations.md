# Raw Notes: Foundations of Agentic AI

## What is an AI Agent?

An AI Agent is an autonomous system that uses a Large Language Model (LLM) as its central reasoning engine ("the brain") to achieve a goal by interacting with its environment. Unlike a standard LLM, which simply predicts the next token in a sequence, an agent uses the LLM to coordinate a loop of planning, memory, and tool use.

### The Agent Formula:
Agent = LLM + Planning + Memory + Tool Use

- **LLM (The Brain)**: Provides the reasoning, language understanding, and decision-making capabilities.
- **Planning**: The ability to break down a complex goal into smaller, manageable steps.
- **Memory**: The ability to store and retrieve information over time (short-term context and long-term knowledge).
- **Tool Use**: The ability to interact with the external world (e.g., searching the web, running code, calling APIs).

### Passive vs. Active AI: Chatbots vs. Agents
- **Passive AI (Chatbot)**: Operates in a request-response mode. The user provides a prompt, and the AI provides an answer. The boundary of the AI is the chat window.
- **Active AI (Agent)**: Operates in a loop. The user provides a goal, and the AI determines which steps to take, which tools to use, and how to verify its own progress until the goal is met.

**Why this matters**: This shift transforms AI from a "consultant" (giving advice) into an "operator" (executing tasks).

---

## The Agentic Loop

The core of agentic behavior is a continuous cycle:
**Perception $\rightarrow$ Reasoning $\rightarrow$ Action $\rightarrow$ Observation**

1. **Perception**: The agent receives an input (user goal) or observes the result of a previous action.
2. **Reasoning**: The agent analyzes the state, reflects on the goal, and decides what to do next.
3. **Action**: The agent executes a specific action (e.g., calling a tool, writing a file).
4. **Observation**: The agent perceives the outcome of that action (e.g., the API response) and feeds it back into the loop.

(Figure 1: The Agentic Loop Diagram)
[1] https://lilianweng.github.io/posts/2023-06-23-agent/

---

## Cognitive Architectures

### 1. ReAct (Reason + Act)
ReAct is the foundational pattern for modern agents. It combines "Reasoning Traces" (Thought) with "Action" steps.

**The Cycle**:
- **Thought**: "I need to find out the current price of NVIDIA stock to answer the user's question."
- **Action**: `get_stock_price("NVDA")`
- **Observation**: "NVDA is currently trading at $135.20."
- **Thought**: "I have the price. Now I can answer the user."
- **Final Answer**: "NVIDIA is currently trading at $135.20."

**Why this matters**: It prevents the LLM from "hallucinating" an answer by forcing it to ground its reasoning in external observations.

#### Code Example: Manual ReAct Implementation
```python
import json

def mock_tool_get_weather(city):
    # In a real agent, this would be an API call
    weather_data = {"New York": "Sunny, 22C", "London": "Rainy, 15C"}
    return weather_data.get(city, "Weather unknown")

def react_agent(user_goal):
    system_prompt = """
    You are a ReAct agent. Use the following format:
    Thought: [Your reasoning about what to do]
    Action: [Tool name]: [Input]
    Observation: [Result of the tool]
    ... (repeat Thought/Action/Observation as needed)
    Final Answer: [The final response to the user]

    Available Tools:
    - get_weather: Returns weather for a city. Format: get_weather: city_name
    """
    
    messages = [{"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_goal}]
    
    # Simple loop to simulate the ReAct cycle
    for i in range(5):
        # Call LLM (Mocked here for brevity, but in reality calls OpenAI/Anthropic)
        # For this example, we simulate the LLM's response for "What is the weather in London?"
        if i == 0:
            response = "Thought: I need to check the weather for London.\nAction: get_weather: London"
        elif i == 1:
            # Simulate the observation step
            observation = mock_tool_get_weather("London")
            response = f"Observation: {observation}\nThought: I now know the weather is rainy and 15C.\nFinal Answer: The weather in London is rainy and 15C."
        else:
            break
            
        print(response)
        if "Final Answer:" in response:
            break

react_agent("What is the weather in London?")
```

---

### 2. Plan-and-Execute
For complex goals, ReAct can "get lost" in the loop. Plan-and-Execute separates the high-level strategy from the low-level execution.

**The Process**:
1. **Planner**: Decomposes the goal into a list of sub-tasks (a "plan").
2. **Executor**: Executes the tasks one by one using a ReAct-style loop.
3. **Re-Planner**: After each step or set of steps, the agent updates the plan based on new observations.

**Scenario**: "Research the top 3 competitors of CloudMesh and write a summary report."
- **Plan**:
  1. Search for "CloudMesh competitors".
  2. For each competitor, find their core value proposition.
  3. Compare the three competitors.
  4. Synthesize a summary report.

**Why this matters**: This prevents the agent from circling in a loop and ensures it stays focused on a long-term goal.

---

### 3. Self-Reflection
Self-Reflection (or Reflexion) is the process of an agent critiquing its own output to improve it.

**The Loop**:
**Draft $\rightarrow$ Critique $\rightarrow$ Revise**

- **Draft**: The agent generates an initial solution.
- **Critique**: The agent (or a separate "critic" LLM) analyzes the solution for bugs, inaccuracies, or missing requirements.
- **Revise**: The agent uses the critique to generate a better version.

**Scenario**: Writing a complex Python function.
- **Draft**: Writes a function that works but has an O(n^2) complexity.
- **Critique**: "The current implementation is inefficient for large datasets. Consider using a hash map to reduce complexity to O(n)."
- **Revise**: Rewrites the function using a dictionary, achieving O(n) complexity.

#### Code Example: Simple Reflection Pattern
```python
def generate_code(prompt):
    return "def add(a, b): return a + b" # Mocked

def critique_code(code):
    return "The code is correct but lacks type hints." # Mocked

def refine_code(original, critique):
    return "def add(a: int, b: int) -> int: return a + b" # Mocked

# Reflection Loop
prompt = "Write a simple addition function."
draft = generate_code(prompt)
critique = critique_code(draft)
final = refine_code(draft, critique)

print(f"Original: {draft}")
print(f"Critique: {critique}")
print(f"Final: {final}")
```

**Why this matters**: Reflection significantly reduces errors in coding and complex reasoning tasks by mimicking the human "second-pass" review process.
