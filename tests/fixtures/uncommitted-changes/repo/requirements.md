# Inventory Requirements

- AC-1: `add_stock(sku, qty)` increases stock; qty must be a positive integer.
- AC-2: `remove_stock(sku, qty)` decreases stock; removing more than available raises InsufficientStock and leaves stock unchanged.
- AC-3: `reserve(sku, qty)` (in progress) holds stock for an order without removing it.
