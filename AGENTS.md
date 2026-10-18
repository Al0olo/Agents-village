# Agent instructions

Guidance for AI coding agents and human contributors working in this repository.

**Scope:** `/`. Agent Village monorepo root.

Keep the root clean: configuration and top-level docs only. Code goes in `crates/` or `harness/`, designs in `experiments/` and `docs/`.
Checks: `cargo fmt --all -- --check && cargo clippy --workspace --all-targets -- -D warnings && cargo test --workspace`; `cd harness && ruff check . && pytest -q`.
`main` changes only through pull requests. Commits use Conventional Commits and carry `Co-Authored-By:` trailers for everyone who contributed.
