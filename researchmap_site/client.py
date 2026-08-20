"""Resilient client for the public researchmap API."""

from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT_SECONDS = 30.0
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
SUPPORTED_SECTION_TYPES = frozenset(
    {
        "awards",
        "books",
        "books_etc",
        "competitive_fundings",
        "education",
        "presentations",
        "published_papers",
        "research_areas",
        "research_experience",
    }
)


class ResearchmapError(RuntimeError):
    """Raised when researchmap data cannot be fetched or validated."""


def _retry_policy() -> Retry:
    return Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=1.0,
        status_forcelist=RETRYABLE_STATUS_CODES,
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
    )


class ResearchmapClient:
    """Fetch public researcher records with bounded retries and timeouts."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._owns_session = session is None
        self.session = session or requests.Session()

        if self._owns_session:
            adapter = HTTPAdapter(max_retries=_retry_policy())
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        self.session.headers.setdefault(
            "User-Agent",
            "richwomanbtc-site-sync/1.0 (+https://github.com/richwomanbtc/richwomanbtc.github.io)",
        )
        self.session.headers.setdefault("Accept", "application/json")

    def fetch_researcher(self, permalink: str) -> dict[str, Any]:
        url = f"{self.base_url}/{permalink}"
        try:
            response = self.session.get(
                url,
                params={"format": "json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            raise ResearchmapError(f"Failed to fetch {url}: {error}") from error

        if not isinstance(payload, dict):
            raise ResearchmapError("researchmap returned a non-object JSON payload")
        if payload.get("@type") != "researchers":
            raise ResearchmapError("researchmap payload is not a researcher record")
        returned_permalink = payload.get("permalink")
        if returned_permalink != permalink:
            raise ResearchmapError(
                f"researchmap returned data for an unexpected permalink: {returned_permalink!r}"
            )
        modified = payload.get("rm:modified")
        if not isinstance(modified, str) or not modified.strip():
            raise ResearchmapError("researchmap payload is missing rm:modified")
        graph = payload.get("@graph")
        if not isinstance(graph, list):
            raise ResearchmapError("researchmap payload is missing an @graph array")
        valid_item_count = sum(
            sum(isinstance(item, dict) for item in section.get("items", []))
            for section in graph
            if isinstance(section, dict)
            and section.get("@type") in SUPPORTED_SECTION_TYPES
            and isinstance(section.get("items"), list)
        )
        if not graph or valid_item_count == 0:
            raise ResearchmapError("researchmap payload contains no public section items")
        return payload

    def close(self) -> None:
        if self._owns_session:
            self.session.close()

    def __enter__(self) -> ResearchmapClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
