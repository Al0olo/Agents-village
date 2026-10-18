# Rule 0: handoff

Applies to every session, every task, every agent.

1. **Start:** read `docs/HANDOFF.md` completely before doing anything else. If it
   disagrees with the code or git history, trust the code and fix the handoff.
2. **During:** when you finish a unit of work, a decision is made, something fails, or
   you learn a quirk of the environment, write it down in `docs/HANDOFF.md` at that moment.
   Do not wait until the end; sessions can be cut off.
3. **End:** run the `handoff` skill. `docs/HANDOFF.md` must say what is done (with PR
   links), what is in progress, the exact next step, open decisions, and anything that
   will trip the next agent. Append a dated entry to `docs/handoff/LOG.md`.
4. **Write for a cold reader** with no memory of this conversation. Name files, commands,
   PR numbers and branches. No "as discussed", no "the above".
5. A change that touches code, experiments or docs without touching `docs/HANDOFF.md` is
   incomplete. The `Stop` hook and CI both enforce this. Use `[skip-handoff]` in a commit
   message only for pure typo fixes.
