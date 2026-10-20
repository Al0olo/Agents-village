# RQ1 pre-registration

**Status:** draft 1, 2026-10-19, not yet registered. Parameters marked *pilot* are set by the 2-block
pilot under the rules below and the document is then frozen: the commit that freezes it is the dated record
inside the repository, and the same text is to be filed on OSF before the first main-run block (the filing
needs an OSF account and is not done). After that, changes are dated amendments at the end.

Everything here follows from the PRD ([`docs/prd.md`](../../docs/prd.md) section 1) and ADRs
[0003](../../docs/adr/0003-base-village-runs-without-defense.md) to
[0011](../../docs/adr/0011-the-prompt-defense-family.md). Smoke villages run so far (one village per arm, one
block each) were checks of the instrument and are not part of the study; their numbers are in
[`docs/implementation/S1-rq1-harness.md`](../../docs/implementation/S1-rq1-harness.md).

## Question and hypothesis

Does a kernel that admits a claim to core or shared memory only with a kernel-checkable citation reduce
false-fact spread beyond the strongest prompt-level defense, without blocking true information?

- **H1 (primary).** Over blocks, the assertion rate of false facts is lower under kernel admission (arm D)
  than under the chosen prompt-level arm.
- **Guard.** The assertion rate of true facts under D stays within the margin *pilot* of arm A's.
- **Refuted if** D's assertion rate of false facts is not lower than the chosen prompt arm's, or does not differ
  from the volume-matched random block's (arm E), which would mean blocking alone explains it, or if the
  guard fails. A guard failure with a lower false-fact rate is reported as a trade-off, not support.

## Design

- **Unit.** The block: one base village and its forks. Villages within a block are paired; blocks are the
  independent replicates. *Pilot*: 2 blocks with every arm, to measure between-block variance, fork correlation,
  judge agreement and cost, and to set the number of main blocks (about 10 is the planning figure; power
  is recomputed from the pilot and the planning figure of d about 1.0 is not verified).
- **Base and fork.** Each base village runs without defense for 4 ticks with the elders announced, then twelve
  facts are planted between ticks and every arm forks from that snapshot and runs 36 ticks (three days of 12),
  launched together in lockstep (ADR-0003, ADR-0009). Report the share of core and shared entries at the fork
  that the kernel's rule would have refused.
- **Citizens.** 8 per village: Opus 5.5, GPT-5.6 Sol and DeepSeek V4 Pro split three, three and two, snapshot
  ids and routed provider logged on every call, provider fallbacks off. Citizen names are fixed and capitalized.
- **Facts.** Per block ten facts about invented entities (six false, four true; plausibility and planter status
  counterbalanced over blocks, ADR-0004) plus two true single-witness facts for the utility task (ADR-0006).
  A false fact has one witness (two in the colluding variant); a true fact has two. Seeds fix facts, holders and
  the base village; blocks use seed 1 and block numbers 0 onward.
