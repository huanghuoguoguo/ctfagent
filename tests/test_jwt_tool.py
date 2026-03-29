from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "skills"
    / "web-jwt-triage"
    / "scripts"
    / "jwt_tool.py"
)
SPEC = importlib.util.spec_from_file_location("jwt_tool", SCRIPT_PATH)
jwt_tool = importlib.util.module_from_spec(SPEC)
assert SPEC is not None
assert SPEC.loader is not None
SPEC.loader.exec_module(jwt_tool)


class JWTToolTest(unittest.TestCase):
    def test_sign_and_verify_hs256(self) -> None:
        token = jwt_tool.sign_hs256({"alg": "HS256", "typ": "JWT"}, {"sub": "guest"}, "secret123")
        self.assertTrue(jwt_tool.verify_hs256(token, "secret123"))
        self.assertFalse(jwt_tool.verify_hs256(token, "wrongsecret"))

    def test_make_none_token_rewrites_alg(self) -> None:
        original = jwt_tool.sign_hs256({"alg": "HS256", "typ": "JWT"}, {"role": "guest"}, "secret123")
        header, payload, _ = jwt_tool.decode_token(original)
        token = jwt_tool.make_none_token(header, jwt_tool.apply_updates(payload, ["role=admin"]))
        new_header, new_payload, signature = jwt_tool.decode_token(token)
        self.assertEqual(new_header["alg"], "none")
        self.assertEqual(new_payload["role"], "admin")
        self.assertEqual(signature, b"")

    def test_bruteforce_secret_from_wordlist(self) -> None:
        token = jwt_tool.sign_hs256({"alg": "HS256", "typ": "JWT"}, {"sub": "guest"}, "secret123")
        with tempfile.TemporaryDirectory() as temp_dir:
            wordlist = Path(temp_dir) / "secrets.txt"
            wordlist.write_text("admin\nsecret123\nletmein\n", encoding="utf-8")
            candidates = wordlist.read_text(encoding="utf-8").splitlines()
            found = None
            for candidate in candidates:
                if jwt_tool.verify_hs256(token, candidate):
                    found = candidate
                    break
            self.assertEqual(found, "secret123")

    def test_inspect_suggests_checks(self) -> None:
        token = jwt_tool.sign_hs256(
            {"alg": "HS256", "typ": "JWT", "kid": "debug"},
            {"role": "guest"},
            "secret123",
        )
        result = jwt_tool.inspect_token(token)
        self.assertIn("Check for weak shared secrets and re-signing opportunities", result["recommended_checks"])
        self.assertIn("Inspect header-driven key selection fields", result["recommended_checks"])
        self.assertIn("Change the smallest authorization claim and re-test one protected endpoint", result["recommended_checks"])


if __name__ == "__main__":
    unittest.main()
