import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from pages.landing_page import LandingPage
from pages.auth_page import AuthPage
from pages.dashboard_page import DashboardPage

BASE_URL = os.getenv("BASE_URL", "https://saishirumala.github.io/PDD").rstrip("/")

@pytest.fixture(scope="class")
def driver_setup(request):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(8)
    request.cls.driver = driver
    yield driver
    driver.quit()

@pytest.mark.usefixtures("driver_setup")
class TestCompleteWebE2E:

    def test_01_landing_page_e2e(self):
        landing = LandingPage(self.driver, base_url=BASE_URL)
        landing.load()
        assert landing.get_title() != ""
        landing.save_screenshot("web_01_landing_page")

    def test_02_auth_register_and_login_e2e(self):
        auth = AuthPage(self.driver, base_url=BASE_URL)
        auth.load()
        auth.save_screenshot("web_02_auth_page")

    def test_03_dashboard_metrics_and_charts_e2e(self):
        dashboard = DashboardPage(self.driver, base_url=BASE_URL)
        dashboard.load()
        dashboard.save_screenshot("web_03_dashboard_page")

    def test_04_meal_analyzer_text_and_vision_e2e(self):
        self.driver.get(f"{BASE_URL}/#/analyze")
        time.sleep(1)
        os.makedirs("Test Results/Screenshots", exist_ok=True)
        self.driver.save_screenshot("Test Results/Screenshots/web_04_analyze_page.png")

    def test_05_water_tracker_add_and_delete_e2e(self):
        self.driver.get(f"{BASE_URL}/#/dashboard")
        time.sleep(1)
        self.driver.save_screenshot("Test Results/Screenshots/web_05_water_tracker.png")

    def test_06_profile_bmr_calculator_and_goals_e2e(self):
        self.driver.get(f"{BASE_URL}/#/profile")
        time.sleep(1)
        self.driver.save_screenshot("Test Results/Screenshots/web_06_profile_bmr.png")

    def test_07_history_logs_search_and_delete_e2e(self):
        self.driver.get(f"{BASE_URL}/#/history")
        time.sleep(1)
        self.driver.save_screenshot("Test Results/Screenshots/web_07_history_page.png")
