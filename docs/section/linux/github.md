# GitHub and Git

!!! info "Learning Objectives"
    By the end of this section, you will be able to:

    * **Distinguish** between Git (the version control system) and GitHub (the hosting platform).
    * **Master** the core Git command-line workflow for local and remote versioning.
    * **Implement** a collaborative workflow using Forks and Pull Requests.
    * **Compare** the usage of the `git` CLI versus the `gh` (GitHub CLI) tool.
    * **Evaluate** and choose between CLI, GUI tools, and IDE integrations for different development scenarios.

The modern software development lifecycle relies on the ability to track changes, experiment with features, and collaborate with others without overwriting work. This is achieved through the combination of Git and GitHub.

While often mentioned in the same breath, they serve entirely different purposes: Git is the tool that tracks the history of your files, and GitHub is the cloud-based service that hosts those histories and adds social and project management layers.

## Git: The Core Version Control

Git is a distributed version control system (DVCS). "Distributed" means that every developer has a full copy of the project history on their local machine, not just a connection to a central server.

### 1. Fundamental Concepts

Before running commands, it is essential to understand the three main areas of a Git project:
1. **Working Directory**: Where you modify your files.
2. **Staging Area (Index)**: A "preview" area where you pick which changes will be part of the next commit.
3. **Local Repository**: Where Git permanently stores the snapshots (commits) of your project.

**Why this matters:** The staging area allows you to be selective. You might have fixed a bug and added a new feature in the same file, but you can commit them separately to keep the project history clean and readable.

### 2. Essential Git Commands

To get started, you must first configure your identity:

```bash
# Set your global identity
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

**The Basic Workflow:**

```bash
# Initialize a new local repository
git init

# Stage a specific file for commit
git add filename.txt

# Stage all changed files
git add .

# Commit staged changes with a descriptive message
git commit -m "Fix: resolve API timeout issue"

# Create a new feature branch
git branch feature-login
git checkout feature-login

# Merge the feature branch back into main
git checkout main
git merge feature-login
```

!!! warning "The Commit Message Trap"
    Avoid vague commit messages like "fixed stuff" or "updates". Use the imperative mood (e.g., "Add user authentication" instead of "Added user authentication") to follow industry standards and make the history searchable.

## GitHub: The Collaborative Platform

GitHub transforms Git from a local tool into a global collaboration engine. It provides a centralized location where teams can share their Git repositories.

### 1. Remotes, Pushing, and Pulling

A "remote" is a version of your project hosted on the internet or a network.

```bash
# Link your local repo to a GitHub remote
git remote add origin https://github.com/user/repo.git

# Upload local commits to the remote server
git push -u origin main

