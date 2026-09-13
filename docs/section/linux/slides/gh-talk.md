---
title: Mastering the GitHub CLI (gh)
type: presentation
---

# Mastering the GitHub CLI (`gh`)
## Streamlining the GitHub Workflow from the Terminal

<!-- speaker notes
Welcome everyone. Today we're moving beyond basic Git. While 'git' handles the versioning, 'gh' handles the platform. We'll learn how to stop switching to the browser every 5 minutes and instead manage your entire GitHub presence from the shell.
-->

---

## Learning Objectives
- **Install** and authenticate the `gh` CLI on Linux
- **Manage** SSH keys and authentication scopes via terminal
- **Automate** repository operations (Forking & Cloning)
- **Execute** the full PR lifecycle (Create $\rightarrow$ Review $\rightarrow$ Merge)
- **Organize** GitHub Issues using command-line tools

<!-- speaker notes
The goal here is productivity. By the end of this session, you'll be able to handle the entire 'social' side of coding—PRs, issues, and repo settings—without ever leaving your IDE or terminal.
-->

---

## Why `gh`? The "Context-Switching Tax"
- **The Problem**: Constant browser switching for PRs, Issues, and Settings
- **The Solution**: The GitHub CLI (`gh`)
- **The Value**:
    - **Speed**: Keyboard-driven management
    - **Automation**: Scriptable workflows for CI/CD
    - **Focus**: Environment stays centered in the terminal

<!-- speaker notes
Every time you switch to a browser, you lose a bit of focus. 'gh' isn't just a convenience; it's a way to integrate your project management directly into your development environment, reducing cognitive load.
-->

---

## Quick Start: Installation
- **macOS**: `brew install gh`
- **Windows**: `winget install --id GitHub.cli`
- **Linux (General)**:
    - **Fedora**: `sudo dnf install gh`
    - **Arch**: `sudo pacman -S github-cli`

<!-- speaker notes
For most users, the system package manager is the fastest route. It handles dependencies and simplifies updates, ensuring you have the latest features without manual binary management.
-->

---

## Ubuntu Setup: The Official Way
- **Avoid** generic package manager versions
- **Use** official GPG keys and repository
- **Benefit**: Access to the latest API features and security patches

```bash
# Setup Keyring
sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
```

<!-- speaker notes
On Ubuntu, using the official GitHub repository is critical. The 'gh' tool evolves rapidly to match API changes; generic versions are often outdated, which can lead to command failures.
-->

---

## Ubuntu Setup: Finalizing Install
```bash
# Add Repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Install
sudo apt update && sudo apt install gh -y
```

<!-- speaker notes
Once the repository is added, a standard apt update and install will pull the correct binary. This ensures the tool is managed by the system's package manager for easy updates.
-->

---

## Pro Tip: The Power of `sudo tee`
- **The Problem**: Writing to system files often requires a root shell
- **The Solution**: `sudo tee`
- **How it works**:
    - `echo` runs as a normal user
    - `tee` runs as root to write the file
    - Prevents the need for `sudo su` or `sudo -i`

<!-- speaker notes
Using 'sudo tee' is a professional shortcut. It allows you to write to system files while maintaining correct permissions, avoiding the risks associated with running a full root shell for simple configuration changes.
-->

---

## Authentication: Linking Your Account
- **The Command**:
  ```bash
  gh auth login
  ```
- **The Process**:
    1. Select host (GitHub.com vs Enterprise)
    2. Choose auth method (Web browser vs Token)
    3. Authorize the CLI

<!-- speaker notes
This is a one-time setup. Once linked, the CLI manages your OAuth tokens securely in your local config, allowing it to perform actions on your behalf across the GitHub API.
-->

---

## Repo Management: Forking
- **The Command**:
  ```bash
  gh repo fork
  ```
- **The Value**:
    - Handles the GitHub-side fork
    - Handles the local-side clone
    - All in one streamlined process

<!-- speaker notes
'gh repo fork' is a massive time-saver. Instead of clicking 'Fork' in the browser and then manually copying the SSH URL to run 'git clone', this single command does both.
-->

---

## Repo Management: Cloning
- **The Command**:
  ```bash
  gh repo clone owner/repo
  ```
