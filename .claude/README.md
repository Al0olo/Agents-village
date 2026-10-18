# .claude

Configuration that makes AI coding agents productive in this repository.

- `rules/`: short rules, some loaded only when matching files are touched
- `skills/`: task procedures an agent loads on demand
- `hooks/`: scripts that run at session start and when a session tries to end
- `settings.json`: wires the hooks

The central rule is the handoff: every session reads `docs/HANDOFF.md` first and updates
it last. See `rules/00-handoff.md` and `skills/handoff/SKILL.md`.
