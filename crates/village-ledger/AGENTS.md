# Agent instructions

**Scope:** `crates/village-ledger`. Double-entry credit ledger that charges citizens for their own inference.

A transfer must conserve the total. Never add a code path that changes a balance without a ledger entry. Tests cover overdraft and conservation.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
