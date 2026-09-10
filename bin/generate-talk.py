import argparse
import os
import subprocess
import sys
from pathlib import Path

def get_marp_themes():
    """Load Marp themes from mkdocs.yml."""
    try:
        import yaml
        config_path = Path("mkdocs.yml")
        if config_path.exists():
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config.get("marp_themes", [])
    except Exception as e:
        print(f"Warning: Could not load themes from mkdocs.yml: {e}", file=sys.stderr)
    return []


def main():
    parser = argparse.ArgumentParser(description="Convert Marp markdown slides to HTML if modified.")
    parser.add_argument("--in", dest="input_file", required=True, help="Input markdown file (e.g., NAME-talk.md)")
    parser.add_argument("--out", dest="output_file", required=True, help="Output HTML file (e.g., NAME-talk.html)")
    parser.add_argument("--force", action="store_true", help="Force regeneration of the HTML file")

    args = parser.parse_args()

    in_path = Path(args.input_file)
    out_path = Path(args.output_file)

    if not in_path.exists():
        print(f"Error: Input file {in_path} does not exist.", file=sys.stderr)
        sys.exit(1)

    # Check if we should generate the HTML
    should_generate = False
    if args.force:
        should_generate = True
    elif not out_path.exists():
        should_generate = True
    else:
        # Compare timestamps: if input file is newer than output file
        if in_path.stat().st_mtime > out_path.stat().st_mtime:
            should_generate = True

    if should_generate:
        print(f"[ INFO ] Converting {in_path} => {out_path}")
        try:
            # Prepare marp command with themes
            cmd = ["marp"]
            themes = get_marp_themes()
            for theme in themes:
                cmd.extend(["--theme", theme])
            cmd.extend(["--html", str(in_path), "-o", str(out_path)])
            
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during marp conversion: {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError:
            print("Error: 'marp' CLI not found. Please install it using 'npm install -g @marp-team/marp-cli'.", file=sys.stderr)
            sys.exit(1)
    else:
        # No output to avoid unnecessary logging unless requested
        pass

if __name__ == "__main__":
    main()
