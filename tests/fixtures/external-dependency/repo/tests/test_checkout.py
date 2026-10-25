import unittest

from checkout import CheckoutService


class FakeGateway:
    def __init__(self, txn="txn-1"):
        self.txn = txn
        self.calls = []

    def charge(self, amount, idempotency_key):
        self.calls.append((amount, idempotency_key))
        return self.txn


class CheckoutTest(unittest.TestCase):
    def test_successful_charge_marks_order_paid(self):
        order = {"id": "o-1", "total": "10.00"}
        result = CheckoutService(FakeGateway()).checkout(order)
        self.assertEqual(result["status"], "PAID")
        self.assertEqual(result["transaction_id"], "txn-1")


if __name__ == "__main__":
    unittest.main()
