import unittest

from accounts import Accounts


class AccountsTest(unittest.TestCase):
    def test_register_and_login(self):
        accounts = Accounts()
        accounts.register("dana", "correct-horse")
        self.assertTrue(accounts.login("dana", "correct-horse"))


if __name__ == "__main__":
    unittest.main()