- **Key Advantage**:
    - No need for full URLs (HTTPS/SSH)
    - Uses shorthand naming
    - Integrates directly with your configured auth

<!-- speaker notes
When you already have a fork or just need a specific repo, 'gh repo clone' is the fastest way to get the code locally. It removes the friction of searching for the clone URL on the project page.
-->

---

## The PR Lifecycle: Overview
**The Full Contribution Loop:**

1. **Create**: `gh pr create` $\rightarrow$ Propose changes
2. **Check**: `gh pr list` $\rightarrow$ Monitor open PRs
3. **Test**: `gh pr checkout` $\rightarrow$ Pull PR locally
4. **Review**: `gh pr review` $\rightarrow$ Approve/Comment
5. **Merge**: `gh pr merge` $\rightarrow$ Finalize the change

<!-- speaker notes
This is the 'Power User' flow. Imagine reviewing a colleague's code: you checkout their PR, run the tests locally, and approve the merge—all without a single click in a browser.
-->

---

## PRs: From Creation to Testing
- **Create a PR**:
  ```bash
  gh pr create --title "Fix: API bug" --body "Details..."
  ```
- **Test a PR locally**:
  ```bash
  gh pr checkout 123
  ```

<!-- speaker notes
'gh pr create' allows you to open a PR immediately after pushing. Even more powerful is 'gh pr checkout', which automatically creates a local branch and pulls the remote PR code for you to test.
-->

---

## PRs: From Review to Merge
- **Review and Approve**:
  ```bash
  gh pr review --approve 123
  ```
- **Merge the PR**:
  ```bash
  gh pr merge 123
  ```

<!-- speaker notes
The final stage is the merge. You can specify the merge method (squash, rebase, or merge commit) directly from the CLI, completing the cycle from local commit to main branch.
-->

---

## Organizing the Backlog: Issues
- **Create an Issue**:
  ```bash
  gh issue create --title "Bug" --body "Description"
  ```
- **Track Issues**:
  ```bash
  gh issue list      # All open issues
  gh issue status    # Issues assigned to YOU
  ```

<!-- speaker notes
Issue management via CLI is perfect for developers who want to keep a 'To-Do' list visible in their terminal. It turns your shell into a lightweight project management dashboard.
-->

---

## Organizing the Backlog: Resolution
- **Close an Issue**:
  ```bash
  gh issue close 123
  ```
- **Link to PRs**:
  - Use keywords like `Closes #123` in your PR description
  - `gh` helps track these associations automatically

<!-- speaker notes
Closing issues from the CLI is the final step in the feature lifecycle. By linking issues to PRs, you maintain a clean audit trail of why a change was made and which bug it resolved.
-->

---

## Self-Assessment
!!! tip "Self-Assessment"
    Test your knowledge by expanding the questions below.

??? question "How do you initially connect your GitHub account to the CLI?"
    Use the `gh auth login` command to authenticate and set up your account.

??? question "What is the fastest way to begin contributing to a repository using `gh`?"
    Use `gh repo fork` to fork the project to your account and clone it locally in one step.

??? question "How do you propose changes to a project using the GitHub CLI?"
    Use `gh pr create` to open a Pull Request directly from the terminal.

??? question "How can you test someone else's Pull Request locally without manual git commands?"
    Use `gh pr checkout <pr-number>` to automatically create a local branch and pull the PR's code.

??? question "How do you stay updated on the current state of a project's bugs and feature requests?"
    Use `gh issue list` to view all open issues associated with the repository.

<!-- speaker notes
Mastering these five patterns removes the friction between writing code and managing the project. You are now operating at the speed of the terminal.
-->

---

## Practical Exercises
1. **Basic Setup**: Install `gh` $\rightarrow$ `auth login` $\rightarrow$ `auth status`
2. **The PR Cycle**: `repo fork` $\rightarrow$ `repo clone` $\rightarrow$ Modify $\rightarrow$ `pr create`
3. **Issue Lifecycle**: `issue create` $\rightarrow$ `issue list` $\rightarrow$ `issue close`

<!-- speaker notes
For Exercise 2, pay attention to the branch you are on when creating the PR. For Exercise 3, try using the --title and --body flags to avoid the interactive prompt.
-->
