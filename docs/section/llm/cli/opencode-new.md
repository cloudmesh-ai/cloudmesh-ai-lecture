# Using `opencode` for lecture notes

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Install OpenCode on various platforms.
    - Configure LLM providers, including local models via Ollama and LiteLLM.
    - Initialize an OpenCode workspace and generate `AGENTS.md`.
    - Create and deploy specialized custom agents for technical formatting and lecture note generation.
    - Understand the difference between **Agents** and **Skills** in OpenCode.

Here is a step-by-step tutorial on how to install and use **OpenCode**, and how to build a specialized custom agent tailored for organizing, summarizing, and generating lecture notes.

---

## Install OpenCode

OpenCode is an open-source AI coding and workflow agent available as a terminal UI (TUI), desktop app, or IDE extension.

### General Install

Install it via Node.js, Homebrew, or your preferred package manager:

```bash
npm install -g opencode-ai
```

Verify the installation by launching the interface:

```bash
opencode
```

### Install on macOS

You can install OpenCode on your Mac as either a desktop application or a terminal interface (TUI) tool using a script or package manager.

#### Option 1: Install OpenCode Desktop App

1. Go to the official OpenCode download page.
2. Click download for macOS (Apple Silicon) or macOS (Intel) depending on your Mac processor.
3. Open the downloaded `.dmg` file.
4. Drag and drop the OpenCode icon into your Applications folder.
5. Open your Applications folder and launch OpenCode (approve the security prompt if macOS asks if you trust an app downloaded from the internet).

#### Option 2: Install OpenCode Terminal (TUI) via Script

1. Open the terminal app on your Mac.
2. Copy and paste the official install command and press Enter:

```bash
curl -fsSL https://opencode.ai/install | bash
```

3. Type `opencode` in your terminal to start the application.

#### Option 3: Install OpenCode Terminal via Homebrew

If you use Homebrew, you can install the recommended OpenCode tap:

```bash
brew install anomalyco/tap/opencode
```

### Step 2: Configure Your LLM Provider

OpenCode lets you plug in any model provider (Anthropic, OpenAI, local Ollama, etc.).

1. Inside the TUI, run the connection command:

```text
/connect
```

2. Choose your provider or use **OpenCode Zen** for curated models. Paste your API key when prompted.

## Integrating Your Own Models

OpenCode allows you to plug in local models (via Ollama or custom OpenAI-compatible endpoints like vLLM or LiteLLM proxy servers) so your lecture notes workflow runs completely offline and privately.

### Step 1: Configure Your Local Backend (Ollama)

Ensure your local serving framework is running and exposing an API endpoint. For example, if you are using Ollama, make sure it is running locally on its standard port (`http://localhost:11434`) and that you have pulled your preferred coding or reasoning model (such as `qwen2.5-coder` or `llama3`).

### Step 2: Update Your Configuration File

OpenCode looks for a configuration file located at `~/.config/opencode/opencode.json` (or `opencode.jsonc`). Add or update the `provider` block to define your local backend using the OpenAI-compatible adapter:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama (Local)",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "qwen2.5-coder:32b": {
          "name": "Qwen 2.5 Coder 32B"
        },
        "deepseek-r1": {
          "name": "DeepSeek R1 Local"
        }
      }
    }
  }
}
```

### Step 3: Set Your Custom Model as Default (Optional)

If you want your lecture notes agent to automatically use your custom model by default, specify the full provider-and-model ID inside your configuration file:

```json
{
  "model": "ollama/qwen2.5-coder:32b"
}
```

#### Custom Gemma4 service via LiteLLM

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "litellm-proxy": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "LiteLLM Proxy Hub",
      "options": {
        "baseURL": "http://localhost:4000/v1",
        "headers": {
          "Authorization": "Bearer your-actual-secret-key"
        }
      },
      "models": {
        "a100-2-gemma4-31b": {
          "name": "A100 Gemma 4 31B"
        },
        "jetstream-gpt-oss-120b": {
          "name": "Jetstream GPT-OSS 120B"
        },
        "jetstream-muse-glimmer": {
          "name": "Jetstream Muse Glimmer"
        },
        "jetstream-llama4": {
          "name": "Jetstream Llama 4 Scout"
        },
        "mac-gpt-oss:20b": {
          "name": "Mac GPT-OSS 20B"
        },
        "mac-qwen2": {
          "name": "Mac Qwen 2.5 32B"
        },
        "mac-qwen3-coder": {
          "name": "Mac Qwen 3 Coder"
        },
        "mac-ollama-gemma4-26b": {
          "name": "Mac Ollama Gemma 4 26B"
        },
        "mac-qwen2.5-32b": {
          "name": "Mac Qwen 2.5 32B"
        },
        "spark-deepseek-r1:32b": {
          "name": "Spark DeepSeek R1 32B"
        },
        "white-qwen3-coder:30b": {
          "name": "White Qwen 3 Coder 30B"
        }
      }
    }
  },
  "model": "litellm-proxy/a100-2-gemma4-31b"
}
```

