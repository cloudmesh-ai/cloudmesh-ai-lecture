# Raw Notes: Memory and State Management in Agentic AI

## Short-Term Memory

### Why This Matters
LLMs are stateless by nature. They don't "remember" previous prompts unless the history is passed back in the current request. However, the "context window" (the maximum number of tokens the model can process) is finite. If a conversation becomes too long, the oldest information is pushed out or the model fails.

### 1. Context Window Management
The context window is the "working memory" of the LLM.

#### Sliding Windows
The simplest approach: keep only the most recent $N$ messages or tokens.
- **Mechanism**: As new messages arrive, the oldest ones are dropped.
- **Trade-off**: Fast and easy, but the agent completely loses early context (e.g., the user's name or the original goal of the session).

#### Summary-based Memory
Instead of dropping old messages, the agent periodically summarizes the conversation.
- **Mechanism**: 
    1. Conversation reaches a threshold.
    2. A separate LLM call summarizes the history: "The user is asking about X, we have already discussed Y and Z."
    3. This summary is prepended to the current context window.
- **Trade-off**: Preserves high-level context but loses granular details.

### Real-World Scenario: Customer Support Bot
A bot helping a user troubleshoot a router. 
- **Sliding Window**: Might forget the router model the user mentioned at the start.
- **Summary-based**: Keeps a summary: "User has a Netgear Nighthawk and is experiencing intermittent Wi-Fi drops." This persists even as the specific troubleshooting steps fill the context window.

### Code Snippet: Simple Sliding Window (Python)
```python
class SlidingWindowMemory:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.window_size:
            self.history.pop(0)

    def get_context(self):
        return self.history

# Usage
memory = SlidingWindowMemory(window_size=3)
memory.add_message("user", "Hi, I'm Alice.")
memory.add_message("assistant", "Hello Alice!")
memory.add_message("user", "I need help with my order.")
memory.add_message("assistant", "I can help. What is the order ID?")
memory.add_message("user", "It is 12345.")

# Only the last 3 messages are kept:
# [{"role": "user", "content": "I need help with my order."}, 
#  {"role": "assistant", "content": "I can help. What is the order ID?"}, 
#  {"role": "user", "content": "It is 12345."}]
print(memory.get_context())
```

---

## Long-Term Memory

### Why This Matters
Short-term memory is session-bound. For a truly agentic experience, an AI must remember a user's preferences, a project's history, or a set of learned facts across days, weeks, or months.

### 1. Vector Databases & RAG
Retrieval Augmented Generation (RAG) turns a database into an external memory bank.
- **Mechanism**:
    1. **Embedding**: Convert text (documents, past chats) into numerical vectors using an embedding model.
    2. **Storage**: Store these vectors in a Vector Database (e.g., Pinecone, Milvus, Weaviate, Chroma).
    3. **Retrieval**: When a query comes in, embed the query and find the "nearest neighbors" (most similar vectors) in the DB.
    4. **Augmentation**: Feed the retrieved text into the LLM prompt as context.

### 2. Persistent State
Persistent state is about saving the "internal variables" of an agent.
- **Mechanism**: Saving the agent's current state (e.g., a JSON object containing `current_step`, `collected_data`, `user_preferences`) to a relational database (PostgreSQL) or a Key-Value store (Redis).
- **Resumption**: When the user returns, the agent loads the state and resumes exactly where it left off.

### Real-World Scenario: Personalized AI Tutor
An AI tutor teaching Python.
- **Long-Term Memory (RAG)**: The tutor remembers that 3 weeks ago, the student struggled with "list comprehensions" by retrieving a summary of that past session.
- **Persistent State**: The tutor knows the student is currently on "Chapter 4: Functions" and has completed 3 of 5 exercises.

### Code Snippet: Simple RAG Concept (Conceptual Python)
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Mock Embedding Model
def get_embedding(text):
    # In reality, use OpenAI or Cohere embedding models
    return np.random.rand(1, 128)

# Memory Store
vector_db = {
    "User prefers dark mode": get_embedding("User prefers dark mode"),
    "User is a Senior Dev": get_embedding("User is a Senior Dev"),
}

def retrieve_memory(query):
    query_vec = get_embedding(query)
    best_match = None
    max_sim = -1
    
    for text, vec in vector_db.items():
        sim = cosine_similarity(query_vec, vec)[0][0]
        if sim > max_sim:
            max_sim = sim
            best_match = text
    return best_match

# Usage
query = "How should I format the UI?"
memory = retrieve_memory(query)
print(f"Retrieved Memory: {memory}") 
# Output: Retrieved Memory: User prefers dark mode (hypothetically)
```

---

## State Machines and Agent Flow

### Why This Matters
Naive agents often run in a simple `while True` loop: "Plan -> Act -> Observe". This is fragile for complex workflows. State machines allow developers to define strict transitions and logic, ensuring the agent follows a predictable path while still being flexible.

### 1. Graph-Based Flow (LangGraph Approach)
Instead of a linear chain, the agent is modeled as a Directed Acyclic Graph (DAG) or a cyclic graph.
- **Nodes**: Represent a specific step (e.g., "Search Web", "Write Draft", "Review Quality"). Each node is a function that takes the current state and returns an updated state.
- **Edges**: Define the transition from one node to another.
- **Conditional Edges**: Use an LLM to decide which node to go to next (e.g., "If the review failed, go back to Write Draft; otherwise, go to Publish").
- **State**: A shared object (schema) that persists across the entire graph execution.

### Real-World Scenario: Automated Research Agent
1. **State**: `{topic: "Quantum Computing", sources: [], draft: "", quality_score: 0}`
2. **Node 1 (Search)**: Finds 5 papers, adds them to `sources`.
3. **Node 2 (Write)**: Uses `sources` to write a `draft`.
4. **Node 3 (Review)**: Evaluates `draft`. If `quality_score < 8`, it triggers a conditional edge back to **Node 1** with a request for "more specific details on X".
5. **Node 4 (Finalize)**: Once score is $\ge 8$, it outputs the final text.

### Code Snippet: LangGraph-style State Concept
```python
from typing import TypedDict, List

# Define the state schema
class AgentState(TypedDict):
    messages: List[str]
    is_complete: bool
    iteration_count: int

def search_node(state: AgentState):
    print("Searching...")
    return {"messages": state["messages"] + ["Found info about AI memory."], "iteration_count": state["iteration_count"] + 1}

def review_node(state: AgentState):
    print("Reviewing...")
    # Simple logic: complete after 2 iterations
    complete = state["iteration_count"] >= 2
    return {"is_complete": complete}

# Simple Graph Controller
def run_graph(initial_state):
    state = initial_state
    while not state["is_complete"]:
        state = search_node(state)
        state = review_node(state)
    return state

# Usage
final_state = run_graph({"messages": [], "is_complete": False, "iteration_count": 0})
print(f"Final State: {final_state}")
```

---

## Visualizations (Conceptual)

- **Figure 1: Sliding Window vs Summary Memory**. A diagram showing a sequence of messages. The sliding window shows a hard cutoff of old messages. The summary memory shows old messages being compressed into a small "summary" block that stays at the top of the context.
  - [1] https://blog.langchain.dev/memory/ (Conceptual reference)

- **Figure 2: The RAG Loop**. A flowchart: Query -> Embedding Model -> Vector DB Search -> Context Augmentation -> LLM -> Response.
  - [2] https://aws.amazon.com/what-is/retrieval-augmented-generation/ (Conceptual reference)

- **Figure 3: Agentic Graph Flow**. A diagram with nodes (Search, Write, Review) and edges, including a loop from Review back to Search.
  - [3] https://langchain-ai.github.io/langgraph/ (Conceptual reference)
