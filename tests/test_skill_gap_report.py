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
    / "skill_gap_report.py"
)
SPEC = importlib.util.spec_from_file_location("skill_gap_report", SCRIPT_PATH)
skill_gap_report = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(skill_gap_report)


class SkillGapReportTest(unittest.TestCase):
    def test_overlap_prefers_update_skill(self) -> None:
        result = skill_gap_report.classify_gap(
            {"overlap_existing_skill", "missing_script"},
            frequency=3,
            existing_skill="web-jwt-triage",
            candidate_skill=None,
        )
        self.assertEqual(result["classification"], "update_skill")
        self.assertIn("update web-jwt-triage/SKILL.md", result["actions"])

    def test_missing_script_prefers_new_script(self) -> None:
        result = skill_gap_report.classify_gap(
            {"repeated_manual_step", "missing_script"},
            frequency=2,
            existing_skill=None,
            candidate_skill="web-xss-triage",
        )
        self.assertEqual(result["classification"], "new_script")

    def test_new_skill_requires_repetition(self) -> None:
        result = skill_gap_report.classify_gap(
            {"repeated_pattern"},
            frequency=2,
            existing_skill=None,
            candidate_skill="web-xss-triage",
        )
        self.assertEqual(result["classification"], "new_skill")
        self.assertIn("create web-xss-triage/SKILL.md", result["actions"])
        self.assertIn("run skill_growth_guard.py before creating the new directory", result["actions"])

    def test_one_off_goes_to_backlog(self) -> None:
        result = skill_gap_report.classify_gap(
            {"one_off_insight"},
            frequency=1,
            existing_skill=None,
            candidate_skill=None,
        )
        self.assertEqual(result["classification"], "backlog_only")

    def test_doc_drift_points_to_real_docs(self) -> None:
        result = skill_gap_report.classify_gap(
            {"doc_drift"},
            frequency=1,
            existing_skill="skill-maintainer",
            candidate_skill=None,
        )
        self.assertEqual(result["classification"], "update_skill")
        self.assertIn("sync docs/skills.md", result["actions"])
        self.assertIn("sync docs/roadmap.md", result["actions"])


if __name__ == "__main__":
    unittest.main()
