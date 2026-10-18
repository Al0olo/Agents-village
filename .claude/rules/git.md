# Git and pull requests

- Branch from an up-to-date `main`: `feat/`, `fix/`, `docs/`, `exp/`, `chore/`.
- Never commit to `main` directly. Open a pull request; CI must pass.
- Conventional Commits: `type(scope): summary`, imperative, under 72 characters.
- Every commit ends with `Co-Authored-By:` trailers for everyone who contributed,
  including the human owner. Keep the trailers the project owner or the harness gives you.
- One logical change per PR. Say what changed and why, and what you ran to check it.
- In cloud sessions `gh pr create` fails (GraphQL is blocked). Use the REST API:
  `gh api repos/al0olo/agents-village/pulls -f title=... -f head=BRANCH -f base=main -F body=@body.md`.
- The clone may be shallow. Fetch with `git fetch origin main` and reset to `FETCH_HEAD`
  if `origin/main` does not resolve.
- Never force-push a branch someone else may have based work on. Never rewrite `main`.
