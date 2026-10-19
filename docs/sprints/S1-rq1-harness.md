# S1 — RQ1 harness

**Weeks:** 1–4  
**Team:** 1 owner + agents (Python)  
**Total points:** ~133  
**Exit criterion:** A Python village can run to the planting event, fork into five arms, and record everything needed to replay and analyze it, using fake and recorded model backends.

## Goal

Build the instrument for RQ1 in plain Python, before the Rust kernel exists: forkable village state, structured claim writes with origin tracking, the five arms, planted facts, probes and metrics.

## In scope

- Append-only event log and deterministic scheduler with injected clock and randomness
- Model interface with fake, recorded and live (OpenRouter) backends; snapshot id and routed provider logged
- Citizen loop, memory tiers, structured claim writes (claim, kind, cited event ids), message forwarding with origin tracking
- Arms A to E: no defense, anchoring plus scrutiny, hedge-preserving consolidation, kernel admission, volume-matched random block
- Fork at the planting event; audit and counterfactual replay from recorded outputs; simultaneous launch
- Fictional fact generator, planting event, colluding-planter arm, neutral probes, awareness probe, utility task
- Blinded judge pipeline and the metrics in `docs/prd.md` section 1

## Out of scope

- The Rust kernel (S4)
- Real-money or real-world reach of any kind
- The main run (S3)

## Tickets

Ticket ids are `S1-T<n>`. Branch names `S1/<area>/<slug>`; PRs say `Closes S1-T<n>`.

### Core simulation

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T1 | Append-only event log (JSONL, ids, hash chain) | 5 | S0 |
| T2 | Village state and deterministic scheduler (injected clock, rng) | 5 | T1 |
| T3 | Model interface: fake, recorded, live backends; log snapshot id and provider | 5 | T1 |
| T4 | Citizen loop: wake, perceive, act, write memory; versioned prompts | 8 | T2,T3 |
| T5 | Memory tiers with structured claim writes | 5 | T1 |
| T6 | Message passing with origin tracking through forwards | 5 | T1,T5 |
| T12 | Consolidation job (two per 3-day run) | 5 | T5 |

### Arms

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T7 | Arm D: wire `admission.py`; extend tests with forwards and collusion | 3 | T6 |
| T8 | Arm A: no defense baseline | 1 | T4 |
| T9 | Arm B: anchoring plus source-scrutiny prompts (versioned, paraphrased) | 3 | T4 |
| T10 | Arm C: hedge-preserving consolidation | 5 | T12 |
| T11 | Arm E: volume-matched random-block control | 3 | T7 |

### Fork and replay

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T13 | Snapshot and fork at the planting event; forks identical until arms diverge | 5 | T2,T6 |
| T14 | Audit and counterfactual replay from recorded outputs | 5 | T1,T3 |
| T15 | Simultaneous launch controller; fallbacks off | 3 | T13 |

### Facts, probes, judging

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T16 | Fictional fact generator (counterbalanced plausibility and planter status) | 3 | T4 |
| T17 | Planting event and colluding-planter arm | 3 | T16,T13 |
| T18 | Neutral probes and awareness probe | 3 | T4 |
| T19 | Utility task that needs true word-of-mouth information | 5 | T4 |
| T20 | Blinded judge pipeline and human-validation sample sheet | 5 | T18 |
| T21 | Metrics: attack rate, time to k adopters, wiki contamination, true-fact acceptance, utility, label creep | 5 | T20 |

### Storage and memory ([ADR-0001](../adr/0001-storage-and-memory.md))

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T25 | SQLite store (WAL, one file per village): schema for events, claims, tiers, ledger, commitments; additive migrations | 5 | T1 |
| T26 | Hash-chain verification and Ed25519 signatures on messages and payments | 5 | T1 |
| T27 | Content-addressed blob store for notes and genome files | 3 | T25 |
| T28 | Retrieval: FTS5 plus sqlite-vec, pinned embedding model, results logged as events | 5 | T25,T3 |
| T29 | Projection rebuild from the log; property test that replay equals live state | 5 | T25,T14 |
| T30 | Bi-temporal claims (event time and record time) | 3 | T5,T25 |
| T31 | Single writer per village, serialized through the village actor | 2 | T25 |
| T32 | Arm F (exploratory): Mem0 OSS adapter, pinned version and models, its memory writes mirrored as events | 5 | T4,T25 |
| T33 | Arm G (exploratory): kernel admission with a corroborated shared tier | 2 | T7 |

### Quality

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T22 | Property tests: origin laundering, fork identity, log replay | 5 | T7,T13,T14 |
| T23 | Cost and usage accounting (tokens, citizen-day) | 3 | T3 |
| T24 | Harness CI: coverage report, type check | 2 | S0 |

## Definition of done

- Fake-backend village runs 3 simulated days end to end
- A village forks into five arms that are state-identical before divergence (tested)
- Replaying a recorded log reproduces the same events (audit replay)
- Admission policy tests cover forwarded-origin laundering and cross-citizen citations
- All metrics compute on a recorded sample
- Projections rebuilt from the log equal the live projections; hash chain verifies; retrieval results are replayed from the log
- `ruff` and `pytest` green; handoff updated

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Fork identity breaks through hidden state | Single state object; property test compares serialized state of forks. |
| Fake backend hides real-model behavior | S2 pilot uses live models; recorded outputs are captured from the pilot for later replay. |
| Prompt arms leak the hypothesis | Awareness probe and paraphrase control are in scope (T18); prompts are versioned. |
| Scope creep into a full simulator | Only what RQ1 measures. Anything else goes to S4 or later. |

## Demo

1. Run a fake-backend village, plant a fact, fork into five arms, print the five attack rates.

## Go/no-go

- Fork identity and replay tests pass. Owner reviews the arm prompts.

State of this sprint on `main`: [implementation audit](../implementation/S1-rq1-harness.md).
