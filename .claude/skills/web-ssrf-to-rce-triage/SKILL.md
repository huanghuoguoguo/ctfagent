---
name: web-ssrf-to-rce-triage
description: Triage CTF web targets that may expose SSRF-style fetchers, local file read via file:// or internal URLs, and localhost-only pivots to code execution. Use when a page fetches attacker-controlled URLs, previews remote resources, or hints at "internal resource" viewing and you need a fast, repeatable path from probing to source read, localhost pivot, and flag extraction.
---

# Web SSRF To RCE Triage

Treat this skill as a compact SOP for CTF web challenges where one user-controlled URL may unlock:

- SSRF to internal HTTP services
- `file://` local file read
- source disclosure
- localhost-only admin/debug/RCE endpoints

Keep the workflow short. Prove each step with one cheap test before escalating.

## Workflow

1. Fingerprint the target.
2. Prove whether the URL parameter is fetched server-side.
3. Test local file read.
4. Read source and webserver config.
5. Identify localhost-only behaviors in source.
6. Pivot through `127.0.0.1` or `localhost`.
7. Verify code execution with a benign command.
8. Enumerate likely flag locations and extract the flag.

## Quick Start

Use `scripts/fetch_target.py` for all routine requests. It keeps the command shape consistent and extracts the `<textarea>` content when the page wraps results in HTML.

Typical sequence:

```bash
python3 .claude/skills/web-ssrf-to-rce-triage/scripts/fetch_target.py \
  --target http://HOST:PORT/ --url http://example.com

python3 .claude/skills/web-ssrf-to-rce-triage/scripts/fetch_target.py \
  --target http://HOST:PORT/ --url file:///etc/passwd

python3 .claude/skills/web-ssrf-to-rce-triage/scripts/fetch_target.py \
  --target http://HOST:PORT/ --url file:///var/www/html/index.php
```

If the source shows localhost-gated logic, pivot with:

```bash
python3 .claude/skills/web-ssrf-to-rce-triage/scripts/fetch_target.py \
  --target http://HOST:PORT/ \
  --url "http://127.0.0.1/?code=echo%20TEST"
```

## Probe Order

Use this order unless the target strongly suggests a different stack.

### 1. Fingerprint

- Load the home page.
- Note the form field name, method, hints, and any "internal resource", "proxy", "preview", or "fetch" language.
- Confirm whether the target wraps output inside HTML, JSON, or raw text.

### 2. Prove Server-Side Fetch

- Send a benign external URL such as `http://example.com`.
- Confirm the returned content is fetched content, not a client-side redirect.

### 3. Test Local File Read

Try, in order:

- `file:///etc/passwd`
- `file:///var/www/html/index.php`
- `file:///proc/self/cmdline`
- `file:///etc/apache2/sites-enabled/000-default.conf`
- `file:///etc/nginx/sites-enabled/default`

If `file://` is blocked, continue with internal HTTP paths and config endpoints.

### 4. Read Source and Config

Prioritize:

- the current application entrypoint
- included config files
- webserver virtual host config
- framework env files

Look for:

- `REMOTE_ADDR` or IP allowlists
- debug parameters
- `eval`, `include`, `system`, `exec`, `passthru`, `assert`
- hidden routes on `127.0.0.1`
- alternate listening ports

### 5. Pivot to Localhost

If the code trusts localhost, test both:

- `http://127.0.0.1/`
- `http://localhost/`

Also test internal ports when the external service is likely a port mapping. Common pattern: the public challenge port maps to container port `80`, so `127.0.0.1/` succeeds while `127.0.0.1:PUBLIC_PORT/` fails.

### 6. Verify RCE Safely

Start with a harmless proof:

- `echo TEST`
- `id`
- `whoami`
- `pwd`

Do not jump straight to long reverse shell payloads. First confirm:

- command output is reflected
- output is truncated or not
- URL encoding rules

### 7. Enumerate for Flag

Once code execution works, check:

- `pwd`
- `whoami`
- `ls -la /`
- `ls -la /root`
- `ls -la /app`
- `ls -la /var/www/html`
- `find / -maxdepth 2 -iname '*flag*' 2>/dev/null`

Read the flag with the smallest command that works.

## Decision Rules

- If `file:///etc/passwd` works, immediately try reading source before blind fuzzing.
- If source reveals localhost-only logic, pivot there before directory brute force.
- If the first localhost request returns empty content, retry against `127.0.0.1/` without the public port.
- If HTML wrappers obscure output, use the helper script's extracted mode first and only inspect raw HTML when needed.
- If command output is HTML-escaped, decode it before concluding the exploit failed.

## Output Discipline

Record four artifacts in your notes:

- the vulnerable parameter and method
- the source snippet or behavior proving the pivot
- the minimal working localhost payload
- the final flag path and extraction command

## Maintenance

Read `references/maintenance.md` before updating this skill. Keep the workflow lean and only add branches that were observed in real targets.
