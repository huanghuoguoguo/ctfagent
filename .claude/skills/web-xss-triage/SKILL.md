---
name: web-xss-triage
description: Triage CTF web targets for reflected and DOM-based XSS. Use when user input is reflected into HTML, attributes, or script sinks, or when browser execution must be confirmed with Playwright rather than guessed from raw responses.
---

# Web XSS Triage

Use this skill after `ctf-solver-profile` when evidence points to client-side code execution through reflected or DOM-based XSS.

Treat it as a short SOP:

- confirm whether the payload is reflected at all
- identify the reflection context before escalating payloads
- use the browser for final execution proof instead of guessing from raw HTML
- change the smallest payload shape that proves JavaScript execution

## Quick Start

Probe a reflected sink:

```bash
python3 .claude/skills/web-xss-triage/scripts/xss_probe.py \
  --target http://127.0.0.1:5006/reflect \
  --param q
```

Run the bundled lab:

```bash
cd targets/web-xss-lab
docker compose up -d
```

Confirm reflected XSS with the existing browser skill:

```bash
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  xss-test \
  --url 'http://127.0.0.1:5006/reflect?q=%3Cscript%3Ealert(1)%3C%2Fscript%3E' \
  --wait-for-alert 2000
```

Confirm DOM XSS:

```bash
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  xss-test \
  --url 'http://127.0.0.1:5006/dom?msg=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E' \
  --wait-for-alert 2000
```

## Workflow

1. Confirm the input reaches the response or a client-side sink.
2. Determine the reflection context: HTML text, quoted attribute, or script block.
3. Pick the smallest payload shape that fits that context.
4. Use Playwright to verify real execution.
5. Only after execution is proven, escalate to cookie theft, DOM extraction, or chained abuse.
6. Save the case with `ctf-knowledge-capture`.

## Probe Order

Start with this order:

1. Benign marker such as `XSSMARK`
2. `<script>alert(1)</script>`
3. `"><svg/onload=alert(1)>`
4. `</script><script>alert(1)</script>`

Interpret them like this:

- reflected in plain HTML text:
  - classic reflected XSS is plausible
- reflected inside a quoted attribute:
  - try a quote-break and event handler payload
- reflected inside a script block:
  - try closing the current script and starting a new one
- not reflected at all:
  - re-check DOM sinks, stored sinks, or whether the issue is another class entirely

## Browser Verification

Do not stop at “the payload appears in HTML”.

Use:

- `.claude/skills/browser-automation-playwright/scripts/browser_ctl.py xss-test`

That gives you:

- dialog capture
- console capture
- optional network request capture

## Local Lab

Bundled lab:

- Path: `targets/web-xss-lab/`
- Reflected sink: `http://127.0.0.1:5006/reflect?q=test`
- Attribute sink: `http://127.0.0.1:5006/attr?q=test`
- DOM sink: `http://127.0.0.1:5006/dom?msg=test`

## Exit Conditions

Switch away from this skill when:

- the payload only reaches server-side templates, not browser sinks
- the sink is actually SSTI or another server-side issue
- the page only reflects safely escaped text and no DOM sink is present
