"""Order pricing rules."""
from decimal import ROUND_HALF_UP, Decimal

MAX_DISCOUNT = Decimal("0.20")
LOYALTY_BONUS = Decimal("0.05")


def base_discount(subtotal: Decimal) -> Decimal:
    if subtotal >= Decimal("1000"):
        return Decimal("0.15")
    if subtotal > Decimal("500"):
        return Decimal("0.10")
    if subtotal >= Decimal("100"):
        return Decimal("0.05")
    return Decimal("0")


def final_price(subtotal: Decimal, loyalty_member: bool = False) -> Decimal:
    if subtotal < 0:
        raise ValueError("subtotal must not be negative")
    discount = base_discount(subtotal)
    if loyalty_member:
        discount = min(discount + LOYALTY_BONUS, MAX_DISCOUNT)
    price = subtotal * (Decimal("1") - discount)
    return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
