---
name: ctf-knowledge-capture
description: Capture solved CTF challenges into organized local Markdown knowledge files and extract reusable exploit patterns from them. Use when finishing a challenge, reviewing a solve, converting terminal notes into durable writeups, or updating local CTF knowledge so future agents can search, compare, and maintain tactics over time.
---

# CTF Knowledge Capture

Use this skill after solving or reviewing a challenge. The goal is to preserve:

- what the challenge was
- how the exploit chain worked
- what misled you
- what reusable pattern should influence future skills

## CRITICAL: Programmatic Access Only

**You must NEVER manually edit files in `knowledge/`.** All memory operations must go through the schema module:

```bash
# Create writeup (ONLY valid way)
python3 -c "
from pathlib import Path
from src.memory.schema import create_writeup, update_index

path = create_writeup(
    Path('.'),
    title='Challenge Name',
    category='web',
    slug='challenge-name',
    source='CTF Platform',
    target='http://target:port',
    tags=['ssrf', 'rce'],
    status='solved'
)
update_index(Path('.'))
print(path)
"

# Create pattern (ONLY valid way)
python3 -c "
from pathlib import Path
from src.memory.schema import create_pattern, update_index

path = create_pattern(
    Path('.'),
    title='SSRF to LFI to RCE',
    category='web',
    slug='ssrf-lfi-rce',
    chain_summary='SSRF via URL fetcher to file:// read to localhost RCE',
    tags=['ssrf', 'lfi', 'rce'],
    status='active'
)
update_index(Path('.'))
print(path)
"

# Query existing notes
python3 src/memory/query.py --root . --kind writeup --category web --tag ssrf

# Validate all knowledge files
python3 -c "
from pathlib import Path
from src.memory.schema import validate_all
errors = validate_all(Path('.'))
for path, msgs in errors.items():
    print(f'{path}: {msgs}')
"
```

**Violations:**
- Do NOT use `Write` tool on `knowledge/*.md`
- Do NOT use `Edit` tool on `knowledge/*.md`
- Do NOT manually create files in `knowledge/`

## Schema Enforcement

All notes are validated against strict schemas:

**Writeup required fields:**
- `title` - Challenge name
- `category` - web/pwn/rev/crypto/misc/forensics
- `slug` - Stable file identifier
- `status` - draft/solved/archived

**Pattern required fields:**
- `title` - Pattern name
- `category` - Category
- `slug` - Stable file identifier
- `status` - draft/active/archived

## Output Layout

```text
knowledge/
├── index.md              # Auto-generated, do not edit
├── writeups/
│   └── web/
│       └── slug.md
└── patterns/
    └── web/
        └── slug.md
```

## Workflow

1. Validate the solve is complete.
2. Create writeup via `create_writeup()`.
3. Fill in the body content (you CAN edit the body after creation).
4. Decide if pattern is needed, create via `create_pattern()`.
5. Run `update_index()` to regenerate index.
6. If pattern affects future solving, update related skill.

## Writeup Body Sections

After programmatic creation, fill in:

- **Challenge Summary** - Source, target, goal
- **Initial Signals** - Entry point, hints, first probe
- **Exploit Chain** - Numbered steps
- **Key Evidence** - What confirmed the path
- **Dead Ends** - What didn't work
- **Payloads And Commands** - Working code
- **Flag / Outcome** - Result
- **Reusable Lessons** - What to remember
- **Pattern Candidates** - Link to patterns

## Pattern Body Sections

- **Chain Summary** - One-line description
- **Preconditions** - When this applies
- **Cheap Probes** - Quick tests
- **Telltale Evidence** - What to look for
- **Escalation Order** - Step sequence
- **Common Mistakes** - What to avoid
- **Payload Shapes** - Example payloads
- **Related Writeups** - Links
- **Skill Impact** - What skill to update

## Decision Rules

- One-off trick → writeup only
- Repeated pattern → create pattern note
- Pattern changes solving order → update skill
- Keep notes concise, grep-friendly
