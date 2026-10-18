# S1 — RQ1 harness (implementation audit)

**Source of intent:** [`docs/sprints/S1-rq1-harness.md`](../sprints/S1-rq1-harness.md)  
**Status:** 🚧 In progress. T1 and T2 done.

```bash
cd harness && pip install -e ".[dev]" && ruff check . && pytest -q
```

## Ticket status

Legend: ✅ done · 🟡 partial · 🚧 in progress or blocked · ⏸ deferred · ⏳ not started

| # | Title | Status | Notes |
| --- | --- | --- | --- |
| T1 | Append-only event log (JSONL, ids, hash chain) | ✅ | `harness/src/agent_village/eventlog.py`, `harness/tests/test_eventlog.py`. Chain verification on open is included, so T26 covers signatures only. `pytest -q tests/test_eventlog.py` |
| T2 | Village state and deterministic scheduler (injected clock, rng) | ✅ | `harness/src/agent_village/village.py`, `harness/tests/test_village.py`. Awake cap, oldest request first, seeded tie-break; every change is a log event. Rebuilding a village from an existing log is T29. `pytest -q tests/test_village.py` |
| T3 | Model interface: fake, recorded, live backends; log snapshot id and provider | ⏳ | |
| T4 | Citizen loop: wake, perceive, act, write memory; versioned prompts | ⏳ | |
| T5 | Memory tiers with structured claim writes | ⏳ | |
| T6 | Message passing with origin tracking through forwards | ⏳ | |
| T7 | Arm D: wire `admission.py`; extend tests with forwards and collusion | ⏳ | |
| T8 | Arm A: no defense baseline | ⏳ | |
| T9 | Arm B: anchoring plus source-scrutiny prompts (versioned, paraphrased) | ⏳ | |
| T10 | Arm C: hedge-preserving consolidation | ⏳ | |
| T11 | Arm E: volume-matched random-block control | ⏳ | |
| T12 | Consolidation job (two per 3-day run) | ⏳ | |
| T13 | Snapshot and fork at the planting event; forks identical until arms diverge | ⏳ | |
| T14 | Audit and counterfactual replay from recorded outputs | ⏳ | |
| T15 | Simultaneous launch controller; fallbacks off | ⏳ | |
| T16 | Fictional fact generator (counterbalanced plausibility and planter status) | ⏳ | |
| T17 | Planting event and colluding-planter arm | ⏳ | |
| T18 | Neutral probes and awareness probe | ⏳ | |
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
