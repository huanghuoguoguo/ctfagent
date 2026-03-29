---
doc_kind: writeup
title: "Web XSS Lab - Reflected and DOM XSS"
category: web
slug: web-xss-lab
created: 2026-03-29
status: completed
tags:
  - xss
  - reflected-xss
  - dom-xss
  - cookie-stealing
---
# Web XSS Lab - Reflected and DOM XSS

## Challenge Summary

- **Source**: Local target `targets/web-xss-lab/`
- **Target**: `http://localhost:5006/`
- **Goal**: Find hidden flags via XSS vulnerabilities

## Initial Signals

- **Entry point**:
  - `/reflected?name=guest` - Server reflects query param into HTML
  - `/dom` - Client reads URL hash and renders via `innerHTML`
- **Visible hints**: Source code in `targets/web-xss-lab/app.py` shows cookie-based flags
- **First confirming probe**: `XSSMARK123` reflected as `<h1>Hello, XSSMARK123!</h1>` - no escaping

## Exploit Chain

1. **Reflected XSS**: Inject `<script>alert(1)</script>` into `name` param, server renders it directly into template
2. **DOM XSS**: Inject `<img src=x onerror=alert(1)>` into URL hash, client reads it and sets `innerHTML`
3. **Flag extraction**: Both endpoints set non-HttpOnly cookies containing flags, readable via `document.cookie`

## Key Evidence

- Playwright confirmed alert(1) execution on both endpoints
- Cookies visible: `flag=CTF{reflected_xss_is_easy}` and `secret=CTF{dom_xss_via_hash_sink}`
- No HttpOnly flag on cookies, allowing JavaScript access via `document.cookie`

## Dead Ends

- None - direct source code access made this a straightforward solve 

## Payloads And Commands

```bash
# Reflected XSS probe
curl "http://localhost:5006/reflected?name=<script>alert(1)</script>"

# DOM XSS probe
curl "http://localhost:5006/dom#<img src=x onerror=alert(1)>"

# Playwright cookie extraction
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5006/reflected?name=<script>alert(1)</script>')
    page.wait_for_timeout(1000)
    print(page.context.cookies())
    browser.close()
"
```

## Flag / Outcome

- `CTF{reflected_xss_is_easy}` - from `/reflected` endpoint cookie
- `CTF{dom_xss_via_hash_sink}` - from `/dom` endpoint cookie

## Reusable Lessons

- **Reflected XSS detection**: Test with marker string, check for unescaped reflection in HTML response
- **DOM XSS detection**: Look for `innerHTML`, `document.write()`, `eval()` with data from `location.hash`, `location.search`, or `location.href`
- **Cookie flags**: Check `Set-Cookie` headers and `document.cookie` - flags often stored in non-HttpOnly cookies
- **Browser verification**: Use Playwright to confirm actual JavaScript execution, not just reflection

## Pattern Candidates

- Existing pattern to update: None - basic XSS patterns already covered in `web-xss-triage` skill
- New pattern worth creating: None - this is a standard lab exercise, not a novel chain
