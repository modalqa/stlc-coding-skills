import unittest

from todos import TodoStore


class TodoStoreTest(unittest.TestCase):
    def test_create_and_list(self):
        store = TodoStore()
        store.create("Buy milk")
        store.create("Walk dog")
        self.assertEqual([t.title for t in store.list()], ["Buy milk", "Walk dog"])

    def test_new_todo_is_not_completed(self):
        self.assertFalse(TodoStore().create("x").completed)


if __name__ == "__main__":
    unittest.main()
