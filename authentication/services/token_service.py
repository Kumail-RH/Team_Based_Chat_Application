import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from bson import ObjectId

from authentication.repositories import token_repository


TOKEN_LIFETIME_DAYS = 7


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_access_token(user_id: ObjectId) -> str:
    raw_token = secrets.token_urlsafe(32)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=TOKEN_LIFETIME_DAYS
    )

    token_repository.create_token(
        user_id=user_id,
        token_hash=hash_token(raw_token),
        expires_at=expires_at,
    )

    return raw_token