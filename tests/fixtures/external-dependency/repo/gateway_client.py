"""Thin HTTP client for the payment gateway sandbox."""
import json
import os
import urllib.request

from checkout import GatewayTimeout, PaymentDeclined


class HttpGateway:
    def __init__(self, base_url: str | None = None, timeout: float = 3.0) -> None:
        self.base_url = base_url or os.environ.get("PAYMENT_GATEWAY_URL", "https://payments-sandbox.example.invalid")
        self.timeout = timeout

    def charge(self, amount: str, idempotency_key: str) -> str:
        body = json.dumps({"amount": amount}).encode()
        request = urllib.request.Request(f"{self.base_url}/charges", data=body, method="POST",
                                         headers={"Idempotency-Key": idempotency_key,
                                                  "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.load(response)
        except TimeoutError as exc:
            raise GatewayTimeout(str(exc)) from exc
        if payload.get("status") == "declined":
            raise PaymentDeclined(payload.get("reason", ""))
        return payload["transaction_id"]
