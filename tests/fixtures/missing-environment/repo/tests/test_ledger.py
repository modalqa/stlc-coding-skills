import unittest
from decimal import Decimal

from ledger import Ledger, connect


class LedgerTest(unittest.TestCase):
    def setUp(self):
        self.conn = connect()
        self.conn.execute("TRUNCATE entries, balances")
        self.ledger = Ledger(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_balance_is_sum_of_entries(self):
        self.ledger.record("acc-1", Decimal("10.00"))
        self.ledger.record("acc-1", Decimal("-2.50"))
        self.assertEqual(self.ledger.balance("acc-1"), Decimal("7.50"))

    def test_zero_amount_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.record("acc-1", Decimal("0"))


if __name__ == "__main__":
    unittest.main()
