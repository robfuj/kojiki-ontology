#!/usr/bin/env python3
"""Replace per-bot schema/prompt directories with symlinks to shared."""

import sys
from pathlib import Path

BASE = Path("/Users/Fujita/Documents/AI Filing System/decision-systems")
SHARED_SCHEMAS = BASE / "shared" / "schemas"
SHARED_PROMPTS = BASE / "shared" / "prompts"

# Find all bot directories
bot_dirs = []
for dept_dir in BASE.iterdir():
    if dept_dir.is_dir() and not dept_dir.name.startswith('.') and not dept_dir.name == 'shared':
        bots_dir = dept_dir / "bots"
        if bots_dir.exists():
            for bot_dir in bots_dir.iterdir():
                if bot_dir.is_dir():
                    bot_dirs.append(bot_dir)

print(f"Found {len(bot_dirs)} bot directories")

for bot_dir in bot_dirs:
    # Handle schema directory
    schema_dir = bot_dir / "schema"
    if schema_dir.exists():
        # Remove existing schema directory
        import shutil
        shutil.rmtree(schema_dir)
    
    # Create symlink to shared schemas
    schema_dir.symlink_to(SHARED_SCHEMAS)
    print(f"  ✅ {bot_dir.relative_to(BASE)}/schema -> shared/schemas")
    
    # Handle pipeline directory
    pipeline_dir = bot_dir / "pipeline"
    if pipeline_dir.exists():
        shutil.rmtree(pipeline_dir)
    
    pipeline_dir.symlink_to(SHARED_PROMPTS)
    print(f"  ✅ {bot_dir.relative_to(BASE)}/pipeline -> shared/prompts")

print("\nDone!")