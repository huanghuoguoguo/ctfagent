#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ctfagent.markdown import dump_frontmatter


def infer_doc_kind(path: Path) -> str:
    parts = set(path.parts)
    if "writeups" in parts:
        return "writeup"
    if "patterns" in parts:
        return "pattern"
    if path.name == "challenge.md":
        return "challenge"
    if path.name == "notes.md":
        return "workspace-notes"
    return "note"


def parse_legacy_header(text: str) -> tuple[dict[str, object], str] | None:
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# "):
        return None

    title = lines[0][2:].strip()
    metadata: dict[str, object] = {"title": title}
    idx = 1
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    legacy_fields: dict[str, str] = {}
    while idx < len(lines):
        line = lines[idx]
        if not line.startswith("- "):
            break
        match = re.match(r"- ([A-Za-z ]+):\s*(.*)", line)
        if not match:
            break
        key = match.group(1).strip().lower().replace(" ", "_")
        legacy_fields[key] = match.group(2).strip()
        idx += 1

    metadata["category"] = legacy_fields.get("category", "")
    metadata["slug"] = legacy_fields.get("slug", "")
    metadata["created"] = legacy_fields.get("created", "")
    metadata["status"] = legacy_fields.get("status", "")
    tag_value = legacy_fields.get("tags", "")
    metadata["tags"] = [item.strip() for item in tag_value.split(",") if item.strip()]

    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    body = "\n".join([lines[0], ""] + lines[idx:]).rstrip() + "\n"
    return metadata, body


def migrate_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        return False
    parsed = parse_legacy_header(text)
    if parsed is None:
        return False
    metadata, body = parsed
    metadata["doc_kind"] = infer_doc_kind(path)
    path.write_text(dump_frontmatter(metadata) + "\n" + body, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for base in [ROOT / "knowledge", ROOT / "workspaces"]:
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            if path.name == "index.md":
                continue
            if migrate_file(path):
                changed += 1
                print(path)
    print(f"migrated={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
