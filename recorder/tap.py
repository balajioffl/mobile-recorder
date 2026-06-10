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


def process_tap():
    global points

    if not points:
        return

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    movement = max(max(xs) - min(xs), max(ys) - min(ys))

    if movement < 30:
        x, y = points[-1]

        print(f"tap at ({x},{y})")

        actions.append({
            "type": "tap",
            "x": x,
            "y": y
        })

    points.clear()


try:
    for line in process.stdout:

        if "ABS_MT_POSITION_X" in line:
            x = hex_to_dec(line.strip().split()[-1])

        elif "ABS_MT_POSITION_Y" in line:
            y = hex_to_dec(line.strip().split()[-1])

            points.append((x, y))
            last_time = time.time()

        if last_time and time.time() - last_time > 0.25:
            process_tap()
            last_time = None

except KeyboardInterrupt:
    print("\nSaving taps...")

    with open("taps.json", "w") as f:
        json.dump(actions, f, indent=4)

    process.kill()