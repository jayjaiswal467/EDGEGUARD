class TrafficState:
    NS_GREEN = "NS_GREEN"
    NS_YELLOW = "NS_YELLOW"
    ALL_RED = "ALL_RED"
    EW_GREEN = "EW_GREEN"
    EW_YELLOW = "EW_YELLOW"


class TrafficController:

    def __init__(self):
        self.current_state = TrafficState.ALL_RED
        self.last_green_direction = None

    def get_state(self):
        return self.current_state

    def transition(self, next_state):
        allowed_transitions = {
            TrafficState.NS_GREEN: [
                TrafficState.NS_YELLOW
            ],

            TrafficState.NS_YELLOW: [
                TrafficState.ALL_RED
            ],

            TrafficState.ALL_RED: [
                TrafficState.NS_GREEN,
                TrafficState.EW_GREEN
            ],

            TrafficState.EW_GREEN: [
                TrafficState.EW_YELLOW
            ],

            TrafficState.EW_YELLOW: [
                TrafficState.ALL_RED
            ]
        }

        allowed = allowed_transitions.get(
            self.current_state, []
        )

        if next_state not in allowed:
            raise ValueError(
                f"Invalid transition: "
                f"{self.current_state} -> {next_state}"
            )

        self.current_state = next_state

        if next_state == TrafficState.NS_GREEN:
            self.last_green_direction = "NS"

        elif next_state == TrafficState.EW_GREEN:
            self.last_green_direction = "EW"

        return self.current_state

    def next_state(self, priority):
        if self.current_state == TrafficState.NS_GREEN:
            return TrafficState.NS_YELLOW

        if self.current_state == TrafficState.NS_YELLOW:
            return TrafficState.ALL_RED

        if self.current_state == TrafficState.EW_GREEN:
            return TrafficState.EW_YELLOW

        if self.current_state == TrafficState.EW_YELLOW:
            return TrafficState.ALL_RED

        if self.current_state == TrafficState.ALL_RED:

            if priority == "NS":
                return TrafficState.NS_GREEN

            if priority == "EW":
                return TrafficState.EW_GREEN

            if priority == "EQUAL":
                if self.last_green_direction == "NS":
                    return TrafficState.EW_GREEN
                else:
                    return TrafficState.NS_GREEN

        raise ValueError(
            f"Invalid priority: {priority}"
        )

    def apply_priority(self, priority):
        next_state = self.next_state(priority)
        return self.transition(next_state)


if __name__ == "__main__":

    controller = TrafficController()

    print("Initial state:", controller.get_state())

    # Valid transition
    controller.apply_priority("NS")
    print("Valid:", controller.get_state())

    # Invalid transition:
    # NS_GREEN -> EW_GREEN should NOT be allowed
    try:
        controller.transition(TrafficState.EW_GREEN)
        print("ERROR: Invalid transition was allowed!")

    except ValueError as e:
        print("PASS: Invalid transition rejected")
        print("Error:", e)