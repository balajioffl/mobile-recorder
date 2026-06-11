import subprocess
import json
import time

actions = []

def add_action(event_type):
    action = {
        "type": event_type,
        "time": round(time.time(), 2)
    }
    actions.append(action)
    print(action)


def save_to_file(filename="button.json"):
    with open(filename, "w") as f:
        json.dump(actions, f, indent=4)
    print(f"\nSaved to {filename}")


def listen_buttons():
    print("Listening for buttons ...")

    process = subprocess.Popen(
        ["adb", "shell", "getevent", "-l"],
        stdout=subprocess.PIPE,
        text=True
    )

    try:
        for line in process.stdout:

            if "KEY_VOLUMEUP" in line and "DOWN" in line:
                add_action("volume_up")

            elif "KEY_VOLUMEDOWN" in line and "DOWN" in line:
                add_action("volume_down")

            elif "KEY_POWER" in line and "DOWN" in line:
                add_action("power_button")

    except KeyboardInterrupt:
        print("\nStopping ...")
        save_to_file()


if __name__ == "__main__":
    listen_buttons()