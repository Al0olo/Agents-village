---
name: docs-style
description: Write or edit documentation, READMEs, PR descriptions and research prose in this repo's style. Use whenever producing prose meant for readers.
---

# Docs style

- Lead with the point. One idea per paragraph. Short sentences.
- Concrete over general: a number, a file, a command, a name.
- No process narration or self-reference in reader-facing documents.
- No padding: cut "it is important to note", "in order to", "robust", "leverage",
  "comprehensive", "seamless".
- Tables only for comparison; lists only for steps or parallel items.
- State uncertainty once, where it applies, and say what would resolve it.
- Each directory has a `README.md` (what it is, for people) and an `AGENTS.md` (rules
  an agent can act on). Update both when the directory's purpose or rules change.
- Reader-facing docs carry a byline and one date at most. Operational state goes in
  `docs/HANDOFF.md` and `docs/handoff/LOG.md`.
- Read it back as a stranger. Cut anything they would skip.
