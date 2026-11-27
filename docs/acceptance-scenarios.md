# Acceptance scenarios

Source: HAC-ACC-001 §11–12. These are the minimum scenarios demonstrated at the version review — each should be covered
by an automated test where possible.

## Minimal scenarios

| ID | Scenario | Data | Expected |
|---|---|---|---|
| REC-01 | Active user login | alex.martin@… | success, `USER` context |
| REC-02 | Wrong credentials | known or unknown email, wrong password | `401 AUTH_INVALID_CREDENTIALS`, same answer whether the email exists or not |
| REC-03 | Disabled account | thomas.roy@… | `403 AUTH_ACCOUNT_DISABLED`, controlled message |
| REC-04 | Auth service unavailable | documented 503 trigger | `503 AUTH_SERVICE_UNAVAILABLE`, distinct message, app keeps working |
| REC-05 | Session check | token from REC-01 | `/api/v1/auth/me` returns the identity |
| REC-06 | Personal preferences | Alex Martin, `pref-001` | read, modify one value, new value persisted |
| REC-07 | Goal management | active user | create, find it in the list, change state or progress |
| REC-08 | Join an open challenge | `chl-001` or `chl-002` (Alex: `chl-005` new, `chl-002` re-join after LEFT) | participation visible |
| REC-09 | Refuse closed challenge | `chl-004` (`CLOSED`) | join refused |
| REC-10 | Progress summary | Alex Martin (`met-001`, `met-002`) | consistent with HAC-DATA-001; no `WELLBEING_CHECKINS` / `HYDRATION_DAYS` → empty state |
| REC-11 | Admin access | lea.bernard@… | `FUNCTIONAL_ADMIN` reaches admin area |
| REC-12 | Admin refused to user | any `USER` calling `/api/v1/admin/**` directly | `403` |
| REC-13 | Create / edit a challenge | Léa Bernard | result visible on next read |

Useful extra cases from HAC-BACKLOG-001: duplicate join on `chl-001` (Alex already `ACTIVE`, `part-001`) → refused / idempotent;
`chl-003` (`UPCOMING`) → join refused; `goal-004` (`SUSPENDED`), `goal-006` / `goal-009` (`CLOSED`) → transition rules.

## Blocking conditions

The version is rejected if any of these remains:

- the app cannot be started from the repository and its instructions;
- screens are static / without application logic;
- the auth simulator is missing or not consumed through the HAC-API-001 contract;
- a `USER` can reach `FUNCTIONAL_ADMIN` features;
- the app reads the simulator's internal data directly;
- a password or sensitive individual data appears in a response, a screen or a log;
- the main features cannot be demonstrated with the synthetic data;
- challenge administration cannot create or modify a challenge according to the rules;
- an auth service error crashes the application;
- the demo uses real or identifying data.
