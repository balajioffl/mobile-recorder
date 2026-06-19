import subprocess
import time
import json


DEVICE = "/dev/input/event4"
DISTANCE_THRESHOLD = 30
SWIPE_TIME_THRESHOLD = 0.3


touching = False
points = []
x = None
y = None
start_time = None


def hex_to_int(value):
    return int(value, 16)


def get_distance(p1, p2):
    return ((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2) ** 0.5


def classify_gesture(points, duration):
    if len(points) < 2:
        return "tap"

    distance = get_distance(points[0], points[-1])

    if distance < DISTANCE_THRESHOLD:
        return "tap"

    if duration < SWIPE_TIME_THRESHOLD:
        return "swipe"

    return "drag"


def save_drag_to_json(start, end, duration, points_count):
    new_data = {
        "type": "drag",
        "start": {"x": start[0], "y": start[1]},
        "end": {"x": end[0], "y": end[1]},
        "duration": round(duration, 3),
        "points_count": points_count
    }

    try:
        with open("drag.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(new_data)

    with open("drag.json", "w") as f:
        json.dump(data, f, indent=4)

    print("DRAG saved")

def handle_touch_start():
    global touching, points, x, y, start_time

    touching = True
    points = []
    x = None
    y = None
    start_time = time.time()

    print("\nTouch started")


def handle_touch_end():
    global touching

    end_time = time.time()
    duration = end_time - start_time

    gesture = classify_gesture(points, duration)

    print("Touch ended")
    print("Gesture:", gesture)

    if gesture == "drag" and len(points) >= 2:
        start = points[0]
        end = points[-1]

        save_drag_to_json(start, end, duration, len(points))

    touching = False


def handle_x(line):
    global x
    x = hex_to_int(line.split()[-1])


def handle_y(line):
    global y, points

    y = hex_to_int(line.split()[-1])

    if touching and x is not None:
        points.append((x, y))


def listen_touch_events():
    process = subprocess.Popen(
        f"adb exec-out getevent -lt {DEVICE}",
        shell=True,
        stdout=subprocess.PIPE,
        text=True
    )

    print("Listening...\n")

    for line in process.stdout:
        line = line.strip()

        if "BTN_TOUCH" in line and "DOWN" in line:
            handle_touch_start()

        elif "BTN_TOUCH" in line and "UP" in line:
            handle_touch_end()

        elif "ABS_MT_POSITION_X" in line:
            handle_x(line)

        elif "ABS_MT_POSITION_Y" in line:
            handle_y(line)


if __name__ == "__main__":
    listen_touch_events()