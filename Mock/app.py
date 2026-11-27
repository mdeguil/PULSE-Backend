"""Mock API d'authentification HealthAI Coach (contrat HAC-API-001 v1.2).

Simulateur d'intégration PULSE (section 9 du document HAC-API-001).
Il expose EXACTEMENT deux endpoints :

    POST /api/v1/auth/login   -> authentifie un utilisateur (email + mot de passe)
    GET  /api/v1/auth/me      -> retourne l'identité liée à un jeton Bearer

Codes HTTP à pouvoir reproduire (section 9) : 200, 400, 401, 403, 503.

Les utilisateurs sont lus depuis la table `utilisateur` de Supabase. Les
jetons de démonstration sont dérivés de l'identifiant utilisateur et ne sont
pas stockés en base.

Lancement :
    pip install -r requirements.txt
    python app.py            # écoute sur :5000
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

load_dotenv(Path(__file__).with_name(".env"))

import db
import security

# ---------------------------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------------------------
TOKEN_TTL_SECONDS = 3600   # valeur annoncée dans "expiresIn" (non appliquée ici)

app = Flask(__name__)
app.config["SUPABASE_URL"] = os.environ.get("SUPABASE_URL")
app.config["SUPABASE_SECRET_KEY"] = (
    os.environ.get("SUPABASE_SECRET_KEY")
    or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)
app.json.sort_keys = False       # garde l'ordre des clés du contrat
app.json.ensure_ascii = False    # UTF-8 : "Inès" reste "Inès"
db.init_app(app)

# Hash "leurre" : sert à faire le même travail de vérification quand l'email
# est inconnu, pour que le temps de réponse ne révèle pas si un compte existe.
DUMMY_HASH = security.hash_password("leurre-sans-importance")

# Mode "panne" (voir section 6). Activable au démarrage ou à chaud.
service_state = {
    "unavailable": os.environ.get("SIMULATE_UNAVAILABLE", "false").lower() == "true"
}


# ---------------------------------------------------------------------------
# 2. OUTILS DE RÉPONSE
# ---------------------------------------------------------------------------
def error(status: int, code: str, message: str):
    """Erreur au format commun (section 6) : {code, message}, sans détail interne."""
    return jsonify({"code": code, "message": message}), status


def public_identity(user) -> dict:
    """Identité exposée au client (section 3). Jamais passwordHash."""
    return {
        "userId": user["userId"],
        "email": user["email"],
        "displayName": user["displayName"],
        "role": user["role"],
        "accountStatus": user["accountStatus"],
    }


def service_unavailable():
    return error(503, "AUTH_SERVICE_UNAVAILABLE",
                 "Authentication service temporarily unavailable")


# ---------------------------------------------------------------------------
# 3. ENDPOINT POST /api/v1/auth/login   (section 4 du contrat)
# ---------------------------------------------------------------------------
@app.post("/api/v1/auth/login")
def login():
    body = request.get_json(silent=True)   # None si JSON illisible / mauvais type

    # --- 400 : requête invalide (4.2 / 4.4) ----------------------------------
    if not isinstance(body, dict):
        return error(400, "AUTH_BAD_REQUEST", "Invalid authentication request")

    email = body.get("email")
    password = body.get("password")
    if not (isinstance(email, str) and email.strip() != ""
            and isinstance(password, str) and password != ""):
        return error(400, "AUTH_BAD_REQUEST", "Invalid authentication request")

    # --- Recherche en base + vérification du mot de passe --------------------
    user = db.find_user_by_email(email.strip())            # requête SQL (db.py)
    stored_hash = user["passwordHash"] if user else DUMMY_HASH
    password_ok = security.verify_password(password, stored_hash)

    # --- 401 : email inconnu OU mauvais mot de passe -> MÊME réponse (4.4) ---
    if user is None or not password_ok:
        return error(401, "AUTH_INVALID_CREDENTIALS", "Invalid credentials")

    # --- 403 : compte désactivé, seulement si identifiants corrects (4.4) ----
    if user["accountStatus"] == "DISABLED":
        return error(403, "AUTH_ACCOUNT_DISABLED", "Account is disabled")

    # --- 200 : réponse nominale (4.3) ----------------------------------------
    response = public_identity(user)
    response.update({
        "accessToken": db.demo_token_for_user(user["userId"]),
        "tokenType": "Bearer",
        "expiresIn": TOKEN_TTL_SECONDS,
    })
    return jsonify(response), 200


# ---------------------------------------------------------------------------
# 4. ENDPOINT GET /api/v1/auth/me   (section 5 du contrat)
# ---------------------------------------------------------------------------
@app.get("/api/v1/auth/me")
def me():
    header = request.headers.get("Authorization", "")
    scheme, _, token = header.partition(" ")
    token = token.strip()

    # --- 401 : jeton absent, mal formé ou inconnu en base (5.3) --------------
    user = db.find_user_by_token(token) if (scheme.lower() == "bearer" and token) else None
    if user is None:
        return error(401, "AUTH_INVALID_TOKEN", "Invalid or missing access token")

    # --- 403 : compte devenu non autorisé (5.3) ------------------------------
    # L'état est relu en base À CHAQUE appel : si un compte passe à DISABLED
    # (ex. UPDATE users SET accountStatus='DISABLED' ...), son jeton existant
    # est immédiatement refusé. Idéal pour démontrer le cas en recette.
    if user["accountStatus"] == "DISABLED":
        return error(403, "AUTH_ACCOUNT_DISABLED", "Account is disabled")

    # --- 200 : identité SANS jeton (5.2) -------------------------------------
    return jsonify(public_identity(user)), 200


# ---------------------------------------------------------------------------
# 5. SIMULATION DU 503  (section 9 : méthode libre mais reproductible)
# ---------------------------------------------------------------------------
# Trois façons de provoquer un 503, toutes documentées dans le README :
#   A) SIMULATE_UNAVAILABLE=true au lancement
#   B) interrupteur à chaud : POST /simulator/unavailable {"enabled": true}
#   C) en-tête par requête : "X-Simulate-Unavailable: true"
@app.before_request
def maybe_simulate_outage():
    if not request.path.startswith("/api/v1/auth"):
        return None
    header_flag = request.headers.get("X-Simulate-Unavailable", "").lower() == "true"
    if service_state["unavailable"] or header_flag:
        return service_unavailable()
    return None


# Routes de PILOTAGE (hors contrat) : réservées à la recette, jamais appelées
# par l'application PULSE (section 8 : pas de contournement de l'API).
@app.get("/simulator/unavailable")
def get_outage_state():
    return jsonify({"enabled": service_state["unavailable"]})


@app.post("/simulator/unavailable")
def set_outage_state():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("enabled"), bool):
        return jsonify({"code": "SIMULATOR_BAD_REQUEST",
                        "message": 'Expected {"enabled": true|false}'}), 400
    service_state["unavailable"] = body["enabled"]
    return jsonify({"enabled": service_state["unavailable"]})


# ---------------------------------------------------------------------------
# 6. ERREURS INATTENDUES (dont les pannes Supabase)
# ---------------------------------------------------------------------------
@app.errorhandler(Exception)
def unexpected_error(exc):
    if isinstance(exc, HTTPException):       # 404, 405... : comportement normal
        return exc
    # Erreur Supabase, bug, etc. : détail dans les logs serveur uniquement,
    # le client reçoit seulement le 503 du contrat (section 6 : pas de trace).
    app.logger.exception("Unexpected error")
    return service_unavailable()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
