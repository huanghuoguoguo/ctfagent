#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit whether a proposed new skill is mature enough to avoid uncontrolled skill growth."
    )
    parser.add_argument("--candidate-skill", help="Candidate skill name under review")
    parser.add_argument("--frequency", type=int, default=1, help="How many times the pattern has appeared")
    parser.add_argument(
        "--overlap",
        action="append",
        default=[],
        help="Existing skill that already overlaps the proposal. Repeat for multiple skills.",
    )
    parser.add_argument(
        "--duplicate-concept",
        action="append",
        default=[],
        help="Existing roadmap or backlog concept that makes this proposal redundant. Repeat for multiple entries.",
    )
    parser.add_argument("--scope-stable", action="store_true", help="The proposed boundary is narrow and stable.")
    parser.add_argument("--has-script", action="store_true", help="A thin helper script already exists.")
    parser.add_argument("--has-test", action="store_true", help="A lightweight regression test already exists.")
    parser.add_argument("--has-target", action="store_true", help="A minimal local lab or fixture already exists.")
    parser.add_argument("--doc-sync", action="store_true", help="CLAUDE.md and docs are already planned for sync.")
    return parser.parse_args()


def audit_growth(
    *,
    candidate_skill: str | None,
    frequency: int,
    overlaps: list[str],
    duplicate_concepts: list[str],
    scope_stable: bool,
    has_script: bool,
    has_test: bool,
    has_target: bool,
    doc_sync: bool,
) -> dict[str, object]:
    issues: list[str] = []
    actions: list[str] = []
    rationale: list[str] = []

    if overlaps:
        issues.append(f"proposal overlaps existing skill ownership: {', '.join(overlaps)}")
        actions.extend(f"update {skill}/SKILL.md instead of creating a new directory" for skill in overlaps)
        rationale.append("Existing skill ownership must be exhausted before the tree grows.")
        return {
            "classification": "prefer_update",
            "issues": issues,
            "required_actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Overlapping ownership blocks new-skill creation.",
        }

    if duplicate_concepts:
        issues.append(f"proposal duplicates an existing roadmap/backlog concept: {', '.join(duplicate_concepts)}")
        actions.append("merge the idea into the existing roadmap item or backlog entry")
        rationale.append("Duplicated concepts increase naming noise without adding capability.")
        return {
            "classification": "backlog_only",
            "issues": issues,
            "required_actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Do not promote a proposal that already exists under another name.",
        }

    if frequency < 2:
        issues.append(f"pattern seen only {frequency} time(s)")
        actions.append("record the lesson in knowledge/skill-backlog.md until the pattern repeats")
        rationale.append("A single appearance is not enough evidence for a permanent structural upgrade.")
        return {
            "classification": "backlog_only",
            "issues": issues,
            "required_actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "New skills require repeated evidence.",
        }

    if not scope_stable:
        issues.append("skill boundary is still vague or unstable")
        actions.append("collect more solves or failed attempts and tighten the ownership boundary")
        rationale.append("Unstable boundaries create skills that keep absorbing unrelated future work.")
        return {
            "classification": "backlog_only",
            "issues": issues,
            "required_actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Unclear scope must mature before it becomes a directory.",
        }

    missing_support: list[str] = []
    if not has_script:
        missing_support.append("thin helper script")
    if not has_test:
        missing_support.append("lightweight regression test")
    if not has_target:
        missing_support.append("minimal local lab or fixture")
    if not doc_sync:
        missing_support.append("doc sync for CLAUDE.md, docs/skills.md, and docs/roadmap.md")

    if missing_support:
        issues.extend(f"missing {item}" for item in missing_support)
        if not has_script:
            actions.append("add at least one thin helper script")
        if not has_test:
            actions.append("add at least one lightweight regression test")
        if not has_target:
            actions.append("add at least one minimal local lab or fixture")
        if not doc_sync:
            actions.append("sync CLAUDE.md, docs/skills.md, and docs/roadmap.md")
        rationale.append("Support artifacts must exist before a new skill is allowed to persist.")
        return {
            "classification": "block_new_skill",
            "issues": issues,
            "required_actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "A prose-only skill proposal is blocked.",
        }

    actions.append(f"create {candidate_skill or '<candidate-skill>'}/SKILL.md")
    actions.append("keep the first iteration narrow and link the supporting script, lab, and test")
    rationale.append("The proposal is repeated, owns a stable boundary, and has the minimum support to stay controlled.")
    return {
        "classification": "allow_new_skill",
        "issues": issues,
        "required_actions": actions,
        "rationale": rationale,
        "anti_entropy_guard": "New-skill growth is permitted only after the guard checks passed.",
    }


def main() -> int:
    args = parse_args()
    result = audit_growth(
        candidate_skill=args.candidate_skill,
        frequency=args.frequency,
        overlaps=args.overlap,
        duplicate_concepts=args.duplicate_concept,
        scope_stable=args.scope_stable,
        has_script=args.has_script,
        has_test=args.has_test,
        has_target=args.has_target,
        doc_sync=args.doc_sync,
    )
    result["inputs"] = {
        "candidate_skill": args.candidate_skill,
        "frequency": args.frequency,
        "overlaps": args.overlap,
        "duplicate_concepts": args.duplicate_concept,
        "scope_stable": args.scope_stable,
        "has_script": args.has_script,
        "has_test": args.has_test,
        "has_target": args.has_target,
        "doc_sync": args.doc_sync,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["classification"] != "block_new_skill" else 1


if __name__ == "__main__":
    raise SystemExit(main())
