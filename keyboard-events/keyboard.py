import xml.etree.ElementTree as ET
import time
import json
import os

actions = []
last_values = {}


def dump_ui():
    os.system("adb shell uiautomator dump /sdcard/ui.xml > /dev/null 2>&1")
    os.system("adb pull /sdcard/ui.xml ui.xml > /dev/null 2>&1")

def get_inputs():
    try:
        tree = ET.parse("ui.xml")
        root = tree.getroot()
    except:
        return []

    inputs = []

    for node in root.iter():
        cls = node.attrib.get("class", "")

        if "EditText" in cls:
            inputs.append({
                "id": node.attrib.get("resource-id"),
                "text": node.attrib.get("text"),
                "class": cls
            })

    return inputs


def track_inputs():
    global last_values

    inputs = get_inputs()

    for el in inputs:
        key = el["id"] or el["class"]
        current = el["text"]

        if key not in last_values:
            last_values[key] = current

        if current != last_values[key]:
            print(f"text → {current}")

            actions.append({
                "type": "input",
                "id": key,
                "text": current
            })

            last_values[key] = current


print("Recording text (ADB mode)... Ctrl+C to stop\n")

try:
    while True:
        dump_ui()
        track_inputs()
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nSaving...")

    with open("keyboard.json", "w") as f:
        json.dump(actions, f, indent=4)