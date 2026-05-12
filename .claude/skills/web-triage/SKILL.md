---
name: web-triage
description: Router for web vulnerability triage. Routes to the appropriate reference workflow based on evidence patterns. Use after ctf-solver-profile when the target is a web challenge requiring vulnerability identification and exploitation.
---

# Web Triage Router

Use this skill after `ctf-solver-profile` when the target is a web challenge.

Treat it as a router: inspect evidence, then jump to the matching reference.

## Routing Table

| Evidence Pattern | Reference |
|------------------|-----------|
| `eyJ...` tokens, `Authorization: Bearer`, JWT claims | [jwt.md](references/jwt.md) |
| `rO0AB`, `gASV`, `O:8:"Class"`, pickle/serialize language | [deserialization.md](references/deserialization.md) |
| SSRF hints, `file://`, internal fetch, localhost pivot | [ssrf.md](references/ssrf.md) |
| Template syntax `{{}}`, `${}`, `<%= %>` evaluating server-side | [ssti.md](references/ssti.md) |
| Parameter affecting rows/errors, `AND 1=1` differential | [sqli.md](references/sqli.md) |
| Reflected input in HTML/attributes, `onerror=alert(1)` | [xss.md](references/xss.md) |

## Quick Decision Flow

1. **See serialized data?** → Check deserialization signatures first
2. **See JWT tokens?** → jwt.md
3. **See URL fetch parameter?** → ssrf.md
4. **See template syntax evaluated?** → ssti.md
5. **See SQL-like parameter influence?** → sqli.md
6. **See reflected HTML with script potential?** → xss.md

## Tool Reference

All web tools are now at `src/tools/web/`:

```
src/tools/web/
├── jwt_tool.py           # JWT inspect, forge, bruteforce
├── boolean_probe.py      # SQLi true/false differential
├── sqlite_boolean_extract.py  # Blind SQLite extraction
├── fetch_target.py       # SSRF/file:// request wrapper
├── ssti_probe.py         # Template injection probes
├── xss_probe.py          # XSS reflection probes
├── detect_ser.py         # Serialization format detection
└── gen_payload.py        # Payload generation (Java/Python/PHP)
```

Usage pattern:

```bash
python3 src/tools/web/<tool>.py <command> --target URL --param NAME
```

## Workflow

1. Fingerprint the target (stack, endpoints, auth mechanism)
2. Match evidence to a reference workflow
3. Follow the reference's probe order
4. Verify exploitation before expanding scope
5. Save the case with `ctf-knowledge-capture`

## Exit Conditions

Switch to another skill category when:

- Evidence points to crypto, pwn, or reverse engineering
- The target is not a web application
- The vulnerability class is not covered here