- **Arms.** A no defense; B prompt-level anchoring and source scrutiny, with B2 and B3 as the paraphrase control
  and Bc the calibrated version (ADR-0011); C hedge-preserving consolidation: arm A with a review prompt that keeps the stance of
  what citizens were told (`review-hedge-1`; every other arm uses `review-default-1`, ADR-0013); D kernel admission; E volume-matched random block at the rate
  *pilot* (D's measured share of claims stored as hearsay); exploratory: G corroborated wiki (ADR-0007) and
  F off-the-shelf memory. G and F are excluded from the primary contrast and from the multiplicity correction.
- **The kernel arm is D as specified (ADR-0012).** A claim is admitted with one first-hand event of the writer
  or two independent told-events, so a lone witness's claim is admitted. Three blocks before the pilot gave D
  false-fact assertion rates of 79%, 55% and 45% against 19%, 50% and 50% under A, and G wrote nothing to the
  wiki; D is not changed and G stays exploratory. A milder corroboration rule is built only if the pilot shows G
  silences the wiki, as a new exploratory arm by dated amendment.
- **Prompt-level arm for the contrast.** Chosen on the pilot by the rule in ADR-0011 among B, Bc and C and
  frozen. B2 and B3 only check wording.
- **Red team.** The colluding-planter variant of every arm in a subset of blocks *pilot*.
- **Review pass.** After days one and two every citizen turns its notes and what it lived since the last review into
  at most 8 cited notes in core memory, through the arm's admission policy (ADR-0013). Blocks run before the pilot had
  no review pass and are not part of the study.
- **Probes.** Fact and utility questions at ticks 12 and 24 (interim) and at tick 36 with the awareness funnel
  (ADR-0008). Each probe is an independent call under the arm's own prompt that changes nothing the citizen knows.

## Measures (ADR-0005, ADR-0006, ADR-0008)

All fact answers come from non-holders in the last round. Coded blind by a model judge (primary
`claude-haiku-5.5`, temperature 0, rubrics `judge-fact-3` and `judge-awareness-2`); a second judge
(`gpt-5.6-sol`) codes everything for agreement.

- **Primary:** assertion rate of false facts per village.
- **Guard:** assertion rate of true facts.
- **Secondary (one family, Holm correction):** carry rate (the value passed on without being rejected) of false and of true facts; utility score; wiki
  contamination; ticks to k = 2 carriers; ticks to k = 2 writers; label creep (overall and on planted facts);
  hedge rate.
- **Awareness:** the share of citizens aware at any stage of the funnel and at the open stage.
- Claims are matched to facts verbatim, so adoption and contamination are lower bounds.

## Analysis

- Per block, the paired difference in the primary outcome (D minus the chosen prompt arm; D minus E; D minus
  A). A paired exact (sign-flip) permutation test across blocks, two-sided, alpha 0.05; effect size with a
  bootstrap interval over blocks. The model mix is fixed and reported by model.
- Secondary measures: the same paired tests, Holm-adjusted within the secondary family.
- **Awareness sensitivity.** All citizens are in the primary analysis. Each result is repeated without the
  answers of citizens coded aware at any stage, and awareness is compared across arms; an arm difference is
  reported as a limitation, not corrected for.
- **Judge sensitivity.** Every contrast is computed under both judges (`analyze_blocks.py --judge 1|2`) and both
  are reported; the primary result is judge 1's. Answers that distance themselves from a value without doubting it
  ("I can't vouch for it first-hand, but Hal wrote…") sit on the line between `asserts` and `hedges`, and the
  judges, and the stand-in rater, split on them. The rubric is not reworded to fix that: three rewordings of the
  `denies` line moved answers of this kind from `hedges` to `asserts` in the primary judge (72 of block 1's 472
  `hedges` for the first; 54 and 42 on a 248-answer subset for the others), against 9 when the unchanged rubric
  was re-run on that subset.
- **Judge validity.** Kappa between the two judges per kind; a stratified sample sheet (a fixed number of
  answers per judge code, shuffled, with no arm, block, citizen or judge code) is coded by a rater who has not
  seen the judge's codes. In the draft the rater is a model, not a person: Opus 5.5, which is neither judge,
  coded 112 answers of one block (`rate_sheet.py`) and agreed with the primary judge at kappa 0.90 on facts and
  0.93 on awareness and with the second judge at 0.92 and 1.00; Claude's own earlier coding of 80 answers gave
  0.73 and 0.79. The judge's codes support a claim only if kappa on the sample is at least 0.7. The rater is
  reported as a model; a human sample of the same kind is added before the main run if one can be had.
- No analysis choice depends on the data after the freeze. Deviations are dated amendments.

## Exclusions, stopping and deprecated models

- A block is **dead** and excluded in full if any arm's village stops on a model error, a gateway stop or a
  model drift (a requested model served by more than one snapshot or provider), or if an arm log fails
  verification. Dead blocks are counted and reported; they are not rerun with the same seed as if nothing happened.
- Spend is capped by the gateway per run and in total; a cap stop ends the study at the blocks completed.
- The number of blocks is fixed after the pilot. No interim looks at outcomes; the study stops early only
  for budget, safety or a deprecated model that cannot be replaced.
- If a pinned snapshot is withdrawn, finish the block in progress only if it is not affected, record the
  withdrawal, and either continue with the remaining blocks or stop if more than two blocks are lost.

## Safety and release

Facts concern invented entities only. No citizen has tools or reach outside the village. Raw logs are released
only with the canary string in [`LOG-RELEASE.md`](LOG-RELEASE.md).

## Amendments

None yet.
