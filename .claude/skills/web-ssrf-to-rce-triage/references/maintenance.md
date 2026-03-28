# Maintenance Notes

Use this file to keep the skill stable as you solve more web CTF challenges.

## What to update

- Add one new probe step only when it repeatedly appears across targets.
- Add one new path or config file only when it materially improves first-pass success.
- Add one new pivot pattern only when it changes solver behavior, not just explanation wording.

## What not to add

- Long writeups
- Challenge-specific payload dumps
- Branches for one-off frameworks unless they recur
- Redundant explanations of SSRF, LFI, or RCE basics

## Review checklist

- Keep `SKILL.md` under roughly 250 lines when possible.
- Ensure the first five minutes of work stay obvious from the top of the file.
- Prefer scripts for repeated request/parse steps instead of embedding long shell snippets.
- Re-test `scripts/fetch_target.py` against a real target after changing parsing logic.
- If a new reference file is added, link it directly from `SKILL.md`.

## Versioning habit

- After each solved target, append a short local note elsewhere in the repo or workspace:
  `target -> what branch of the skill was useful -> what was missing`
- Batch-edit the skill after 3-5 targets instead of after every single solve.
