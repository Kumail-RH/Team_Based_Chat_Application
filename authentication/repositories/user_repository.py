from typing import Optional
from bson import ObjectId
from config.mongo import database

users = database["users"]

# Create new user
def create_user(name: str, email: str, password_hash: str,) -> dict:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    user = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password_hash": password_hash,
        "is_active": True,
        "email_verified_at": None,
        "created_at": now,
        "updated_at": now,
    }

    result = users.insert_one(user)
    user["_id"] = result.inserted_id
    return user

def get_user_by_email(email: str) -> Optional[dict]:
    return users.find_one({"email": email.strip().lower()})

def find_user_by_id(user_id: ObjectId) -> Optional[dict]:
    return users.find_one({"_id": user_id})