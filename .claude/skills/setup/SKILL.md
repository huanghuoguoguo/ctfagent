---
name: setup
description: Introduce this repository, verify the Claude Code setup at a high level, collect challenge basics, and create or inspect a workspace before solving. Use when the user is new to the repo or asks to get started.
argument-hint: "[challenge brief or setup goal]"
disable-model-invocation: true
---

# Setup

This is the user-facing front door for the repository.

When the user runs `/setup`, do not assume they already know the internal scripts, skill tree, or workspace structure. Your job is to lower setup friction and get them to a usable starting point quickly.

## Main Goals

1. Explain the project in one short paragraph.
2. Confirm what still needs to be configured in Claude Code.
3. Ask for the minimum challenge information needed to start.
4. Create or inspect a workspace when enough information is available.
5. Tell the user what the next best step is.

## Default Behavior

Treat `/setup` as a guided onboarding flow:

- First explain that this repo is a `Claude Code`-first CTF workspace.
- Tell the user they can usually just configure Claude Code, run `/setup`, provide challenge info, and continue solving.
- Keep the explanation short. Do not dump architecture details unless the user asks.
- If the user already included structured challenge details in `/setup`, skip the long explanation and move straight into workspace creation.

## What To Check

If the user wants help configuring the environment, check these items at a high level:

- Claude Code is running in the repository root.
- The repository-local Claude Code config exists at `.claude/settings.local.json`, if this repo expects local settings.
- Required account, endpoint, model, or auth values appear to be configured.

Important:

- Never print secrets, tokens, or full credential values back to the user.
- If config appears incomplete, say what category of value is missing and where it should be configured.
- Prefer phrasing like "set your endpoint/token/model in `.claude/settings.local.json`" instead of echoing sensitive content.

## Minimum Challenge Inputs

Ask for only the fields needed to start:

- title
- category
- target URL, host, or connection info
- statement or short description
- attachment paths, if any
- constraints, if any

If some fields are missing, ask only for the missing essentials. Do not force the user through a long questionnaire.

## Workspace Behavior

When enough challenge information is available, normalize it into `workspaces/<challenge-id>/`.

Prefer the one-shot setup helper first when `/setup` already contains structured fields such as title, category, target, attachments, description, and constraints:

```bash
python3 scripts/setup_challenge.py --input-file <captured-setup-text>
```

This helper accepts labeled text like:

```text
题目标题：Internal Resource Viewer
分类：web
目标：http://127.0.0.1:8080/
附件：/path/to/app.zip
题目描述：The site previews internal resources.
限制：先做低成本验证，不要直接爆破。
```

If the helper reports missing fields, ask only for those missing essentials.

If the helper succeeds, immediately inspect the new workspace:

1. Show the resulting workspace path.
2. Inspect it with:

```bash
python3 scripts/show_challenge.py <workspace-dir>
```

3. Summarize what is now ready.
4. Recommend the next step, usually `ctf-solver-profile` and then a category skill.

If the user did not provide structured fields yet, continue with the guided flow and gather the missing basics first. When you have enough information, you may still use `python3 scripts/init_challenge.py ...` directly.

## Existing Workspace

If the user already has a workspace or points to one under `workspaces/`, inspect it instead of recreating it.

## Response Style

- Be concise and user-facing.
- Prioritize "what to do now".
- Keep internal implementation details in the background.
- Only mention deeper repository structure if the user explicitly asks for it.
- When `/setup` includes enough challenge info, bias toward action: create the workspace instead of asking the user to repeat the same fields.
