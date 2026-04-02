from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from __lib__.markdown import load_markdown_file


@dataclass(slots=True)
class MarkdownDocument:
    path: Path
    metadata: dict[str, object]
    body: str | None  # None when lazy_body=True in iter_markdown_documents
    title: str


def infer_title(body: str, path: Path) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def infer_doc_kind(path: Path) -> str:
    parts = set(path.parts)
    if "writeups" in parts:
        return "writeup"
    if "patterns" in parts:
        return "pattern"
    if path.name == "challenge.md":
        return "challenge"
    if path.name == "notes.md":
        return "workspace-notes"
    return "note"


def iter_markdown_documents(
    root: str | Path,
    scopes: list[str] | None = None,
    lazy_body: bool = False,
) -> list[MarkdownDocument]:
    root_path = Path(root)
    search_roots = [root_path / scope for scope in (scopes or ["knowledge", "workspaces"])]
    documents: list[MarkdownDocument] = []

    for search_root in search_roots:
        if not search_root.exists():
            continue
        for path in sorted(search_root.rglob("*.md")):
            metadata, body = load_markdown_file(path)
            title = str(metadata.get("title") or infer_title(body, path))
            if "doc_kind" not in metadata:
                metadata["doc_kind"] = infer_doc_kind(path)
            documents.append(
                MarkdownDocument(
                    path=path,
                    metadata=metadata,
                    body=None if lazy_body else body,
                    title=title,
                )
            )
    return documents


def load_body(doc: MarkdownDocument, root: str | Path) -> str:
    """Load the body of a document that was created with lazy_body=True.

    Args:
        doc: A MarkdownDocument with body=None
        root: The root directory to resolve relative paths

    Returns:
        The body content of the markdown file
    """
    _, body = load_markdown_file(doc.path)
    return body


def query_documents(
    documents: list[MarkdownDocument],
    *,
    doc_kind: str | None = None,
    category: str | None = None,
    status: str | None = None,
    tags: list[str] | None = None,
    text: str | None = None,
    root: str | Path | None = None,
) -> list[MarkdownDocument]:
    filtered = documents
    if doc_kind:
        filtered = [doc for doc in filtered if doc.metadata.get("doc_kind") == doc_kind]
    if category:
        filtered = [doc for doc in filtered if doc.metadata.get("category") == category]
    if status:
        filtered = [doc for doc in filtered if doc.metadata.get("status") == status]
    if tags:
        lowered_tags = {tag.lower() for tag in tags}
        filtered = [
            doc
            for doc in filtered
            if lowered_tags.intersection(
                {tag.lower() for tag in doc.metadata.get("tags", []) if isinstance(tag, str)}
            )
        ]
    if text:
        # Lazy load bodies if needed and root is provided
        needle = text.lower()
        if any(doc.body is None for doc in filtered) and root is not None:
            for doc in filtered:
                if doc.body is None:
                    doc.body = load_body(doc, root)
        filtered = [
            doc
            for doc in filtered
            if needle in doc.title.lower() or (doc.body and needle in doc.body.lower())
        ]
    return filtered
