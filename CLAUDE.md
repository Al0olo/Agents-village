@AGENTS.md
@docs/HANDOFF.md

# Claude Code notes

- The two imports above load the repo rules and the current handoff state at session
  start. Treat `docs/HANDOFF.md` as the authority on what happened last and what to do next.
- Path-scoped rules in `.claude/rules/` load when you touch matching files. Skills in
  `.claude/skills/` load by task; invoke `handoff` at the start and end of every session.
- `gh pr create` is blocked in cloud sessions (GraphQL). Open PRs with the GitHub MCP tool
  (`mcp__github__create_pull_request`, load it with ToolSearch; it works where `gh` is not available),
  or else with `gh api repos/al0olo/agents-village/pulls -f title=... -f head=... -f base=main -F body=@file`.
- A `Stop` hook blocks ending the session when code changed but `docs/HANDOFF.md` did not.
