# ADR-0015 — A spend cap for the study, and what it buys

- **Status:** Accepted
- **Date:** 2026-10-20
- **Authors:** Abdullah Farag, Claude (the owner set the cap on 2026-10-20: "like 200$ max")
- **Context links:** [ADR-0009](0009-rq1-run-configuration.md), [ADR-0014](0014-what-the-kernel-can-answer-and-how-many-blocks.md), [PRE-REGISTRATION](../../experiments/rq1-provenance/PREREGISTRATION.md)

## Context

ADR-0014's block-count rule asks for about 45 blocks to detect a 15-point effect at the spread seen so far, at about $20 for a six-arm block ($1,000 or more). The owner caps the pilot and main run together at $200 of inference.

Measured costs (block 4, four arms, 40 ticks, two judges): villages $11.62 (Opus 5.5 $7.26, GPT-5.6 Sol $3.94, DeepSeek V4 Pro $0.42), judges $1.78, so $2.9 an arm for villages and $0.45 an arm for judging. Six arms (A, B, Bc, C, D, E) therefore cost about $20 a block, extrapolated, not measured. Prices per million tokens in and out: Opus 5.5 $4 and $20, GPT-5.6 Sol $4 and $20, Sonnet 5.5 $2 and $10, Haiku 5.5 $0.10 and $0.50, DeepSeek V4 Pro $0.44 and $0.87 (the OpenRouter model list).

## Decision

1. **The cap is $200 for the pilot and the main run together**, enforced with `--max-cost` on every block and tracked in the handoff. Nothing is run past it without the owner.
2. **The block count is the smaller of the ADR-0014 rule and what the cap buys** at the cost per block measured on the pilot. If the cap binds, the report states the number of blocks, the smallest effect the test could detect at 80% power for the observed spread (`power_table.py`), and that the study is underpowered for 15 points.
3. **Arm G and the paraphrase arms B2 and B3 are not in the main run** (exploratory or wording checks). The main run's arms are A, B, Bc, C, D and E.
4. **At the unchanged model mix, $200 buys about nine six-arm blocks, two of them the pilot.** That detects a 30-point effect at a spread of 0.2 (about 7 blocks, `power-table.txt`) and little else.
5. **Two changes would roughly halve the cost per block and are not yet adopted**, because each changes ADR-0009 or the judge and needs a check that costs under $5: Sonnet 5.5 in place of Opus 5.5 for three citizens (about $0.9 an arm less), and DeepSeek V4 Pro as the second judge in place of GPT-5.6 Sol (about $1.5 a block less, if it agrees with the primary judge at kappa 0.85 or better on stored answers). Together they would give about $12.5 a block and about 14 main blocks. The owner decides whether to spend the check and take the swap.

## Consequences

### Positive

- The study cannot overrun, and the report says what the money bought.

### Negative / trade-offs

- Within $200 the study is underpowered for the effect sizes the earlier blocks suggest, so a null result will mean "no large effect", not "no effect".
- A cheaper mix is a weaker test of frontier models, and a swap changes the instrument between the exploratory blocks and the study.

### Follow-ups

- The owner's decision on item 5, then the pilot.

## Alternatives considered

1. **Run the ADR-0014 count anyway.** It costs about $900 and the owner declined.
2. **Fewer arms.** The intersection-union contrast needs B, Bc and C; A is the guard's reference and E the blocking control.
3. **Shorter villages (two days).** It lowers cost about a third but shortens the time for spread, which the pilot cannot evaluate.
