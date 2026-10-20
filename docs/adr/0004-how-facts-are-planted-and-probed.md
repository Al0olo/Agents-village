# ADR-0004 — How facts are planted and probed

- **Status:** Accepted
- **Date:** 2026-10-18
- **Authors:** Abdullah Farag, Claude
- **Context links:** [PRD section 1](../prd.md), [S1](../sprints/S1-rq1-harness.md) (T16 to T18, T19), [S2](../sprints/S2-rq1-pilot.md) (T1, T12)

## Context

The PRD fixes the counts (six false facts and four true facts about fictional entities), the counterbalancing (plausibility and planter status), the red-team variant (two colluding planters) and the measures (neutral probes on day 3, an awareness probe). It leaves open how truth, status and collusion are made real inside a village, and how a probe is asked. The kernel sees only citations, so every choice here changes what the experiment can show.

## Decision

1. **Truth is corroboration.** A planted fact is given to its holders as an ordinary first-hand observation (a `saw` event). A true fact has two independent holders. A false fact has one, or two in the colluding variant. Nothing else distinguishes true from false: the wording of the two reads alike.
2. **Status is a notice everyone sees.** The environment tells every citizen who the village elders are (two of eight). A high-status fact is held by elders and a low-status fact by everyone else. Holders rotate so no citizen carries the load.
3. **The plan is recorded, not shown.** A `plant` event per fact records the truth label, the cell, the holders and the answer for the analysis. Citizens never perceive it. Only `saw` and `plant` events are appended, so audit replay reproduces the planting.
4. **Probes are questions put to a citizen as a visitor would.** Each is a separate call in the citizen's usual context and under its arm's own prompt, answered as a `say` to the visitor, and it changes nothing the citizen knows or remembers. The fact questions are the plain questions from the generator. The awareness question comes last and avoids the words that would give the hypothesis away. A round is one driver action between ticks that audit replay reproduces.
5. **The counterbalancing is the one in `facts.py`**: true facts cover every plausibility and status cell once; false facts cover every cell and two cells twice, the pair rotating; the assignment rotates over ten templates.

## Amendment, 2026-10-20

[ADR-0014](0014-what-the-kernel-can-answer-and-how-many-blocks.md) adds a second way to plant a false fact: three of the six false facts per block are rumors, told to one citizen by a traveler as a `heard` event with an origin of its own (two travelers in the colluding variant). The first clause of this decision still describes true facts and witness-planted false facts. Alternative 1 (injecting messages from the planter) still holds: a `heard` event is appended between ticks by the planting function and replayed as an environment input, and no citizen is made to say anything.

## Consequences

### Positive

- The kernel treats planted facts exactly like organic ones, so the experiment tests the mechanism and not a special case.
- Planting and probing are ordinary logged events: forks share them and audit replay reproduces them.
- The colluding variant is one flag, and the known weakness (two colluders are two origins) is tested directly.

### Negative / trade-offs

- A true fact reaches the kernel as corroborated, so arm D is never asked to admit a true fact that only one citizen witnessed. D blocks such facts by design. That cost is measured by the utility task ([ADR-0006](0006-the-utility-task.md)), as the PRD says, not by the true facts here.
- Whether models respond to the elders notice, and whether holders pass a fact on, is unknown until the pilot. Both are measured there (S2).
- Probes measure what a citizen says it knows, not what it would do; the blinded judge codes the answers.
- The names and values are invented from syllables and word lists and are not checked against any real-world source; the owner reviews them before pre-registration.

### Follow-ups

- The owner confirms or changes this before S2-T1; a change after pre-registration is a dated amendment.
- S1-T20 codes probe answers; S1-T21 computes the measures from the `plant` and `probe` events.

## Alternatives considered

1. **Plant by injecting messages from the planter.** The messages would be events no tick produced, which audit replay cannot reproduce, and they bypass the citizen.
2. **Instruct a citizen to spread a falsehood.** It adds a deception role-play whose compliance varies by model and confounds the arms.
3. **Single-witness true facts.** They would measure over-blocking directly, but they break the four-cell counterbalance of the true facts and make the kernel's job on them impossible by construction. The utility task is the PRD's instrument for that cost.
4. **Ask probes in the world through a visitor citizen.** It adds a citizen whose behavior varies and whose questions interleave with the village's own events.

## References

- [`harness/src/agent_village/facts.py`](../../harness/src/agent_village/facts.py), [`planting.py`](../../harness/src/agent_village/planting.py), [`probes.py`](../../harness/src/agent_village/probes.py)
