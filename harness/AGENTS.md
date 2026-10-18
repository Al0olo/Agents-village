# Agent instructions

**Scope:** `harness`. Python harness and reference implementations used to run experiments before the Rust kernel is ready.

Python 3.10+. Install with `pip install -e ".[dev]"`; test with `pytest -q`; lint with `ruff check .`. Keep policy code pure and deterministic so it can be ported to Rust unchanged.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
