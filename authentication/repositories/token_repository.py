from datetime import datetime, timezone
from bson import ObjectId
from config.mongo import database

tokens = database["auth_tokens"]


def create_token(user_id: ObjectId, token_hash: str, expires_at: datetime,) -> dict:
    token = {
        "user_id": user_id,
        "token_hash": token_hash,
        "created_at": datetime.now(timezone.utc),
        "expires_at": expires_at,
        "revoked_at": None,
    }

    result = tokens.insert_one(token)
    token["_id"] = result.inserted_id
    return token

def find_token_by_hash(token_hash: str):
    return tokens.find_one({"token_hash": token_hash})


def revoke_token(token_id: ObjectId) -> None:
    tokens.update_one(
        {
            "_id": token_id,
            "revoked_at": None,
        },
        {
            "$set": {
                "revoked_at": datetime.now(timezone.utc),
            }
        },
    )