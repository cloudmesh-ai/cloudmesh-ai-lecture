## Learning Objectives

!!! info "Learning Objectives"

    By the end of this chapter, you will be able to:
    - Programmatically fetch static resources from a web page.
    - Use Python to parse HTML and identify downloadable assets.
    - Normalize relative URLs to absolute paths for resource retrieval.
    - Rewrite HTML links to enable offline viewing of a web page.

## Overview

Below is a programmatic method to fetch everything that is directly reachable from `https://openclaw.ai/ecosystem` (the HTML page itself and the static resources it references such as images, CSS, JavaScript, PDFs, etc.).

## Programmatic Asset Retrieval

The script performs the following operations:

1. **Downloads the HTML** of the page.
2. **Parses the markup** to collect URLs of linked resources (`<img>`, `<link rel="stylesheet">`, `<script src>`, `<a href>` that point to files such as PDFs, PNGs, JPGs, etc.).
3. **Normalises relative URLs** to absolute URLs.
4. **Downloads each resource** into a local folder called `openclaw_ecosystem/`.
5. **Creates a small `index.html`** that references the downloaded assets so the page can be opened offline and rendered correctly.

This code can be run in any Python environment with internet access.

```python
import os, re, sys, json, hashlib
from urllib.parse import urljoin, urlparse, urldefrag
import requests
from bs4 import BeautifulSoup

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
BASE_URL = "https://openclaw.ai/ecosystem"
OUTPUT_DIR = "openclaw_ecosystem"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OpenClawDownloader/1.0)"}
# file extensions we consider "downloadable" assets
DOWNLOADABLE_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".css", ".js",
    ".pdf", ".doc", ".docx", ".xlsx", ".xls", ".ppt", ".pptx",
    ".mp4", ".webm", ".mp3", ".wav"
}

# ------------------------------------------------------------------
# Helper utilities
# ------------------------------------------------------------------
def safe_filename(url):
    """Create a reproducible, filesystem-safe filename from a URL."""
    url = urldefrag(url)[0]            # strip fragment
    parsed = urlparse(url)
    path = parsed.path
    if path.endswith("/"):
        path += "index.html"
    # keep the directory structure, but replace any unsafe chars with _
    safe_path = re.sub(r"[^\w\-.\\/]", "_", path.lstrip("/"))
    return os.path.join(OUTPUT_DIR, safe_path)

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def download_file(url, dest_path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        ensure_dir(dest_path)
        with open(dest_path, "wb") as f:
            f.write(r.content)
        print(f"✔ downloaded {url} → {dest_path}")
    except Exception as e:
        print(f"✘ failed {url}: {e}")

def is_downloadable(url):
    parsed = urlparse(url)
    _, ext = os.path.splitext(parsed.path.lower())
    return ext in DOWNLOADABLE_EXTS

# ------------------------------------------------------------------
# Step 1 – fetch the main HTML page
# ------------------------------------------------------------------
print(f"Fetching main page: {BASE_URL}")
resp = requests.get(BASE_URL, headers=HEADERS, timeout=30)
resp.raise_for_status()
html = resp.text

# Save the original HTML (will be rewritten later to point to local files)
main_path = os.path.join(OUTPUT_DIR, "index.html")
ensure_dir(main_path)
with open(main_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved original HTML to {main_path}")

# ------------------------------------------------------------------
# Step 2 – parse page and collect asset URLs
# ------------------------------------------------------------------
soup = BeautifulSoup(html, "html.parser")
asset_urls = set()

# Images
for img in soup.find_all("img", src=True):
    asset_urls.add(urljoin(BASE_URL, img["src"]))
# Stylesheets
for link in soup.find_all("link", href=True):
    if link.get("rel") and "stylesheet" in link["rel"]:
        asset_urls.add(urljoin(BASE_URL, link["href"]))
# Scripts
for script in soup.find_all("script", src=True):
    asset_urls.add(urljoin(BASE_URL, script["src"]))
# Explicit file links (e.g., PDFs, docs)
for a in soup.find_all("a", href=True):
    href = a["href"]
    full = urljoin(BASE_URL, href)
    if is_downloadable(full):
        asset_urls.add(full)

print(f"Found {len(asset_urls)} asset URLs to download.")

# ------------------------------------------------------------------
# Step 3 – download each asset
# ------------------------------------------------------------------
for url in sorted(asset_urls):
    local_path = safe_filename(url)
    # Skip if already downloaded
    if os.path.exists(local_path):
        print(f"✔ already exists: {local_path}")
        continue
    download_file(url, local_path)

# ------------------------------------------------------------------
# Step 4 – rewrite HTML to point to local copies
# ------------------------------------------------------------------
def local_ref(original_url):
    # Return the relative path from the output folder to the saved file
    local_path = safe_filename(original_url)
    rel_path = os.path.relpath(local_path, OUTPUT_DIR)
    return rel_path.replace("\\", "/")  # normalise for HTML

# Update tags in the soup
for img in soup.find_all("img", src=True):
    img["src"] = local_ref(urljoin(BASE_URL, img["src"]))
for link in soup.find_all("link", href=True):
    if link.get("rel") and "stylesheet" in link["rel"]:
        link["href"] = local_ref(urljoin(BASE_URL, link["href"]))
for script in soup.find_all("script", src=True):
    script["src"] = local_ref(urljoin(BASE_URL, script["src"]))
for a in soup.find_all("a", href=True):
    href = a["href"]
    full = urljoin(BASE_URL, href)
    if is_downloadable(full):
        a["href"] = local_ref(full)

# Write the rewritten HTML back (overwrites the original index.html)
with open(main_path, "w", encoding="utf-8") as f:
    f.write(str(soup))
print(f"\nAll assets downloaded. Open the offline page at: {main_path}")
```

