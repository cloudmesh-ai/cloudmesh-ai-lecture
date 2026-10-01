# Writing an ACM-Styled Paper in Markdown

!!! info "Learning Objectives"
    * Set up a Dockerized toolchain (Pandoc, LaTeX, and acmart) for ACM publication.
    * Configure a Pandoc wrapper template to manage the ACM LaTeX class.
    * Implement a Lua filter to automatically generate author blocks from YAML metadata.
    * Author a research paper in Markdown with citations and bibliography.
    * Build a production-ready PDF using a Makefile and Docker container.

## Overview

This chapter provides a concise workflow for authoring scientific manuscripts in plain Markdown and producing a final PDF that conforms to the official ACM *acmart* class. To ensure a reproducible environment and avoid complex local installations of TeX Live, this workflow centers on a **Docker-based deployment**.

## Core Sections

### 1. The Dockerized Toolchain

Instead of installing Pandoc and LaTeX locally, we use a Docker image that contains all the necessary dependencies.

#### The Dockerfile
Create a `Dockerfile` to build the environment:

```Dockerfile
FROM pandoc/latex:latest

# Install the ACM class
RUN tlmgr install acmart

# Copy the CSL file into the container
COPY acm.csl /usr/local/share/csl/acm.csl

WORKDIR /data
```

#### Building the Image
Build the image once to prepare the environment:

```bash
docker build -t acm-md .
```

### 2. Obtaining the ACM Template

The foundation of the layout is the `acmart` class file.

