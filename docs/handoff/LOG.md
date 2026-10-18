# Handoff log

Newest first. One entry per session. State lives in [`../HANDOFF.md`](../HANDOFF.md);
this file is history, so a future agent can see how decisions were reached.

## 2026-10-18 · Claude Sonnet 5.5 · rules, skills and handoff system

- Owner decided the frontend stack: TypeScript with Next.js. Updated `.claude/rules/frontend.md`, the `frontend-observer` skill and the handoff.
- Added `AGENTS.md`/`CLAUDE.md` at the root and `CLAUDE.md` imports in key directories,
  path-scoped rules in `.claude/rules/`, ten skills in `.claude/skills/`, hooks
  (SessionStart context, Stop handoff check), `scripts/check-handoff.sh` and a CI job.
- Why: the owner wants any new agent to continue from the last one's state without
  rediscovering anything. Rule 0 makes the handoff mandatory and enforced.
- Sources used: Claude Code docs on memory, skills and hooks. Third-party skill lists
  (aggregators) were not audited; listed as optional only.

## 2026-10-18 · Claude Sonnet 5.5 · repo bootstrap (earlier in the day)

- Created `main` and merged PRs #1 (scaffold), #2 (docs), #3 (README and hero),
  #4 (social preview), #5 (sources and per-directory README/AGENTS).
- Before that, in the research phase: novelty review, a two-pass adversarial review of the
  papers, and verification of the load-bearing claims. Corrections made: the Mandela effect
  "74.4%" average is undefined (anchoring beat scrutiny short-term), PIMMUR figures are
  65.2% and 50.6%, Energy Society used five small models, Survive at All Costs is cited for
  prevalence only. RQ1 was redesigned around paired forks because 4 villages per arm cannot
  beat p = 0.029. RQ2 and RQ3 were deferred.
