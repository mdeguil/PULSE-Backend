# PULSE-Backend documentation

PULSE V1 – *Coach & Challenges*: a voluntary wellbeing space where an employee personalises their experience,
sets personal goals, joins collective challenges and follows their own progress. A functional admin manages challenges
(and, optionally, content). **Employers never see individual data.**

## Project docs (Markdown — maintained by the squad)

| Document | Content |
|---|---|
| [business-rules.md](business-rules.md) | All business rules `RG-*` from HAC-PROD-001 |
| [data-model.md](data-model.md) | Entities, enums, ER diagram, target English naming |
| [api-conventions.md](api-conventions.md) | Routes, security, error format, endpoint list |
| [auth-simulator.md](auth-simulator.md) | Contract of the authentication service and of the simulator to build |
| [database.md](database.md) | Storage choice, profiles, fixtures |
| [acceptance-scenarios.md](acceptance-scenarios.md) | Minimal acceptance scenarios `REC-*` and blocking conditions |
| [decisions.md](decisions.md) | Squad decisions and open questions |

## Reference specifications (`specs/` — provided, read-only, in French)

These documents are internal and **not versioned** (`docs/specs/` is git-ignored because the repository is public).
Get them from the team and place them in `docs/specs/` locally.

| Ref | File | Defines |
|---|---|---|
| HAC-PROD-001 | `specs/02_HAC-PROD-001 …pdf` | Functional scope, business rules, priorities (MoSCoW) |
| HAC-TECH-001 | `specs/03_HAC-TECH-001 …pdf` | Existing IS, integration constraints, squad scope |
| HAC-API-001 | `specs/04_HAC-API-001 …pdf` | Authentication API contract |
| HAC-BACKLOG-001 | `specs/05_HAC-BACKLOG-001 …xlsx` | User stories `US-*` |
| HAC-DATA-001 | _not stored in the repo_ | Synthetic dev/acceptance data — will become fixtures |
| HAC-UX-001 | `specs/07_HAC-UX-001 …pdf` | Reference screens (images only) |
| HAC-ACC-001 | `specs/08_HAC-ACC-001 …pdf` | Acceptance criteria `ACC-*`, scenarios `REC-*` |
| HAC-PULSE-V1-001 | _missing_ | Mission order — **not provided yet** |

When the specs disagree: HAC-PULSE-V1-001 defines what to build, HAC-API-001 the auth contract, HAC-DATA-001 the data,
HAC-ACC-001 what must be demonstrable, HAC-TECH-001 the technical constraints.
A functional ambiguity must be raised with the Product Direction before choosing (log it in `decisions.md`).

## Out of scope for V1

Employer portal, individual HR indicators, medical diagnosis, AI model, native mobile app, recommendation engine,
full admin console, real IAM / OAuth2 / OIDC / SSO / MFA, Docker, CI/CD, Kubernetes, target relational/NoSQL model
(V2 covers architecture, SQL/NoSQL and APIs; V3 covers Docker, CI/CD and delivery).

## Rules for maintaining these docs

- Written in English, like the rest of the project.
- Any change to an entity or enum updates `data-model.md` in the same pull request.
- Code enforcing a rule references its id (`RG-GOAL-05`) in a comment or Javadoc.
- Every squad decision left open by the specs is recorded in `decisions.md`.
