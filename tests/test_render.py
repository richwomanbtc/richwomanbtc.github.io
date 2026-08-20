from researchmap_site.config import ProfileConfig, SocialLink
from researchmap_site.render import render_all


def sample_payload() -> dict[str, object]:
    return {
        "permalink": "kenjikun",
        "degrees": [{"degree": {"en": "Doctor of Science"}}],
        "@graph": [
            {
                "@type": "research_areas",
                "items": [
                    {
                        "discipline": {"en": "Information science"},
                        "research_field": {"en": "Machine learning"},
                    },
                    {
                        "discipline": {"en": "Humanities & social sciences"},
                        "research_field": {"en": "Money and finance"},
                    },
                ],
            },
            {
                "@type": "research_experience",
                "items": [
                    {
                        "affiliation": {"en": "Example University"},
                        "job": {"en": "Researcher"},
                        "from_date": "2025-04",
                        "to_date": "9999",
                    }
                ],
            },
            {
                "@type": "education",
                "items": [
                    {
                        "affiliation": {"en": "Example University"},
                        "from_date": "2020-04",
                        "to_date": "2024-03",
                    }
                ],
            },
            {
                "@type": "published_papers",
                "items": [
                    {
                        "paper_title": {"en": "Safe <script> title"},
                        "authors": {
                            "en": [{"name": "Alice"}, {"name": "Bob"}],
                            "ja": [{"name": "アリス"}, {"name": "ボブ"}],
                        },
                        "publication_name": {"en": "Journal"},
                        "publication_date": "2026-01",
                        "referee": True,
                        "identifiers": {"doi": ["10.1000/example"]},
                    }
                ],
            },
            {
                "@type": "awards",
                "items": [
                    {
                        "award_name": {"en": "Best Paper"},
                        "association": {"en": "Example Society"},
                        "award_date": "2026",
                    }
                ],
            },
        ],
    }


def test_render_all_normalizes_sections_and_escapes_api_text() -> None:
    profile = ProfileConfig(
        email="person [at] example.test",
        social_links=(SocialLink("GitHub", "https://github.com/example", "fa-brands fa-github"),),
    )

    rendered = render_all(sample_payload(), profile)

    assert "Ph.D. in Science" in rendered["profile.md"]
    assert "2025-04 – Present" in rendered["profile.md"]
    assert "- Machine learning" in rendered["research_areas.md"]
    assert "- Finance" in rendered["research_areas.md"]
    assert "Information science" not in rendered["research_areas.md"]
    assert "Money and finance" not in rendered["research_areas.md"]
    assert "Alice, Bob" in rendered["papers.md"]
    assert "    - **Authors:** Alice, Bob" in rendered["papers.md"]
    assert "アリス" not in rendered["papers.md"]
    assert "&lt;script&gt;" in rendered["papers.md"]
    assert "Example Society" in rendered["awards.md"]
    assert "books.md" not in rendered
    assert "projects.md" not in rendered
