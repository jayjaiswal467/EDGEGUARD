
import time

from controller import TrafficController, TrafficState
from serial_comm import SerialCommunicator


PORT = "COM3"
GREEN_DURATION = 5
YELLOW_DURATION = 2
ALL_RED_DURATION = 1


def duration_for_state(state):
    if state in (TrafficState.NS_GREEN, TrafficState.EW_GREEN):
        return GREEN_DURATION

    if state in (TrafficState.NS_YELLOW, TrafficState.EW_YELLOW):
        return YELLOW_DURATION

    return ALL_RED_DURATION


def main():
    controller = TrafficController()
    esp32 = SerialCommunicator(PORT)

    try:
        esp32.connect()
        time.sleep(2)  # Allow ESP32 to restart after serial opens

        esp32.start_heartbeat()

        # Establish a known starting state
        esp32.send_command("ALL_RED")
        print("[CONTROLLER] Starting in ALL_RED")
        time.sleep(ALL_RED_DURATION)

        # Temporary test priorities.
        # Next, we'll replace these with live vehicle counts.
        priorities = ["NS", "EW", "EQUAL", "NS", "EW"]

        for priority in priorities:
            next_state = controller.apply_priority(priority)

            esp32.send_command(next_state)
            print(
                f"[CONTROLLER] Priority={priority}, "
                f"State={next_state}"
            )

            time.sleep(duration_for_state(next_state))

        esp32.send_command("ALL_RED")
        print("[CONTROLLER] Test complete; ALL_RED commanded")

    except KeyboardInterrupt:
        print("\n[CONTROLLER] Stopped by user")

    except Exception as error:
        print(f"[CONTROLLER] Error: {error}")

    finally:
        # Stop heartbeat and close serial cleanly
        try:
            if esp32.serial_connection is not None:
                esp32.send_command("ALL_RED")
        except Exception:
            pass

        esp32.close()


if __name__ == "__main__":
    main()
