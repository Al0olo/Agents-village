# hooks

- `session-start.sh`: prints branch, recent commits, uncommitted files and the latest handoff log entry into context
- `stop-handoff.sh`: blocks ending a session when files changed but `docs/HANDOFF.md` did not

Both are wired in `../settings.json`. The check logic is `scripts/check-handoff.sh`, also used by CI.
