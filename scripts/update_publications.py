#!/usr/bin/env python3
"""Fetch publications from Google Scholar and generate publications/index.qmd."""

from scholarly import scholarly
from pathlib import Path

SCHOLAR_ID = "dBavvs0AAAAJ"
OUTPUT = Path(__file__).resolve().parent.parent / "publications" / "index.qmd"


def fetch_publications(scholar_id: str) -> list[dict]:
    """Fetch and return publications sorted by year (newest first)."""
    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["publications"])

    pubs = []
    for pub in author["publications"]:
        filled = scholarly.fill(pub)
        bib = filled["bib"]
        pubs.append(
            {
                "title": bib.get("title", ""),
                "authors": bib.get("author", ""),
                "venue": bib.get(
                    "journal", bib.get("conference", bib.get("venue", ""))
                ),
                "year": bib.get("pub_year", ""),
                "citations": filled.get("num_citations", 0),
                "url": filled.get("pub_url", ""),
                "abstract": bib.get("abstract", ""),
            }
        )

    pubs.sort(key=lambda p: p["year"], reverse=True)
    return pubs


def render_qmd(pubs: list[dict]) -> str:
    """Render publications list as Quarto markdown."""
    lines = [
        "---",
        'title: "Publications"',
        "---",
        "",
        f"*Auto-generated from [Google Scholar](https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en).*",
        "",
    ]

    # Group by year
    years: dict[str, list[dict]] = {}
    for pub in pubs:
        yr = pub["year"] or "Unknown"
        years.setdefault(yr, []).append(pub)

    for year in sorted(years, reverse=True):
        lines.append(f"## {year}")
        lines.append("")
        for pub in years[year]:
            title = pub["title"]
            if pub["url"]:
                title = f'[{pub["title"]}]({pub["url"]})'

            lines.append(f"### {title}")
            lines.append("")
            lines.append(f'**{pub["authors"]}**')
            lines.append("")
            if pub["venue"]:
                lines.append(f'*{pub["venue"]}*')
                lines.append("")
            if pub["citations"] > 0:
                lines.append(f'Citations: {pub["citations"]}')
                lines.append("")
            if pub["abstract"]:
                lines.append("::: {.callout-note collapse='true' title='Abstract'}")
                lines.append(pub["abstract"])
                lines.append(":::")
                lines.append("")

    return "\n".join(lines)


def main():
    print(f"Fetching publications for scholar ID: {SCHOLAR_ID}")
    pubs = fetch_publications(SCHOLAR_ID)
    print(f"Found {len(pubs)} publications")

    content = render_qmd(pubs)
    OUTPUT.write_text(content)
    print(f"Written to {OUTPUT}")


if __name__ == "__main__":
    main()
