from selenium import webdriver
import time
from selenium.webdriver.common.by import By

def test_chatbot_usability():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5000")

    # Test chatbot interaction
    driver.find_element(By.NAME, "message").send_keys("What are the symptoms of COVID-19?")
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    # Verify response
    response = driver.find_element(By.CLASS_NAME, "chatbot-response").text
    assert "symptoms" in response.lower()
    driver.quit()