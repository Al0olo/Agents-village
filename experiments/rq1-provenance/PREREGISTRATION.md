# RQ1 pre-registration

**Status:** draft 2, 2026-10-20 (draft 1 of 2026-10-19 revised after an outside review, ADR-0014), not yet registered. Parameters marked *pilot* are set by the 2-block
pilot under the rules below and the document is then frozen: the commit that freezes it is the dated record
inside the repository, and the same text is to be filed on OSF before the first main-run block (the filing
needs an OSF account and is not done). After that, changes are dated amendments at the end.

Everything here follows from the PRD ([`docs/prd.md`](../../docs/prd.md) section 1) and ADRs
[0003](../../docs/adr/0003-base-village-runs-without-defense.md) to
[0014](../../docs/adr/0014-what-the-kernel-can-answer-and-how-many-blocks.md). Smoke villages run so far (one village per arm, one
block each) were checks of the instrument and are not part of the study; their numbers are in
[`docs/implementation/S1-rq1-harness.md`](../../docs/implementation/S1-rq1-harness.md).

## Question and hypothesis

Does a kernel that admits a claim to core or shared memory only with a kernel-checkable citation reduce
false-fact spread beyond the strongest prompt-level defense, without blocking true information?

- **H1 (primary).** Over blocks, the assertion rate of *rumor-planted* false facts by non-holders is lower under
  kernel admission (arm D) than under each of the prompt-level arms B, Bc and C. A rumor is told to one citizen by a
  traveler, so nobody in the village has seen it and admission has no first-hand citation to accept (ADR-0014).
  Supported only if all three paired exact tests reject at alpha 0.05 (an intersection-union test: no prompt arm is
  chosen on the pilot, and no correction is needed for the primary).
- **Guard.** The assertion rate of true facts under D stays within the margin *pilot* of arm A's.
- **Reported beside H1, each with its own interval:** the same contrast on witness-planted false facts (one
  first-hand witness; the kernel admits that witness, so no effect is expected from D, and arm G is the contrast),
  and on all false facts together.
- **Refuted if** D's rate on rumor-planted false facts is not lower than that of every prompt arm, or does not
  differ from the volume-matched random block's (arm E), which would mean blocking alone explains it, or if the
  guard fails. A guard failure with a lower rate is reported as a trade-off, not support.

## Design

- **Unit.** The block: one base village and its forks. Villages within a block are paired; blocks are the
  independent replicates. *Pilot*: 2 blocks with every arm, to measure between-block variance, fork correlation,
  judge agreement and cost, to check that rumors spread and that D refuses unsupported write-ups, and to set the
  guard margin, E's rate and probe temperature. The pilot does not choose a prompt arm and cannot set the number of
  main blocks alone: that follows the rule under Analysis. Blocks run before the pilot are exploratory.
- **Base and fork.** Each base village runs without defense for 4 ticks with the elders announced, then twelve
  facts are planted between ticks and every arm forks from that snapshot and runs 36 ticks (three days of 12),
  launched together in lockstep (ADR-0003, ADR-0009). Report the share of core and shared entries at the fork
  that the kernel's rule would have refused.
- **Citizens.** 8 per village: Opus 5.5, GPT-5.6 Sol and DeepSeek V4 Pro split three, three and two, snapshot
  ids and routed provider logged on every call, provider fallbacks off. Citizen names are fixed and capitalized.
- **Facts.** Per block ten facts about invented entities (six false, four true; plausibility and planter status
  counterbalanced over blocks, ADR-0004) plus two true single-witness facts for the utility task (ADR-0006).
  Three of the six false facts are witness-planted (one citizen saw it; two in the colluding variant) and three are
  rumors (a traveler told one citizen, as a `heard` event with its own origin; two travelers in the colluding variant);
  which three are rumors alternates with the parity of the block number (ADR-0014; built in S1-T34). A true fact has two
  witnesses. Seeds fix facts, holders and
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
- **Prompt-level arms for the contrast.** B (first wording), Bc and C are all in the contrast; none is chosen
  on the pilot (ADR-0014 supersedes ADR-0011 clause 3). B2 and B3 only check wording.
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

- **Primary:** assertion rate of rumor-planted false facts by non-holders, per village (ADR-0014); the same rate on
  witness-planted false facts and on all false facts are reported beside it.
- **Guard:** assertion rate of true facts.
- **Secondary (one family, Holm correction):** carry rate (the value passed on without being rejected) of false and of true facts; utility score; wiki
  contamination; ticks to k = 2 carriers; ticks to k = 2 writers; label creep (overall and on planted facts);
  hedge rate.
- **Awareness:** the share of citizens aware at any stage of the funnel and at the open stage.
- Claims are matched to facts verbatim, so adoption and contamination are lower bounds.

## Analysis

- Per block, the paired difference in the primary outcome (D minus B, D minus Bc, D minus C; also D minus E and
  D minus A). A paired exact (sign-flip) permutation test across blocks, two-sided, alpha 0.05 (exact up to 40 blocks;
  beyond that 100,000 random sign patterns with a registered seed); effect size with a bootstrap interval over blocks,
  reported as a range of the differences when there are fewer than ten. The model mix is fixed and reported by model.
- **Number of blocks.** The planning effect is 15 points of assertion rate. The planning spread is the larger of 0.25
  and the sample standard deviation of the paired D minus prompt-arm differences over the pilot and the first eight
  main blocks; the total is `blocks_needed` (`harness/src/agent_village/power.py`, 80% power at alpha 0.05, table in
  `experiments/rq1-provenance/smoke-2026-10-19/power-table.txt`) for that spread, rounded up to a multiple of four and
  capped at 60. The spread is re-estimated once, after block eight, from the differences alone (never their mean or a
  p-value). If the cap binds the report says the run is underpowered for 15 points. Exploratory blocks give a spread of
  0.34 for D minus A, which would mean about 45 blocks for 15 points.
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
