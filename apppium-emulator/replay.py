from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
import json
import time


options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "com.saucelabs.mydemoapp.android"
options.app_activity = ".view.activities.SplashActivity"
options.automation_name = "UiAutomator2"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

with open("record.json") as f:
    actions = json.load(f)

replay_results = []

def find_element(step):
    try:
        if step.get("resource_id") and step["resource_id"] != "null":
            return driver.find_element(AppiumBy.ID, step["resource_id"])

        if step.get("content_desc"):
            return driver.find_element(
                AppiumBy.ACCESSIBILITY_ID,
                step["content_desc"]
            )

        if step.get("text"):
            return driver.find_element(
                AppiumBy.XPATH,
                f"//*[@text='{step['text']}']"
            )

    except:
        return None

    return None

for step in actions:
    result = {
        "step": step,
        "status": "",
        "method": "",
        "error": None
    }

    try:
        el = find_element(step)

        if el:
            el.click()
            print("Clicked:", step.get("text"))

            result["status"] = "success"
            result["method"] = "element"

        else:
            bounds = step.get("bounds")

            if bounds:
                x = bounds["x"] + bounds["width"] // 2
                y = bounds["y"] + bounds["height"] // 2

                driver.execute_script("mobile: clickGesture", {
                    "x": x,
                    "y": y
                })

                print(f"Clicked by coordinates: ({x},{y})")

                result["status"] = "success"
                result["method"] = "coordinates"

            else:
                print("No locator found")
                result["status"] = "failed"
                result["error"] = "No locator"

        time.sleep(1)

    except Exception as e:
        print("Failed:", step, e)
        result["status"] = "failed"
        result["error"] = str(e)

    replay_results.append(result)

with open("replay.json", "w") as f:
    json.dump(replay_results, f, indent=4)

print("Replay results saved to replay.json")
driver.quit()