from pathlib import Path
import os

docs_dir = 'docs'
src_path = 'section/linux/github.md'
p = Path(src_path)
talk_md_rel_path = p.parent / "slides" / f"{p.stem}-talk.md"
full_talk_md_path = Path(docs_dir) / talk_md_rel_path

print(f"Source: {src_path}")
print(f"Rel Path: {talk_md_rel_path}")
print(f"Full Path: {full_talk_md_path}")
print(f"Exists: {full_talk_md_path.exists()}")