# Download changes from the remote and merge them into your local branch
git pull origin main
```

### 2. The Contribution Workflow (Fork & PR)

In professional and open-source environments, you rarely push directly to the `main` branch of a project. Instead, you use the Fork and Pull Request (PR) model.

1. **Fork**: Create a personal copy of the repository on your GitHub account.
2. **Clone**: Download your fork to your local machine.
3. **Branch**: Create a new branch for your specific change.
4. **Push**: Upload your branch to your fork.
5. **Pull Request**: Ask the original project maintainer to "pull" your changes into their project.

**Why this matters:** This model protects the production code. The maintainer can review your code, request changes, and run automated tests before any of your code ever touches the main codebase.

## Git vs. GitHub CLI (`gh`)

A common point of confusion for beginners is when to use `git` and when to use `gh`.

### 1. The Core Difference

* **`git`**: Operates on the **version control** level. It cares about snapshots, diffs, branches, and merges. It works regardless of whether you use GitHub, GitLab, or Bitbucket.
* **`gh`**: Operates on the **platform** level. It interacts with the GitHub API to manage Issues, Pull Requests, Releases, and Repository settings.

### 2. Comparison Table

| Feature | `git` CLI | `gh` CLI |
| :--- | :--- | :--- |
| **Primary Goal** | Manage file history | Manage GitHub platform |
| **Commits** | `git commit` (Yes) | No |
| **Branches** | `git branch` (Yes) | No |
| **Pull Requests** | No (Requires Web UI) | `gh pr create` (Yes) |
| **Issues** | No | `gh issue create` (Yes) |
| **Authentication** | SSH/HTTPS keys | OAuth / Browser login |
| **Scope** | Local $\rightarrow$ Remote | API $\rightarrow$ GitHub Cloud |

### 3. Which one to use?

Use **`git`** when you are doing the actual work: writing code, creating branches, and committing changes.
Use **`gh`** when you are managing the project: opening a PR, checking the status of a CI build, or reporting a bug via an issue.

!!! tip "The Power Combo"
    The most efficient developers use both. They use `git` to commit their work and `gh pr create` to submit it for review, all without ever leaving the terminal.

## GUI Tools and IDE Integration

While the CLI is the most powerful way to use Git, Graphical User Interfaces (GUIs) provide a visual representation of the project history (the "commit graph") that is difficult to replicate in text.

### 1. Standalone GUI Clients

* **GitHub Desktop**: The simplest entry point. Great for beginners who want a visual way to stage and commit.
* **GitKraken**: A professional-grade tool with an incredible visual commit graph and built-in merge conflict resolution.
* **Sourcetree**: A feature-rich client by Atlassian, preferred in many corporate environments.

### 2. IDE Integration

Modern IDEs integrate Git directly into their editor, reducing the need to switch windows.

**Visual Studio Code (VS Code):**
* **Built-in**: Basic staging, committing, and branching are handled in the "Source Control" tab.
* **GitLens (Plugin)**: The industry standard. It adds "git blame" annotations to every line of code, showing you exactly who changed what and when.

**JetBrains PyCharm / IntelliJ:**
* **Built-in**: JetBrains provides a visual merge tool. Their "Three-Way Merge" window makes resolving complex conflicts significantly easier than in VS Code.

### 3. Recommendation: Which to use?

| Scenario | Recommended Tool | Why? |
| :--- | :--- | :--- |
| **Daily Coding** | IDE (VS Code/PyCharm) | Fastest loop for committing and basic branching. |
| **Complex History/Merge** | GitKraken or PyCharm | Visual graphs make it easier to see where branches diverged. |
| **Automation/Scripting** | `git` + `gh` CLI | Essential for CI/CD and power-user speed. |
| **Absolute Beginners** | GitHub Desktop | Lowers the barrier to entry by removing the command line. |

!!! tip "Professional Advice"
    Learn the CLI first. GUIs are abstractions; if the GUI crashes or encounters a complex state (like a detached HEAD), only knowing the CLI will allow you to fix the repository without losing data.

!!! tip "Summary Checklist"
    Ensure you can perform these core tasks:

    * [ ] Initialize a repo (`git init`) and make your first commit.
    * [ ] Push code to a remote and pull updates from others.
    * [ ] Create a feature branch and merge it into main.
    * [ ] Fork a repository and submit a Pull Request.
    * [ ] Use `gh` to create an issue or check PR status.
    * [ ] Resolve a merge conflict using an IDE tool.

## Practical Exercises

!!! note "Exercise 1: Local Foundations"
    **Task:** Create a new folder, initialize it as a Git repository, create three different files, and commit them in two separate commits.
    **Deliverable:** Run `git log --oneline` and take a screenshot of the history.

!!! note "Exercise 2: The Collaborative Loop"
    **Task:** 
    1. Fork a public repository on GitHub.
    2. Clone your fork locally.
    3. Create a branch called `dev-update`.
    4. Make a change, commit it, and push it to your fork.
    5. Use `gh pr create` to open a Pull Request to the original repository.
    **Deliverable:** The URL of the Pull Request.

!!! note "Exercise 3: Conflict Resolution"
    **Task:** 
    1. Create two branches from `main`.
    2. Modify the same line of the same file in both branches and commit.
    3. Merge the first branch into `main`.
    4. Attempt to merge the second branch into `main` and resolve the resulting merge conflict using your IDE's merge tool.
    **Deliverable:** A screenshot of the resolved file and the final commit message.
