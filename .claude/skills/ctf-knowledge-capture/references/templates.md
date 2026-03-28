# Note Templates

Use the generated templates as the default format. Keep sections stable so agents can grep and compare notes across challenges.

## Metadata Rules

- Every note should start with frontmatter.
- Keep these keys stable when available:
  `doc_kind`, `title`, `category`, `slug`, `created`, `status`, `tags`
- Treat Markdown body text as human-readable evidence and frontmatter as agent-queryable metadata.

## Writeup Template Intent

- `Challenge Summary`: identify the target and the win condition.
- `Initial Signals`: preserve the earliest evidence that should influence future triage.
- `Exploit Chain`: keep the minimal ordered path from entry to outcome.
- `Key Evidence`: include source snippets, endpoint behavior, or file paths that proved the chain.
- `Dead Ends`: preserve false assumptions worth avoiding later.
- `Payloads And Commands`: keep only the payloads that mattered.
- `Reusable Lessons`: summarize what should transfer to future targets.
- `Pattern Candidates`: decide whether to update an existing pattern or create a new one.

## Pattern Template Intent

- `Chain Summary`: name the exploit family clearly.
- `Preconditions`: state what must be true before the chain is viable.
- `Cheap Probes`: list the lowest-cost tests first.
- `Telltale Evidence`: record strong indicators, not generic possibilities.
- `Escalation Order`: define the order future agents should follow.
- `Common Mistakes`: store recurring wrong turns.
- `Payload Shapes`: keep abstract payload forms rather than challenge-specific clutter.
- `Related Writeups`: link concrete supporting cases.
- `Skill Impact`: state whether a skill should change because of this pattern.

## Naming Rules

- File names must use lowercase slugs with hyphens.
- Prefer challenge names for writeups and exploit-chain names for patterns.
- Do not encode dates in filenames. Use metadata inside the file instead.

## Editing Rules

- Preserve headings so local search remains reliable.
- Prefer bullets over paragraphs.
- Do not duplicate large chunks between a writeup and a pattern note. Link instead.
