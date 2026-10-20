# ADR-0014 — What the kernel can answer, how arms are compared, and how many blocks

- **Status:** Accepted
- **Date:** 2026-10-20
- **Authors:** Abdullah Farag, Claude (after an outside review of the draft pre-registration on 2026-10-20)
- **Context links:** [ADR-0004](0004-how-facts-are-planted-and-probed.md), [ADR-0007](0007-corroborated-shared-tier.md), [ADR-0011](0011-the-prompt-defense-family.md), [ADR-0012](0012-the-kernel-arm-stays-as-specified.md), [PRD section 1](../prd.md)

## Context

An outside review of the draft pre-registration raised four points that the pilot would have baked in.

1. **D cannot win the primary measure by construction.** A planted false fact is one citizen's first-hand observation, which the kernel admits, so wiki contamination under D was 100%, 100%, 67% and 100%. The measure then tests whether hearsay gets laundered only through a channel the witness's own entry has already opened.
2. **A pilot of two blocks cannot set the block count.** The spread of the paired D minus A difference in four exploratory blocks is 0.34 (+60, +5, -5, -17 points). Simulating the registered test (`power_table.py`) gives, at a spread of 0.30 to 0.40, 35 to 60 blocks for a true effect of 15 points and 21 to 34 for 20 points; ten blocks reach 80% power only if the spread is 0.10 to 0.20 and the effect 20 points or more. The exact test also stopped at 20 blocks (fixed: 40, by meeting in the middle).
3. **Choosing the strongest prompt arm on two noisy blocks invites a winner's curse**, which would flatter the kernel in the main contrast (ADR-0011, clause 3).
4. **The measure rests on a model's reading** (no person has coded anything) and the rubric is sensitive at one boundary (audit, 2026-10-20). That stays disclosed and is not changed here.

## Decision

1. **A rumor condition.** Of the six false facts in a block, three are planted as before (one witness, first-hand `saw`) and three as rumors: a traveler tells one citizen of the fact's status level, as a `heard` event with its own origin (`traveler:<fact>`), so nobody in the village has seen it. Which three are rumors alternates with the parity of the block number, so every cell of the design is a rumor in half the blocks. The colluding variant has two travelers with two origins. True facts and utility facts are planted as before. This is built in S1-T34 and the pilot waits for it.
2. **The primary outcome is the assertion rate of rumor-planted false facts by non-holders.** It is the case the kernel is built for: the village holds no first-hand source, so a citation is either missing or a single hearsay origin, and admission refuses it. Reported beside it, each with its own interval: witness-planted false facts (arm D is expected to show nothing, and G is the contrast), and all false facts together (the earlier definition). The guard is unchanged: assertion of true facts within the margin set on the pilot.
3. **H1 is an intersection-union contrast.** Arm D must have a lower primary rate than each of B, Bc and C in the main run, each by the paired exact test at alpha 0.05; the hypothesis is supported only if all three reject, and no multiplicity correction is needed for the primary. This removes the pilot's choice of a prompt arm (ADR-0011, clause 3 is superseded; the rest of ADR-0011 stands) and with it the winner's curse. It costs power: the weakest of the three decides. B2 and B3 still only check wording.
4. **The pilot sets other things**: the guard margin, the rate of arm E (D's share of claims stored as hearsay), probe temperature, whether the rumor condition behaves (hearers pass rumors on, D refuses unsupported write-ups), and a first estimate of the spread.
5. **The number of blocks is set by a written rule, not by the number ten.** The planning effect is 15 points. The planning spread is the larger of 0.25 and the sample standard deviation of the paired D minus prompt-arm differences over the pilot and the first eight main blocks, and the total block count is `power_table.blocks_needed` at 80% power, rounded up to a multiple of four and capped at 60. The re-estimate uses only the spread of the differences, not their mean or any p-value, and is made once, after block eight. If the cap is hit the report says the run is underpowered for 15 points. The exact test is used up to 40 blocks; above that the sign-flip p-value is a Monte Carlo estimate with a registered seed and 100,000 flips.
6. **Intervals** from fewer than ten blocks are reported as ranges of the differences (the bootstrap of three numbers is that), and the report says so.

## Consequences

### Positive

- The study can say something about D whichever way it comes out: the rumor rate is the question D can answer, and the witness rate measures the limit ADR-0012 names.
- No arm is chosen on two noisy blocks, and the block count follows the data.

### Negative / trade-offs

- Three rumor facts per block halve the false facts behind the primary rate, which raises its block-to-block spread. The pilot measures that; if it is large the block count rises.
- A traveler is a new kind of event (`heard`), and a rumor is a told event with no citizen behind it; hearers might not pass it on. If the pilot shows rumors never spread under any arm, the primary outcome has no variance and the design is reconsidered by dated amendment.
- Forty to sixty blocks of seven arms at about $23 each is $900 to $1,400 in inference.

### Follow-ups

- S1-T34: `heard` events, the rumor plan, metrics split by source, replay support (ADR-0004 gets a dated note).
- Rewrite H1, the design and the analysis sections of the pre-registration to match.

## Alternatives considered

1. **Keep witness-planted false facts only and word H1 as laundering.** It is honest but leaves D no way to show an effect on spread, which was the PRD's question.
2. **Plant every false fact as a rumor.** It gives the primary rate twice the facts but drops the lone-witness limit from the study; the mixed design reports both.
3. **Pick the prompt arm on the pilot anyway and report the others.** It keeps ADR-0011 but builds a selection effect into the main contrast.
4. **Fix ten blocks.** Ten blocks cannot detect 15 points unless the spread is below 0.1.

## References

- [`harness/src/agent_village/power.py`](../../harness/src/agent_village/power.py), [`experiments/rq1-provenance/power_table.py`](../../experiments/rq1-provenance/power_table.py) and its output in [`smoke-2026-10-19/power-table.txt`](../../experiments/rq1-provenance/smoke-2026-10-19/power-table.txt).
