# Agent instructions

**Scope:** `crates`. The Rust workspace. Each crate has one job; shared settings live in the root `Cargo.toml`.

Add a crate by listing it in the root `[workspace] members`. `unsafe_code` is forbidden workspace-wide. Keep crates free of cross-dependencies except through `village-cli`.

Repository-wide rules are in the root [AGENTS.md](/AGENTS.md); they apply here too.
