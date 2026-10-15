# Raw Notes: Multi-Agent Systems (MAS)

## Why Multi-Agent?

### Specialization: Divide and Conquer
**Concept**: Instead of one "god-model" trying to handle everything, we split the task into roles.
- **Analogy**: A software development team. You don't have one person who does requirements, architecture, coding, testing, and DevOps simultaneously. You have a Product Manager, an Architect, a Developer, and a QA Engineer.
- **Technical Benefit**:
    - **Prompt Specialization**: Each agent has a focused system prompt (Persona). A "Reviewer" agent is prompted to be critical and pedantic, while a "Coder" agent is prompted to be creative and functional.
    - **Context Window Management**: Agents only receive the information relevant to their specific role, reducing noise and "lost in the middle" effects.
    - **Modularity**: You can swap out a "Coder" agent (e.g., using GPT-4o) with a more specialized model (e.g., DeepSeek Coder) without affecting the "Manager" agent.

**Why this matters**: Complex tasks often require conflicting mindsets (e.g., creation vs. critique). Forcing one LLM to do both in a single turn often leads to compromise or oversight.

### Reducing Hallucinations
**Concept**: Using multiple agents to verify and challenge each other.

- **Adversarial Agents (The Debate Pattern)**:
    - Agent A proposes a solution.
    - Agent B (the Adversary) is tasked specifically with finding flaws, edge cases, or inaccuracies in Agent A's proposal.
    - Agent A revises the proposal based on the critique.
    - This iterative loop pushes the output toward a more grounded truth.

- **Consensus Mechanisms**:
    - **Majority Voting**: Three independent agents generate an answer to a factual question. The system selects the most common answer.
    - **Judge/Critic Pattern**: Multiple "Worker" agents provide drafts; a high-reasoning "Judge" agent evaluates them against a set of criteria and selects/merges the best parts.

**Why this matters**: LLMs are probabilistic. By introducing "checks and balances," we move from "hope it's right" to "verified by multiple perspectives."

---

## Orchestration Patterns

### 1. Hierarchical Orchestration
**Structure**: Manager -> Workers.
- **Mechanism**: A "Manager" agent acts as the orchestrator. It receives the high-level goal, decomposes it into a set of sub-tasks, assigns these tasks to specialized worker agents, and reviews their outputs.
- **Real-world Scenario**: An AI Agency.
    - **Manager**: Project Lead.
    - **Worker 1**: Market Researcher.
    - **Worker 2**: Copywriter.
    - **Worker 3**: Graphic Designer.
- **Pros**: Clear control, easy to debug, structured output.
- **Cons**: Manager becomes a bottleneck; if the manager fails to decompose the task correctly, the workers will fail.

### 2. Sequential Orchestration (The Pipeline)
**Structure**: Agent A -> Agent B -> Agent C.
- **Mechanism**: A linear chain where the output of one agent is the input to the next.
- **Real-world Scenario**: Content Pipeline.
    - **Researcher**: Finds 5 key facts about a topic.
    - **Writer**: Turns those facts into a blog post.
    - **Editor**: Checks for grammar and tone.
- **Pros**: Simple to implement, predictable flow.
- **Cons**: No feedback loop (unless explicitly added); errors in early stages propagate to the end.

### 3. Joint Collaboration (Shared Workspace/Blackboard)
**Structure**: Agents <-> Shared State.
- **Mechanism**: All agents have access to a shared "Blackboard" or state object. Agents observe the state and "volunteer" to act when they see a task they are suited for, or are called by a coordinator based on the current state.
- **Real-world Scenario**: Collaborative Coding.
    - All agents see the current codebase and the issue ticket.
    - The "Architect" updates the plan on the blackboard.
    - The "Coder" sees the updated plan and writes the code.
    - The "Tester" sees the code and writes a test.
- **Pros**: High flexibility, supports complex non-linear workflows.
- **Cons**: Higher complexity in state management; risk of "infinite loops" if agents keep correcting each other.

---

## Frameworks Overview

