# Checkout Service

Charges orders through an external payment gateway client.

Run the unit tests: `python3 -m unittest discover -s tests -t .`

`tests/test_gateway_integration.py` talks to the payment sandbox at `PAYMENT_GATEWAY_URL` (default `https://payments-sandbox.example.invalid`).
