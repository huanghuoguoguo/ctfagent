from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from __lib__.markdown import dump_frontmatter
from __lib__.models import ChallengeInfo


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "challenge"


class WorkspaceManager:
    """Create and load challenge packages under workspaces/."""

    def __init__(self, root: str | Path = "workspaces") -> None:
        self.root = Path(root)

    def create(self, challenge: ChallengeInfo, *, overwrite: bool = False) -> Path:
        workspace_dir = self.root / challenge.id
        if workspace_dir.exists():
            if not overwrite:
                raise FileExistsError(f"workspace already exists: {workspace_dir}")
            shutil.rmtree(workspace_dir)

        attachments_dir = workspace_dir / "attachments"
        artifacts_dir = workspace_dir / "artifacts"
        attachments_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        copied_attachments = self._copy_attachments(challenge, attachments_dir)
        stored = ChallengeInfo(
            id=challenge.id,
            title=challenge.title,
            category=challenge.category,
            content=challenge.content,
            platform=challenge.platform,
            platform_id=challenge.platform_id,
            url=challenge.url,
            attachments=copied_attachments,
            tags=list(challenge.tags),
            status=challenge.status,
            metadata=dict(challenge.metadata),
            constraints=list(challenge.constraints),
        )

        (workspace_dir / "challenge.md").write_text(
            self._render_challenge_markdown(stored),
            encoding="utf-8",
        )
        (workspace_dir / "metadata.json").write_text(
            json.dumps(stored.to_metadata_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (workspace_dir / "notes.md").write_text(
            self._render_notes_markdown(stored),
            encoding="utf-8",
        )
        return workspace_dir

    def load(self, workspace_dir: str | Path) -> ChallengeInfo:
        workspace_path = Path(workspace_dir)
        metadata = json.loads((workspace_path / "metadata.json").read_text(encoding="utf-8"))
        challenge_markdown = (workspace_path / "challenge.md").read_text(encoding="utf-8")
        content = self._extract_description(challenge_markdown)
        return ChallengeInfo(
            id=metadata["id"],
            title=metadata["title"],
            category=metadata["category"],
            content=content,
            platform=metadata.get("platform", "manual"),
            platform_id=metadata.get("platform_id", ""),
            url=metadata.get("url", ""),
            attachments=list(metadata.get("attachments", [])),
            tags=list(metadata.get("tags", [])),
            status=metadata.get("status", "new"),
            constraints=list(metadata.get("constraints", [])),
            metadata=dict(metadata.get("metadata", {})),
        )

    def _copy_attachments(self, challenge: ChallengeInfo, attachments_dir: Path) -> list[str]:
        stored_paths: list[str] = []
        for source in challenge.normalized_attachments():
            destination = attachments_dir / source.name
            shutil.copy2(source, destination)
            stored_paths.append(str(Path("attachments") / source.name))
        return stored_paths

    def _render_challenge_markdown(self, challenge: ChallengeInfo) -> str:
        frontmatter = dump_frontmatter(
            {
                "doc_kind": "challenge",
                "id": challenge.id,
                "title": challenge.title,
                "category": challenge.category,
                "platform": challenge.platform,
                "platform_id": challenge.platform_id,
                "url": challenge.url,
                "status": challenge.status,
                "tags": challenge.tags,
                "attachments": challenge.attachments,
            }
        )
        attachment_lines = "\n".join(
            f"  - {item}" for item in challenge.attachments
        ) or "  - none"
        constraint_lines = "\n".join(
            f"- {item}" for item in challenge.constraints
        ) or "- none"
        url_line = challenge.url or "(not provided)"
        return (
            f"{frontmatter}\n"
            f"# {challenge.title}\n\n"
            f"- ID: {challenge.id}\n"
            f"- Category: {challenge.category}\n"
            f"- Platform: {challenge.platform}\n"
            f"- Platform ID: {challenge.platform_id or '(not provided)'}\n"
            f"- URL: {url_line}\n"
            f"- Attachments:\n{attachment_lines}\n\n"
            f"## Description\n\n"
            f"{challenge.content.strip()}\n\n"
            f"## Constraints\n\n"
            f"{constraint_lines}\n"
        )

    def _extract_description(self, markdown_text: str) -> str:
        marker = "## Description"
        constraints_marker = "## Constraints"
        if marker not in markdown_text:
            return ""
        description = markdown_text.split(marker, maxsplit=1)[1]
        if constraints_marker in description:
            description = description.split(constraints_marker, maxsplit=1)[0]
        return description.strip()

    def _render_notes_markdown(self, challenge: ChallengeInfo) -> str:
        frontmatter = dump_frontmatter(
            {
                "doc_kind": "workspace-notes",
                "id": challenge.id,
                "title": challenge.title,
                "category": challenge.category,
                "status": challenge.status,
                "tags": challenge.tags,
            }
        )
        return (
            f"{frontmatter}\n"
            "# Notes\n\n"
            "- hypotheses:\n"
            "- validated findings:\n"
            "- dead ends:\n"
        )


def make_challenge_id(title: str, fallback: str = "challenge") -> str:
    slug = slugify(title)
    return slug or fallback
