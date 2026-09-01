"""
Paper search tool.

Uses the `arxiv` package (a thin wrapper around arXiv's public Atom
API) to search for papers by keyword. Free, no API key, and directly
relevant to a research assistant — this is the tool a literature
review or "find related work" query would route to.
"""

from dataclasses import dataclass

import arxiv


@dataclass
class PaperResult:
    title: str
    authors: list[str]
    summary: str
    url: str
    published: str  # ISO date string


def search_papers(query: str, max_results: int = 5) -> list[PaperResult]:
    """Search arXiv for papers matching `query`.

    Like search_web, this uses a synchronous client under the hood —
    called via asyncio.to_thread from the async graph node.
    """
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    results: list[PaperResult] = []
    for r in client.results(search):
        results.append(
            PaperResult(
                title=r.title.strip(),
                authors=[a.name for a in r.authors],
                summary=r.summary.strip().replace("\n", " "),
                url=r.entry_id,
                published=r.published.date().isoformat() if r.published else "",
            )
        )

    return results
