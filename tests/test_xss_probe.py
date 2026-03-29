from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "web-xss-triage"
    / "scripts"
    / "xss_probe.py"
)
SPEC = importlib.util.spec_from_file_location("xss_probe", SCRIPT_PATH)
xss_probe = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(xss_probe)


class XSSProbeTest(unittest.TestCase):
    def test_classify_html_text_context(self) -> None:
        body = "<div>Hello <script>alert(1)</script></div>"
        self.assertEqual(
            xss_probe.classify_reflection_context(body, "<script>alert(1)</script>"),
            "html_text",
        )

    def test_classify_attr_double_context(self) -> None:
        body = '<input value="XSSMARK">'
        self.assertEqual(xss_probe.classify_reflection_context(body, "XSSMARK"), "attr_double")

    def test_classify_script_block_context(self) -> None:
        body = "<script>var data = 'XSSMARK';</script>"
        self.assertEqual(xss_probe.classify_reflection_context(body, "XSSMARK"), "script_block")

    def test_recommend_follow_up_for_attr_context(self) -> None:
        assessment, payload = xss_probe.recommend_follow_up("attr_double")
        self.assertIn("quoted attribute", assessment)
        self.assertIn("svg/onload", payload)


if __name__ == "__main__":
    unittest.main()
