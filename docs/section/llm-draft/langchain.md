# LLM Orchestration with LangChain

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Understand the role of LangChain as an orchestration layer for Large Language Models (LLMs).
    - Implement dynamic prompt generation using `PromptTemplates`.
    - Create efficient workflows using the LangChain Expression Language (LCEL).
    - Manage conversational state and history using `Memory` components.
    - Implement Retrieval Augmented Generation (RAG) using Vector Stores and Embeddings.
    - Develop autonomous `Agents` that utilize external tools to complete complex tasks.

While Large Language Models (LLMs) like GPT-4 or Claude are incredibly powerful, using them in production requires more than just a simple API call. A raw LLM is stateless, limited by its training cutoff date, and cannot interact with the physical world or your private data without a surrounding framework.

LangChain is an open-source orchestration framework designed to bridge this gap. It allows developers to "chain" different components—such as prompts, models, memory, and external data sources—into a cohesive application. By providing a standardized interface, LangChain enables the creation of complex AI workflows, moving from simple chat bots to autonomous agents capable of reasoning and tool use.

## Core Building Blocks

The foundation of any LangChain application consists of three primary components: the Model, the Prompt, and the Output Parser.

### LLMs vs. ChatModels

LangChain distinguishes between two types of model interfaces:
1. **LLMs**: Pure text-in, text-out models.
2. **ChatModels**: Models that take a list of messages (System, Human, AI) as input and return a message as output.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Initialize a ChatModel
model = ChatOpenAI(model="gpt-4o")

messages = [
    SystemMessage(content="You are a helpful assistant that speaks like a pirate."),
    HumanMessage(content="Tell me about the cloud.")
]

response = model.invoke(messages)
print(response.content)
```

### Prompt Templates

Hard-coding prompts is fragile and unscalable. `PromptTemplates` allow you to define a blueprint with variables that are filled at runtime.

```python
from langchain_core.prompts import ChatPromptTemplate

template = ChatPromptTemplate.from_messages([
    ("system", "You are a technical expert in {topic}."),
    ("human", "Explain {concept} in three bullet points."),
])

# Formatting the prompt
prompt_value = template.invoke({"topic": "Kubernetes", "concept": "Pod Autoscaling"})
print(prompt_value)
```

### Output Parsers

LLMs return strings, but applications often require structured data (like JSON or a Python list). Output Parsers handle the transformation of the raw model output into a usable format.

```python
from langchain_core.output_parsers import StrOutputParser

parser = StrOutputParser()
# This parser simply extracts the string content from a ChatMessage
```

## LangChain Expression Language (LCEL)

The modern way to build chains in LangChain is through **LCEL**, which uses a declarative syntax centered around the pipe operator (`|`). This makes the flow of data explicit and easy to debug.

### Basic Chain Implementation

A typical chain follows the sequence: `Prompt` $\rightarrow$ `Model` $\rightarrow$ `Parser`.

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Define components
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
model = ChatOpenAI(model="gpt-4o")
parser = StrOutputParser()

# 2. Construct the chain using the pipe operator
chain = prompt | model | parser

# 3. Execute the chain
result = chain.invoke({"topic": "cloud computing"})
print(result)
```

## Conversational Memory

Because LLMs are stateless, they do not remember previous turns of a conversation. Memory components allow us to store and inject the conversation history back into the prompt.

### Using Buffer Memory

The simplest form of memory is the `ConversationBufferMemory`, which stores all messages in a raw list.

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain # Legacy for simplicity in this example

# Note: In LCEL, memory is typically handled by manually passing a list of messages
# or using a RunnableWithMessageHistory wrapper.
memory = ConversationBufferMemory()
memory.save_context({"input": "Hi, I'm Grey"}, {"output": "Hello Grey! How can I help you today?"})

