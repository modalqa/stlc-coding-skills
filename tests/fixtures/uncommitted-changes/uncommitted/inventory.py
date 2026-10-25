"""Inventory helpers."""


class InsufficientStock(Exception):
    pass


class Inventory:
    def __init__(self) -> None:
        self.stock: dict[str, int] = {}
        self.reserved: dict[str, int] = {}  # WIP(dev): reservations, not finished yet

    def add_stock(self, sku: str, qty: int) -> None:
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("qty must be a positive integer")
        self.stock[sku] = self.stock.get(sku, 0) + qty

    def remove_stock(self, sku: str, qty: int) -> None:
        available = self.stock.get(sku, 0)
        if qty > available:
            raise InsufficientStock(sku)
        self.stock[sku] = available - qty

    def reserve(self, sku: str, qty: int) -> None:
        # WIP(dev): still need to subtract existing reservations from availability
        if qty > self.stock.get(sku, 0):
            raise InsufficientStock(sku)
        self.reserved[sku] = self.reserved.get(sku, 0) + qty
