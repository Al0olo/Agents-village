# S0 — Repository foundations

**Weeks:** 0 (done)  
**Team:** 1 owner + agents  
**Total points:** ~25  
**Exit criterion:** Monorepo on `main` with CI green, docs, agent rules and a working handoff system.

## Goal

Make the repository something any agent or contributor can pick up: structure, docs, rules, CI and enforced handoff.

## In scope

- Rust workspace and Python harness scaffolds with tests
- PRD, milestones and research sources in `docs/`
- README, hero and social images
- README and AGENTS file per directory
- Agent rules, skills, hooks and the handoff system
- Sprint and task docs (this folder)

## Out of scope

- Any simulation or experiment code
- Observer UI

## Tickets

Ticket ids are `S0-T<n>`. Branch names `S0/<area>/<slug>`; PRs say `Closes S0-T<n>`.

### Foundations

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T1 | Monorepo scaffold: Rust workspace, Python harness, CI | 5 | — |
| T2 | PRD and milestones in `docs/` | 3 | — |
| T3 | README with hero image | 2 | T1 |
| T4 | Social preview image | 1 | T3 |
| T5 | Research sources and per-directory README and AGENTS | 3 | T2 |
| T6 | Agent rules, skills, hooks, enforced handoff | 8 | T1 |
| T7 | Sprint plan and implementation audit docs | 3 | T6 |

## Definition of done

- `main` protected by PR-only workflow and CI
- `cargo test --workspace` and `pytest` pass
- `scripts/check-handoff.sh` passes on a PR that updates the handoff
- Every directory has README.md and AGENTS.md

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Docs drift from code | Implementation audits record state; handoff is enforced by hook and CI. |

## Demo

1. Open a fresh agent session: it reads `docs/HANDOFF.md`, states the next step, and starts S1 T1 without questions.

## Go/no-go

- Owner confirms the license and the model-mix question in `docs/HANDOFF.md`.

State of this sprint on `main`: [implementation audit](../implementation/S0-foundations.md).
