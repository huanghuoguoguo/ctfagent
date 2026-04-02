"""Shared utilities for pwn exploit scaffolding scripts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_analysis(path: str) -> dict:
    """Load analysis.json from pwn recon output."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def format_address(value: int | None) -> str:
    """Format an address for template rendering.

    Returns "0x0" for None values, otherwise hex representation.
    """
    if value is None:
        return "0x0"
    return hex(value)


def pick_symbol(symbols: dict[str, int], *names: str) -> tuple[str | None, int | None]:
    """Find the first matching symbol name from a list of candidates.

    Args:
        symbols: Dictionary of symbol names to addresses.
        *names: Candidate symbol names to search for, in priority order.

    Returns:
        Tuple of (name, address) if found, (None, None) otherwise.
    """
    for name in names:
        if name in symbols:
            return name, symbols[name]
    return None, None


def build_context(
    args: argparse.Namespace,
    analysis: dict,
    template: str,
    extra_keys: dict | None = None,
) -> dict:
    """Build the context dictionary for template rendering.

    Args:
        args: Parsed command-line arguments.
        analysis: Analysis dictionary from pwn recon.
        template: Selected template name.
        extra_keys: Optional additional keys to merge into context.

    Returns:
        Context dictionary with common keys plus any extra_keys.
    """
    binary_path = args.binary or analysis.get("file", {}).get("path") or "./chall"
    libc_path = args.libc
    if not libc_path:
        libc_path = analysis.get("libc", {}).get("path") if analysis.get("libc") else None

    context = {
        "template": template,
        "host": args.host,
        "port": args.port,
        "offset": args.offset,
        "binary_path": binary_path,
        "libc_path": libc_path,
        "symbols": analysis.get("symbols", {}),
    }

    if extra_keys:
        context.update(extra_keys)

    return context