### Step 4: Verify and Select Inside OpenCode

1. Launch or restart your terminal interface:

```bash
opencode
```

2. Open the model selection menu by typing:

```text
/models
```

3. Select your custom local model from the list. Your lecture notes agent will now process transcripts, structure outlines, and draft markdown study guides directly through your local hardware.

### Step 3: Initialize Your Lecture Notes Project

Navigate to your workspace directory where you want to store your course materials and notes:

```bash
cd /path/to/lecture-notes-project
opencode
```

Once inside, run the initialization command:

```text
/init
```

This command analyzes your repository structure and generates an `AGENTS.md` file at the root, which acts as a foundational instruction map for your workspace rules and formatting patterns.

---

### Step 4: Create a Custom Agent for Lecture Notes

OpenCode supports custom subagents and specialized instruction sets. To build a dedicated agent that parses raw transcripts, slides, or rough outlines and formats them into clean, structured lecture notes, follow these steps:

#### 1. Define the Agent File

Create a configuration block or markdown instruction file inside your project structure (or globally in your OpenCode configuration folder) under an agents definition directory, or declare it in your workspace rules.

Create a file named `.opencode/agents/lecture_notes_agent.md` (or add it directly to your project instructions):

```markdown
# Agent: Lecture Notes Assistant
Description: Specialized agent for transforming raw transcripts, audio dumps, or rough professor notes into structured, highly readable study materials.

## Core Responsibilities
- Clean up conversational filler, stutters, and tangents from raw transcripts.
- Structure content logically with clear headings (Markdown format), key definitions, core concepts, and summary takeaways.
- Generate review questions or flashcard-style prompts at the end of each section.
- Maintain a consistent academic and professional tone.

## Output Format
1. **Overview / Executive Summary**: 3–4 bullet points capturing the big picture.
2. **Key Concepts & Definitions**: Vocabulary terms clearly bolded with concise explanations.
3. **Detailed Lecture Breakdown**: Chronological or topical expansion using clean markdown hierarchies.
4. **Review & Self-Test Questions**: 3 open-ended comprehension questions.
```

#### 2. Invoke Your Workflow Using Plan and Build Modes

OpenCode utilizes distinct working states to safeguard your files:

- **Plan Mode (`Tab` key)**: Use this mode to direct your agent before it writes or modifies any files.
- *Example prompt:* `"Using the raw transcript in transcripts/lecture_01.txt, draft a comprehensive study guide structured according to the Lecture Notes Assistant layout."`

- **Reviewing the Plan**: The agent will return an implementation strategy. You can drag and drop raw files or reference materials right into the terminal interface to feed context directly to the model.
- **Build Mode (`Tab` key)**: Switch back to Build mode and give the final command:
- *Example prompt:* `"Looks great. Go ahead and write the output to notes/lecture_01_cleaned.md."`

### Next Steps

Would you like to focus on setting up a specific pipeline (like integrating automated transcript files via Python scripts), or configure a local model (via Ollama) to handle your lecture notes privately? Tell me where you want to start.

---

Here is a custom OpenCode agent configuration designed specifically to enforce your strict Markdown formatting rules and technical chapter writing standards.

You can save this file directly into your workspace under `.opencode/agents/markdown_formatter.md`.

---

## Understanding Agents vs. Skills

In OpenCode, it is important to distinguish between **Agents** and **Skills**, as they serve different purposes in the AI workflow.

### What is an Agent?
An **Agent** is a specialized configuration of instructions, personas, and rules. It tells the LLM *how* to behave, *what* tone to use, and *which* standards to follow.
- **Example**: The `markdown_formatter` agent defines strict rules for headings, spacing, and prohibited words to ensure documentation is professional and consistent.
- **Configuration**: Defined in `.opencode/agents/*.md`.

### What is a Skill?
A **Skill** is a discrete capability or tool that the system can execute. If an agent is the "mind," a skill is a "tool" in its belt. Skills allow the AI to interact with the outside world or perform specific programmatic tasks.
- **Example**: A skill might be "Read File," "Execute Shell Command," or "Search GitHub Issues."
- **Configuration**: Registered via the OpenCode plugin system (often defined in TypeScript/JavaScript).

### Key Difference Summary

| Feature | Agent | Skill |
| :--- | :--- | :--- |
| **Nature** | Instructions & Persona | Tools & Functionality |
| **Purpose** | Guides behavior and output quality | Enables specific actions and data retrieval |
| **Definition** | Markdown files (`.md`) | Code/Plugins (TypeScript/JS) |
| **Analogy** | The "Architect" (plans and directs) | The "Power Tool" (does the actual work) |

