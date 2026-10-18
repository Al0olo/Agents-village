# Handoff log

Newest first. One entry per session. State lives in [`../HANDOFF.md`](../HANDOFF.md);
this file is history, so a future agent can see how decisions were reached.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T15 launch controller

- PR #18 (echo gap, ADR-0003) was merged. T15 is the in-process controller; the cloud batch runner is S2-T15 and the run monitor S3-T3, so I kept this to launch, lockstep and a minimal abort rule.
- Design: `launch.launch` forks every arm from one snapshot, all or nothing (files are removed on any failure), with one `RunConfig` and a backend from one zero-argument factory, so an arm cannot be given different settings. A `launch` event in each log records arm, snapshot head, config hash and prompt version and hash, which also closes the earlier gap that `max_awake` and `LoopConfig` were not logged. `Launch.run` advances all arms one tick at a time behind a barrier, concurrently on threads, or one after another on a single worker; both go through the same code and give identical logs. Any arm failing, or drift, marks the block dead.
- Drift is defined without assuming how OpenRouter names things: a requested model that served more than one (served model, provider) pair across all calls in all arms, base run included. It aborts by default and can be tolerated and reported. The scan is incremental.
- Tests first: 24, including a threading barrier that only passes if arms really run concurrently (and a negative control that breaks in sequential mode), lockstep ordering, thread/sequential equality, arm-order independence, all-or-nothing launch, failure propagation, drift from a changed snapshot, a provider switch, drift since the base run, tolerated drift, per-model checking, and an arm with its own prompt. Mutation-checked 20 mutants; every real one is caught. Two survivors are equivalent (`wait` is redundant with `f.exception()`; a scan offset that skips only a `tick` event).
- Mistakes caught on re-read: three mutants I wrote referenced undefined names and failed for the wrong reason, so I redid them; a test compared an event id with a hash; several drift tests assumed a call at an exact tick and now compute the tick from the log.
- Not verified: behavior against the real OpenRouter (stable served ids, provider names).

## 2026-10-18 · Claude Sonnet 5.5 · closing the base-policy decision and the echo gap

