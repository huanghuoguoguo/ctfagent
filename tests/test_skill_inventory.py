from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "skill-maintainer"
    / "scripts"
    / "check_skill_inventory.py"
)
SPEC = importlib.util.spec_from_file_location("check_skill_inventory", SCRIPT_PATH)
check_skill_inventory = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(check_skill_inventory)


class SkillInventoryTest(unittest.TestCase):
    def test_parse_readme_count(self) -> None:
        text = "当前已实现 **13 个核心 skill**，位于 ..."
        self.assertEqual(check_skill_inventory.parse_readme_count(text), 13)

    def test_parse_claude_active_skills(self) -> None:
        text = """
## Active Skills
1. `ctf-solver-profile/` - ...
2. `web-jwt-triage/` - ...

## Roadmap
"""
        self.assertEqual(
            check_skill_inventory.parse_claude_active_skills(text),
            ["ctf-solver-profile", "web-jwt-triage"],
        )

    def test_parse_roadmap_priorities(self) -> None:
        text = """
## Roadmap
1. `web-xss-triage`
2. `web-backdoor-triage`

## MCP Tools to Integrate (Future)
"""
        self.assertEqual(
            check_skill_inventory.parse_roadmap_priorities(text),
            ["web-xss-triage", "web-backdoor-triage"],
        )


if __name__ == "__main__":
    unittest.main()
