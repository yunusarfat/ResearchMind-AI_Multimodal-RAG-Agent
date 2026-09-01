# """
# Chat/query endpoint.

# Pipeline: verify the chat belongs to the caller -> planner decides
# RETRIEVE / WEB_SEARCH / PAPER_SEARCH / DIRECT -> run the matching tool
# (if any) -> build numbered context -> stream a Gemini answer, grounded
# in that context if a tool ran, otherwise answered directly.

# Persistence: the user's message is saved before streaming starts (so
# it's never lost even if generation fails partway through), and the
# assistant's full answer + citations are saved once streaming
# completes. The chat's title is set from the first message and its
# updated_at is bumped on every turn, which is what the chat list sorts
# by.

# RETRIEVE is always scoped to the authenticated user's own documents
# (user_id is resolved from the JWT before the stream starts, then
# threaded through to hybrid_search -- never guessed or left optional).
# WEB_SEARCH and PAPER_SEARCH are external/global by nature and aren't
# user-scoped.
# """

# import asyncio
# import json
# import uuid

# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.responses import StreamingResponse
# from sqlalchemy import func, select

# from app.agents.nodes.planner import plan
# from app.agents.routers.routing import DIRECT, PAPER_SEARCH, RETRIEVE, WEB_SEARCH, route_after_planning
# from app.api.schemas import ChatQueryRequest
# from app.core.deps import get_current_user
# from app.core.llm import stream_answer
# from app.db.database import get_session
# from app.db.models import Chat, Message, User
# from app.rag.context.builder import BuiltContext, build_context, build_external_context
# from app.rag.reranking.reranker import get_reranker
# from app.rag.retrieval.hybrid_search import hybrid_search
# from app.tools.paper_search import search_papers
# from app.tools.web_search import search_web

# router = APIRouter(prefix="/chat", tags=["chat"])

# TITLE_MAX_LENGTH = 48


# async def _get_owned_chat(chat_id: str, user_id: uuid.UUID) -> Chat:
#     try:
#         chat_uuid = uuid.UUID(chat_id)
#     except ValueError:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

#     async with get_session() as session:
#         chat = await session.scalar(
#             select(Chat).where(Chat.id == chat_uuid, Chat.user_id == user_id)
#         )
#     if chat is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")
#     return chat


# def _derive_title(query: str) -> str:
#     cleaned = " ".join(query.strip().split())
#     if len(cleaned) <= TITLE_MAX_LENGTH:
#         return cleaned or "New chat"
#     return cleaned[:TITLE_MAX_LENGTH].rstrip() + "…"


# async def _save_user_message(chat_id: uuid.UUID, query: str, is_first_message: bool) -> None:
#     async with get_session() as session:
#         session.add(Message(id=uuid.uuid4(), chat_id=chat_id, role="user", content=query, sources=[]))

#         if is_first_message:
#             chat = await session.get(Chat, chat_id)
#             if chat is not None:
#                 chat.title = _derive_title(query)


# async def _save_assistant_message(chat_id: uuid.UUID, content: str, sources: list[dict]) -> None:
#     async with get_session() as session:
#         session.add(
#             Message(id=uuid.uuid4(), chat_id=chat_id, role="assistant", content=content, sources=sources)
#         )
#         # Touching the Chat row (even a no-op attribute set) isn't needed --
#         # SQLAlchemy's onupdate=func.now() on Chat.updated_at only fires on
#         # an actual UPDATE to that row, so explicitly bump it here.
#         chat = await session.get(Chat, chat_id)
#         if chat is not None:
#             chat.updated_at = func.now()


# async def _get_context(query: str, route: str, user_id: str) -> BuiltContext:
#     if route == RETRIEVE:
#         async with get_session() as session:
#             hybrid_results = await hybrid_search(session, query, user_id=user_id)
#         reranker = get_reranker()
#         final_chunks = reranker.rerank(query, hybrid_results)
#         return build_context(final_chunks)

#     if route == WEB_SEARCH:
#         results = await asyncio.to_thread(search_web, query)
#         items = [{"title": r.title, "snippet": r.snippet, "url": r.url} for r in results]
#         return build_external_context(items, content_type="web")

#     if route == PAPER_SEARCH:
#         results = await asyncio.to_thread(search_papers, query)
#         items = [
#             {
#                 "title": r.title,
#                 "snippet": f"{r.summary} (Published: {r.published})",
#                 "url": r.url,
#             }
#             for r in results
#         ]
#         return build_external_context(items, content_type="paper")

