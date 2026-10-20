# ADR-0013 — A review pass for every arm, and arm C changes only its prompt

- **Status:** Accepted
- **Date:** 2026-10-20
- **Authors:** Abdullah Farag, Claude (the owner delegated these decisions to Claude)
- **Context links:** [ADR-0001](0001-storage-and-memory.md), [ADR-0009](0009-rq1-run-configuration.md), [ADR-0011](0011-the-prompt-defense-family.md), [PRD section 1](../prd.md), [S1](../sprints/S1-rq1-harness.md) (T10, T12)

## Context

The PRD's arm C is the fix proposed in Manufactured Confidence (arXiv 2606.29279): memory layers that rewrite what an agent was told into "durable facts" launder hedges (laundering rate 1.00 for two off-the-shelf layers, 0.00 for a verbatim store), and a prompt that keeps the stated stance ("preserve the user's epistemic stance: if a claim was hedged, casual, attributed, or unverified", "never upgrade a tentative claim into a settled fact"; wrong grants 0.45 to 0.10 on hedged hearsay) removes most of it. Read at section level through a summarizing fetch of the HTML version; Appendix C abbreviates the full prompt and the paper's code repository could not be opened, so the wording below is ours and only the two quoted phrases are the paper's. Nothing in the harness consolidates memory yet, and blocks 1 to 3 ran without it, although ADR-0009 plans two consolidations per run.

## Decision

1. **A review pass** runs for every arm at the end of simulated days one and two (after that day's probe round, before the next day): each citizen is asked, in one call under the arm's review prompt, to turn what it has seen, done, heard and said since its last review, together with its core and recall notes, into short standalone notes, each citing the event numbers it rests on. At most 8 notes per review.
2. **The review is not in the write path of the treatment.** Every note goes through `Memory.write_claim` and the arm's admission policy, exactly like a note the citizen writes in its turn, requesting the private core tier. A note is not evidence (ADR-0001): under arm D a note citing only a told event is stored as hearsay, so the kernel stops laundering by construction, and under A, B and the others the note enters core as fact whatever it says. The declared kind of a note is taken from the first cited event of the writer's own, never from the model.
3. **The default review prompt** (`review-default-1`) asks for durable facts "that a later you can rely on", the paper's default instruction in the village's terms. It is the baseline of every arm except C, so the baseline shares the behaviour the paper measured.
4. **Arm C** is arm A (admit all, baseline citizen prompt) with the review prompt `review-hedge-1`, which adds the stance rule: keep who said it, how sure they were and whether you saw it yourself, never turn a tentative or secondhand claim into a settled one, never drop a doubt that was raised. It is the only difference from A, so C against A isolates the consolidator's prompt. It is a prompt for the consolidator, not for the citizen (ADR-0011).
5. **Logging and replay.** A review is a driver action between ticks, like a probe round: a `consolidation` marker (prompt version and hash), then per citizen a `model_call`, the `claim` events of its notes, and a `review` event holding the log position reviewed through. Audit replay re-executes it from the marker with the arm's review prompt and reports a different prompt as a divergence; a branch uses the new arm's prompt. A reply that is not a valid note list is an `invalid_action` and writes nothing.
6. **Blocks gain the pass by default** (`BlockConfig.consolidate`, `run_block.py --no-consolidation`). Blocks 1 to 3 are pre-pilot and ran without it.

## Consequences

### Positive

- The study tests the PRD's arm C and, under A, the laundering the paper reports; under D, whether the kernel stops it.
- The review adds 16 calls per arm and block, a small share of a village's cost.

### Negative / trade-offs

- Every arm now has a second paraphrased copy of what citizens know, so a false value can be re-expressed more confidently in core memory under A and B, and the review notes count as claims in the measures (writers, hearsay share for arm E's rate).
- The default prompt is our rendering of the paper's, not the paper's text, and a citizen's review is one model's reading of its own day. The pilot shows whether it launders.
- Reviewing at two fixed points ignores what is worth keeping; it keeps the design simple and replayable.

### Follow-ups

- Run one block with the pass and compare it with blocks 1 to 3 before the pilot fixes the design.
- If the pilot shows the default prompt does not launder, say so in the report; arm C then tests a difference that does not exist, which is a result.

## Alternatives considered

1. **Consolidate only in arm C.** It would make C differ from A by the pass itself, not by the prompt.
2. **A deterministic summarizer.** It cannot launder, so it cannot test the paper's mechanism.
3. **A third-party memory layer.** It puts a model in the write path with its own prompts (ADR-0001); arm F covers that as exploratory.
4. **Make the consolidator the citizen's own `remember` action again.** It would not be a distinct, loggable, replayable step.

## References

- Manufactured Confidence, arXiv [2606.29279](https://arxiv.org/abs/2606.29279) (abstract and HTML sections; quoted phrases from Appendix C and Section 3).
