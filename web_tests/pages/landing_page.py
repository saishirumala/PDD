from selenium.webdriver.common.by import By
from .base_page import BasePage

class LandingPage(BasePage):
    HERO_TITLE = (By.TAG_NAME, "h1")
    ANALYZE_BTN = (By.XPATH, "//a[contains(@href, 'analyze') or contains(text(), 'Analyze')]")
    GET_STARTED_BTN = (By.XPATH, "//a[contains(text(), 'Get Started') or contains(@href, 'auth')]")

    def load(self):
        self.navigate_to("/")

    def get_hero_text(self):
        return self.find_element(*self.HERO_TITLE).text
