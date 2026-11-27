"""Tests de conformité du simulateur au contrat HAC-API-001 (cas 200/400/401/403/503).
Lancer avec :  pytest -v"""
import pytest

INES = {"email": "ines.moreau@demo.healthaicoach.fr", "password": "TestPassword!"}
ADMIN = {"email": "karim.dupont@demo.healthaicoach.fr", "password": "TestAdmin!"}
DISABLED = {"email": "nadia.haddad@demo.healthaicoach.fr", "password": "TestPassword!"}


# ---- /login ---------------------------------------------------------------
def test_login_200_user(client):
    r = client.post("/api/v1/auth/login", json=INES)
    assert r.status_code == 200
    body = r.get_json()
    assert body["userId"] == "usr-20041" and body["role"] == "USER"
    assert body["displayName"] == "Inès Moreau"          # UTF-8 préservé
    assert body["tokenType"] == "Bearer" and body["expiresIn"] == 3600
    assert body["accessToken"] == "demo-token-usr-20041"
    assert "password" not in body and "passwordHash" not in body


def test_login_200_admin_role(client):
    r = client.post("/api/v1/auth/login", json=ADMIN)
    assert r.status_code == 200 and r.get_json()["role"] == "FUNCTIONAL_ADMIN"


def test_login_email_is_case_insensitive(client):
    r = client.post("/api/v1/auth/login",
                    json={**INES, "email": "INES.Moreau@Demo.HealthAICoach.fr"})
    assert r.status_code == 200


@pytest.mark.parametrize("payload", [
    {}, {"email": "a@b.fr"}, {"password": "x"},
    {"email": "", "password": "x"}, {"email": "a@b.fr", "password": ""},
    {"email": 123, "password": "x"},
])
def test_login_400(client, payload):
    r = client.post("/api/v1/auth/login", json=payload)
    assert r.status_code == 400 and r.get_json()["code"] == "AUTH_BAD_REQUEST"


def test_login_400_invalid_json(client):
    r = client.post("/api/v1/auth/login", data="pas du json",
                    content_type="application/json")
    assert r.status_code == 400


def test_login_401_wrong_password_and_unknown_email_look_identical(client):
    wrong_pwd = client.post("/api/v1/auth/login", json={**INES, "password": "nope"})
    unknown = client.post("/api/v1/auth/login",
                          json={"email": "inconnu@x.fr", "password": "nope"})
    assert wrong_pwd.status_code == unknown.status_code == 401
    assert wrong_pwd.get_json() == unknown.get_json()


def test_login_injection_attempt_is_just_invalid_credentials(client):
    """Un email malveillant ne peut pas contourner la recherche Supabase."""
    r = client.post("/api/v1/auth/login",
                    json={"email": "' OR '1'='1' --", "password": "x"})
    assert r.status_code == 401


def test_login_403_only_with_correct_credentials(client):
    ok = client.post("/api/v1/auth/login", json=DISABLED)
    assert ok.status_code == 403
    assert ok.get_json()["code"] == "AUTH_ACCOUNT_DISABLED"
    bad = client.post("/api/v1/auth/login", json={**DISABLED, "password": "x"})
    assert bad.status_code == 401        # pas de fuite d'information


# ---- /me ------------------------------------------------------------------
def test_me_200(client):
    token = client.post("/api/v1/auth/login", json=INES).get_json()["accessToken"]
    r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.get_json()["userId"] == "usr-20041"
    assert "accessToken" not in r.get_json()


@pytest.mark.parametrize("headers", [
    {}, {"Authorization": "Bearer faux"}, {"Authorization": "Basic abc"},
    {"Authorization": "Bearer "},
])
def test_me_401(client, headers):
    r = client.get("/api/v1/auth/me", headers=headers)
    assert r.status_code == 401 and r.get_json()["code"] == "AUTH_INVALID_TOKEN"


def test_me_401_for_demo_token_with_unknown_user(client):
    r = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer demo-token-inconnu"},
    )
    assert r.status_code == 401


def test_me_403_disabled_account(client):
    r = client.get("/api/v1/auth/me",
                   headers={"Authorization": "Bearer demo-token-usr-20043"})
    assert r.status_code == 403


def test_me_403_when_account_becomes_disabled_after_login(client, supabase):
    """Scénario 5.3 : un compte actif est désactivé APRÈS avoir reçu son jeton."""
    token = client.post("/api/v1/auth/login", json=INES).get_json()["accessToken"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200

    supabase.tables["utilisateur"][0]["account_status"] = "DISABLED"
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 403


# ---- 503 ------------------------------------------------------------------
def test_503_with_header(client):
    r = client.post("/api/v1/auth/login", json=INES,
                    headers={"X-Simulate-Unavailable": "true"})
    assert r.status_code == 503
    assert r.get_json()["code"] == "AUTH_SERVICE_UNAVAILABLE"


def test_503_with_toggle(client):
    client.post("/simulator/unavailable", json={"enabled": True})
    assert client.get("/api/v1/auth/me").status_code == 503
    client.post("/simulator/unavailable", json={"enabled": False})
    assert client.post("/api/v1/auth/login", json=INES).status_code == 200


def test_503_when_supabase_is_unconfigured(client):
    """Supabase non configuré -> 503 propre, sans détail technique au client."""
    import app as app_module

    app_module.app.config["SUPABASE_CLIENT"] = None
    app_module.app.config["SUPABASE_URL"] = None
    app_module.app.config["SUPABASE_SECRET_KEY"] = None
    app_module.app.extensions.pop("supabase", None)
    r = client.post("/api/v1/auth/login", json=INES)
    assert r.status_code == 503
    assert r.get_json() == {"code": "AUTH_SERVICE_UNAVAILABLE",
                            "message": "Authentication service temporarily unavailable"}
