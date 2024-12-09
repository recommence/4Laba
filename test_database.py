import unittest
from db import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(':memory:')  # Use in-memory database
        self.db.init_db()  # Ensure the database is initialized before each test

    def tearDown(self):
        self.db.disconnect()

    def test_add_user(self):
        user_id = self.db.add_user('Said Nabiev', 'said@example.com')
        self.assertIsNotNone(user_id)

    def test_get_user(self):
        user_id = self.db.add_user('Mark Cucumber', 'markich@example.com')
        user = self.db.get_user(user_id)
        self.assertEqual(user[1], 'Mark Cucumber')
        self.assertEqual(user[2], 'markich@example.com')

    def test_update_user(self):
        user_id = self.db.add_user('Bob Smith', 'bob@example.com')
        self.db.update_user(user_id, 'Robert Smith', 'robert@example.com')
        user = self.db.get_user(user_id)
        self.assertEqual(user[1], 'Robert Smith')
        self.assertEqual(user[2], 'robert@example.com')

    def test_delete_user(self):
        user_id = self.db.add_user('Alice Johnson', 'alice@example.com')
        self.db.delete_user(user_id)
        user = self.db.get_user(user_id)
        self.assertIsNone(user)

    def test_add_multiple_users(self):
        user1_id = self.db.add_user('User1', 'user1@example.com')
        user2_id = self.db.add_user('User2', 'user2@example.com')
        self.assertNotEqual(user1_id, user2_id)

    def test_get_nonexistent_user(self):
        user = self.db.get_user(999)
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()
