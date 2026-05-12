# CLAUDE.md

Repository guidance for `Claude Code`.

## Project

`CTFAgent` is a `Claude Code`-first CTF workspace.

Default user path:

1. configure `Claude Code`
2. run `/setup`
3. provide challenge info
4. let the repo create or inspect a workspace

Do not force users to learn internal scripts before they can start.

## Working Defaults

- Prefer evidence-first analysis over brute force.
- Start with short validating probes and source/metadata reads.
- Use `workspaces/<challenge-id>/` for challenge-local context and artifacts.
- Keep reusable knowledge in `knowledge/`, not only in chat history.
- Treat platform integration as optional. It is only needed for pull/download/spawn/submit workflows.

## Active Skills

Current implemented Skills:

1. `setup/` - User-facing onboarding and workspace setup
2. `ctf-solver-profile/` - Evidence-first solver posture and category switching
3. `challenge-workspace-bootstrap/` - Normalize a challenge into `workspaces/<challenge-id>/`
4. `web-triage/` - Router for web vulnerabilities (JWT, SQLi, SSRF, SSTI, XSS, deserialization)
5. `pwn-triage/` - Router for binary exploitation (initial recon, stack overflow, canary/PIE bypass)
6. `rev-triage/` - Binary identification, packer detection, and static/dynamic RE triage
7. `ctf-knowledge-capture/` - Save solved cases and reusable patterns into Markdown notes
8. `skill-maintainer/` - Turn solve feedback into the smallest safe repo upgrade and block uncontrolled skill growth
9. `browser-automation/` - Headless browser control for XSS and DOM workflows
10. `network-search/` - DuckDuckGo search fallback for external research

Recommended invocation order:

1. `setup`
2. `challenge-workspace-bootstrap`
3. `ctf-solver-profile`
4. one concrete category skill (`web-triage`, `pwn-triage`, or `rev-triage`)
5. optional support skills such as `browser-automation` or `network-search`
6. `ctf-knowledge-capture`
7. `skill-maintainer`

## Roadmap

1. `skill-quality-bar-and-doc-alignment`
2. `regression-target-convention`
3. `crypto-encoding-decision-tree`
4. `web-backdoor-triage`
5. `artifact-inspection-utility`
6. `skill-maintainer`

## Docs

- `docs/README.md`
- `docs/overview.md`
- `docs/workflow.md`
- `docs/workspace.md`
- `docs/skills.md`
- `docs/roadmap.md`
