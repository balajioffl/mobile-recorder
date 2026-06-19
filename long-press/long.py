import subprocess
import time
import json

DEVICE = "/dev/input/event4"
LONG_PRESS_TIME = 0.6
MOVE_THRESHOLD = 20

touching = False
x = None
y = None
start_x = None
start_y = None
start_time = None


def hex_to_int(value):
    return int(value, 16)


def get_distance(x1, y1, x2, y2):
    return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5


def is_long_press(duration, distance):
    return duration >= LONG_PRESS_TIME and distance < MOVE_THRESHOLD


def save_long_press_to_json(start, duration):
    new_data = {
        "type": "long_press",
        "start": {"x": start[0], "y": start[1]},
        "duration": round(duration, 3)
    }

    try:
        with open("long.json", "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []

    except Exception as e:
        print("JSON read error:", e)
        data = []

    data.append(new_data)

    with open("long.json", "w") as f:
        json.dump(data, f, indent=4)

    print("LONG press saved:", new_data)


def handle_touch_start():
    global touching, start_time, start_x, start_y, x, y

    touching = True
    start_time = time.time()
    start_x = None
    start_y = None
    x = None
    y = None

    print("\n started")


def handle_touch_end():
    global touching

    if not touching:
        return

    duration = time.time() - start_time

    if start_x is not None and x is not None:
        distance = get_distance(start_x, start_y, x, y)
    else:
        distance = 0

    print("Duration:", round(duration, 3))
    print("Movement:", round(distance, 2))

    if is_long_press(duration, distance) and start_x is not None:
        save_long_press_to_json((start_x, start_y), duration)
    else:
        print("Not a long press")

    touching = False


def handle_x(line):
    global x
    x = hex_to_int(line.split()[-1])


def handle_y(line):
    global y, start_x, start_y, x

    y = hex_to_int(line.split()[-1])

    if touching and x is not None:
        if start_x is None:
            start_x = x
            start_y = y


def listen_touch_events():
    process = subprocess.Popen(
        f"adb exec-out getevent -lt {DEVICE}",
        shell=True,
        stdout=subprocess.PIPE,
        text=True
    )

    print("Listening for long press...\n")

    for line in process.stdout:
        line = line.strip()

        if "ABS_MT_TRACKING_ID" in line and "ffffffff" not in line:
            handle_touch_start()

        elif "ABS_MT_TRACKING_ID" in line and "ffffffff" in line:
            handle_touch_end()

        elif "ABS_MT_POSITION_X" in line:
            handle_x(line)

        elif "ABS_MT_POSITION_Y" in line:
            handle_y(line)


if __name__ == "__main__":
    listen_touch_events()