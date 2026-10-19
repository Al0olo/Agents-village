# Handoff

Updated: 2026-10-19 by Claude Sonnet 5.5 · Branch: `claude/gracious-albattani-osio94` · Base: `main` at `394f775`

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
- Done, sprint S1 so far (PRs #10 to #25), in `harness/src/agent_village/`: event log, scheduler, model interface
  and OpenRouter backend (with `Retrying`), memory tiers, messages, citizen loop, snapshot and fork, arms A, D,
  E (`RandomBlock`, `matched_rate`) and exploratory G (`admit_corroborated`, ADR-0007), launch controller, replay,
  facts, planting, probes, utility task (ADR-0006), judge and metrics (ADR-0005). ADR-0004 and 0005 are accepted.
  `admit` ignores a told event that originates with the writer; the base village runs without defense until
  the fork (ADR-0003). Live checks and smoke villages are in the audit; status per ticket is there too.
- Done, PR #26: S1-T9 arm B (three pinned wordings; arms B, B2, B3).
- In progress, owner-delegated decisions in PR #27 (`claude/gracious-albattani-osio94`): the owner handed the open
  decisions to Claude; they are ADR-0008 (measures: assertion primary, carry rates, rubric `judge-fact-2`, two
  judges, awareness funnel with `judge-awareness-2`, interim probe rounds), ADR-0009 (run configuration: models,
  a day of 12 ticks, probe schedule, cost basis), ADR-0010 (citizens remember their own experience, `render-2`);
  ADR-0006 and 0007 are accepted. Found with OpenRouter I/O logging: citizens forgot their own sightings and
  disowned wiki entries, which distorted arm B; fixed. 827 tests, 100% coverage.
- Decided: IaC is OpenTofu on AWS in `infra/`. Memory is a projection of an event log we own
  (SQLite in the harness, Postgres in the kernel, forks by log prefix; ADR-0001). Observer UI
  is TypeScript with Next.js in `apps/observer/`, not scaffolded yet. Base village runs
  without defense (ADR-0003).
- Not started: RQ1 pre-registration, the pilot, the real kernel (M1), the observer UI.

## Next step

Once this PR is merged, restart the branch from `main`. First re-run arm B and its paraphrases (and A, D, E, G)
on `render-2` and a 36-tick village with the interim probe rounds (ADR-0009), about $8 to $10 and 40 minutes:
the old arm B numbers are partly the forgetting artifact. Then T12 and T10 (consolidation at ticks 12 and 24,
and arm C; design it as ADR-0011, reading the Manufactured Confidence paper beyond its abstract), then the
storage tickets T25 to T31, then the pre-registration (S2-T1) from ADRs 0004 to 0010. The owner still owns:
approving and registering the pre-registration, a human coding the sample sheet, and the real gateway. Live
checks are fine: the owner put $50 on the key (about $18 used) and allowed frontier models; the live backend has
no gateway cap, so cap every script and never print the key. Stored prompts and outputs of calls made since
logging was enabled are readable at `/generation/content?id=<generation id>` (HTTP 404 for older calls): read
them before changing a prompt. Open the PR yourself with the template filled in; the owner reviews and merges.

## Queue

Follow the sprint plan in `docs/sprints/`: S1 harness (weeks 1 to 4), S2 pilot and
pre-registration (5 to 8), S3 main run and report (9 to 16), S4 Rust kernel in parallel
(5 to 16). S5 to S8 are outlined and wait for RQ1. Ticket status is in `docs/implementation/`.

## Decisions (taken by Claude on the owner's delegation, 2026-10-19)

- Primary outcome is the assertion rate; carry rates (asserted or hedged) are secondary and say whether spread
  fell (ADR-0008). Arm B wording stands. Arm G stays strict and exploratory, no milder variant until the pilot
  shows G silences the wiki (ADR-0007). The utility task needs no nudge: frontier citizens pass single-witness
  facts on (ADR-0006). Model mix is Opus 5.5, GPT-5.6 Sol and DeepSeek V4 Pro; a day is 12 ticks; cost basis is
  measured, about $20 to $30 a block extrapolated (ADR-0009). License Apache-2.0 stands; inference runs on the
  owner's OpenRouter key behind a spend cap before any reported run. Names and templates stand after a 12-name
  sample search (none real).
- Still open and owner-only: human validation of the judge on the sample sheet (the two judges agree at
  kappa 0.90 and 1.0, which is not human validation); registering the pre-registration; a real self-hosted
  open-weight replicate (S2-T13).
- Flagged, not decided: in the fifth village awareness at the direct question was 0 of 8 under no defense, 1
  under the prompt defense and 4 under the kernel; an arm difference would threaten the unawareness control,
  so replicate it before registering. A kernel arm's hearsay is visible in the citizen's Recall section.
- Single villages are noisy: the same seed and models gave A attack 36%, 17% and 26% (rubric 2). The pilot's
  between-village variance sets the number of blocks; do not read a contrast from one block.

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
  returns empty content at small `max_tokens`: use `OpenRouterBackend(..., reasoning={model: {"enabled": False}})`
  per model; Opus 5.5 and `openai/gpt-oss-20b` cannot disable it (HTTP 400), so give them a larger `max_tokens`. Not verified: the cost per citizen-day,
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
