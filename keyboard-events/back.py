import subprocess
import json
import time
import sys

actions = []
last_event_time = 0
DEBOUNCE = 0.3


def start_logcat():
    return subprocess.Popen(
        ["adb", "logcat", "-v", "brief"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )


def is_back_event(line):
    return (
        "KeyEvent" in line and
        "KEYCODE_BACK" in line and
        "DOWN" in line
    )


def save_and_exit(process):
    print("\nSaving...")

    with open("back.json", "w") as f:
        json.dump(actions, f, indent=4)

    process.kill()
    sys.exit(0)


def run():
    global last_event_time

    process = start_logcat()

    print("BACK button...\n")

    try:
        for line in process.stdout:

            now = time.time()

            if now - last_event_time < DEBOUNCE:
                continue

            if is_back_event(line):
                print("BACK pressed")

                actions.append({
                    "type": "system",
                    "action": "back",
                    "time": round(now, 2)
                })

                last_event_time = now

    except KeyboardInterrupt:
        save_and_exit(process)


if __name__ == "__main__":
    run()