# scripts

Repository scripts used by CI and hooks.

- `check-handoff.sh`: exits non-zero when the branch changes files but not `docs/HANDOFF.md`; skipped by `[skip-handoff]` in a commit message
