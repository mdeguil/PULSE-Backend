"""Supabase access for the mock authentication API."""

from flask import current_app
from supabase import Client, create_client

USER_TABLE = "user"
USER_COLUMNS = "user_id,email,password_hash,display_name,role,account_status"
DEMO_TOKEN_PREFIX = "demo-token-"


def _map_user(row):
    if row is None:
        return None
    return {
        "userId": row["user_id"],
        "email": row["email"],
        "passwordHash": row["password_hash"],
        "displayName": row["display_name"],
        "role": row["role"],
        "accountStatus": row["account_status"],
    }


def init_app(app) -> None:
    """Create the Supabase client once when server credentials are configured."""
    url = app.config.get("SUPABASE_URL")
    key = app.config.get("SUPABASE_SECRET_KEY")
    if bool(url) != bool(key):
        raise RuntimeError(
            "Both SUPABASE_URL and SUPABASE_SECRET_KEY must be configured"
        )
    if url and key:
        app.extensions["supabase"] = create_client(url, key)


def get_client() -> Client:
    client = current_app.config.get("SUPABASE_CLIENT")
    if client is not None:
        return client

    url = current_app.config.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        raise RuntimeError(
            "Supabase is not configured; set SUPABASE_URL and "
            "SUPABASE_SECRET_KEY"
        )
    if not key.isascii():
        raise RuntimeError("SUPABASE_SECRET_KEY must contain only ASCII characters")

    client = current_app.extensions.get("supabase")
    if client is None:
        client = create_client(url, key)
        current_app.extensions["supabase"] = client
    return client


def _first_row(response):
    rows = response.data or []
    return rows[0] if rows else None


def find_user_by_email(email: str):
    """Look up a user by normalized, lowercase email."""
    return _map_user(_first_row(
        get_client()
        .table(USER_TABLE)
        .select(USER_COLUMNS)
        .eq("email", email.strip().lower())
        .limit(1)
        .execute()
    ))


def find_user_by_id(user_id: str):
    return _map_user(_first_row(
        get_client()
        .table(USER_TABLE)
        .select(USER_COLUMNS)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    ))


def find_user_by_token(token: str):
    if not token.startswith(DEMO_TOKEN_PREFIX):
        return None
    user_id = token[len(DEMO_TOKEN_PREFIX):]
    if not user_id:
        return None
    return find_user_by_id(user_id)


def demo_token_for_user(user_id: str) -> str:
    return f"{DEMO_TOKEN_PREFIX}{user_id}"
