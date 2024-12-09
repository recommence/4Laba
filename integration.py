import unittest
from db import Database
import os
import time

class TestDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        self.db_name = 'test_integration.db'
        self.db = Database(self.db_name)
        self.db.init_db()

    def tearDown(self):
        self.db.disconnect()
        time.sleep(0.1)  # ????????? ????????? ???????? ????? ????????? ?????
        if os.path.exists(self.db_name):
            try:
                os.remove(self.db_name)
            except PermissionError:
                print(f"Warning: Could not delete {self.db_name}. It may be in use.")

    def test_persistence(self):
        user_id = self.db.add_user('Test User', 'test@example.com')
        self.db.disconnect()

        new_db = Database(self.db_name)
        user = new_db.get_user(user_id)
        self.assertEqual(user[1], 'Test User')
        self.assertEqual(user[2], 'test@example.com')
        new_db.disconnect()

    def test_multiple_connections(self):
        user_id = self.db.add_user('Connection Test', 'connection@example.com')

        second_connection = Database(self.db_name)
        user = second_connection.get_user(user_id)
        self.assertEqual(user[1], 'Connection Test')
        self.assertEqual(user[2], 'connection@example.com')
        second_connection.disconnect()

    def test_large_data(self):
        for i in range(1000):
            self.db.add_user(f'User{i}', f'user{i}@example.com')
        self.db.disconnect()

        new_db = Database(self.db_name)
        for i in range(1000):
            user = new_db.get_user(i + 1)
            self.assertEqual(user[1], f'User{i}')
            self.assertEqual(user[2], f'user{i}@example.com')
        new_db.disconnect()

if __name__ == '__main__':
    unittest.main()

