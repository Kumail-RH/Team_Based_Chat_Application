from config.mongo import database


def ensure_auth_indexes() -> None:
    """Create indexes required by authentication."""

    database["users"].create_index(
        [("email", 1)],
        unique=True,
        name="unique_user_email",
    )

    database["auth_tokens"].create_index(
        [("token", 1)],
        unique=True,
        name="unique_token_hash",
    )

    database["auth_tokens"].create_index(
        [("expires_at", 1)],
        expireAfterSeconds=0,
        name="token_expiry_ttl",
    )