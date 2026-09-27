#!/usr/bin/env python3
import re
from pathlib import Path

def display_masked_settings():
    settings_path = Path.home() / ".claude" / "settings.json"
    
    if not settings_path.exists():
        print(f"❌ Settings file not found at: {settings_path}")
        return
        
    content = settings_path.read_text(encoding="utf-8")
    
    # 1. Mask any sk-... API keys anywhere in the text
    content_masked = re.sub(r'sk-[a-zA-Z0-9\-_]+', 'sk-[REDACTED]', content)
    
    # 2. Mask explicit key/token/password values assigned in JSON strings
    content_masked = re.sub(
        r'("(?:token|key|secret|password|auth)"\s*:\s*")[^"]+(")',
        r'\1[REDACTED]\2',
        content_masked,
        flags=re.IGNORECASE
    )
    
    print(f"📄 Masked view of: {settings_path}\n")
    print(content_masked)

if __name__ == "__main__":
    display_masked_settings()