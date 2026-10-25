"""Boundary, negative and rounding tests for pricing rules (STLC run, TC-001..TC-009)."""
import unittest
from decimal import Decimal

from pricing import final_price


class PricingBoundaryTest(unittest.TestCase):
    def test_tc001_just_below_100_has_no_discount(self):
        self.assertEqual(final_price(Decimal("99.99")), Decimal("99.99"))

    def test_tc002_exactly_100_gets_five_percent(self):
        self.assertEqual(final_price(Decimal("100.00")), Decimal("95.00"))

    def test_tc003_upper_edge_of_five_percent_tier(self):
        self.assertEqual(final_price(Decimal("499.99")), Decimal("474.99"))

    def test_tc004_exactly_500_gets_ten_percent(self):
        self.assertEqual(final_price(Decimal("500.00")), Decimal("450.00"))

    def test_tc005_upper_edge_of_ten_percent_tier(self):
        self.assertEqual(final_price(Decimal("999.99")), Decimal("899.99"))

    def test_tc006_exactly_1000_gets_fifteen_percent(self):
        self.assertEqual(final_price(Decimal("1000.00")), Decimal("850.00"))

    def test_tc007_loyalty_bonus_and_cap(self):
        self.assertEqual(final_price(Decimal("750.00"), loyalty_member=True), Decimal("637.50"))
        self.assertEqual(final_price(Decimal("2000.00"), loyalty_member=True), Decimal("1600.00"))

    def test_tc008_negative_rejected_zero_allowed(self):
        with self.assertRaises(ValueError):
            final_price(Decimal("-0.01"))
        self.assertEqual(final_price(Decimal("0.00")), Decimal("0.00"))

    def test_tc009_rounds_half_up_to_cents(self):
        # 100.10 * 0.95 = 95.095 -> 95.10 with ROUND_HALF_UP
        self.assertEqual(final_price(Decimal("100.10")), Decimal("95.10"))


if __name__ == "__main__":
    unittest.main()
