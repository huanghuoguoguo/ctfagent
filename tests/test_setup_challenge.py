from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ctfagent.setup_parser import parse_setup_text


class SetupChallengeTest(unittest.TestCase):
    def test_parse_setup_text_with_structured_fields(self) -> None:
        request = parse_setup_text(
            "\n".join(
                [
                    "题目标题：Internal Resource Viewer",
                    "分类：web",
                    "目标：http://127.0.0.1:8080/",
                    "附件：/tmp/app.zip, /tmp/hint.txt",
                    "题目描述：The site previews internal resources.",
                    "限制：先做低成本验证，不要直接爆破。",
                ]
            )
        )

        self.assertEqual(request.title, "Internal Resource Viewer")
        self.assertEqual(request.category, "web")
        self.assertEqual(request.url, "http://127.0.0.1:8080/")
        self.assertEqual(request.attachments, ["/tmp/app.zip", "/tmp/hint.txt"])
        self.assertEqual(request.constraints, ["先做低成本验证", "不要直接爆破。"])
        self.assertEqual(request.content, "The site previews internal resources.")

    def test_parse_setup_text_generates_fallback_content(self) -> None:
        request = parse_setup_text(
            "\n".join(
                [
                    "Title: JWT Warmup",
                    "Category: web",
                    "Target: http://127.0.0.1:5005/",
                ]
            )
        )

        self.assertTrue(request.fallback_content_used)
        self.assertIn("Target: http://127.0.0.1:5005/", request.content)
        self.assertEqual(request.missing_fields(), [])

    def test_setup_script_creates_workspace_from_input_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            attachment = temp_path / "app.py"
            attachment.write_text("print('hello')\n", encoding="utf-8")
            input_file = temp_path / "setup.txt"
            input_file.write_text(
                "\n".join(
                    [
                        "题目标题：Internal Resource Viewer",
                        "分类：web",
                        "目标：http://127.0.0.1:8080/",
                        f"附件：{attachment}",
                        "题目描述：The site previews internal resources.",
                    ]
                ),
                encoding="utf-8",
            )

            script = Path(__file__).resolve().parents[1] / "scripts" / "setup_challenge.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--input-file",
                    str(input_file),
                    "--workspace-root",
                    str(temp_path / "workspaces"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            workspace_dir = Path(payload["workspace_dir"])
            self.assertTrue(payload["ok"])
            self.assertTrue((workspace_dir / "challenge.md").exists())
            self.assertTrue((workspace_dir / "metadata.json").exists())
            self.assertTrue((workspace_dir / "attachments" / "app.py").exists())


if __name__ == "__main__":
    unittest.main()
