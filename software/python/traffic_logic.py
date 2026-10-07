# ============================================================
# EDGEGUARD - Traffic Intelligence
# Phase 1
# ============================================================

MIN_GREEN = 10
MAX_GREEN = 60

# Maximum number of consecutive cycles one direction
# can receive priority before the other direction gets a chance.
MAX_CONSECUTIVE_PRIORITY = 3


def calculate_traffic(north, south, east, west):
    """
    Calculate total traffic for North-South and East-West.
    """

    ns_total = north + south
    ew_total = east + west

    return ns_total, ew_total


def determine_priority(ns_total, ew_total):
    """
    Determine which traffic axis gets priority.

    NS  -> North/South has more traffic
    EW  -> East/West has more traffic
    EQUAL -> both have equal traffic
    """

    if ns_total > ew_total:
        return "NS"

    elif ew_total > ns_total:
        return "EW"

    else:
        return "EQUAL"


def calculate_green_time(traffic_count):
    """
    Calculate adaptive green time.

    Formula:
        T = 10 + (traffic_count * 2)

    Bounded between:
        MIN_GREEN = 10 seconds
        MAX_GREEN = 60 seconds
    """

    if not isinstance(traffic_count, int):
        raise ValueError("Traffic count must be an integer")

    if traffic_count < 0:
        raise ValueError("Traffic count cannot be negative")

    green_time = 10 + (traffic_count * 2)

    green_time = min(MAX_GREEN, green_time)
    green_time = max(MIN_GREEN, green_time)

    return green_time


def apply_fairness(priority, ns_total, ew_total, consecutive_priority):
    """
    Prevent one direction from being starved indefinitely.

    If one direction has received priority for too many
    consecutive cycles, force the other direction to get
    an opportunity.

    This function only decides traffic priority.
    Safety transitions remain the responsibility of controller.py.
    """

    if consecutive_priority >= MAX_CONSECUTIVE_PRIORITY:

        if priority == "NS" and ew_total > 0:
            return "EW"

        if priority == "EW" and ns_total > 0:
            return "NS"

    return priority


def update_priority_counter(
    priority,
    previous_priority,
    consecutive_priority
):
    """
    Update the consecutive-priority counter.

    If the same direction receives priority again,
    increase the counter.

    If priority changes, reset the counter.
    """

    if priority == "EQUAL":
        return 0

    if priority == previous_priority:
        return consecutive_priority + 1

    return 1


def get_traffic_decision(
    north,
    south,
    east,
    west,
    previous_priority=None,
    consecutive_priority=0
):
    """
    Complete EDGEGUARD traffic decision.

    Input:
        N/S/E/W vehicle counts

    Output:
        Traffic totals
        Priority
        Adaptive green times
        Fairness counter
    """

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    counts = {
        "north": north,
        "south": south,
        "east": east,
        "west": west
    }

    for direction, count in counts.items():

        if not isinstance(count, int):
            raise ValueError(
                f"{direction} traffic count must be an integer"
            )

        if count < 0:
            raise ValueError(
                f"{direction} traffic count cannot be negative"
            )

    # --------------------------------------------------------
    # Calculate directional totals
    # --------------------------------------------------------

    ns_total, ew_total = calculate_traffic(
        north,
        south,
        east,
        west
    )

    # --------------------------------------------------------
    # Determine normal priority
    # --------------------------------------------------------

    normal_priority = determine_priority(
        ns_total,
        ew_total
    )

    # --------------------------------------------------------
    # Apply fairness / anti-starvation
    # --------------------------------------------------------

    priority = apply_fairness(
        normal_priority,
        ns_total,
        ew_total,
        consecutive_priority
    )

    # --------------------------------------------------------
    # Update consecutive priority counter
    # --------------------------------------------------------

    new_consecutive_priority = update_priority_counter(
        priority,
        previous_priority,
        consecutive_priority
    )

    # --------------------------------------------------------
    # Adaptive green times
    # --------------------------------------------------------

    ns_green = calculate_green_time(ns_total)
    ew_green = calculate_green_time(ew_total)

    # --------------------------------------------------------
    # Return complete decision
    # --------------------------------------------------------

    return {
        "north": north,
        "south": south,
        "east": east,
        "west": west,

        "ns_total": ns_total,
        "ew_total": ew_total,

        "normal_priority": normal_priority,
        "priority": priority,

        "ns_green": ns_green,
        "ew_green": ew_green,

        "consecutive_priority": new_consecutive_priority
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    north = 8
    south = 3
    east = 15
    west = 2

    decision = get_traffic_decision(
        north,
        south,
        east,
        west
    )

    print("========================================")
    print("       EDGEGUARD TRAFFIC DECISION")
    print("========================================")

    print("North:", decision["north"])
    print("South:", decision["south"])
    print("East:", decision["east"])
    print("West:", decision["west"])

    print("----------------------------------------")

    print("NS traffic:", decision["ns_total"])
    print("EW traffic:", decision["ew_total"])

    print("----------------------------------------")

    print("Normal priority:",
          decision["normal_priority"])

    print("Final priority:",
          decision["priority"])

    print("----------------------------------------")

    print("NS green time:",
          decision["ns_green"], "seconds")

    print("EW green time:",
          decision["ew_green"], "seconds")

    print("----------------------------------------")

    print("Consecutive priority:",
          decision["consecutive_priority"])

    print("========================================")