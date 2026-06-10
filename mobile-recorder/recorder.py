import subprocess
import json
import time
import os
import xml.etree.ElementTree as ET

actions = []

def start_adb():
    return subprocess.Popen(
        "adb shell getevent -lt",
        shell=True,
        stdout=subprocess.PIPE,
        text=True
    )

def hex_to_dec(v):
    return int(v, 16)


def dump_ui():
    os.system("adb shell uiautomator dump /sdcard/ui.xml > /dev/null 2>&1")
    time.sleep(0.3)
    os.system("adb pull /sdcard/ui.xml ui.xml > /dev/null 2>&1")


def find_element(x, y):
    try:
        tree = ET.parse("ui.xml")
        root = tree.getroot()
    except:
        return None

    best_match = None
    smallest_area = float("inf")

    for node in root.iter():
        bounds = node.attrib.get("bounds")
        if not bounds:
            continue

        coords = bounds.replace("[", "").replace("]", ",").split(",")
        x1, y1, x2, y2 = map(int, coords[:4])

        if x1 <= x <= x2 and y1 <= y <= y2:
            area = (x2 - x1) * (y2 - y1)

            if area < smallest_area:
                smallest_area = area
                best_match = {
                    "text": node.attrib.get("text"),
                    "id": node.attrib.get("resource-id"),
                    "class": node.attrib.get("class"),
                    "bounds": bounds
                }

    return best_match


points = []
last_time = None

def process_gesture():
    global points

    if not points:
        return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    movement = max(max(xs) - min(xs), max(ys) - min(ys))

    if movement < 30:
        x, y = points[-1]

        print(f"\n tap at ({x},{y})")

        dump_ui()
        element = find_element(x, y)

        print("element:", element)

        actions.append({
            "type": "tap",
            "x": x,
            "y": y,
            "element": element
        })

    else:
        start = points[0]
        end = points[-1]

        print(f"\n swipe → {start} → {end}")

        actions.append({
            "type": "swipe",
            "start": list(start),
            "end": list(end)
        })

    points.clear()

def run():
    global last_time

    process = start_adb()

    print("Recording taps . . .\n")

    x = None
    y = None

    try:
        for line in process.stdout:

            if "ABS_MT_POSITION_X" in line:
                x = hex_to_dec(line.strip().split()[-1])

            elif "ABS_MT_POSITION_Y" in line:
                y = hex_to_dec(line.strip().split()[-1])

                if x is not None:
                    points.append((x, y))
                    last_time = time.time()
                    x, y = None, None

            if last_time and time.time() - last_time > 0.1:
                process_gesture()
                last_time = None

    except KeyboardInterrupt:
        print("\nSaving...")

        with open("steps.json", "w") as f:
            json.dump(actions, f, indent=4)

        process.kill()


if __name__ == "__main__":
    run()