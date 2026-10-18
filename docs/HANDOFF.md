# Handoff

Updated: 2026-10-18 by Claude Sonnet 5.5 · Branch: `claude/gracious-albattani-osio94` · Base: `main` at `412b24e`

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
- Done: S1-T2, village state and deterministic scheduler (`harness/src/agent_village/village.py`, 20 tests): injected `SimClock` and `random.Random`, awake cap, oldest wake request first with seeded tie-break, every change a log event. Merged in PR #11.
- Done: S1-T3, model interface (`model.py`: `Request`, `Response`, `FakeBackend`, `Model`, `RecordedBackend`; `openrouter.py`: live backend, fallbacks always off, 26 tests). `Model` logs `model_call` events with requested and served model and routed provider; `RecordedBackend.from_log` replays them. Merged in PR #12.
- Done: S1-T5, memory tiers with structured claim writes (`harness/src/agent_village/memory.py`, 21 tests): `Memory(log, policy).write_claim(writer, text, kind, cites, tier)`, tiers core, recall and shared, decision logged as a `claim` event, state rebuilds from the log without rerunning the policy. Merged in PR #13.
- Done: S1-T6, message passing with origin tracking (`harness/src/agent_village/messages.py`, 19 tests): `Messenger.send/forward/received`; a send logs a `message` event and the recipient's `told` event; forwards add the forwarder to the origins and never remove one; a message cannot go to its own origins. Tested end to end with `Memory` and `admit`. Merged in PR #14.
- Done: S1-T4, the citizen loop (`runner.py`, `actions.py`, `prompts.py`; 114 new tests, 221 in all, 100% line and branch coverage measured with pytest-cov, which is not a project dependency yet). Each wake is a turn of at most `max_steps` model calls; a reply parses to `say`, `forward`, `remember` or `sleep`; the step budget, clamped sleeps, logged `invalid_action` and `turn_end` events bound every loop. A fake-backend village of 8 citizens runs 72 ticks end to end and replays from recorded outputs to an identical log head. Merged in PR #15.
- Done: S1-T13, snapshot and fork (`fork.py`; `EventLog.fork` and `head_at`; `Village` and `Runner` now rebuild from an existing log). A `Snapshot` is the log position, its head and the rng state, taken between ticks; `fork(snapshot, source, dest, backend, policy, prompt, specs, max_awake)` copies the verified log prefix and rebuilds the world with the arm's own policy, prompt and backend. 291 tests, 100% line and branch coverage. PR open on branch `claude/gracious-albattani-osio94`.
- Decided: IaC is OpenTofu on AWS in `infra/`; the owner delegated the choice. Memory is a projection of an event log we own; SQLite in the harness, Postgres in the kernel, same schema, forks by log prefix (`docs/adr/0001-storage-and-memory.md`).
- Decided: observer UI is TypeScript with Next.js (App Router) in `apps/observer/`, pnpm. Not scaffolded yet; add the CI job when it is.
- Not started: RQ1 pre-registration, the 2-block pilot, the paired-fork village runner,
  the real kernel (M1), the observer UI.

## Next step

Once the S1-T13 PR is merged, restart the branch from `main` and take S1-T7 and S1-T8 as
one small arms module (`arms.py`): a named arm is a memory policy plus a prompt. Arm D is
`admission.admit` with the baseline prompt (its forward and collusion tests exist in
`test_messages.py`); arm A admits everything with the same prompt. Keep them separate
commits or PRs if the owner prefers one ticket per PR. Then S1-T15 (simultaneous launch
controller using `fork.fork`, fallbacks off), T14 (audit and counterfactual replay), T9,
T16, T18 and the storage tickets T25 to T31. The pre-registration is S2-T1; do not run
anything live before it is approved. Open the PR yourself with the template filled in; the
owner reviews and merges.

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

- OpenRouter: only the request side (`provider.allow_fallbacks`, `provider.only`) and the generation record (`data.provider_name`) are documented. Whether the chat response carries a `provider` field, and how soon the generation record is readable after a call, are NOT verified; the backend tolerates both and fails if neither names the provider. Check on the first live call in S2.
- The live backend has no spend cap or kill switch. Do not call it outside S2-T5's gateway.

- Evidence convention (S1-T5): `saw` and `did` events are written by the citizen; `told` events are written by the recipient with `origins` in the payload. Tool receipts and ledger entries are not evidence yet; add their kinds with a forgery test when those tickets land.
- Archival memory is not implemented (T27, T28); the PRD's four tiers are three here until then.

- `Messenger` does not know who the citizens are and does not wake the recipient; the T4 loop and `Village` own both.
- The colluding-senders test in `tests/test_messages.py` documents a known limit of kernel admission, not a bug: two distinct liars are two origins. The colluding-planter arm (T17) measures it.
- S1-T7 is smaller than planned: forward and collusion tests already exist in `test_messages.py`. What remains is making `admit` selectable as an arm policy.

- Acting is not evidence (S1-T4): the loop logs `message` and `claim` events but never `did` events for what a citizen says or writes. A `did` for `say` would let a citizen cite its own utterance as first-hand evidence for what it said, which defeats arm D. First-hand events must come from the environment (planting, tool receipts, ledger).
- Defaults in `LoopConfig` (4 steps, sleep 6 of at most 24 ticks, 400 tokens, temperature 0.7, 20 memory lines per tier) and the text of `BASELINE` are placeholders. The owner reviews arm prompts at the S1 gate; the pre-registration freezes them.
- A model error propagates out of `Runner.tick()` and leaves every woken citizen awake. That run is dead by design (exclusion rules cover crashed villages); there is no retry.
- A message to a citizen who has not yet acted this tick does not wake them again; they see it on their turn. Tested for both orders.
- Message and memory text is flattened to one line when rendered, so a message cannot forge an event line such as `[999] You saw: ...`. Evidence is by log id, so forging a line never fools the kernel, only the model.
- `python3 -m pytest` is needed for coverage flags in this sandbox; plain `pytest` ignores the pytest-cov plugin.

- `Village` no longer refuses a non-empty log: it rebuilds from it and sets the clock to the last tick. Every mutator appends an event and applies it through `_apply`, the same method the rebuild uses, so live and rebuilt state cannot drift. The 'projection rebuild' part of S1-T29 for the village, runner cursors and memory is therefore done; T29 still owns SQLite projections and the replay-equals-live property test over all projections.
- Snapshots are valid only between ticks; `World.snapshot()` raises while any citizen is awake. The planting event (T17) must be appended between ticks, and the snapshot taken after it.
- `RecordedBackend.from_log` replays every `model_call` in a log, including those before a fork. Prompts embed the tick, so identical requests across ticks do not occur today, but T14 should replay only calls after the fork point. Arms with a recorded backend need one `RecordedBackend` per fork: it is consumed as it replays.
- Arms must be built by passing a different policy, prompt or backend to `fork.fork`. `max_awake` and `LoopConfig` are not logged; every arm must be given the same values, and the run layer should record them with the config hash.
- Coverage: `python3 -m pytest --cov=agent_village --cov-branch` works if `pytest-cov` is installed (it is not a project dependency until T24). `.coverage` is now git-ignored; it was committed by mistake in the S1-T4 PR and removed here.

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
