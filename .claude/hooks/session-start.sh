#!/usr/bin/env bash
# Prints live repo state into the agent's context at session start, resume and compaction.
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
echo "== Agent Village session context =="
echo "Rule 0: read docs/HANDOFF.md first and update it before you finish (skill: handoff)."
echo
echo "Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
echo "Recent commits:"; git log --oneline -5 2>/dev/null
echo
echo "Uncommitted:"; git status --short 2>/dev/null | head -20
echo
if [ -f docs/handoff/LOG.md ]; then
  echo "Latest handoff log entry:"
  awk '/^## /{n++} n==1' docs/handoff/LOG.md | head -40
fi
exit 0
