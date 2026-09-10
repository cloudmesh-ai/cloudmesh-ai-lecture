# Mastering the GitHub CLI (gh)

!!! info "Learning Objectives"
    By the end of this section, you will be able to:

    * **Install** and authenticate the GitHub CLI (`gh`) on a Linux system.
    * **Manage** SSH keys and authentication scopes from the terminal.
    * **Automate** repository operations, including forking and cloning.
    * **Execute** the full Pull Request lifecycle (create, checkout, review, merge) without leaving the shell.
    * **Organize** and track GitHub Issues using command-line tools.

The GitHub CLI (`gh`) is an extension of the standard Git toolset. While `git` manages the local version control and transport to a remote, `gh` manages GitHub-specific features—such as Pull Requests, Issues, and Repository settings—directly from your terminal.

By integrating these workflows into the shell, developers can avoid constant browser context-switching and automate their repository management. This is particularly useful for CI/CD pipeline scripts and developers who prefer a keyboard-driven workflow.

## Installation and Authentication

Setting up the GitHub CLI requires both the installation of the binary and the authentication of your GitHub account.

### 1. Simplified Installation

For most users, the fastest way to install the GitHub CLI is through a system package manager.

**Why this matters:** Package managers handle dependencies and simplify the update process, allowing you to keep the tool current with a single command.

**macOS (Homebrew):**

```bash
brew install gh
```

**Windows (winget):**

```bash
winget install --id GitHub.cli
```

**Linux (General):**

Many Linux distributions provide `gh` through their standard package managers. For example:
- **Fedora**: `sudo dnf install gh`
- **Arch Linux**: `sudo pacman -S github-cli`

### 2. Detailed Installation for Ubuntu

For Ubuntu 24.04 and newer, the official GitHub repository is the recommended source to ensure you receive the latest updates and security patches.

**Why this matters:** Using the official repository instead of a generic package manager version ensures that you have access to the latest `gh` features, which are updated frequently to match GitHub's API changes.

```bash
# Install curl and create the keyrings directory for GPG keys
sudo apt update && sudo apt install curl -y
sudo mkdir -p -m 755 /etc/apt/keyrings

# Download the official GitHub GPG key to verify package integrity
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg

# Add the official GitHub repository to the system sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Update package lists and install the gh CLI
sudo apt update
sudo apt install gh -y
```

!!! tip "Professional Shortcut"
    Using `sudo tee` allows you to write to system files while maintaining the correct permissions, avoiding the need to enter a root shell for simple configuration changes.

### 3. Authentication

Once installed, you must link the CLI to your GitHub account.

```bash
# Start the interactive login process
gh auth login
```

During this process, you will be prompted to select:
1. **GitHub.com or GitHub Enterprise Server**: Choose the host where your account resides.
2. **Preferred protocol for Git operations**: SSH is recommended for automated environments, while HTTPS is easier for beginners.
3. **Authentication method**: Browser-based login is the fastest for local machines, while a Personal Access Token (PAT) is required for headless servers.

!!! warning "Insufficient OAuth Scopes"
    If you receive an error stating "insufficient OAuth scopes" when performing an action (like adding an SSH key), your current session lacks the necessary permissions. Refresh your token with the required scope:
    ```bash
    # Grant permission to manage public keys
    gh auth refresh -s write:public_key
    ```

## Managing SSH Keys

The `gh` tool simplifies the process of syncing your local environment with your GitHub account's security settings.

**Why this matters:** SSH keys provide a secure, passwordless way to communicate with GitHub, which is essential for seamless `git push` and `git pull` operations.

To add your existing public key to your GitHub account:

```bash
# Add a local public key to your GitHub account
gh ssh-key add ~/.ssh/id_rsa.pub
```

!!! tip "Best Practice"
    Always use a strong encryption algorithm (like Ed25519) when generating your SSH keys for better security and performance.

## Repository Operations

`gh` allows you to perform high-level repository management tasks without opening a web browser.

### 1. Forking a Repository

Forking creates a personal copy of someone else's project, allowing you to make changes without affecting the original source.

**Why this matters:** In open-source development, you rarely have write access to the upstream repository. Forking is the standard mechanism for contributing via Pull Requests.

```bash
# Fork the current repository to your own account
gh repo fork
```

### 2. Cloning a Repository

You can clone repositories using a simplified shorthand instead of the full URL.

```bash
# Clone a repository using the owner/repo shorthand
gh repo clone cloudmesh-ai-lecture/cloudmesh-ai-lecture
```

## The Pull Request Lifecycle

The Pull Request (PR) workflow is where `gh` provides the most significant productivity gains, allowing you to move a feature from a local branch to a merged state entirely from the shell.

### 1. Creating a Pull Request

After you have pushed your feature branch to your fork, you can initiate the review process.

**Why this matters:** Automating PR creation reduces the friction of contributing and ensures that PR descriptions are consistent.

