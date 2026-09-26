# MkDocs Documentation

!!! info "Learning Objectives"
    By the end of this chapter, you will be able to install MkDocs, configure a basic site using `mkdocs.yml`, and generate a static documentation website.

## Overview

MkDocs is a static site generator geared towards building project documentation. It uses Markdown for content creation. The resulting site is a collection of static HTML files that can be hosted on any web server.

## Installation

MkDocs is written in Python and can be installed using pip.

```bash
pip install mkdocs
```

For a modern look, the Material for MkDocs theme is recommended.

```bash
pip install mkdocs-material
```

## Basic Configuration

The `mkdocs.yml` file is the central configuration point for an MkDocs project. It defines the site name, the theme used, and the structure of the navigation menu.

### Configuration Example

Below is a basic example of an `mkdocs.yml` file.

```yaml
site_name: My Project Documentation
theme:
  name: material

nav:
  - Home: index.md
  - User Guide:
      - Installation: guide/install.md
      - Configuration: guide/config.md
  - API Reference: api.md
```

!!! note "Navigation Structure"
    The `nav` section allows you to define the hierarchy of your documentation. Indented items under a parent key create dropdown menus in the navigation bar.

## Common Commands

MkDocs provides a command-line interface to manage the development and deployment process.

### Local Preview

To preview changes, use the `serve` command. This starts a local development server that automatically reloads the page when files are modified.

```bash
mkdocs serve
```

### Generating the Site

To generate the static HTML files for deployment, use the `build` command.

```bash
mkdocs build
```

The output files are placed in the `site/` directory by default.

## Best Practices

### Folder Structure

Maintain a clean directory structure to keep the project manageable.

```text
docs/
├── index.md
├── guide/
│   ├── install.md
│   └── config.md
└── api.md
mkdocs.yml
```

### Cross-Referencing

Use relative paths to link between pages. This ensures that links remain functional regardless of where the site is hosted.

```markdown
For more details, see the [Installation Guide](guide/install.md).
```

## Summary Checklist

- [ ] MkDocs and `mkdocs-material` installed.
- [ ] `mkdocs.yml` configured with `site_name` and `nav`.
- [ ] Content created in the `docs/` directory using Markdown.
- [ ] Site verified locally using `mkdocs serve`.
- [ ] Static files generated using `mkdocs build`.

## Assignments

1. Install MkDocs and the Material theme in your local environment.
2. Create a basic project structure with an `index.md` and a subfolder containing at least two documentation pages.
3. Configure a `mkdocs.yml` file to reflect this structure and launch the local server to verify the navigation.

## Self-Evaluation

??? note "What is the primary purpose of the mkdocs.yml file?"
    The `mkdocs.yml` file serves as the central configuration file where the site name, theme, and navigation structure are defined.

??? note "Which command is used to preview documentation changes locally?"
    The `mkdocs serve` command starts a local server that provides a live preview of the documentation.

??? note "How should links between different pages be formatted in MkDocs?"
    Links between pages should use relative paths to the Markdown files within the `docs/` directory.

## Appendix: Integrating Multiple Repositories

It is possible to integrate Markdown (.md) documents hosted in different repositories into a single unified MkDocs site. Depending on the workflow and hosting provider, there are a few standard methods:

### 1. Dedicated MkDocs Plugins (Recommended)

Several open-source plugins automate the process of fetching documentation from external repositories during the build phase:

- **`mkdocs-multirepo-plugin`**: One of the most popular plugins for GitHub/GitLab integration. It allows you to specify remote repositories and branches in your configuration file. During the build, it clones or pulls those remote docs directly into your site structure without needing manual git submodules.
- **`mkdocs-monorepo-plugin`**: Often used alongside **Git submodules**, this plugin allows a central MkDocs project to consume documentation folders living inside sub-repositories.
- **`mkdocs-multisource-docs`**: Useful if you are working specifically with GitLab and need automated collection from multiple project repos using an application configuration file.

### 2. Git Submodules

If you prefer a native Git approach without third-party fetch plugins:

1. Add separate repositories as **Git submodules** inside the main documentation repository's `docs/` folder.
2. Reference the markdown files inside the main `mkdocs.yml` navigation (`nav`) section just like any local file.

### 3. CI/CD Pipeline Automation

If you want to keep repositories entirely decoupled, you can configure a CI/CD action (such as GitHub Actions):

- Set a pipeline script to clone the separate repositories into the `docs` directory right before running the `mkdocs build` command.
