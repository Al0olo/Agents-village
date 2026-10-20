# Handoff

Updated: 2026-10-20 by Claude Sonnet 5.5 · Branch: `claude/gracious-albattani-osio94` · Base: `main` at `dfeacd3`

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
- Done, PR #27: ADR-0008 to 0010 (measures, run configuration, citizens' memory), `render-2`, ADR-0006 and 0007 accepted.
- Done, PR #28: the owner handed the remaining items to Claude. Added:
  `gateway.py` (spend cap, call cap, per-model cap, latching kill file; S2-T5), `block.py` and
  `experiments/rq1-provenance/run_block.py` (one RQ1 block live, two judges, credit preflight),
  `analysis.py` (paired exact test, intervals, Holm; S2-T2), arm Bc and ADR-0011 (prompt family chosen on the pilot),
  per-model provider pins, `judge-fact-3` and `judge-awareness-2` with `replay_codes`, the pre-registration draft
  (S2-T1) and log release plan (S2-T11), reference-paper findings in the experiment-design skill. 903 tests, 100% coverage.
- Decided: IaC is OpenTofu on AWS in `infra/`. Memory is a projection of an event log we own
  (SQLite in the harness, Postgres in the kernel, forks by log prefix; ADR-0001). Observer UI
  is TypeScript with Next.js in `apps/observer/`, not scaffolded yet. Base village runs
  without defense (ADR-0003).
- Done, PRs #29 to #31: replication blocks 1 to 3 on `render-2` (false facts asserted: A 19, 50, 50%; B 2, 10%; Bc 26, 60%;
  D 79, 55, 45%; G 0, 0%; B lowers true-fact assertion and utility as much and not carriage, Bc does nothing, D is not better
  than A because the lone witness is admitted, G silences the wiki; awareness did not differ by arm), `rate_sheet.py` (Opus 5.5 as
  the stand-in human, kappa 0.90 and 0.92 with the judges; a model, not a person), `analyze_blocks.py` (`--judge 1|2`),
  ADR-0012 (D stays as specified, G exploratory), and a test that three rewordings of the rubric's `denies` line shift a
  borderline class, so the rubric stays. Numbers: `docs/implementation/S1-rq1-harness.md`, `experiments/rq1-provenance/smoke-2026-10-19/`.
- Done, PR #32 (branch `claude/gracious-albattani-osio94`): S1-T10 and T12, ADR-0013: a review pass at the end
  of days 1 and 2 in every arm (`consolidation.py`, `Runner.review`, `parse_notes`, `BlockConfig.consolidate`), with audit
  replay support, and arm C (`STANCE_PRESERVING`: arm A with the hedge-preserving review prompt). 958 tests, 100% coverage,
  every mutant killed. Block 4 (A, B, C, D, first with the review): false facts asserted 60, 21, 55, 43%; C is a null against A;
  the default review prompt did not visibly strip doubts; D's told notes became hearsay (10 of 32) where other arms stored
  them as fact. One block, not comparable with blocks 1 to 3.
- Done, PR #31: ADR-0012 (D stays as specified, G exploratory), the
  decision written into the pre-registration, a judge-sensitivity analysis (`analyze_blocks.py --judge 2`: same
  contrasts under GPT-5.6 Sol), and a test that three rewordings of the `denies` line of the rubric shift 23 to 27% of a
  borderline class (so the rubric is not changed; the skill and the audit say how to test a rewording).
- Done, PR #30: replication blocks 2 (A, D, G) and 3 (A, B, Bc, D, G)
  and `experiments/rq1-provenance/analyze_blocks.py` (per-block table, paired differences from arm A). False facts
  asserted, blocks 1 to 3: A 19, 50, 50%; B 2, 10%; Bc 26, 60%; D 79, 55, 45%; G 0, 0%. B lowers true-fact assertion and
  utility as much (25%; 36, 0%) without lowering carriage; Bc does nothing; D is not better than A (+20 points,
  interval -5 to +60) because the lone witness's wiki entry is admitted (wiki contamination 100, 100, 67%); G silences
  the wiki (true facts 0, 8%). Awareness did not differ consistently (D 6, 2, 4 of 8; A 3, 3, 4). Numbers in
  `docs/implementation/S1-rq1-harness.md` and `experiments/rq1-provenance/smoke-2026-10-19/blocks-1-3.txt`.
- Not started: RQ1 pre-registration filing, the pilot, the real kernel (M1), the observer UI.

## Next step

