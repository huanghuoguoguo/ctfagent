#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SKILLS_DIR = Path(__file__).resolve().parents[2]  # .claude/skills/
if str(_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILLS_DIR))
_PROJECT_ROOT = Path(__file__).resolve().parents[4]  # project root

from __lib__.models import ChallengeInfo
from __lib__.workspace import WorkspaceManager, make_challenge_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a local CTF challenge workspace.")
    parser.add_argument("--title", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--content")
    parser.add_argument("--content-file")
    parser.add_argument("--id")
    parser.add_argument("--platform", default="manual")
    parser.add_argument("--platform-id", default="")
    parser.add_argument("--url", default="")
    parser.add_argument("--attachment", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--workspace-root", default=str(_PROJECT_ROOT / "workspaces"))
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.content and not args.content_file:
        raise SystemExit("one of --content or --content-file is required")

    content = args.content
    if content is None:
        content = Path(args.content_file).expanduser().read_text(encoding="utf-8")

    challenge = ChallengeInfo(
        id=args.id or make_challenge_id(args.title),
        title=args.title,
        category=args.category,
        content=content,
        platform=args.platform,
        platform_id=args.platform_id,
        url=args.url,
        attachments=list(args.attachment),
        tags=list(args.tag),
        constraints=list(args.constraint),
    )
    workspace_dir = WorkspaceManager(args.workspace_root).create(
        challenge,
        overwrite=args.overwrite,
    )
    print(workspace_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
