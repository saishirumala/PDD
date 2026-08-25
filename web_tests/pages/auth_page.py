from selenium.webdriver.common.by import By
from .base_page import BasePage

class AuthPage(BasePage):
    EMAIL_INPUT = (By.XPATH, "//input[@type='email']")
    PASSWORD_INPUT = (By.XPATH, "//input[@type='password']")
    SUBMIT_BTN = (By.XPATH, "//button[@type='submit']")

    def load(self):
        self.navigate_to("/auth")

    def login(self, email, password):
        self.type_text(*self.EMAIL_INPUT, email)
        self.type_text(*self.PASSWORD_INPUT, password)
        self.click(*self.SUBMIT_BTN)
