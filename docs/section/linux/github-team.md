
# Chapter – Collaborative Development with Forked Repositories  

## 1️⃣ Introduction  

When two developers need to work on the same code‑base but do not have direct write access to the upstream (origin) repository, the *fork‑and‑pull‑request* workflow is the de‑facto standard. This chapter walks you through every step of that workflow, from creating a fork to merging the final changes back into the upstream repository, while keeping the history clean and the collaboration efficient.

---

## 2️⃣ Learning Objectives  

!!! note  
- Understand the purpose of a fork and how it differs from a branch in the upstream repo.  
- Clone a fork, create feature branches, and keep them in sync with upstream.  
- Use pull requests (PRs) to propose changes, trigger CI, and collect feedback.  
- Resolve merge conflicts and perform a clean rebase when needed.  
- Merge a PR safely with appropriate merge strategies (merge‑commit, squash, or rebase).  
- Apply post‑merge housekeeping (delete branches, update documentation, tag releases).  

---

## 3️⃣ Prerequisites  

| Item | Reason |
|------|--------|
| Git (≥2.30) installed locally | Core version‑control commands. |
| Access to the hosting platform (GitHub, GitLab, Bitbucket, etc.) | Fork creation, PR UI, CI integration. |
| A CI pipeline configured on the upstream repo (e.g., GitHub Actions, GitLab CI) | Automated verification before any merge. |
| Basic markdown editing skills | PR description, commit messages, documentation updates. |

---

## 4️⃣ End‑to‑End Workflow  

### 4.1 Fork the Upstream Repository  

1. Navigate to the upstream repository page (e.g., `https://github.com/org/project`).  
2. Click **Fork** – the platform creates a copy under your personal account (`your‑user/project`).  

> **Why fork?**  
> - You obtain a private writeable space.  
> - The upstream remains protected; only maintainers can push directly.  

### 4.2 Clone Your Fork Locally  

```bash
# Clone via SSH (recommended) or HTTPS
git clone git@github.com:your-user/project.git
cd project
```

### 4.3 Add the Upstream Remote  

```bash
git remote add upstream https://github.com/org/project.git
# Verify
git remote -v
# upstream  https://github.com/org/project.git (fetch)
# upstream  https://github.com/org/project.git (push)
# origin    git@github.com:your‑user/project.git (fetch)
# origin    git@github.com:your‑user/project.git (push)
```

> **Purpose** – `upstream` points to the original repo; `origin` points to your fork.  

### 4.4 Keep a Clean `main` (or `master`) Branch  

Before starting any work, synchronize your local `main` with upstream:

```bash
git checkout main
git fetch upstream
git reset --hard upstream/main   # discard any local diverging commits
git push origin main --force     # keep fork’s main identical to upstream
```

> **Tip:** Perform this step at the beginning of each day or before a new feature.

### 4.5 Create a Feature Branch  

```bash
git checkout -b feature/awesome‑logic
```

- Branch names should be descriptive and follow your team’s naming convention (`feature/`, `bugfix/`, `docs/`).  
- The branch is **based on the freshly synced `main`**, ensuring a minimal diff.

### 4.6 Develop, Commit, and Push  

1. **Write code** – adhere to the project’s style guide.  
2. **Stage changes**  
   ```bash
   git add path/to/file1 path/to/file2
   ```
3. **Write an atomic commit**  
   ```bash
   git commit -m "feat: add awesome logic to process user input"
   ```
   Follow the conventional‑commit format (type, scope, description).  
4. **Push the branch to your fork**  
   ```bash
   git push -u origin feature/awesome‑logic
   ```

### 4.7 Open a Pull Request  

1. Go to the fork’s GitHub page.  
2. You’ll see a banner: *“Compare & pull request”* – click it.  
3. Ensure the **base repository** is the upstream (`org/project`) and **base branch** is `main`.  
4. The **compare branch** should be `your‑user:feature/awesome‑logic`.  
5. Fill in the PR template:  
   - **Title** – concise, prefixed with the ticket/issue ID if applicable.  
   - **Description** – what the change does, why it’s needed, and any relevant screenshots or logs.  
   - **Testing instructions** – how the reviewer can verify the change locally.  

6. Add **reviewers** (your colleague, team leads, or CI bots).  

### 4.8 Review Cycle  

| Activity | Who does it? | What to look for |
|----------|--------------|------------------|
| Automated CI | CI system (GitHub Actions, GitLab CI) | Build succeeds, unit/integration tests pass, linting clean. |
| Human code review | Assigned reviewers | Correctness, readability, adherence to architecture, edge‑case handling. |
| Security audit (optional) | Security champion / automated scanners | Secrets, vulnerable dependencies, compliance. |

**Best practices for reviewers**  

- Use inline comments for specific lines.  
- Summarize overall feedback in the PR comment box.  
- Approve only when the change meets the definition of done.  

### 4.9 Incorporate Feedback  

After reviewers comment:

