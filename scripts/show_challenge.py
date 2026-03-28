#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ctfagent.workspace import WorkspaceManager


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <workspace-dir>", file=sys.stderr)
        return 2

    challenge = WorkspaceManager().load(sys.argv[1])
    print(f"# {challenge.title}")
    print(f"- ID: {challenge.id}")
    print(f"- Category: {challenge.category}")
    print(f"- Platform: {challenge.platform}")
    print(f"- URL: {challenge.url or '(not provided)'}")
    print("")
    print("## Description")
    print("")
    print(challenge.content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
