---
name: ctf-knowledge-capture
description: Capture solved CTF challenges into organized local Markdown knowledge files and extract reusable exploit patterns from them. Use when finishing a challenge, reviewing a solve, converting terminal notes into durable writeups, or updating local CTF knowledge so future agents can search, compare, and maintain tactics over time.
---

# CTF Knowledge Capture

Use this skill after solving or reviewing a challenge. The goal is not to write a polished blog post. The goal is to preserve:

- what the challenge was
- how the exploit chain worked
- what misled you
- what reusable pattern should influence future skills

Always save notes to local Markdown files under `knowledge/`.

## Output Layout

Use this structure:

```text
knowledge/
├── index.md
├── writeups/
│   ├── web/
│   ├── pwn/
│   ├── rev/
│   ├── crypto/
│   ├── misc/
│   └── forensics/
└── patterns/
    ├── web/
    ├── pwn/
    ├── rev/
    ├── crypto/
    ├── misc/
    └── forensics/
```

Use `writeups/` for one concrete target. Use `patterns/` for reusable chains such as `ssrf-to-lfi-to-localhost-rce`.

## Workflow

1. Decide the category.
2. Create or update one writeup file.
3. Decide whether the solve teaches a reusable pattern.
4. Create or update one pattern file if needed.
5. Update `knowledge/index.md` with links.
6. If the pattern changes future solving behavior, update the related skill separately.

## Quick Start

Create a new writeup scaffold:

```bash
python3 .claude/skills/ctf-knowledge-capture/scripts/new_note.py \
  --root /home/yhh/ctfagent \
  --kind writeup \
  --category web \
  --slug internal-resource-viewer \
  --title "Internal Resource Viewer"
```

Create a new reusable pattern scaffold:

```bash
python3 .claude/skills/ctf-knowledge-capture/scripts/new_note.py \
  --root /home/yhh/ctfagent \
  --kind pattern \
  --category web \
  --slug ssrf-to-lfi-to-localhost-rce \
  --title "SSRF to LFI to Localhost RCE"
```

Read `references/templates.md` when you need the exact section meanings.

## Writeup Rules

Every writeup must answer these questions:

- What was the vulnerable surface?
- What evidence proved the intended exploit path?
- What dead ends or false assumptions slowed the solve?
- What was the minimal working exploit chain?
- Which detail should be promoted into a reusable pattern or skill rule?

Keep writeups concise. Prefer factual bullets over long prose.

## Pattern Rules

Create or update a pattern note only when the lesson generalizes across multiple challenges.

A pattern note should contain:

- the chain name
- preconditions
- cheap probes
- telltale evidence
- common mistakes
- escalation order
- example payload shapes
- links to supporting writeups

Do not turn every challenge into a new pattern. A one-off trick belongs only in the writeup.

## Decision Rules

- If the solve has one target-specific quirk, update only the writeup.
- If the same branch will likely appear again, update or create a pattern note.
- If the pattern changes the order of operations in future solving, update the related skill after saving the knowledge files.
- If the note becomes long, compress narrative and keep only evidence, chain, and reusable lessons.

## Maintenance

Use `knowledge/index.md` as the table of contents.

Keep each note easy to grep:

- use stable slugs in file names
- use one H1 only
- keep exploit chain in its own section
- include keywords such as `ssrf`, `lfi`, `localhost`, `rce`

Read `references/templates.md` before changing note structure. Keep template changes centralized there instead of drifting formats across many files.
