# S2 — RQ1 pilot and pre-registration

**Weeks:** 5–8  
**Team:** 1 owner + agents  
**Total points:** ~47  
**Exit criterion:** A pre-registration the owner has approved and a 2-block pilot that fixes the block count, the cost, and the coding reliability.

## Goal

Turn the design into a registered plan and measure what it cannot guess: between-village variance, fork correlation, judge reliability and cost per citizen-day.

## In scope

- Pre-registration document and OSF registration
- Analysis code tested on simulated data
- Live model gateway with pinned snapshots, provider logging and a hard cost cap
- The 2-block pilot (10 villages, 3 days)
- Power recomputation and block-count decision
- Pilot report

## Out of scope

- The main run (S3)
- RQ2 and RQ3

## Tickets

Ticket ids are `S2-T<n>`. Branch names `S2/<area>/<slug>`; PRs say `Closes S2-T<n>`.

### Pre-registration

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T1 | Draft `experiments/rq1-provenance/PREREGISTRATION.md` from the experiment-design checklist | 5 | S1 |
| T2 | Analysis code: paired within-block differences, exact permutation test, effect sizes with intervals, Holm correction | 5 | S1 T21 |
| T3 | Power simulation script parameterized by pilot estimates | 3 | T2 |
| T4 | Decide and pin the model mix (two frontier, one open-weight); record in the handoff | 2 | owner |
| T10 | Owner review, then OSF registration | 3 | T1,T2,T3 |
| T11 | Canary string and log release plan | 2 | T1 |

### Infrastructure

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T5 | Gateway config: OpenRouter routing, snapshot pinning, provider logging, fallback off, hard spend cap and kill switch | 5 | S1 T3 |

### Pilot

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T6 | Run the pilot: 2 blocks, 5 arms, 8 citizens, 3 days | 8 | T4,T5 |
| T7 | Judge reliability: blinded judge against human-coded sample | 5 | T6 |
| T8 | Estimate variance and fork correlation; recompute power; set block count | 3 | T6,T3 |
| T9 | Pilot report in `experiments/rq1-provenance/pilot/` | 3 | T7,T8 |
| T12 | Awareness probe calibration | 3 | T6 |

## Definition of done

- Pre-registration approved by the owner and registered on OSF
- Block count set from pilot data, with the power calculation attached
- Cost per citizen-day measured and budget approved
- Judge agreement with the human sample meets the threshold in the pre-registration
- Pilot logs archived; handoff updated

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Pilot variance is too large to detect a plausible effect | Increase blocks, shorten the planting-to-probe window, or tighten measures; decide before registering. |
| Hosted model drift mid-pilot | Arms launch together; snapshot ids logged; abort rule in the plan. |
| Inference cost overruns | Hard cap and kill switch (T5) before any live run. |

## Demo

1. Show the registered plan, the pilot's five arm results with intervals, and the power curve.

## Go/no-go

- Owner approves the plan and the budget. If the pilot shows no detectable effect at an affordable block count, stop and redesign rather than register.

State of this sprint on `main`: [implementation audit](../implementation/S2-rq1-pilot.md).
