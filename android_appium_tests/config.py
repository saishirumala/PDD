import os

APPIUM_SERVER_URL = os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723")
APK_PATH = os.getenv("APK_PATH", os.path.abspath("app-release.apk"))

ANDROID_CAPABILITIES = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:deviceName": "Android Emulator",
    "appium:app": APK_PATH,
    "appium:appPackage": "com.nutriguide.app",
    "appium:appActivity": ".MainActivity",
    "appium:autoGrantPermissions": True,
    "appium:newCommandTimeout": 300,
    "appium:noReset": False
}
