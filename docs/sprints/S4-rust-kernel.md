# S4 — Rust kernel (M1)

**Weeks:** 5–16 (parallel to S2 and S3)  
**Team:** 1 owner + agents (Rust)  
**Total points:** ~110  
**Exit criterion:** Ten citizens run for 72 hours on top models, survive crashes, and leave a log that supports audit replay and counterfactual branching; cost per citizen-day is measured.

## Goal

Build the production kernel in parallel with the RQ1 experiment, without letting it block the experiment.

## In scope

- Citizen actors, mailboxes, scheduler, sleep and wake
- Postgres event log as the single source of truth; replay command; loop watchdog
- Model router with budgets; ledger persistence
- Observer CLI; MAST failure tags on every trace
- Stack decision memo (Ractor or Kameo, Rust friction)
- Admission port with shared test vectors, only after RQ1 semantics are final

## Out of scope

- Gateway to the real world (S8)
- Observer web UI (S5)

## Tickets

Ticket ids are `S4-T<n>`. Branch names `S4/<area>/<slug>`; PRs say `Closes S4-T<n>`.

### Kernel

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T1 | Kernel skeleton: citizen actors, mailbox, scheduler | 8 | S0 |
| T2 | Postgres event log, append-only, with migrations | 8 | T1 |
| T3 | Sleep and wake: wake on message, timer or event; sleeping holds no model call | 5 | T1 |
| T4 | Replay command that rebuilds citizen state from the log | 8 | T2 |
| T5 | Loop watchdog | 3 | T1 |

### Money and models

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T6 | Model router behind a `Model` trait with per-citizen budgets and timeouts | 8 | T1 |
| T7 | Ledger persistence and kernel-enforced spend caps | 5 | T2, existing ledger |
| T8 | Checkpoint every model call and tool call so a crash resumes without repaying tokens | 8 | T2,T6 |

### Storage and memory ([ADR-0001](../adr/0001-storage-and-memory.md))

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T15 | Postgres schema mirroring the SQLite one: events, claims, tiers, ledger, commitments; additive migrations | 5 | T2 |
| T16 | tsvector and pgvector retrieval with results recorded as events | 5 | T15 |
| T17 | Projection snapshots and fork-by-prefix | 5 | T4,T15 |
| T18 | Schema parity test: the same log yields identical projections in SQLite and Postgres | 5 | S1 T29, T15 |

### Infrastructure as code ([ADR-0002](../adr/0002-infrastructure-as-code.md))

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T19 | RDS Postgres 16 and networking in `infra/` | 5 | S2 T13 |
| T20 | Kernel container image and service deployment | 3 | T1,T19 |
| T21 | Observability: tracing and metrics export to CloudWatch or OTel | 3 | T20 |

### Observability and analysis

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T9 | Observer CLI: live event stream and cost per citizen | 5 | T2 |
| T10 | MAST failure tags on every trace | 3 | T2 |
| T11 | Progress file and task list pattern for long runs | 3 | T1 |

### Port and verify

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T12 | Port admission policy; shared test vectors read by Rust and Python | 5 | S1 T7, S3 done |
| T13 | 72-hour, 10-citizen run; measure cost per citizen-day | 8 | T1–T8 |
| T14 | Stack decision memo | 2 | T13 |

## Definition of done

- 10 citizens run 72 hours, survive injected crashes, resume without repaying tokens
- Replay of the log rebuilds identical state
- Ledger conserves its total across the run
- Cost per citizen-day measured and recorded
- Rust gate (`fmt`, `clippy -D warnings`, `test`) green

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Rust slows iteration | Time-box: if the stack hurts, record it in the memo and reconsider; the experiment does not depend on this sprint. |
| Kernel diverges from the Python reference | Shared test vectors (T12); port only after semantics are frozen. |
| Prerelease dependencies in the critical path | Own event log provides durability; avoid prerelease durable-execution SDKs. |

## Demo

1. Kill a citizen process mid-run; show the village resume from the log with no repaid tokens and an identical replay.

## Go/no-go

- Owner reads the stack memo and decides whether the kernel continues in Rust.

State of this sprint on `main`: [implementation audit](../implementation/S4-rust-kernel.md).
