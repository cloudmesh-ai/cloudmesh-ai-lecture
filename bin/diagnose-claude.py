#!/usr/bin/env python3
import os
from pathlib import Path

def check_claude_state():
    print("🔍 Diagnosing Claude Code extension session paths...\n")
    
    claude_dir = Path.home() / ".claude"
    projects_dir = claude_dir / "projects"
    
    if not claude_dir.exists():
        print(f"❌ The main directory {claude_dir} does not exist.")
        return

    print(f"✅ Found Claude directory: {claude_dir}")
    
    if projects_dir.exists():
        projects = list(projects_dir.iterdir())
        print(f"📁 Found {len(projects)} logged project session folders in ~/.claude/projects/:")
        for p in projects:
            print(f"   - {p.name}")
            # Check if the folder names contain paths that might no longer match current reality
    else:
        print("ℹ️ No projects directory found yet.")

    # Check current workspace vs common cache issues
    current_cwd = Path.cwd().resolve()
    print(f"\n📂 Your current working directory realpath is:\n   {current_cwd}")
    print("\n💡 Conclusion:")
    print("If you see old project folder names above that do not match your current path structure,")
    print("the VS Code extension sidebar is likely crashing trying to read those stale paths.")
    print("To fix this, run:")
    print("   rm -rf ~/.claude/projects/*")

if __name__ == "__main__":
    check_claude_state()
