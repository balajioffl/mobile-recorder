from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time

options = UiAutomator2Options()

options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "com.swaglabsmobileapp"
options.app_activity = ".MainActivity"
options.automation_name = "UiAutomator2"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

time.sleep(5)

try:
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()
    time.sleep(2)

except:
    pass

# Username
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Username").send_keys("standard_user")

# Password
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-Password").send_keys("secret_sauce")

time.sleep(1)

# Login
driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-LOGIN").click()

time.sleep(5)

# Validation
try:
    driver.find_element(AppiumBy.ACCESSIBILITY_ID, "test-PRODUCTS")
    print("Test Passed")

except:
    print("Test Failed")

driver.quit()
