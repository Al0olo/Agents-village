---
name: frontend-observer
description: Build the observer UI that watches a running village. Use when creating or changing anything under apps/ or any web UI, dashboards, or timeline and provenance views.
paths:
  - "apps/**"
---

# Observer UI

Purpose: let a human watch, pause, inspect and kill a village without being part of any
citizen's loop. Rules are in `.claude/rules/frontend.md`.

1. Read the observer requirements in `docs/prd.md` (sections 5 and 6) and the current
   stack decision in `docs/HANDOFF.md`. If no stack is recorded, propose one to the owner
   (default proposal: TypeScript strict, React with Vite, plain CSS variables, Vitest,
   Playwright) and record the decision before building.
2. Define the typed client for the kernel's event stream first; all views read from it.
3. Views in priority order: live event stream and cost per citizen; citizen detail with
   memory tiers and hearsay versus fact; provenance trace for a claim (event ids and
   origins); fork and replay controls; experiment arm comparison.
4. For visual direction use the `frontend-design` skill (official, in `anthropics/skills`).
   For charts use the `dataviz` skill if available. Keep light and dark themes and phone width.
5. Test logic with Vitest and each screen with a Playwright smoke test; check the page in a
   real browser before calling it done.
6. Update `docs/HANDOFF.md`.
