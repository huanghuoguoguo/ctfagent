from __future__ import annotations

import re
from dataclasses import dataclass, field


FIELD_ALIASES = {
    "title": {
        "title",
        "challenge title",
        "题目标题",
        "标题",
        "题目",
    },
    "category": {
        "category",
        "分类",
        "题目分类",
    },
    "url": {
        "url",
        "target",
        "host",
        "connection",
        "目标",
        "目标地址",
        "连接",
        "连接方式",
        "主机",
        "地址",
    },
    "attachments": {
        "attachment",
        "attachments",
        "附件",
        "附件路径",
    },
    "content": {
        "content",
        "description",
        "statement",
        "prompt",
        "题目描述",
        "描述",
        "题面",
        "题目内容",
    },
    "constraints": {
        "constraint",
        "constraints",
        "限制",
        "限制条件",
    },
    "platform": {
        "platform",
        "平台",
    },
    "platform_id": {
        "platform id",
        "platform-id",
        "题号",
        "平台题号",
    },
}


@dataclass(slots=True)
class SetupRequest:
    title: str = ""
    category: str = ""
    content: str = ""
    url: str = ""
    platform: str = "manual"
    platform_id: str = ""
    attachments: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    fallback_content_used: bool = False

    def missing_fields(self) -> list[str]:
        missing: list[str] = []
        if not self.title:
            missing.append("title")
        if not self.category:
            missing.append("category")
        if not self.content and not self.url and not self.attachments:
            missing.append("description-or-target")
        return missing


def parse_setup_text(text: str) -> SetupRequest:
    values: dict[str, list[str] | str] = {
        "attachments": [],
        "constraints": [],
    }
    current_field: str | None = None
    current_lines: list[str] = []

    for raw_line in text.splitlines():
        matched_field, initial_value = _match_field(raw_line)
        if matched_field is not None:
            _commit_field(values, current_field, current_lines)
            current_field = matched_field
            current_lines = [initial_value] if initial_value else []
            continue
        if current_field is not None:
            current_lines.append(raw_line)

    _commit_field(values, current_field, current_lines)

    request = SetupRequest(
        title=str(values.get("title", "")).strip(),
        category=str(values.get("category", "")).strip(),
        content=_normalize_block(str(values.get("content", ""))),
        url=str(values.get("url", "")).strip(),
        platform=str(values.get("platform", "manual")).strip() or "manual",
        platform_id=str(values.get("platform_id", "")).strip(),
        attachments=list(values.get("attachments", [])),
        constraints=list(values.get("constraints", [])),
    )
    if not request.content:
        fallback = _build_fallback_content(request)
        if fallback:
            request.content = fallback
            request.fallback_content_used = True
    return request


def _match_field(line: str) -> tuple[str | None, str]:
    match = re.match(r"^\s*(?:[-*]\s*)?([^:：]+?)\s*[:：]\s*(.*)$", line)
    if not match:
        return None, ""
    label = _normalize_label(match.group(1))
    for field_name, aliases in FIELD_ALIASES.items():
        if label in aliases:
            return field_name, match.group(2).strip()
    return None, ""


def _normalize_label(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _normalize_block(value: str) -> str:
    lines = [line.rstrip() for line in value.splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def _commit_field(store: dict[str, list[str] | str], field: str | None, lines: list[str]) -> None:
    if field is None:
        return
    value = _normalize_block("\n".join(lines))
    if field in {"attachments", "constraints"}:
        existing = list(store.get(field, []))
        existing.extend(_split_items(value))
        store[field] = existing
        return
    store[field] = value


def _split_items(value: str) -> list[str]:
    items: list[str] = []
    for raw_line in value.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s*", "", line)
        parts = [part.strip() for part in re.split(r"[,\n，；;]+", line) if part.strip()]
        items.extend(parts)
    return items


def _build_fallback_content(request: SetupRequest) -> str:
    lines: list[str] = []
    if request.url:
        lines.append("Challenge initialized from /setup.")
        lines.append("")
        lines.append(f"Target: {request.url}")
    if request.attachments:
        if not lines:
            lines.append("Challenge initialized from /setup.")
            lines.append("")
        lines.append("Attachments:")
        lines.extend(f"- {item}" for item in request.attachments)
    return "\n".join(lines).strip()
