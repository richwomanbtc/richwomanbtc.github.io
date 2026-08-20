"""Orchestrate a validated, atomic researchmap content refresh."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from markdown import markdown

from .config import SiteConfig
from .render import render_all

FRONT_MATTER = re.compile(r"^---\s*\n[\s\S]*?\n---\s*\n?")


class ResearcherFetcher(Protocol):
    def fetch_researcher(self, permalink: str) -> dict[str, Any]: ...


@dataclass(frozen=True)
class SyncResult:
    output_directory: Path
    generated_files: tuple[str, ...]
    last_updated: str
    source_modified: str


def _utc_timestamp(now: datetime) -> str:
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    return now.astimezone(UTC).strftime("%Y-%m-%d %H:%M (UTC)")


def _metadata(*, permalink: str, last_updated: str, source_modified: str) -> str:
    lines = [
        f"last_updated: {last_updated}",
        f"permalink: {permalink}",
        f"source: https://researchmap.jp/{permalink}",
    ]
    if source_modified:
        lines.append(f"source_modified: {source_modified}")
    return "\n".join(lines) + "\n"


def _replace_directory(staging: Path, destination: Path) -> None:
    """Replace a generated directory and restore the old tree on failure."""

    backup = destination.parent / f".{destination.name}.backup-{uuid4().hex}"
    had_destination = destination.exists()
    if had_destination and not destination.is_dir():
        raise OSError(f"Output path is not a directory: {destination}")

    if had_destination:
        os.replace(destination, backup)
    try:
        os.replace(staging, destination)
    except BaseException:
        if had_destination and backup.exists():
            os.replace(backup, destination)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def _html_fragment(markdown_source: str) -> str:
    source = FRONT_MATTER.sub("", markdown_source).strip()
    if not source:
        return ""
    # Fragments are mounted below an <h2> section title in index.html.
    source = re.sub(r"^(#{1,5})([ \t]+)", r"#\1\2", source, flags=re.MULTILINE)
    return markdown(source, extensions=["extra", "sane_lists"]).strip() + "\n"


def _render_manual_content(directory: Path | None) -> dict[str, str]:
    if directory is None:
        return {}
    if not directory.is_dir():
        raise OSError(f"Manual content directory does not exist: {directory}")

    rendered: dict[str, str] = {}
    for source in sorted(directory.glob("*.md")):
        fragment = _html_fragment(source.read_text(encoding="utf-8"))
        if fragment:
            rendered[f"{source.stem}.html"] = fragment
    return rendered


def synchronize(
    config: SiteConfig,
    client: ResearcherFetcher,
    output_directory: str | Path,
    *,
    manual_content_directory: str | Path | None = None,
    now: datetime | None = None,
) -> SyncResult:
    """Fetch, render, validate, and atomically publish generated content."""

    payload = client.fetch_researcher(config.researchmap.permalink)
    markdown_sections = render_all(payload, config.profile)
    if "profile.md" not in markdown_sections:
        raise ValueError("Rendering produced no profile content")

    rendered = {
        f"{Path(filename).stem}.html": _html_fragment(content)
        for filename, content in markdown_sections.items()
    }
    manual_directory = (
        Path(manual_content_directory).resolve() if manual_content_directory is not None else None
    )
    manual_sections = _render_manual_content(manual_directory)
    collisions = sorted(rendered.keys() & manual_sections.keys())
    if collisions:
        raise ValueError(
            "Manual content conflicts with generated sections: " + ", ".join(collisions)
        )
    rendered.update(manual_sections)

    timestamp = _utc_timestamp(now or datetime.now(UTC))
    source_modified = str(payload.get("rm:modified") or "").strip()
    rendered["metadata.yml"] = _metadata(
        permalink=config.researchmap.permalink,
        last_updated=timestamp,
        source_modified=source_modified,
    )

    output = Path(output_directory).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent))
    try:
        for filename, content in sorted(rendered.items()):
            path = staging / filename
            path.write_text(content, encoding="utf-8", newline="\n")
        _replace_directory(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    return SyncResult(
        output_directory=output,
        generated_files=tuple(sorted(rendered)),
        last_updated=timestamp,
        source_modified=source_modified,
    )