```bash
# Make changes locally on the same branch
git add updated/file.py
git commit --amend   # or create a new commit
git push --force-with-lease   # safely overwrite remote branch
```

- **Never rewrite history** that other collaborators have based work on.  
- Use `--force-with-lease` to protect against accidental overwrites.

### 4.10 Resolve Merge Conflicts (if any)  

1. **Fetch the latest upstream `main`**  
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main   # fast‑forward, no conflicts expected
   git push origin main
   ```

2. **Rebase your feature branch onto the updated `main`**  
   ```bash
   git checkout feature/awesome‑logic
   git rebase main
   # Resolve conflicts file by file
   # After each resolution:
   git add <file>
   git rebase --continue
   ```

3. **Force‑push the rebased branch**  
   ```bash
   git push --force-with-lease
   ```

Rebasing keeps the PR’s commit history linear, which simplifies the final merge.

### 4.11 Merge the Pull Request  

When CI passes, reviewers approve, and any conflicts are resolved, you can merge. Choose the merge strategy that matches your project’s policy:

| Strategy | Result | When to use |
|----------|--------|-------------|
| **Merge commit** (`Create a merge commit`) | Preserves full branch history; a single merge commit appears on `main`. | Large feature branches where you want to retain the development timeline. |
| **Squash and merge** | All commits from the branch are collapsed into one commit on `main`. | Small or iterative changes; keeps `main` tidy. |
| **Rebase and merge** | Commits are rebased onto `main` without a merge commit. | When you want a strictly linear history and have already rebased locally. |

After merging:

1. **Delete the remote feature branch** (GitHub shows a button).  
2. **Delete the local branch**  
   ```bash
   git branch -d feature/awesome‑logic
   ```

### 4.12 Post‑Merge Activities  

| Task | Why it matters |
|------|----------------|
| **Update documentation** (README, changelog) | Keeps users informed of new behavior. |
| **Tag a release (if applicable)** | Provides an immutable snapshot for downstream consumers. |
| **Notify stakeholders** (Slack, email) | Communication loop closes the development cycle. |
| **Sync fork’s `main`** (as in 4.4) | Ensures the fork stays a clean mirror of upstream. |

---

## 5️⃣ Common Pitfalls & How to Avoid Them  

| Problem | Symptom | Fix |
|---------|---------|-----|
| Divergent `main` in fork | PR shows huge diff unrelated to your work. | Re‑sync `main` with upstream (Step 4.4) and re‑base your branch. |
| Accidentally pushing directly to upstream `main` | CI fails, maintainers reject. | Set branch protection rules on upstream; work only on feature branches. |
| Stale CI pipeline | PR passes locally but fails after merge. | Run the CI on the **latest** `main` (GitHub checks the merge commit automatically). |
| Forgetting to update the PR description after large changes | Reviewers lack context. | Edit the PR description whenever the scope changes. |
| Over‑writing a teammate’s commits with `git push --force` | Lost work, frustration. | Use `--force-with-lease` and avoid force‑pushing after a reviewer has begun a review. |

---

## 6️⃣ Assignments  

1. **Set up a forked workflow**:  
   - Fork the public repository `https://github.com/psf/requests`.  
   - Clone it locally, add the upstream remote, and synchronize `main`.  

2. **Implement a tiny feature**:  
   - Add a new helper function `requests.utils.is_json_response(response)` that returns `True` if the `Content‑Type` header indicates JSON.  
   - Write unit tests covering at least three cases (valid JSON header, non‑JSON header, missing header).  

3. **Open a PR**:  
   - Follow the PR template guidelines; request a review from a classmate or a friend.  

4. **Run the full review loop**:  
   - Have your peer leave at least two review comments.  
   - Incorporate the feedback, resolve any merge conflicts (you can simulate a conflict by editing the same line in upstream `main`).  

5. **Merge the PR** using the *Squash and merge* strategy.  
   - Delete the feature branch both locally and on the remote.  

6. **Document the changes**:  
   - Update the project’s `CHANGELOG.md` entry.  
   - Tag a new version (`v2.28.1`) on the fork and push the tag.  

Submit a short report (≈300 words) describing each step you performed, any problems you encountered, and how you solved them.

---

## 7️⃣ Self‑Assessment Checklist  

- [ ] I can create a fork and add the upstream remote.  
- [ ] My local `main` stays in sync with upstream before I start work.  
- [ ] I use feature branches with clear, conventional names.  
- [ ] My commits are atomic, well‑described, and follow the project’s commit‑message style.  
- [ ] I can open a PR, fill in a proper description, and assign reviewers.  
- [ ] I understand how CI integrates with the PR and can interpret failing checks.  
- [ ] I know how to rebase a branch onto an updated `main` and resolve conflicts.  
- [ ] I can choose the appropriate merge strategy and perform the merge safely.  
- [ ] I clean up remote and local branches after merging.  
- [ ] I update documentation, tag releases, and keep the fork’s `main` mirrored to upstream.  

If you can answer **yes** to every bullet, you are ready to collaborate on any fork‑based open‑source or internal project with confidence.