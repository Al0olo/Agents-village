# Agent instructions

Canonical instructions for any AI coding agent (Claude Code, Codex, others) and for human
contributors. Claude Code loads this through `CLAUDE.md`. Deeper rules live in
`.claude/rules/` (loaded by path) and `.claude/skills/` (loaded by task).

## Rule 0: leave the context better than you found it

Every session starts by reading [`docs/HANDOFF.md`](docs/HANDOFF.md) and ends by updating
it. A new agent must be able to continue from where the last one stopped without asking
anyone or re-deriving anything. No exceptions, including for small changes and for
sessions that end early. Use the `handoff` skill; the exact procedure and the template
are there. CI fails a pull request that changes code but not `docs/HANDOFF.md`.

## What this project is

Agent Village is an instrument for pre-registered experiments on long-lived LLM societies,
and a framework to run them. The flagship question (RQ1) is whether kernel-enforced
citation provenance beats prompt-level defenses against false-fact spread. RQ2 and RQ3
are deferred. Read `docs/prd.md` section 1 before changing anything experimental.

## Repository map

| Path | Purpose |
| --- | --- |
| `crates/` | Rust workspace: kernel, ledger, memory, cli |
| `harness/` | Python harness and reference implementations (RQ1 runs here first) |
| `experiments/` | One folder per research question: design, pre-registration, configs, analysis |
| `docs/` | PRD, milestones, research sources, handoff state |
| `docs/sprints/` | Sprint plans and tickets (intent) |
| `docs/implementation/` | What is actually on `main`, per sprint (state) |
| `.claude/` | Rules, skills and hooks for agents |
| `infra/` | Infrastructure as code (OpenTofu), see ADR-0002 |
| `scripts/` | Repository scripts used by CI and hooks |

## Non-negotiables

1. **Handoff** (Rule 0).
2. **Pre-registration before runs.** Never change an experimental treatment, measure or
   analysis after runs start. Amend with a dated note instead.
3. **Do not invent evidence.** Every number, paper and quote comes from a source you
   opened. Mark abstract-level or secondary claims as such (`docs/research/sources.md`).
4. **Verify, then claim.** Run the tests and commands before saying something works.
   Report what failed and what you did not check.
5. **`main` only changes through pull requests** with CI green. Conventional Commits.
   Credit co-authors with `Co-Authored-By:` trailers.
6. **Safety by construction.** No ambient authority, no unbounded spend, no real-world
   reach from research runs. Plant facts only about fictional entities.
7. **Keep it small and plain.** No speculative abstractions, no padding in prose, no
   process narration in documents meant for readers.

## Commands

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cd harness && ruff check . && ruff format --check . && mypy && pytest -q --cov
scripts/check-handoff.sh        # does this branch update docs/HANDOFF.md?
```

## Skills

| Skill | Use when |
| --- | --- |
| `handoff` | Starting or finishing any session (always) |
| `sprint-workflow` | Picking up, working or closing a sprint ticket |
| `git-pr-workflow` | Branching, committing, opening or updating a PR |
| `rust-workflow` | Touching `crates/` |
| `python-harness` | Touching `harness/` |
| `frontend-observer` | Building the observer UI (`apps/`) |
| `experiment-design` | Designing, registering or analyzing an experiment |
| `research-sources` | Adding or checking a paper, number or claim |
| `kernel-invariants` | Changing the event log, ledger, memory policy or replay |
| `security-review` | Anything that touches memory admission, tools, money or the gateway |
| `docs-style` | Writing or editing prose |

Optional third-party skills are listed in `.claude/skills/README.md`.
