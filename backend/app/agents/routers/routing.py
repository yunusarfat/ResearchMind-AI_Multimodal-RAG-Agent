"""
Conditional routing.

Reads the planner's decision out of state and tells LangGraph which
node to run next. Kept in its own module (rather than inline in
graph.py) so routing logic stays testable and grows cleanly as more
tools/routes are added.
"""

from app.agents.state import AgentState

RETRIEVE = "RETRIEVE"
WEB_SEARCH = "WEB_SEARCH"
PAPER_SEARCH = "PAPER_SEARCH"
DIRECT = "DIRECT"


def route_after_planning(state: AgentState) -> str:
    return state.get("route", DIRECT)
