"""
Memory schema module for CTF knowledge storage.

Enforces structure on writeups and patterns. All memory operations must go through this module.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Any

# Allow running as standalone script
if __name__ == "__main__" or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.common.markdown import dump_frontmatter, split_frontmatter


class DocKind(str, Enum):
    WRITEUP = "writeup"
    PATTERN = "pattern"


class Status(str, Enum):
    DRAFT = "draft"
    SOLVED = "solved"
    ACTIVE = "active"
    ARCHIVED = "archived"


class Category(str, Enum):
    WEB = "web"
    PWN = "pwn"
    REV = "rev"
    CRYPTO = "crypto"
    MISC = "misc"
    FORENSICS = "forensics"


@dataclass
class WriteupFrontmatter:
    """Schema for writeup documents."""
    doc_kind: str = "writeup"
    title: str = ""
    category: str = ""
    slug: str = ""
    created: str = ""
    status: str = "draft"
    tags: list[str] = field(default_factory=list)
    source: str = ""  # CTF platform or lab source
    target: str = ""  # Target URL or binary path

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []
        if not self.title:
            errors.append("title is required")
        if not self.category:
            errors.append("category is required")
        elif self.category not in [c.value for c in Category]:
            errors.append(f"invalid category: {self.category}")
        if not self.slug:
            errors.append("slug is required")
        if self.status not in [s.value for s in Status]:
            errors.append(f"invalid status: {self.status}")
        return errors


@dataclass
class PatternFrontmatter:
    """Schema for pattern documents."""
    doc_kind: str = "pattern"
    title: str = ""
    category: str = ""
    slug: str = ""
    created: str = ""
    status: str = "draft"
    tags: list[str] = field(default_factory=list)
    chain_summary: str = ""  # One-line description of the attack chain

    def validate(self) -> list[str]:
        """Return list of validation errors."""
        errors = []
        if not self.title:
            errors.append("title is required")
        if not self.category:
            errors.append("category is required")
        elif self.category not in [c.value for c in Category]:
            errors.append(f"invalid category: {self.category}")
        if not self.slug:
            errors.append("slug is required")
        if self.status not in [s.value for s in Status]:
            errors.append(f"invalid status: {self.status}")
        return errors


def parse_writeup(path: Path) -> tuple[WriteupFrontmatter, str, list[str]]:
    """Parse a writeup file and return frontmatter, body, and validation errors."""
    metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))

    fm = WriteupFrontmatter(
        doc_kind=metadata.get("doc_kind", "writeup"),
        title=metadata.get("title", ""),
        category=metadata.get("category", ""),
        slug=metadata.get("slug", path.stem),
        created=metadata.get("created", ""),
        status=metadata.get("status", "draft"),
        tags=metadata.get("tags", []),
        source=metadata.get("source", ""),
        target=metadata.get("target", ""),
    )

    errors = fm.validate()
    return fm, body, errors


def parse_pattern(path: Path) -> tuple[PatternFrontmatter, str, list[str]]:
    """Parse a pattern file and return frontmatter, body, and validation errors."""
    metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))

    fm = PatternFrontmatter(
        doc_kind=metadata.get("doc_kind", "pattern"),
        title=metadata.get("title", ""),
        category=metadata.get("category", ""),
        slug=metadata.get("slug", path.stem),
        created=metadata.get("created", ""),
        status=metadata.get("status", "draft"),
        tags=metadata.get("tags", []),
        chain_summary=metadata.get("chain_summary", ""),
    )

    errors = fm.validate()
    return fm, body, errors


def write_writeup(path: Path, fm: WriteupFrontmatter, body: str) -> None:
    """Write a writeup file with validated frontmatter."""
    errors = fm.validate()
    if errors:
        raise ValueError(f"Validation errors: {errors}")

    data = {k: v for k, v in asdict(fm).items() if v}
    content = dump_frontmatter(data) + "\n" + body
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_pattern(path: Path, fm: PatternFrontmatter, body: str) -> None:
    """Write a pattern file with validated frontmatter."""
    errors = fm.validate()
    if errors:
        raise ValueError(f"Validation errors: {errors}")

    data = {k: v for k, v in asdict(fm).items() if v}
    content = dump_frontmatter(data) + "\n" + body
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- Body Templates ---

WRITEUP_TEMPLATE = """# {title}

## Challenge Summary

- Source: {source}
- Target: {target}
- Goal:

## Initial Signals

- Entry point:
- Visible hints:
- First confirming probe:

## Exploit Chain

1.
2.

## Key Evidence

-

## Dead Ends

-

## Payloads And Commands

```bash
```

## Flag / Outcome

-

## Reusable Lessons

