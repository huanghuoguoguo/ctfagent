from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_SAFE_SCALAR = re.compile(r"^[A-Za-z0-9_.:/@+-]+$")


def _encode_scalar(value: Any) -> str:
    if value is None:
        return '""'
    text = str(value)
    if text == "":
        return '""'
    if _SAFE_SCALAR.fullmatch(text):
        return text
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def dump_frontmatter(metadata: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            if not value:
                lines.append("  []")
                continue
            for item in value:
                lines.append(f"  - {_encode_scalar(item)}")
            continue
        lines.append(f"{key}: {_encode_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def _decode_scalar(value: str) -> str:
    stripped = value.strip()
    if stripped in {"", '""'}:
        return ""
    if stripped.startswith('"') and stripped.endswith('"'):
        inner = stripped[1:-1]
        return inner.replace('\\"', '"').replace("\\\\", "\\")
    return stripped


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text

    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}, text

    frontmatter_text = text[4:end]
    body = text[end + len(marker) :]
    metadata: dict[str, Any] = {}
    current_list_key: str | None = None

    for raw_line in frontmatter_text.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                continue
            metadata.setdefault(current_list_key, [])
            metadata[current_list_key].append(_decode_scalar(line[4:]))
            continue
        if line == "  []":
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", maxsplit=1)
        key = key.strip()
        value = value.strip()
        if value == "":
            metadata[key] = []
            current_list_key = key
            continue
        metadata[key] = _decode_scalar(value)
        current_list_key = None

    return metadata, body


def load_markdown_file(path: str | Path) -> tuple[dict[str, Any], str]:
    return split_frontmatter(Path(path).read_text(encoding="utf-8"))
