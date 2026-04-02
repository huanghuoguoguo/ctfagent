#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SKILLS_DIR = Path(__file__).resolve().parents[2]  # .claude/skills/
if str(_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILLS_DIR))

_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # project root

from __lib__.models import ChallengeInfo
from __lib__.setup_parser import parse_setup_text
from __lib__.workspace import WorkspaceManager, make_challenge_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a challenge workspace from /setup-style text.")
    parser.add_argument("--input")
    parser.add_argument("--input-file")
    parser.add_argument("--workspace-root", default=str(_PROJECT_ROOT / "workspaces"))
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.input and not args.input_file:
        raise SystemExit("one of --input or --input-file is required")

    raw_text = args.input
    if raw_text is None:
        raw_text = Path(args.input_file).expanduser().read_text(encoding="utf-8")

    request = parse_setup_text(raw_text)
    missing = request.missing_fields()
    if missing:
        print(
            json.dumps(
                {
                    "ok": False,
                    "missing_fields": missing,
                    "parsed": {
                        "title": request.title,
                        "category": request.category,
                        "url": request.url,
                        "attachments": request.attachments,
                        "constraints": request.constraints,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    challenge = ChallengeInfo(
        id=make_challenge_id(request.title),
        title=request.title,
        category=request.category,
        content=request.content,
        platform=request.platform,
        platform_id=request.platform_id,
        url=request.url,
        attachments=request.attachments,
        constraints=request.constraints,
    )
    workspace_dir = WorkspaceManager(args.workspace_root).create(
        challenge,
        overwrite=args.overwrite,
    )
    print(
        json.dumps(
            {
                "ok": True,
                "workspace_dir": str(workspace_dir),
                "id": challenge.id,
                "title": challenge.title,
                "category": challenge.category,
                "url": challenge.url,
                "attachments": request.attachments,
                "constraints": request.constraints,
                "fallback_content_used": request.fallback_content_used,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
