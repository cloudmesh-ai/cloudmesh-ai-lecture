import re
import os
from pathlib import Path

def on_page_markdown(markdown, page, config, files):
    """
    Automatically injects a 'View Presentation Slides' button if a corresponding 
    -talk.md file exists for the current page.
    Links directly to the Marp-generated HTML file using a site-root relative path.
    """
    # 1. Ignore the talk pages themselves to avoid recursive buttons
    if page.file.src_path.endswith("-talk.md"):
        return markdown

    # 2. Construct the paths
    p = Path(page.file.src_path)
    # Look for the talk markdown file in the 'slides' subdirectory relative to the page
    # e.g., 'section/linux/index.md' -> 'section/linux/slides/index-talk.md'
    talk_md_rel_path = p.parent / "slides" / f"{p.stem}-talk.md"
    talk_md_path_str = str(talk_md_rel_path)

    # 3. Check if the talk file actually exists (either in files collection or on disk)
    docs_dir = config.get('docs_dir', 'docs')
    full_talk_md_path = Path(docs_dir) / talk_md_rel_path
    
    if talk_md_path_str in files or full_talk_md_path.exists():
        # Use the full path relative to the site root to avoid issues with MkDocs directory URLs
        # e.g., 'section/linux/gh-talk.md' -> '/section/linux/slides/gh-talk.html'
        talk_html_path = str(p.parent / "slides" / f"{p.stem}-talk.html")
        if not talk_html_path.startswith('/'):
            talk_html_path = '/' + talk_html_path
        
        # Use raw HTML for the button since 'pymdownx.attr' is disabled.
        # Updated to use a light grey background, smaller font, and a black FontAwesome icon.
        # Use actual newlines for markdown formatting
        button_snippet = f'\n\n<a id="presentation-button" href="{talk_html_path}" class="md-button" style="text-decoration: none; display: inline-flex; align-items: center; gap: 8px; background-color: #e0e0e0; color: #333; font-size: 0.85em; padding: 4px 12px; border-radius: 4px;"> <i class="fa-solid fa-person-chalkboard" style="color: black;"></i> View Presentation Slides</a>\n\n'
        
        # 4. Inject after the first H1 header (# Title)
        pattern = r'^(#\s+.+)$'
        
        new_markdown = re.sub(
            pattern, 
            rf'\1{button_snippet}', 
            markdown, 
            count=1, 
            flags=re.MULTILINE
        )
        return new_markdown

    return markdown

