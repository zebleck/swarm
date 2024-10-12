import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Set up the Selenium driver (ensure you have the appropriate WebDriver installed, e.g., ChromeDriver)
driver = (
    webdriver.Chrome()
)  # You can replace Chrome with any other browser driver you use


def login():
    # Navigate to the login URL
    driver.get("http://localhost:4280/.auth/login/aadb")

    # Wait for the page to load (you might need to adjust the sleep duration or use WebDriverWait for a specific element)
    time.sleep(2)

    # Type the user ID into the input field
    user_id_input = driver.find_element(By.ID, "userId")
    user_id_input.clear()
    user_id_input.send_keys("fd38d44f-99ab-45d3-90ca-85bb27292fa9")

    # Type the username into the input field
    username_input = driver.find_element(By.ID, "userDetails")
    username_input.clear()
    username_input.send_keys("zebleck")

    # Submit the form
    submit_button = driver.find_element(By.ID, "submit")
    submit_button.click()

    # Wait for the login process to complete and redirect

    # Navigate back to the desired URL
    driver.get("http://localhost:3000")
    time.sleep(10)  # Adjust this as needed

    # Close the browser
    driver.quit()


if __name__ == "__main__":
    login()
