---
name: pulse-pull-request-rules
description: PULSE team pull request rules. Use them to open, review, comment on or merge a PR in the PULSE project, and to know which status the ticket should be in.
---

# PULSE pull request rules

A PR gets your work reviewed by another team member before it reaches the target branch. Each step of the PR moves the ticket forward on the board.

This skill covers PRs from a work branch to its target branch (in this repository: `backend` or `mock`, see `.claude/CLAUDE.md`, section Git). Promoting `dev` to `main` is a separate topic.

## Ticket workflow

The statuses are the team board's own labels — use them exactly as written, do not rename them.

| Moment | Ticket status |
| --- | --- |
| The developer is working on the ticket | `En cours` |
| The PR is opened (or fixes are pushed) | `À relire` |
| At least one comment is left on the PR | `En cours` |
| The PR is approved | `À merge` |
| The branch is merged into the target branch | `À tester en recette` |

If the PR is approved without any comment, the ticket goes straight from `À relire` to `À merge`.

## Opening a PR

1. The PR is opened by the branch owner.
2. It always targets the branch the work branch was created from (`backend` or `mock` in this repository).
3. One PR = one ticket. If it covers several tickets, split it.
4. The title follows the commit convention: `Type : description in English` (e.g. `Feature : add challenge list page`).
5. The description contains:
    - the ticket number or link (e.g. `Ticket #301`);
    - what changed;
    - how to test;
    - a screenshot if the display changed.
6. Before opening the PR:
    - `git pull origin <target branch>` and resolve conflicts on your branch;
    - check that the project starts and that the lint passes (backend: `./mvnw test` from `pulse/`);
    - review your own changes in the *Files changed* tab.
7. If the work is not finished but you want feedback, open the PR as a *Draft*. The ticket stays `En cours`.
8. Once the PR is open, the ticket moves to `À relire`.

## Choosing the reviewer

- The PR is reviewed by the second person assigned to the ticket.
- If the ticket has only one assignee, either:
    - the author picks a reviewer in the team and adds them to the ticket;
    - or the PR is reviewed by the project lead.
- Never review your own PR.

## Reviewing a PR

- The reviewer reviews within 24 working hours.
- Every comment starts with a prefix that gives its weight:
    - `blocking:` must be fixed before merging;
    - `suggestion:` optional improvement;
    - `question:` request for explanation.
- Comments are about the code, never about the person, and suggest a solution when possible.
- As soon as at least one comment is left, the ticket moves to `En cours`.
- If everything is fine, the reviewer approves the PR (*Approve*) and the ticket moves to `À merge`.

## Handling comments

- The branch owner fixes the code, or replies to the comment if they think they are right.
- Once the fixes are pushed, they request a new review (*Re-request review*) and the ticket goes back to `À relire`.
- The person who wrote the comment marks the conversation as resolved, not the PR author.
- If both still disagree after discussing, the team decides at the next team meeting.

## Merging

- Never merge a PR without approval.
- When the ticket is `À merge`, the branch owner merges it themselves.
- Choose **"Create a merge commit"**, never *Squash* or *Rebase*: work branches are reused, and a squash would bring conflicts back at the next merge.
- Do not delete your branch after merging.
- After merging:
    - the ticket moves to `À tester en recette`;
    - the owner runs `git pull origin <target branch>` on their branch before starting another ticket.

## How to apply this skill

- To write a PR: suggest a title in the commit format and a description with the four required items.
- To review: write comments with the `blocking:`, `suggestion:` or `question:` prefixes.
- When asked "where is the ticket at" or "what do I do now": give the next step and the matching board status.
