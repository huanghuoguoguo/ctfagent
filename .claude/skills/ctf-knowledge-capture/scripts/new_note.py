#!/usr/bin/env python3
import argparse
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ctfagent.markdown import dump_frontmatter


CATEGORIES = ["web", "pwn", "rev", "crypto", "misc", "forensics"]


def build_writeup(title: str, category: str, slug: str, created: str) -> str:
    frontmatter = dump_frontmatter(
        {
            "doc_kind": "writeup",
            "title": title,
            "category": category,
            "slug": slug,
            "created": created,
            "status": "draft",
            "tags": [],
        }
    )
    return f"""{frontmatter}
# {title}

## Challenge Summary

- Source:
- Target:
- Goal:

## Initial Signals

- Entry point:
- Visible hints:
- First confirming probe:

## Exploit Chain

1. 
2. 
3. 

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


def build_pattern(title: str, category: str, slug: str, created: str) -> str:
    frontmatter = dump_frontmatter(
        {
            "doc_kind": "pattern",
            "title": title,
            "category": category,
            "slug": slug,
            "created": created,
            "status": "draft",
            "tags": [],
        }
    )
    return f"""{frontmatter}
# {title}

## Chain Summary

- One-line chain:
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
3. 

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


def update_index(index_path: Path, relpath: str, title: str, kind: str, category: str) -> None:
    if not index_path.exists():
        index_path.write_text(
            "# Knowledge Index\n\n## Writeups\n\n## Patterns\n",
            encoding="utf-8",
        )

    content = index_path.read_text(encoding="utf-8")
    line = f"- [{title}]({relpath})\n"
    if line in content:
        return

    marker = "## Writeups\n" if kind == "writeup" else "## Patterns\n"
    insert = f"{line}"
    category_header = f"### {category}\n"

    if category_header not in content:
        content = content.replace(marker, marker + "\n" + category_header)

    pos = content.find(category_header)
    next_header = content.find("\n### ", pos + len(category_header))
    if next_header == -1:
        next_header = len(content)

    section = content[pos:next_header]
    if line not in section:
        section = section.rstrip() + "\n" + line
        content = content[:pos] + section + content[next_header:]

    index_path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a CTF knowledge note scaffold.")
    parser.add_argument("--root", required=True, help="Repository root")
    parser.add_argument("--kind", required=True, choices=["writeup", "pattern"])
    parser.add_argument("--category", required=True, choices=CATEGORIES)
    parser.add_argument("--slug", required=True, help="Stable file slug")
    parser.add_argument("--title", required=True, help="Document title")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    knowledge = root / "knowledge"
    subdir = "writeups" if args.kind == "writeup" else "patterns"
    note_dir = knowledge / subdir / args.category
    note_dir.mkdir(parents=True, exist_ok=True)

    path = note_dir / f"{args.slug}.md"
    created = dt.date.today().isoformat()
    if not path.exists():
        content = (
            build_writeup(args.title, args.category, args.slug, created)
            if args.kind == "writeup"
            else build_pattern(args.title, args.category, args.slug, created)
        )
        path.write_text(content, encoding="utf-8")

    relpath = path.relative_to(root).as_posix()
    update_index(knowledge / "index.md", relpath, args.title, args.kind, args.category)

    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
