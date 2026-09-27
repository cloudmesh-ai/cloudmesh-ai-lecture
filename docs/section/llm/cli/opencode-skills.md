# Exhaustive Tutorial: Advanced OpenCode Skills Architecture & Implementation

!!! info "Learning Objectives"
    After completing this tutorial, you will be able to:
    - Understand the core architecture of OpenCode skills, including discovery hierarchies, YAML frontmatter configuration, and dynamic context injection.
    - Implement a production-ready custom skill using the unified `SKILL.md` format that combines precise trigger descriptions with deterministic execution workflows.
    - Scale skill libraries efficiently across multi-repository environments using project-local and user-global directory structures.
    - Maintain modular and token-efficient agent workflows by offloading bulk documentation to on-demand reference files and helper scripts.

---

## 1. Core Architecture and Anatomy of an OpenCode Skill

An **OpenCode skill** is a modular package of reusable instructions, references, and scripts that gives AI agents specialized domain knowledge and workflow procedures. OpenCode implements the open Agent Skills standard natively, allowing agents to dynamically discover and load skills contextually.

Every skill resides in its own directory and centers around a mandatory `SKILL.md` file. A well-structured skill directory looks like this:

```text
git-release/
├── SKILL.md            # Required: YAML frontmatter + markdown instructions
├── agents/             # Optional: Sub-agents specific to this skill
├── references/         # Optional: Deep documentation loaded on demand
└── templates/          # Optional: Boilerplate files or code skeletons
```

### The `SKILL.md` Structure

The file opens with YAML frontmatter specifying metadata, followed by markdown instruction bodies:

```markdown
---
name: Git Release
description: Prepare the changelog, version bump, tag, and release notes. Use when asked to cut a release, bump versions, or draft release notes.
slash: true
metadata:
  opencode/autoinvoke: false
---

# Git Release Workflow
1. Analyze git log since the last tag.
2. Generate structured changelog entries.
3. Update version flags in configuration files.
```

* **`name`**: Human-readable name of the skill.
* **`description`**: **The most important field.** OpenCode pattern-matches against this description at every turn to decide when to trigger the skill. Vague descriptions cause poor model activation.
* **`slash: true`**: Exposes the skill as a direct command shortcut if desired.
* **`opencode/autoinvoke: false`**: Hides the skill from automatic model advertising (it remains registered and loadable explicitly by ID).

---

## 2. Discovery Precedence and Execution Mechanics

OpenCode scans multiple directories to discover markdown files and `SKILL.md` files.

### Discovery Locations & Hierarchy (Lowest to Highest Precedence)

1. Built-in system skills
2. `.claude/skills/` (global, then path ancestors toward current directory)
3. `.agents/skills/` (global, then path ancestors toward current directory)
4. `~/.config/opencode/skills/` (user global)
5. Project `.opencode/skills/` (from project root to current subdirectory)
6. Explicit configuration entries

If two sources define a skill with the identical ID, the source registered *later* (higher precedence) overrides the earlier one.

### How OpenCode Executes Skills

1. **Startup Indexing:** At initialization, OpenCode's native skill tool supplies the model with a lightweight manifest listing every installed skill's **ID, name, and description** (omitting the full markdown body to save context tokens).
2. **Contextual Activation:** During a coding loop, the model evaluates active tasks against available descriptions. When a match occurs, the model invokes the skill tool by its exact ID.
3. **Body Injection:** OpenCode injects the raw Markdown body (stripping out frontmatter) directly into the conversation context alongside the base directory path and supporting reference paths.

---

## 3. Comprehensive Implementation Blueprint

Below is a production-ready unified skill template illustrating how to combine dynamic routing with strict, executable steps.

```markdown
---
name: Documentation Link Validator
description: Use this skill when the user requests a check for broken links, link validation, or verification of site navigation.
slash: true
metadata:
  opencode/autoinvoke: true
  author: Engineering Productivity Team
---
```

# Skill: Documentation Link Validator

## Purpose
Ensure zero broken internal or external links across project documentation by executing containerized test suites and performing targeted remediation.

## Execution Workflow
1. Run the `make linkchecker` command to execute the Docker-based validation suite.
2. Parse the output logs specifically for `404 Not Found` or `DNS Resolution` errors.
3. For each broken link discovered, locate the source markdown file using grep:
   ```bash
   grep -rn "target_broken_url" docs/
    ```

4. Propose a precise URL correction or draft a removal patch for the affected line.
5. Verify the fix by re-running the specific test target:
```bash
make linkchecker-file FILE=path/to/modified.md

```



## Verification & Edge Cases

* If the Docker daemon is unreachable, abort and notify the user to start the Docker service.
* If an external link is flaky (rate-limited), log a warning rather than failing the build.


## 4. Best Practices for Authoring Effective Skills

