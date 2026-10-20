---
name: handoff
description: Read the previous agent's state at the start of a session and write yours at the end. Use at the start and end of every session, after any milestone, decision, failure or environment discovery, and whenever the user says "continue", "pick up", "where are we" or "wrap up".
---

# Handoff

The goal: the next agent, with no memory of this conversation, continues without asking
anyone and without re-deriving anything.

## At the start

1. Read `docs/HANDOFF.md` in full, then the top 3 entries of `docs/handoff/LOG.md`.
2. Verify it against reality: `git status`, `git log --oneline -10`,
   `git branch -a`, and open PRs (the GitHub MCP `list_pull_requests`, or `gh api repos/al0olo/agents-village/pulls --jq '.[].title'`).
3. If the handoff and reality disagree, believe reality, then fix the handoff before
   starting new work and say so in the log.
4. Restate the next step to the user in one or two sentences, then do it.

## While working

Update `docs/HANDOFF.md` immediately when any of these happens: a unit of work finishes,
a decision is made, an approach fails, you find an environment quirk, you open or merge a PR.

## At the end (or when cut off)

1. Rewrite `docs/HANDOFF.md` using the template below. It is current state, not history:
   replace stale lines, do not pile up.
2. Prepend a dated entry to `docs/handoff/LOG.md` (newest first): what you did, why,
   what failed, links. History lives there.
3. Run `scripts/check-handoff.sh` and commit the handoff with the work.
4. Final message to the user: what is done, what is next, anything that needs their decision.

## Template for docs/HANDOFF.md

```
# Handoff
Updated: YYYY-MM-DD by <agent/model> · Branch: <name> · Last commit: <sha>

## Objective
One paragraph: what the project is trying to achieve right now.

## State
- Done: item (PR #n)
- In progress: item, exactly where it stopped, uncommitted files if any
- Not started: item

## Next step
The single next action, concrete enough to start immediately, with commands.

## Queue
Ordered list after the next step.

## Open decisions (owner needs to decide)
Question, options, my recommendation.

## Gotchas
Environment quirks, failed approaches and why, things that look wrong but are intended.

## How to verify
Commands that prove the current state is healthy.

## Pointers
Files and docs to read for depth.
```

## Quality bar

- Name files, branches, PR numbers, commands. No "as above", no "the thing we discussed".
- Record failed approaches and why, so nobody repeats them.
- Separate what you verified from what you assume, and say which is which.
- Keep `docs/HANDOFF.md` under about 150 lines; move history to the log.
