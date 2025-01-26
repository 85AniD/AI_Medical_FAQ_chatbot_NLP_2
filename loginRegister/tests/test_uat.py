from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Test user registration and login
def test_user_registration_and_login():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000/register")

    # Register a new user
    driver.find_element(By.NAME, "name").send_keys("Test User")
    driver.find_element(By.NAME, "email").send_keys("test@example.com")
    driver.find_element(By.NAME, "password").send_keys("Qaz_123")
    driver.find_element(By.NAME, "confirm-password").send_keys("Qaz_123")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    # Login with the new user
    driver.get("http://localhost:5000/login")
    driver.find_element(By.NAME, "email").send_keys("test@example.com")
    driver.find_element(By.NAME, "password").send_keys("Qaz_123")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    # Verify login success
    assert "index" in driver.current_url
    driver.quit()