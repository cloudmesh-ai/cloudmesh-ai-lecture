# Claude Code: The Agentic CLI for Software Engineering

Claude Code is a revolutionary command-line interface (CLI) that brings the power of Claude's reasoning and coding capabilities directly into the developer's terminal. Unlike web-based LLM interfaces, Claude Code is an **agentic tool**: it doesn't just suggest code; it can execute commands, read your filesystem, run tests, and iterate on complex engineering tasks autonomously.

## Installation and Setup

Claude Code is distributed as an npm package and requires a modern Node.js environment.

### Prerequisites
- **Node.js**: Version 18 or higher is required.
- **Operating System**: Compatible with macOS, Linux, and Windows (via WSL2 recommended).
- **Anthropic API Key**: A valid API key with credits from the Anthropic Console.

### Installation Commands
To install Claude Code globally on your system, run:

```bash
npm install -g @anthropic-ai/claude-code
```

### First-Run Setup
Once installed, launch the tool by typing:

```bash
claude
```

On the first launch, you will be prompted to authenticate. The tool will guide you through a browser-based OAuth flow or ask for your API key to link your local environment to your Anthropic account.

---

## Purpose: Why a CLI Agent?

For years, developers have used LLMs by copying and pasting code between an IDE and a browser. This "context switching" is slow and error-prone. Claude Code solves this by residing where the code lives: the terminal.

### From Chatbot to Agent
While a chatbot answers questions, an **agent** takes actions. Claude Code can:
- **Explore**: Search through a massive codebase using `grep` and `find` to understand how a feature is implemented.
- **Execute**: Run build commands, execute test suites, and analyze the output to find bugs.
- **Iterate**: Write a fix, run the test, see it fail, and refine the code—all without user intervention for every step.
- **Manage**: Perform git operations, create commits, and manage project documentation.

---

## Core Features

### 1. Terminal and Filesystem Access
Claude Code is equipped with a set of powerful tools that allow it to interact with your local environment directly:
- **Bash Tool**: It can execute almost any shell command. This allows it to install dependencies (`npm install`), run build scripts (`make`), or check system logs.
- **Read/Write/Edit**: Unlike simple LLMs that rewrite whole files, Claude can perform **precision edits**. It identifies the exact line to change and applies a surgical update, which is faster and significantly reduces token usage.
- **Search & Navigation**: It uses `grep`, `find`, and directory listings to navigate your project structure without needing you to provide every file manually.

### 2. Comprehensive Command Reference
Claude Code uses "slash commands" to control the agent's behavior, session state, and environment.

| Command | Description | Example Use Case |
| :--- | :--- | :--- |
| `/config` | Opens the configuration menu. | Change the default model or adjust permission settings. |
| `/compact` | Prunes the conversation history. | Use this when the session gets long to save tokens and reduce latency. |
| `/help` | Displays the help menu. | Quickly find a command you forgot. |
| `/review` | Analyzes the current git diff. | "Check my changes for any potential edge-case bugs before I commit." |
| `/init` | Creates a `CLAUDE.md` file. | Establish project-specific rules (e.g., "Always use tabs for indentation"). |
| `/cost` | Displays current session expenditure. | Monitor how many credits you've spent on the current task. |
| `/clear` | Clears the current conversation. | Start a fresh task without previous context interfering. |
| `/exit` | Gracefully exits the CLI. | Close the session. |
| `/bug` | Reports a bug in Claude Code. | Let the Anthropic team know if a tool failed unexpectedly. |
| `/reset` | Resets the session state. | Completely wipe the agent's short-term memory for the current task. |

### 3. Specialized Agents
Claude Code can spawn **subagents** to handle complex, multi-step tasks in parallel or with a specialized focus. Instead of one general-purpose chat, you can delegate work to agents with specific "personas" or toolsets. These agents are defined by a configuration file (usually in `.claude/agents/`) that specifies their model and instructions.

**Concrete Example: The "Deep Refactor" Workflow**
Imagine you need to migrate your entire application from using `console.log` to a structured logging library like `Winston`. This is too large for a single prompt.

**The Delegation Process:**
1. **The Request**: You tell the main agent: *"I need to migrate all logging to Winston. Spawn a **Researcher agent** to map every single log call in the codebase, and then a **Refactor agent** to update them and verify the tests."*
2. **Agent 1 (Researcher)**: The main agent spawns a Researcher. This agent follows a specific definition (see `examples/researcher-agent.md`) that instructs it to use exhaustive search and mapping tools.
3. **Agent 2 (Refactor)**: Once the map is complete, the main agent spawns a Refactor agent. This agent iterates through the map, applying precision edits to each file and running `npm test` after every single change to ensure no regressions.
4. **The Result**: The main agent reports: *"Migration complete. 154 log calls updated across 22 files. All tests passed."*

This approach ensures that the "thinking" (mapping) and "doing" (editing/testing) are isolated, preventing the model from losing track of the goal in a massive conversation.

### 4. Skills and Workflows
**Skills** are packaged, reusable sets of instructions that encapsulate a specific professional workflow. They are like "macros" for AI engineering, often stored as Markdown files that define the exact steps the agent must take.

**Concrete Example: The `deployment-ready` Skill**
In a professional project, you might define a custom skill (or use a built-in one) to ensure code quality before a release.