### CrewAI
- **Philosophy**: Role-based, process-driven.
- **Key Concepts**:
    - `Agent`: Defined by role, goal, and backstory.
    - `Task`: A specific assignment with a description and expected output.
    - `Crew`: A collection of agents and tasks with a defined `Process` (Sequential or Hierarchical).
- **Best for**: Business process automation, structured workflows.

### AutoGen (by Microsoft)
- **Philosophy**: Conversation-centric.
- **Key Concepts**:
    - `ConversableAgent`: Agents that can send and receive messages.
    - `GroupChatManager`: Orchestrates conversations between multiple agents.
    - `UserProxyAgent`: Allows a human to stay in the loop.
- **Best for**: Open-ended problem solving, autonomous research, scenarios requiring heavy interaction between agents.

### LangGraph (by LangChain)
- **Philosophy**: Graph-based state machines.
- **Key Concepts**:
    - `Nodes`: Python functions (often LLM calls) that modify the state.
    - `Edges`: Define the path from one node to another (including conditional edges).
    - `State`: A shared object passed between nodes.
- **Best for**: Production-grade agents, complex cycles (loops), precise control over the agentic flow.

---

## Code Examples

### CrewAI: Simple Sequential Crew
```python
from crewai import Agent, Task, Crew, Process

# Define Agents
researcher = Agent(
  role='Senior Research Analyst',
  goal='Uncover cutting-edge developments in AI Agents',
  backstory='You are an expert at identifying emerging trends in AI.',
  verbose=True
)

writer = Agent(
  role='Tech Content Strategist',
  goal='Craft compelling articles on AI Agents',
  backstory='You transform complex tech research into easy-to-read guides.',
  verbose=True
)

# Define Tasks
task1 = Task(description='Analyze the latest trends in Multi-Agent Systems for 2025.', agent=researcher, expected_output='A bulleted list of 5 key trends.')
task2 = Task(description='Write a blog post based on the research trends.', agent=writer, expected_output='A 500-word blog post.')

# Instantiate Crew
crew = Crew(
  agents=[researcher, writer],
  tasks=[task1, task2],
  process=Process.sequential
)

result = crew.kickoff()
print(result)
```

### AutoGen: Basic Conversation
```python
import autogen

config_list = [{"model": "gpt-4", "api_key": "YOUR_API_KEY"}]

# Create agents
assistant = autogen.AssistantAgent(
    name="Assistant",
    llm_config={"config_list": config_list}
)

user_proxy = autogen.UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=2,
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Write a python script to fetch the current price of Bitcoin and print it."
)
```

### LangGraph: Simple Cycle (Self-Correction)
```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    content: str
    critique: str
    iterations: int

def generator(state: AgentState):
    print("---GENERATING---")
    return {"content": "The capital of France is Lyon.", "iterations": state["iterations"] + 1}

def critic(state: AgentState):
    print("---CRITIQUING---")
    if "Paris" in state["content"]:
        return {"critique": "Correct"}
    return {"critique": "Wrong, the capital is Paris."}

def should_continue(state: AgentState):
    if state["critique"] == "Correct" or state["iterations"] >= 3:
        return END
    return "generator"

workflow = StateGraph(AgentState)
workflow.add_node("generator", generator)
workflow.add_node("critic", critic)

workflow.set_entry_point("generator")
workflow.add_edge("generator", "critic")
workflow.add_conditional_edges("critic", should_continue)

app = workflow.compile()
app.invoke({"content": "", "critique": "", "iterations": 0})
```

---

## Suggested Diagrams

- **Figure 1: Hierarchical vs Sequential vs Joint Orchestration**.
  (Diagram showing a Manager node branching to workers, a linear chain of nodes, and a central hub with agents orbiting it).
  Footnote: [1] https://blog.langchain.dev/langgraph/

- **Figure 2: The Adversarial Debate Loop**.
  (Diagram showing Agent A -> Proposal -> Agent B -> Critique -> Agent A -> Revised Proposal).
  Footnote: [2] https://microsoft.github.io/autogen/
