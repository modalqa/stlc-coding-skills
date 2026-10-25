# Test Cases — RUN-20261025T044700Z

## Test Conditions

| ID | Condition | Requirement IDs | Risk IDs |
|---|---|---|---|
| TCOND-001 | Balance arithmetic | REQ-002 | RISK-002 |
| TCOND-002 | Amount validation | REQ-001 | RISK-003 |
| TCOND-003 | Atomicity | REQ-003 | RISK-001 |
| TCOND-004 | Immutability | REQ-004 | RISK-004 |

## Test Cases

### TC-001

- **test_case_id:** TC-001
- **requirement_ids:** REQ-002
- **risk_ids:** RISK-002
- **title:** Balance is sum of entries
- **objective:** Sum of +10.00 and -2.50
- **preconditions:** Disposable DB, empty tables
- **test_data:** acc-1: 10.00, -2.50
- **steps:** 1. record 10.00
2. record -2.50
3. balance(acc-1)
- **expected_result:** 7.50
- **test_level:** integration
- **test_type:** functional
- **design_technique:** equivalence partitioning
- **automation_status:** AUTOMATED
- **priority:** CRITICAL

### TC-002

- **test_case_id:** TC-002
- **requirement_ids:** REQ-001
- **risk_ids:** RISK-003
- **title:** Zero amount rejected
- **objective:** Validation
- **preconditions:** Disposable DB
- **test_data:** 0
- **steps:** 1. record(acc-1, 0)
- **expected_result:** ValueError; nothing persisted
- **test_level:** integration
- **test_type:** negative
- **design_technique:** equivalence partitioning
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-003

- **test_case_id:** TC-003
- **requirement_ids:** REQ-003
- **risk_ids:** RISK-001
- **title:** Atomic write on failure
- **objective:** Neither row persists if the balance upsert fails
- **preconditions:** Disposable DB; balances table made to reject the insert
- **test_data:** acc-2: 5.00
- **steps:** 1. Force the balances insert to fail
2. record(acc-2, 5.00)
3. Query entries for acc-2
- **expected_result:** Exception raised; zero entries for acc-2
- **test_level:** integration
- **test_type:** negative
- **design_technique:** error guessing
- **automation_status:** TO_AUTOMATE
- **priority:** CRITICAL

### TC-004

- **test_case_id:** TC-004
- **requirement_ids:** REQ-004
- **risk_ids:** RISK-004
- **title:** Entries cannot be updated
- **objective:** Immutability enforcement
- **preconditions:** Schema available
- **test_data:** n/a
- **steps:** 1. Review the schema/permissions for UPDATE/DELETE on entries
- **expected_result:** UPDATE/DELETE denied
- **test_level:** integration
- **test_type:** functional
- **design_technique:** use case
- **automation_status:** MANUAL
- **priority:** MEDIUM
