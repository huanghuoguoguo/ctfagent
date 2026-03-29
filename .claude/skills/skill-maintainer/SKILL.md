---
name: skill-maintainer
description: Maintain and evolve the CTF skill system after solving or reviewing a challenge. Use when a solve exposed repeated manual work, a missing probe order, an absent helper script, lab drift, duplicate skill ideas, or documentation inconsistency and you need a constrained path for improving the repo without causing skill sprawl.
---

# Skill Maintainer

This skill does not solve the challenge itself. It maintains the solving system.

Use it after a solve, after a failed line of attack, or after reviewing a new pattern. Its job is to decide the smallest safe upgrade that makes the agent better next time.

The default rule is:

- prefer updating an existing skill over creating a new one
- prefer a thin script over a new skill when the gap is procedural
- prefer a pattern or backlog entry over a new skill when the evidence is weak

## What It Can Produce

A maintenance pass should end in exactly one of these outcomes:

1. `update_skill`
2. `new_script`
3. `new_target`
4. `new_test`
5. `new_pattern`
6. `new_skill`
7. `backlog_only`

If the evidence is thin, choose `backlog_only`.

## Quick Start

Classify a feedback bundle:

```bash
python3 .claude/skills/skill-maintainer/scripts/skill_gap_report.py \
  --existing-skill web-jwt-triage \
  --signal repeated_manual_step \
  --signal missing_script \
  --signal missing_test \
  --frequency 3
```

Check inventory drift and duplicate roadmap entries:

```bash
python3 .claude/skills/skill-maintainer/scripts/check_skill_inventory.py \
  --root .
```

Record unresolved work in:

- `knowledge/skill-backlog.md`

## Workflow

1. Gather feedback from `workspaces/`, `artifacts/`, solved writeups, and failed probes.
2. Decide whether the gap belongs in:
   - an existing skill
   - a new script
   - a new lab
   - a new test
   - a reusable pattern
   - backlog only
3. Only propose `new_skill` when the pattern is repeated and clearly cannot fit an existing skill.
4. If a repo change is made, require script/lab/test/doc sync before calling it complete.

## Anti-Entropy Rules

Never create a new skill if one of these is true:

- the gap can be fixed by updating an existing skill
- the gap is only one repeated shell command or payload shape
- the pattern appeared only once
- there is no lab, fixture, or test path yet

Prefer these upgrade shapes, in order:

1. `update_skill`
2. `new_script`
3. `new_test`
4. `new_target`
5. `new_pattern`
6. `new_skill`

## Required Inputs

A good maintenance pass should consider:

- what repeated manual work happened
- what the agent misclassified
- what tool or script was missing
- whether the issue already overlaps an existing skill
- whether the lesson is repeated enough to justify a new skill

## Exit Conditions

Stop after the smallest useful change.

Do not bundle multiple new topic skills into one maintenance pass.
