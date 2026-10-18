---
paths:
  - "crates/**"
  - "Cargo.toml"
  - "Cargo.lock"
---

# Rust rules

- Edition 2021, stable toolchain, `unsafe` forbidden (workspace lint). Do not add `allow`s
  to silence a lint; fix the code or justify in a comment next to a narrow `#[allow]`.
- Gate: `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`,
  `cargo test --workspace`. All three before every commit.
- Errors: libraries return typed errors (`thiserror`); only binaries use `anyhow`. No
  `unwrap`/`expect` outside tests except for provable invariants, with the invariant in
  the message. No panics on external input.
- Money is integer credits. Never use floating point for ledger amounts.
- Make illegal states unrepresentable: newtypes for ids (`CitizenId`, `EventId`), enums for
  states, private fields with constructors that validate.
- Async: tokio, structured concurrency, no blocking calls on the runtime, every model or
  tool call has a timeout and a cancellation path. Citizens are actors that own their state.
- Determinism: the policy code (admission, ledger, scheduling decisions) is pure and
  deterministic. Randomness and time come in through a trait so replay can control them.
- Public items are documented; every new behavior has a test; every bug fix has a
  regression test. Prefer table-driven and property tests (`proptest`) for invariants.
- Dependencies: add the fewest, pin via `Cargo.lock`, prefer well-maintained crates, and
  note why in the PR. No dependency on a network service from the kernel's core path.
- Port policy code from `harness/` only after the Python reference and its tests are final
  for the experiment, and add a cross-language test vector file both sides read.
