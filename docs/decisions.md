# Decisions & open questions

The specs leave several choices to the squad and require them to be documented. Record each one here with its date.

## Open questions for the Product Direction

| # | Question | Source | Status |
|---|---|---|---|
| Q1 | `RG-CHAL-09` and `ACC-CHAL-09` are referenced but never defined. What do they cover? | HAC-BACKLOG-001 US-CHAL-02/03 | open |
| Q2 | Mission order HAC-PULSE-V1-001 is referenced as the reference document but was not provided. | all specs | open |

## Squad decisions to take

| # | Topic | Options | Decision |
|---|---|---|---|
| D1 | Re-joining a challenge after `LEFT` (HAC-PROD-001 §6.4 note) | new participation · reactivate the old one | _TODO_ |
| D2 | Reactivating a `SUSPENDED` goal (RG-GOAL-06) | not supported · `SUSPENDED` → `ACTIVE` | _TODO_ |
| D3 | How to trigger the simulator 503 (HAC-API-001 §9) | config flag · admin endpoint on the simulator · magic email · stop the simulator | _TODO_ |
| D4 | Storage for V1 | H2 in-memory · H2 file · Supabase | proposed: H2 + fixtures (see `database.md`) |
| D5 | Fixtures mechanism | `data.sql` · `CommandLineRunner` + JSON | _TODO_ (fixtures written later) |
| D6 | Ids of records created at runtime | UUID · prefixed (`goal-<uuid>`) · sequence (`goal-011`) | _TODO_ |
| D7 | How the backend validates a token | call `/me` on every request · call `/me` once and cache for `expiresIn` | _TODO_ |
| D8 | Challenge status: stored or derived from dates | stored (admin sets it, checked for consistency) · computed from `startDate`/`endDate` | _TODO_ |

## Decision log

| Date | # | Decision | Why |
|---|---|---|---|
| | | | |