---


### Custom Agent Definition: `markdown_formatter.md`

```markdown
# Agent: Markdown Formatting and Technical Chapter Specialist
Description: Specialized agent for generating and auditing technical documentation, ensuring strict adherence to formatting standards, structural sequences, and a neutral, direct technical tone.

## Core Responsibilities
- Transform raw technical topics into structured book chapters following a strict sequence (Title, Learning Objectives, Overview, Core Sections with Subsections, Summary Checklist, Practical Exercises, References).
- Enforce rigorous spacing rules around headings, lists, and code blocks.
- Strip all "AI fluff," marketing adjectives, and prohibited buzzwords from the text.
- Standardize mkdocs-material admonitions and ASCII-only punctuation.

## Strict Formatting Rules

### 1. Headings
- Always include exactly one empty line after every heading (`#`, and `##`, `###`).
- Do not use emojis in headings.
- Remove "TL;DR:" if it appears in a heading.
- Never use "Mastering" in titles.

### 2. Numbers & Lists
- Use regular ASCII numbers (e.g., 1, 2, 3) instead of emoji icons.
- Always include exactly one empty line before every list (bulleted or numbered).

### 3. Code Blocks
- Always add an empty line before the starting ``` fence.
- Never leave an empty line immediately before the closing ``` fence.
- Always use appropriate language identifiers (` ```python `, ` ```bash `, ` ```yaml `, etc.).

### 4. Admonitions (mkdocs-material style)
- `!!! info "Title"`: Used for objectives, tips, and general high-level information.
- `!!! note "Title"`: Used for exercises, important reminders, or key takeaways.
- `!!! warning "Title"`: Used for common pitfalls, cautions, or critical warnings.

### 5. Punctuation & Quotes
- Use only straight ASCII quotes (`"` and `'`). Never use smart quotes (`"`, `"`, `'`, `'`).

## Tone and Language Restrictions
- Keep the tone neutral, technical, and direct.
- Avoid promotional language, exaggerated adjectives, and generic filler.
- **Prohibited terms**: "best tool", "best approach", "cutting-edge", "revolutionary", "state-of-the-art", "game-changer", "comprehensive guide", "professional tool", "superior", "powerful", "gold standard", "industry leading".
```

---

### How to Use Your New Agent in OpenCode

1. **Place the File**: Save the block above as `.opencode/agents/markdown_formatter.md` in your project's root directory.
2. **Invoke via Plan Mode**: Press `Tab` in your OpenCode terminal interface to enter Plan Mode, and reference your agent:

```text
Using the markdown_formatter agent, draft a technical chapter on "Configuring Slurm Batch Jobs" following the strict chapter structure and formatting standards.
```

3. **Review and Build**: Inspect the output layout (checking spacing around code blocks and admonitions), then switch to Build mode to write it to your documentation folder.

---

## Assignments

!!! note "Assignment 1: Install and test an agent"
    1. **Installation**: Install OpenCode using the method best suited for your OS.
    2. **Configuration**: Connect a model provider and successfully run the `/models` command.
    3. **Agent Creation**: Create the `markdown_formatter.md` agent in your project directory.
    4. **Validation**: Use the `markdown_formatter` agent to format a raw text file into a structured technical chapter.

---

## Self-Assessment
Test your knowledge by expanding the questions below.
??? question "Can you explain the difference between Plan Mode and Build Mode in OpenCode?"
    Plan Mode (`Tab`) is used to define the strategy and intent before any file changes occur. Build Mode (`Tab`) is where the agent actually executes the plan and writes to the filesystem.

??? question "What is the purpose of the `.opencode/agents/` directory?"
    This directory stores specialized instruction sets (custom agents) that allow OpenCode to perform specific tasks (like technical formatting) with consistent rules and personas.

??? question "How do you configure a local model provider like Ollama in `opencode.json`?"
    You add a `provider` block to `opencode.json` using the `@ai-sdk/openai-compatible` npm package and specify the `baseURL` (e.g., `http://localhost:11434/v1` for Ollama).

??? question "Why is it important to define strict formatting rules for technical documentation agents?"
    They ensure a professional, neutral, and consistent output across a large documentation set, removing AI-generated fluff and ensuring compatibility with specific tools like mkdocs-material.

??? question "Which admonition style should be used for learning objectives according to the `markdown_formatter` agent?"
    The `!!! info "Title"` style should be used for objectives, tips, and general high-level information.

??? question "What are some of the prohibited terms when using the `markdown_formatter` agent to ensure a neutral technical tone?"
    Terms like "best tool", "cutting-edge", "revolutionary", "state-of-the-art", and "game-changer" are prohibited to maintain a direct, neutral technical tone.

