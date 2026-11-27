# API conventions

Status: **proposal** derived from HAC-API-001, HAC-ACC-001 and HAC-BACKLOG-001. Confirm or amend, then record changes in `decisions.md`.

## General

- Base path: `/api/v1`. JSON only, properties in **camelCase**, dates ISO 8601 (`LocalDate` → `2026-02-01`, timestamps in UTC).
- Resources are plural nouns in kebab-case (`/challenges`, `/goals`).
- Controllers never expose JPA entities: request DTOs (`XxxRequest`) and response DTOs (`XxxResponse`) in `dto`.
- Request DTOs are validated with Bean Validation (`@Valid`, `@NotBlank`, `@Positive`, …) — ACC-SEC-03.
- State changes are explicit actions (`POST /goals/{id}/suspend`) rather than a free `status` field in an update body,
  so that transitions are checked by the service (RG-GOAL-05..07, RG-CHAL-07).

## Security

- Every endpoint except login requires `Authorization: Bearer <accessToken>` (token issued by the auth service).
- The backend resolves the identity by calling `GET /api/v1/auth/me` on the auth service (see `auth-simulator.md`).
- **The current user always comes from the token, never from the request.** Personal resources live under `/api/v1/me/...`;
  no endpoint accepts a `userId` parameter for personal data (ACC-PREF-06, ACC-GOAL-09, ACC-PROG-03).
- Accessing another user's resource by id returns **404** (do not reveal that it exists).
- `/api/v1/admin/**` requires `FUNCTIONAL_ADMIN` (RG-ADM-01, ACC-ADM-02); admin endpoints never return users' personal data (RG-ADM-06).

## Error format

Same structure as the auth contract, for every error of the API:

```json
{ "code": "GOAL_NOT_MODIFIABLE", "message": "This goal is closed and can no longer be modified" }
```

- Produced by a single `@RestControllerAdvice`. Unexpected exceptions → `500 INTERNAL_ERROR` with a generic message;
  details are logged server-side only (no stack trace, path or config in the response — ACC-SEC-07).
- Validation errors may add a `fields` array: `[{ "field": "targetValue", "message": "must be greater than 0" }]`.

| HTTP | `code` (examples) | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | invalid body / parameter |
| 401 | `AUTH_INVALID_CREDENTIALS`, `AUTH_INVALID_TOKEN` | bad credentials, missing / invalid token |
| 403 | `AUTH_ACCOUNT_DISABLED`, `ACCESS_DENIED` | disabled account, role not allowed |
| 404 | `NOT_FOUND` | unknown resource or resource of another user |
| 409 | `CHALLENGE_NOT_JOINABLE`, `PARTICIPATION_ALREADY_ACTIVE`, `PARTICIPATION_NOT_ACTIVE`, `GOAL_NOT_MODIFIABLE`, `INVALID_STATUS_TRANSITION` | business rule violation |
| 502 | `AUTH_INVALID_RESPONSE` | auth service returned an unexpected response |
| 503 | `AUTH_SERVICE_UNAVAILABLE` | auth service unavailable (RG-AUTH-06) |

## Endpoints (V1)

### Session

| Method | Path | Story | Notes |
|---|---|---|---|
| POST | `/api/v1/session/login` | US-AUTH-01/02 | forwards to the auth service, maps its errors, returns identity + token (never the password) |
| GET | `/api/v1/me` | US-AUTH-01 | current identity (`userId`, `displayName`, `role`) |

### Preferences — role `USER`

| Method | Path | Story |
|---|---|---|
| GET | `/api/v1/me/preferences` | US-PREF-01 |
| PUT | `/api/v1/me/preferences` | US-PREF-02 |

### Goals — role `USER`

| Method | Path | Story | Rules |
|---|---|---|---|
| GET | `/api/v1/me/goals` | US-GOAL-01 | RG-GOAL-01 |
| POST | `/api/v1/me/goals` | US-GOAL-02 | created `ACTIVE`, target > 0 |
| GET | `/api/v1/me/goals/{goalId}` | US-GOAL-01 | |
| PUT | `/api/v1/me/goals/{goalId}` | US-GOAL-03 | only if `ACTIVE` |
| PUT | `/api/v1/me/goals/{goalId}/progress` | US-GOAL-03 | value ≥ 0 |
| POST | `/api/v1/me/goals/{goalId}/suspend` | US-GOAL-04 | `ACTIVE` → `SUSPENDED` |
| POST | `/api/v1/me/goals/{goalId}/close` | US-GOAL-04 | `ACTIVE`/`SUSPENDED` → `CLOSED` |
| POST | `/api/v1/me/goals/{goalId}/reactivate` | — | optional (RG-GOAL-06) |

### Challenges — role `USER`

| Method | Path | Story | Rules |
|---|---|---|---|
| GET | `/api/v1/challenges` | US-CHAL-01 | all statuses, distinguished |
| GET | `/api/v1/challenges/{challengeId}` | US-CHAL-02 | includes whether the current user can join |
| POST | `/api/v1/challenges/{challengeId}/join` | US-CHAL-03 | `OPEN` only, no duplicate active participation, idempotent |
| POST | `/api/v1/challenges/{challengeId}/leave` | US-CHAL-05 | active participation → `LEFT` |
| GET | `/api/v1/me/participations` | US-CHAL-04 | current user's participations + progress |

### Progress — role `USER`

| Method | Path | Story | Notes |
|---|---|---|---|
| GET | `/api/v1/me/progress` | US-PROG-01/02 | metrics + goals + participations; missing metrics returned as explicit empty entries, not errors |

### Administration — role `FUNCTIONAL_ADMIN`

| Method | Path | Story | Priority |
|---|---|---|---|
| GET | `/api/v1/admin/challenges` | US-ADM-01 | MUST |
| POST | `/api/v1/admin/challenges` | US-ADM-02 | MUST |
| PUT | `/api/v1/admin/challenges/{challengeId}` | US-ADM-03 | MUST |
| GET | `/api/v1/admin/contents` | US-ADM-04 | SHOULD |
| POST | `/api/v1/admin/contents` | US-ADM-04 | SHOULD |
| PUT | `/api/v1/admin/contents/{contentId}` | US-ADM-04 | SHOULD |

## Documentation

OpenAPI is part of the programme trajectory (HAC-TECH-001 §6) but not required for V1 — nice to have (springdoc).
