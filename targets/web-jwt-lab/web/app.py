from __future__ import annotations

import base64
import hashlib
import hmac
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 5005
WEAK_SECRET = "secret123"
FLAG = "CTF{jwt_none_and_weak_hmac_are_both_real_paths}"


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def encode_segment(data: dict) -> str:
    return b64url_encode(json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def sign_hs256(header: dict, payload: dict, secret: str) -> str:
    header_part = encode_segment(header)
    payload_part = encode_segment(payload)
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{b64url_encode(signature)}"


def decode_token(token: str) -> tuple[dict, dict, bytes]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid token format")
    header = json.loads(b64url_decode(parts[0]).decode("utf-8"))
    payload = json.loads(b64url_decode(parts[1]).decode("utf-8"))
    signature = b64url_decode(parts[2]) if parts[2] else b""
    return header, payload, signature


def verify_hs256(token: str, secret: str) -> tuple[bool, dict | None]:
    try:
        header, payload, signature = decode_token(token)
    except Exception:
        return False, None
    if header.get("alg") != "HS256":
        return False, None
    signing_input = ".".join(token.split(".")[:2]).encode("ascii")
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(expected, signature):
        return False, None
    return True, payload


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, body: dict) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/":
            self._send_json(
                200,
                {
                    "message": "JWT training lab",
                    "login": "/login?user=guest",
                    "admin": "/admin with Bearer token or ?token=",
                    "note": "role=admin unlocks the flag",
                },
            )
            return

        if parsed.path == "/login":
            user = query.get("user", ["guest"])[0]
            payload = {"sub": user, "role": "guest"}
            header = {"alg": "HS256", "typ": "JWT"}
            token = sign_hs256(header, payload, WEAK_SECRET)
            self._send_json(
                200,
                {
                    "token": token,
                    "hint": "HS256 is enabled and some deployments still trust alg=none.",
                },
            )
            return

        if parsed.path == "/admin":
            token = query.get("token", [""])[0]
            auth = self.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1]

            if not token:
                self._send_json(401, {"error": "missing token"})
                return

            try:
                header, payload, _ = decode_token(token)
            except Exception as exc:
                self._send_json(400, {"error": f"invalid token: {exc}"})
                return

            if header.get("alg") == "none":
                trusted_payload = payload
            else:
                ok, trusted_payload = verify_hs256(token, WEAK_SECRET)
                if not ok or trusted_payload is None:
                    self._send_json(403, {"error": "signature verification failed"})
                    return

            if trusted_payload.get("role") == "admin":
                self._send_json(200, {"flag": FLAG})
                return

            self._send_json(403, {"error": "admin role required", "payload": trusted_payload})
            return

        self._send_json(404, {"error": "not found"})


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), Handler)
    server.serve_forever()
