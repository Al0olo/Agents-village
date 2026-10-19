# ADR-0010 — Citizens remember what they saw, did, heard and said

- **Status:** Accepted
- **Date:** 2026-10-19
- **Authors:** Abdullah Farag, Claude (the owner delegated these decisions to Claude on 2026-10-19)
- **Context links:** [ADR-0003](0003-base-village-runs-without-defense.md), [ADR-0004](0004-how-facts-are-planted-and-probed.md), [ADR-0008](0008-measures-amended-after-the-smoke-tests.md)

## Context

The owner noticed a citizen answering a visitor that the elder named on a wiki entry "says she never wrote it or made that trip", and that the models seemed to suspect the village. The stored inputs and outputs of the calls (OpenRouter's I/O logging, read with `/generation/content`) showed why. A citizen's prompt held its memory tiers, the wiki, and a "New since you last acted" list that showed each sighting and each received message once. After that turn nothing in the prompt said what the citizen had seen, done, heard or said. The elder Ada wrote her four first-hand sightings to the wiki, and some turns later read the entry, found her own name on it, and wrote: "my own memory holds no record of those trips". She flagged the entry as unverified, told others she had not written it, and the others repeated it.

Across the smoke villages 15 of 147 turns in arm B, 1 of 144 in arm D and none in A (137 turns) or G (80) mention losing or disowning the citizen's own entry or memory; arm B is the most affected because its prompt tells citizens to trust only their own experience, so a citizen that cannot recall an experience distrusts it. This is a fault of the harness, not behavior to measure: a villager remembers what they saw, did and said, and the false-fact dynamics should not be driven by amnesia. It also made citizens doubt the village.

## Decision

1. **Two sections stay in a citizen's prompt after an event stops being new**, both limited to the most recent `memory_limit` entries and both excluding what is still in "New since you last acted" so nothing shows twice:
   - *What you have seen and done*: the citizen's own `saw` and `did` events, with their event numbers, which are evidence and can be cited.
   - *Recent conversations*: messages the citizen received (with the number of the `told` event, which is evidence) and messages it sent ("You told bo: ...", "You passed on to cy: ...") without a number, because acting is not evidence.
2. Text is flattened to one line as everywhere else, so a message cannot forge an event line.
3. Every `step` event records the render version (`render-2`); a change to the layout is a new version, like a prompt change.
4. The system prompts are unchanged, so arms A, B, D, E and G still differ only in their policy and prompt.

## Consequences

### Positive

- A citizen can always cite its own observation and knows what it wrote, so the false-fact dynamics are not distorted by forgetting. In the first run after the change no turn in arms A, B or D mentioned disowning an entry (0 of 254 turns), against 15 of 147 in arm B before.
- Elders remember who the elders are and a witness remembers what it witnessed, which a first-hand evidence rule needs.

### Negative / trade-offs

- Prompts are longer (a few hundred tokens), and more first-hand events stay citable, which makes first-hand claims easier under every arm.
- The arm B results in the three earlier villages were produced with the old layout and are partly an artifact of the forgetting; arm B is run again on the new layout before any number is reported.
- Recent conversations are limited, so a long village still forgets old talk; consolidation (S1-T12) is where older material is kept.

### Follow-ups

- Re-run arm B and its paraphrases on `render-2` (the first run after the change gave assertion rate 0% and hedge rate 83% for B, so the effect on hedging stands for one village).
- Archival memory (S1-T27, T28) for what falls out of the window.

## Alternatives considered

1. **Tell the citizen "you wrote entry N" in the wiki line.** It fixes one symptom, and the citizen would still not know what it saw or said.
2. **Show the whole history.** The prompt grows without bound and cost with it.
3. **Leave it and treat disowning as emergent behavior.** It comes from the harness dropping the citizen's own memory, not from the arms.

## References

- [`harness/src/agent_village/runner.py`](../../harness/src/agent_village/runner.py) (`_render`, `_remember`, `RENDER_VERSION`)