# Retrieve history to inject into the next prompt
history = memory.load_memory_variables({})
print(history)
```

## Retrieval Augmented Generation (RAG)

RAG is the process of providing the LLM with specific, retrieved documents to ground its answer in factual, private, or up-to-date data.

### The RAG Pipeline

A professional RAG pipeline consists of five stages:
1. **Loading**: Importing documents (PDFs, Text, HTML).
2. **Splitting**: Breaking documents into smaller "chunks" to fit the LLM's context window.
3. **Embedding**: Converting text chunks into numerical vectors.
4. **Storing**: Saving vectors in a Vector Store (e.g., FAISS, ChromaDB).
5. **Retrieving**: Searching the store for the most relevant chunks based on the user's query.

### Implementing a Simple RAG Chain

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 1. Setup Embeddings and Vector Store
embeddings = OpenAIEmbeddings()
texts = [
    "Cloudmesh is an open-source framework for cloud management.",
    "The lecture series focuses on Python, Linux, and AI orchestration.",
    "LangChain is used to build LLM-powered applications."
]
vectorstore = FAISS.from_texts(texts, embeddings)
retriever = vectorstore.as_retriever()

# 2. Define the RAG Prompt
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI(model="gpt-4o")

# 3. Create the RAG Chain
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()} 
    | prompt 
    | model
)

# 4. Query the data
response = rag_chain.invoke("What is Cloudmesh?")
print(response.content)
```

## Agents and Tool Use

Agents are the most advanced use case in LangChain. Unlike a static chain, an agent uses the LLM as a "reasoning engine" to decide *which* tool to call and in *what* order to solve a problem.

### Defining Tools

A tool is essentially a Python function with a clear description that the LLM can understand.

```python
from langchain.agents import tool

@tool
def get_system_status(service_name: str) -> str:
    """Returns the current status of a cloud service."""
    # In a real scenario, this would call an API
    statuses = {"compute": "Online", "storage": "Degraded", "network": "Online"}
    return statuses.get(service_name, "Unknown service")

tools = [get_system_status]
```

### The Agent Loop (ReAct Pattern)

Agents typically follow the **ReAct** (Reason + Act) pattern:
- **Thought**: The LLM decides what to do.
- **Action**: The LLM calls a tool.
- **Observation**: The LLM sees the tool's output.
- **Repeat**: Until the final answer is reached.

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain import hub

# Initialize model and tools
model = ChatOpenAI(model="gpt-4o")
prompt = hub.pull("hwchase17/openai-functions-agent") # Standard prompt from LangChain Hub

# Create the agent
agent = create_openai_functions_agent(model, tools, prompt)

# Create the executor to run the agent
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent
agent_executor.invoke({"input": "What is the status of the storage service?"})
```

!!! tip "Summary Checklist"

    - [ ] Differentiated between `LLM` and `ChatModel` interfaces.
    - [ ] Implemented a `ChatPromptTemplate` with dynamic variables.
    - [ ] Constructed a pipeline using LCEL pipe (`|`) operators.
    - [ ] Integrated a `ConversationBufferMemory` to track dialogue history.
    - [ ] Built a RAG pipeline using a Vector Store and Embeddings.
    - [ ] Defined custom tools and integrated them into an `AgentExecutor`.

!!! note "Assignment 1: Dynamic Knowledge Bot"

    **Task**: Create a basic LCEL chain that takes a user's name and a technical topic, and returns a personalized explanation of that topic written in the style of a specific famous person.
    **Goal**: Practice using `PromptTemplates` and basic chain construction.

!!! note "Assignment 2: Local Document RAG"

    **Task**: Implement a RAG pipeline that:
    1. Loads a local `.txt` file containing a set of project guidelines.
    2. Splits the text into chunks of 500 characters.
    3. Uses a Vector Store to answer questions about the guidelines.
    **Goal**: Implement the full RAG lifecycle from loading to retrieval.

!!! note "Assignment 3: Autonomous Cloud Auditor"

    **Task**: Create an Agent with two tools:
    1. `get_resource_count(cloud_provider)`: Returns a dummy number of VMs.
    2. `calculate_cost(count)`: Multiplies the count by a fixed rate.
    The agent should be able to answer: "How much is it costing us to run our resources on AWS?"
    **Goal**: Build an agent that can sequence multiple tool calls to arrive at a final numerical answer.
