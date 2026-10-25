# Ledger Requirements

- AC-1: Recording an entry stores account, amount (2 decimals) and timestamp; amounts of 0 are rejected.
- AC-2: The balance of an account is the sum of its entries.
- AC-3: Recording an entry and updating the balance happen in one transaction; on failure neither is persisted.
- AC-4: Entries are immutable; corrections are new, opposite entries.
