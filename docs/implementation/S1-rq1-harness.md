# S1 — RQ1 harness (implementation audit)

**Source of intent:** [`docs/sprints/S1-rq1-harness.md`](../sprints/S1-rq1-harness.md)  
**Status:** ⏳ Not started.

Nothing from this sprint is on `main` yet. When work starts, replace this note with the ticket status table below and the reproduction steps.

## Ticket status

Legend: ✅ done · 🟡 partial · 🚧 in progress or blocked · ⏸ deferred · ⏳ not started

| # | Title | Status | Notes |
| --- | --- | --- | --- |
| T1 | Append-only event log (JSONL, ids, hash chain) | ⏳ | |
| T2 | Village state and deterministic scheduler (injected clock, rng) | ⏳ | |
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
