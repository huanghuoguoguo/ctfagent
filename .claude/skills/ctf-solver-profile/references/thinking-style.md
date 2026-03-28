# Thinking Style

Use this file to keep the solver profile concrete without bloating `SKILL.md`.

## What expert behavior looks like

- Build a model of the target before throwing complex payloads at it.
- Prefer discriminating probes over broad noisy scans when the surface is small.
- Treat source disclosure as a force multiplier.
- Treat controlled timing as evidence, not as an exploit by itself.
- Distinguish "no output" from "no code path".

## What expert behavior does not look like

- Repeating the same payload idea across many parameter names with no new evidence.
- Calling every blank page an LFI or every socket service a pwn binary.
- Running expensive brute force before checking source, metadata, and defaults.
- Switching categories emotionally instead of because the evidence changed.

## Probe ordering heuristics

- If source is readable, read it before payload escalation.
- If the service is blank but dynamic, test for hidden code-exec or debug parameters with safe probes.
- If the target is noisy and broad, narrow it with headers, status codes, and content-length differences first.
- If the target is binary, start with `file`, strings, protections, symbols, and dynamic behavior.

## Confidence language

Keep internal reasoning and notes explicit:

- `confirmed`: directly observed
- `likely`: more evidence for than against
- `possible`: viable but weakly supported
- `discarded`: contradicted by evidence

## Finish condition

A challenge is not fully handled until:

- the flag is recovered or the blocking issue is explicit
- the exploit chain is stated clearly
- the case is recorded locally
- any reusable pattern is identified
