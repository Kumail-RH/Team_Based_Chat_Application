from datetime import datetime, timezone

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from authentication.repositories import token_repository, user_repository
from authentication.services.token_service import hash_token


class MongoUser:
    """Lightweight user object for DRF; no Django user table required."""

    def __init__(self, document: dict):
        self.id = document["_id"]
        self.pk = self.id
        self.name = document["name"]
        self.email = document["email"]
        self.is_active = document["is_active"]
        self.is_authenticated = True
        self.is_anonymous = False


class MongoTokenAuthentication(BaseAuthentication):
    keyword = b"token"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()

        if not parts:
            return None

        if parts[0].lower() != self.keyword:
            return None
        if len(parts) != 2:
            raise AuthenticationFailed("Invalid authorization header.")
        try:
            raw_token = parts[1].decode("utf-8")
        except UnicodeDecodeError:
            raise AuthenticationFailed("Invalid token.")

        token = token_repository.find_token_by_hash(hash_token(raw_token))

        if not token or token.get("revoked_at") is not None:
            raise AuthenticationFailed("Invalid or revoked token.")

        expires_at = token["expires_at"]

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            raise AuthenticationFailed("Token has expired.")

        user = user_repository.find_user_by_id(token["user_id"])

        if not user or not user.get("is_active", False):
            raise AuthenticationFailed("User is inactive or unavailable.")

        return MongoUser(user), token

    def authenticate_header(self, request):
        return 'Token realm="api"'