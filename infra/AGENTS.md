# Agent instructions: infra

**Scope:** `infra/`. Infrastructure as code.

Nothing is created by hand except the state backend bootstrap. Every change goes through a PR with `terraform fmt`, `validate` and a reviewed `plan` in the PR body. No static cloud keys anywhere; CI uses OIDC. Research runs get no egress beyond the model gateway. The spend kill switch must be tested before any live run. Never commit state or secrets. See `.claude/rules/infra.md` and `docs/adr/0002-infrastructure-as-code.md`. Root rules in [AGENTS.md](/AGENTS.md) apply.
