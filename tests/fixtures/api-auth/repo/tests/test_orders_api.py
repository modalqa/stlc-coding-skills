import unittest

from orders_api import handle


def req(method, path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return {"method": method, "path": path, "headers": headers}


class OrdersApiTest(unittest.TestCase):
    def test_owner_can_read_order(self):
        status, body = handle(req("GET", "/orders/1001", "tok-alice"))
        self.assertEqual(status, 200)
        self.assertEqual(body["owner"], "alice")

    def test_missing_token_is_rejected(self):
        status, _ = handle(req("GET", "/orders/1001"))
        self.assertEqual(status, 401)


if __name__ == "__main__":
    unittest.main()
