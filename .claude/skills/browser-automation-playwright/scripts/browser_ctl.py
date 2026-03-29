#!/usr/bin/env python3
"""
Playwright Browser Control Script for CTF
Headless browser automation for XSS testing, DOM extraction, screenshot capture, etc.

Usage:
    python3 browser_ctl.py <command> [options]

Commands:
    screenshot    Capture page screenshot
    evaluate      Execute JavaScript and return result
    extract       Extract DOM content by selector
    navigate      Navigate to URL with options
    form          Fill and submit forms
    xss-test      Test XSS payloads with console capture
    chain         Execute multiple actions
    csp-test      Test CSP restrictions
    request       Intercept and modify requests
    storage       View/modify localStorage/sessionStorage
"""

import argparse
import base64
import json
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: Playwright not installed.")
    print("Install with: pip3 install playwright && playwright install chromium")
    sys.exit(1)


def check_browser_environment():
    """Check if browser environment is properly configured."""
    import shutil
    import os

    checks = {
        'playwright_package': True,
        'chromium_installed': False,
        'system_deps': [],
        'missing_libs': []
    }

    # Check for Playwright chromium
    try:
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            checks['chromium_installed'] = browser_path is not None
            checks['browser_path'] = browser_path
    except Exception as e:
        checks['chromium_error'] = str(e)

    # Check system libraries
    required_libs = ['libgbm.so.1', 'libnss3.so', 'libatk-1.0.so.0']
    lib_paths = ['/usr/lib', '/usr/lib64', '/lib', '/lib64', '/usr/local/lib']

    for lib in required_libs:
        found = False
        for path in lib_paths:
            if os.path.exists(os.path.join(path, lib)):
                found = True
                break
        if found:
            checks['system_deps'].append(lib)
        else:
            checks['missing_libs'].append(lib)

    return checks


def create_browser_context(playwright, headless: bool = True, proxy: Optional[str] = None,
                          user_agent: Optional[str] = None, viewport: Optional[str] = None):
    """Create and configure browser context."""
    try:
        browser = playwright.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-setuid-sandbox'] if headless else []
        )
    except Exception as e:
        error_msg = str(e)
        if 'libgbm.so.1' in error_msg:
            print("Error: Missing system library libgbm.so.1", file=sys.stderr)
            print("Install with: sudo apt-get install libgbm1", file=sys.stderr)
        elif 'libnss3' in error_msg:
            print("Error: Missing system library libnss3", file=sys.stderr)
            print("Install with: sudo apt-get install libnss3", file=sys.stderr)
        else:
            print(f"Error launching browser: {error_msg}", file=sys.stderr)
            print("Run 'playwright install-deps chromium' to install all dependencies", file=sys.stderr)
        raise

    context_options = {}

    if proxy:
        context_options['proxy'] = {'server': proxy}

    if user_agent:
        context_options['user_agent'] = user_agent

    if viewport:
        width, height = map(int, viewport.split('x'))
        context_options['viewport'] = {'width': width, 'height': height}
    else:
        context_options['viewport'] = {'width': 1920, 'height': 1080}

    context = browser.new_context(**context_options)
    return browser, context


