import unittest

from gateway_client import HttpGateway


class GatewaySandboxTest(unittest.TestCase):
    """Requires network access to the payment sandbox."""

    def test_sandbox_charge_returns_transaction_id(self):
        txn = HttpGateway().charge(amount="1.00", idempotency_key="integration-smoke")
        self.assertTrue(txn)


if __name__ == "__main__":
    unittest.main()
