# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CTFAgent** is a CTF (Capture The Flag) automation system using Claude Code and Claude Agent SDK. The project follows a two-phase approach:

- **Phase 1** (Current): Direct Claude Code usage for CTF workflow validation
- **Phase 2** (Future): Python automation with Claude Agent SDK

## Naming Conventions

Use these exact terms in all documentation and code:

- `Claude Code` - The CLI tool
- `Claude Agent SDK` - The Python/TypeScript SDK (formerly Claude Code SDK)
- `Skills` - CTF playbooks stored in `.claude/skills/`
- `MCP` - Model Context Protocol tools

## Project Structure

```
ctfagent/
├── docs/                   # Architecture documentation
│   ├── claude-agent-sdk-ctf-agent-design.md    # Master index
│   ├── phase1-claude-code-ctf-workflow.md      # Phase 1 guide
│   ├── phase2-agent-sdk-python-automation.md   # Phase 2 guide
│   └── agent-sdk-official-notes.md             # SDK reference
├── .claude/
│   ├── skills/            # Active CTF skills/playbooks
│   └── settings.local.json # Local settings with env vars and permissions
├── knowledge/             # Local writeups and reusable exploit patterns
├── workspaces/            # Challenge workspaces
└── .mcp.json             # MCP server configuration (future)
```

## Phase 1 Development Mode

Currently in Phase 1: Validate Claude Code can solve CTF challenges interactively before building automation.

Key aspects:
- Each challenge gets an isolated workspace under `workspaces/<challenge-id>/`
- Skills for CTF categories go in `.claude/skills/<skill-name>/SKILL.md`
- Tools and MCP servers provide CTF capabilities
- Security: Challenge execution should be sandboxed; credentials isolated

## Current Working Method

The repository now has a concrete Phase 1 solving loop:

1. Start with `ctf-solver-profile`
2. Invoke one concrete category skill after evidence supports the category
3. Solve and preserve key artifacts during the process
4. Save the result with `ctf-knowledge-capture`
5. Promote repeated exploit chains into `knowledge/patterns/`

Do not start with long exploit payloads or broad guessing. Default to short validating probes and source/metadata acquisition first.

## Active Skills

Current implemented Skills:

1. `ctf-solver-profile/` - Front-door solver posture, evidence-first reasoning, category switching rules
2. `web-ssrf-to-rce-triage/` - Web SSRF, local file read, source disclosure, and localhost pivot workflow
3. `ctf-knowledge-capture/` - Save solved cases and reusable patterns into organized Markdown notes

Recommended invocation order:

1. `ctf-solver-profile`
2. one category skill such as `web-ssrf-to-rce-triage`
3. `ctf-knowledge-capture` after solving or when consolidating findings

## Skill Categories to Create Next

After the current baseline, prioritize these additional Skills:

1. `pwn-initial-recon/` - Binary analysis SOP
2. `web-sqli-triage/` - SQL injection detection
3. `web-ssti-triage/` - SSTI detection
4. `crypto-encoding-decision-tree/` - Crypto identification
5. `rev-unpack-and-trace/` - Reverse engineering workflow
6. `web-backdoor-triage/` - Blank-page PHP backdoors, short-parameter `assert/eval/system` checks

## MCP Tools to Integrate

Priority CTF tools for MCP wrapping:

- `nmap`, `ffuf`, `sqlmap`, `gobuster`, `dirsearch` (Web)
- `pwntools` execution wrapper (Pwn)
- `gdb`/`gef`/`pwndbg` wrapper (Pwn)
- `angr`, `z3` (Reverse/Crypto)
- `binwalk`, `foremost`, `exiftool` (Forensics)
- `ghidra`/`rizin`/`radare2` batch interface (Reverse)

## Security Boundaries

- Each challenge: isolated workspace directory
- Sensitive credentials: never in agent workspace
- High-risk tools: container or sandbox execution
- Network: allowlist egress, challenge environments only
- Flag submission: via proxy tool, token not exposed to model

## Knowledge Base

Persist solved challenge knowledge under `knowledge/`:

- `knowledge/writeups/<category>/` - One file per concrete challenge
- `knowledge/patterns/<category>/` - Reusable exploit chains and heuristics
- `knowledge/index.md` - Table of contents

Current web examples:

- `knowledge/writeups/web/internal-resource-viewer.md`
- `knowledge/writeups/web/171-80-2-169-18148.md`
- `knowledge/patterns/web/ssrf-to-lfi-to-localhost-rce.md`
- `knowledge/patterns/web/obfuscated-assert-get-rce.md`

When a challenge is solved, update the writeup first. Only update a pattern or a Skill when the lesson generalizes.

## Custom Tools (Phase 2)

When implementing Phase 2 Python automation, prioritize these custom tools:

1. `init_challenge` - Create workspace, download/extract attachments
2. `submit_flag` - Submit to platform without exposing token
3. `query_playbook` - Query knowledge base
4. `run_solver` - Execute solver in sandbox
5. `inspect_artifact` - File metadata and hash
6. `spawn_target` - Start Docker challenge or connect to remote

## Documentation References

- Phase 1 workflow: `docs/phase1-claude-code-ctf-workflow.md`
- Phase 2 architecture: `docs/phase2-agent-sdk-python-automation.md`
- SDK notes: `docs/agent-sdk-official-notes.md`
- Master index: `docs/claude-agent-sdk-ctf-agent-design.md`
- Solver profile: `.claude/skills/ctf-solver-profile/SKILL.md`
- Knowledge capture: `.claude/skills/ctf-knowledge-capture/SKILL.md`

## Environment Configuration

Local settings are in `.claude/settings.local.json` with:
- Custom Anthropic API endpoint and model
- Tool permissions configured
- Bash restrictions for security

## Practical Defaults

When solving in this repo:

- Prefer evidence-rich reads over brute force
- Use the smallest probe that can confirm a hypothesis
- Record dead ends, not just successes
- Treat blank dynamic pages as possible backdoors, not as empty targets
- Preserve commands, source snippets, and flag paths in `knowledge/`
