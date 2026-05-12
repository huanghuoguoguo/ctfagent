#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check skill inventory drift and duplicate roadmap entries.")
    parser.add_argument("--root", default=".", help="Repository root")
    return parser.parse_args()


def parse_readme_count(readme_text: str) -> int | None:
    match = re.search(r"当前已实现 \*\*(\d+) 个核心 skill\*\*", readme_text)
    return int(match.group(1)) if match else None


def parse_claude_active_skills(claude_text: str) -> list[str]:
    skills: list[str] = []
    active_section = False
    for line in claude_text.splitlines():
        if line.strip() == "## Active Skills":
            active_section = True
            continue
        if active_section and line.startswith("## "):
            break
        if active_section:
            match = re.match(r"\d+\.\s+`([^`]+?)/`", line.strip())
            if match:
                skills.append(match.group(1))
    return skills


def parse_roadmap_priorities(claude_text: str) -> list[str]:
    priorities: list[str] = []
    roadmap_section = False
    for line in claude_text.splitlines():
        if line.strip() == "## Roadmap":
            roadmap_section = True
            continue
        if roadmap_section and line.startswith("## "):
            break
        if roadmap_section:
            match = re.match(r"\d+\.\s+`([^`]+)`", line.strip())
            if match:
                priorities.append(match.group(1))
    return priorities


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    skill_names = sorted(path.parent.name for path in (root / ".claude" / "skills").glob("*/SKILL.md"))
    readme_text = (root / "README.md").read_text(encoding="utf-8")
    claude_text = (root / "CLAUDE.md").read_text(encoding="utf-8")

    readme_count = parse_readme_count(readme_text)
    claude_active = parse_claude_active_skills(claude_text)
    roadmap_priorities = parse_roadmap_priorities(claude_text)

    errors: list[str] = []
    warnings: list[str] = []

    if readme_count is not None and readme_count != len(skill_names):
        errors.append(f"README skill count says {readme_count}, but repo has {len(skill_names)} skill directories.")

    missing_from_claude = sorted(set(skill_names) - set(claude_active))
    extra_in_claude = sorted(set(claude_active) - set(skill_names))
    if missing_from_claude:
        errors.append(f"Skills missing from CLAUDE.md active list: {', '.join(missing_from_claude)}")
    if extra_in_claude:
        errors.append(f"CLAUDE.md references non-existent active skills: {', '.join(extra_in_claude)}")

    duplicate_priorities = sorted({name for name in roadmap_priorities if roadmap_priorities.count(name) > 1})
    if duplicate_priorities:
        warnings.append(f"Duplicate roadmap priorities in CLAUDE.md: {', '.join(duplicate_priorities)}")

    result = {
        "root": str(root),
        "skill_count": len(skill_names),
        "skills": skill_names,
        "readme_count": readme_count,
        "claude_active": claude_active,
        "roadmap_priorities": roadmap_priorities,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