**The Skill Definition:**
A skill like `security-review` (see `examples/security-review-skill.md`) doesn't just say "be secure"—it provides a rigorous checklist:
1. **Analyze the Diff**: Identify all modified lines.
2. **Threat Modeling**: Specifically check for OWASP Top 10 (Injection, Broken Access Control, etc.).
3. **Verification**: Construct concrete failure scenarios for every suspected flaw.

**How it's used in the CLI:**
Instead of typing four different prompts, the developer simply runs:
```bash
/deployment-ready
```
**The Outcome**: Claude returns a structured report:
- ✅ Linting: Passed.
- ❌ Tests: 2 failures in `user_service.test.ts`.
- ⚠️ Changelog: Not updated.
- ✅ Security: No critical vulnerabilities found.
*"I found 2 test failures. Would you like me to fix them and update the changelog now?"*


### 5. Model Context Protocol (MCP)
Claude Code supports the **Model Context Protocol (MCP)**, an open standard that allows the agent to connect to external tools and data sources seamlessly.

By configuring MCP servers, you can grant Claude access to:
- **Project Management**: "List all open Jira tickets assigned to me and summarize them."
- **Live Data**: "Query the production database to find why user #123 is seeing a 500 error."
- **Communication**: "Read the last 10 messages from the #dev-alerts Slack channel."

### 6. Hooks and Automation
The `settings.json` file allows you to define **Hooks**—automated triggers that execute commands based on agent actions.

**Concrete Example**:
You can configure a `post-edit` hook:
- **Trigger**: Every time Claude uses the `Edit` tool to change a file.
- **Action**: Run `npm run lint`.
- **Result**: If the linter fails, the output is fed back to Claude immediately, and the agent fixes the linting error before you even see the change.

### 7. Persistent Memory
Claude Code uses a local memory system (stored in `.claude/memory/`) to maintain long-term project context. It remembers:
- **Architectural Decisions**: "We decided to use PostgreSQL instead of MongoDB for the user store."
- **User Preferences**: "The user prefers functional style over object-oriented style in Python."
- **Project Nuances**: "The legacy `/api/v1` endpoints are read-only and should not be modified."

---

## Cost Management and Optimization

Claude Code operates on a **pay-as-you-go** model via the Anthropic API. Because agentic loops can involve many tool calls and large context windows, costs can accumulate quickly.

### How to Minimize Costs
Since there is no "free" tier for the professional API, cost optimization is critical:

#### 1. Model Selection
In `/config`, choose the model that matches the task complexity:
- **Sonnet**: Use for complex logic, architectural changes, and deep bug hunting.
- **Haiku**: Use for documentation, simple refactors, and basic questions. Haiku is significantly cheaper and faster.

#### 2. Aggressive Context Pruning
The "context window" is the total text the model processes per turn. As a session grows, you pay more for every single message.
- **Use `/compact` frequently**: This summarizes the history and removes verbose tool outputs (like long build logs), keeping your token count low.

#### 3. Precision Prompting
Vague prompts lead to "over-reading."
- **Bad**: *"Fix the bugs in the project."* (Agent may read every file in the repo).
- **Good**: *"Fix the type error in `src/utils/parser.ts` around line 150."* (Agent reads one file).

#### 4. The `.claudeignore` File
Prevent the agent from reading massive, irrelevant files (like `package-lock.json`, `.git` folders, or large `.log` files) by adding them to a `.claudeignore` file. This prevents accidental token spikes.

#### 5. Monitoring
Regularly run the `/cost` command to track your spend in real-time and set hard limits in the Anthropic Console to avoid unexpected bills.

---

## Case Study: Using Claude Code to Write a Book Chapter

To illustrate the power of the agentic loop, let's look at the real-world process used to create this very chapter. Writing high-quality technical documentation requires a cycle of research, drafting, and iterative refinement—a process where Claude Code excels.

### The Workflow

1. **Initial Blueprinting**: 
   The user defines the high-level requirements (e.g., "I want a chapter on Claude Code covering installation, features, and cost optimization"). The agent proposes a structure and gets sign-off.

2. **Automated Research**: 
   Instead of relying on static training data, the agent uses `WebSearch` and specialized `claude-code-guide` agents to find the most recent installation commands, updated pricing models, and new slash commands.

3. **First Draft (The "Skeleton")**: 
   Using the `Write` tool, the agent creates the initial `.md` file. This establishes the layout and fills in the basic technical facts.

4. **Iterative Expansion (The "Muscle")**: 
   The user provides feedback (e.g., "Make the command section more exhaustive" or "Add concrete examples"). The agent then:
   - Uses `Read` to analyze the existing text.
   - Uses `Edit` to surgically insert new tables, detailed command descriptions, and narrative examples.
   - Spawns subagents to verify technical accuracy.

5. **Supplementary Asset Creation**: 
   To move from "telling" to "showing," the agent creates standalone files in an `examples/` directory (like `security-review-skill.md`). This allows the reader to see the actual code/markdown that powers a skill.

### Key Takeaway for Authors
The value of Claude Code here is not just the "generation" of text, but the **tight feedback loop**. The author can request a change, and the agent can immediately implement it across multiple files, verify it against the project structure, and present the updated version for review—all without the author ever leaving the terminal.
