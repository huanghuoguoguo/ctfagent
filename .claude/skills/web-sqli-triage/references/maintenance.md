# Maintenance Notes

Keep this skill focused on first-pass triage and the shortest reliable blind-extraction path.

## What to update

- Add one new DB-specific branch only after it repeats across solved targets.
- Add one helper script flag or matcher only when it removes repeated manual work.
- Add one new probe only when it changes the first ten minutes of solver behavior.

## What not to add

- Full SQLi theory
- Long DBMS cheat sheets
- Challenge-specific brute-force logs
- Heavy automation before the oracle is proven

## Review checklist

- Keep `SKILL.md` short enough that the probe order is obvious.
- Re-test both helper scripts against `targets/web-sqli-lab` after logic changes.
- Prefer concise examples that show oracle selection, not every payload family.
- Move repeated extraction details into scripts rather than expanding prose.
