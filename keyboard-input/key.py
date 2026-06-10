import subprocess
import xml.etree.ElementTree as ET
import time
import json
import signal

actions = []
last_values = {}

current_buffer = ""
last_type_time = 0
PAUSE_THRESHOLD = 0.5
running = True


def stop_handler(signum, frame):
    global running
    running = False
    print("\nStopping...")


signal.signal(signal.SIGINT, stop_handler)


def dump_ui():
    subprocess.run(
        ["adb", "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    subprocess.run(
        ["adb", "pull", "/sdcard/ui.xml", "ui.xml"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def get_inputs():
    try:
        tree = ET.parse("ui.xml")
        root = tree.getroot()
    except:
        return []

    inputs = []

    for node in root.iter():
        if "EditText" in node.attrib.get("class", ""):
            inputs.append({
                "id": node.attrib.get("resource-id") or "input",
                "text": node.attrib.get("text") or ""
            })

    return inputs


def track_inputs():
    global last_values, current_buffer, last_type_time

    inputs = get_inputs()

    for el in inputs:
        key = el["id"]
        current = el["text"]

        if key not in last_values:
            last_values[key] = current
            continue

        previous = last_values[key]

        if current.startswith(previous):
            new_text = current[len(previous):]
        else:
            new_text = current

        if new_text.strip():
            current_buffer += new_text
            last_type_time = time.time()

        last_values[key] = current


def flush_buffer():
    global current_buffer

    if current_buffer.strip():
        print(f"\nTyped → {current_buffer.strip()}")

        actions.append({
            "type": "input",
            "text": current_buffer.strip(),
            "time": round(time.time(), 2)
        })

        current_buffer = ""


def run():
    global last_type_time

    print("Recording...\n")

    while running:
        dump_ui()
        track_inputs()

        if time.time() - last_type_time > PAUSE_THRESHOLD:
            flush_buffer()

        time.sleep(0.2)

    flush_buffer()

    print("\nSaving...")

    with open("text.json", "w") as f:
        json.dump(actions, f, indent=4)

    print("Done")


if __name__ == "__main__":
    run()