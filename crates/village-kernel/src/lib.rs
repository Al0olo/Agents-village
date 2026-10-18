//! Kernel of Agent Village: citizen actors, mailboxes, the scheduler and the
//! append-only event log.
//!
//! Status: scaffold. Milestone M1 fills this crate in. The event log is the
//! single source of truth; every perception, tool call and payment is an event,
//! which is what makes audit replay and counterfactual forks possible.

/// Identifier of a citizen. Stable for the life of the village.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct CitizenId(pub u64);

/// Identifier of an event in the log. Monotonic within a village.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub struct EventId(pub u64);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn event_ids_are_ordered() {
        assert!(EventId(1) < EventId(2));
        assert_ne!(CitizenId(1), CitizenId(2));
    }
}
