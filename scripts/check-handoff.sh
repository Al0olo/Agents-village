#!/usr/bin/env bash
# Fails when this branch changes files but not docs/HANDOFF.md.
# Usage: scripts/check-handoff.sh [base-ref]   (base defaults to $BASE, origin/main, then main)
set -u
cd "$(git rev-parse --show-toplevel)" || exit 2

base="${1:-${BASE:-}}"
if [ -z "$base" ]; then
  for c in origin/main main; do
    if git rev-parse --verify -q "$c" >/dev/null; then base="$c"; break; fi
  done
fi

changed=""
if [ -n "$base" ] && mb=$(git merge-base "$base" HEAD 2>/dev/null); then
  changed=$(git diff --name-only "$mb" HEAD)
  msgs=$(git log --format=%B "$mb"..HEAD)
else
  msgs=""
fi
# uncommitted work counts too
changed="$changed
$(git status --porcelain | sed -E 's/^.{3}//; s/.* -> //')"
changed=$(printf '%s\n' "$changed" | sed '/^$/d' | sort -u)

[ -z "$changed" ] && { echo "handoff: no changes, nothing to check"; exit 0; }
printf '%s\n' "$msgs" | grep -q '\[skip-handoff\]' && { echo "handoff: skipped by commit message"; exit 0; }

others=$(printf '%s\n' "$changed" | grep -v -E '^(docs/HANDOFF\.md|docs/handoff/LOG\.md)$' || true)
[ -z "$others" ] && { echo "handoff: only handoff files changed"; exit 0; }

if printf '%s\n' "$changed" | grep -q -x 'docs/HANDOFF.md'; then
  echo "handoff: ok (docs/HANDOFF.md updated)"; exit 0
fi

echo "handoff: FAIL. Files changed but docs/HANDOFF.md was not updated." >&2
echo "Run the 'handoff' skill: update docs/HANDOFF.md and prepend an entry to docs/handoff/LOG.md." >&2
exit 1
