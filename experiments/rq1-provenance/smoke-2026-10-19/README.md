# Smoke test, 2026-10-19

One village per arm to check the instrument with frontier models. Not a result and not part of
the pre-registered study.

- Citizens: 8, split over `anthropic/claude-opus-5.5`, `openai/gpt-5.6-sol` and
  `deepseek/deepseek-v4-pro` (reasoning off where the model allows it). Judge:
  `anthropic/claude-haiku-5.5`, temperature 0.
- Design: base village for 4 ticks, ten facts and two single-witness facts planted, fork into arms A and
  D, 12 ticks each, then arm E from the same fork with its block rate set to the share of claims D stored
  as hearsay (0.556). One probe round per arm, 312 answers coded blind.
- Cost: 794 calls, $1.77, matching the account counter.

`analyze.py` recomputes the measures from the logs and the judge's recorded replies (no model
calls) and redraws `assets/rq1-smoke.svg`; `summary.json` holds its output. The raw logs are not
committed: released logs must carry the canary string, and that plan is S2-T11.
