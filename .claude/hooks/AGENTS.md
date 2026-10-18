# Agent instructions: hooks

**Scope:** `.claude/hooks/`.

Hooks must be fast, quiet on success and safe to run repeatedly. `stop-handoff.sh` must never loop: it exits when `stop_hook_active` is true. Test with sample JSON on stdin. Root rules in [AGENTS.md](/AGENTS.md) apply.
