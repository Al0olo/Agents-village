# Handoff

Updated: 2026-10-18 by Claude Sonnet 5.5 · Branch: `claude/gracious-albattani-osio94` · Base: `main` at `21736e7`

## Objective

Build Agent Village as an instrument for pre-registered experiments on long-lived LLM
societies. Flagship question RQ1: does a kernel that admits claims into shared memory only
with a kernel-checkable citation reduce false-fact spread beyond the strongest prompt-level
defense, without blocking true information? RQ2 (purpose vs model and cost) and RQ3 (what
parent-authored reproduction selects for) are deferred until RQ1 is reported. The owner
(Abdullah Farag, Dubai) wants research novelty and a respectable reputation first;
funding is a later concern.

## State

- Done: PRD and Milestones written and polished, now in `docs/prd.md` and `docs/milestones.md`.
  The repo is the source of truth from here on. The original editable drafts are Claude Docs
  artifacts (PRD `510fd672-456e-4e1e-8caf-1e8fb822afe6`, Milestones `0b366759-60d8-4636-9cae-ace8a2587bbd`
  at claude.ai/code/artifact/<id>); they are stale copies, do not edit them.
- Done: monorepo scaffold (PR #1): Rust workspace (`village-kernel`, `village-ledger`
  [tested, double-entry], `village-memory`, `village-cli`), Python harness with a tested
  reference admission policy (`harness/src/agent_village/admission.py`), CI, community files.
- Done: README with hero image (PR #3), research sources with reading levels (PR #5),
  README and AGENTS file in every directory (PR #5), social preview image (PR #4).
- Done: agent rules, skills, hooks and handoff system (PR #6); sprint plan and implementation audits (PR #7).
- Done: ADR-0001 storage and memory and ADR-0002 IaC (PR #8).
- Done: decisions finalized (PR #9): ADR-0002 accepted as OpenTofu on AWS with ECS Fargate on-demand runners; RQ1 gets an exploratory arm F (Mem0 OSS) after the pilot, ticket S1-T32.
- Done: S1-T1, the append-only hash-chained JSONL event log (`harness/src/agent_village/eventlog.py`, 15 tests). It verifies the chain on open, so S1-T26 now covers Ed25519 signatures only. Merged in PR #10.
- Done: S1-T2, village state and deterministic scheduler (`harness/src/agent_village/village.py`, 20 tests): injected `SimClock` and `random.Random`, awake cap, oldest wake request first with seeded tie-break, every change a log event. On branch `claude/gracious-albattani-osio94`, not yet in a PR.
- Decided: IaC is OpenTofu on AWS in `infra/`; the owner delegated the choice. Memory is a projection of an event log we own; SQLite in the harness, Postgres in the kernel, same schema, forks by log prefix (`docs/adr/0001-storage-and-memory.md`).
- Decided: observer UI is TypeScript with Next.js (App Router) in `apps/observer/`, pnpm. Not scaffolded yet; add the CI job when it is.
- Not started: RQ1 pre-registration, the 2-block pilot, the paired-fork village runner,
  the real kernel (M1), the observer UI.

## Next step

Open the PR for S1-T2 (`Closes S1-T2`; REST API command in `.claude/rules/git.md`), then
take S1-T3 (model interface with fake, recorded and live backends; log snapshot id and
routed provider) in `harness/src/agent_village/`. After that T5, T6, T4 and the storage
tickets T25 to T31. The pre-registration is S2-T1 and comes after the harness exists; do
not run anything live before it is approved.

## Queue

Follow the sprint plan in `docs/sprints/`: S1 harness (weeks 1 to 4), S2 pilot and
pre-registration (5 to 8), S3 main run and report (9 to 16), S4 Rust kernel in parallel
(5 to 16). S5 to S8 are outlined and wait for RQ1. Ticket status is in `docs/implementation/`.

## Open decisions (owner)

- License is Apache-2.0, chosen by the agent without asking; confirm.
- Model mix for RQ1: two frontier models and one pinned open-weight model; which ones.
- Where to run the pilot and who pays for inference (estimate about $1k to $10k for the
  full RQ1 at assumed prices; the measured cost per citizen-day replaces it).

## Gotchas

- `gh pr create` fails in cloud sessions (GraphQL blocked). Use the REST API; see
  `.claude/rules/git.md`.
- The clone is shallow; `origin/main` may not resolve. `git fetch origin main` then
  `git reset --hard FETCH_HEAD` on `main`.
- `pip install` needs `--break-system-packages` in the sandbox.
- GitHub shows the repo as `Al0olo/Agents-village`; API path `al0olo/agents-village` works.
- Do not add `README.md` under `.github/`: GitHub would show it instead of the root README.
- Verified numbers: exact permutation test floors (p = 0.029 at 4 per arm). NOT verified:
  the power estimate (d about 1.0 with 10 blocks) and the $1k to $10k cost; these are planning
  numbers. Papers cited at abstract level or from secondary summaries are marked in
  `docs/research/sources.md`; never state their figures as verified.
- Papers still unread or unverified: Behavioral Inheritance peer-review status, Genomebook
  beyond the abstract, Survive at All Costs full text, AI Village and Moltbook figures, MAST
  numbers, Emergence World licence, the Sotopia, Voyager, Generative Agents, Concordia and
  Melting Pot claims.
- Third-party skills were not audited; see `.claude/skills/README.md`.

- The event log is a plain JSONL file with no database yet. T25 moves events into SQLite; keep `EventLog` as the interface so callers do not change. Dropping the tail of a log still verifies, so compare `head` against a recorded value.
- The session branch name `claude/...` overrides the `S<n>/<area>/<slug>` convention when the harness assigns one; the PR still says `Closes S1-T<n>`.

- `Village` refuses a non-empty log: rebuilding state from a log is T29, not T2. Its tick events are the only record of the clock, so keep them.
- After editing a source file twice within one second, pytest can run stale bytecode (found while mutation-testing). Delete `__pycache__` if a result contradicts the source.

## How to verify

```bash
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace
cd harness && ruff check . && pytest -q
scripts/check-handoff.sh
```

## Pointers

- `docs/sprints/README.md`: sprint index and conventions; `docs/implementation/README.md`: status index
- `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`: how to work here
- `docs/prd.md` section 1: research questions and the RQ1 design
- `docs/milestones.md`: M1 to M5, gates, cost model
- `docs/research/sources.md`: bibliography with reading levels
- `docs/handoff/LOG.md`: history of sessions
