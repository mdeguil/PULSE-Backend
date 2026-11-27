"""Hachage des mots de passe (bibliothèque standard uniquement).

Même un mock ne stocke pas de mot de passe en clair : on garde un hash
PBKDF2-HMAC-SHA256 salé. Format stocké :  pbkdf2_sha256$<itérations>$<sel>$<hash>

Rappel HAC-API-001 section 1 : pas besoin du niveau d'un vrai IAM. PBKDF2 de
la stdlib suffit largement ici (en production on préférerait argon2/bcrypt).
"""
import hashlib
import hmac
import secrets

ITERATIONS = 100_000


def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)          # sel aléatoire unique
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Vérifie un mot de passe contre un hash stocké (temps constant)."""
    try:
        algo, iterations, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), hash_hex)
    except ValueError:
        return False   # hash stocké mal formé -> refus, jamais d'exception