#     return BuiltContext(context_text="", citations=[])


# def _citations_to_dicts(citations) -> list[dict]:
#     return [
#         {
#             "marker": c.marker,
#             "chunk_id": c.chunk_id,
#             "document_id": c.document_id,
#             "page_number": c.page_number,
#             "section": c.section,
#             "content_type": c.content_type,
#             "snippet": c.snippet,
#             "source_url": c.source_url,
#         }
#         for c in citations
#     ]


# async def _event_stream(query: str, user_id: str, chat_id: uuid.UUID, is_first_message: bool):
#     await _save_user_message(chat_id, query, is_first_message)

#     plan_state = await plan({"query": query})
#     route = route_after_planning(plan_state)
#     yield _sse("route", route)

#     full_answer = ""

#     if route == DIRECT:
#         async for token in stream_answer(query, context_text=None):
#             full_answer += token
#             yield _sse("answer", token)
#         yield _sse("citations", [])
#         await _save_assistant_message(chat_id, full_answer, [])
#         return

#     context = await _get_context(query, route, user_id)

#     if not context.citations:
#         message = "I couldn't find anything relevant to answer that."
#         yield _sse("answer", message)
#         yield _sse("citations", [])
#         await _save_assistant_message(chat_id, message, [])
#         return

#     async for token in stream_answer(query, context.context_text):
#         full_answer += token
#         yield _sse("answer", token)

#     citations_payload = _citations_to_dicts(context.citations)
#     yield _sse("citations", citations_payload)
#     await _save_assistant_message(chat_id, full_answer, citations_payload)


# def _sse(event: str, data) -> str:
#     """Format a single Server-Sent-Event message."""
#     return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# @router.post("/query")
# async def query(
#     request: ChatQueryRequest,
#     current_user: User = Depends(get_current_user),
# ) -> StreamingResponse:
#     # Verify chat ownership BEFORE opening the stream, so an invalid/
#     # not-owned chat_id returns a normal 404 instead of a broken stream.
#     chat = await _get_owned_chat(request.chat_id, current_user.id)
#     is_first_message = len(chat.title) == 0 or chat.title == "New chat"

#     return StreamingResponse(
#         _event_stream(request.query, str(current_user.id), chat.id, is_first_message),
#         media_type="text/event-stream",
#     )






"""
Chat/query endpoint.

Pipeline: verify the chat belongs to the caller -> planner decides
RETRIEVE / WEB_SEARCH / PAPER_SEARCH / DIRECT -> run the matching tool
(if any) -> build numbered context -> stream a Gemini answer, grounded
in that context if a tool ran, otherwise answered directly.

Persistence: the user's message is saved before streaming starts (so
it's never lost even if generation fails partway through), and the
assistant's full answer + citations are saved once streaming
completes. The chat's title is set from the first message and its
updated_at is bumped on every turn, which is what the chat list sorts
by.

RETRIEVE is always scoped to the authenticated user's own documents
(user_id is resolved from the JWT before the stream starts, then
threaded through to hybrid_search -- never guessed or left optional).
WEB_SEARCH and PAPER_SEARCH are external/global by nature and aren't
user-scoped.
"""

import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select

from app.agents.nodes.planner import plan
from app.agents.routers.routing import DIRECT, PAPER_SEARCH, RETRIEVE, WEB_SEARCH, route_after_planning
from app.api.schemas import ChatQueryRequest
from app.core.deps import get_current_user
from app.core.llm import stream_answer
from app.db.database import get_session
from app.db.models import Chat, Message, User
from app.rag.context.builder import BuiltContext, build_context, build_external_context
# from app.rag.reranking.reranker import get_reranker
from app.rag.retrieval.hybrid_search import hybrid_search
from app.tools.paper_search import search_papers
from app.tools.web_search import search_web

router = APIRouter(prefix="/chat", tags=["chat"])

TITLE_MAX_LENGTH = 48


async def _get_owned_chat(chat_id: str, user_id: uuid.UUID) -> Chat:
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

    async with get_session() as session:
        chat = await session.scalar(
            select(Chat).where(Chat.id == chat_uuid, Chat.user_id == user_id)
        )
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")
    return chat


def _derive_title(query: str) -> str:
    cleaned = " ".join(query.strip().split())
    if len(cleaned) <= TITLE_MAX_LENGTH:
        return cleaned or "New chat"
    return cleaned[:TITLE_MAX_LENGTH].rstrip() + "…"


