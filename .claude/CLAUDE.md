# PULSE-Backend

Backend of **PULSE V1 – Coach & Challenges** (HealthAI Coach, EPSI MSPR TPRE501): a voluntary wellbeing space where an
employee manages preferences, personal goals, collective challenges and a personal progress summary; a functional admin
manages challenges (and optionally content). Employers never see individual data.

## Language

**Everything is written in English**: class, field, method and enum names, table/column names, comments, Javadoc,
log messages, API paths, commit messages, PR descriptions and documentation.
Exception: enum **values** imposed by the specs stay as-is (`ACTIVITE`, `QUOTIDIEN`, `MATIN`, `FICHE`, …).

## Documentation — read before changing code

Index: `docs/README.md`. Read the relevant file first:

- Entities / enums → `docs/data-model.md` (update it in the same change)
- Business logic → `docs/business-rules.md` (reference rule ids `RG-<DOMAIN>-<NN>` in the code)
- Controllers / DTOs / errors / security → `docs/api-conventions.md`
- Anything touching authentication → `docs/auth-simulator.md`
- Datasource, fixtures → `docs/database.md`
- Tests → `docs/acceptance-scenarios.md` (scenarios `REC-*`)
- Squad choices and open questions → `docs/decisions.md`

Original specs (French, PDF/Excel) are in `docs/specs/` — the Markdown docs are the working summary.
If something is marked _TODO_ or is an open question in `decisions.md`, ask instead of inventing a rule.

## Non-negotiable rules (acceptance blockers)

- **Current user = identity from the Bearer token**, never a `userId` from the request. Personal data under `/api/v1/me/...`;
  another user's resource → 404.
- **Role checks in the backend** on every endpoint; `/api/v1/admin/**` = `FUNCTIONAL_ADMIN` only. Admins never get users' personal data.
- **Auth service is external**: called only over HTTP via one client package, base URL from configuration, every response
  validated, 400/401/403/503/invalid response handled explicitly. Never read the simulator's data directly.
- **Errors** use `{ "code": "...", "message": "..." }` from one `@RestControllerAdvice`; never a stack trace, path or config.
- **No secrets or passwords** in the repo, responses or logs (demo passwords included). Only HAC-DATA-001 synthetic data.
- **Don't add features** outside the V1 scope (see `docs/README.md`) at the expense of MUST items.

## Structure

- `pulse/`: Spring Boot application (contains `pom.xml` — run Maven commands from this folder).
  - `src/main/java/com/pulse/backend/entity/`, `.../enums/`
  - Planned packages: `repository`, `service`, `controller`, `dto`, `auth.client` (auth service client), `exception`.
- `Mock/`: authentication **simulator** (separate from PULSE code — ACC-QUAL-01). Not built yet.
- `docs/`: project documentation; `docs/specs/`: reference specifications.
- `.mcp.json`: MCP servers (Supabase, read-only).
- `.github/CODEOWNERS`: mdeguil is code owner; enforced on `main` only.

## Stack

- Java 17, **Spring Boot 4.2** (Spring Framework 7, Jakarta EE 11, Hibernate 7, Jackson 3)
- Web MVC, Data JPA, Validation, Actuator, Lombok
- H2 + fixtures (to be written) for V1; Supabase optional — see `docs/database.md`.

Spring Boot 4 differs from 3.x — do not copy Boot 3 snippets blindly:
- Starters are modular: `spring-boot-starter-webmvc` (not `-web`), `spring-boot-h2console`, and matching `-test` starters per module.
- Jackson 3 uses the `tools.jackson` package (not `com.fasterxml.jackson`, except annotations).
- Use `jakarta.*` imports, never `javax.*`.

## Commands

From `pulse/`:

- Build: `./mvnw clean package` (Windows: `mvnw.cmd clean package`)
- Tests: `./mvnw test`
- Run the app: `./mvnw spring-boot:run`

## Conventions

- Entities: `@Entity` + `@Table(name = "<snake_case_name>")`, Lombok `@Getter @Setter @NoArgsConstructor @AllArgsConstructor`.
- IDs: `String`, named `<entityName>Id` (e.g. `challengeId`). Fixture records keep their HAC-DATA-001 ids (`chl-001`);
  ids are assignable, not forced UUID (runtime format: `docs/decisions.md` D6).
- Enums persisted with `@Enumerated(EnumType.STRING)`.
- Required fields: `@Column(nullable = false)` on entities **and** Bean Validation on request DTOs.
- No `User` entity: users come from the auth service and are referenced by a `String` `userId`, never a foreign key.
- Status changes go through service methods that check allowed transitions (goals, participations).
- Existing code still uses French names — target names are in `docs/data-model.md` ("Target English naming").

## Git

Team rules are in two skills — follow them for every commit and pull request:

- `.claude/skills/pulse-commit-convention/SKILL.md`: format `Type : description in English`, one logical change per commit,
  and a **mandatory review by the `commit-reviewer` agent** (`.claude/agents/commit-reviewer.md`) before any commit — no commit without verdict OK.
- `.claude/skills/pulse-pull-request-rules/SKILL.md`: PR from the work branch to its reference branch (`backend` or `mock`), title in commit format, "Create a merge commit" only.
  Human review is required **only for PRs targeting `main`**; other PRs are merged by their owner without a reviewer.

Branches in this repository (the skills refer to this section for the base and target branch):

```
main (production) ← dev (integration) ← backend (reference: PULSE app)  ← work branches
                                      ← mock    (reference: auth simulator) ← work branches
```

- Every change is made on a work branch created from `backend` (PULSE code) or `mock` (simulator code, `Mock/`).
- Pull requests from a work branch target that reference branch (`backend` or `mock`), not `dev`.
- `backend` and `mock` are merged into `dev`, then `dev` into `main`, through pull requests.
- Never commit directly on `main`, `dev`, `backend` or `mock`. Only `main` is protected on GitHub (ruleset "verif merge", code owner mdeguil in `.github/CODEOWNERS`).
- Never commit secrets (Supabase keys, `.env`, `.claude/settings.local.json`).
- The GitHub repository is **public**.
