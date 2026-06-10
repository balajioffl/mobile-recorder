from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time

options = UiAutomator2Options()

options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "io.appium.android.apis"
options.app_activity = ".ApiDemos"
options.automation_name = "UiAutomator2"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

time.sleep(5)

driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Accessibility").click()

time.sleep(2)

driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Accessibility Node Querying").click()

time.sleep(3)

print("Test Passed")

driver.quit()
