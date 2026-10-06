import time

from traffic_logic import get_traffic_decision


# Traffic light states
NS_GREEN = "NS_GREEN"
NS_YELLOW = "NS_YELLOW"
ALL_RED = "ALL_RED"
EW_GREEN = "EW_GREEN"
EW_YELLOW = "EW_YELLOW"


def show_state(state):
    print("\nCurrent State:", state)

    if state == NS_GREEN:
        print("North: GREEN")
        print("South: GREEN")
        print("East: RED")
        print("West: RED")

    elif state == NS_YELLOW:
        print("North: YELLOW")
        print("South: YELLOW")
        print("East: RED")
        print("West: RED")

    elif state == ALL_RED:
        print("North: RED")
        print("South: RED")
        print("East: RED")
        print("West: RED")

    elif state == EW_GREEN:
        print("North: RED")
        print("South: RED")
        print("East: GREEN")
        print("West: GREEN")

    elif state == EW_YELLOW:
        print("North: RED")
        print("South: RED")
        print("East: YELLOW")
        print("West: YELLOW")


def run_cycle(decision):

    if decision["priority"] == "NS":
        first_phase = NS_GREEN
        first_time = decision["ns_green"]

        second_phase = EW_GREEN
        second_time = decision["ew_green"]

    elif decision["priority"] == "EW":
        first_phase = EW_GREEN
        first_time = decision["ew_green"]

        second_phase = NS_GREEN
        second_time = decision["ns_green"]

    else:
        first_phase = NS_GREEN
        first_time = decision["ns_green"]

        second_phase = EW_GREEN
        second_time = decision["ew_green"]

    # First direction
    show_state(first_phase)
    print("Duration:", first_time, "seconds")
    time.sleep(2)  # Demo delay

    # Yellow transition
    if first_phase == NS_GREEN:
        show_state(NS_YELLOW)
    else:
        show_state(EW_YELLOW)

    print("Duration: 3 seconds")
    time.sleep(2)

    # Safety transition
    show_state(ALL_RED)
    print("Duration: 2 seconds")
    time.sleep(2)

    # Second direction
    show_state(second_phase)
    print("Duration:", second_time, "seconds")
    time.sleep(2)

    # Yellow transition
    if second_phase == NS_GREEN:
        show_state(NS_YELLOW)
    else:
        show_state(EW_YELLOW)

    print("Duration: 3 seconds")
    time.sleep(2)

    # Safety transition
    show_state(ALL_RED)
    print("Duration: 2 seconds")
    time.sleep(2)


# ---------------------------------------
# TEST TRAFFIC DATA
# ---------------------------------------

north = 8
south = 3
east = 15
west = 2


# Get traffic decision
decision = get_traffic_decision(
    north,
    south,
    east,
    west
)


print("================================")
print("      EDGEGUARD CONTROLLER")
print("================================")

print("\nTraffic:")
print("North:", north)
print("South:", south)
print("East:", east)
print("West:", west)

print("\nPriority:", decision["priority"])
print("NS green:", decision["ns_green"], "seconds")
print("EW green:", decision["ew_green"], "seconds")


# Run traffic cycle
run_cycle(decision)