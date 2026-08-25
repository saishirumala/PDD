import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver, base_url="https://saishirumala.github.io/PDD"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def navigate_to(self, path=""):
        target_url = f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(target_url)

    def find_element(self, by, value, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def click(self, by, value, timeout=10):
        element = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()

    def type_text(self, by, value, text, timeout=10):
        element = self.find_element(by, value, timeout)
        element.clear()
        element.send_keys(text)

    def get_title(self):
        return self.driver.title

    def save_screenshot(self, name):
        os.makedirs("Test Results/Screenshots", exist_ok=True)
        path = os.path.join("Test Results/Screenshots", f"{name}.png")
        self.driver.save_screenshot(path)
        return path
