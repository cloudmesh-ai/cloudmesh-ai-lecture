import os
import re

files = [
    "docs/index.md",
    "docs/lecture/assignments/overview.md",
    "docs/lecture/edge/edge.md",
    "docs/section/container/orchestration/openshift.md",
    "docs/section/ai/skit-learn/scikit-learn.md",
    "docs/section/linux/slides/github-talk.md",
    "docs/section/linux/ubuntu-cheatsheet.md",
    "docs/section/linux/slides/gh-talk.md",
    "docs/section/cloud/resources/slides/virtualization-talk.md",
    "docs/drafts/section/opencv/secchi.md",
    "docs/section/rest/rest.md",
    "docs/drafts/section/facedetection/facedetection.md",
    "docs/drafts/section/fingerprint/fingerprint.md",
    "docs/drafts/section/numpy/numpy.md",
    "docs/drafts/sections.md",
    "docs/drafts/section/dask/dask.md",
    "docs/drafts/section/opencv/opencv.md",
    "docs/drafts/section/scipy/scipy.md",
    "docs/drafts/section/cloudmesh/installation.md",
    "docs/drafts/section/random-forest/random-forest.md",
    "docs/drafts/section/cloudmesh/inventory.md",
    "docs/drafts/section/cloudmesh/stopwatch.md",
    "docs/drafts/section/deprecated/python-install-pyenv.md",
    "docs/drafts/section/cloudmesh/python-cloudmesh.md",
    "docs/drafts/section/deprecated/python-deprecated.md",
    "docs/drafts/section/cloudmesh/python-cmd5.md",
    "docs/drafts/section/cloudmesh/console.md",
    "docs/drafts/section/pandas/DataCleaning-Preparation.md",
    "docs/drafts/section/cloudmesh/shell.md",
    "docs/drafts/outdated/google-colab/python-google-colab.md"
]

for file_path in files:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match frontmatter block
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
            # Remove frontmatter and prepend # Title
            new_content = "# " + title + "\n\n" + content[match.end():].lstrip()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Converted {file_path}")

