# S3 — RQ1 main run and report

**Weeks:** 9–16  
**Team:** 1 owner + agents + 1 human coder  
**Total points:** ~62  
**Exit criterion:** A complete, honest write-up of RQ1 with released code and logs, whichever way the result goes.

## Goal

Run the registered experiment exactly as written, analyze it exactly as registered, and publish.

## In scope

- Frozen, hash-pinned configs
- All blocks, run in parallel within budget
- Blinded coding, analysis exactly as registered, red-team arm
- Deviation log, paper draft, released code and logs with the canary string

## Out of scope

- Any change to arms, measures or analysis (amend instead)
- RQ2 and RQ3

## Tickets

Ticket ids are `S3-T<n>`. Branch names `S3/<area>/<slug>`; PRs say `Closes S3-T<n>`.

### Run

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T1 | Freeze configs and record their hashes | 2 | S2 |
| T2 | Run all blocks (about 10) with simultaneous arm launch | 13 | T1 |
| T3 | Run monitor: cost, crashes, drift, exclusion triggers | 3 | T2 |
| T4 | Apply exclusion rules exactly as registered | 2 | T2 |

### Analysis

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T5 | Blinded coding of probes by judge plus human sample | 8 | T2 |
| T6 | Run the registered analysis; produce tables and figures | 5 | T5 |
| T7 | Red-team (colluding planters) results | 3 | T5 |
| T8 | Deviation log with dated amendments | 2 | T2 |

### Write-up and release

| # | Title | Points | Depends |
| --- | --- | --- | --- |
| T9 | Paper: 3 to 4 page proposal first, then full draft | 13 | T6 |
| T10 | Release code, configs and logs with canary string | 3 | T6 |
| T11 | Two external reviewers read the draft | 3 | T9 |
| T12 | Choose venue and submit | 2 | T11 |
| T13 | Scale the batch runner to all blocks; cost dashboard and alarms from `infra/` | 3 | S2 T15 |

## Definition of done

- All registered analyses run; deviations logged and dated
- Primary contrast reported with effect size and interval, either way
- Code and logs released; canary string present
- Paper draft reviewed by two people outside the project

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Models are deprecated or change mid-run | Registered plan covers it; pinned snapshots; abort rule. |
| Null result | Reported as a finding; the design makes a null informative. |
| Cost overrun | Hard cap from S2; run blocks in batches and stop at the cap. |

## Demo

1. Walk through the headline figure: attack rate by arm with paired differences.

## Go/no-go

- Owner decides whether to start RQ2 or RQ3 design, based on the result.

State of this sprint on `main`: [implementation audit](../implementation/S3-rq1-main.md).