* **Write Trigger-Specific Descriptions:** Avoid lazy descriptions like `"helps with web tasks"`. Instead, use explicit functional conditions: `"Use when the user asks to scrape a URL, search the web, crawl documentation, or extract structured data."`
* **Keep `SKILL.md` Lean:** Offload verbose edge-case explanations, API specs, and long schemas into separate files inside a `references/` subdirectory. The model can load them only when required.
* **Keep Scope Narrow:** Adhere to a *"One skill, one job"* philosophy. Multi-purpose skills create overlapping descriptions, causing erratic routing behavior.
* **Leverage Deterministic Scripts:** If a task requires rigid parsing, file sorting, or syntax validation, bundle an executable script in the skill folder rather than relying entirely on LLM generation.

---

## Assignments

!!! note "Practical Exercises"
    1. **Audit & Selection**: Identify a repetitive, multi-step engineering or documentation workflow in your current project (e.g., release management, environment bootstrapping, or compliance validation) that would benefit from modular automation.
    2. **Implementation**: Draft a complete skill package adhering to the unified `SKILL.md` template structure. Your draft must include:
       - YAML frontmatter with a trigger-specific `description` and `opencode/autoinvoke: true`.
       - A clear purpose statement.
       - A 5-step concrete execution workflow featuring explicit shell commands or tool calls.
       - An edge-case or error-handling subsection.
    3. **Deployment & Testing**: Place your custom skill inside your project's `.opencode/skills/<skill-name>/` directory. Initialize an OpenCode session, invoke the skill either automatically via a natural language prompt or manually, and verify that the agent adheres strictly to the defined workflow steps.

---

## Self-Evaluation

??? note "What is the primary architectural difference between an OpenCode skill and a static system prompt?"
    A system prompt is global, monolithic, and always present in the context window, whereas an OpenCode skill is modularly indexed by description and injected dynamically only when a task matches its trigger criteria, preserving token space.

??? note "Why is the `description` field in the YAML frontmatter critical for OpenCode execution?"
    The OpenCode orchestrator evaluates available skill descriptions against user prompts during initialization and runtime to decide when to trigger the skill. Vague descriptions lead to missed activations or false positives.

??? note "How do reference directories help maintain context efficiency in large skills?"
    By keeping the primary `SKILL.md` concise and offloading verbose documentation, schemas, or error tables into a `references/` subdirectory, the agent loads detailed context only on-demand when explicitly required.

??? note "What is the recommended approach for writing workflow instructions within a skill?"
    Instructions should consist of direct, deterministic, and executable steps (specifying exact commands, tools, and error-handling conditions) rather than vague behavioral goals.

## Appendix

**Yes, you can use the exact same skills across both Claude Code and OpenCode.**

Both platforms natively implement the open **Agent Skills** specification. This compatibility allows you to author a skill package once and drop it into either environment's directory structure without modifying its core content.

---

### 1. Shared Directory Locations

Because OpenCode natively scans Claude-compatible paths, you can store your skills in standard `.claude/skills/` directories, and both tools will discover them.

* **Project Scope (Shared via Git):**
```text
your-project/
├── .claude/skills/<skill-name>/SKILL.md    # Discovered by both Claude & OpenCode
└── .opencode/skills/<skill-name>/SKILL.md  # Alternative OpenCode-native path

```


* **Global Scope (Machine-wide):**
```text
~/.claude/skills/<skill-name>/SKILL.md      # Discovered globally by both
~/.config/opencode/skills/<skill-name>/SKILL.md # OpenCode global fallback

```



---

### 2. Frontmatter Compatibility

The intersection of frontmatter fields recognized across both environments focuses on the required metadata standard:

```markdown
---
name: git-release
description: Create consistent releases and changelogs. Use when asked to cut a release, bump versions, or draft release notes.
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
---

```

* **`name`**: Must match the containing directory name, using lowercase alphanumeric characters and single hyphens (1–64 characters).
* **`description`**: Must be between 1 and 1024 characters. Both engines rely heavily on this exact string during initialization to decide when to trigger the skill dynamically.

---

### 3. Key Interoperability Caveats

While the markdown body and folder layout are fully interchangeable, keep two platform-specific execution details in mind:

1. **Environment Placeholders:** Claude Code supports specific runner variables like `${CLAUDE_SKILL_DIR}` inside skill instructions to reference bundled script paths. OpenCode handles path resolution relative to the skill's base directory automatically, but if you write custom scripts inside a `scripts/` folder, keep paths clean and explicit so they evaluate cleanly in both runtimes.
2. **Permission Guardrails:** OpenCode uses explicit block/allow permission maps inside `opencode.json` to control which agents can invoke specific skill IDs, whereas Claude Code relies primarily on its internal tool authorization prompts.

Are you looking to migrate an existing library of `.claude` skills over to an OpenCode workflow structure?