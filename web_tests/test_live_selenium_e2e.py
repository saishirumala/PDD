import os
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from pages.landing_page import LandingPage
from pages.auth_page import AuthPage
from pages.dashboard_page import DashboardPage

BASE_URL = os.getenv("BASE_URL", "https://saishirumala.github.io/PDD").rstrip("/")

@pytest.fixture(scope="class")
def driver_init(request):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(10)
    request.cls.driver = driver
    yield driver
    driver.quit()

@pytest.mark.usefixtures("driver_init")
class TestLiveSeleniumE2E:

    def test_01_verify_live_url_availability(self):
        """Verifies that the deployed GitHub Pages URL returns HTTP 200"""
        response = requests.get(BASE_URL, timeout=15)
        assert response.status_code == 200, f"Deployed URL {BASE_URL} returned status code {response.status_code}"

    def test_02_landing_page_title_and_elements(self):
        """Tests that the live landing page loads and title/elements render correctly"""
        landing = LandingPage(self.driver, base_url=BASE_URL)
        landing.load()
        assert landing.get_title() != ""
        landing.save_screenshot("test_02_landing_page")

    def test_03_auth_page_navigation(self):
        """Tests live navigation to the Auth page"""
        auth = AuthPage(self.driver, base_url=BASE_URL)
        auth.load()
        auth.save_screenshot("test_03_auth_page")

    def test_04_dashboard_page_navigation(self):
        """Tests live navigation to the Dashboard page"""
        dashboard = DashboardPage(self.driver, base_url=BASE_URL)
        dashboard.load()
        dashboard.save_screenshot("test_04_dashboard_page")
