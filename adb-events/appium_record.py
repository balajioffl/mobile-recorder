from appium import webdriver
from appium.options.android import UiAutomator2Options
import json
import time
import signal
import sys

actions = []
last_element = None

options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.app_package = "com.saucelabs.mydemoapp.android"
options.app_activity = ".view.activities.SplashActivity"
options.automation_name = "UiAutomator2"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

print("Data recording started... (Ctrl+C to stop)\n")


def save_and_exit(sig=None, frame=None):
    print("Saving actions...")

    with open("record.json", "w") as f:
        json.dump(actions, f, indent=4)

    print("Saved full JSON")
    sys.exit(0)


signal.signal(signal.SIGINT, save_and_exit)


def get_full_element_data(el):
    try:
        return {
            "action": "interact",
            "text": el.text,
            "resource_id": el.get_attribute("resourceId"),
            "class": el.get_attribute("className"),
            "package": el.get_attribute("package"),
            "content_desc": el.get_attribute("contentDescription"),
            "enabled": el.get_attribute("enabled"),
            "clickable": el.get_attribute("clickable"),
            "focusable": el.get_attribute("focusable"),
            "focused": el.get_attribute("focused"),
            "checkable": el.get_attribute("checkable"),
            "checked": el.get_attribute("checked"),
            "scrollable": el.get_attribute("scrollable"),
            "long_clickable": el.get_attribute("longClickable"),
            "password": el.get_attribute("password"),
            "selected": el.get_attribute("selected"),
            "bounds": el.rect
        }
    except:
        return None


while True:
    try:
        time.sleep(1)

        el = driver.switch_to.active_element
        rect = el.rect

        element_id = (
            el.get_attribute("resourceId"),
            el.get_attribute("className"),
            rect["x"],
            rect["y"],
            el.text
        )

        if element_id != last_element:
            data = get_full_element_data(el)

            if data:
                print("Recorded:", data)
                actions.append(data)

            last_element = element_id

    except KeyboardInterrupt:
        save_and_exit()

    except Exception:
        pass