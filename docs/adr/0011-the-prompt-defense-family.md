# ADR-0011 — The prompt defense is a family, chosen on the pilot and frozen

- **Status:** Accepted; clause 3 (the pilot picks the better prompt arm) is superseded by [ADR-0014](0014-what-the-kernel-can-answer-and-how-many-blocks.md)
- **Date:** 2026-10-19
- **Authors:** Abdullah Farag, Claude (the owner delegated these decisions to Claude on 2026-10-19)
- **Context links:** [PRD section 1](../prd.md), [ADR-0008](0008-measures-amended-after-the-smoke-tests.md), [`.claude/skills/experiment-design/SKILL.md`](../../.claude/skills/experiment-design/SKILL.md)

## Context

The primary contrast is the kernel (arm D) against the better of the prompt-level arms. In the smoke villages before the memory fix (ADR-0010) arm B, the anchoring-and-scrutiny prompt, took the assertion rate of false facts to 2 to 21% and the assertion rate of true facts to 0%: citizens read every value out as "one unconfirmed report". After the fix, on the corrected rubric, one village gave 50% for false facts and 54% for true against 67% and 67% with no defense, so the strictness was largely an artifact of citizens forgetting their own experience; the family and the selection rule are kept because the pilot, not one village, decides. A kernel that does better on true facts would then be compared with a defense that refuses everything, which is a strawman.

The reference papers say this is expected. In Manufactured Confidence an active distrust instruction made agents distrust correct memory on every model tested (false escalation 1.00 on a correct memory), a passive "unverified" tag was mostly ignored, and what helped was keeping the stated confidence and having a second reliable source (Tables 1, 4, 8; reading level in `docs/research/sources.md`). The Mandela-effect paper's defenses are written for a question-answering task with misleading peers and require an independent answer from the agent's own knowledge first, which does not exist for invented entities; arm B is therefore an adaptation, not their prompt. PIMMUR treats a behavioral prescription such as "act skeptically" as a violation of minimal control unless it is the treatment, which here it is, in the prompt arms only.

## Decision

1. **The prompt-level arms are a family.** Arm B has three wordings of a strict anchoring-and-scrutiny prompt (`anchor-scrutiny-1a` to `1c`, the second and third for the paraphrase control). Arm Bc is a calibrated version (`anchor-calibrated-1`): the same two ideas, but it tells the citizen to share first-hand knowledge plainly, to pass on what others said with who said it, to count agreeing independent accounts for more, not to dismiss what it did not see, and to say "I do not know" only when it has nothing.
2. **Arm C is a prompt for the consolidator**, not for the citizen (S1-T10), following the paper's fix of keeping the stated confidence.
3. **The better prompt-level arm is chosen on the pilot blocks and frozen before the main run.** Among B (first wording), Bc and C, it is the arm with the lowest assertion rate of false facts whose assertion rate of true facts stays within the guard margin of arm A (ADR-0008); if none qualifies, the one with the highest true-fact rate; ties go to the cheaper arm. The pilot's choice and the numbers behind it are written into the pre-registration. B2 and B3 are not candidates; they show whether wording alone moves the result.
4. **Every prompt in the family and the baseline carries no hypothesis words**, a test checks it, and the baseline prompt carries no behavioral prescription.

## Consequences

### Positive

- The strongest prompt baseline is given equal tuning effort to the kernel's, so a win by the kernel is not a win over a strawman, and a loss is reported as one.
- A strict prompt that only trades true facts for false ones is reported as that.

### Negative / trade-offs

- A pilot with two blocks picks the baseline with noise (single villages differ a lot); the choice is on the pilot only and the main run does not revisit it.
- One more arm per block (Bc), and the strict B arms cost two to three times the others.

### Follow-ups

- Run Bc beside B in a village to see whether the calibrated wording keeps true facts (S2 pilot). One village so far, on the third rubric: Bc 62% assertion rate of false facts and 54% of true, against 50% and 54% for B and 67% and 67% for no defense in the village before it; the first run of Bc scored zero assertions only because the second rubric coded attribution as a hedge (ADR-0008).
- Write arm C's consolidator prompt after reading the paper's code (S1-T10).

## Alternatives considered

1. **Keep B as the only prompt arm.** It is the PRD's arm, but the smoke villages show it abdicates, so the contrast would be unfair to the prompt side.
2. **Tune the prompt on the main run.** It would be a researcher degree of freedom; the pilot-only rule closes it.

## References

- [`harness/src/agent_village/prompts.py`](../../harness/src/agent_village/prompts.py), [`arms.py`](../../harness/src/agent_village/arms.py)
