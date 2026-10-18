#!/usr/bin/env bash
# Blocks the end of a session when files changed but docs/HANDOFF.md did not.
input=$(cat)
# Avoid loops: if the hook already forced a continuation, let the session end.
printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && exit 0
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -x scripts/check-handoff.sh ] || exit 0
if out=$(scripts/check-handoff.sh 2>&1); then exit 0; fi
reason="You changed files but did not update docs/HANDOFF.md. Run the handoff skill now: rewrite docs/HANDOFF.md (done, in progress, exact next step, open decisions, gotchas), prepend an entry to docs/handoff/LOG.md, then finish. For a pure typo fix, put [skip-handoff] in the commit message."
printf '{"decision":"block","reason":"%s"}\n' "$reason"
exit 0