Credit is not the limit (auto top-up at $5 adds $20; a four-arm block with judges costs about $13). Run one job at a time
and set `--max-cost` above villages plus judges: a second job beside a block caused HTTP 429s that killed a block, and the
pinned DeepSeek endpoint throttles in bursts (`run_block.py` now retries for about 6 minutes). In this order:
(1) **The 2-block pilot (S2-T6)**: every arm A, B, Bc, C, D, E (rate from D's measured hearsay share, `matched_rate`), G, with
the review pass, two judges; then the numbers it sets: the margin for the true-fact guard, the number of main blocks, the
prompt-level arm for the contrast by the rule in ADR-0011, E's rate, probe temperature (0.7 placeholder). Run a block per
call; `run_block.py` takes `--arms A,B,Bc,C,D,E,G` (E is built by `chosen`). Then freeze `PREREGISTRATION.md` with those numbers
(OSF needs an account the owner has not made).
(2) A power/cost estimate from the pilot (S2-T3) and the notebook for `analyze_blocks.py`.
(3) Storage tickets T25 to T31. Live checks are fine, behind `Gateway`; never print the key. Open the PR yourself with the
template filled in; the owner reviews and merges.
Settled, do not reopen without new data: arm D stays as specified and G exploratory (ADR-0012); the rubric stays
`judge-fact-3` and every contrast is run under both judges; the review pass is in every arm and arm C changes only its
prompt (ADR-0013).

## Queue

Follow the sprint plan in `docs/sprints/`: S1 harness (weeks 1 to 4), S2 pilot and
pre-registration (5 to 8), S3 main run and report (9 to 16), S4 Rust kernel in parallel
(5 to 16). S5 to S8 are outlined and wait for RQ1. Ticket status is in `docs/implementation/`.

## Decisions (taken by Claude on the owner's delegation, 2026-10-19)

- Measures (ADR-0008): primary is the assertion rate of false facts, guard is true facts, carry rate says whether spread
  fell; rubric `judge-fact-3` counts attribution without doubt as an assertion; awareness is a funnel scored by
  `judge-awareness-2`; probe rounds each day. Run configuration (ADR-0009): Opus 5.5, GPT-5.6 Sol, DeepSeek V4 Pro each
  pinned to one provider, a day is 12 ticks. Citizens remember their own experience (ADR-0010). The prompt defense is a
  family (B strict, three wordings; Bc calibrated) chosen on the pilot by a written rule and frozen (ADR-0011). Arm G
  stays strict and exploratory (ADR-0007); the utility task needs no nudge (ADR-0006); license Apache-2.0.
- The earlier statement that "arm B still zeroes assertions" was wrong: it came from a rubric that coded attribution as
  a hedge, and the village before the memory fix also had citizens forgetting their own entries. On the corrected rubric
  and layout B gave 50% against 67% with no defense (one village). Keep this in mind before trusting any single number.
- Judge validity: two models agree at kappa 0.79 to 0.96; Opus 5.5 as stand-in human (112 answers, block 1) agrees at
  0.90 to 0.92 on facts; Claude's own blind coding earlier gave 0.73 and 0.79. No person has coded anything. The weak
  spot is answers that distance themselves from a value without doubting it (`asserts` or `hedges`), on which the judges
  and Opus split; no rewording fixed it (audit, 2026-10-20).
- Awareness by arm did not replicate (village 5: D 4 of 8 against A 0; blocks 1 to 3: D 6, 2, 4 against A 3, 3, 4).
  The pre-registration stays a draft until the pilot and the OSF filing.
- Villages are noisy: arm A's assertion rate was 71%, 36%, 36% and 67% in four earlier villages and 19%, 50%, 50% in
  the three blocks; D's was 79%, 55%, 45%. Three blocks cannot give p below 0.25. The pilot's between-block variance sets
  the number of blocks.

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
  backend in `Retrying` (2 to 30 s backoff, attempts logged); `Gateway` caps spend and calls and has a kill file (S2-T5). Haiku 5.5 reasons by default and
  returns empty content at small `max_tokens`: use `OpenRouterBackend(..., reasoning={model: {"enabled": False}})`
  per model; Opus 5.5 and `openai/gpt-oss-20b` cannot disable it (HTTP 400), so give them a larger `max_tokens`. Not verified: the cost per citizen-day,
  frontier-model behavior. Put every live call behind `Gateway` and check `/credits` first (the account, not only the key, can run dry). Unpinned providers drift: pin each model with `only`.
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
- A review pass (ADR-0013) is a driver action between ticks: a `consolidation` marker, then per citizen a `model_call`, the `claim`
  events of its notes and a `review` event (`through` = log position read up to). Audit replay re-executes it with the arm's review
  prompt; its notes go through the arm's policy, so a note citing only told events is hearsay under the kernel.
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
