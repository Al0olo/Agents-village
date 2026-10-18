---
name: experiment-design
description: Design, pre-register, run or analyze an experiment (RQ1, RQ2, RQ3). Use when writing a pre-registration, choosing arms, measures, sample size or statistics, planting facts, or interpreting results.
paths:
  - "experiments/**"
---

# Experiment design

Read `docs/prd.md` section 1 first. RQ1 is the flagship; RQ2 and RQ3 are deferred.

## Pre-registration checklist (commit before the first run)

- Question, hypothesis and the result that would refute it.
- Arms and the primary contrast (RQ1: kernel admission against the better prompt arm).
- The base village runs without defense until the fork (ADR-0003); report the share of core and shared entries at the fork that the kernel's rule would have refused.
- Unit of analysis: the village or paired block. Blocks, forks and their number, with the
  pilot that sets it.
- Measures, how each is coded, who or what codes it (blinded judge plus human-validated sample).
- Model mix, pinned snapshot ids, routed provider, fallbacks off, arms launched together.
- Planted facts: fictional entities only, counterbalanced plausibility and planter status.
- Exploratory arms (for example F, off-the-shelf memory) are labelled exploratory, excluded from the primary contrast and from multiplicity correction.
- Controls: awareness probe, prompt-paraphrase control, volume-matched random-block control.
- Exclusion rules for crashed villages, stopping rule, plan for deprecated models.
- Analysis: paired within-block differences, effect sizes with intervals, correction for
  multiple comparisons, power estimate and how it will be recomputed from the pilot.
- Support and refutation conditions written in advance.

## Statistics reminders

- Exact permutation test floor is about 0.029 with 4 per arm, 0.10 with 3 per arm, so
  unpaired small designs cannot reach significance. Paired forks are the power tool.
- R0 is undefined with 7 susceptibles at daily resolution; do not use it.
- Report negative results.

## Procedure

1. Write `experiments/<rq>/PREREGISTRATION.md` from the checklist; get the owner's review.
2. Run the 2-block pilot; record variance, fork correlation, coding reliability, cost per citizen-day.
3. Freeze configs (hash-pinned), register on OSF, then run.
4. Analyze exactly as registered; put deviations in a dated amendment.
5. Update `docs/HANDOFF.md`.
