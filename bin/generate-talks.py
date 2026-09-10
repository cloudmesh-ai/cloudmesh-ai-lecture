import os
import subprocess
import sys
import argparse
from pathlib import Path

def get_marp_themes():
    """Load Marp themes from mkdocs.yml."""
    try:
        import yaml
        config_path = Path("mkdocs.yml")
        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.unsafe_load(f)
                return config.get("marp_themes", [])
    except Exception as e:
        print(f"Warning: Could not load themes from mkdocs.yml: {e}", file=sys.stderr)
    return []


def convert_slide(in_path, out_path, force=False):
    """Converts a single Marp markdown file to HTML if modified or forced."""
    should_generate = False
    if force:
        should_generate = True
    elif not out_path.exists():
        should_generate = True
    else:
        if in_path.stat().st_mtime > out_path.stat().st_mtime:
            should_generate = True

    # ANSI escape codes for colors
    DARK_GREEN = "\033[32m"
    DARK_BLUE = "\033[34m"
    RESET = "\033[0m"

    if should_generate:
        try:
            # Ensure output directory exists (though it should be the same as in_path.parent)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare marp command with themes
            cmd = ["marp"]
            themes = get_marp_themes()
            for theme in themes:
                cmd.extend(["--theme", theme])
            cmd.extend(["--html", str(in_path), "-o", str(out_path)])
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Post-process: Remove Marpit fragments to prevent incremental reveal
            # This ensures slides advance in a single click regardless of auto-fragmentation
            html_content = out_path.read_text(encoding="utf-8")
            import re
            # Remove data-marpit-fragment="X"
            html_content = re.sub(r'\sdata-marpit-fragment="[^"]*"', '', html_content)
            # Remove data-marpit-fragments="X"
            html_content = re.sub(r'\sdata-marpit-fragments="[^"]*"', '', html_content)

            # Restore visible instructor notes: convert hidden bespoke-marp-note to visible instructor-notes
            # Move speaker notes inside the slides to make them visible as overlays
            notes = re.findall(r'<div class="bespoke-marp-note"[^>]*>(.*?)</div>', html_content, flags=re.DOTALL)
            html_content = re.sub(r'<div class="bespoke-marp-note"[^>]*>.*?</div>', '', html_content, flags=re.DOTALL)
            
            slide_count = 0
            def insert_note(match):
                nonlocal slide_count
                if slide_count < len(notes):
                    note_content = notes[slide_count]
                    slide_count += 1
                    return f'<div class="instructor-notes">{note_content}</div></section>'
                return match.group(0)

            html_content = re.sub(r'</section>', insert_note, html_content)

            out_path.write_text(html_content, encoding="utf-8")

            print(f"{DARK_GREEN}[+] {in_path}: new slides generated: {out_path}{RESET}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error converting {in_path}: {e.stderr.decode()}", file=sys.stderr)
            return False
        except FileNotFoundError:
            print("Error: 'marp' CLI not found. Please install it using 'npm install -g @marp-team/marp-cli'.", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"{DARK_BLUE}[-] {in_path}: html up to date{RESET}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Marp HTML slides from markdown.")
    parser.add_argument("--force", action="store_true", help="Force regeneration of all slides")
    args = parser.parse_args()

    # Search for all *-talk.md files in the docs directory
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("Error: 'docs' directory not found.", file=sys.stderr)
        sys.exit(1)

    # Find all files matching the pattern recursively
    talk_files = list(docs_dir.rglob("*-talk.md"))
    
    if not talk_files:
        print("No *-talk.md files found in docs directory.")
        return

    if args.force:
        print(f"Force regenerating {len(talk_files)} slide files...")
    else:
        print(f"Found {len(talk_files)} slide files. Checking for updates...")
    
    for md_file in talk_files:
        # The HTML file should be in the same directory as the source .md file
        html_file = md_file.with_suffix(".html")
        convert_slide(md_file, html_file, force=args.force)

if __name__ == "__main__":
    main()
