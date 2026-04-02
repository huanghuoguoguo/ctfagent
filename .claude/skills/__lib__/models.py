from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ChallengeInfo:
    """Structured challenge data shared across packaging and platform layers."""

    id: str
    title: str
    category: str
    content: str
    platform: str = "manual"
    platform_id: str = ""
    url: str = ""
    attachments: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    status: str = "new"
    metadata: dict[str, Any] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)

    def normalized_attachments(self) -> list[Path]:
        return [Path(item).expanduser() for item in self.attachments]

    def to_metadata_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "platform": self.platform,
            "platform_id": self.platform_id,
            "url": self.url,
            "attachments": list(self.attachments),
            "tags": list(self.tags),
            "status": self.status,
            "constraints": list(self.constraints),
        }
        if self.metadata:
            data["metadata"] = dict(self.metadata)
        return data


@dataclass(slots=True)
class SubmitResult:
    success: bool
    message: str = ""
