# Handoff log

Newest first. One entry per session. State lives in [`../HANDOFF.md`](../HANDOFF.md);
this file is history, so a future agent can see how decisions were reached.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T2 village state and scheduler

- PR #10 (T1) was merged; restarted the session branch from `main` at `21736e7`.
- Implemented `harness/src/agent_village/village.py`: `SimClock`, `VillageState`, `Village` (`add_citizen`, `request_wake`, `sleep`, `step`, `state`). Design choices: one pending wake per citizen (earliest wins); a due citizen who is still awake keeps its request until it sleeps, so no wake is lost; the awake cap is the OASIS-style subset idea from the PRD; order within the cap is oldest request, then a seeded draw, then name, so nobody starves and a seed fixes the order. Reasons (message, timer, event) are recorded for audit.
- Tests first, 20 cases. Mutation-checked by hand: removing the cap, ranking by random first, ignoring awake citizens and keeping the latest wake each fail tests. A stale `.pyc` briefly made a restored file look broken; clearing `__pycache__` fixed it.
- Not done: rebuilding a village from a log (T29), forks (T13), wake-on-message (T6). Seeds are not logged by the village; the run layer must record them with the config hash.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T1 event log

- Handoff header was stale (named a merged branch and an old base); corrected to `main` at `fe6b1af`. No open PRs at the start.
- Implemented `harness/src/agent_village/eventlog.py`: JSONL, sequential ids, SHA-256 over a canonical JSON form that includes the previous hash, verified on open; payloads are normalised through JSON so live events equal reloaded ones. Tests first, 15 cases including edit, delete, reorder and truncation. The pinned hash vector was computed independently of the implementation.
- Scope choice: chain verification landed in T1 because the chain cannot be tested without it; T26 keeps signatures. Not done: single-writer locking (T31), SQLite (T25).
- Did not install the optional third-party skills: unaudited, and nothing in T1 needs them. The project skills in `.claude/skills/` were the reference.
- Verified: `ruff check`, `ruff format --check`, `pytest -q` (21 passed) in `harness/`. Cargo gate not run; no Rust changed.

## 2026-10-18 · Claude Sonnet 5.5 · decisions: OpenTofu and the memory arm

- Owner delegated both open decisions. Read OpenTofu's site and repository (MPL-2.0, LF-stewarded, native state encryption, drop-in for Terraform) and Mem0's README (Apache-2.0, LLM in the write path, benchmark scores vendor-reported for the managed platform). Chose OpenTofu on AWS with ECS Fargate on-demand (no Spot: interruptions invalidate blocks), and an exploratory arm F with Mem0 OSS after the pilot, excluded from the primary contrast. The BUSL status of Terraform comes from OpenTofu's own page, not an independent source.
- Not verified: OpenTofu's latest version number (the site banner said 1.13.0; the repo page showed none), Fargate versus EC2 cost.

## 2026-10-18 · Claude Sonnet 5.5 · ADR-0001 storage and memory

- Owner asked what to use for agent memory and storage and wanted the harness air-tight. Decision: event log we own, rebuildable projections, SQLite in the harness, Postgres in the kernel, forks by log prefix; no off-the-shelf memory layer in the write path. Search results on memory products were aggregators, so no benchmark numbers were used.
- Owner asked whether IaC is planned: it was not (only a gateway ticket in S2). Added ADR-0002 (proposed: Terraform on AWS, minimal, phased) and tickets S2-T13 to T17, S3-T13, S4-T19 to T21. Hakim's ADR-0005 informed the choice.
- Added `docs/adr/` (template from the Hakim repo), S1-T25 to T31, S4-T15 to T18, kernel invariants 9 and 10, PRD sections 7 and 8 updated. Open: optional off-the-shelf-memory arm for RQ1 (owner to decide before pre-registration).

## 2026-10-18 · Claude Sonnet 5.5 · sprint plan and implementation audits

- Modelled on the layout of the owner's `Al0olo/hakim` repo: `docs/sprints/` holds intent (goal, tickets with points and dependencies, definition of done, risks, demo, go/no-go) and `docs/implementation/` holds state per sprint. Adapted for research: sprints S1 to S3 run RQ1 on a Python harness, S4 builds the Rust kernel in parallel, S5 to S8 are outlined for after RQ1.
- Branch naming changed to `S<n>/<area>/<slug>`; PRs say `Closes S<n>-T<m>`. Added the `sprint-workflow` skill.
- Point totals: S1 about 100, S2 about 47, S3 about 59, S4 about 79; these are planning estimates, not measured.

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
