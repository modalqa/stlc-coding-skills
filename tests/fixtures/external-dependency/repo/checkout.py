"""Checkout flow that charges orders via a payment gateway."""


class GatewayTimeout(Exception):
    pass


class PaymentDeclined(Exception):
    pass


class PaymentUnavailable(Exception):
    pass


class CheckoutService:
    def __init__(self, gateway, max_retries: int = 2) -> None:
        self.gateway = gateway
        self.max_retries = max_retries

    def checkout(self, order: dict) -> dict:
        attempts = 0
        while True:
            attempts += 1
            try:
                txn = self.gateway.charge(amount=order["total"], idempotency_key=f"{order['id']}-{attempts}")
            except PaymentDeclined:
                order["status"] = "DECLINED"
                return order
            except GatewayTimeout:
                if attempts > self.max_retries:
                    order["status"] = "FAILED"
                    raise PaymentUnavailable(order["id"]) from None
                continue
            order["status"] = "PAID"
            order["transaction_id"] = txn
            return order
