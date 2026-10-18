---
name: kernel-invariants
description: Change the event log, ledger, memory admission, scheduler or replay. Use when touching crates/village-kernel, village-ledger, village-memory, or the admission policy in the harness.
paths:
  - "crates/**"
  - "harness/src/**"
---

# Kernel invariants

These must hold after every change. Add a test for any you touch.

1. **The event log is the source of truth.** Every perception, tool call, model output and
   payment is an event. State is derived by replay. No state that replay cannot rebuild.
2. **Append-only.** Events are never edited or deleted; corrections are new events.
3. **Ledger conserves.** A transfer debits and credits the same amount; the total changes
   only through explicit mint and burn entries. A balance never goes negative. Integer credits.
4. **Spend is kernel-enforced.** Per-citizen and per-lineage caps live in the kernel.
5. **Admission is deterministic and model-free.** A claim becomes fact only with a
   first-hand event in the writer's own log or two told-events with disjoint origins, none
   of which originates with the writer; otherwise it is stored as hearsay. Rejected writes fail silently as hearsay. Origins
   are tracked through forwards so they cannot be laundered.
6. **Replay is honest.** Audit replay and counterfactual forks use recorded model outputs.
   Never claim bit-for-bit reproducibility; hosted models are not deterministic.
7. **Sleeping is free.** A sleeping citizen holds no model call.
8. **Forks are identical.** A fork starts from identical state; arms launch together.
9. **The log is hash-chained** and messages and payments are signed by the citizen; one writer per village.
10. **Projections are rebuildable.** Claims, tiers, ledger and commitments equal a fold over the log; retrieval results are recorded so replay does not drift; no model sits in a memory write path. See `docs/adr/0001-storage-and-memory.md`.

Before merging: run the gate, replay a recorded log and compare state, and note any
invariant you relaxed (there should be none) in the PR and the handoff.
