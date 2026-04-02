---
name: browser-automation-playwright
description: Control headless browsers using Playwright for CTF web challenges. Use for XSS validation, DOM analysis, screenshot capture, cookie manipulation, JavaScript execution, and automating complex multi-step web interactions.
---

# Browser Automation with Playwright

Use this skill to control headless browsers via Playwright for CTF web challenges
requiring JavaScript execution, DOM manipulation, or multi-step user interactions.

## When to Use

- **XSS Payload Validation**: Verify if XSS payloads execute in real browser context
- **DOM-based Challenges**: Extract data from JavaScript-rendered content
- **Multi-step Forms**: Automate sequences requiring interaction
- **Cookie/Session Testing**: Manipulate cookies, test session behaviors
- **Screenshot Analysis**: Visual confirmation of page states
- **CSP Bypass Testing**: Verify Content Security Policy restrictions
- **Prototype Pollution**: Test JavaScript prototype chain attacks

## When NOT to Use

- Static HTML analysis that `curl` / `requests` can handle
- API-only targets with no browser-rendered content
- Challenges where server-side response alone reveals the flag

## CTF Workflow Patterns

### XSS Payload Validation

Test whether a reflected or stored XSS payload actually fires in a browser
context. Use `xss-test` with `--capture-console` and `--wait-for-alert`.

### DOM Content Extraction

Render a page with JavaScript, then pull content from a selector. Use `extract`
with `--wait-for-selector` when the flag is populated by client-side code.

### Cookie / Session Manipulation

Set arbitrary cookies before navigating. Use `navigate` with `--cookies` to
test session fixation, forged tokens, or privilege escalation via cookies.

### Multi-step Automation

Chain login, navigation, form fill, and extraction into one run. Use `chain`
with a JSON step array to replay multi-step flows without manual intervention.

### CSP Bypass Testing

Load a page and attempt inline/iframe/eval payloads against the site's CSP.
Use `csp-test` with a payload file to iterate quickly.

## Core Commands (summary)

| Command | Purpose |
|---------|---------|
| `screenshot` | Capture page screenshot |
| `evaluate` | Run JS and return result |
| `extract` | Pull DOM text by selector |
| `xss-test` | Fire XSS payload, capture alert |
| `chain` | Multi-action sequence |
| `form` | Fill and submit a form |
| `csp-test` | Test CSP restrictions |
| `navigate` | Go to URL with cookies/headers |
| `request` | Intercept/modify requests |
| `storage` | View/modify web storage |

All commands live in `scripts/browser_ctl.py`. Invoke as:

```bash
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  <command> --url "http://target" [options]
```

See `references/api-reference.md` for full command options, installation steps,
troubleshooting, and detailed usage examples.

## Exit Conditions

- **Flag obtained**: XSS/DOM extraction returned the flag string.
- **Payload confirmed**: `xss-test` captured the expected alert or console output.
- **No browser needed**: Target is API-only or static; fall back to `curl`/`requests`.
- **Environment broken**: Playwright or Chromium fails to launch after dependency install; escalate to manual investigation.

## Installation (quick)

```bash
pip3 install playwright && playwright install chromium
```

Full dependency details and troubleshooting are in `references/api-reference.md`.
