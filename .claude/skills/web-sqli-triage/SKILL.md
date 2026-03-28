---
name: web-sqli-triage
description: Triage CTF web targets for SQL injection, especially boolean-blind SQLite-style cases, and move from confirmation to lightweight schema and flag extraction. Use when a parameter affects rows, errors, timing, or JSON/body differences and you need a disciplined path from quick probes to DB-specific extraction.
---

# Web SQLi Triage

Use this skill after `ctf-solver-profile` when evidence points to SQL injection.

Treat it as a short SOP:

- confirm injection with the cheapest differential probe
- identify the response oracle
- identify the likely database family
- escalate to schema extraction only after the oracle is stable

## Quick Start

Compare true and false probes:

```bash
python3 .claude/skills/web-sqli-triage/scripts/boolean_probe.py \
  --target http://127.0.0.1:5001/search \
  --param id \
  --true-payload "1 AND 1=1" \
  --false-payload "1 AND 1=0"
```

Extract a SQLite integer such as table count:

```bash
python3 .claude/skills/web-sqli-triage/scripts/sqlite_boolean_extract.py int \
  --target http://127.0.0.1:5001/search \
  --param id \
  --prefix "1 AND " \
  --expr "SELECT COUNT(*) FROM sqlite_master WHERE type='table'" \
  --true-status 200 \
  --max 10
```

Extract a SQLite string such as a hidden table name:

```bash
python3 .claude/skills/web-sqli-triage/scripts/sqlite_boolean_extract.py string \
  --target http://127.0.0.1:5001/search \
  --param id \
  --prefix "1 AND " \
  --expr "SELECT tbl_name FROM sqlite_master WHERE type='table' LIMIT 1 OFFSET 2" \
  --true-status 200 \
  --max-length 32
```

## Workflow

1. Fingerprint the endpoint and parameter type.
2. Compare a true condition and a false condition.
3. Decide the response oracle: status code, body substring, length delta, or timing.
4. Infer the likely DB family from syntax and target stack.
5. Use the smallest DB-specific metadata query that proves structure.
6. Extract only the columns or values needed for the flag.
7. Save the case with `ctf-knowledge-capture`.

## First Probes

Start with short, low-noise probes:

- `1 AND 1=1`
- `1 AND 1=0`
- `1'`
- `1 ORDER BY 1`
- `1 UNION SELECT 1`

For string contexts, switch to quote-balanced versions instead of repeating numeric payloads blindly.

## Oracle Selection

Prefer these in order:

1. Different status codes
2. Stable body substring present only on true
3. Stable body length difference
4. Timing only when no content oracle exists

If you do not have a stable oracle, stop and improve observation before brute forcing characters.

## SQLite Branch

When the target looks like Python/Flask, SQLite is common. Prioritize:

- `sqlite_master` for tables
- `PRAGMA_TABLE_INFO('table_name')` for columns
- `LENGTH()` and `SUBSTR()` for blind extraction

Typical extraction order:

1. count tables
2. identify the interesting table
3. identify the interesting column
4. extract the shortest secret that wins the challenge

## Decision Rules

- If `AND 1=1` and `AND 1=0` differ, stabilize that oracle before trying UNION payloads.
- If errors are swallowed, shift early to boolean-blind extraction instead of chasing verbose errors.
- If one hidden table is enough, do not enumerate the full schema.
- Script character extraction once the manual pattern is confirmed.

## Maintenance

Read `references/maintenance.md` before growing this skill. Keep challenge-specific payload dumps out of the main body.
