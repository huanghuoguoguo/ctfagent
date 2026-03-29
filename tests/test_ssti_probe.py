from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "web-ssti-triage"
    / "scripts"
    / "ssti_probe.py"
)
SPEC = importlib.util.spec_from_file_location("ssti_probe", SCRIPT_PATH)
ssti_probe = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(ssti_probe)


class SSTIProbeTest(unittest.TestCase):
    def test_evaluate_probe_flags_literal_reflection(self) -> None:
        result = ssti_probe.evaluate_probe("Hello {{7*7}}", "{{7*7}}", ["49"])
        self.assertTrue(result["payload_reflected"])
        self.assertFalse(result["looks_evaluated"])

    def test_infer_engine_prefers_jinja2_when_string_repeat_hits(self) -> None:
        probe_results = {
            "jinja_math": {"looks_evaluated": True, "expected_hits": ["49"]},
            "jinja_string": {"looks_evaluated": True, "expected_hits": ["7777777"]},
            "dollar_math": {"looks_evaluated": False, "expected_hits": []},
            "erb_math": {"looks_evaluated": False, "expected_hits": []},
        }
        engine, next_probe = ssti_probe.infer_engine(probe_results)
        self.assertEqual(engine, "Jinja2 is likely")
        self.assertEqual(next_probe, "{{config.FLAG}}")

    def test_infer_engine_falls_back_to_freemarker(self) -> None:
        probe_results = {
            "jinja_math": {"looks_evaluated": False, "expected_hits": []},
            "jinja_string": {"looks_evaluated": False, "expected_hits": []},
            "dollar_math": {"looks_evaluated": True, "expected_hits": ["49"]},
            "erb_math": {"looks_evaluated": False, "expected_hits": []},
        }
        engine, next_probe = ssti_probe.infer_engine(probe_results)
        self.assertEqual(engine, "Freemarker or EL-style handling is plausible")
        self.assertEqual(next_probe, "${7*'7'}")


if __name__ == "__main__":
    unittest.main()