async def _save_user_message(chat_id: uuid.UUID, query: str, is_first_message: bool) -> None:
    async with get_session() as session:
        session.add(Message(id=uuid.uuid4(), chat_id=chat_id, role="user", content=query, sources=[]))

        if is_first_message:
            chat = await session.get(Chat, chat_id)
            if chat is not None:
                chat.title = _derive_title(query)


async def _save_assistant_message(chat_id: uuid.UUID, content: str, sources: list[dict]) -> None:
    async with get_session() as session:
        session.add(
            Message(id=uuid.uuid4(), chat_id=chat_id, role="assistant", content=content, sources=sources)
        )
        # Touching the Chat row (even a no-op attribute set) isn't needed --
        # SQLAlchemy's onupdate=func.now() on Chat.updated_at only fires on
        # an actual UPDATE to that row, so explicitly bump it here.
        chat = await session.get(Chat, chat_id)
        if chat is not None:
            chat.updated_at = func.now()


async def _get_context(query: str, route: str, user_id: str) -> BuiltContext:
    if route == RETRIEVE:
        async with get_session() as session:
            hybrid_results = await hybrid_search(
                session,
                query,
                user_id=user_id,
            )

        return build_context(hybrid_results)

    if route == WEB_SEARCH:
        results = await asyncio.to_thread(search_web, query)
        items = [{"title": r.title, "snippet": r.snippet, "url": r.url} for r in results]
        return build_external_context(items, content_type="web")

    if route == PAPER_SEARCH:
        results = await asyncio.to_thread(search_papers, query)
        items = [
            {
                "title": r.title,
                "snippet": f"{r.summary} (Published: {r.published})",
                "url": r.url,
            }
            for r in results
        ]
        return build_external_context(items, content_type="paper")

    return BuiltContext(context_text="", citations=[])
    if route == RETRIEVE:
        async with get_session() as session:
            hybrid_results = await hybrid_search(session, query, user_id=user_id)
        reranker = get_reranker()
        final_chunks = reranker.rerank(query, hybrid_results)
        return build_context(final_chunks)

    if route == WEB_SEARCH:
        results = await asyncio.to_thread(search_web, query)
        items = [{"title": r.title, "snippet": r.snippet, "url": r.url} for r in results]
        return build_external_context(items, content_type="web")

    if route == PAPER_SEARCH:
        results = await asyncio.to_thread(search_papers, query)
        items = [
            {
                "title": r.title,
                "snippet": f"{r.summary} (Published: {r.published})",
                "url": r.url,
            }
            for r in results
        ]
        return build_external_context(items, content_type="paper")

    return BuiltContext(context_text="", citations=[])


def _citations_to_dicts(citations) -> list[dict]:
    return [
        {
            "marker": c.marker,
            "chunk_id": c.chunk_id,
            "document_id": c.document_id,
            "page_number": c.page_number,
            "section": c.section,
            "content_type": c.content_type,
            "snippet": c.snippet,
            "source_url": c.source_url,
        }
        for c in citations
    ]


async def _event_stream(query: str, user_id: str, chat_id: uuid.UUID, is_first_message: bool):
    await _save_user_message(chat_id, query, is_first_message)

    plan_state = await plan({"query": query})
    route = route_after_planning(plan_state)
    yield _sse("route", route)

    full_answer = ""

    if route == DIRECT:
        async for token in stream_answer(query, context_text=None):
            full_answer += token
            yield _sse("answer", token)
        yield _sse("citations", [])
        await _save_assistant_message(chat_id, full_answer, [])
        return

    context = await _get_context(query, route, user_id)

    if not context.citations:
        message = "I couldn't find anything relevant to answer that."
        yield _sse("answer", message)
        yield _sse("citations", [])
        await _save_assistant_message(chat_id, message, [])
        return

    async for token in stream_answer(query, context.context_text):
        full_answer += token
        yield _sse("answer", token)

    citations_payload = _citations_to_dicts(context.citations)
    yield _sse("citations", citations_payload)
    await _save_assistant_message(chat_id, full_answer, citations_payload)


def _sse(event: str, data) -> str:
    """Format a single Server-Sent-Event message."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/query")
async def query(
    request: ChatQueryRequest,
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    # Verify chat ownership BEFORE opening the stream, so an invalid/
    # not-owned chat_id returns a normal 404 instead of a broken stream.
    chat = await _get_owned_chat(request.chat_id, current_user.id)
    is_first_message = len(chat.title) == 0 or chat.title == "New chat"

    return StreamingResponse(
        _event_stream(request.query, str(current_user.id), chat.id, is_first_message),
        media_type="text/event-stream",
    )
