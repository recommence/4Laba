import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests
import time
import threading
from app import app
import logging

logging.basicConfig(level=logging.DEBUG)

class TestUserInterface(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://localhost:5000"
        cls.flask_thread = threading.Thread(target=cls.run_flask_app)
        cls.flask_thread.daemon = True
        cls.flask_thread.start()
        cls.wait_for_flask()

    @classmethod
    def tearDownClass(cls):
        try:
            requests.get(f"{cls.base_url}/shutdown")
        except requests.exceptions.ConnectionError:
            pass  # Expected as the server is shutting down
        cls.flask_thread.join(timeout=5)

    @classmethod
    def run_flask_app(cls):
        app.run(port=5000)

    @classmethod
    def wait_for_flask(cls):
        max_retries = 30
        for _ in range(max_retries):
            try:
                response = requests.get(f"{cls.base_url}/health")
                if response.status_code == 200:
                    return
            except requests.exceptions.ConnectionError:
                time.sleep(0.5)
        raise Exception("Flask app failed to start")

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.reset_database_for_tests()
        time.sleep(0.5)

    def tearDown(self):
        self.driver.quit()

    def reset_database_for_tests(self):
        response = requests.post(f"{self.base_url}/reset")
        response.raise_for_status()

    def test_add_user(self):
        data = {"name": "Selenium Test", "email": "selenium@test.com"}
        response = requests.post(f"{self.base_url}/user", json=data)
        logging.debug(f"Add user response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 201)
        user_id = response.json()['id']
        
        self.driver.get(f"{self.base_url}/user/{user_id}")
        name_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user-name"))
        )
        email_element = self.driver.find_element(By.ID, "user-email")

        self.assertIn("Selenium Test", name_element.text)
        self.assertIn("selenium@test.com", email_element.text)

    def test_user_not_found(self):
        self.driver.get(f"{self.base_url}/user/9999")
        try:
            error_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "error-message"))
            )
            self.assertEqual(error_element.text, "User not found")
        except TimeoutException:
            logging.error("Error message element not found")
            self.fail("Error message element not found")

    def test_add_multiple_users(self):
        for i in range(3):
            data = {"name": f"User {i}", "email": f"user{i}@test.com"}
            response = requests.post(f"{self.base_url}/user", json=data)
            logging.debug(f"Add user {i} response: {response.status_code}, {response.text}")
            self.assertEqual(response.status_code, 201)

        response = requests.get(f"{self.base_url}/users")
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertEqual(len(users), 3)

    def test_add_duplicate_user(self):
        data = {"name": "First User", "email": "duplicate@test.com"}
        response = requests.post(f"{self.base_url}/user", json=data)
        logging.debug(f"Add first user response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 201)

        data = {"name": "Second User", "email": "duplicate@test.com"}
        response = requests.post(f"{self.base_url}/user", json=data)
        logging.debug(f"Add duplicate user response: {response.status_code}, {response.text}")
        self.assertEqual(response.status_code, 400)
        self.assertIn("User with this email already exists", response.json()['error'])

if __name__ == "__main__":
    unittest.main()

