from traffic_logic import get_traffic_decision
from controller import TrafficController, TrafficState


class FakeSerial:
    def write(self, data):
        print(f"[FAKE ESP32] Received: {data.decode().strip()}")


class FakeSerialCommunicator:
    def __init__(self):
        self.serial_connection = FakeSerial()

    def send_command(self, command):
        valid_commands = {
            "NS_GREEN",
            "NS_YELLOW",
            "EW_GREEN",
            "EW_YELLOW",
            "ALL_RED"
        }

        if command not in valid_commands:
            raise ValueError(f"Invalid command: {command}")

        message = command + "\n"
        self.serial_connection.write(
            message.encode("utf-8")
        )

        print(f"[SERIAL] Sent: {command}")


def state_to_command(state):
    return state


def main():

    print("=" * 50)
    print("EDGEGUARD SOFTWARE INTEGRATION TEST")
    print("=" * 50)

    # STEP 1: Vehicle counts
    

    north = 8
    south = 3
    east = 15
    west = 2

    print("\n[INPUT]")
    print(f"North: {north}")
    print(f"South: {south}")
    print(f"East:  {east}")
    print(f"West:  {west}")

    # STEP 2: Traffic logic
    

    decision = get_traffic_decision(
        north,
        south,
        east,
        west
    )

    print("\n[TRAFFIC LOGIC]")
    print(f"NS Total: {decision['ns_total']}")
    print(f"EW Total: {decision['ew_total']}")
    print(f"Priority: {decision['priority']}")
    print(f"NS Green: {decision['ns_green']}s")
    print(f"EW Green: {decision['ew_green']}s")

    # STEP 3: Controller

    controller = TrafficController()

    print("\n[CONTROLLER]")

    state = controller.apply_priority(
        decision["priority"]
    )

    print(f"State: {state}")

    
    # STEP 4: Serial communication

    serial_comm = FakeSerialCommunicator()

    print("\n[SERIAL COMMUNICATION]")

    command = state_to_command(state)

    serial_comm.send_command(command)

    print("\n" + "=" * 50)
    print("INTEGRATION TEST PASSED")
    print("=" * 50)


if __name__ == "__main__":
    main()