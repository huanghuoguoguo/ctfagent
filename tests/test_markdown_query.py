from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ctfagent.markdown import dump_frontmatter, split_frontmatter
from ctfagent.query import iter_markdown_documents, query_documents


class MarkdownQueryTest(unittest.TestCase):
    def test_frontmatter_roundtrip(self) -> None:
        text = dump_frontmatter(
            {
                "doc_kind": "writeup",
                "title": "SQLite Blind SQL Injection",
                "category": "web",
                "tags": ["sqlite", "blind-sqli"],
            }
        ) + "\n# SQLite Blind SQL Injection\n"

        metadata, body = split_frontmatter(text)
        self.assertEqual(metadata["doc_kind"], "writeup")
        self.assertEqual(metadata["category"], "web")
        self.assertEqual(metadata["tags"], ["sqlite", "blind-sqli"])
        self.assertIn("# SQLite Blind SQL Injection", body)

    def test_query_documents_filters_by_kind_and_tag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            note_path = root / "knowledge" / "writeups" / "web"
            note_path.mkdir(parents=True, exist_ok=True)
            note = note_path / "sqlite.md"
            note.write_text(
                dump_frontmatter(
                    {
                        "doc_kind": "writeup",
                        "title": "SQLite Blind SQL Injection",
                        "category": "web",
                        "status": "solved",
                        "tags": ["sqlite", "blind-sqli"],
                    }
                )
                + "\n# SQLite Blind SQL Injection\n\nBoolean oracle.\n",
                encoding="utf-8",
            )

            docs = iter_markdown_documents(root)
            matches = query_documents(docs, doc_kind="writeup", tags=["sqlite"])
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0].title, "SQLite Blind SQL Injection")

    def test_query_script_outputs_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            note_path = root / "knowledge" / "patterns" / "web"
            note_path.mkdir(parents=True, exist_ok=True)
            note = note_path / "ssrf.md"
            note.write_text(
                dump_frontmatter(
                    {
                        "doc_kind": "pattern",
                        "title": "SSRF Pattern",
                        "category": "web",
                        "status": "active",
                        "tags": ["ssrf"],
                    }
                )
                + "\n# SSRF Pattern\n\nPivot localhost.\n",
                encoding="utf-8",
            )
            script = Path(__file__).resolve().parents[1] / "scripts" / "query_markdown.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--root",
                    str(root),
                    "--kind",
                    "pattern",
                    "--tag",
                    "ssrf",
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn('"title": "SSRF Pattern"', result.stdout)


if __name__ == "__main__":
    unittest.main()
