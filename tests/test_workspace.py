from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SKILLS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "skills"
if str(_SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILLS_DIR))

from __lib__.models import ChallengeInfo
from __lib__.workspace import WorkspaceManager


class WorkspaceManagerTest(unittest.TestCase):
    def test_create_workspace_from_challenge(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            attachment = temp_path / "app.py"
            attachment.write_text("print('hello')\n", encoding="utf-8")

            challenge = ChallengeInfo(
                id="web-hello",
                title="Web Hello",
                category="web",
                content="Visit the target and find the flag.",
                url="http://127.0.0.1:8080",
                attachments=[str(attachment)],
                constraints=["Do not brute force."],
            )

            manager = WorkspaceManager(temp_path / "workspaces")
            workspace_dir = manager.create(challenge)

            self.assertTrue((workspace_dir / "challenge.md").exists())
            self.assertTrue((workspace_dir / "metadata.json").exists())
            self.assertTrue((workspace_dir / "notes.md").exists())
            self.assertEqual(
                (workspace_dir / "attachments" / "app.py").read_text(encoding="utf-8"),
                "print('hello')\n",
            )

            metadata = json.loads((workspace_dir / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["attachments"], ["attachments/app.py"])

    def test_load_workspace_restores_description(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            challenge = ChallengeInfo(
                id="rev-intro",
                title="Rev Intro",
                category="rev",
                content="Recover the password from the binary.",
            )

            manager = WorkspaceManager(temp_path / "workspaces")
            workspace_dir = manager.create(challenge)
            loaded = manager.load(workspace_dir)

            self.assertEqual(loaded.id, "rev-intro")
            self.assertEqual(loaded.title, "Rev Intro")
            self.assertEqual(loaded.content, "Recover the password from the binary.")

    def test_init_script_creates_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            script = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "challenge-workspace-bootstrap" / "scripts" / "init_workspace.py"
            result = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--title",
                    "Misc One",
                    "--category",
                    "misc",
                    "--content",
                    "Decode the archive.",
                    "--workspace-root",
                    str(temp_path / "workspaces"),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            workspace_dir = Path(result.stdout.strip())
            self.assertTrue((workspace_dir / "challenge.md").exists())
            self.assertIn("misc-one", str(workspace_dir))


if __name__ == "__main__":
    unittest.main()
