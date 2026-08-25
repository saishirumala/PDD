from selenium.webdriver.common.by import By
from .base_page import BasePage

class DashboardPage(BasePage):
    DASHBOARD_TITLE = (By.TAG_NAME, "h1")
    CALORIES_CARD = (By.XPATH, "//*[contains(text(), 'Calorie Tracking') or contains(text(), 'Calories')]")

    def load(self):
        self.navigate_to("/dashboard")

    def get_header_text(self):
        return self.find_element(*self.DASHBOARD_TITLE).text
