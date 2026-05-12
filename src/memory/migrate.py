#!/usr/bin/env python3
"""
Migrate existing knowledge files to use the new schema.

This script:
1. Reads all existing writeups and patterns
2. Validates and normalizes their frontmatter
3. Rewrites them with proper schema compliance
4. Regenerates the index
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as standalone script
if __name__ == "__main__" or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.memory.schema import (
    WriteupFrontmatter,
    PatternFrontmatter,
    write_writeup,
    write_pattern,
    update_index,
    validate_all,
)
from src.tools.common.markdown import split_frontmatter


def migrate_writeup(path: Path) -> tuple[bool, list[str]]:
    """Migrate a single writeup file. Returns (success, errors)."""
    try:
        content = path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(content)

        # Normalize fields
        fm = WriteupFrontmatter(
            doc_kind="writeup",
            title=metadata.get("title", path.stem),
            category=metadata.get("category", "web"),
            slug=metadata.get("slug", path.stem),
            created=metadata.get("created", ""),
            status=metadata.get("status", "draft"),
            tags=metadata.get("tags", []),
            source=metadata.get("source", ""),
            target=metadata.get("target", ""),
        )

        errors = fm.validate()
        if errors:
            return False, errors

        # Rewrite with clean frontmatter
        write_writeup(path, fm, body)
        return True, []

    except Exception as e:
        return False, [str(e)]


def migrate_pattern(path: Path) -> tuple[bool, list[str]]:
    """Migrate a single pattern file. Returns (success, errors)."""
    try:
        content = path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(content)

        # Normalize fields
        fm = PatternFrontmatter(
            doc_kind="pattern",
            title=metadata.get("title", path.stem),
            category=metadata.get("category", "web"),
            slug=metadata.get("slug", path.stem),
            created=metadata.get("created", ""),
            status=metadata.get("status", "draft"),
            tags=metadata.get("tags", []),
            chain_summary=metadata.get("chain_summary", ""),
        )

        errors = fm.validate()
        if errors:
            return False, errors

        # Rewrite with clean frontmatter
        write_pattern(path, fm, body)
        return True, []

    except Exception as e:
        return False, [str(e)]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    knowledge = root / "knowledge"

    print("=== Migrating knowledge files ===\n")

    # Migrate writeups
    writeups_dir = knowledge / "writeups"
    if writeups_dir.exists():
        for md_file in writeups_dir.rglob("*.md"):
            if md_file.name == "index.md":
                continue
            success, errors = migrate_writeup(md_file)
            relpath = md_file.relative_to(root)
            if success:
                print(f"✓ {relpath}")
            else:
                print(f"✗ {relpath}: {errors}")

    # Migrate patterns
    patterns_dir = knowledge / "patterns"
    if patterns_dir.exists():
        for md_file in patterns_dir.rglob("*.md"):
            if md_file.name == "index.md":
                continue
            success, errors = migrate_pattern(md_file)
            relpath = md_file.relative_to(root)
            if success:
                print(f"✓ {relpath}")
            else:
                print(f"✗ {relpath}: {errors}")

    # Regenerate index
    print("\n=== Regenerating index ===")
    update_index(root)
    print("✓ knowledge/index.md")

    # Validate all
    print("\n=== Validation ===")
    errors = validate_all(root)
    if errors:
        print("Errors found:")
        for path, msgs in errors.items():
            print(f"  {path}: {msgs}")
        return 1
    else:
        print("All files valid ✓")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
