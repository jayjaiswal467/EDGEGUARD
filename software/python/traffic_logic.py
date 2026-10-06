MIN_GREEN = 10
MAX_GREEN = 60


def calculate_traffic(north, south, east, west):
    ns_total = north + south
    ew_total = east + west

    return ns_total, ew_total


def determine_priority(ns_total, ew_total):
    if ns_total > ew_total:
        return "NS"
    elif ew_total > ns_total:
        return "EW"
    else:
        return "EQUAL"


def calculate_green_time(traffic_count):
    green_time = 10 + (traffic_count * 2)

    green_time = min(MAX_GREEN, green_time)
    green_time = max(MIN_GREEN, green_time)

    return green_time


def get_traffic_decision(north, south, east, west):

    ns_total, ew_total = calculate_traffic(
        north, south, east, west
    )

    priority = determine_priority(
        ns_total, ew_total
    )

    ns_green = calculate_green_time(ns_total)
    ew_green = calculate_green_time(ew_total)

    return {
        "north": north,
        "south": south,
        "east": east,
        "west": west,
        "ns_total": ns_total,
        "ew_total": ew_total,
        "priority": priority,
        "ns_green": ns_green,
        "ew_green": ew_green
    }


# Test data
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

print("North:", decision["north"])
print("South:", decision["south"])
print("East:", decision["east"])
print("West:", decision["west"])

print("NS traffic:", decision["ns_total"])
print("EW traffic:", decision["ew_total"])

print("Priority:", decision["priority"])

print("NS green time:",
      decision["ns_green"], "seconds")

print("EW green time:",
      decision["ew_green"], "seconds")