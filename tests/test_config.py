from pathlib import Path

import pytest

from researchmap_site.config import ConfigError, load_config

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_repository_config_is_valid() -> None:
    config = load_config(PROJECT_ROOT / "site.toml")

    assert config.researchmap.permalink == "kenjikun"
    assert config.researchmap.base_url == "https://api.researchmap.jp"
    assert {link.label for link in config.profile.social_links} == {
        "X",
        "YouTube",
        "GitHub",
    }
    assert {link.mark for link in config.profile.social_links} == {"X", "▶", "GH"}


def test_config_requires_an_https_api(tmp_path: Path) -> None:
    config_file = tmp_path / "site.toml"
    config_file.write_text(
        """
[researchmap]
permalink = "person"
base_url = "http://example.test"

[profile]
email = "person@example.test"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="HTTPS"):
        load_config(config_file)
