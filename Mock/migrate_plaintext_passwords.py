"""Migrate plaintext values in utilisateur.password_hash to salted PBKDF2 hashes."""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

from security import hash_password

USER_TABLE = "utilisateur"
PAGE_SIZE = 500
PBKDF2_PREFIX = "pbkdf2_sha256$"
OTHER_HASH_FORMATS = (
    ("bcrypt", ("$2a$", "$2b$", "$2y$", "bcrypt$")),
    ("argon2", ("$argon2",)),
    ("scrypt", ("$scrypt$", "scrypt$")),
    ("PBKDF2-SHA512", ("pbkdf2_sha512$",)),
    ("SHA-256", ("sha256$",)),
    ("SHA-512", ("sha512$",)),
)


def detect_other_hash_format(value: str) -> str | None:
    lowered = value.lower()
    return next(
        (
            format_name
            for format_name, prefixes in OTHER_HASH_FORMATS
            if lowered.startswith(prefixes)
        ),
        None,
    )


def is_valid_pbkdf2_hash(value: str) -> bool:
    if not value.startswith(PBKDF2_PREFIX):
        return False

    parts = value.split("$")
    if len(parts) != 4:
        raise ValueError("Malformed PBKDF2 password hash found; migration stopped")

    _, iteration_count, salt_hex, digest_hex = parts
    try:
        iterations = int(iteration_count)
        salt = bytes.fromhex(salt_hex)
        digest = bytes.fromhex(digest_hex)
    except ValueError as exc:
        raise ValueError(
            "Malformed PBKDF2 password hash found; migration stopped"
        ) from exc

    if iterations <= 0 or len(salt) != 16 or len(digest) != 32:
        raise ValueError("Malformed PBKDF2 password hash found; migration stopped")

    return True


def build_migration_plan(rows: list[dict]) -> tuple[list[tuple[str, str]], int]:
    updates = []
    already_hashed = 0

    for row in rows:
        user_id = row.get("user_id")
        password_value = row.get("password_hash")
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("A user record has a missing or invalid user_id")
        if not isinstance(password_value, str) or not password_value:
            raise ValueError("A user record has an empty or invalid password_hash")

        if is_valid_pbkdf2_hash(password_value):
            already_hashed += 1
            continue

        other_format = detect_other_hash_format(password_value)
        if other_format is not None:
            raise ValueError(
                f"A {other_format} encoded value was found; migration stopped "
                "before any database changes"
            )

        updates.append((user_id, hash_password(password_value)))

    return updates, already_hashed


def read_user_rows(client) -> list[dict]:
    rows = []
    start = 0

    while True:
        response = (
            client.table(USER_TABLE)
            .select("user_id,password_hash")
            .range(start, start + PAGE_SIZE - 1)
            .execute()
        )
        page = response.data or []
        rows.extend(page)
        if len(page) < PAGE_SIZE:
            return rows
        start += PAGE_SIZE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replace plaintext values in utilisateur.password_hash with PBKDF2 "
            "hashes. The default mode only previews the number of changes."
        )
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="write the generated hashes to Supabase",
    )
    parser.add_argument(
        "--confirm-plaintext",
        action="store_true",
        help="confirm that unrecognized values in password_hash are plaintext",
    )
    args = parser.parse_args()

    if args.apply and not args.confirm_plaintext:
        parser.error("--apply requires --confirm-plaintext")
    if args.confirm_plaintext and not args.apply:
        parser.error("--confirm-plaintext can only be used with --apply")

    return args


def main() -> None:
    args = parse_args()
    load_dotenv(Path(__file__).with_name(".env"))

    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = (
        os.environ.get("SUPABASE_SECRET_KEY")
        or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    )
    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Set SUPABASE_URL and SUPABASE_SECRET_KEY "
            "(or SUPABASE_SERVICE_ROLE_KEY) in Mock/.env"
        )
    if not supabase_key.isascii():
        raise RuntimeError("The Supabase server key must contain only ASCII characters")

    client = create_client(supabase_url, supabase_key)
    rows = read_user_rows(client)
    updates, already_hashed = build_migration_plan(rows)

    print(f"User records scanned: {len(rows)}")
    print(f"Already PBKDF2-hashed: {already_hashed}")
    print(f"Plaintext values to replace: {len(updates)}")

    if not args.apply:
        print("Dry run only; Supabase was not modified.")
        print(
            "After backing up the table and confirming its remaining values are "
            "plaintext, rerun with --apply --confirm-plaintext."
        )
        return

    for index, (user_id, password_hash) in enumerate(updates, start=1):
        updated_rows = (
            client.table(USER_TABLE)
            .update({"password_hash": password_hash})
            .eq("user_id", user_id)
            .select("user_id")
            .execute()
            .data
            or []
        )
        if len(updated_rows) != 1:
            raise RuntimeError(
                "Expected to update exactly one user record; migration stopped"
            )
        print(f"Updated {index}/{len(updates)} password hashes.")

    print("Migration completed; no table or column was added or changed.")


if __name__ == "__main__":
    main()
