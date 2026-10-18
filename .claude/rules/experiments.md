---
paths:
  - "experiments/**"
  - "docs/research/**"
  - "docs/prd.md"
  - "docs/milestones.md"
---

# Experiment and research rules

- A pre-registration is committed (and registered on OSF) before the first run:
  hypotheses, arms, measures, exclusions, stopping rule, analysis. After runs start,
  change nothing silently; add a dated amendment.
- The village or the paired block is the unit of analysis. One run is an anecdote.
  An exact permutation test with 4 per arm cannot go below p = 0.029, so use paired forks.
- Every model and provider is pinned and logged on every call; arms run at the same time;
  fallbacks are off. Balance the model mix per village.
- Plant facts only about fictional entities. Keep the canary string in released logs.
- Include an awareness probe and a prompt-paraphrase control. Report negative results.
- Claims need sources you opened. Record the reading level in `docs/research/sources.md`.
  Never repeat a number from a paper you only saw in a summary as if verified.
- Keep RQ2 and RQ3 deferred until RQ1 is reported, unless the owner says otherwise.
