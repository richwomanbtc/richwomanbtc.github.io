from datetime import UTC, datetime
from pathlib import Path

import pytest

from researchmap_site.client import ResearchmapError
from researchmap_site.config import ProfileConfig, ResearchmapConfig, SiteConfig
from researchmap_site.sync import synchronize

CONFIG = SiteConfig(
    researchmap=ResearchmapConfig(permalink="kenjikun", base_url="https://api.researchmap.jp"),
    profile=ProfileConfig(email="person [at] example.test", social_links=()),
)


class FakeClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def fetch_researcher(self, permalink: str) -> dict[str, object]:
        assert permalink == "kenjikun"
        return self.payload


class FailingClient:
    def fetch_researcher(self, permalink: str) -> dict[str, object]:
        raise ResearchmapError(f"could not fetch {permalink}")


def payload() -> dict[str, object]:
    return {
        "permalink": "kenjikun",
        "rm:modified": "2026-01-15T06:32:11Z",
        "degrees": [{"degree": {"en": "Doctor of Science"}}],
        "@graph": [],
    }


def test_synchronize_replaces_the_generated_tree(tmp_path: Path) -> None:
    output = tmp_path / "_auto_contents"
    output.mkdir()
    (output / "stale.md").write_text("stale", encoding="utf-8")
    manual = tmp_path / "_contents"
    manual.mkdir()
    (manual / "research.md").write_text(
        "---\ntitle: Research\n---\n\n## Topic\n\n- Result\n",
        encoding="utf-8",
    )

    result = synchronize(
        CONFIG,
        FakeClient(payload()),
        output,
        manual_content_directory=manual,
        now=datetime(2026, 8, 20, 12, 34, tzinfo=UTC),
    )

    assert not (output / "stale.md").exists()
    assert (output / "profile.html").is_file()
    research = (output / "research.html").read_text(encoding="utf-8")
    assert "<h3>Topic</h3>" in research
    assert "title: Research" not in research
    metadata = (output / "metadata.yml").read_text(encoding="utf-8")
    assert "last_updated: 2026-08-20 12:34 (UTC)" in metadata
    assert "source_modified: 2026-01-15T06:32:11Z" in metadata
    assert result.generated_files == (
        "metadata.yml",
        "profile.html",
        "research.html",
    )
    assert not list(tmp_path.glob("._auto_contents.*"))


def test_failed_fetch_preserves_the_previous_tree(tmp_path: Path) -> None:
    output = tmp_path / "_auto_contents"
    output.mkdir()
    old_file = output / "profile.html"
    old_file.write_text("old content", encoding="utf-8")

    with pytest.raises(ResearchmapError):
        synchronize(CONFIG, FailingClient(), output)

    assert old_file.read_text(encoding="utf-8") == "old content"


def test_manual_content_cannot_replace_generated_sections(tmp_path: Path) -> None:
    manual = tmp_path / "_contents"
    manual.mkdir()
    (manual / "profile.md").write_text("replacement", encoding="utf-8")

    with pytest.raises(ValueError, match="profile.html"):
        synchronize(
            CONFIG,
            FakeClient(payload()),
            tmp_path / "_auto_contents",
            manual_content_directory=manual,
        )
