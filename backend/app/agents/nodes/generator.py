"""
Generator node.

Produces the final answer text (non-streaming) from whatever the
planner/retriever put into state. Used when the graph is run
end-to-end (CLI/testing). The live FastAPI endpoint calls
app.core.llm.stream_answer directly instead, so the response can be
streamed token-by-token to the client — LangGraph's node-level
execution model doesn't naturally support that without extra
plumbing (astream_events), which isn't worth the complexity yet for
a single-tool graph.
"""

from app.agents.state import AgentState
from app.core.llm import generate_answer


async def generate(state: AgentState) -> AgentState:
    query = state["query"]
    context_text = state.get("context_text")  # None on the DIRECT route

    answer = await generate_answer(query, context_text)

    return {**state, "answer": answer}
