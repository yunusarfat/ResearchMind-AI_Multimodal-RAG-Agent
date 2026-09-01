# """
# Gemini generation layer.

# Takes the context block built by app/rag/context/builder.py (numbered
# chunks with [1] [2] markers) and streams a grounded answer from Gemini,
# instructed to cite using those same markers. This is intentionally the
# only place that talks to the LLM API — swapping providers later means
# changing this file only.
# """

# from collections.abc import AsyncIterator

# import google as genai

# from app.core.config import settings

# _SYSTEM_INSTRUCTION = (
#     "You are ResearchMind, a research assistant that answers questions "
#     "strictly using the numbered context provided below. Rules:\n"
#     "1. Only use information present in the context. If the context doesn't "
#     "contain the answer, say so plainly — do not guess or use outside knowledge.\n"
#     "2. Cite every factual claim using the matching marker, e.g. [1], [2].\n"
#     "3. If multiple sources support a claim, cite all of them, e.g. [1][3].\n"
#     "4. Be precise and concise. Do not repeat the context verbatim — synthesize it."
# )


# def _configure() -> None:
#     genai.configure(api_key=settings.GEMINI_API_KEY)


# def _build_prompt(query: str, context_text: str) -> str:
#     return (
#         f"CONTEXT:\n{context_text}\n\n"
#         f"QUESTION:\n{query}\n\n"
#         "Answer the question using only the context above, citing sources "
#         "with [n] markers."
#     )


# def describe_image(image_path: str, instruction: str) -> str:
#     """
#     Send an image to Gemini with a specific instruction and return the
#     text description. Used by both the image and chart processors —
#     the instruction is what differentiates a generic caption from a
#     trend/value extraction over a chart.
#     """
#     _configure()

#     model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)

#     uploaded_file = genai.upload_file(image_path)
#     response = model.generate_content([uploaded_file, instruction])

#     return response.text.strip() if response.text else ""


# def _build_direct_prompt(query: str) -> str:
#     """Prompt used when the planner decides no document retrieval is
#     needed (greetings, general questions about the assistant, etc.)."""
#     return (
#         "You are ResearchMind, a research assistant for analyzing academic "
#         "papers. The user's message doesn't require document retrieval. "
#         "Respond naturally and briefly. If they ask what you can do, "
#         "mention you can answer questions about their uploaded papers, "
#         "including text, tables, and charts, with citations.\n\n"
#         f"Message: {query}"
#     )


# async def generate_answer(query: str, context_text: str | None) -> str:
#     """Non-streaming generation — used by the agent graph (app/agents)
#     and CLI scripts. The live API's chat endpoint uses stream_answer
#     directly instead, for token-by-token streaming."""
#     _configure()

#     model = genai.GenerativeModel(
#         model_name=settings.GEMINI_MODEL,
#         system_instruction=_SYSTEM_INSTRUCTION if context_text else None,
#     )

#     prompt = _build_prompt(query, context_text) if context_text else _build_direct_prompt(query)
#     response = model.generate_content(prompt)
#     return response.text.strip() if response.text else ""


# async def stream_answer(query: str, context_text: str | None) -> AsyncIterator[str]:
#     """Yield the answer text incrementally as Gemini generates it.
#     If context_text is empty/None, answers directly with no grounding
#     (used for the DIRECT route — greetings, general questions)."""
#     _configure()

#     model = genai.GenerativeModel(
#         model_name=settings.GEMINI_MODEL,
#         system_instruction=_SYSTEM_INSTRUCTION if context_text else None,
#     )

#     prompt = _build_prompt(query, context_text) if context_text else _build_direct_prompt(query)

#     # google-generativeai's streaming call is sync/blocking under the hood;
#     # generate_content(..., stream=True) returns an iterator of chunks.
#     response_stream = model.generate_content(prompt, stream=True)

#     for chunk in response_stream:
#         if chunk.text:
#             yield chunk.text





"""
Gemini generation layer.

Takes the context block built by app/rag/context/builder.py (numbered
chunks with [1] [2] markers) and streams a grounded answer from Gemini,
instructed to cite using those same markers. This is intentionally the
only place that talks to the LLM API — swapping providers later means
changing this file only.
"""

from collections.abc import AsyncIterator

from google import genai

from app.core.config import settings

_SYSTEM_INSTRUCTION = (
    "You are ResearchMind, a research assistant that answers questions "
    "strictly using the numbered context provided below. Rules:\n"
    "1. Only use information present in the context. If the context doesn't "
    "contain the answer, say so plainly — do not guess or use outside knowledge.\n"
    "2. Cite every factual claim using the matching marker, e.g. [1], [2].\n"
    "3. If multiple sources support a claim, cite all of them, e.g. [1][3].\n"
    "4. Be precise and concise. Do not repeat the context verbatim — synthesize it."
)


def _build_prompt(query: str, context_text: str) -> str:
    return (
        f"CONTEXT:\n{context_text}\n\n"
        f"QUESTION:\n{query}\n\n"
        "Answer the question using only the context above, citing sources "
        "with [n] markers."
    )


def describe_image(image_path: str, instruction: str) -> str:
    """
    Send an image to Gemini with a specific instruction and return the
    text description. Used by both the image and chart processors — the
    instruction is what differentiates a generic caption from a trend/value
    extraction over a chart.
    """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            genai.types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/png",
            ),
            instruction,
        ],
    )

    return response.text.strip() if response.text else ""
    """
    Send an image to Gemini with a specific instruction and return the
    text description. Used by both the image and chart processors — the
    instruction is what differentiates a generic caption from a trend/value
    extraction over a chart.
    """

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[
            image_bytes,
            instruction,
        ],
    )

    return response.text.strip() if response.text else ""


def _build_direct_prompt(query: str) -> str:
    """Prompt used when the planner decides no document retrieval is
    needed (greetings, general questions about the assistant, etc.)."""
    return (
        "You are ResearchMind, a research assistant for analyzing academic "
        "papers. The user's message doesn't require document retrieval. "
        "Respond naturally and briefly. If they ask what you can do, "
        "mention you can answer questions about their uploaded papers, "
        "including text, tables, and charts, with citations.\n\n"
        f"Message: {query}"
    )


async def generate_answer(query: str, context_text: str | None) -> str:
    """Non-streaming generation — used by the agent graph (app/agents)
    and CLI scripts. The live API's chat endpoint uses stream_answer
    directly instead, for token-by-token streaming."""

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        _build_prompt(query, context_text)
        if context_text
        else _build_direct_prompt(query)
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "system_instruction": _SYSTEM_INSTRUCTION
            if context_text
            else None
        },
    )

    return response.text.strip() if response.text else ""


async def stream_answer(
    query: str,
    context_text: str | None,
) -> AsyncIterator[str]:
    """Yield the answer text incrementally as Gemini generates it.
    If context_text is empty/None, answers directly with no grounding
    (used for the DIRECT route — greetings, general questions)."""

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        _build_prompt(query, context_text)
        if context_text
        else _build_direct_prompt(query)
    )

    response_stream = client.models.generate_content_stream(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config={
            "system_instruction": _SYSTEM_INSTRUCTION
            if context_text
            else None
        },
    )

    for chunk in response_stream:
        if chunk.text:
            yield chunk.text