def cmd_screenshot(args):
    """Capture page screenshot."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            if args.wait_for_selector:
                page.wait_for_selector(args.wait_for_selector, timeout=args.timeout)

            if args.wait:
                time.sleep(args.wait / 1000)

            page.screenshot(path=args.output, full_page=args.full_page)
            print(f"Screenshot saved: {args.output}")

        except PlaywrightTimeout:
            print(f"Error: Timeout waiting for page load", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_evaluate(args):
    """Execute JavaScript and return result."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        console_logs = []

        if args.capture_console:
            page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            if args.wait:
                time.sleep(args.wait / 1000)

            result = page.evaluate(args.script)
            print(json.dumps(result, indent=2, default=str))

            if console_logs:
                print("\n--- Console Logs ---", file=sys.stderr)
                for log in console_logs:
                    print(log, file=sys.stderr)

        except PlaywrightTimeout:
            print(f"Error: Timeout", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_extract(args):
    """Extract DOM content by selector."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            if args.wait_for_selector:
                page.wait_for_selector(args.wait_for_selector, timeout=args.timeout)

            if args.wait:
                time.sleep(args.wait / 1000)

            if args.selector:
                elements = page.query_selector_all(args.selector)
                results = []
                for el in elements:
                    text = el.inner_text()
                    html = el.inner_html()
                    results.append({'text': text, 'html': html})
                print(json.dumps(results, indent=2))
            else:
                content = page.content()
                print(content)

        except PlaywrightTimeout:
            print(f"Error: Timeout waiting for selector", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_navigate(args):
    """Navigate to URL with cookie/header support."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        # Set cookies if provided
        if args.cookies:
            cookies = json.loads(args.cookies)
            context.add_cookies([
                {'name': k, 'value': v, 'url': args.url}
                for k, v in cookies.items()
            ])

        # Set extra headers if provided
        if args.headers:
            headers = json.loads(args.headers)
            page.set_extra_http_headers(headers)

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            if args.wait:
                time.sleep(args.wait / 1000)

            # Get page info
            info = {
                'url': page.url,
                'title': page.title(),
                'cookies': context.cookies(),
                'content_length': len(page.content())
            }
            print(json.dumps(info, indent=2))

        except PlaywrightTimeout:
            print(f"Error: Timeout", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_form(args):
    """Fill and submit forms."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            fields = json.loads(args.fields)
            for selector, value in fields.items():
                page.fill(selector, value)
                print(f"Filled: {selector}")

            if args.submit:
                page.click(args.submit)
                page.wait_for_load_state('networkidle')
                print(f"Submitted: {args.submit}")

            if args.output:
                page.screenshot(path=args.output)
                print(f"Screenshot saved: {args.output}")

            # Return current page info
            info = {
                'url': page.url,
                'title': page.title(),
                'content': page.content()[:1000] + '...' if len(page.content()) > 1000 else page.content()
            }
            print(json.dumps(info, indent=2))

        except PlaywrightTimeout:
            print(f"Error: Timeout", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_xss_test(args):
    """Test XSS payloads with dialog and console capture."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        dialogs = []
        console_logs = []

        page.on('dialog', lambda dialog: [
            dialogs.append({'type': dialog.type, 'message': dialog.message}),
            dialog.accept()
        ])

        page.on('console', lambda msg: console_logs.append({
            'type': msg.type,
            'text': msg.text,
            'location': str(msg.location)
        }))

        network_requests = []
        if args.capture_network:
            page.on('request', lambda req: network_requests.append({
                'url': req.url,
                'method': req.method,
                'headers': dict(req.headers)
            }))

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            # Wait for potential XSS execution
            wait_time = args.wait_for_alert if args.wait_for_alert else 3000
            time.sleep(wait_time / 1000)

            result = {
                'xss_triggered': len(dialogs) > 0,
                'dialogs': dialogs,
                'console_logs': console_logs[:50],  # Limit output
            }

            if args.capture_network:
                result['network_requests'] = network_requests[:20]

            print(json.dumps(result, indent=2))

        except PlaywrightTimeout:
            print(f"Error: Timeout", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_chain(args):
    """Execute multiple actions in sequence."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        console_logs = []
        if args.capture_console:
            page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        try:
            steps = json.loads(args.steps)
            results = []

            for i, step in enumerate(steps):
                action = step.get('action')
                result = {'step': i, 'action': action}

                if action == 'goto':
                    page.goto(step['url'], timeout=args.timeout)
                    result['url'] = page.url

                elif action == 'fill':
                    page.fill(step['selector'], step['value'])
                    result['selector'] = step['selector']

                elif action == 'click':
                    page.click(step['selector'])
                    page.wait_for_load_state('networkidle')
                    result['selector'] = step['selector']

                elif action == 'wait':
                    time.sleep(step.get('ms', 1000) / 1000)

                elif action == 'extract':
                    el = page.query_selector(step['selector'])
                    if el:
                        result['content'] = el.inner_text()
                    else:
                        result['error'] = 'Element not found'

                elif action == 'evaluate':
                    result['result'] = page.evaluate(step['script'])

                elif action == 'screenshot':
                    path = step.get('path', f'step_{i}.png')
                    page.screenshot(path=path)
                    result['screenshot'] = path

                results.append(result)

            final_output = {
                'steps': results,
                'final_url': page.url,
                'final_title': page.title()
            }

            if console_logs:
                final_output['console_logs'] = console_logs

            print(json.dumps(final_output, indent=2))

        except Exception as e:
            print(f"Error in chain execution: {e}", file=sys.stderr)
            print(json.dumps({'error': str(e), 'completed_steps': results}, indent=2))
            return 1
        finally:
            browser.close()

    return 0


def cmd_storage(args):
    """View/modify localStorage and sessionStorage."""
    with sync_playwright() as p:
        browser, context = create_browser_context(
            p, headless=args.headless, proxy=args.proxy,
            user_agent=args.user_agent, viewport=args.viewport
        )
        page = context.new_page()

        try:
            page.goto(args.url, timeout=args.timeout, wait_until='networkidle')

            # Get storage
            local_storage = page.evaluate('() => Object.entries(localStorage)')
            session_storage = page.evaluate('() => Object.entries(sessionStorage)')

            # Set storage if provided
            if args.set_local:
                items = json.loads(args.set_local)
                for k, v in items.items():
                    page.evaluate(f'() => localStorage.setItem("{k}", "{v}")')

            if args.set_session:
                items = json.loads(args.set_session)
                for k, v in items.items():
                    page.evaluate(f'() => sessionStorage.setItem("{k}", "{v}")')

            result = {
                'localStorage': {k: v for k, v in local_storage},
                'sessionStorage': {k: v for k, v in session_storage}
            }

            if args.set_local or args.set_session:
                # Refresh storage after modifications
                result['localStorage'] = {k: v for k, v in page.evaluate('() => Object.entries(localStorage)')}
                result['sessionStorage'] = {k: v for k, v in page.evaluate('() => Object.entries(sessionStorage)')}

            print(json.dumps(result, indent=2))

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        finally:
            browser.close()

    return 0


def cmd_check():
    """Check browser environment and dependencies."""
    print("=== Playwright Browser Environment Check ===\n")

    # Check Python package
    print("[1] Python Package")
    try:
        import playwright
        print(f"    ✓ Playwright installed")
    except ImportError:
        print("    ✗ Playwright not installed")
        print("    → Install: pip3 install playwright")
        return 1

    # Check browser
    print("\n[2] Browser Binary")
    try:
        with sync_playwright() as p:
            browser_path = p.chromium.executable_path
            if browser_path:
                print(f"    ✓ Chromium found: {browser_path}")
            else:
                print("    ✗ Chromium not installed")
                print("    → Install: playwright install chromium")
                return 1
    except Exception as e:
        print(f"    ✗ Error checking browser: {e}")
        print("    → Install browser: playwright install chromium")
        return 1

    # Check system dependencies
    print("\n[3] System Dependencies")
    import os
    required_libs = {
        'libgbm.so.1': 'libgbm1',
        'libnss3.so': 'libnss3',
        'libatk-1.0.so.0': 'libatk1.0-0',
        'libatk-bridge-2.0.so.0': 'libatk-bridge2.0-0',
        'libxkbcommon.so.0': 'libxkbcommon0',
        'libgtk-3.so.0': 'libgtk-3-0',
    }

    lib_paths = ['/usr/lib', '/usr/lib64', '/lib', '/lib64', '/usr/lib/x86_64-linux-gnu']
    missing = []

    for lib, pkg in required_libs.items():
        found = False
        for path in lib_paths:
            if os.path.exists(os.path.join(path, lib)):
                found = True
                break
        if found:
            print(f"    ✓ {lib}")
        else:
            print(f"    ✗ {lib} (package: {pkg})")
            missing.append(pkg)

    # Test browser launch
    print("\n[4] Browser Launch Test")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
            print("    ✓ Browser launches successfully")
    except Exception as e:
        print(f"    ✗ Browser launch failed: {e}")
        if missing:
            print(f"\n    → Install missing packages:")
            print(f"       sudo apt-get install {' '.join(missing)}")
        print(f"    → Or run: playwright install-deps chromium")
        return 1

    print("\n=== All Checks Passed ===")
    print("Environment ready for browser automation!")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Playwright Browser Control for CTF',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global options
    parser.add_argument('--headless', type=lambda x: x.lower() == 'true', default=True,
                       help='Run in headless mode - no GUI required (default: true)')
    parser.add_argument('--timeout', type=int, default=30000, help='Timeout in ms (default: 30000)')
    parser.add_argument('--proxy', type=str, help='Proxy URL (e.g., http://127.0.0.1:8080)')
    parser.add_argument('--user-agent', type=str, help='Custom user agent')
    parser.add_argument('--viewport', type=str, help='Viewport size (e.g., 1920x1080)')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # screenshot command
    p_screenshot = subparsers.add_parser('screenshot', help='Capture page screenshot')
    p_screenshot.add_argument('--url', required=True, help='Target URL')
    p_screenshot.add_argument('--output', required=True, help='Output file path')
    p_screenshot.add_argument('--full-page', action='store_true', help='Capture full page')
    p_screenshot.add_argument('--wait', type=int, help='Wait time in ms after load')
    p_screenshot.add_argument('--wait-for-selector', help='Wait for selector before screenshot')

    # evaluate command
    p_evaluate = subparsers.add_parser('evaluate', help='Execute JavaScript')
    p_evaluate.add_argument('--url', required=True, help='Target URL')
    p_evaluate.add_argument('--script', required=True, help='JavaScript code to execute')
    p_evaluate.add_argument('--wait', type=int, help='Wait time in ms')
    p_evaluate.add_argument('--capture-console', action='store_true', help='Capture console logs')

    # extract command
    p_extract = subparsers.add_parser('extract', help='Extract DOM content')
    p_extract.add_argument('--url', required=True, help='Target URL')
    p_extract.add_argument('--selector', help='CSS selector')
    p_extract.add_argument('--wait-for-selector', help='Wait for this selector')
    p_extract.add_argument('--wait', type=int, help='Wait time in ms')

    # navigate command
    p_navigate = subparsers.add_parser('navigate', help='Navigate with cookies/headers')
    p_navigate.add_argument('--url', required=True, help='Target URL')
    p_navigate.add_argument('--cookies', help='JSON cookies object')
    p_navigate.add_argument('--headers', help='JSON headers object')
    p_navigate.add_argument('--wait', type=int, help='Wait time in ms')

    # form command
    p_form = subparsers.add_parser('form', help='Fill and submit forms')
    p_form.add_argument('--url', required=True, help='Target URL')
    p_form.add_argument('--fields', required=True, help='JSON object of field selectors and values')
    p_form.add_argument('--submit', help='Submit button selector')
    p_form.add_argument('--output', help='Screenshot output path')

    # xss-test command
    p_xss = subparsers.add_parser('xss-test', help='Test XSS payloads')
    p_xss.add_argument('--url', required=True, help='Target URL with payload')
    p_xss.add_argument('--wait-for-alert', type=int, help='Time to wait for alert dialogs')
    p_xss.add_argument('--capture-console', action='store_true', help='Capture console logs')
    p_xss.add_argument('--capture-network', action='store_true', help='Capture network requests')

    # chain command
    p_chain = subparsers.add_parser('chain', help='Execute action chain')
    p_chain.add_argument('--steps', required=True, help='JSON array of actions')
    p_chain.add_argument('--capture-console', action='store_true', help='Capture console logs')

    # storage command
    p_storage = subparsers.add_parser('storage', help='View/modify storage')
    p_storage.add_argument('--url', required=True, help='Target URL')
    p_storage.add_argument('--set-local', help='Set localStorage items (JSON)')
    p_storage.add_argument('--set-session', help='Set sessionStorage items (JSON)')

    # check command
    p_check = subparsers.add_parser('check', help='Check browser environment')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Handle check command separately (no browser needed)
    if args.command == 'check':
        return cmd_check()

    commands = {
        'screenshot': cmd_screenshot,
        'evaluate': cmd_evaluate,
        'extract': cmd_extract,
        'navigate': cmd_navigate,
        'form': cmd_form,
        'xss-test': cmd_xss_test,
        'chain': cmd_chain,
        'storage': cmd_storage,
        'check': cmd_check,
    }

    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
