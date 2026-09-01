"""
Firebase Admin SDK initialization and Google ID token verification.

The frontend performs the actual Google Sign-In using the Firebase
client SDK and gets back an ID token. This module verifies that token
server-side (proving it was really issued by Google/Firebase for this
project, not forged) and extracts the user's email/name/UID from it.

Setup required (one-time, see README):
  1. Create a Firebase project at https://console.firebase.google.com
  2. Enable Google as a Sign-In provider (Authentication > Sign-in method)
  3. Project Settings > Service Accounts > Generate new private key
  4. Save the downloaded JSON as `firebase-credentials.json` in backend/
     (or set FIREBASE_CREDENTIALS_PATH in .env to wherever you put it)
"""

from functools import lru_cache

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from app.core.config import settings


@lru_cache
def _get_firebase_app():
    """Initialize the Firebase Admin app exactly once."""
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    return firebase_admin.initialize_app(cred)


class GoogleTokenInvalid(Exception):
    """Raised when the provided Firebase/Google ID token fails verification."""
    pass


def verify_google_id_token(id_token: str) -> dict:
    """
    Verify a Firebase/Google ID token and return the decoded claims.

    Returns a dict with at least: uid, email, name (name may be absent
    for some accounts — callers should fall back to email in that case).
    Raises GoogleTokenInvalid if the token is missing, expired, or
    otherwise fails verification.
    """
    _get_firebase_app()  # ensure initialized

    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception as exc:  # firebase_admin raises several distinct exception
        # types (ExpiredIdTokenError, InvalidIdTokenError, etc.) — any
        # failure here means "reject this token", so we collapse them.
        raise GoogleTokenInvalid(str(exc)) from exc

    if "email" not in decoded:
        raise GoogleTokenInvalid("Google token did not include an email address.")

    return decoded
