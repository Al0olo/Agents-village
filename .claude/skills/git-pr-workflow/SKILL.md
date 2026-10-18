---
name: git-pr-workflow
description: Branch, commit and open pull requests in this repo. Use whenever creating a branch, writing a commit message, pushing, opening or updating a PR, or when CI fails on a PR.
---

# Git and PR workflow

1. Sync: `git fetch origin main && git checkout main && git reset --hard FETCH_HEAD`
   (the clone may be shallow; `origin/main` can fail to resolve).
2. Branch: `git checkout -b S<n>/<area>/<slug>` for a sprint ticket (see `docs/sprints/`), otherwise `fix/`, `docs/` or `chore/` plus a slug.
3. Work in small commits. Gate before each: see `AGENTS.md` Commands.
4. Update `docs/HANDOFF.md` in the same PR (skill `handoff`).
5. Commit message:

```
type(scope): imperative summary

Why this change, in a sentence or two.

Co-Authored-By: Abdullah Farag <ali.frg.c@gmail.com>
Co-Authored-By: <your model name> <noreply@anthropic.com>
```

6. Push: `git push -u origin <branch>`.
7. Open the PR with the REST API (GraphQL is blocked in cloud sessions):

```bash
gh api repos/al0olo/agents-village/pulls \
  -f title="type: summary" -f head=<branch> -f base=main -F body=@/tmp/pr.md --jq '.html_url'
```

   Body: what changed, why, what you ran to check it, and anything the reviewer must decide.
8. If CI fails, read the log, fix on the same branch, push. Do not merge red.
9. Merge order: if PRs depend on each other, say so in the body and merge in order.

Never commit to `main`, never force-push shared branches, never skip hooks.
