# Handoff

Updated: 2026-10-18 by Claude Sonnet 5.5 · Branch: `chore/claude-rules-skills-handoff` · Base: `main` at `36794f6`

## Objective

Build Agent Village as an instrument for pre-registered experiments on long-lived LLM
societies. Flagship question RQ1: does a kernel that admits claims into shared memory only
with a kernel-checkable citation reduce false-fact spread beyond the strongest prompt-level
defense, without blocking true information? RQ2 (purpose vs model and cost) and RQ3 (what
parent-authored reproduction selects for) are deferred until RQ1 is reported. The owner
(Abdullah Farag, Dubai) wants research novelty and a respectable reputation first;
funding is a later concern.

## State

- Done: PRD and Milestones written and polished, now in `docs/prd.md` and `docs/milestones.md`.
  The repo is the source of truth from here on. The original editable drafts are Claude Docs
  artifacts (PRD `510fd672-456e-4e1e-8caf-1e8fb822afe6`, Milestones `0b366759-60d8-4636-9cae-ace8a2587bbd`
  at claude.ai/code/artifact/<id>); they are stale copies, do not edit them.
- Done: monorepo scaffold (PR #1): Rust workspace (`village-kernel`, `village-ledger`
  [tested, double-entry], `village-memory`, `village-cli`), Python harness with a tested
  reference admission policy (`harness/src/agent_village/admission.py`), CI, community files.
- Done: README with hero image (PR #3), research sources with reading levels (PR #5),
  README and AGENTS file in every directory (PR #5), social preview image (PR #4).
- In progress: this branch adds the agent rules, skills, hooks and handoff system (this PR).
- Not started: RQ1 pre-registration, the 2-block pilot, the paired-fork village runner,
  the real kernel (M1), the observer UI.

## Next step

After this PR merges, write `experiments/rq1-provenance/PREREGISTRATION.md` using the
checklist in `.claude/skills/experiment-design/SKILL.md` and the design in `docs/prd.md`
section 1 (arms A to E, paired forks, about 10 blocks of 8 citizens for 3 days, 6 false
and 4 true planted facts about fictional entities, primary outcome final attack rate of
kernel admission against the better prompt arm). Get the owner's review before any run.

## Queue

1. Build a plain-Python village simulator with forkable state and a model interface (fake
   and recorded implementations) so the pilot can run before the Rust kernel exists.
2. Implement the structured claim writes, origin tracking through forwards, and the
   random-block control arm in the harness, with tests.
3. Run the 2-block pilot (10 villages, 3 days) to measure variance, fork correlation,
   coding reliability and cost per citizen-day; recompute power; set the block count.
4. Register on OSF, then run RQ1.
5. M1 Rust kernel in parallel; port admission only after the Python semantics are final,
   with shared test vectors.

## Open decisions (owner)

- Frontend stack for the observer UI (proposal: TypeScript strict, React with Vite, Vitest,
  Playwright). Nothing is built; do not add a frontend build to CI until chosen.
- License is Apache-2.0, chosen by the agent without asking; confirm.
- Model mix for RQ1: two frontier models and one pinned open-weight model; which ones.
- Where to run the pilot and who pays for inference (estimate about $1k to $10k for the
  full RQ1 at assumed prices; the measured cost per citizen-day replaces it).

## Gotchas

- `gh pr create` fails in cloud sessions (GraphQL blocked). Use the REST API; see
  `.claude/rules/git.md`.
- The clone is shallow; `origin/main` may not resolve. `git fetch origin main` then
  `git reset --hard FETCH_HEAD` on `main`.
- `pip install` needs `--break-system-packages` in the sandbox.
- GitHub shows the repo as `Al0olo/Agents-village`; API path `al0olo/agents-village` works.
- Do not add `README.md` under `.github/`: GitHub would show it instead of the root README.
- Verified numbers: exact permutation test floors (p = 0.029 at 4 per arm). NOT verified:
  the power estimate (d about 1.0 with 10 blocks) and the $1k to $10k cost; these are planning
  numbers. Papers cited at abstract level or from secondary summaries are marked in
  `docs/research/sources.md`; never state their figures as verified.
- Papers still unread or unverified: Behavioral Inheritance peer-review status, Genomebook
  beyond the abstract, Survive at All Costs full text, AI Village and Moltbook figures, MAST
  numbers, Emergence World licence, the Sotopia, Voyager, Generative Agents, Concordia and
  Melting Pot claims.
- Third-party skills were not audited; see `.claude/skills/README.md`.

## How to verify

```bash
cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace
cd harness && ruff check . && pytest -q
scripts/check-handoff.sh
```

## Pointers

- `AGENTS.md`, `CLAUDE.md`, `.claude/rules/`, `.claude/skills/`: how to work here
- `docs/prd.md` section 1: research questions and the RQ1 design
- `docs/milestones.md`: M1 to M5, gates, cost model
- `docs/research/sources.md`: bibliography with reading levels
- `docs/handoff/LOG.md`: history of sessions
