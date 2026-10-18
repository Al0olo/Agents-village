---
paths:
  - "apps/**"
  - "**/*.{tsx,ts,jsx,css,html}"
---

# Frontend rules (observer UI)

- The observer is a window, not a leash: it can pause, inspect and kill, but it is never
  part of a citizen's loop and never sends content that a citizen reads as instruction.
- TypeScript in strict mode, no `any`. Components are small and typed; data comes from
  the kernel's event stream through one typed client module.
- Everything shown comes from events: any number on screen must be derivable from the log.
  Show provenance (event id, origin) next to claims.
- Accessible by default: semantic HTML, labels, keyboard operation, contrast that passes
  WCAG AA, light and dark themes, works at phone width.
- Use the `frontend-design` skill for visual decisions; avoid templated defaults.
- Tests for logic (Vitest) and a Playwright smoke test per screen. No secrets in the client.
- State the stack choice in `docs/HANDOFF.md` once it is made; until then do not add a
  frontend build to CI.
