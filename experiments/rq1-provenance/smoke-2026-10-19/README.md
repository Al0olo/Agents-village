# Smoke tests, 2026-10-19

Two villages per arm to check the instrument with frontier models. Not results and not part of
the pre-registered study.

- Citizens: 8, split over `anthropic/claude-opus-5.5`, `openai/gpt-5.6-sol` and
  `deepseek/deepseek-v4-pro` (reasoning off where the model allows it). Judge:
  `anthropic/claude-haiku-5.5`, temperature 0, answers shuffled and coded blind.
- Design: base village for 4 ticks, ten facts and two single-witness facts planted, fork into arms, 12
  ticks each. Arm E is launched from the same fork afterwards, with its block rate set to the share of
  claims D stored as hearsay.
- `village-1`: arms A, D and E (E rate 0.556); 794 calls, $1.77. `village-2`: arms A, D, G and E (E rate
  0.429); 1,027 calls, $1.87. Both matched the account's usage counter within 0.1%.

All three villages were coded blind by the primary judge with the second rubric (`judge-fact-2`, ADR-0008); village 1 was first coded with the first rubric, and the tables in the audit before the sixth run use that coding. A second judge (`openai/gpt-5.6-sol`) coded village 3 for agreement: kappa 0.75 with the first rubric, 0.90 with the second.

`analyze.py` recomputes the measures from the logs and the judge's recorded replies (no model
calls), writes `summary-village-N.json`, and redraws `assets/rq1-smoke.svg` for the village it is
given. The raw logs are not committed: released logs must carry the canary string, and that plan is
S2-T11.
