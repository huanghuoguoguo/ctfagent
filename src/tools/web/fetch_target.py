#!/usr/bin/env python3
import argparse
import html
import re
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(
        description="Submit a URL to a CTF fetcher page and extract the response body or textarea content."
    )
    parser.add_argument("--target", required=True, help="Challenge endpoint, e.g. http://host:port/")
    parser.add_argument("--url", required=True, help="Value to submit in the url parameter")
    parser.add_argument("--param", default="url", help="Form parameter name. Default: url")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the full response body instead of extracting textarea content",
    )
    return parser.parse_args()


def fetch(target, param, supplied_url):
    command = [
        "curl",
        "-sS",
        "--max-time",
        "20",
        "-X",
        "POST",
        target,
        "--data-urlencode",
        f"{param}={supplied_url}",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout


def extract_textarea(body):
    match = re.search(r"<textarea[^>]*>(.*?)</textarea>", body, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return body
    return html.unescape(match.group(1)).strip()


def main():
    args = parse_args()
    try:
        body = fetch(args.target, args.param, args.url)
    except Exception as exc:
        print(f"[error] request failed: {exc}", file=sys.stderr)
        return 1

    print(body if args.raw else extract_textarea(body))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
