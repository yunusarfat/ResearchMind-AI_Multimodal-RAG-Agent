"""
Auth dependency for protected routes.

Usage in an endpoint:
    @router.post("/upload")
    async def upload(file: UploadFile, current_user: User = Depends(get_current_user)):
        ...

Reads the "Authorization: Bearer <token>" header, verifies the JWT,
and loads the matching User row. Raises 401 on any failure (missing
header, invalid/expired token, or user no longer exists).
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.core.security import decode_access_token
from app.db.database import get_session
from app.db.models import User

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> User:
    token = credentials.credentials
    user_id_str = decode_access_token(token)

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject.")

    async with get_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

    return user
