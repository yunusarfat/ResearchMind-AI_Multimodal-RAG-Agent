"""
Auth endpoints: manual signup/login, Google login, and "who am I".

Design: regardless of how a user authenticates (email/password OR
Google), the response is always the same shape -- an access_token
(JWT issued by this backend) plus the user's profile. Every other
protected endpoint in the app only ever has to check one token
format (see app/core/deps.py::get_current_user), never caring which
login path was originally used.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.schemas import (
    GoogleLoginRequest,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.core.deps import get_current_user
from app.core.firebase import GoogleTokenInvalid, verify_google_id_token
from app.core.security import create_access_token, hash_password, verify_password
from app.db.database import get_session
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        auth_provider=user.auth_provider,
    )


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest) -> TokenResponse:
    async with get_session() as session:
        existing = await session.scalar(select(User).where(User.email == payload.email))
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        user = User(
            id=uuid.uuid4(),
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            firebase_uid=None,
            auth_provider="manual",
        )
        session.add(user)
        await session.flush()  # populate user.id/created_at before using them below

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=_user_to_response(user))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.email == payload.email))

        # Same error for "no such user" and "wrong password" -- never
        # reveal which one it was, that leaks which emails are registered.
        invalid_credentials = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

        if user is None or user.password_hash is None:
            # password_hash is None for Google-only accounts -- they
            # can't log in with a password at all.
            raise invalid_credentials

        if not verify_password(payload.password, user.password_hash):
            raise invalid_credentials

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=_user_to_response(user))


@router.post("/google", response_model=TokenResponse)
async def google_login(payload: GoogleLoginRequest) -> TokenResponse:
    try:
        claims = verify_google_id_token(payload.id_token)
    except GoogleTokenInvalid as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {exc}",
        )

    firebase_uid = claims["uid"]
    email = claims["email"]
    name = claims.get("name") or email.split("@")[0]

    async with get_session() as session:
        # Look up by firebase_uid first (returning user), then by email
        # (a manual-signup user who is now also signing in with Google
        # using the same email -- link the accounts rather than erroring).
        user = await session.scalar(select(User).where(User.firebase_uid == firebase_uid))

        if user is None:
            user = await session.scalar(select(User).where(User.email == email))

        if user is None:
            user = User(
                id=uuid.uuid4(),
                name=name,
                email=email,
                password_hash=None,
                firebase_uid=firebase_uid,
                auth_provider="google",
            )
            session.add(user)
            await session.flush()
        elif user.firebase_uid is None:
            # Existing manual account signing in with Google for the
            # first time via the same email -- link it.
            user.firebase_uid = firebase_uid

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled.")

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token, user=_user_to_response(user))


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _user_to_response(current_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: User = Depends(get_current_user)) -> None:
    """
    Permanently deletes the account and everything owned by it.

    Every owned table (documents, chunks, chats, messages) has
    ondelete="CASCADE" back to users.id (see app/db/models.py), so
    deleting this one row is sufficient -- Postgres handles the rest
    at the DB level, not application code looping over tables.
    """
    async with get_session() as session:
        user = await session.get(User, current_user.id)
        if user is not None:
            await session.delete(user)
