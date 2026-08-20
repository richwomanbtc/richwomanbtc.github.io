from __future__ import annotations

import requests

from researchmap_site.client import ResearchmapClient, ResearchmapError


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse | None = None) -> None:
        self.headers: dict[str, str] = {}
        self.response = response
        self.last_request: tuple[str, dict[str, str], float] | None = None

    def get(self, url: str, *, params: dict[str, str], timeout: float) -> FakeResponse:
        self.last_request = (url, params, timeout)
        if self.response is None:
            raise requests.Timeout("timed out")
        return self.response


def test_fetch_researcher_uses_format_and_timeout() -> None:
    session = FakeSession(
        FakeResponse(
            {
                "@type": "researchers",
                "permalink": "kenjikun",
                "rm:modified": "2026-01-15T06:32:11Z",
                "@graph": [{"@type": "education", "items": [{"rm:id": "1"}]}],
            }
        )
    )
    client = ResearchmapClient(
        "https://api.researchmap.jp/",
        timeout=12.5,
        session=session,  # type: ignore[arg-type]
    )

    payload = client.fetch_researcher("kenjikun")

    assert payload["permalink"] == "kenjikun"
    assert session.last_request == (
        "https://api.researchmap.jp/kenjikun",
        {"format": "json"},
        12.5,
    )


def test_fetch_researcher_rejects_invalid_schema() -> None:
    session = FakeSession(
        FakeResponse(
            {
                "@type": "researchers",
                "permalink": "kenjikun",
                "rm:modified": "2026-01-15T06:32:11Z",
            }
        )
    )
    client = ResearchmapClient(
        "https://api.researchmap.jp",
        session=session,  # type: ignore[arg-type]
    )

    try:
        client.fetch_researcher("kenjikun")
    except ResearchmapError as error:
        assert "@graph" in str(error)
    else:
        raise AssertionError("invalid payload should fail")


def test_fetch_researcher_rejects_a_degraded_empty_payload() -> None:
    session = FakeSession(
        FakeResponse(
            {
                "@type": "researchers",
                "permalink": "kenjikun",
                "rm:modified": "2026-01-15T06:32:11Z",
                "@graph": [],
            }
        )
    )
    client = ResearchmapClient(
        "https://api.researchmap.jp",
        session=session,  # type: ignore[arg-type]
    )

    try:
        client.fetch_researcher("kenjikun")
    except ResearchmapError as error:
        assert "no public section items" in str(error)
    else:
        raise AssertionError("empty researcher data should fail")


def test_fetch_researcher_rejects_unknown_or_malformed_sections() -> None:
    session = FakeSession(
        FakeResponse(
            {
                "@type": "researchers",
                "permalink": "kenjikun",
                "rm:modified": "2026-01-15T06:32:11Z",
                "@graph": [{"@type": "unknown-error", "items": [None]}],
            }
        )
    )
    client = ResearchmapClient(
        "https://api.researchmap.jp",
        session=session,  # type: ignore[arg-type]
    )

    try:
        client.fetch_researcher("kenjikun")
    except ResearchmapError as error:
        assert "no public section items" in str(error)
    else:
        raise AssertionError("unsupported sections should fail")


def test_fetch_researcher_turns_network_errors_into_sync_failures() -> None:
    session = FakeSession()
    client = ResearchmapClient(
        "https://api.researchmap.jp",
        session=session,  # type: ignore[arg-type]
    )

    try:
        client.fetch_researcher("kenjikun")
    except ResearchmapError as error:
        assert "timed out" in str(error)
    else:
        raise AssertionError("network errors should fail the sync")
