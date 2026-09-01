"""
Chat session CRUD endpoints.

Every operation here is scoped to the authenticated user: a chat_id
that exists but belongs to a different account returns 404 (not 403 --
we don't reveal that the resource exists at all to a non-owner).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ChatCreateRequest, ChatDetail, ChatSummary, MessageResponse
from app.core.deps import get_current_user
from app.db.database import get_session
from app.db.models import Chat, User

router = APIRouter(prefix="/chats", tags=["chats"])


def _chat_to_summary(chat: Chat) -> ChatSummary:
    return ChatSummary(
        id=str(chat.id),
        title=chat.title,
        created_at=chat.created_at.isoformat(),
        updated_at=chat.updated_at.isoformat(),
    )


def _chat_to_detail(chat: Chat) -> ChatDetail:
    return ChatDetail(
        id=str(chat.id),
        title=chat.title,
        created_at=chat.created_at.isoformat(),
        updated_at=chat.updated_at.isoformat(),
        messages=[
            MessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                sources=m.sources or [],
                created_at=m.created_at.isoformat(),
            )
            for m in chat.messages
        ],
    )


async def _get_owned_chat(session: AsyncSession, chat_id: str, user_id: uuid.UUID) -> Chat:
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")

    chat = await session.scalar(
        select(Chat).where(Chat.id == chat_uuid, Chat.user_id == user_id)
    )
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found.")
    return chat


@router.post("", response_model=ChatSummary, status_code=status.HTTP_201_CREATED)
async def create_chat(
    payload: ChatCreateRequest,
    current_user: User = Depends(get_current_user),
) -> ChatSummary:
    async with get_session() as session:
        chat = Chat(
            id=uuid.uuid4(),
            user_id=current_user.id,
            title=payload.title or "New chat",
        )
        session.add(chat)
        await session.flush()
        await session.refresh(chat)
        return _chat_to_summary(chat)


@router.get("", response_model=list[ChatSummary])
async def list_chats(current_user: User = Depends(get_current_user)) -> list[ChatSummary]:
    async with get_session() as session:
        result = await session.execute(
            select(Chat).where(Chat.user_id == current_user.id).order_by(Chat.updated_at.desc())
        )
        chats = result.scalars().all()
        return [_chat_to_summary(c) for c in chats]


@router.get("/{chat_id}", response_model=ChatDetail)
async def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
) -> ChatDetail:
    async with get_session() as session:
        chat = await _get_owned_chat(session, chat_id, current_user.id)
        # Explicitly load messages (lazy relationship) before the session closes.
        await session.refresh(chat, attribute_names=["messages"])
        return _chat_to_detail(chat)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    async with get_session() as session:
        chat = await _get_owned_chat(session, chat_id, current_user.id)
        await session.delete(chat)
