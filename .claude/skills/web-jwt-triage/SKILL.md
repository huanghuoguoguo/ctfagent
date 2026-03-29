---
name: web-jwt-triage
description: Triage CTF web targets that use JWT-based authentication. Use when you see Bearer tokens, `eyJ...` strings, `Authorization` headers, or role/session claims that may be forgeable through `alg=none`, weak HMAC secrets, or header-driven key confusion.
---

# Web JWT Triage

Use this skill after `ctf-solver-profile` when the target uses JWT for session or authorization checks.

Treat it as a short SOP:

- inspect the token structure before mutating it
- decide whether the problem is unsigned acceptance, weak HMAC signing, or header-driven key confusion
- change the smallest claim that proves authorization control
- verify the bypass before exploring extra JWT branches

## Quick Start

Inspect a token:

```bash
python3 .claude/skills/web-jwt-triage/scripts/jwt_tool.py inspect \
  --token 'eyJ...'
```

Craft an `alg=none` token with an updated claim:

```bash
python3 .claude/skills/web-jwt-triage/scripts/jwt_tool.py make-none \
  --token 'eyJ...' \
  --set role=admin
```

Re-sign a token with a weak HS256 secret:

```bash
python3 .claude/skills/web-jwt-triage/scripts/jwt_tool.py resign-hs256 \
  --token 'eyJ...' \
  --secret secret123 \
  --set role=admin
```

Bruteforce a weak secret from a small wordlist:

```bash
python3 .claude/skills/web-jwt-triage/scripts/jwt_tool.py bruteforce-hs256 \
  --token 'eyJ...' \
  --wordlist ./secrets.txt
```

## Workflow

1. Decode the header and payload.
2. Note `alg`, `kid`, `jku`, `jwk`, `x5u`, `x5c`, and authorization claims such as `role`, `admin`, or `scope`.
3. Test the simplest likely failure first:
   - `alg=none`
   - weak HS256 secret
   - header-supplied key confusion
4. Change the minimum claim needed to prove authorization control.
5. Verify the bypass against one protected endpoint.
6. Save the case with `ctf-knowledge-capture`.

## Probe Order

Use this order unless the target strongly suggests otherwise:

1. Inspect the token with `jwt_tool.py inspect`
2. If `alg` is `HS256`, check for weak shared secrets
3. If the server appears to trust unsigned tokens, try `alg=none`
4. If headers include `kid`, `jku`, or `jwk`, treat it as a key-selection problem, not just a claim-tampering problem

## Interpretation Hints

- `alg=none` accepted:
  - The server is trusting unsigned tokens
  - Change one claim such as `role=admin` and re-test

- `HS256` with a weak secret:
  - Re-sign the token instead of leaving it unsigned
  - Keep `typ` and other expected fields stable unless the target proves otherwise

- `kid` / `jku` / `jwk` present:
  - The server may be loading keys from attacker-controlled metadata
  - Confirm whether the issue is path traversal, remote key fetch, or header confusion

## Local Lab

Bundled lab:

- Path: `targets/web-jwt-lab/`
- Endpoint: `http://127.0.0.1:5005/login?user=guest`
- Protected endpoint: `http://127.0.0.1:5005/admin`
- Goal: turn a guest token into admin access via `alg=none` or the weak HS256 secret

## Exit Conditions

Switch away from this skill when:

- the token is only a transport format and the real issue is server-side session confusion
- the endpoint is using opaque sessions rather than JWT
- behavior points to OAuth flow abuse, open redirect, or CSRF instead of token forgery
