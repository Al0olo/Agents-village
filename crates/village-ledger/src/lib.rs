//! Double-entry credit ledger.
//!
//! Every transfer debits one account and credits another by the same amount, so
//! the sum of all balances never changes except through explicit mint and burn
//! entries. Citizens pay for their own inference from this ledger.

use std::collections::HashMap;

/// Account identifier.
pub type Account = String;

/// Errors a transfer can produce.
#[derive(Debug, PartialEq, Eq)]
pub enum LedgerError {
    /// The paying account does not hold enough credits.
    InsufficientFunds { needed: u64, available: u64 },
}

/// In-memory ledger. Persistence arrives with the event log in milestone M1.
#[derive(Debug, Default)]
pub struct Ledger {
    balances: HashMap<Account, u64>,
}

impl Ledger {
    /// Create credits in an account (the village treasury or an endowment).
    pub fn mint(&mut self, to: &str, amount: u64) {
        *self.balances.entry(to.to_owned()).or_default() += amount;
    }

    /// Current balance; unknown accounts hold zero.
    pub fn balance(&self, account: &str) -> u64 {
        self.balances.get(account).copied().unwrap_or(0)
    }

    /// Move credits between accounts, failing if the payer cannot cover it.
    pub fn transfer(&mut self, from: &str, to: &str, amount: u64) -> Result<(), LedgerError> {
        let available = self.balance(from);
        if available < amount {
            return Err(LedgerError::InsufficientFunds {
                needed: amount,
                available,
            });
        }
        *self.balances.entry(from.to_owned()).or_default() -= amount;
        *self.balances.entry(to.to_owned()).or_default() += amount;
        Ok(())
    }

    /// Sum of all balances.
    pub fn total(&self) -> u64 {
        self.balances.values().sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn transfer_conserves_total() {
        let mut l = Ledger::default();
        l.mint("treasury", 100);
        l.transfer("treasury", "ada", 40).unwrap();
        assert_eq!(l.balance("ada"), 40);
        assert_eq!(l.total(), 100);
    }

    #[test]
    fn overdraft_is_refused() {
        let mut l = Ledger::default();
        l.mint("ada", 5);
        assert_eq!(
            l.transfer("ada", "bo", 6),
            Err(LedgerError::InsufficientFunds {
                needed: 6,
                available: 5
            })
        );
        assert_eq!(l.balance("ada"), 5);
    }
}
