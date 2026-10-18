---
name: python-harness
description: Write, test and run Python harness and experiment code. Use when adding or changing anything under harness/ or experiments/, writing analysis scripts, or implementing the RQ1 admission policy and paired-fork runner.
paths:
  - "harness/**"
  - "experiments/**"
---

# Python harness workflow

Rules are in `.claude/rules/python.md`; this is the procedure.

1. Setup once: `cd harness && pip install -e ".[dev]"` (add `--break-system-packages` in the cloud sandbox).
2. Write the test first in `harness/tests/test_<module>.py`, including the failure cases.
3. Implement as pure functions over frozen dataclasses; inject clocks and randomness.
4. Gate: `ruff check .` and `pytest -q` from `harness/`.
5. Experiment code lives under `experiments/<rq>/`; it imports `agent_village`, reads a
   hash-pinned config, writes raw logs to `runs/` (git-ignored) and derives tables with a
   separate analysis script.
6. Every run records: config hash, model snapshot ids, routed provider, seeds, git sha.
7. Analysis: paired within-block differences, effect size with interval, exact permutation
   test where counts are small. Follow the pre-registration; deviations get a dated amendment.
8. Update `docs/HANDOFF.md`.

`admission.py` is the experimental treatment. Changing it changes the experiment: update
tests and the pre-registration first.
