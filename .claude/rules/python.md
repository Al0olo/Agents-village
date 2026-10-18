---
paths:
  - "harness/**"
  - "experiments/**/*.py"
---

# Python rules

- Python 3.10+, src layout, package `agent_village`. Type-annotate everything public.
- Gate: `ruff check .` and `pytest -q` from `harness/`. Both before every commit.
- Policy and analysis code is pure and deterministic: no hidden clocks, no global
  randomness. Pass a seeded `random.Random` or a clock object in.
- Frozen dataclasses for records; `Enum` for closed sets; no mutable default arguments.
- Tests: one file per module, `pytest` style, cover the failure cases that matter to the
  experiment (laundered origins, cross-citizen citations, empty input), not just the happy path.
- Experiment code must log: config hash, model snapshot ids, routed provider, seeds.
  Never overwrite raw run logs; derive analysis tables from them with a script.
- Statistics: report effect sizes with intervals; the unit is the village or paired block;
  use exact permutation tests where counts are small. Never `p`-hack: the analysis is
  fixed in the pre-registration.
- No network calls in unit tests. Model calls go behind an interface with a recorded or
  fake implementation for tests.
- Dependencies: standard library first; add one only with a reason in the PR.
