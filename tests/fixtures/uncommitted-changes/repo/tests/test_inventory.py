import unittest

from inventory import Inventory


class InventoryTest(unittest.TestCase):
    def test_add_then_remove(self):
        inv = Inventory()
        inv.add_stock("sku-1", 5)
        inv.remove_stock("sku-1", 2)
        self.assertEqual(inv.stock["sku-1"], 3)


if __name__ == "__main__":
    unittest.main()