### Execution Summary

| Step | Result |
|------|--------|
| **Fetch main page** | Saves the original HTML as `openclaw_ecosystem/index.html`. |
| **Collect assets** | Gathers every image, stylesheet, script, and direct file link (PDF, DOCX, etc.) that the page references. |
| **Download assets** | Stores each file under the same directory hierarchy as on the site (e.g., `openclaw_ecosystem/static/css/style.css`). |
| **Rewrite links** | Alters the saved `index.html` so that all `src`/`href` attributes now point to the locally-saved copies. |
| **Final output** | The `openclaw_ecosystem/index.html` file can be opened in any browser for offline viewing. |

### Implementation Steps

1. **Install required Python packages**:

   ```bash
   pip install requests beautifulsoup4
   ```

2. **Save the script** to a file, such as `download_openclaw_ecosystem.py`.

3. **Execute the script**:

   ```bash
   python download_openclaw_ecosystem.py
   ```

4. Navigate to the `openclaw_ecosystem` folder and open `index.html` in a browser.

## Technical Constraints

* **Robots & Terms of Service** - Verify that usage complies with OpenClaw terms of service and `robots.txt` rules.
* **Dynamic Content** - This downloader captures static assets linked in the HTML. Data loaded via client-side JavaScript APIs is not captured.
* **Rate Limiting** - For large-scale scraping, implement `time.sleep()` between requests to avoid server overload.
* **Authentication** - Links requiring login sessions or API tokens will result in 403/401 responses.

## Summary Checklist

- [ ] Python environment configured with `requests` and `beautifulsoup4`.
- [ ] Target URL defined in `BASE_URL`.
- [ ] Assets downloaded to local directory.
- [ ] HTML links rewritten to relative local paths.
- [ ] Offline page verified in browser.

## Assignments

!!! note "Assignment.1: Extend Asset Types"

    Modify the `DOWNLOADABLE_EXTS` set in the script to include additional file formats (e.g., `.zip`, `.tar.gz`) and verify that these files are correctly identified and downloaded.

??? tip "Solution: Extend Asset Types"
    Add the desired extensions to the `DOWNLOADABLE_EXTS` set:
    ```python
    DOWNLOADABLE_EXTS = {
        # ... existing extensions ...
        ".zip", ".tar.gz", ".7z"
    }
    ```

!!! note "Assignment.2: Implement Request Delay"

    To prevent server overload, add a 1-second delay between each file download using the `time` module.

??? tip "Solution: Implement Request Delay"
    Import the `time` module and add `time.sleep(1)` inside the download loop:
    ```python
    import time
    # ...
    for url in sorted(asset_urls):
        # ...
        download_file(url, local_path)
        time.sleep(1)
    ```

## References

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library Documentation](https://requests.readthedocs.io/)

## Self-Assessment
Test your knowledge by expanding the questions below.
??? question "How does the script handle relative URLs found in the HTML?"
    The script uses `urllib.parse.urljoin` to combine the `BASE_URL` with relative paths, converting them into absolute URLs before downloading.

??? question "What is the purpose of the `safe_filename` function?"
    It ensures that URLs are converted into valid filesystem paths by removing fragments, normalizing paths, and replacing unsafe characters with underscores.

??? question "Why are the HTML links rewritten after downloading assets?"
    The original HTML contains absolute URLs pointing to the live server. Rewriting them to relative paths ensures the page renders correctly when opened from the local filesystem without an internet connection.
