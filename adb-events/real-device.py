import subprocess
import json


def hex_to_dec(val):
    return int(val, 16)


def start_adb():
    return subprocess.Popen(
        "adb shell getevent -lt",
        shell=True,
        stdout=subprocess.PIPE,
        text=True
    )


class TouchState:
    def __init__(self):
        self.x = None
        self.y = None
        self.touching = False
        self.last_point = None


def handle_touch_start(state):
    state.touching = True


def handle_touch_end(state, actions):
    state.touching = False

    if state.last_point:
        x, y = state.last_point

        print(f"tap → ({x}, {y})")

        actions.append({
            "type": "tap",
            "x": x,
            "y": y
        })


def handle_pointer(line, state, actions):

    if "ABS_MT_POSITION_X" in line:
        state.x = hex_to_dec(line.strip().split()[-1])

    elif "ABS_MT_POSITION_Y" in line:
        state.y = hex_to_dec(line.strip().split()[-1])

        if state.x is not None:
            x, y = state.x, state.y

            print(f"pointer → ({x}, {y})")

            actions.append({
                "type": "point",
                "x": x,
                "y": y
            })

            state.last_point = (x, y)
            state.x, state.y = None, None


def save_actions(actions, filename="actions.json"):
    print("\nSaving to file...")

    with open(filename, "w") as f:
        json.dump(actions, f, indent=4)


def run_recorder():
    actions = []
    state = TouchState()

    process = start_adb()

    print("Recording... \n")

    try:
        for line in process.stdout:

            if "BTN_TOUCH" in line and "DOWN" in line:
                handle_touch_start(state)

            elif "BTN_TOUCH" in line and "UP" in line:
                handle_touch_end(state, actions)

            elif state.touching:
                handle_pointer(line, state, actions)

    except KeyboardInterrupt:
        save_actions(actions)
        process.kill()


if __name__ == "__main__":
    run_recorder()