# S1 — RQ1 harness (implementation audit)

**Source of intent:** [`docs/sprints/S1-rq1-harness.md`](../sprints/S1-rq1-harness.md)  
**Status:** 🚧 In progress. T1 to T8 and T13 to T18 done.

```bash
cd harness && pip install -e ".[dev]" && ruff check . && pytest -q
```

## Ticket status

Legend: ✅ done · 🟡 partial · 🚧 in progress or blocked · ⏸ deferred · ⏳ not started

| # | Title | Status | Notes |
| --- | --- | --- | --- |
| T1 | Append-only event log (JSONL, ids, hash chain) | ✅ | `harness/src/agent_village/eventlog.py`, `harness/tests/test_eventlog.py`. Chain verification on open is included, so T26 covers signatures only. `pytest -q tests/test_eventlog.py` |
| T2 | Village state and deterministic scheduler (injected clock, rng) | ✅ | `harness/src/agent_village/village.py`, `harness/tests/test_village.py`. Awake cap, oldest request first, seeded tie-break; every change is a log event. Rebuilding a village from an existing log is T29. `pytest -q tests/test_village.py` |
| T3 | Model interface: fake, recorded, live backends; log snapshot id and provider | ✅ | `harness/src/agent_village/model.py`, `openrouter.py`; tests `test_model.py`, `test_openrouter.py`. The live backend is tested against a fake transport and a local HTTP server; it has not called OpenRouter. Spend cap and kill switch are S2-T5. |
| T4 | Citizen loop: wake, perceive, act, write memory; versioned prompts | ✅ | `harness/src/agent_village/runner.py`, `actions.py`, `prompts.py`; tests `test_runner.py`, `test_actions.py`, `test_prompts.py`. A fake-backend village of 8 citizens runs 72 ticks, is deterministic per seed, respects the awake cap, calls the model only for awake citizens, and replays from recorded outputs to an identical log head. The baseline prompt is a placeholder until the owner reviews the arm prompts. `pytest -q tests/test_runner.py` |
| T5 | Memory tiers with structured claim writes | ✅ | `harness/src/agent_village/memory.py`, `harness/tests/test_memory.py`. Core, recall and shared tiers; archival waits for T27 and T28. The admission policy is injected; `admission.admit` is arm D, wired in T7. `pytest -q tests/test_memory.py` |
| T6 | Message passing with origin tracking through forwards | ✅ | `harness/src/agent_village/messages.py`, `harness/tests/test_messages.py`. `send`, `forward`, `received`; checked end to end through `Memory` and `admit` (forward laundering stays hearsay, colluding senders count as independent). Waking the recipient is not wired; that is T4. `pytest -q tests/test_messages.py` |
| T7 | Arm D: wire `admission.py`; extend tests with forwards and collusion | ✅ | `harness/src/agent_village/arms.py` (`KERNEL_ADMISSION`); tests `test_admission.py` (12 new policy cases), `test_arms.py`. After review one rule was added to `admission.py`: a told event that originates with the writer is not evidence. A gossiping 8-citizen village forked into arms A and D is checked against an independent recomputation of every logged decision and of every message's origins; no hearsay reaches core or shared memory under D. `pytest -q tests/test_arms.py tests/test_admission.py` |
| T8 | Arm A: no defense baseline | ✅ | `harness/src/agent_village/arms.py` (`NO_DEFENSE`, `admit_all`); same prompt as arm D, so the arms differ only in the memory policy. After the fork it stores every claim as fact where requested, and adds more to shared memory than D. `arms.BASE` (arm A) is the policy of the shared base village until the fork ([ADR-0003](../adr/0003-base-village-runs-without-defense.md)). `pytest -q tests/test_arms.py` |
| T9 | Arm B: anchoring plus source-scrutiny prompts (versioned, paraphrased) | ⏳ | |
| T10 | Arm C: hedge-preserving consolidation | ⏳ | |
| T11 | Arm E: volume-matched random-block control | ⏳ | |
| T12 | Consolidation job (two per 3-day run) | ⏳ | |
| T13 | Snapshot and fork at the planting event; forks identical until arms diverge | ✅ | `harness/src/agent_village/fork.py`, `eventlog.py` (`fork`, `head_at`), `village.py` and `runner.py` (rebuild from a log); tests `test_fork.py`, `test_village.py`, `test_eventlog.py`, `test_runner.py`. A snapshot is the log position, its head hash and the rng state, taken between ticks. A fork starts in exactly the base's state, continues exactly like a base that never forked, shares the log prefix byte for byte, and diverges only through the arm's policy, prompt or backend. The planting event itself is T17. `pytest -q tests/test_fork.py` |
| T14 | Audit and counterfactual replay from recorded outputs | ✅ | `harness/src/agent_village/replay.py`, `model.py` (`RecordedBackend.from_log(log, start)`); tests `test_replay.py`, `test_model.py`. `audit(original, dest, start, arm, config)` re-drives a recorded run from a seed or from the snapshot an arm was forked from, runs the real runner against recorded outputs, re-appends `saw`, `did` and `launch` events, and reports the first differing event. `branch(...)` replays to a tick boundary, then continues under a changed arm, reusing recorded outputs for identical requests and counting reused and fresh calls. A replayed log is byte-identical to the original. Only `saw`, `did` and `launch` events may be appended between ticks. `pytest -q tests/test_replay.py` |
| T15 | Simultaneous launch controller; fallbacks off | ✅ | `harness/src/agent_village/launch.py`, `harness/tests/test_launch.py`. `launch(snapshot, source, directory, arms, make_backend, config)` forks every arm all or nothing with one `RunConfig` and one backend factory, and appends a `launch` event (arm, snapshot head, config hash, prompt version and hash) to each log. `Launch.run` advances the arms one tick at a time behind a barrier, on threads or one after another with identical results. A failed arm or detected drift (a requested model that served more than one snapshot or provider, base run included) stops and excludes the block. Fallbacks are off in `OpenRouterBackend` (S1-T3). The cloud batch runner that calls this is S2-T15; the run monitor is S3-T3. `pytest -q tests/test_launch.py` |
| T16 | Fictional fact generator (counterbalanced plausibility and planter status) | ✅ | `harness/src/agent_village/facts.py`, `harness/tests/test_facts.py`. Ten facts per block, six false and four true, from ten templates; the design is counterbalanced within a block, over four blocks and over twenty. Names and values are invented and not checked against any real source; the owner reviews them before pre-registration. `pytest -q tests/test_facts.py` |
| T17 | Planting event and colluding-planter arm | ✅ | `harness/src/agent_village/planting.py`, `harness/tests/test_planting.py`. `announce` names the elders to everyone, `make_plan` picks holders by status (true facts two, false facts one, two when colluding), `plant` appends `plant` markers and first-hand `saw` events and returns the snapshot. Checked against the kernel: a true fact told by both holders is admitted, a single holder's false fact is hearsay, and two colluders get a false fact through. The design is [ADR-0004](../adr/0004-how-facts-are-planted-and-probed.md) (proposed). `pytest -q tests/test_planting.py` |
| T18 | Neutral probes and awareness probe | ✅ | `harness/src/agent_village/probes.py`, `Runner.ask` in `runner.py`, probe support in `replay.py`; tests `test_probes.py`. A round asks every citizen every question in an independent call under the arm's own prompt, records `probe` events, and changes nothing the citizen knows. Audit replay and branches reproduce rounds. Coding the answers is T20. `pytest -q tests/test_probes.py` |
| T19 | Utility task that needs true word-of-mouth information | ⏳ | |
| T20 | Blinded judge pipeline and human-validation sample sheet | ⏳ | |
| T21 | Metrics: attack rate, time to k adopters, wiki contamination, true-fact acceptance, utility, label creep | ⏳ | |
| T22 | Property tests: origin laundering, fork identity, log replay | ⏳ | |
| T23 | Cost and usage accounting (tokens, citizen-day) | ⏳ | |
| T24 | Harness CI: coverage report, type check | ⏳ | |
| T25 | SQLite store: schema, WAL, additive migrations | ⏳ | |
| T26 | Hash-chain verification and Ed25519 signatures | ⏳ | |
| T27 | Content-addressed blob store | ⏳ | |
| T28 | Retrieval: FTS5 plus sqlite-vec, results logged | ⏳ | |
| T29 | Projection rebuild; replay equals live state | ⏳ | |
| T30 | Bi-temporal claims | ⏳ | |
| T31 | Single writer per village | ⏳ | |
| T32 | Arm F (exploratory): Mem0 OSS adapter | ⏳ | |
