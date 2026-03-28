---
name: ctf-solver-profile
description: Apply an evidence-first expert workflow before and during CTF solving. Use when starting any CTF challenge, when a target is ambiguous, when choosing between web/pwn/rev/crypto/misc directions, or when the agent needs a stable expert problem-solving style instead of ad hoc guessing. This skill defines the solver profile, escalation order, switching rules, and note discipline that should govern all category-specific skills.
---

# CTF Solver Profile

This skill is the front door for CTF work. It is not a themed persona. It is a decision policy.

Use it to force a consistent solving style:

- gather evidence before naming the bug
- prove each assumption with the cheapest useful test
- keep multiple hypotheses alive until one is confirmed
- switch categories deliberately instead of thrashing
- preserve artifacts and notes as you go

After applying this profile, call a category skill only when the evidence supports it.

## Core Posture

Operate like a senior solver, not a payload vending machine.

That means:

- prefer short validating probes over long exploit chains
- read source or metadata before brute force when possible
- separate facts, hypotheses, and next tests
- avoid repeating the same failed probe shape under new names
- stop and reframe when a line of attack yields no new evidence

## Default Workflow

1. Classify the artifact or target at a high level.
2. Record initial facts without overcommitting to one category.
3. Generate 2 to 4 plausible hypotheses.
4. Choose the cheapest probe that best separates those hypotheses.
5. Escalate only after one hypothesis gains real evidence.
6. Once a category is clear, invoke the matching category skill.
7. Keep a running note of evidence, dead ends, and working payloads.
8. When solved, hand off to `ctf-knowledge-capture`.

## First Five Minutes

Always answer these questions first:

- What exactly is the input artifact or live target?
- What category does it most resemble right now?
- What one or two clues support that classification?
- What is the cheapest next probe?
- What result would cause a category switch?

If you cannot answer those questions, you are not ready to brute force.

## Evidence Levels

Use these levels mentally when reasoning:

- `fact`: directly observed behavior, file contents, headers, strings, timing, symbols, hashes
- `hypothesis`: a plausible explanation not yet confirmed
- `decision`: a next action chosen because it distinguishes hypotheses

Do not treat a hypothesis as settled just because it feels likely.

## Category Switching

Read `references/category-switches.md` when classification is unstable.

Use these examples:

- A blank PHP page with a tiny query surface may be a webshell or backdoor, not a normal web app.
- A network service that immediately crashes on malformed input may be pwn, not web.
- A file that looks like junk text may still be encoded crypto or a packed binary.
- A web challenge with only one fetch parameter may really be an SSRF-to-source-read problem, not directory brute force.

## Escalation Rules

- Start with visibility probes: version, headers, strings, source, metadata, usage, symbols.
- Move to controlled execution probes: `phpinfo();`, `id`, `sleep(3)`, test strings, harmless file reads.
- Escalate to real exploitation only after controlled probes confirm the path.
- Enumerate for flags only after you have stable execution or a stable read primitive.

## Dead-End Detection

You are probably stuck when:

- multiple probes are the same shape with only renamed parameters
- no new evidence appeared in the last 5 to 10 actions
- you are guessing payloads without a model of the target
- you stopped recording why earlier branches failed

When stuck:

1. list current facts
2. list live hypotheses
3. list one probe per hypothesis
4. drop branches with no distinguishing evidence

## Output Discipline

Maintain a compact running state:

- target summary
- current category guess
- confirmed primitives
- dead ends
- next best probe

After solving, save the case with `ctf-knowledge-capture`.

## Interaction With Other Skills

- Start with this skill first.
- Then invoke one concrete category skill such as `web-ssrf-to-rce-triage`.
- Do not load multiple heavy category skills unless the evidence genuinely spans them.
- If a solve reveals a repeated pattern, record it in `knowledge/patterns/` and only then update the category skill.

## Maintenance

This skill should stay short and stable. Put detailed heuristics in reference files, not in the main body.

Read `references/thinking-style.md` for the detailed solver stance and `references/category-switches.md` for cross-category cues.
