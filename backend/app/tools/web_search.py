"""
Web search tool.

Uses DuckDuckGo's search (via the `ddgs` package) since it requires no
API key — good for a portfolio project where asking the user to
provision a paid search API key is unnecessary friction. Swapping to a
paid provider (Tavily, Serper, Bing) later only means changing this
file; the return shape stays the same.
"""

from dataclasses import dataclass

from ddgs import DDGS


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str


def search_web(query: str, max_results: int = 5) -> list[WebResult]:
    """Run a web search and return the top results.

    Note: DDGS is a synchronous/blocking client. This tool is called
    from an async graph node (see nodes/web_search_node.py), which
    accepts the small blocking cost for now — the correct fix at scale
    would be to run this in a thread pool via asyncio.to_thread.
    """
    results: list[WebResult] = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(
                WebResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                )
            )

    return results
