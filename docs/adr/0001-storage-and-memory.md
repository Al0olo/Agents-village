# ADR-0001 — Storage and memory: an event log we own, with rebuildable projections

- **Status:** Accepted
- **Date:** 2026-10-18
- **Authors:** Abdullah Farag, Claude
- **Context links:** [PRD sections 7 and 8](../prd.md), [S1](../sprints/S1-rq1-harness.md), [S4](../sprints/S4-rust-kernel.md)

## Context

Citizens must remember for weeks, be forkable at an exact event, and be replayable. RQ1's treatment is the memory admission policy, so memory cannot be a black box. Off-the-shelf memory layers (Mem0, Letta, Zep and similar) put a language model in the write path for extraction and consolidation. That would confound the treatment, break deterministic replay, and hide provenance.

Reading levels for comparisons of those products are low: the sources found are aggregator posts, so no benchmark numbers are relied on here.

## Decision

Memory is a **projection of an append-only, hash-chained event log that we own**. Nothing about memory lives outside the log.

1. **Truth.** Events: perceptions, messages, model calls (prompt hash, output, snapshot id, routed provider), tool calls, payments. Each event has a monotonic id, a content hash chained to the previous one, and, for messages and payments, an Ed25519 signature by the citizen. One writer per village, serialized through the village actor.
2. **Projections.** Rebuildable from the log: claims (claim text, kind seen, did or told, cited event ids, origin set, admission result fact or hearsay, event time and record time), memory tiers (core, recall, archival, shared), ledger balances, commitments. Admission is a pure function computed at write time.
3. **Retrieval.** Full-text plus vector search. The embedding model is pinned and logged; every retrieval result is recorded as an event so replay does not drift. Retrieval ranks; it never decides admission.
4. **Blobs.** Citizen notes and genome files are content-addressed (sha256) and referenced from events, so forks share them and diffs are free.
5. **Engines.** Harness (S1 to S3): SQLite in WAL mode, one file per village, FTS5 and sqlite-vec. Kernel (S4): Postgres with tsvector and pgvector. The schema is the same in both, and a parity test checks that the same log yields identical projections.
6. **Forks.** A fork is a new stream sharing the parent's log up to event N plus a copy of the projections. In SQLite that is a file copy; in Postgres, prefix replay or projection snapshots. No database-branching vendor.
7. **Borrowed ideas, not code.** Letta's tier vocabulary and Zep and Graphiti's bi-temporal facts (valid time versus record time). Graph memory is out of scope for v1.

## Consequences

### Positive

- The admission policy is the only gate into core and shared memory, and it is deterministic and testable.
- Audit replay and counterfactual forks are properties of the design.
- The harness and the kernel share a schema, so the Rust port is mechanical and checked by test vectors.
- No infrastructure is needed for S1 to S3.

### Negative / trade-offs

- We build and maintain memory ourselves, including retrieval quality.
- Two engines to keep in parity, until the kernel replaces the harness.
- Embedding drift must be controlled by pinning and logging.

### Follow-ups

- Tickets: S1-T25 to T31 and S4-T15 to T18.
- Update PRD sections 7 and 8.
- Optional extra RQ1 arm: an off-the-shelf memory product (for example Mem0), to show the kernel beats a real product and not only prompts. Costs one more arm of budget; owner to decide before pre-registration.

## Alternatives considered

1. **Mem0, Letta or Zep as the memory layer.** LLM in the write path; opaque provenance; not replayable.
2. **Postgres from day one.** Needs infrastructure and slows forking; adds nothing to RQ1.
3. **A graph database.** Premature; adds a query model we do not need to test the hypothesis.
4. **Database branching (Neon-style) for forks.** Vendor dependency; event-log forks are simpler and engine-independent.

## References

- [PRD section 8, memory and identity](../prd.md)
- [Research sources](../research/sources.md)
