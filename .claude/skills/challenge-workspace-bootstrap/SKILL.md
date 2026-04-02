---
name: challenge-workspace-bootstrap
description: Create or inspect a local challenge workspace before solving. Use when the user gives a new题面、附件目录、目标 URL、平台信息，或当仓库里还没有标准化的 `workspaces/<challenge-id>/` 包，需要让 Claude Code 先把 challenge 组织成统一入口再开始分析。
---

# Challenge Workspace Bootstrap

This skill standardizes new challenges for `Claude Code`. It is not a Python host workflow.

Use it to create a local workspace that `cc` can read directly:

- `challenge.md` for the human/model-readable statement
- `metadata.json` for structured fields
- `attachments/` for original files
- `notes.md` for active solving notes
- `artifacts/` for generated outputs

## When To Use

- A new challenge arrives as plain text, screenshots, or loose files.
- The user gives you a target URL and one or more attachments.
- You want a stable directory before invoking category skills.
- You need to inspect an existing workspace quickly.

## Quick Start

Create a new workspace from inline text:

```bash
python3 .claude/skills/challenge-workspace-bootstrap/scripts/init_workspace.py \
  --title "Internal Resource Viewer" \
  --category web \
  --url http://127.0.0.1:8080/ \
  --content "The site previews internal resources." \
  --constraint "Prefer short validating probes first."
```

Create a new workspace from a saved statement file and attachments:

```bash
python3 .claude/skills/challenge-workspace-bootstrap/scripts/init_workspace.py \
  --title "Target Name" \
  --category web \
  --content-file /path/to/statement.md \
  --attachment /path/to/app.zip \
  --attachment /path/to/hint.txt
```

Inspect an existing workspace:

```bash
python3 .claude/skills/challenge-workspace-bootstrap/scripts/show_challenge.py workspaces/internal-resource-viewer
```

## Workflow

1. Create or locate a stable challenge id.
2. Normalize the challenge into `workspaces/<challenge-id>/`.
3. Read `challenge.md` before jumping into exploitation.
4. Keep temporary reasoning in `notes.md`.
5. Save scripts and dumps in `artifacts/`.
6. After solving, switch to `ctf-knowledge-capture`.

## Rules

- Do not leave challenge context only in chat history.
- Prefer attaching original files instead of pasting large blobs into notes.
- Keep platform metadata and solving notes separate.
- Do not treat this workspace layer as agent orchestration; it is only shared structure for `cc`.

## Notes

- The bootstrap script uses `__lib__` shared helpers for file packaging.
- This repository's solving loop remains `Claude Code` + `Skills` + local tools.
