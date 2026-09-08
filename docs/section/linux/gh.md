# Mastering the GitHub CLI (gh)

!!! info "Learning Objectives"
    By the end of this section, you will be able to:

    * **Install** and authenticate the GitHub CLI (`gh`) on a Linux system.
    * **Manage** SSH keys and authentication scopes from the terminal.
    * **Automate** repository operations, including forking and cloning.
    * **Execute** the full Pull Request lifecycle (create, checkout, review, merge) without leaving the shell.
    * **Organize** and track GitHub Issues using command-line tools.

---

## Introduction to the GitHub CLI

The GitHub CLI (`gh`) is an extension of the standard Git toolset. While `git` manages the local version control and transport to a remote, `gh` manages the GitHub-specific features—such as Pull Requests, Issues, and Repository settings—directly from your terminal.

By integrating these workflows into the shell, developers can avoid constant browser context-switching and automate their repository management.

---

## Step-by-Step Implementation

Follow these steps to set up the GitHub CLI and begin managing your projects.

### 1. Installation and Authentication

For Ubuntu 24.04 and newer, we use the official GitHub repository to ensure we have the latest version. Modern Ubuntu versions require GPG keys to be stored in `/etc/apt/keyrings` for security and compatibility.

**Installation:**

```bash
# Install curl and create the keyrings directory
sudo apt update && sudo apt install curl -y
sudo mkdir -p -m 755 /etc/apt/keyrings

# Download the official GitHub GPG key
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null
sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg

# Add the official GitHub repository to the sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Install gh
sudo apt update
sudo apt install gh -y
```

**Authentication:**

Run the following command to start the interactive login process:

```bash
gh auth login
```

You will be prompted to choose your account type, preferred protocol (HTTPS or SSH), and authentication method (browser or token).

### 2. Managing SSH Keys

The `gh` tool simplifies adding your local public keys to your GitHub account.

To add a new SSH key:

```bash
gh ssh-key add ~/.ssh/id_rsa.pub
```

If you encounter an error regarding "insufficient OAuth scopes," you must refresh your authentication to grant the necessary permissions:

```bash
gh auth refresh -s write:public_key
```

### 3. Repository Operations

You can create forks and clone repositories without navigating to the GitHub website.

**Forking a Repository:**

If you do not have write access to a project, create a personal fork:

```bash
gh repo fork
```

**Cloning a Repository:**

Clone a repository using the `gh` shorthand:

```bash
gh repo clone owner/repo
```

### 4. The Pull Request Workflow

`gh` provides a complete set of tools to manage the PR lifecycle.

**Creating a Pull Request:**

After pushing your branch, create the PR:

```bash
gh pr create
```

**Managing and Reviewing PRs:**

Check the status of your current PR:

```bash
gh pr status
```

List all open PRs in the repository:

```bash
gh pr list
```

As a reviewer, you can checkout a specific PR to test the changes locally:

```bash
gh pr checkout 123
```

Once verified, approve the PR:

```bash
gh pr review --approve 123
```

**Merging and Closing:**

Merge the approved PR into the main branch:

```bash
gh pr merge 123
```

Close a PR without merging:

```bash
gh pr close 123
```

### 5. Managing Issues

Issues can be tracked and modified directly from the shell.

**Creating an Issue:**

```bash
gh issue create --title "Bug: API Timeout" --body "The API times out after 30 seconds of inactivity."
```

**Listing and Closing Issues:**

List all open issues:

```bash
gh issue list
```

Check the status of issues assigned to you:

```bash
gh issue status
```

Close a specific issue:

```bash
gh issue close 123
```

---

## Summary Checklist

The following commands form the core of the GitHub CLI workflow:

1. **Auth**: `gh auth login` (Connect account).
2. **Keys**: `gh ssh-key add` (Sync public keys).
3. **Repos**: `gh repo fork` (Fork project) and `gh repo clone` (Download).
4. **PRs**: `gh pr create` $\rightarrow$ `gh pr checkout` $\rightarrow$ `gh pr review` $\rightarrow$ `gh pr merge`.
5. **Issues**: `gh issue create` (Report bug) and `gh issue list` (Track).

---

## Assignments

!!! note "Assignment 1: Setup and Auth"
    **Task:** 

    1. Install the `gh` CLI on your Linux machine.
    2. Authenticate your account using `gh auth login`.
    3. Verify your authentication status and add your public SSH key to GitHub using the CLI.
    **Deliverable:** A screenshot of the terminal showing the output of `gh auth status`.

!!! note "Assignment 2: The PR Cycle"
    **Task:** 

    1. Fork a public repository using `gh repo fork`.
    2. Clone your fork locally.
    3. Create a new branch and make a small text change (e.g., updating a README).
    4. Create a Pull Request using `gh pr create`.
    5. List your PR using `gh pr list` to verify it is open.
    **Deliverable:** The URL of your created Pull Request.

!!! note "Assignment 3: Issue Tracking"
    **Task:** 

    1. Create a new issue in your forked repository using `gh issue create`.
    2. List all open issues to confirm it exists.
    3. Use `gh issue close` to close the issue you just created.
    **Deliverable:** A screenshot of the terminal showing the issue creation and the subsequent closure.
