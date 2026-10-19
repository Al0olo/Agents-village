# ADR-0009 — RQ1 run configuration: models, simulated day, probes, cost

- **Status:** Accepted
- **Date:** 2026-10-19
- **Authors:** Abdullah Farag, Claude (the owner delegated these decisions to Claude on 2026-10-19)
- **Context links:** [PRD section 1](../prd.md), [milestones](../milestones.md), [ADR-0008](0008-measures-amended-after-the-smoke-tests.md)

## Context

The pre-registration needs a fixed model mix, a length for a simulated day (the PRD says three days with two consolidations but the harness counts ticks), a probe schedule, and a cost basis. The smoke villages give measured evidence for the first and last.

## Decision

1. **Model mix.** Two frontier models and one open-weight model, citizens split three, three and two: `anthropic/claude-opus-5.5`, `openai/gpt-5.6-sol` and `deepseek/deepseek-v4-pro`. On the real citizen prompt each returned a valid action every time (four samples each) and in three whole villages no model drifted: the dated snapshots behind the aliases were `claude-opus-5.5-20260921`, `gpt-5.6-sol-20260709` and `deepseek-v4-pro-20260423`, and each model kept one provider. Reasoning is switched off where the model allows it (GPT-5.6 Sol, DeepSeek V4 Pro) and left on for Opus 5.5, which refuses to switch it off, with a larger token budget (700). Provider fallbacks stay off and each model is pinned to one provider (`provider.only`): `anthropic`, `openai` and `deepinfra/fp8` (full-precision weights; the open-weight model is offered by sixteen providers at fp4, fp8 and unknown precision). Unpinned, DeepSeek V4 Pro was served by Baidu and StreamLake within one block, and the launch controller's drift check rejected all three blocks of the first replication attempt at tick 5; with fallbacks off but no pin, a block cannot complete. The open-weight model is hosted by an OpenRouter provider (Relace in the smoke tests), not self-hosted; the PRD's self-hosted pinned replicate is a later ticket (S2-T13 onward).
2. **A simulated day is 12 ticks**, so a run is 36 ticks with two consolidations (S1-T12) at ticks 12 and 24. This is what the smoke tests ran per arm (12 ticks) and it gives a citizen a few turns a day at the loop's sleep bounds.
3. **Probe schedule.** Fact-only rounds at ticks 12 and 24 and the full round (facts, utility task, awareness funnel) at tick 36 (ADR-0008).
4. **Judge.** `anthropic/claude-haiku-5.5` with reasoning off and a 60-token cap, second judge `openai/gpt-5.6-sol` (ADR-0008).
5. **Cost basis (measured, then extrapolated).** The three smoke villages cost $8.52 for 3,408 calls, about $0.0025 a call, summed from per-call costs and matched to the account counter within 0.1%. In the third village six arms of 12 ticks, one full probe round and the judge cost $4.88, about $0.81 an arm. Scaling to 36 ticks and adding two fact-only rounds suggests about $1.7 to $4.5 per arm (the prompt-defense arms cost two to three times the others) and about $20 to $30 per block of eight arms (A, B with its two paraphrases, C, D, E, G). Ten blocks would then cost a few hundred dollars before reruns and the pilot, well under the PRD's $1k to $10k. This is an extrapolation from short villages with no consolidation and is not verified; the pilot replaces it.
6. **Who pays and where.** Inference runs through OpenRouter on the owner's key, with a hard spend cap in the gateway (S2-T5) before any run that is reported. Smoke tests before that use a script-side cap.
7. **License.** Apache-2.0 stands.
8. **Names and templates.** The place and person names are syllable combinations. A sample of 12 of the 184 names was searched and none matched a real place or person (two near matches, Ibthorpe and Skelmanthorpe, are different words); the sample is not exhaustive. The ten templates and the lists stand as written. A name found to be real is replaced and the change dated.

## Consequences

### Positive

- The pre-registration can name its models, run length and probe times.
- The cost question has a measured basis instead of a guess.

### Negative / trade-offs

- A day of 12 ticks is a choice, not a measurement; a different day length changes cost and the number of turns per citizen.
- Opus 5.5's mandatory reasoning makes its turns slower and dearer than the other two.
- Models are deprecated; a snapshot that disappears mid-study follows the plan in the pre-registration.

### Follow-ups

- Re-measure cost per village once consolidation exists (S1-T12) and in the pilot (S2).
- Self-host the open-weight replicate (S2-T13 onward).

## Alternatives considered

1. **A cheaper small-model mix.** The PRD requires frontier models for the real experiment, and small models passed facts on rarely in the first checks.
2. **A longer day.** More turns per citizen, but cost grows with it and the smoke tests ran at 12.

## References

- [`docs/implementation/S1-rq1-harness.md`](../implementation/S1-rq1-harness.md) ("Live check" and the smoke villages)
