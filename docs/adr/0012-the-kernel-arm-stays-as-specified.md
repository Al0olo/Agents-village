# ADR-0012 — The kernel arm stays as specified

- **Status:** Accepted
- **Date:** 2026-10-20
- **Authors:** Abdullah Farag, Claude (the owner accepted Claude's recommendation on 2026-10-20)
- **Context links:** [ADR-0007](0007-corroborated-shared-tier.md), [ADR-0004](0004-how-facts-are-planted-and-probed.md), [PRD section 1](../prd.md), [pre-registration](../../experiments/rq1-provenance/PREREGISTRATION.md)

## Context

Three complete blocks (arms A, B, Bc, D and G, 40 ticks; audit in [S1](../implementation/S1-rq1-harness.md)) gave arm D, kernel admission as specified, false-fact assertion rates of 79%, 55% and 45% against 19%, 50% and 50% with no defense, and wiki contamination of 100%, 100% and 67%. The kernel admits a claim that cites one first-hand event of the writer, and a planted false fact is its one witness's first-hand observation, so the witness's wiki entry is admitted and the other citizens read it. Arm G, which also needs two independent sources for the shared tier, wrote nothing to the wiki and gave out almost no true facts (0% and 8%).

## Decision

1. **Arm D stays as registered.** Its rule is the PRD's mechanism, and a result that it does not reduce false-fact assertion beyond the prompt defense is a result. It is not changed to look better.
2. **Arm G stays exploratory** (ADR-0007), outside the primary contrast and the multiplicity correction.
3. **A milder corroboration rule is not built** unless the pilot shows G silences the wiki, as ADR-0007 already says. If it is built, it is a dated amendment to the pre-registration, enters as a new exploratory arm, and is not part of the primary contrast.
4. **The planted fact is not moved to hearsay** (ADR-0004, alternative 2).
5. **The hypothesis is reported as a possibly refuted one.** The pre-registration already says H1 is refuted if D's rate is not lower than the chosen prompt arm's, and the three blocks lean that way; the main run decides it.

## Consequences

### Positive

- The primary contrast stays the one the PRD pre-registered, so a null result is not a retrofit.
- The cost of the lone-witness gap is reported by G beside D, with the utility task showing what closing it costs.

### Negative / trade-offs

- The study may report that the kernel as specified does not help against a lone first-hand witness. That is a narrower claim than the PRD's hope, and it is what the data support so far.
- The pilot's two blocks are the first test of D, B and C against each other in the same blocks, so any change to the kernel arm waits for them.

### Follow-ups

- Write the decision into the pre-registration before the pilot.
- Revisit only if the pilot contradicts the three blocks above.

## Alternatives considered

1. **Make corroboration the registered kernel.** It answers a different question and blocks true single-witness facts too (utility 0% and 7%).
2. **Redesign the planted fact so the witness is not a lone first-hand source.** The planter would then have invented a source, a deception role-play whose compliance varies by model (ADR-0004).
3. **Drop D from the primary contrast and rely on G.** It would hide the result that matters most.

## References

- [`docs/implementation/S1-rq1-harness.md`](../implementation/S1-rq1-harness.md), replication blocks 1 to 3.
