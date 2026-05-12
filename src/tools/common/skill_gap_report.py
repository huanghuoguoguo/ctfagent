#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify skill-system feedback into the smallest safe upgrade.")
    parser.add_argument(
        "--signal",
        action="append",
        default=[],
        choices=[
            "repeated_manual_step",
            "missing_probe_order",
            "missing_script",
            "missing_lab",
            "missing_test",
            "repeated_pattern",
            "overlap_existing_skill",
            "doc_drift",
            "one_off_insight",
        ],
        help="Observed feedback signal. Repeat this flag for multiple signals.",
    )
    parser.add_argument("--existing-skill", help="Existing skill that likely owns the gap")
    parser.add_argument("--candidate-skill", help="Candidate new skill name if a new skill is being considered")
    parser.add_argument("--category", help="Challenge category such as web/pwn/rev/crypto")
    parser.add_argument("--frequency", type=int, default=1, help="How many times this pattern has appeared")
    return parser.parse_args()


def classify_gap(
    signals: set[str],
    frequency: int,
    existing_skill: str | None,
    candidate_skill: str | None,
) -> dict[str, object]:
    actions: list[str] = []
    rationale: list[str] = []

    if "doc_drift" in signals:
        actions.extend(["sync README.md", "sync CLAUDE.md", "sync docs/skills.md", "sync docs/roadmap.md"])
        if existing_skill:
            actions.insert(0, f"update {existing_skill}/SKILL.md if behavior changed")
        rationale.append("Documentation drift is a maintenance failure, not a reason for a new skill.")
        return {
            "classification": "update_skill" if existing_skill else "backlog_only",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Do not create a new skill just to explain stale docs.",
        }

    if existing_skill and "overlap_existing_skill" in signals:
        actions.append(f"update {existing_skill}/SKILL.md")
        rationale.append("The gap overlaps an existing skill, so update that skill before proposing a new one.")
        if "missing_script" in signals:
            actions.append("add or extend a thin helper script")
        if "missing_test" in signals:
            actions.append("add a lightweight regression test")
        if "missing_lab" in signals:
            actions.append("add or extend a local lab/fixture")
        return {
            "classification": "update_skill",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Existing-skill overlap blocks new-skill creation.",
        }

    if "missing_script" in signals:
        actions.append("add a thin helper script")
        rationale.append("Repeated manual work should become a script before it becomes a new skill.")
        if existing_skill:
            actions.append(f"link the script from {existing_skill}/SKILL.md")
        if "missing_test" in signals:
            actions.append("add a script-level regression test")
        return {
            "classification": "new_script",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "One repeated command shape is not enough to justify a new skill.",
        }

    if "missing_test" in signals:
        actions.append("add a lightweight regression test")
        rationale.append("The capability exists, but its behavior is not being protected against drift.")
        return {
            "classification": "new_test",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Add the smallest test first instead of growing the skill tree.",
        }

    if "missing_lab" in signals:
        actions.append("add a minimal local lab or fixture")
        rationale.append("A skill without a replayable target will drift and should not expand first.")
        return {
            "classification": "new_target",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "Build the target before adding more written SOP.",
        }

    if "one_off_insight" in signals and frequency <= 1:
        actions.append("record the lesson in knowledge/skill-backlog.md or a pattern note")
        rationale.append("Single-use insights should not become a permanent skill immediately.")
        return {
            "classification": "backlog_only",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "One-off observations must mature before they change the skill inventory.",
        }

    if "repeated_pattern" in signals and frequency >= 2:
        if existing_skill:
            actions.append(f"update {existing_skill}/SKILL.md")
            rationale.append("The pattern repeats, but it still fits an existing skill boundary.")
            return {
                "classification": "update_skill",
                "actions": actions,
                "rationale": rationale,
                "anti_entropy_guard": "Repeated patterns still prefer consolidation over new directories.",
            }
        actions.append(f"create {candidate_skill or '<candidate-skill>'}/SKILL.md")
        actions.append("add at least one thin script")
        actions.append("add at least one minimal local lab or fixture")
        actions.append("add at least one lightweight test")
        actions.append("run skill_growth_guard.py before creating the new directory")
        actions.append("sync README.md, CLAUDE.md, docs/skills.md, and docs/roadmap.md")
        rationale.append("The pattern is repeated and no existing skill owns it cleanly.")
        return {
            "classification": "new_skill",
            "actions": actions,
            "rationale": rationale,
            "anti_entropy_guard": "New-skill creation is allowed only because repetition and ownership checks passed.",
        }

    actions.append("record the gap in knowledge/skill-backlog.md")
    rationale.append("The evidence is not strong enough for a structural repo change.")
    return {
        "classification": "backlog_only",
        "actions": actions,
        "rationale": rationale,
        "anti_entropy_guard": "Default to backlog when evidence is weak.",
    }


def main() -> int:
    args = parse_args()
    result = classify_gap(
        set(args.signal),
        args.frequency,
        args.existing_skill,
        args.candidate_skill,
    )
    result["inputs"] = {
        "signals": args.signal,
        "frequency": args.frequency,
        "existing_skill": args.existing_skill,
        "candidate_skill": args.candidate_skill,
        "category": args.category,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
