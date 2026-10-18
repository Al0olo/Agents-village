---
name: rust-workflow
description: Write, test and review Rust code in the crates/ workspace. Use when adding or changing anything under crates/, Cargo.toml, or porting a policy from the Python harness.
paths:
  - "crates/**"
---

# Rust workflow

Rules are in `.claude/rules/rust.md`; this is the procedure.

1. Read the crate's `AGENTS.md` and `docs/prd.md` sections 5 to 8 for the requirement you are implementing.
2. Write the test first for the behavior (unit test in the module, or a table-driven test).
3. Implement the smallest change that passes. Types over comments: newtypes, enums, private fields.
4. Gate, in this order, and fix before moving on:
   `cargo fmt --all` then `cargo clippy --workspace --all-targets -- -D warnings` then `cargo test --workspace`.
5. For an invariant (ledger conserves total, replay rebuilds identical state), add a
   property test with `proptest` rather than a handful of examples.
6. Porting from Python: read `harness/src/agent_village/<module>.py`, port with the same
   names, share test vectors in `tests/vectors/*.json` that both languages load.
7. Update crate docs and `docs/HANDOFF.md`.

Review checklist: no `unwrap` on external input, no float money, no blocking in async,
timeouts on every model and tool call, errors typed, public items documented, no new
dependency without a reason.
