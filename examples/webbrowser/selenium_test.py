import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="run.log",
    filemode="a",
)
logger = logging.getLogger(__name__)

logger.info("Starting the scraping process")
driver = webdriver.Chrome()  # Make sure you have chromedriver installed and in PATH
driver.get("https://www.freelance.de/")


driver.quit()