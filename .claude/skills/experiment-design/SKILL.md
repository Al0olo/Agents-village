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
- Controls: awareness probe (a funnel, ADR-0008), prompt-paraphrase control, volume-matched random-block control.
- Prompt baselines: a family tuned on pilot blocks and frozen before the main run, with the selection rule written down (see the reference findings below).
- Awareness: report the probe, how it is scored and why answers are kept or excluded; analyze with and without aware citizens.
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

## Reference findings to design against

Each was read at source through a summarizing fetch, so quotes are excerpts and numbers are what the
paper reports for its own setting; `docs/research/sources.md` has the reading levels.

- **Mandela effect in multi-agent systems (2602.00428, Section 5.1, Appendix D.1, repo `eval_defense.py`).**
  The two prompt defenses are structured: *cognitive anchoring* makes the agent give an independent answer from its
  own knowledge first, treat others' statements as "an unverified claim, not evidence", and change its answer only
  for an "exceptionally compelling" argument; *source scrutiny* makes it assume persuasive intent, deconstruct the
  conversation and treat unnaturally coordinated consensus as low credibility. They run in a question-answering
  protocol with misleading peers, not a persistent village. Reported for GPT-4o, short-term: false-memory shift
  46.0% to 17.8% (anchoring) and 26.5% (scrutiny). Our arm B is an adaptation to the village, not their prompt.
- **Manufactured Confidence (2606.29279, Tables 1, 4, 5, 8, 9).** A hedge is discounted and a flat assertion
  obeyed ("probably" 0.00 to 0.40 unauthorized grants against 0.81 for the confident form). A passive
  "unverified" tag is mostly ignored; an active distrust instruction makes the agent distrust correct memory
  too (false escalation on a correct memory 1.00 on every model). Consolidation by an LLM extractor launders
  hedges (laundering rate 1.00 for mem0 and LangMem against 0.00 for a verbatim store). The fix is to keep the
  stance ("preserve the user's epistemic stance", "never upgrade a tentative claim"), which cut wrong grants from
  0.45 to 0.10, and one reliable redundant source restores correct decisions. Consequence for us: a strict
  distrust prompt (arm B) is expected to abdicate on true facts, so the prompt family must include a calibrated
  variant, and arm C is a prompt for the consolidator, not for the citizen.
- **PIMMUR (2509.18052, v2 HTML).** Unawareness: agents should not be able to infer the hypothesis; a model
  counts as aware if it names the phenomenon and describes its mechanism, and a study fails if three of five
  models infer it (average 47.6% of studies in v2). Minimal control: procedural instructions are fine,
  behavioral prescriptions such as "act skeptically" are violations unless they are the treatment. When agents
  knew the theory a balance outcome rose from 34.37% to 60.73% (the "Silicon Hawthorne" effect). So the baseline
  prompt carries no behavioral prescription, only the treatment arms do.
- **Suspicion probes (APS Observer review of Barrett, Neuberg and Luce, Chester and Lasko, Klein).** Probes ask
  what the study was about and whether anything seemed odd; they "have never been systemically validated"; only
  30% of probe-using studies said how they scored. Options: exclude highly suspicious participants, analyze them
  separately, or combine them if results do not differ. Report the probe, the scoring and the justification;
  Klein's check runs a variant told to act as the researchers expect. Not read: the primary papers.

Design rules that follow: never treat one prompt wording as "the" prompt baseline; keep suspicious and naive
citizens in the primary analysis and report both; code awareness blind with a rubric that does not count a careful
community as suspicion; a defense that lowers assertions without lowering carrying is a confidence defense.

- **Rubric edits move the boundary they do not mention.** Rewording one line of a coding rubric changed 23 to 27%
  of a borderline class in the neighbouring line (against 7% for a re-run of the unchanged rubric). Before adopting a
  new wording, re-code a subset that includes the borderline answers, run the unchanged rubric again as the noise
  control, and compare both with a stronger reader. If the boundary moves for an unintended reason, keep the old
  rubric, run the analysis under two judges and report both.
