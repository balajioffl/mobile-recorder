import subprocess
import json
import signal
import sys
import re
import time

actions = []

def get_screen_size():
    output = subprocess.check_output("adb shell wm size", shell=True).decode()
    match = re.search(r'(\d+)x(\d+)', output)
    return int(match.group(1)), int(match.group(2))

SCREEN_W, SCREEN_H = get_screen_size()
RAW_MAX = 32767

def scale(val, max_screen):
    return int((val / RAW_MAX) * max_screen)

print("ADB Recorder Started (Ctrl+C to stop)\n")

proc = subprocess.Popen(
    ["adb", "shell", "getevent", "-lt"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

start_x = start_y = None
end_x = end_y = None
touch_start_time = None

def save_and_exit(sig=None, frame=None):
    print("\nSaving...")
    with open("record.json", "w") as f:
        json.dump(actions, f, indent=4)
    proc.kill()
    print("Saved record.json")
    sys.exit(0)

signal.signal(signal.SIGINT, save_and_exit)

try:
    for line in proc.stdout:

        if "ABS_MT_POSITION_X" in line:
            raw = int(line.strip().split()[-1], 16)
            x = scale(raw, SCREEN_W)
            if start_x is None:
                start_x = x
            end_x = x

        if "ABS_MT_POSITION_Y" in line:
            raw = int(line.strip().split()[-1], 16)
            y = scale(raw, SCREEN_H)
            if start_y is None:
                start_y = y
            end_y = y

        if "ABS_MT_TRACKING_ID" in line:

            if "ffffffff" not in line:
                touch_start_time = time.time()
                start_x = start_y = end_x = end_y = None

            else:
                if start_x is not None and start_y is not None:

                    duration = time.time() - touch_start_time
                    dx = abs(end_x - start_x)
                    dy = abs(end_y - start_y)

                    if dx < 10 and dy < 10:
                        if duration > 0.7:
                            action = {
                                "action": "long_press",
                                "x": start_x,
                                "y": start_y,
                                "duration": round(duration, 2)
                            }
                            print("LONG PRESS:", action)
                        else:
                            action = {
                                "action": "tap",
                                "x": start_x,
                                "y": start_y
                            }
                            print("TAP:", action)

                    else:
                        action = {
                            "action": "swipe",
                            "start": {"x": start_x, "y": start_y},
                            "end": {"x": end_x, "y": end_y}
                        }
                        print("SWIPE:", action)

                    actions.append(action)

except Exception as e:
    print("Error:", e)
    save_and_exit()