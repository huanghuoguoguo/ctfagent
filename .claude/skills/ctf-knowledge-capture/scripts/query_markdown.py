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

from __lib__.query import iter_markdown_documents, query_documents


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query markdown notes by frontmatter metadata.")
    parser.add_argument("--root", default=str(_PROJECT_ROOT))
    parser.add_argument("--scope", action="append")
    parser.add_argument("--kind")
    parser.add_argument("--category")
    parser.add_argument("--status")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--text")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.root).resolve()
    documents = iter_markdown_documents(root, scopes=args.scope)
    matches = query_documents(
        documents,
        doc_kind=args.kind,
        category=args.category,
        status=args.status,
        tags=args.tag or None,
        text=args.text,
    )[: args.limit]

    if args.json:
        print(
            json.dumps(
                [
                    {
                        "path": doc.path.relative_to(root).as_posix(),
                        "title": doc.title,
                        "metadata": doc.metadata,
                    }
                    for doc in matches
                ],
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    for doc in matches:
        print(
            f"{doc.metadata.get('doc_kind','note')}\t"
            f"{doc.metadata.get('category','')}\t"
            f"{doc.metadata.get('status','')}\t"
            f"{doc.path.relative_to(root).as_posix()}\t"
            f"{doc.title}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
