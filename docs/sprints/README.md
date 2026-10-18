# Sprint plan

Derived from [`docs/milestones.md`](../milestones.md) and section 1 of [`docs/prd.md`](../prd.md). Research comes first: RQ1 runs on a Python harness (S1 to S3) while the Rust kernel (S4) is built in parallel. Each sprint file is self-contained:

- **Goal** and **exit criterion**
- **Scope** (in and out)
- **Tickets** with points and dependencies
- **Definition of done**, **risks**, **demo**, **go/no-go**

This folder holds *intent*. What is actually on `main` is tracked in [`../implementation/`](../implementation/README.md).

## Sprints

| ID | Sprint | Weeks | Sizing | Exit criterion |
| --- | --- | --- | --- | --- |
| S0 | [Repository foundations](./S0-foundations.md) | 0 (done) | 1 owner + agents | Monorepo on `main` with CI green, docs, agent rules and a working handoff system. |
| S1 | [RQ1 harness](./S1-rq1-harness.md) | 1–4 | 1 owner + agents (Python) | A Python village can run to the planting event, fork into five arms, and record everything needed to replay and analyze it, using fake and recorded model backends. |
| S2 | [RQ1 pilot and pre-registration](./S2-rq1-pilot.md) | 5–8 | 1 owner + agents | A pre-registration the owner has approved and a 2-block pilot that fixes the block count, the cost, and the coding reliability. |
| S3 | [RQ1 main run and report](./S3-rq1-main.md) | 9–16 | 1 owner + agents + 1 human coder | A complete, honest write-up of RQ1 with released code and logs, whichever way the result goes. |
| S4 | [Rust kernel (M1)](./S4-rust-kernel.md) | 5–16 (parallel to S2 and S3) | 1 owner + agents (Rust) | Ten citizens run for 72 hours on top models, survive crashes, and leave a log that supports audit replay and counterfactual branching; cost per citizen-day is measured. |
| S5 to S8 | [After RQ1](./post-rq1.md) | after S3 | evolving | Village, economy, spawn, open world; RQ2 and RQ3 |

> **Why research first?** The framework is not novel on its own; a controlled result is. RQ1 does not need the Rust kernel, so S1 to S3 run on Python and the kernel (S4) proceeds in parallel without blocking it.

## Working conventions

- **Point scale:** 1 (up to 2h), 2 (half a day), 3 (1 day), 5 (2 to 3 days), 8 (about a week). Anything above 8 is split.
- **Labels:** `area:harness`, `area:kernel`, `area:experiment`, `area:research`, `area:safety`, `area:ui`, `area:infra`, `area:docs`.
- **Branch naming:** `S<n>/<area>/<slug>`, for example `S1/harness/event-log`. Work outside a ticket uses `chore/`, `docs/` or `fix/`.
- **PR rules:** one ticket per PR where feasible, linked with `Closes S1-T4`; CI must pass; update `docs/HANDOFF.md` and the sprint's implementation audit in the same PR.
- **Definition of Ready:** acceptance criteria written, design or pre-registration section linked, test plan stated.
- **Definition of Done:** tests added, docs updated, handoff updated, and for experiment tickets the pre-registration unchanged or amended with a date.
- **Research gates:** an experiment sprint is not done until its result is written up, positive or negative. No run starts before its pre-registration is approved.
- **Precedence:** if a ticket conflicts with the pre-registration, the pre-registration wins; raise the conflict, do not paper over it.
- **Status vocabulary** (used in the implementation audits): ✅ done, 🟡 partial, 🚧 in progress or blocked, ⏸ deferred, ⏳ not started.
