---
name: sprint-workflow
description: Pick up, work and close a sprint ticket. Use when the user says "next ticket", "start S1", "continue the sprint", asks what to work on, or when a PR closes a ticket; also when updating sprint or implementation docs.
---

# Sprint workflow

Two layers, kept in sync:

- `docs/sprints/S<n>-*.md`: intent. Goal, tickets (id, title, points, dependencies), definition of done, risks, demo, go/no-go. Change only when the plan changes, and say why in the PR.
- `docs/implementation/S<n>-*.md`: state. One row per ticket with ✅ 🟡 🚧 ⏸ ⏳ and notes (files, PR, how to verify).

## Pick up a ticket

1. Read `docs/HANDOFF.md`, then the sprint file and its audit.
2. Choose the lowest-numbered ticket whose dependencies are ✅. If the handoff names one, take that.
3. Check Definition of Ready: acceptance criteria clear, design or pre-registration section linked, test plan stated. If not, fix the ticket text first.
4. Mark the row 🚧 in the audit.

## Work it

- Branch `S<n>/<area>/<slug>`; one ticket per PR where feasible (see `git-pr-workflow`).
- Tests first. Run the gate for the language.
- A ticket larger than 8 points is split in the sprint file before you start.
- If you discover new work, add a ticket (next free number, points, dependencies) instead of hiding it in a PR.

## Close it

1. Audit row: ✅ with the PR, the files and a reproduction command. Partial work is 🟡 with the follow-up ticket named.
2. Update the sprint's status line in `docs/implementation/README.md`.
3. Update `docs/HANDOFF.md` (done, next step) and `docs/handoff/LOG.md`.
4. PR body: `Closes S<n>-T<m>`, what changed, what you ran.

## Close a sprint

All tickets ✅ or explicitly ⏸ with a reason; the definition of done verified; the go/no-go gate written into the handoff for the owner. Never start the next sprint's work past the gate without the owner's decision.

## Research sprints

For S1 to S3 the pre-registration governs. A ticket that would change an arm, measure or analysis after registration becomes a dated amendment, not a silent edit.