1. Download the latest *acmart* zip from the ACM website: [ACM Reference Formatting](https://www.acm.org/publications/authors/reference-formatting).
2. Extract the zip file to a local directory. The resulting `acmart.cls` file is the critical component that Pandoc uses to define the document structure.

### 3. Creating the Pandoc Wrapper Template

Because the ACM class has specific requirements for metadata, a wrapper LaTeX template (`acm-pandoc.tex`) is used to map Pandoc variables to LaTeX commands.

```tex
\documentclass[sigconf,screen]{acmart}
\usepackage{booktabs}
\usepackage{microtype}
\usepackage{hyperref}
\usepackage{xcolor}

\title{$title$}
\author{$author-meta$}
\date{$date$}

\begin{document}
\maketitle

$if(abstract)$
\begin{abstract}
$abstract$
\end{abstract}
$endif$

$if(keywords)$
\keywords{$keywords$}
$endif$

$body$

$if(bibliography)$
\bibliographystyle{ACM-Reference-Format}
\bibliography{$bibliography$}
$endif$

\end{document}
```

### 4. Automating Author Blocks with Lua

The `acmart` class expects a specific series of `\author` and `\affiliation` commands. A Lua filter (`acm-authors.lua`) transforms the YAML author list into these specific LaTeX commands.

```lua
function Meta(meta)
  if meta.author then
    local out = {}
    for _, a in ipairs(meta.author) do
      local line = string.format("\\author{%s}", a.name or "")
      if a.affiliation then
        line = line .. string.format("\\affiliation{\\institution{%s}}", a.affiliation)
      end
      if a.email then
        line = line .. string.format("\\email{%s}", a.email)
      end
      if a.orcid then
        line = line .. string.format("\\orcid{%s}", a.orcid)
      end
      table.insert(out, line)
    end
    meta["author-meta"] = pandoc.MetaString(table.concat(out, "\n"))
  end
  return meta
end
```

### 5. Authoring the Manuscript

#### YAML Front-matter

All metadata must be defined in a YAML block at the top of the Markdown file (`paper.md`).

```yaml
---
title: "A Novel Approach to Real-Time Graph Processing"
author:
  - name: "Alice B. Researcher"
    affiliation: "University of Example"
    email: "alice@example.edu"
    orcid: "0000-0001-2345-6789"
  - name: "Bob C. Engineer"
    affiliation: "Example Corp."
    email: "bob@excorp.com"
    orcid: "0000-0002-9876-5432"
date: "2026-10"
abstract: |
  We present a new algorithm for streaming graph analytics that reduces latency by 45%.
keywords: ["graph processing", "streaming", "parallel"]
---
```

#### Body Content and Extensions

Use standard Markdown for the body. For ACM-specific requirements, use raw LaTeX blocks or Pandoc extensions.

| Feature | Pandoc Syntax | Example |
| :--- | :--- | :--- |
| Figure with Caption | `![Alt text](path){#fig:label}` | `![Pipeline](/img/pipeline.pdf){#fig:pipeline}` |
| Table with Caption | `: Caption text` after table | `| ... |\n: Table 1. Results.` |
| Cross-reference | `[@fig:label]` | "see Figure @fig:latency" |
| Citations | `[@key]` | "as shown by Smith [@smith2020]" |
| Raw LaTeX | ````{=latex} ... ```` | ````{=latex} \begin{algorithm} ... \end{algorithm} ```` |

#### Bibliography Management

Citations are managed using a BibTeX file (`refs.bib`).

```bibtex
@article{smith2020,
  author    = {John Smith and Jane Doe},
  title     = {Streaming Graph Algorithms},
  journal   = {IEEE Transactions on Knowledge and Data Engineering},
  year      = {2020},
  volume    = {32},
  number    = {5},
  pages     = {1234--1245},
  doi       = {10.1109/TKDE.2020.1234567}
}
```

### 6. The Build Process via Makefile

To simplify the Docker command, use a `Makefile` to manage the build process. This centralizes the complex command-line options, making the process reproducible and easy to share with co-authors.

#### The Makefile Implementation

```make
# ----------------------------------------------------------------------
# Makefile for an ACM paper written in Markdown, compiled via Docker
# ----------------------------------------------------------------------

# ---------- Configuration ------------------------------------------------
# Name of the main markdown file (without extension)
MD_SRC        := paper

# Bibliography file
BIBFILE       := refs.bib

# Pandoc wrapper template for the camera‑ready version
TEMPLATE_CR   := acm-pandoc.tex

# Pandoc wrapper template for the anonymous manuscript version
# (if the file does not exist the rule $(TEMPLATE_ANON) will create it)
TEMPLATE_ANON := acm-pandoc-anon.tex

# Lua filter that builds the author blocks
LUA_FILTER    := acm-authors.lua

# CSL file (installed in the Docker image)
CSL_PATH      := /usr/local/share/csl/acm.csl

# Docker image name
IMAGE_NAME    := acm-md

# Pandoc options common to both builds
PANDOC_OPTS   := \
    --pdf-engine=xelatex \
    --lua-filter=$(LUA_FILTER) \
    --citeproc \
    --csl=$(CSL_PATH) \
    --bibliography=$(BIBFILE) \
    -f markdown+raw_tex+raw_attribute \
    -V fontsize=10pt \
    -V linestretch=1.0

# ----------------------------------------------------------------------
# Primary targets
# ----------------------------------------------------------------------
.PHONY: all clean image pdf anon pdf-anon

all: pdf pdf-anon

# Build the Docker image (runs only if the image does not exist)
image:
    @docker build -t $(IMAGE_NAME) .

# ----------------------------------------------------------------------
# Camera‑ready PDF (class option sigconf)
# ----------------------------------------------------------------------
pdf: $(MD_SRC).pdf

$(MD_SRC).pdf: $(MD_SRC).md $(TEMPLATE_CR) $(LUA_FILTER) $(BIBFILE) image
    @docker run --rm \
        -v "$(CURDIR)":/data \
        $(IMAGE_NAME) \
        pandoc $(MD_SRC).md \
            $(PANDOC_OPTS) \
            --template=$(TEMPLATE_CR) \
            -o $(MD_SRC).pdf

# ----------------------------------------------------------------------
# Anonymous manuscript PDF (class option manuscript)
# ----------------------------------------------------------------------
pdf-anon: $(MD_SRC)-anon.pdf

$(MD_SRC)-anon.pdf: $(MD_SRC).md $(TEMPLATE_ANON) $(LUA_FILTER) $(BIBFILE) image
    @docker run --rm \
        -v "$(CURDIR)":/data \
        $(IMAGE_NAME) \
        pandoc $(MD_SRC).md \
            $(PANDOC_OPTS) \
            --template=$(TEMPLATE_ANON) \
            -o $(MD_SRC)-anon.pdf

# If the anonymous template file does not exist, create it by
# copying the regular template and swapping the class options.
$(TEMPLATE_ANON):
    @cp $(TEMPLATE_CR) $(TEMPLATE_ANON)
    @sed -i '' 's/\[sigconf,/[manuscript,/' $(TEMPLATE_ANON) || \
      sed -i 's/\[sigconf,/[manuscript,/' $(TEMPLATE_ANON)

# ----------------------------------------------------------------------
# Utility targets
# ----------------------------------------------------------------------
clean:
    @rm -f $(MD_SRC).pdf $(MD_SRC)-anon.pdf

# Remove the Docker image (use with care)
clean-image:
    @docker rmi $(IMAGE_NAME)

# ----------------------------------------------------------------------
# Help
# ----------------------------------------------------------------------
help:
    @echo "Makefile targets:"
    @echo "  all          – build both camera‑ready and anonymous PDFs"
    @echo "  pdf          – build only the camera‑ready PDF"
    @echo "  pdf-anon     – build only the anonymous PDF"
    @echo "  image        – (re)build the Docker image"
    @echo "  clean        – delete generated PDFs"
    @echo, "  clean-image  – delete the Docker image"
    @echo "  help         – print this message"
```

#### How the Build Process Works

The workflow uses Docker to create a consistent environment, ensuring the PDF looks the same regardless of the host OS.

1.  **Image Creation (`make image`)**: This builds the `acm-md` Docker image. It installs Pandoc, TeX Live, and the `acmart` class into a container. Because this is a separate build step, it only needs to be run once or when the `Dockerfile` changes.
2.  **Volume Mounting**: When the PDF is generated, the Makefile uses the `-v "$(CURDIR)":/data` flag. This "mounts" your current local folder into the container at `/data`. This allows the containerized Pandoc to read your `.md` and `.bib` files and write the final `.pdf` directly back to your local disk.
3.  **The Pandoc Pipeline**: The `make pdf` target executes a complex Pandoc command that:
    *   Uses `xelatex` for high-quality Unicode and font rendering.
    *   Applies the `acm-authors.lua` filter to transform YAML metadata into LaTeX author blocks.
    *   Invokes `citeproc` and the `acm.csl` file to format citations in the official ACM style.
    *   Utilizes the `acm-pandoc.tex` wrapper to ensure the output conforms to the `acmart` class layout.
4.  **Result**: The final output is a professional, camera-ready PDF produced without requiring any local LaTeX or Pandoc installation.

#### Typical Workflow

```bash
# 1. Build the Docker image (only needed once)
make image

# 2. Compile the camera-ready version
make pdf        # produces paper.pdf

# 3. Remove generated PDFs
make clean
```

For specific requirements like conference info or anonymous review, modify the class options or insert raw LaTeX blocks:

*   **Conference Info**: Insert `\acmConference{...}{...}{...}` as raw LaTeX.
*   **Anonymous Review**: Use the `manuscript` option in `\documentclass` in the template.
*   **Appendices**: Add a top-level `# Appendix` heading; Pandoc triggers the LaTeX `\appendix` command automatically.

## Summary Checklist

* [ ] Created the `Dockerfile` and built the `acm-md` image.
* [ ] Configured the `acm-pandoc.tex` wrapper and `acm-authors.lua` filter.
* [ ] Authored the manuscript with valid YAML front-matter and a `.bib` file.
* [ ] Successfully produced a PDF using `make pdf`.
* [ ] Verified that citations and bibliography conform to the ACM style.

## Assignments

!!! note "Assignment.1: Dockerized ACM Build"
    Create a minimal Markdown paper with a title, one author, and a short abstract. Set up the Docker environment and use a Makefile to produce a PDF that conforms to the ACM layout.

    ??? tip "Solution: Dockerized ACM Build"
        Ensure the `Dockerfile`, `acm-pandoc.tex`, and `acm-authors.lua` files are in your project root. Run `make image` followed by `make pdf`.

!!! note "Assignment.2: Citations and Bibliography"
    Add a bibliography file `refs.bib` with at least two entries. Insert citations into your Markdown paper using the `[@key]` syntax and verify that the final PDF generates a correctly formatted "References" section.

    ??? tip "Solution: Citations and Bibliography"
        Ensure the `--citeproc` and `--csl=acm.csl` flags are active in your Pandoc command (via the Makefile). Verify that the CSL file is correctly copied into the Docker image.

## References

* ACM Authoring Guide - <https://www.acm.org/publications/authors/reference-formatting>
* Pandoc Documentation - <https://pandoc.org/MANUAL.html>
* CSL Styles Repository - <https://github.com/citation-style-language/styles>

## Self-Evaluation

??? note "Why is a Docker container preferred over a local LaTeX installation for this workflow?"
    LaTeX distributions are massive and often have complex dependency chains. A Docker container provides a lightweight, reproducible environment that ensures every contributor uses the exact same version of Pandoc and the `acmart` class.

??? note "What is the primary advantage of using a Lua filter for author blocks?"
    The `acmart` class requires very specific LaTeX commands for each author attribute. A Lua filter allows authors to keep their metadata in a clean YAML list while automating the generation of the required LaTeX syntax.

??? note "How does the `--citeproc` flag interact with the CSL file?"
    `--citeproc` activates the citation processing engine. It uses the CSL (Citation Style Language) file to determine exactly how the in-text citations and the final bibliography should be formatted (e.g., numbering vs. author-date).
