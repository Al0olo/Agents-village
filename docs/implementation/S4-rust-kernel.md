# S4 — Rust kernel (M1) (implementation audit)

**Source of intent:** [`docs/sprints/S4-rust-kernel.md`](../sprints/S4-rust-kernel.md)  
**Status:** ⏳ Not started.

Nothing from this sprint is on `main` yet. When work starts, replace this note with the ticket status table below and the reproduction steps.

## Ticket status

Legend: ✅ done · 🟡 partial · 🚧 in progress or blocked · ⏸ deferred · ⏳ not started

| # | Title | Status | Notes |
| --- | --- | --- | --- |
| T1 | Kernel skeleton: citizen actors, mailbox, scheduler | ⏳ | |
| T2 | Postgres event log, append-only, with migrations | ⏳ | |
| T3 | Sleep and wake: wake on message, timer or event; sleeping holds no model call | ⏳ | |
| T4 | Replay command that rebuilds citizen state from the log | ⏳ | |
| T5 | Loop watchdog | ⏳ | |
| T6 | Model router behind a `Model` trait with per-citizen budgets and timeouts | ⏳ | |
| T7 | Ledger persistence and kernel-enforced spend caps | ⏳ | |
| T8 | Checkpoint every model call and tool call so a crash resumes without repaying tokens | ⏳ | |
| T9 | Observer CLI: live event stream and cost per citizen | ⏳ | |
| T10 | MAST failure tags on every trace | ⏳ | |
| T11 | Progress file and task list pattern for long runs | ⏳ | |
| T12 | Port admission policy; shared test vectors read by Rust and Python | ⏳ | |
| T13 | 72-hour, 10-citizen run; measure cost per citizen-day | ⏳ | |
| T14 | Stack decision memo | ⏳ | |
