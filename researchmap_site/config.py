"""Configuration loading and validation."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when the site configuration is invalid."""


@dataclass(frozen=True)
class SocialLink:
    label: str
    url: str
    icon: str


@dataclass(frozen=True)
class ProfileConfig:
    email: str
    social_links: tuple[SocialLink, ...]


@dataclass(frozen=True)
class ResearchmapConfig:
    permalink: str
    base_url: str


@dataclass(frozen=True)
class SiteConfig:
    researchmap: ResearchmapConfig
    profile: ProfileConfig


def _required_string(data: dict[str, Any], key: str, section: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"{section}.{key} must be a non-empty string")
    return value.strip()


def _https_url(data: dict[str, Any], key: str, section: str) -> str:
    value = _required_string(data, key, section)
    if not value.startswith("https://"):
        raise ConfigError(f"{section}.{key} must use HTTPS")
    return value


def load_config(path: str | Path) -> SiteConfig:
    """Load a validated TOML configuration file."""

    config_path = Path(path)
    try:
        with config_path.open("rb") as file:
            raw = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigError(f"Could not read {config_path}: {error}") from error

    researchmap = raw.get("researchmap")
    profile = raw.get("profile")
    if not isinstance(researchmap, dict):
        raise ConfigError("Missing [researchmap] configuration")
    if not isinstance(profile, dict):
        raise ConfigError("Missing [profile] configuration")

    links: list[SocialLink] = []
    social_links = profile.get("social_links", [])
    if not isinstance(social_links, list):
        raise ConfigError("profile.social_links must be an array of tables")
    for index, item in enumerate(social_links):
        section = f"profile.social_links[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{section} must be a table")
        links.append(
            SocialLink(
                label=_required_string(item, "label", section),
                url=_https_url(item, "url", section),
                icon=_required_string(item, "icon", section),
            )
        )

    base_url = _https_url(researchmap, "base_url", "researchmap").rstrip("/")

    return SiteConfig(
        researchmap=ResearchmapConfig(
            permalink=_required_string(researchmap, "permalink", "researchmap"),
            base_url=base_url,
        ),
        profile=ProfileConfig(
            email=_required_string(profile, "email", "profile"),
            social_links=tuple(links),
        ),
    )
