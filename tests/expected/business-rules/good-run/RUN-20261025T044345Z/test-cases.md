# Test Cases — RUN-20261025T044345Z

## Test Conditions

| ID | Condition | Requirement IDs | Risk IDs |
|---|---|---|---|
| TCOND-001 | No discount below 100 | REQ-001 | RISK-001 |
| TCOND-002 | 5% tier edges | REQ-002 | RISK-001 |
| TCOND-003 | 10% tier edges | REQ-003 | RISK-001 |
| TCOND-004 | 15% tier edge | REQ-004 | RISK-001 |
| TCOND-005 | Loyalty bonus and cap | REQ-005 | RISK-002 |
| TCOND-006 | Invalid subtotal handling | REQ-006 | RISK-003 |
| TCOND-007 | Rounding | REQ-007 | RISK-004 |

## Test Cases

### TC-001

- **test_case_id:** TC-001
- **requirement_ids:** REQ-001
- **risk_ids:** RISK-001
- **title:** Just below 100 has no discount
- **objective:** Lower tier upper edge
- **preconditions:** None
- **test_data:** 99.99
- **steps:** 1. final_price(99.99)
- **expected_result:** 99.99
- **test_level:** unit
- **test_type:** boundary
- **design_technique:** boundary value analysis
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-002

- **test_case_id:** TC-002
- **requirement_ids:** REQ-002
- **risk_ids:** RISK-001
- **title:** Exactly 100 gets 5%
- **objective:** 5% tier lower edge (inclusive)
- **preconditions:** None
- **test_data:** 100.00
- **steps:** 1. final_price(100.00)
- **expected_result:** 95.00
- **test_level:** unit
- **test_type:** boundary
- **design_technique:** boundary value analysis
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-003

- **test_case_id:** TC-003
- **requirement_ids:** REQ-002
- **risk_ids:** RISK-001
- **title:** Upper edge of 5% tier
- **objective:** 5% tier upper edge
- **preconditions:** None
- **test_data:** 499.99
- **steps:** 1. final_price(499.99)
- **expected_result:** 474.99
- **test_level:** unit
- **test_type:** boundary
- **design_technique:** boundary value analysis
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-004

- **test_case_id:** TC-004
- **requirement_ids:** REQ-003
- **risk_ids:** RISK-001
- **title:** Exactly 500 gets 10%
- **objective:** 10% tier lower edge (inclusive)
- **preconditions:** None
- **test_data:** 500.00
- **steps:** 1. final_price(500.00)
- **expected_result:** 450.00
- **test_level:** unit
- **test_type:** boundary
- **design_technique:** boundary value analysis
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-005

- **test_case_id:** TC-005
- **requirement_ids:** REQ-003
- **risk_ids:** RISK-001
- **title:** Upper edge of 10% tier
- **objective:** 10% tier upper edge
- **preconditions:** None
- **test_data:** 999.99
- **steps:** 1. final_price(999.99)
- **expected_result:** 899.99
- **test_level:** unit
- **test_type:** boundary
- **design_technique:** boundary value analysis
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-006

- **test_case_id:** TC-006
- **requirement_ids:** REQ-004
- **risk_ids:** RISK-001
- **title:** Exactly 1000 gets 15%
- **objective:** 15% tier lower edge (inclusive)
- **preconditions:** None
- **test_data:** 1000.00
- **steps:** 1. final_price(1000.00)
- **expected_result:** 850.00
- **test_level:** unit
- **test_type:** boundary
- **design_technique:** boundary value analysis
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-007

- **test_case_id:** TC-007
- **requirement_ids:** REQ-005
- **risk_ids:** RISK-002
- **title:** Loyalty bonus and 20% cap
- **objective:** Bonus adds 5 points; cap at 20%
- **preconditions:** Customer is a loyalty member
- **test_data:** 750.00 member; 2000.00 member
- **steps:** 1. final_price(750.00, True)
2. final_price(2000.00, True)
- **expected_result:** 637.50 and 1600.00
- **test_level:** unit
- **test_type:** functional
- **design_technique:** decision table
- **automation_status:** AUTOMATED
- **priority:** HIGH

### TC-008

- **test_case_id:** TC-008
- **requirement_ids:** REQ-006
- **risk_ids:** RISK-003
- **title:** Negative rejected, zero allowed
- **objective:** Input validation
- **preconditions:** None
- **test_data:** -0.01; 0.00
- **steps:** 1. final_price(-0.01)
2. final_price(0.00)
- **expected_result:** ValueError; 0.00
- **test_level:** unit
- **test_type:** negative
- **design_technique:** error guessing
- **automation_status:** AUTOMATED
- **priority:** MEDIUM

### TC-009

- **test_case_id:** TC-009
- **requirement_ids:** REQ-007
- **risk_ids:** RISK-004
- **title:** Half-up rounding to cents
- **objective:** Rounding mode
- **preconditions:** None
- **test_data:** 100.10 (95.095 before rounding)
- **steps:** 1. final_price(100.10)
- **expected_result:** 95.10
- **test_level:** unit
- **test_type:** functional
- **design_technique:** error guessing
- **automation_status:** AUTOMATED
- **priority:** MEDIUM

### TC-010

- **test_case_id:** TC-010
- **requirement_ids:** REQ-001;REQ-002;REQ-003;REQ-004
- **risk_ids:** RISK-001
- **title:** Existing suite: one value per tier
- **objective:** Representative partition per tier
- **preconditions:** None
- **test_data:** 50.00; 250.00; 750.00; 2000.00
- **steps:** 1. Run tests/test_pricing.py
- **expected_result:** 50.00; 237.50; 675.00; 1700.00
- **test_level:** unit
- **test_type:** functional
- **design_technique:** equivalence partitioning
- **automation_status:** AUTOMATED
- **priority:** HIGH
