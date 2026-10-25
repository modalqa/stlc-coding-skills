# Checkout Requirements

- AC-1: A successful charge marks the order PAID and stores the gateway transaction id.
- AC-2: A declined charge marks the order DECLINED; the customer is never charged twice.
- AC-3: A gateway timeout is retried at most 2 additional times with the same idempotency key. If all attempts time out, the order is left PENDING_PAYMENT and the error is reported to the caller as PaymentUnavailable.
- AC-4: The idempotency key is the order id.