```bash
# Create a PR interactively (prompts for title and body)
gh pr create
```

### 2. Reviewing and Testing PRs

As a maintainer or a peer reviewer, you can manage PRs efficiently.

```bash
# Check the status of the PR associated with the current branch
gh pr status

# List all open PRs in the current repository
gh pr list

# Checkout a specific PR (e.g., PR #123) to test changes locally
gh pr checkout 123

# Approve a PR after verifying the changes
gh pr review --approve 123
```

### 3. Merging and Closing

Once a PR is approved and passes CI tests, it can be merged.

```bash
# Merge the approved PR into the base branch
gh pr merge 123

# Close a PR without merging if the changes are no longer needed
gh pr close 123
```

## Managing Issues

Issues are used to track bugs, tasks, and feature requests. `gh` allows you to manage this backlog without leaving your IDE.

### 1. Creating an Issue

When you encounter a bug, you can report it immediately.

**Why this matters:** Reporting issues via CLI allows you to include environment details or log snippets directly from your terminal into the issue body.

```bash
# Create a new issue with a title and body
gh issue create --title "Bug: API Timeout" --body "The API times out after 30 seconds of inactivity in the production environment."
```

### 2. Tracking and Closing Issues

You can monitor your workload and resolve issues as they are fixed.

```bash
# List all open issues in the repository
gh issue list

# Check the status of issues specifically assigned to you
gh issue status

# Close a specific issue (e.g., Issue #123)
gh issue close 123
```

!!! tip "Summary Checklist"
    Ensure you have mastered these core `gh` commands:

    * **Authentication**: `gh auth login` to connect your account.
    * **Security**: `gh ssh-key add` to sync public keys.
    * **Repositories**: `gh repo fork` for contributing and `gh repo clone` for downloading.
    * **Pull Requests**: `gh pr create` $\rightarrow$ `gh pr checkout` $\rightarrow$ `gh pr review` $\rightarrow$ `gh pr merge`.
    * **Issues**: `gh issue create` for reporting and `gh issue list` for tracking.

## Practical Exercises

!!! note "Exercise 1: Basic Setup"
    **Task:** Install the `gh` CLI on your Linux machine, authenticate your account, and verify the connection.
    
    1. Run the installation script provided in the Installation section.
    2. Run `gh auth login` and complete the browser-based authentication.
    3. Verify your status by running `gh auth status`.
    **Deliverable:** A screenshot of the terminal showing the output of `gh auth status`.

!!! note "Exercise 2: The PR Cycle"
    **Task:** Perform a full contribution cycle from forking to PR creation.
    
    1. Find a public repository and fork it using `gh repo fork`.
    2. Clone your fork locally using `gh repo clone`.
    3. Create a new branch, make a small change to a README or documentation file, and commit it.
    4. Push the branch and create a Pull Request using `gh pr create`.
    5. Verify the PR is open by running `gh pr list`.
    **Deliverable:** The URL of your created Pull Request.

!!! note "Exercise 3: Issue Lifecycle"
    **Task:** Manage the lifecycle of a GitHub Issue using the CLI.
    
    1. Create a new issue in your forked repository using `gh issue create`.
    2. List all open issues to confirm the issue exists.
    3. Use `gh issue close` to resolve and close the issue.
    **Deliverable:** A screenshot of the terminal showing the issue creation and the subsequent closure.

## Appendix: Command Reference

The following table summarizes the most commonly used GitHub CLI commands for quick reference.

| Command | Example | Description |
| :--- | :--- | :--- |
| `gh auth login` | `gh auth login` | Authenticate the CLI with your GitHub account. |
| `gh auth refresh` | `gh auth refresh -s write:public_key` | Refresh OAuth scopes to grant additional permissions. |
| `gh ssh-key add` | `gh ssh-key add ~/.ssh/id_rsa.pub` | Add a local public SSH key to your GitHub account. |
| `gh repo fork` | `gh repo fork` | Fork a repository to your personal account. |
| `gh repo clone` | `gh repo clone owner/repo` | Clone a repository using shorthand. |
| `gh pr create` | `gh pr create` | Create a new Pull Request interactively. |
| `gh pr status` | `gh pr status` | Check the status of the PR for the current branch. |
| `gh pr list` | `gh pr list` | List open Pull Requests in the repository. |
| `gh pr checkout` | `gh pr checkout 123` | Checkout a specific PR locally for testing. |
| `gh pr review` | `gh pr review --approve 123` | Approve or comment on a Pull Request. |
| `gh pr merge` | `gh pr merge 123` | Merge a Pull Request into the base branch. |
| `gh issue create` | `gh issue create --title "Bug" --body "Details"` | Create a new GitHub Issue. |
| `gh issue list` | `gh issue list` | List all open issues in the repository. |
| `gh issue status` | `gh issue status` | Show status of issues assigned to you. |
| `gh issue close` | `gh issue close 123` | Close a specific issue. |

