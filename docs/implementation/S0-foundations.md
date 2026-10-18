# S0 — Foundations (implementation audit)

**Source of intent:** [`docs/sprints/S0-foundations.md`](../sprints/S0-foundations.md)  
**Status:** ✅ Complete once this PR merges.

## TL;DR

```bash
cargo test --workspace   # ledger conservation and overdraft tests, kernel and memory smoke tests
cd harness && pytest -q  # 6 admission-policy tests
ruff check .             # clean
scripts/check-handoff.sh # passes when docs/HANDOFF.md is updated
```

## Ticket status

Legend: ✅ done · 🟡 partial · 🚧 in progress or blocked · ⏸ deferred · ⏳ not started

| # | Title | Status | Notes |
| --- | --- | --- | --- |
| T1 | Monorepo scaffold: Rust workspace, Python harness, CI | ✅ | PR #1. `Cargo.toml` workspace with four crates; `harness/` with `admission.py` and 6 tests; `.github/workflows/ci.yml`. |
| T2 | PRD and milestones in `docs/` | ✅ | PR #2. `docs/prd.md`, `docs/milestones.md`. |
| T3 | README with hero image | ✅ | PR #3. `README.md`, `assets/hero.png`. |
| T4 | Social preview image | ✅ | PR #4. `assets/social-preview.png` (1280x640). The owner uploads it in repository settings. |
| T5 | Research sources and per-directory README and AGENTS | ✅ | PR #5. `docs/research/sources.md`; README and AGENTS in each directory (not `.github/`, not skill folders). |
| T6 | Agent rules, skills, hooks, enforced handoff | ✅ | PR #6. `AGENTS.md`, `CLAUDE.md`, `.claude/rules`, ten skills, hooks, `scripts/check-handoff.sh`, CI `handoff` job, `docs/HANDOFF.md`. |
| T7 | Sprint plan and implementation audit docs | 🚧 | This PR. Sprint and implementation docs. |

## Deferred or open

- Apache-2.0 was chosen without the owner's confirmation.
- No frontend build in CI yet; the observer UI is TypeScript with Next.js and arrives in S5.
