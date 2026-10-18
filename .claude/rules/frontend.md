---
paths:
  - "apps/**"
  - "**/*.{tsx,ts,jsx,css,html}"
---

# Frontend rules (observer UI)

Stack (decided by the owner): TypeScript and Next.js (App Router), in `apps/observer/`.

- The observer is a window, not a leash: it can pause, inspect and kill, but it is never
  part of a citizen's loop and never sends content that a citizen reads as instruction.
- TypeScript in strict mode, no `any`. Next.js App Router: server components by default,
  `"use client"` only where interaction needs it. Components are small and typed; data
  comes from the kernel's event stream through one typed client module (`lib/events.ts`).
- pnpm, ESLint with `next/core-web-vitals` and `typescript-eslint`, Prettier. Validate every
  external payload at the boundary (zod); never trust event JSON by type assertion alone.
- Everything shown comes from events: any number on screen must be derivable from the log.
  Show provenance (event id, origin) next to claims.
- Accessible by default: semantic HTML, labels, keyboard operation, contrast that passes
  WCAG AA, light and dark themes, works at phone width.
- Use the `frontend-design` skill for visual decisions; avoid templated defaults.
- Tests for logic (Vitest) and a Playwright smoke test per screen. No secrets in the client.
- CI: once `apps/observer/` exists, add a job running `pnpm lint`, `pnpm typecheck`,
  `pnpm test` and `pnpm build`. The observer is read-only toward citizens: it talks to the
  kernel's operator API, never to a citizen.
