//! Memory tiers and the kernel admission policy.
//!
//! The policy under test in RQ1: a claim reaches core or shared memory as fact
//! only if it cites at least one first-hand event in the writer's own log, or at
//! least two told-events whose origin sets are disjoint. Everything else is kept
//! as hearsay in recall. The reference implementation lives in
//! `harness/src/agent_village/admission.py`; this crate will port it once the
//! Python results fix the semantics.

/// Where a memory lives.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Tier {
    /// Always in context.
    Core,
    /// Searchable per-citizen history; hearsay lands here.
    Recall,
    /// Long-term store.
    Archival,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tiers_compare() {
        assert_ne!(Tier::Core, Tier::Recall);
        assert_ne!(Tier::Recall, Tier::Archival);
    }
}
