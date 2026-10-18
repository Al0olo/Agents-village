# Contributing

Agent Village is a research instrument first and a framework second. Contributions
that make experiments more credible are as welcome as code.

## Workflow

1. Open an issue first for anything larger than a small fix. For new experiments use
   the *Research proposal* template.
2. Branch from `main`: `feat/...`, `fix/...`, `docs/...`, `exp/...`.
3. Open a pull request. `main` is only changed through reviewed pull requests, and CI
   (Rust and Python) must pass.
4. Use [Conventional Commits](https://www.conventionalcommits.org/) for messages
   (`feat:`, `fix:`, `docs:`, `exp:`, `chore:`).
5. Credit everyone who contributed to a commit with `Co-Authored-By:` trailers.

## Repository layout

| Path | What lives there |
| --- | --- |
| `crates/` | Rust workspace: kernel, ledger, memory, CLI |
| `harness/` | Python harness and reference implementations used to run experiments first |
| `experiments/` | One folder per research question: design, pre-registration, configs, analysis |
| `docs/` | Product requirements, milestones, research notes |
| `assets/` | Images used by the docs |

## Research rules

- **Pre-registration comes before runs.** Hypotheses, metrics, exclusion rules and the
  analysis plan are committed (and registered on OSF) before the first run. Changes
  afterwards are dated amendments, never silent edits.
- **The village, or the paired block, is the unit of analysis.** A single run is an
  anecdote.
- **Report negative results.** A refuted question is a finding.
- **Cite what you read.** Mark claims taken from abstracts or secondary summaries as such.
- **Plant facts only about fictional entities**, and keep the canary string in released logs.

## Safety

Anything that reaches the outside world (the gateway) needs an ethics review and a
working kill switch before it merges. See `SECURITY.md`.
