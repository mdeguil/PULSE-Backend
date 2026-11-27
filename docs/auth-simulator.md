# Authentication service & simulator

Source: HAC-API-001 v1.2, HAC-TECH-001 §3.4, HAC-ACC-001 §4.

The HealthAI Coach authentication service is an **external dependency**. The squad has no access to it and must build a
**local simplified simulator** implementing the same contract. PULSE consumes the simulator exactly as it would consume the
real service: replacing one by the other must not require rewriting business logic.

## Contract

- Version `v1`, HTTP/JSON, UTF-8, `application/json`, prefix `/api/v1/auth`.
- JSON properties in camelCase; dates in ISO 8601 UTC.
- Roles: `USER`, `FUNCTIONAL_ADMIN`. Account status: `ACTIVE`, `DISABLED`.

### `POST /api/v1/auth/login`

Request (both fields required, empty string = invalid, extra properties ignored):

```json
{ "email": "alex.martin@demo.healthaicoach.fr", "password": "<demo password>" }
```

`200 OK`:

```json
{
  "userId": "usr-10027",
  "email": "alex.martin@demo.healthaicoach.fr",
  "displayName": "Alex Martin",
  "role": "USER",
  "accountStatus": "ACTIVE",
  "accessToken": "demo-token-usr-10027",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

`accessToken` is **opaque** to clients: never parse it.

| HTTP | `code` | `message` | When |
|---|---|---|---|
| 400 | `AUTH_BAD_REQUEST` | Invalid authentication request | missing / empty field, unreadable body |
| 401 | `AUTH_INVALID_CREDENTIALS` | Invalid credentials | any other failure — must not reveal whether the email exists |
| 403 | `AUTH_ACCOUNT_DISABLED` | Account is disabled | **only** if email and password are correct and the account is `DISABLED` |
| 503 | `AUTH_SERVICE_UNAVAILABLE` | Authentication service temporarily unavailable | simulated outage |

### `GET /api/v1/auth/me`

Header `Authorization: Bearer <accessToken>`. `200 OK` returns `userId`, `email`, `displayName`, `role`, `accountStatus`.

| HTTP | `code` | When |
|---|---|---|
| 401 | `AUTH_INVALID_TOKEN` | missing or invalid token |
| 403 | `AUTH_ACCOUNT_DISABLED` | account became disabled (optional to reproduce on `/me`) |
| 503 | `AUTH_SERVICE_UNAVAILABLE` | simulated outage |

### Error body (all errors)

```json
{ "code": "ERROR_CODE", "message": "Human readable message" }
```

## Demo users

Provided by the simulator **fixtures** (to be written, from HAC-DATA-001 — not stored in `docs/`). They must cover at least
one `ACTIVE` `USER`, one `DISABLED` `USER` and one `FUNCTIONAL_ADMIN` (scenarios REC-01, REC-03, REC-11).
Demo passwords live only in the simulator fixtures (dev/acceptance) — never in docs, code comments, responses or logs.

## Simulator requirements

Must:
- expose `POST /login` and `GET /me` with the exact paths, methods and JSON structures above;
- use the HAC-DATA-001 users and roles;
- reproduce 200, 400, 401, 403 and 503 — the 503 trigger must be **reproducible and documented** (see `decisions.md`);
- deliver a demo token usable on `/me`;
- stay simple (it is not an IAM project).

Must not: OAuth2/OIDC, SSO, MFA, token refresh, forgotten password, account creation/deletion, identity federation, key management.

The simulator code must be clearly separated from PULSE code (ACC-QUAL-01) — planned location: `Mock/`.

## Integration rules on the PULSE side

- Auth service base URL is a configuration property (e.g. `pulse.auth.base-url`), never hard-coded.
- All calls go through **one** client class/package (e.g. `com.pulse.backend.auth.client`) — no HTTP calls to the auth service elsewhere.
- Validate every response (status, required fields, known role / status values) before use; an unexpected response is handled like a failure, not trusted.
- Map each failure explicitly: invalid request, invalid credentials, disabled account, unavailable service, invalid response. Unavailable ≠ wrong credentials (RG-AUTH-06).
- Never read the simulator's data files or database directly (ACC-AUTH-10, blocking condition).
- Role checks are done in the backend on every protected endpoint (ACC-AUTH-15).
