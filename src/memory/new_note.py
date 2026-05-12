#!/usr/bin/env python3
"""
Create new knowledge notes using the schema module.

This is the ONLY valid way to create new writeups and patterns.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running as standalone script
if __name__ == "__main__" or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.memory.schema import (
    create_writeup,
    create_pattern,
    update_index,
    Category,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a CTF knowledge note scaffold. This is the ONLY valid way to create notes."
    )
    parser.add_argument("--root", required=True, help="Repository root")
    parser.add_argument("--kind", required=True, choices=["writeup", "pattern"])
    parser.add_argument("--category", required=True, choices=[c.value for c in Category])
    parser.add_argument("--slug", required=True, help="Stable file slug")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--status", default="draft", choices=["draft", "solved", "active", "archived"])
    parser.add_argument("--tag", action="append", default=[], help="Tag (can repeat)")
    # Writeup-specific
    parser.add_argument("--source", default="", help="CTF platform or lab source (writeup only)")
    parser.add_argument("--target", default="", help="Target URL or binary path (writeup only)")
    # Pattern-specific
    parser.add_argument("--chain-summary", default="", help="One-line chain description (pattern only)")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.kind == "writeup":
        path = create_writeup(
            root=root,
            title=args.title,
            category=args.category,
            slug=args.slug,
            source=args.source,
            target=args.target,
            tags=args.tag,
            status=args.status,
        )
    else:
        path = create_pattern(
            root=root,
            title=args.title,
            category=args.category,
            slug=args.slug,
            chain_summary=args.chain_summary,
            tags=args.tag,
            status=args.status,
        )

    # Regenerate index
    update_index(root)

    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
