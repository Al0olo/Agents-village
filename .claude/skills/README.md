# Skills

Project skills for agents working in this repository. Each skill is a folder with a
`SKILL.md` whose `description` tells the agent when to load it. They are short on
purpose: rules sit in `.claude/rules/`, and long references can be added next to a skill.

| Skill | Use when |
| --- | --- |
| `handoff` | Starting or finishing any session (always) |
| `git-pr-workflow` | Branching, committing, opening or updating a PR |
| `rust-workflow` | Touching `crates/` |
| `python-harness` | Touching `harness/` or `experiments/` |
| `frontend-observer` | Building the observer UI |
| `experiment-design` | Designing, registering or analyzing an experiment |
| `research-sources` | Adding or checking a paper, number or claim |
| `kernel-invariants` | Changing the event log, ledger, memory policy or replay |
| `security-review` | Reviewing a change for safety |
| `docs-style` | Writing or editing prose |

## Optional third-party skills

Listed from public skill directories and not audited. Skills run with the agent's
permissions, so read a skill's files before installing it.

| Source | Why it may help |
| --- | --- |
| [anthropics/skills](https://github.com/anthropics/skills) | Official examples including `frontend-design` and `webapp-testing`; install with `/plugin marketplace add anthropics/skills` |
| [apollographql/skills](https://github.com/apollographql/skills) | Includes a `rust-best-practices` skill |
| [obra/superpowers](https://github.com/obra/superpowers) | Planning, TDD and git worktree workflow |
| [upstash/context7](https://github.com/upstash/context7) | Current library documentation on demand |
| [lackeyjb/playwright-skill](https://github.com/lackeyjb/playwright-skill) | Browser tests for the observer UI |

Skill folders do not carry their own README or AGENTS file; `SKILL.md` is the document.
