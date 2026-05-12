#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare true/false SQLi probe responses.")
    parser.add_argument("--target", required=True, help="Endpoint URL")
    parser.add_argument("--param", required=True, help="Injectable parameter name")
    parser.add_argument("--true-payload", required=True)
    parser.add_argument("--false-payload", required=True)
    parser.add_argument("--method", choices=["GET", "POST"], default="GET")
    parser.add_argument("--show-body", action="store_true")
    parser.add_argument("--timeout", type=float, default=10.0)
    return parser.parse_args()


def send_request(target: str, param: str, payload: str, method: str, timeout: float) -> tuple[int, str]:
    encoded = urllib.parse.urlencode({param: payload})
    request_url = target
    data = None

    if method == "GET":
        separator = "&" if urllib.parse.urlparse(target).query else "?"
        request_url = f"{target}{separator}{encoded}"
    else:
        data = encoded.encode("utf-8")

    request = urllib.request.Request(request_url, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def summarize(status: int, body: str) -> dict[str, object]:
    return {
        "status": status,
        "length": len(body),
        "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
        "preview": body[:160].replace("\n", "\\n"),
    }


def main() -> int:
    args = parse_args()
    true_status, true_body = send_request(
        args.target,
        args.param,
        args.true_payload,
        args.method,
        args.timeout,
    )
    false_status, false_body = send_request(
        args.target,
        args.param,
        args.false_payload,
        args.method,
        args.timeout,
    )

    result = {
        "true_probe": summarize(true_status, true_body),
        "false_probe": summarize(false_status, false_body),
        "status_diff": true_status != false_status,
        "length_diff": len(true_body) != len(false_body),
        "body_diff": true_body != false_body,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.show_body:
        print("\n[true body]\n")
        print(true_body)
        print("\n[false body]\n")
        print(false_body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