- PR #17 (T7, T8) was merged. The owner asked to close the two items I had raised before starting T15. I took my own recommendation for the decision and changed the policy for the gap, since no pre-registration exists and no run has started; both are recorded so they can be revisited before S2-T1 freezes the design.
- Gap: `admit` now ignores a told event whose origins include the writer. Via `Messenger` the case was unreachable, but the policy should not depend on that. Tests first (two failed before the change), then the rule in `admission.py`, and the statement of the rule updated in the module docstring, `README.md`, `docs/prd.md`, the `village-memory` doc comment and the kernel-invariants skill. The Rust gate (fmt, clippy, test) was run because a crate comment changed. One mutant survives and is equivalent (`admit` already filters cited events to the writer's own).
- Decision: ADR-0003, the shared base village runs without defense until the fork. `arms.BASE` is arm A. The arms tests now build the base that way, check the kernel only on writes after the fork, and assert that the base's unbacked entries exist and that arm D never reclassifies them. The pre-registration is to report, per block, the share of core and shared entries at the fork that the kernel's rule would have refused.
- Rewrote `docs/HANDOFF.md` as current state: it had grown past the length limit and kept gotchas that were no longer true (Village refusing a non-empty log, T7 being smaller than planned).

## 2026-10-18 · Claude Sonnet 5.5 · S1-T7 and S1-T8 arms D and A

- PR #16 (T13) was merged. Added `arms.py`: an arm is a memory policy plus a prompt; arm D is `admission.admit`, arm A is `admit_all`; both use the baseline prompt so the policy is the only difference. `admission.py` is untouched.
- Beyond the ticket text: 12 policy-level cases in `test_admission.py` (duplicate citations, chain overlap, partial overlap, empty origins, other citizens' events, unknown ids, colluders, order independence, purity) and a village-level test. A gossiping 8-citizen village (forwards, cited claims, environment observations) runs 24 ticks, is snapshotted, forks into A and D, and runs 48 more. Two independent oracles check the result from the log alone: every logged admission decision, and every message's origins against its forward chain. No hearsay reaches core or shared memory under D; A stores every claim as fact; D keeps less in shared memory; hearsay is kept in recall, not dropped.
- Mutation-checked 11 mutants across `admission.py`, `messages.py` and `arms.py` (inverted disjointness, dropped writer filter, empty origins counted, `did` dropped, `told` counted as evidence, always-fact, forwarder not added, origin-return allowed, wrong arm policies and prompt); all are caught.
- Raised for the owner: the base-run policy before the planting event is a design choice for the pre-registration. Noted a gap in the policy that `Messenger` closes but `admit` does not (a told event whose origins include the writer); recorded for the Rust port instead of changing the treatment.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T13 snapshot and fork

- PR #15 (T4) was merged. Inventoried all mutable state: `Village` (citizens, awake, pending, clock, rng), `Runner` (cursors, a queued set that is empty between ticks), `Memory` (a fold of the log). Everything except the rng state is derivable from the log, so a snapshot is the log position, its head and the rng state.
- Design: `Village.__init__` now folds an existing log, and every mutator appends then applies through the same `_apply`, so live and rebuilt state agree by construction. `Runner` resumes over a non-empty log and rebuilds cursors from `step` events. `EventLog.fork` copies a prefix byte for byte (refuses to overwrite). `fork.fork` verifies the head, copies the prefix, restores the rng and rebuilds with the arm's policy, prompt and backend. A failed fork deletes its destination.
- Tests (70 new): fork at ticks 0, 1, 5, 17, 40 over several seeds; start state equals base; the fork continues exactly like a base that never forked; two forks of one arm stay identical; arms share the prefix byte for byte and diverge only afterwards, at a `step` event when the prompt differs; independence of files; a wrong rng state makes forks diverge (the hidden-state risk is real); refusal of foreign, short, tampered or colliding inputs; a fork replays recorded outputs to the base's head.
- Mutation-checked: dropping the rng restore, head check, mid-tick check, cursor restore, citizen check, prefix length, no-overwrite, pending cleanup, clock restore and snapshot field validation each fail tests. Survivors that were real: a dead length check in `fork` (removed) and untested snapshot validation, which coverage exposed as unreachable because my bad cases used an invalid rng state (fixed).
- Mistake of mine: the S1-T4 PR committed `harness/.coverage` through `git add -A`. Untracked and ignored here.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T4 citizen loop

- PR #14 (T6) was merged. Owner asked for T4 with everything tested. Designed from the PRD (FR2 loop, step budget from MAST, no hypothesis leakage) and the existing modules; split into `actions.py` (strict parser), `prompts.py` (versioned, hashed) and `runner.py` (the loop) so each is tested alone.
- Decisions: one JSON action per model reply with four actions (`say`, `forward`, `remember`, `sleep`); invalid replies and failed actions are logged and shown to the citizen as a neutral notice, and burn a step; a write's admission result is never shown; every turn ends asleep (voluntary or by budget); sleep length is clamped; messages wake the recipient unless they still act this tick. Acting logs `message` and `claim` events, never `did`, so a citizen cannot cite its own utterance as evidence. Model errors stop the run.
- Found while re-reading my tests: a wake request to a recipient who has not yet acted this tick cost a pointless model call next tick; fixed with a queued set and a seed-swept test for both orders. Also found a flawed test that depended on turn order within a tick.
- Verified: 221 tests, 100% line and branch coverage (pytest-cov installed ad hoc), and hand mutation of 17 behaviors in the runner and parser; every real mutant is caught (a comment-only mutant is equivalent). One survivor (core and wiki limits untested) led to a new test. The T1 coverage gap (unreadable records in the event log) got a test too.
- Not verified: behavior with a real model; whether the baseline prompt reads naturally to frontier models; any live call.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T6 message passing

- PR #13 (T5) was merged. Owner asked about T4 versus T6; T4 was unblocked (depends on T2 and T3) but I recommended T6 first so the loop's perception is designed once around real messages; the owner agreed.
- Implemented `messages.py`. A first-hand send has the sender as its only origin; a forward copies the text and adds the forwarder to the received origins. Origins are the kernel's tracked forwards only: a citizen who retypes hearsay in their own words becomes a new origin, and two colluding liars count as independent sources. Both are limits of the mechanism as the PRD specifies it, and the colluding-planter arm (T17) exists to measure them.
- Added a rule not in the ticket: a message cannot go to one of its own origins. Without it, a citizen could message themselves and pair that echo with one real teller to reach two disjoint origins.
- Tests first, 19 cases, including end-to-end checks through `Memory` and `admit`. Mutation-checked: forwards not adding the forwarder, forwards resetting origins, dropping the origin-return rule, letting a citizen forward someone else's `told` event, `received` ignoring the recipient and accepting negative ids each fail tests.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T5 memory tiers

- PR #12 (T3) was merged. Implemented `memory.py` from PRD section 1 (the mechanism) and section 8 (tiers): structured claim writes with an injected admission policy, so arms can swap the policy later and `admission.admit` is arm D.
- Choices: the declared kind is stored (the label-creep metric needs it) but never used for the decision; a rejected write lands in the writer's recall as hearsay with no error; core and recall are private, shared is global; the decision is logged and the projection rebuilds from the log without calling the policy. Only `saw`, `did` and `told` events are evidence, so a claim, a model call or any other kind cannot launder itself into fact.
- Left out on purpose: the archival tier (no behavior to test before T27 and T28), tool-receipt and ledger evidence, consolidation (T12), bi-temporal fields (T30).
- Tests first, 21 cases. Mutation-checked: storing hearsay in the requested tier, letting claims count as evidence, leaking private tiers, dropping told origins and rebuilding with a hard-coded decision each fail tests.

## 2026-10-18 · Claude Sonnet 5.5 · S1-T3 model interface

- PR #11 (T2) was merged. Owner asked me to open PRs myself from now on; they review and merge.
- Read OpenRouter's docs (provider routing, API overview, get a generation): fallbacks are `provider.allow_fallbacks` (default true), restriction is `provider.only`, the served model is `response.model`. The routed provider is documented only as `data.provider_name` on `GET /generation?id=`; the chat response schema shows no `provider` field. The backend uses a `provider` field if present, else the generation record, else raises.
- Implemented `model.py` (request validation incl. `max_tokens >= 1`, fake, logging `Model`, `RecordedBackend`) and `openrouter.py` (injected transport, stdlib `urllib` transport). `canonical_hash` moved into `eventlog.py` so request and event hashes share one canonical form; the pinned event hash is unchanged.
- Tests first, 26 cases, including audit replay (replaying recorded outputs gives an identical log head). Mutation-checked: fallbacks on, silent "unknown" provider, non-consuming replay, request model logged as served, and `max_tokens` bound each fail tests.
- Not verified: any real OpenRouter call. Not done: spend cap and kill switch (S2-T5), usage accounting (T23).

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
