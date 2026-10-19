# Handoff

Updated: 2026-10-19 by Claude Sonnet 5.5 · Branch: `claude/gracious-albattani-osio94` · Base: `main` at `fa62722`

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
  (the original Claude Docs artifacts are stale copies, do not edit them), the monorepo with the Rust
  workspace and Python harness, research sources, agent rules, skills, sprint plan and audits,
  ADR-0001 (storage and memory), ADR-0002 (OpenTofu on AWS), and the exploratory Mem0 arm F (S1-T32).
- Done, sprint S1 (merged), all in `harness/src/agent_village/`:
  T1 event log `eventlog.py` (#10), T2 scheduler `village.py` (#11), T3 model interface
  `model.py` and `openrouter.py` (#12), T5 memory tiers `memory.py` (#13), T6 messages
  `messages.py` (#14), T4 citizen loop `runner.py`, `actions.py`, `prompts.py` (#15),
  T13 snapshot and fork `fork.py` (#16), T7 and T8 arms D and A `arms.py` (#17), T15 launch
  controller `launch.py` (#19), T14 replay `replay.py` (#20).
  Status per ticket is in `docs/implementation/S1-rq1-harness.md`.
- Done, PRs #18 to #21: `admit` ignores a told event that originates with the writer, and the shared
  base village runs without defense until the fork (ADR-0003, `arms.BASE`); launch controller `launch.py`;
  replay `replay.py`; facts, planting and probes (`facts.py`, `planting.py`, `probes.py`, `Runner.ask`; ADR-0004, proposed).
- Done, PR #22: S1-T20 blinded judge `judge.py` and S1-T21 metrics `metrics.py` (ADR-0005), and the first live
  OpenRouter check ("Live check" in `docs/implementation/S1-rq1-harness.md`): provider on the chat response,
  generation id and cost on `Response`, `served_snapshots`, `reasoning` option, HTTP status in transport errors.
- In progress, S1-T19 and the completion of T21 (`claude/gracious-albattani-osio94`, PR to be opened): the utility
  task (`facts.utility_facts`, `UTILITY_FRAME`, `Metrics.utility_score`; ADR-0006, proposed); `openrouter.Retrying`
  retries 429, 5xx and failed connections with backoff and logs the attempts; the runner finds a recipient in any
  case; a no-content response says how it ended. ADR-0004 and ADR-0005 are accepted. 661 tests, 100% coverage.
- Decided: IaC is OpenTofu on AWS in `infra/`. Memory is a projection of an event log we own
  (SQLite in the harness, Postgres in the kernel, forks by log prefix; ADR-0001). Observer UI
  is TypeScript with Next.js in `apps/observer/`, not scaffolded yet. Base village runs
  without defense (ADR-0003).
- Not started: RQ1 pre-registration, the pilot, the real kernel (M1), the observer UI.

## Next step

Once this PR is merged, restart the branch from `main` and take T11
(arm E, the random block: a deterministic policy keyed on the claim, block rate set from arm D in the
pilot), T9 (arm B prompts, which the owner reviews), T12 and T10 (consolidation and arm C), and the
storage tickets T25 to T31. The pre-registration is S2-T1; do not run an experiment before it is
approved. Short live checks of plumbing are fine under a hard cap (no gateway yet: S2-T5). Open the PR
yourself with the template filled in; the owner reviews and merges.

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
- Decided by recommendation: ADR-0004 (true facts have two independent holders, so arm D blocks single-witness
  facts by design) and ADR-0005 (codes, k = 2, verbatim claim matcher). Still for the owner: review the fact
  templates and name lists (`facts.py`), the awareness question and the utility frame (both pinned by tests),
  and the judge model, accepted only if human-sample kappa is good (pilot).
- ADR-0006 (proposed): the utility task. Two true single-witness facts per block asked as a task. In the live
  check the score was 0 of 14 in both arms because small models did not pass them on; if the pilot shows the
  same at frontier quality, the task needs a nudge decided before pre-registration.

## Gotchas

Environment
- `gh pr create` fails in cloud sessions (GraphQL blocked); PRs are opened with the GitHub MCP tool.
- The clone may be shallow; `git fetch origin main` then `git checkout -B <branch> origin/main`.
- `pip install` needs `--break-system-packages`. Coverage needs `pytest-cov` (not a project
  dependency until S1-T24) and `python3 -m pytest --cov=agent_village --cov-branch`; `.coverage` is git-ignored.
- After editing a source file twice within one second, pytest can run stale bytecode; delete `__pycache__`.
- GitHub shows the repo as `Al0olo/Agents-village`; API path `al0olo/agents-village` works. No `README.md` under `.github/`.

Research claims
- Verified: exact permutation test floors (p = 0.029 at 4 per arm). NOT verified: the power
  estimate (d about 1.0 with 10 blocks) and the $1k to $10k cost. Papers cited at abstract level
  or from secondary summaries are marked in `docs/research/sources.md`; never state their figures
  as verified. Third-party skills were not audited.
- OpenRouter, verified live (details in the audit): the chat response names the `provider`; the model
  field is the alias, the dated snapshot is only in the generation record (about 9 s later); `usage.cost`
  is per call and matches the key counter. The sandbox proxy adds the credential: use `urllib_transport(None)`,
  send no key, never print one. With fallbacks off, upstream HTTP 429 happens (about 1.5% of calls): wrap the
  backend in `Retrying` (2 to 30 s backoff, attempts logged); the spend cap stays with the gateway (S2-T5). Haiku 5.5 reasons by default and
  returns empty content at small `max_tokens`: use `OpenRouterBackend(..., reasoning={"enabled": False})`.
  `openai/gpt-oss-20b` cannot disable reasoning and is unusable. Not verified: the cost per citizen-day,
  frontier-model behavior. The live backend has no spend cap or kill switch (S2-T5): cap any live script.
- Write citizen names capitalized: lowercase names caused most invalid actions in the first live check (35 and 44
  invalid actions fell to 6 and 7 once capitalized). The runner also matches a recipient in any case.

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
- Launch blocks only through `launch.launch`: every arm gets the same `RunConfig` and a backend from one
  factory, and each log gets a `launch` event with the config hash. A block that fails or drifts (one requested
  model served more than one snapshot or provider, base run included) is dead and excluded. Whether the real
  OpenRouter reports a stable served id for a pinned snapshot is NOT verified, so the drift check may false-alarm
  on the first live call. S3-T3 (run monitor) and S2-T15 (cloud batch runner) build on `Launch`.
- Audit replay re-drives a log with the real runner on `RecordedBackend.from_log(log, start)`; `saw`, `did`,
  `plant` and `launch` events are re-appended and a `probe_round` is re-executed from its marker. Any other
  event a driver appends between ticks is reported as unreplayable. A replayed log is byte-identical; the first
  difference is reported with its index and reason.
- A branch (counterfactual) replays to a tick boundary to recover state and rng, then continues as another arm.
  It must not append marker events, or every later event number shifts. Prompts carry event numbers, so once a
  branch's numbering diverges no recorded output matches and every call is fresh (`ReplayBackend` counts both).
  Per-citizen numbers would keep reuse alive but change the treatment; revisit only if counterfactuals become a tool.
- A model error stops the run (no retry), leaving woken citizens awake; exclusion rules cover crashed villages.
- Pre-fork memory entries stay as the base stored them (ADR-0003); the kernel never reclassifies them.
- Archival memory is not implemented (T27, T28). The event log is JSONL until T25 moves it into SQLite behind
  the same `EventLog` interface; dropping the tail of a log still verifies, so compare `head` against a recorded value.
- The session branch `claude/...` overrides the `S<n>/<area>/<slug>` convention; PRs still say `Closes S1-T<n>`.
- Facts, planting and probes: a block is `generate(seed, block)`, `make_plan(...)`, `announce` before the first
  tick, `plant` between ticks (returns the snapshot to fork from), then `probes.run_round` at the end. Planted facts
  are first-hand `saw` events plus `plant` markers; never inject messages. Probes go through `Runner.ask`, which
  changes nothing a citizen knows; the reply is a `say` to `visitor` and `answer_of` extracts the text.
- Small models rarely passed a planted fact on in 8 ticks; frontier behavior and the elders notice are for the
  pilot. Probe temperature is the loop's (0.7 placeholder); decide it before pre-registration. The judge runs
  at temperature 0, `max_tokens` 60, with reasoning off; a judge reply that does not parse is `None`.

## How to verify

```bash
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace
cd harness && ruff check . && pytest -q
scripts/check-handoff.sh
```

## Pointers

- `docs/sprints/README.md`: sprint index; `docs/implementation/README.md`: status index
- `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`: how to work here
- `docs/prd.md` section 1: research questions and the RQ1 design
- `docs/adr/`: decisions (ADR-0003 base village, ADR-0004 planting, ADR-0005 coding and measures)
- `docs/milestones.md`: M1 to M5, gates, cost model
- `docs/research/sources.md`: bibliography with reading levels
- `docs/handoff/LOG.md`: history of sessions
