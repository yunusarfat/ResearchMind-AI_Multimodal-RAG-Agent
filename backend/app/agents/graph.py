"""
Agent graph.

Wires together: planner -> (conditional on route) -> tool node -> generator
                                                    `-> generator (DIRECT route, no tool)

Routes: RETRIEVE (user's documents), WEB_SEARCH (internet), PAPER_SEARCH
(arXiv), DIRECT (no tool). The retriever node needs an open AsyncSession
and a user_id (see nodes/retriever.py) -- both request-scoped -- so the
graph is built per-request via `build_graph(session, user_id)` rather
than once at import time.
"""

from functools import partial

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.nodes.generator import generate
from app.agents.nodes.paper_search_node import paper_search_node
from app.agents.nodes.planner import plan
from app.agents.nodes.retriever import retrieve
from app.agents.nodes.web_search_node import web_search_node
from app.agents.routers.routing import DIRECT, PAPER_SEARCH, RETRIEVE, WEB_SEARCH, route_after_planning
from app.agents.state import AgentState


def build_graph(session: AsyncSession, user_id: str):
    graph = StateGraph(AgentState)

    graph.add_node("planner", plan)
    graph.add_node("retriever", partial(retrieve, session=session, user_id=user_id))
    graph.add_node("web_search", web_search_node)
    graph.add_node("paper_search", paper_search_node)
    graph.add_node("generator", generate)

    graph.set_entry_point("planner")

    graph.add_conditional_edges(
        "planner",
        route_after_planning,
        {
            RETRIEVE: "retriever",
            WEB_SEARCH: "web_search",
            PAPER_SEARCH: "paper_search",
            DIRECT: "generator",
        },
    )

    graph.add_edge("retriever", "generator")
    graph.add_edge("web_search", "generator")
    graph.add_edge("paper_search", "generator")
    graph.add_edge("generator", END)

    return graph.compile()


async def run_agent(query: str, session: AsyncSession, user_id: str) -> AgentState:
    """Convenience entrypoint: run the full graph and return final state.
    Used by CLI/testing. The live streaming API endpoint (app/api/chat.py)
    orchestrates planner+retrieval the same way but calls stream_answer
    separately for token-by-token streaming."""
    app = build_graph(session, user_id)
    result = await app.ainvoke({"query": query})
    return result
