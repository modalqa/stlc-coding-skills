# Order Pricing Rules

Acceptance criteria:

- AC-1: Orders with a subtotal below 100.00 receive no discount.
- AC-2: Subtotals from 100.00 up to and including 499.99 receive a 5% discount.
- AC-3: Subtotals from 500.00 up to and including 999.99 receive a 10% discount.
- AC-4: Subtotals of 1000.00 or more receive a 15% discount.
- AC-5: Loyalty members receive an additional 5 percentage points of discount; the total discount is capped at 20%.
- AC-6: A negative subtotal is rejected with a ValueError. A subtotal of 0.00 is valid and costs 0.00.
- AC-7: The final price is rounded half-up to 2 decimal places.
