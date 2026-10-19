# ADR-0007 — An exploratory arm whose shared tier needs corroboration

- **Status:** Proposed
- **Date:** 2026-10-19
- **Authors:** Abdullah Farag, Claude
- **Context links:** [PRD section 1](../prd.md), [S1](../sprints/S1-rq1-harness.md) (T7, T33), [ADR-0004](0004-how-facts-are-planted-and-probed.md), [ADR-0006](0006-the-utility-task.md)

## Context

Arm D admits a claim as fact if it cites one first-hand event of the writer's own. A planted false fact is, by ADR-0004, the first-hand observation of its one witness. In the first frontier-model smoke test (one village per arm) that witness wrote the false fact to the shared wiki citing their own observation, the kernel admitted it, and arm D matched no defense: 5 of 6 false facts reached the wiki in both arms, and attack rate was 50% against 57%. The kernel stopped only re-telling. As specified, it cannot stop a lone first-hand witness, which is also how a deliberate liar publishes.

## Decision

1. **Keep arm D as registered.** It is the PRD's mechanism, and a refutation of it is a result.
2. **Add arm G, exploratory.** Its policy is the kernel's with one change: a claim for the shared tier needs two sources with disjoint origins even when the writer saw it first-hand. A first-hand event is one source whose origin is the writer; a told-event is a source with its own origins, and one that traces back to the writer does not count. Two first-hand events of the writer are one source. A claim for core memory, which is private, is judged exactly as under D.
3. **G only withholds.** It never admits a claim the kernel would refuse. What it adds to D's refusals is the lone witness's shared claim, which goes to recall as hearsay like any other.
4. **Exploratory status.** Like arm F, G is pre-registered as exploratory and excluded from the primary contrast (D against the better of B and C) and from the multiplicity correction. It runs in the same forks as the other arms.
5. **Mechanism.** `Claim` carries `shared`, set by `Memory.write_claim` when the requested tier is shared, so a policy can tell the tiers apart; `admit_corroborated` is in `admission.py` beside `admit`.

## Consequences

### Positive

- The experiment can say whether the lone witness is the whole story: if G cuts false-fact spread where D does not, provenance helps once a single witness cannot publish.
- D's registered claim is untouched, so the primary result is not changed by this arm.

### Negative / trade-offs

- G blocks true facts that only one citizen witnessed, as it blocks false ones. The utility task (ADR-0006) measures that cost; expect it to be larger than D's.
- A witness who is told the same fact by someone independent can publish, so a colluding pair still gets through, as under D.
- Each extra arm adds one village per block to the inference bill.
- The invariant that admission needs a first-hand event or two disjoint told-events describes D; G is stricter and the Rust kernel need not implement it for RQ1.

### Follow-ups

- Report G beside D in the pilot (S2) and decide whether it stays in the main run.
- The owner reviews the definition of a source before pre-registration; a change after S2-T1 is a dated amendment.

## Alternatives considered

1. **Change the kernel (D) to require corroboration.** It would drop the PRD's mechanism and answer a different question.
2. **Change what is planted so the false fact is hearsay for its planter.** The planter would then have lied about having seen it, which is a deception role-play whose compliance varies by model (ADR-0004, alternative 2).
3. **Gate core memory too.** Core is private, so a lone witness believing their own observation does not spread anything.

## References

- [`harness/src/agent_village/admission.py`](../../harness/src/agent_village/admission.py), [`arms.py`](../../harness/src/agent_village/arms.py)
