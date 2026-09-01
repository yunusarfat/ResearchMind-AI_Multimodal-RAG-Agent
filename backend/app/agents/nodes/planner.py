# """
# Planner node.

# Decides which tool (if any) should handle the query:
#   - RETRIEVE:     answer using the user's own uploaded documents (RAG)
#   - WEB_SEARCH:   answer using current web information
#   - PAPER_SEARCH: find related/external academic papers (arXiv)
#   - DIRECT:       no tool needed (greetings, general questions)

# As more tools are added, this is the single place that grows — the
# rest of the graph just reacts to whatever route comes out of here.
# """

# import google import genai

# from app.agents.state import AgentState
# from app.core.config import settings

# _ROUTING_INSTRUCTION = (
#     "You are a routing classifier for a research assistant. Decide which "
#     "single tool should handle the user's message.\n\n"
#     "Respond with exactly one word, no punctuation:\n"
#     "RETRIEVE, WEB_SEARCH, PAPER_SEARCH, or DIRECT.\n\n"
#     "Use RETRIEVE for: questions about the user's own uploaded papers — "
#     "specific facts, tables, figures, findings, comparisons within those "
#     "documents.\n"
#     "Use WEB_SEARCH for: questions needing current/general information "
#     "from the internet not tied to the user's documents (news, current "
#     "events, definitions of things not in their papers, 'what is the "
#     "latest X').\n"
#     "Use PAPER_SEARCH for: requests to find OTHER/related academic papers, "
#     "literature search, 'find papers about X', 'what other work exists on Y'.\n"
#     "Use DIRECT for: greetings, small talk, or questions about what the "
#     "assistant itself can do.\n\n"
#     f"Message: {{query}}\n\nAnswer with one word only."
# )


# def _configure() -> None:
#     genai.configure(api_key=settings.GEMINI_API_KEY)


# async def plan(state: AgentState) -> AgentState:
#     """LangGraph node: sets state['route'] to one of the four labels."""
#     query = state["query"]

#     _configure()
#     model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
#     response = model.generate_content(_ROUTING_INSTRUCTION.format(query=query))

#     decision = (response.text or "").strip().upper()

#     valid_routes = {"RETRIEVE", "WEB_SEARCH", "PAPER_SEARCH", "DIRECT"}
#     route = decision if decision in valid_routes else "DIRECT"

#     return {**state, "route": route}





"""
Planner node.

Decides which tool (if any) should handle the query:
  - RETRIEVE:     answer using the user's own uploaded documents (RAG)
  - WEB_SEARCH:   answer using current web information
  - PAPER_SEARCH: find related/external academic papers (arXiv)
  - DIRECT:       no tool needed (greetings, general questions)
"""

from google import genai

from app.agents.state import AgentState
from app.core.config import settings

_ROUTING_INSTRUCTION = (
    "You are a routing classifier for a research assistant. Decide which "
    "single tool should handle the user's message.\n\n"
    "Respond with exactly one word, no punctuation:\n"
    "RETRIEVE, WEB_SEARCH, PAPER_SEARCH, or DIRECT.\n\n"
    "Use RETRIEVE for: questions about the user's own uploaded papers — "
    "specific facts, tables, figures, findings, comparisons within those "
    "documents.\n"
    "Use WEB_SEARCH for: questions needing current/general information "
    "from the internet not tied to the user's documents (news, current "
    "events, definitions of things not in their papers, 'what is the "
    "latest X').\n"
    "Use PAPER_SEARCH for: requests to find OTHER/related academic papers, "
    "literature search, 'find papers about X', 'what other work exists on Y'.\n"
    "Use DIRECT for: greetings, small talk, or questions about what the "
    "assistant itself can do.\n\n"
    f"Message: {{query}}\n\nAnswer with one word only."
)


def _get_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def plan(state: AgentState) -> AgentState:
    """LangGraph node: sets state['route'] to one of the four labels."""
    query = state["query"]

    client = _get_client()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=_ROUTING_INSTRUCTION.format(query=query),
    )

    decision = (response.text or "").strip().upper()

    valid_routes = {"RETRIEVE", "WEB_SEARCH", "PAPER_SEARCH", "DIRECT"}
    route = decision if decision in valid_routes else "DIRECT"

    return {**state, "route": route}