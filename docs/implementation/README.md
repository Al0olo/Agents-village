# Implementation notes

This folder records **what is actually on `main`**, ticket by ticket, per sprint.

The companion [`docs/sprints/`](../sprints/README.md) files define *intent* (goal, tickets, definition of done). These files record *state*: what works today, what is stubbed, what was deferred, and how to reproduce the green path locally.

Keep each file honest. A ticket marked ✅ must be verifiable with the commands below. A deferred ticket says why and links the blocker. Update the relevant audit in the same PR that changes the state, together with `docs/HANDOFF.md`.

## Sprint index

| Sprint | Status | Doc |
| --- | --- | --- |
| S0 — Foundations | ✅ Complete | [S0-foundations.md](./S0-foundations.md) |
| S1 — RQ1 harness | 🚧 T1 (event log), T2 (scheduler) and T3 (model interface) and T5 (memory tiers) done; `admission.py` from S0 | [S1-rq1-harness.md](./S1-rq1-harness.md) |
| S2 — RQ1 pilot and pre-registration | ⏳ Not started | [S2-rq1-pilot.md](./S2-rq1-pilot.md) |
| S3 — RQ1 main run and report | ⏳ Not started | [S3-rq1-main.md](./S3-rq1-main.md) |
| S4 — Rust kernel | ⏳ Not started; `village-ledger` has a tested in-memory ledger, the other crates are scaffolds | [S4-rust-kernel.md](./S4-rust-kernel.md) |
| S5 to S8 | ⏳ Not started; outline only | [post-rq1.md](../sprints/post-rq1.md) |

## Conventions

- ✅ **Done**: on `main`, verified by a test or a concrete reproduction step.
- 🟡 **Partial**: primary path works; the gap has a named ticket.
- 🚧 **In progress or blocked**: blocker recorded.
- ⏸ **Deferred**: not in this sprint; points to the sprint that will pick it up.
- ⏳ **Not started**.

## Reproduction baseline

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cd harness && ruff check . && pytest -q
scripts/check-handoff.sh
```

All must exit 0. This is the minimum bar for any change to merge.