-

## Pattern Candidates

- Existing pattern to update:
- New pattern worth creating:
"""

PATTERN_TEMPLATE = """# {title}

## Chain Summary

- One-line chain: {chain_summary}
- Typical target shape:

## Preconditions

-

## Cheap Probes

-

## Telltale Evidence

-

## Escalation Order

1.
2.

## Common Mistakes

-

## Payload Shapes

```text
```

## Related Writeups

-

## Skill Impact

- Related skill:
- Rule to add or update:
"""


def create_writeup(
    root: Path,
    title: str,
    category: str,
    slug: str,
    source: str = "",
    target: str = "",
    tags: list[str] | None = None,
    status: str = "draft",
) -> Path:
    """Create a new writeup with proper schema."""
    knowledge = root / "knowledge" / "writeups" / category
    path = knowledge / f"{slug}.md"

    if path.exists():
        return path

    fm = WriteupFrontmatter(
        doc_kind="writeup",
        title=title,
        category=category,
        slug=slug,
        created=date.today().isoformat(),
        status=status,
        tags=tags or [],
        source=source,
        target=target,
    )

    body = WRITEUP_TEMPLATE.format(
        title=title,
        source=source,
        target=target,
    )

    write_writeup(path, fm, body)
    return path


def create_pattern(
    root: Path,
    title: str,
    category: str,
    slug: str,
    chain_summary: str = "",
    tags: list[str] | None = None,
    status: str = "draft",
) -> Path:
    """Create a new pattern with proper schema."""
    knowledge = root / "knowledge" / "patterns" / category
    path = knowledge / f"{slug}.md"

    if path.exists():
        return path

    fm = PatternFrontmatter(
        doc_kind="pattern",
        title=title,
        category=category,
        slug=slug,
        created=date.today().isoformat(),
        status=status,
        tags=tags or [],
        chain_summary=chain_summary,
    )

    body = PATTERN_TEMPLATE.format(
        title=title,
        chain_summary=chain_summary,
    )

    write_pattern(path, fm, body)
    return path


def update_index(root: Path) -> None:
    """Regenerate the knowledge index from existing files."""
    knowledge = root / "knowledge"
    index_path = knowledge / "index.md"

    writeups_by_category: dict[str, list[tuple[str, str]]] = {}
    patterns_by_category: dict[str, list[tuple[str, str]]] = {}

    # Scan writeups
    writeups_dir = knowledge / "writeups"
    if writeups_dir.exists():
        for cat_dir in writeups_dir.iterdir():
            if cat_dir.is_dir():
                for md_file in sorted(cat_dir.glob("*.md")):
                    fm, _, errors = parse_writeup(md_file)
                    if not errors:
                        relpath = md_file.relative_to(root).as_posix()
                        writeups_by_category.setdefault(cat_dir.name, []).append(
                            (fm.title, relpath)
                        )

    # Scan patterns
    patterns_dir = knowledge / "patterns"
    if patterns_dir.exists():
        for cat_dir in patterns_dir.iterdir():
            if cat_dir.is_dir():
                for md_file in sorted(cat_dir.glob("*.md")):
                    fm, _, errors = parse_pattern(md_file)
                    if not errors:
                        relpath = md_file.relative_to(root).as_posix()
                        patterns_by_category.setdefault(cat_dir.name, []).append(
                            (fm.title, relpath)
                        )

    # Build index
    lines = ["# Knowledge Index\n"]

    lines.append("## Writeups\n")
    for category in sorted(writeups_by_category.keys()):
        lines.append(f"\n### {category}\n")
        for title, relpath in writeups_by_category[category]:
            lines.append(f"- [{title}]({relpath})\n")

    lines.append("\n## Patterns\n")
    for category in sorted(patterns_by_category.keys()):
        lines.append(f"\n### {category}\n")
        for title, relpath in patterns_by_category[category]:
            lines.append(f"- [{title}]({relpath})\n")

    index_path.write_text("".join(lines), encoding="utf-8")


def validate_all(root: Path) -> dict[str, list[str]]:
    """Validate all knowledge files. Return dict of path -> errors."""
    errors: dict[str, list[str]] = {}
    knowledge = root / "knowledge"

    for kind in ["writeups", "patterns"]:
        kind_dir = knowledge / kind
        if not kind_dir.exists():
            continue

        for md_file in kind_dir.rglob("*.md"):
            if md_file.name == "index.md":
                continue

            if kind == "writeups":
                _, _, file_errors = parse_writeup(md_file)
            else:
                _, _, file_errors = parse_pattern(md_file)

            if file_errors:
                errors[str(md_file.relative_to(root))] = file_errors

    return errors
