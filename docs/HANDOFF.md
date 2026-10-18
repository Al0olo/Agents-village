# Handoff

Updated: 2026-10-18 by Claude Sonnet 5.5 · Branch: `claude/gracious-albattani-osio94` · Base: `main` at `350f312`

## Objective

Build Agent Village as an instrument for pre-registered experiments on long-lived LLM
societies. Flagship question RQ1: does a kernel that admits claims into shared memory only
with a kernel-checkable citation reduce false-fact spread beyond the strongest prompt-level
defense, without blocking true information? RQ2 (purpose vs model and cost) and RQ3 (what
parent-authored reproduction selects for) are deferred until RQ1 is reported. The owner
(Abdullah Farag, Dubai) wants research novelty and a respectable reputation first;
funding is a later concern.

## State

- Done, project setup (PRs #1 to #9): PRD and milestones in `docs/prd.md` and `docs/milestones.md`
  (the original Claude Docs artifacts are stale copies, do not edit them), monorepo scaffold
  with the Rust workspace and the Python harness, README, research sources, agent rules,
  skills and handoff system, sprint plan and audits, ADR-0001 (storage and memory), ADR-0002
  (OpenTofu on AWS), and the exploratory Mem0 arm F (S1-T32).
- Done, sprint S1 (merged), all in `harness/src/agent_village/`:
  T1 event log `eventlog.py` (#10), T2 scheduler `village.py` (#11), T3 model interface
  `model.py` and `openrouter.py` (#12), T5 memory tiers `memory.py` (#13), T6 messages
  `messages.py` (#14), T4 citizen loop `runner.py`, `actions.py`, `prompts.py` (#15),
  T13 snapshot and fork `fork.py` (#16), T7 and T8 arms D and A `arms.py` (#17), T15 launch
  controller `launch.py` (#19).
  Status per ticket is in `docs/implementation/S1-rq1-harness.md`.
- Done, PR #18: `admit` ignores a told event whose origins include the writer (the writer's own
  claim coming back), and ADR-0003 settles that the shared base village runs without defense
  until the fork (`arms.BASE`, which is arm A).
- Done, PR #19: S1-T15, the launch controller (`launch.py`).
- In progress: S1-T14, audit and counterfactual replay (`replay.py`; `RecordedBackend.from_log` now takes a
  start position; 38 new tests, 388 in all, 100% line and branch coverage). PR open on branch
  `claude/gracious-albattani-osio94`.
- Decided: IaC is OpenTofu on AWS in `infra/`. Memory is a projection of an event log we own
  (SQLite in the harness, Postgres in the kernel, forks by log prefix; ADR-0001). Observer UI
  is TypeScript with Next.js in `apps/observer/`, not scaffolded yet. Base village runs
  without defense (ADR-0003).
- Not started: RQ1 pre-registration, the 2-block pilot, the real kernel (M1), the observer UI.

## Next step

Once the S1-T14 PR is merged, restart the branch from `main` and take S1-T16 (fictional fact
generator, counterbalanced plausibility and planter status), then T17 (the planting event and the
colluding-planter arm) and T18 (neutral probes and the awareness probe). Plant facts as `saw`
events appended between ticks, snapshot after, and keep every fact about fictional entities only.
Then T11 (arm E, the random block: a deterministic policy keyed on the claim, with the block rate
as a parameter that the pilot sets from arm D), T9 (arm B prompts, which the owner reviews), T12
and T10 (consolidation and arm C), T19 to T21 (utility task, judge, metrics) and the storage
tickets T25 to T31. The pre-registration is S2-T1; do not run anything live before it is
approved. Open the PR yourself with the template filled in; the owner reviews and merges.

## Queue

Follow the sprint plan in `docs/sprints/`: S1 harness (weeks 1 to 4), S2 pilot and
pre-registration (5 to 8), S3 main run and report (9 to 16), S4 Rust kernel in parallel
(5 to 16). S5 to S8 are outlined and wait for RQ1. Ticket status is in `docs/implementation/`.

## Open decisions (owner)

- License is Apache-2.0, chosen by the agent without asking; confirm.
- Model mix for RQ1: two frontier models and one pinned open-weight model; which ones.
- Where to run the pilot and who pays for inference (estimate about $1k to $10k for the
  full RQ1 at assumed prices; the measured cost per citizen-day replaces it).
- Arm prompts and `LoopConfig` defaults are placeholders until the owner reviews them at the S1 gate.

## Gotchas

Environment
- `gh pr create` fails in cloud sessions (GraphQL blocked); PRs are opened with the GitHub MCP tool.
- The clone may be shallow; `git fetch origin main` then `git checkout -B <branch> origin/main`.
- `pip install` needs `--break-system-packages`. Coverage needs `pytest-cov` (not a project
  dependency until S1-T24) and `python3 -m pytest --cov=agent_village --cov-branch`; `.coverage` is git-ignored.
- After editing a source file twice within one second, pytest can run stale bytecode; delete `__pycache__`.
- GitHub shows the repo as `Al0olo/Agents-village`; API path `al0olo/agents-village` works.
  Do not add `README.md` under `.github/`.

Research claims
- Verified: exact permutation test floors (p = 0.029 at 4 per arm). NOT verified: the power
  estimate (d about 1.0 with 10 blocks) and the $1k to $10k cost. Papers cited at abstract level
  or from secondary summaries are marked in `docs/research/sources.md`; never state their figures
  as verified. Third-party skills were not audited.
- OpenRouter: only the request side (`provider.allow_fallbacks`, `provider.only`) and the generation
  record (`data.provider_name`) are documented. Whether the chat response carries a `provider`
  field, and how soon the generation record is readable, are NOT verified; check on the first
  live call in S2. The live backend has no spend cap or kill switch (S2-T5): never call it outside that gateway.

Design rules that tests depend on
- Evidence is only `saw`, `did` (written by the citizen or environment) and `told` (written by the
  recipient with `origins`). Acting is not evidence: the loop never logs `did` for what a citizen
  says or writes. Tool receipts and ledger entries are not evidence yet; add them with a forgery test.
- Origins only grow along a forward; a message never goes to one of its own origins, and `admit`
  also ignores a told event that originates with the writer. Two colluding senders are two
  independent origins by design; the colluding-planter arm (S1-T17) measures that.
- A village's state is a fold over its log; only the rng state lives outside it, so a `Snapshot`
  is the log position, head and rng state. Snapshots are valid between ticks only. The planting
  event (T17) must be appended between ticks, then the snapshot taken.
- Launch blocks only through `launch.launch`: every arm gets the same `RunConfig` (specs, `max_awake`,
  `LoopConfig`) and a backend from one factory, and each log gets a `launch` event with the config
  hash. Forks made by hand with `fork.fork` do not record the config.
- A block that fails or drifts is dead (`Launch` refuses further ticks); the experiment excludes it.
  Drift means one requested model served more than one snapshot or provider across all arms, base
  run included. Whether the real OpenRouter reports a stable served id for a pinned snapshot is NOT
  verified, so the drift check may false-alarm on the first live call; check in S2.
  S3-T3 (run monitor) and S2-T15 (cloud batch runner) build on `Launch`.
- Audit replay re-drives a log: ticks run the real runner against `RecordedBackend.from_log(log, start)`,
  and `saw`, `did` and `launch` events are re-appended. Anything else a driver appends between ticks
  (for example a hand-made `request_wake`) is reported as unreplayable. A replayed log is byte-identical
  to the original; the first difference is reported with its index and reason. Audits of launched arms
  check the arm name, config hash and prompt hash against the `launch` event.
- A branch (counterfactual) replays to a tick boundary to recover the state and rng there, then continues
  as a different arm. It must not append marker events, or all later event numbers shift. Prompts carry
  event numbers, so after a branch's numbering diverges no recorded output matches again and every call
  is fresh; `ReplayBackend` counts replayed and fresh calls. Per-citizen numbers in prompts would keep
  reuse alive longer but change the treatment; not needed for RQ1, revisit only if counterfactuals become a tool.
- A model error stops the run (no retry), leaving woken citizens awake; exclusion rules cover crashed villages.
- Pre-fork memory entries stay as the base stored them (ADR-0003); the kernel never reclassifies them.
- Archival memory is not implemented (T27, T28): three tiers of the PRD's four until then.
- The event log is a JSONL file; T25 moves it into SQLite behind the same `EventLog` interface.
  Dropping the tail of a log still verifies, so compare `head` against a recorded value.
- The session branch `claude/...` overrides the `S<n>/<area>/<slug>` convention; PRs still say `Closes S1-T<n>`.

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
- `docs/adr/`: decisions, including ADR-0003 on the base village
- `docs/milestones.md`: M1 to M5, gates, cost model
- `docs/research/sources.md`: bibliography with reading levels
- `docs/handoff/LOG.md`: history of sessions
