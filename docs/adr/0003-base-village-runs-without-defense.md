# ADR-0003 — The shared base village runs without defense until the fork

- **Status:** Accepted
- **Date:** 2026-10-18
- **Authors:** Abdullah Farag, Claude
- **Context links:** [PRD section 1](../prd.md), [S1](../sprints/S1-rq1-harness.md) (T13, T15, T17), [S2](../sprints/S2-rq1-pilot.md) (T1)

## Context

RQ1 runs one base village to the planting event and then forks it into every arm. The base village needs a memory policy of its own, and that policy decides what core and shared memory hold when the arms start. The question must be settled before the pre-registration, because it fixes the starting state of every arm.

## Decision

The base village runs under arm A's policy, which admits every claim, with the baseline prompt (`arms.BASE`). Treatment starts at the fork.

What the base stored stays as stored. The kernel judges only writes made after the fork and never reclassifies earlier entries. Memory entries are not evidence, so an unbacked entry from the base cannot back a later claim.

## Consequences

### Positive

- No arm's treatment shapes the shared history, so one base serves all arms and the arms start in identical state.
- The base is not a sixth, hidden arm.

### Negative / trade-offs

- Arm D starts with some entries in core and shared memory that its own rule would have kept as hearsay. They can mislead citizens, and a false belief planted later may land next to them. This works against arm D.
- Running the base under the kernel instead would give arm A a cleaner start, which also works against D. Neither choice favors the flagship claim.

### Follow-ups

- The pre-registration (S2-T1) states this choice and reports, for each block, the share of core and shared entries at the fork that the kernel's rule would have refused, so the size of the effect is visible.
- Changing it after registration is a dated amendment.

## Alternatives considered

1. **Run the base under the kernel (arm D).** The base becomes one arm's history, and arm A inherits a cleaner start than a village without defense would have.
2. **A separate base village per arm.** Breaks the paired design: arms would no longer start from identical state.
3. **Re-run admission over the base's entries at the fork, for arm D only.** A retroactive treatment: the arms would differ before the fork, and forks would no longer be identical until the arms diverge.

## References

- [`harness/src/agent_village/arms.py`](../../harness/src/agent_village/arms.py)
- [`harness/tests/test_arms.py`](../../harness/tests/test_arms.py)
