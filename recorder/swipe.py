import subprocess
import json
import time

actions = []

def hex_to_dec(v):
    return int(v, 16)

process = subprocess.Popen(
    "adb shell getevent -lt",
    shell=True,
    stdout=subprocess.PIPE,
    text=True
)

points = []
last_time = None

def process_swipe():
    global points

    if len(points) < 2:
        points = []
        return

    start = points[0]
    end = points[-1]

    print(f"swipe → {start} → {end}")

    actions.append({
        "type": "swipe",
        "start": list(start),
        "end": list(end)
    })

    points = []

try:
    for line in process.stdout:

        if "ABS_MT_POSITION_X" in line:
            x = hex_to_dec(line.strip().split()[-1])

        elif "ABS_MT_POSITION_Y" in line:
            y = hex_to_dec(line.strip().split()[-1])

            points.append((x, y))
            last_time = time.time()

        if last_time and time.time() - last_time > 0.3:
            process_swipe()
            last_time = None

except KeyboardInterrupt:
    with open("swipe.json", "w") as f:
        json.dump(actions, f, indent=4)

    process.kill()