"""
Agent state.

This TypedDict is what flows through every node in the LangGraph graph.
Kept flat and serializable (no ORM objects, no live DB sessions) so the
graph stays easy to reason about, test, and later persist/replay.
"""

from typing import TypedDict


class Citation(TypedDict):
    marker: str
    chunk_id: str
    document_id: str
    page_number: int | None
    section: str | None
    content_type: str
    snippet: str


class AgentState(TypedDict, total=False):
    query: str

    # Set by the planner node: "RETRIEVE" | "WEB_SEARCH" | "PAPER_SEARCH" | "DIRECT"
    route: str

    # Set by whichever tool node ran (retriever / web_search / paper_search).
    context_text: str
    citations: list[Citation]

    # Set by the generator node.
    answer: str
