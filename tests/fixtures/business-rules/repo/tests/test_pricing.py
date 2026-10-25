import unittest
from decimal import Decimal

from pricing import final_price


class FinalPriceTest(unittest.TestCase):
    def test_small_order_has_no_discount(self):
        self.assertEqual(final_price(Decimal("50.00")), Decimal("50.00"))

    def test_medium_order_gets_five_percent(self):
        self.assertEqual(final_price(Decimal("250.00")), Decimal("237.50"))

    def test_large_order_gets_ten_percent(self):
        self.assertEqual(final_price(Decimal("750.00")), Decimal("675.00"))

    def test_very_large_order_gets_fifteen_percent(self):
        self.assertEqual(final_price(Decimal("2000.00")), Decimal("1700.00"))


if __name__ == "__main__":
    unittest.main()
