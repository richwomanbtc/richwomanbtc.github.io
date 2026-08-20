"""Normalize researchmap records and render the site's Markdown fragments."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from html import escape as html_escape
from typing import Any
from urllib.parse import quote

from .config import ProfileConfig

LANGUAGES = ("en", "ja")
DEGREE_ALIASES = {
    "Doctor of Science": "Ph.D. in Science",
    "博士(理学)": "Ph.D. in Science",
    "博士（理学）": "Ph.D. in Science",
    "博士(工学)": "Ph.D. in Engineering",
    "博士（工学）": "Ph.D. in Engineering",
    "修士(理学)": "Master of Science",
    "修士（理学）": "Master of Science",
    "修士(工学)": "Master of Engineering",
    "修士（工学）": "Master of Engineering",
    "学士(理学)": "Bachelor of Science",
    "学士（理学）": "Bachelor of Science",
}
AFFILIATION_ALIASES = {
    "株式会社松尾研究所": "Matsuo Institute Inc.",
    "株式会社メルカリ": "Mercari Inc.",
    "大和証券株式会社": "Daiwa Securities Co., Ltd.",
}
MARKDOWN_SPECIAL = re.compile(r"([\\`*_{}\[\]<>#|])")


def _text(value: Any, languages: Sequence[str] = LANGUAGES) -> str:
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, Mapping):
        return ""
    for language in languages:
        candidate = value.get(language)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    for candidate in value.values():
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return ""


def _md(value: Any) -> str:
    """Escape API-provided text before inserting it into Markdown."""

    escaped = html_escape(str(value).strip(), quote=False)
    return MARKDOWN_SPECIAL.sub(r"\\\1", escaped)


def _section_items(payload: Mapping[str, Any], *section_types: str) -> list[dict[str, Any]]:
    graph = payload.get("@graph", [])
    if not isinstance(graph, list):
        return []
    for section in graph:
        if not isinstance(section, dict) or section.get("@type") not in section_types:
            continue
        items = section.get("items", [])
        return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []
    return []


def _people(value: Any) -> list[str]:
    people: Iterable[Any]
    if isinstance(value, Mapping):
        selected: list[Any] = []
        for language in LANGUAGES:
            candidate = value.get(language)
            if isinstance(candidate, list) and candidate:
                selected = candidate
                break
        if not selected:
            selected = next(
                (candidate for candidate in value.values() if isinstance(candidate, list)),
                [],
            )
        people = selected
    elif isinstance(value, list):
        people = value
    else:
        return []

    names: list[str] = []
    for person in people:
        if isinstance(person, str):
            name = person.strip()
        elif isinstance(person, Mapping):
            name = _text(person.get("name"))
        else:
            name = ""
        if name and name not in names:
            names.append(name)
    return names


def _first_text(item: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = _text(item.get(key))
        if value:
            return value
    return ""


def _period(item: Mapping[str, Any]) -> str:
    start = str(item.get("from_date") or "").strip()
    end = str(item.get("to_date") or "").strip()
    if end == "9999":
        end = "Present"
    if start and end:
        return f"{start} – {end}"
    return start or end


def _year(value: Any) -> str:
    text = str(value or "").strip()
    return text.split("-", 1)[0]


def _sort_by_date(items: Iterable[dict[str, Any]], *keys: str) -> list[dict[str, Any]]:
    def sort_key(item: Mapping[str, Any]) -> str:
        for key in keys:
            value = item.get(key)
            if value:
                return str(value)
        return ""

    return sorted(items, key=sort_key, reverse=True)


def _details(lines: list[str]) -> list[str]:
    # Python-Markdown requires four spaces for a nested list. Keeping details
    # under their title also lets the shared CSS treat each record as one item.
    return [f"    - {line}" for line in lines if line]


def render_profile(payload: Mapping[str, Any], config: ProfileConfig) -> str:
    lines: list[str] = []
    degrees = payload.get("degrees")
    if isinstance(degrees, list):
        for degree_info in degrees:
            if not isinstance(degree_info, Mapping):
                continue
            degree = _text(degree_info.get("degree"))
            degree = DEGREE_ALIASES.get(degree, degree)
            if degree:
                lines.append(f"**Degree:** {_md(degree)}")
                lines.append("")
                break

    lines.extend((f"**Email:** {_md(config.email)}", ""))
    if config.social_links:
        lines.append('<div class="social-links" aria-label="Social links">')
        for link in config.social_links:
            url = html_escape(link.url, quote=True)
            label = html_escape(link.label, quote=True)
            mark = html_escape(link.mark)
            lines.append(
                f'  <a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'aria-label="{label}" title="{label}"><span aria-hidden="true">'
                f"{mark}</span></a>"
            )
        lines.extend(("</div>", ""))

    experience = _sort_by_date(
        _section_items(payload, "research_experience"), "from_date", "to_date"
    )
    if experience:
        lines.extend(("## Career", ""))
        for item in experience:
            affiliation = _first_text(item, "affiliation")
            affiliation = AFFILIATION_ALIASES.get(affiliation, affiliation)
            if not affiliation:
                continue
            role_parts = [
                _first_text(item, "section"),
                _first_text(item, "job"),
            ]
            role = ", ".join(part for part in role_parts if part)
            entry = f"- **{_md(affiliation)}**"
            if role:
                entry += f" — {_md(role)}"
            period = _period(item)
            if period:
                entry += f" ({_md(period)})"
            lines.append(entry)
        lines.append("")

    education = _sort_by_date(_section_items(payload, "education"), "from_date")
    if education:
        lines.extend(("## Education", ""))
        for item in education:
            school = _first_text(item, "affiliation")
            if not school:
                continue
            department = _first_text(item, "department")
            course = _first_text(item, "course")
            details = ", ".join(dict.fromkeys(value for value in (department, course) if value))
            entry = f"- **{_md(school)}**"
            if details:
                entry += f" — {_md(details)}"
            period = _period(item)
            if period:
                entry += f" ({_md(period)})"
            lines.append(entry)
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def _doi(item: Mapping[str, Any]) -> str:
    identifiers = item.get("identifiers")
    if isinstance(identifiers, Mapping):
        values = identifiers.get("doi")
        if isinstance(values, list) and values:
            return str(values[0]).strip()
        if isinstance(values, str):
            return values.strip()
    value = item.get("doi")
    return str(value).strip() if value else ""


def render_papers(payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    papers = _sort_by_date(_section_items(payload, "published_papers"), "publication_date")
    for paper in papers:
        title = _first_text(paper, "paper_title", "title") or "Unknown title"
        badges: list[str] = []
        if paper.get("referee") is True:
            badges.append('<span class="badge">Peer reviewed</span>')
        if paper.get("published_paper_type") == "doctoral_thesis":
            badges.append('<span class="badge badge--thesis">Doctoral thesis</span>')
        suffix = f" {' '.join(badges)}" if badges else ""
        lines.append(f"- **{_md(title)}**{suffix}")

        detail_lines: list[str] = []
        authors = _people(paper.get("authors"))
        if authors:
            detail_lines.append(f"**Authors:** {_md(', '.join(authors))}")
        journal = _first_text(paper, "publication_name", "publication")
        if journal:
            detail_lines.append(f"**Journal:** {_md(journal)}")
        year = _year(paper.get("publication_date"))
        if year:
            detail_lines.append(f"**Year:** {_md(year)}")
        doi = _doi(paper)
        if doi:
            doi_url = "https://doi.org/" + quote(doi, safe="/:._-")
            detail_lines.append(f"**DOI:** [{_md(doi)}]({doi_url})")
        lines.extend(_details(detail_lines))
        lines.append("")
    return "\n".join(lines).strip()


def render_books(payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    books = _sort_by_date(_section_items(payload, "books", "books_etc"), "publication_date")
    for book in books:
        title = _first_text(book, "book_title", "title") or "Unknown title"
        lines.append(f"- **{_md(title)}**")
        detail_lines: list[str] = []
        authors = _people(book.get("authors"))
        if authors:
            detail_lines.append(f"**Authors:** {_md(', '.join(authors))}")
        publisher = _first_text(book, "publisher")
        if publisher:
            detail_lines.append(f"**Publisher:** {_md(publisher)}")
        year = _year(book.get("publication_date"))
        if year:
            detail_lines.append(f"**Year:** {_md(year)}")
        identifiers = book.get("identifiers")
        isbn = ""
        if isinstance(identifiers, Mapping):
            values = identifiers.get("isbn")
            if isinstance(values, list) and values:
                isbn = str(values[0])
        if not isbn and book.get("isbn"):
            isbn = str(book["isbn"])
        if isbn:
            detail_lines.append(f"**ISBN:** {_md(isbn)}")
        lines.extend(_details(detail_lines))
        lines.append("")
    return "\n".join(lines).strip()


def render_presentations(payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    presentations = _sort_by_date(
        _section_items(payload, "presentations"), "presentation_date", "year"
    )
    for presentation in presentations:
        title = _first_text(presentation, "presentation_title", "title")
        if not title:
            title = "Unknown title"
        badge = (
            ' <span class="badge">Peer reviewed</span>'
            if presentation.get("referee") is True
            else ""
        )
        lines.append(f"- **{_md(title)}**{badge}")
        detail_lines: list[str] = []
        presenters = _people(presentation.get("presenters") or presentation.get("authors"))
        if presenters:
            detail_lines.append(f"**Presenters:** {_md(', '.join(presenters))}")
        event = _first_text(
            presentation,
            "conference_name",
            "conference",
            "meeting",
            "event",
        )
        if event:
            detail_lines.append(f"**Event:** {_md(event)}")
        year = _year(presentation.get("presentation_date") or presentation.get("year"))
        if year:
            detail_lines.append(f"**Year:** {_md(year)}")
        lines.extend(_details(detail_lines))
        lines.append("")
    return "\n".join(lines).strip()


def render_projects(payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    projects = _sort_by_date(
        _section_items(payload, "competitive_fundings"), "from_date", "to_date"
    )
    for project in projects:
        title = _first_text(project, "research_project_title", "title")
        if not title:
            title = "Unknown title"
        lines.append(f"- **{_md(title)}**")
        detail_lines: list[str] = []
        funding = _first_text(project, "funding_system")
        if funding:
            detail_lines.append(f"**Funding system:** {_md(funding)}")
        period = _period(project)
        if period:
            detail_lines.append(f"**Period:** {_md(period)}")
        lines.extend(_details(detail_lines))
        lines.append("")
    return "\n".join(lines).strip()


def render_awards(payload: Mapping[str, Any]) -> str:
    lines: list[str] = []
    awards = _sort_by_date(_section_items(payload, "awards"), "award_date", "date")
    for award in awards:
        name = _first_text(award, "award_name", "name") or "Unknown award"
        lines.append(f"- **{_md(name)}**")
        detail_lines: list[str] = []
        organization = _first_text(award, "association", "award_organization", "organization")
        if organization:
            detail_lines.append(f"**Organization:** {_md(organization)}")
        title = _first_text(award, "award_title")
        if title:
            detail_lines.append(f"**Awarded work:** {_md(title)}")
        year = _year(award.get("award_date") or award.get("date"))
        if year:
            detail_lines.append(f"**Year:** {_md(year)}")
        lines.extend(_details(detail_lines))
        lines.append("")
    return "\n".join(lines).strip()


def render_all(payload: Mapping[str, Any], profile_config: ProfileConfig) -> dict[str, str]:
    """Render every supported section, omitting empty optional sections."""

    candidates = {
        "profile.md": render_profile(payload, profile_config),
        "papers.md": render_papers(payload),
        "books.md": render_books(payload),
        "presentations.md": render_presentations(payload),
        "projects.md": render_projects(payload),
        "awards.md": render_awards(payload),
    }
    return {name: content.strip() + "\n" for name, content in candidates.items() if content.strip()}
