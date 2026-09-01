"""
Password hashing and JWT session tokens.

Uses `bcrypt` directly (not passlib) -- passlib's bcrypt backend has a
long-standing version-compatibility bug with newer bcrypt releases
that silently breaks hashing/verification, so calling bcrypt directly
avoids that whole class of trouble.

Both login paths (manual email/password AND Google/Firebase) end in
the same place: a JWT issued by *this* backend. That means the rest
of the API only ever has to verify one token format, regardless of
how the user originally authenticated.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Malformed hash -- never let a bad hash 500 the request.
        return False


def create_access_token(user_id: str) -> str:
    """Issue a JWT for a user. `sub` (subject) is the user's UUID as a string."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Return the user_id encoded in the token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
