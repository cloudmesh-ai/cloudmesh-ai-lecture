# Assignment Summary & Catch‑up Plan

This document compiles the key assignments posted on Piazza for the **cloudmesh‑ai** course and presents a concise plan organized into three sections. All progress should be recorded in `assignments/STATUS.md`.

---

## 1. Catch‑up Plan

The catch‑up plan provides a schedule developed by you to bring you up to speed on missed material and keep you on track for the remainder of the class. Follow the checklist below and document each completed step in `assignments/STATUS.md`.

### Checklist

1. **Generate and register an SSH key** on GitHub. Verify with `ssh -T git@github.com`.
2. **Create a class directory** `~/work/` and clone the required repositories (your project repo, `cloudmesh‑ai‑common`, `cloudmesh‑ai‑vm`, `cloudmesh‑ai‑llm‑mock`).
3. **Install Bash utilities** (`git`, `curl`, `jq`, `make`).
4. **Set up the Jetstream LLM** (see Piazza post [149] for detailed steps). Use the LLM in the Cline environment and in your code to run a test inference.
5. **Run the smoke tests** for `cloudmesh‑ai‑vm` (Piazza post [155]) on your local machine and on the assigned clouds (Jetstream, Chameleon, make a section for each in your STATUS.md file).
6. **Develop a small PR** for a provider in `cloudmesh‑ai‑vm` (e.g., add a minimal `create_instance` implementation).
7. **Prepare compency demo** – record a short screen‑capture showing the SSH key workflow, Bash commands, and a push to GitHub. Do not upload any videos to GitHub.
8. **Read every Piazza post** (including follow‑ups) and adjust your notification settings accordingly.
9. **Mandatory proficiency check** – attend the live Nov 5 session (re‑scheduled to Nov 12, further rescheduled to after Nov 14th, as for an offic hour meeting before Thu 19) or submit a screen‑recorded demo before Thu 19. See the “Mandatory Assignments” note for details. If you miss that deadline you will be assigned an "F" for this task as you missed three chances to show your compency.

### Progress Documentation

After each step, add a bullet point to `assignments/STATUS.md` with links to any screenshots, videos, or pull requests you created. Keep the entry to **≤ 5 bullets per week**.

---

## 2. cloudmesh‑ai‑vm Development

The `cloudmesh‑ai‑vm` component is used throughout the course to provide a practical playground for the concepts taught in class. Follow these weekly tasks:

1. **Branch** – work on the `dev3` branch of the `cloudmesh‑ai‑vm` repository.
2. **Provider development** – implement or improve providers (e.g., Lima, Multipass, Chameleon, Jetstream, Docker, ..., e.g. what you selected). Aim for small, incremental PRs.
3. **Run smoke tests** – execute the existing test suite and any new tests you add after each change.
4. **LLM‑assisted review** – use the Jetstream LLM to review code, generate improvement suggestions, and verify the output before committing.
5. **File issues** – create GitHub issues only for novel problems; reference existing issues where applicable.
6. **Submit PRs** – keep each pull request focused on a single feature or fix. Coordinate with classmates to combine related PRs.
7. **Update `STATUS.md`** – log weekly progress, linking to PRs and any issues filed.
8. **Multi‑cloud testing** – run your provider on both Jetstream and Chameleon to demonstrate DevOps workflow in a team setting. Then also check the provider on your other cloud(s). We need to avoid that your provider breaks other providers. It is therefor not enough to yust check it on your providor.
9. **Mandatory proficiency check** – the Nov 5/12/19 live session includes a hands‑on LLM demonstration in Cline; ensure you can showcase this during the check. You are allowed to work in teams and show md files with screenshots.
If this check of using the LLM is not completed by Nov 19 this task will be graded with an "F" as you had 3 times the chance to show it.

> **Note:** Do **not** commit any environment files, secret keys, or other sensitive information to the repository.

---

## 3. Class Project

Your personal project should be organized under a single directory (e.g., `~/work/`). 
Clonin ito ~/work the forked repos for 
Use the `cloudmesh‑ai‑llm‑mock` and `cloudmesh‑ai‑vm` so you can use them as templates for the project layout.
Make sure to also clone your onw repo into ~/work which we call from now on with the placeholder <REPONAME>

### Project Structure

```
<REPONAME>/
├── src/        # source code
├── docs/       # documentation
├── Makefile    # make commands for build / test
└── pyproject.toml
```

### Development Workflow

* **Installation** – run `pip install -e .` or `make install` (adjust as needed for your project).
* **LLM assistance** – ask the Jetstream LLM to suggest improvements, generate code snippets, or write documentation. **Review every line** before applying, as the model may produce incorrect suggestions.
* **Version control** – push all changes via SSH enabled github using the SSH key set up in the catch‑up plan.
* **Safety** – never commit `.env` files, credentials, or other secrets. make sure your program only uses sectrets in ~/.config/... If we find one in github you will be getting a full grade deduction. So be careful
* **Documentation** – maintain a clear `README.md` with installation and usage instructions. Include screenshots or a short video if the project is complex. Also create a detailed mkdocs documentation.

### Progress Documentation

Record your weekly achievements in `assignments/STATUS.md` with links to the relevant commits, PRs, or documentation updates.

---

## References

* <https://piazza.com/class/mt5rkdsycb31c3/post/191> – Main assignment description.
* <https://piazza.com/class/mt5rkdsycb31c3/post/149> – LLM setup on Jetstream.
* <https://piazza.com/class/mt5rkdsycb31c3/post/188> – Git Bash & SSH key instructions.
* <https://piazza.com/class/mt5rkdsycb31c3/post/150> – Step‑by‑step SSH key guide.
* <https://piazza.com/class/mt5rkdsycb31c3/post/176> – Additional assignment (post 176).
* <https://piazza.com/class/mt5rkdsycb31c3/post/187> – Required reading 1.
* <https://piazza.com/class/mt5rkdsycb31c3/post/153> – Required reading 2.
* <https://piazza.com/class/mt5rkdsycb31c3/post/155> – Smoke tests instructions.
