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
    / "skill_growth_guard.py"
)
SPEC = importlib.util.spec_from_file_location("skill_growth_guard", SCRIPT_PATH)
skill_growth_guard = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(skill_growth_guard)


class SkillGrowthGuardTest(unittest.TestCase):
    def test_overlap_prefers_update(self) -> None:
        result = skill_growth_guard.audit_growth(
            candidate_skill="web-backdoor-triage",
            frequency=3,
            overlaps=["web-ssrf-to-rce-triage"],
            duplicate_concepts=[],
            scope_stable=True,
            has_script=True,
            has_test=True,
            has_target=True,
            doc_sync=True,
        )
        self.assertEqual(result["classification"], "prefer_update")

    def test_duplicate_concept_stays_in_backlog(self) -> None:
        result = skill_growth_guard.audit_growth(
            candidate_skill="skill-quality-bar-and-doc-alignment",
            frequency=3,
            overlaps=[],
            duplicate_concepts=["skill-quality-bar-and-doc-alignment"],
            scope_stable=True,
            has_script=True,
            has_test=True,
            has_target=True,
            doc_sync=True,
        )
        self.assertEqual(result["classification"], "backlog_only")

    def test_missing_support_blocks_new_skill(self) -> None:
        result = skill_growth_guard.audit_growth(
            candidate_skill="web-backdoor-triage",
            frequency=3,
            overlaps=[],
            duplicate_concepts=[],
            scope_stable=True,
            has_script=False,
            has_test=True,
            has_target=False,
            doc_sync=False,
        )
        self.assertEqual(result["classification"], "block_new_skill")
        self.assertIn("add at least one thin helper script", result["required_actions"])
        self.assertIn("add at least one minimal local lab or fixture", result["required_actions"])

    def test_repeated_stable_supported_skill_is_allowed(self) -> None:
        result = skill_growth_guard.audit_growth(
            candidate_skill="web-backdoor-triage",
            frequency=3,
            overlaps=[],
            duplicate_concepts=[],
            scope_stable=True,
            has_script=True,
            has_test=True,
            has_target=True,
            doc_sync=True,
        )
        self.assertEqual(result["classification"], "allow_new_skill")
        self.assertIn("create web-backdoor-triage/SKILL.md", result["required_actions"])


if __name__ == "__main__":
    unittest.main()
