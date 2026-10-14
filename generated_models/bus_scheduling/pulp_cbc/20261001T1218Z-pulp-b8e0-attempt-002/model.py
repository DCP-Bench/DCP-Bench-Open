"""Bus scheduling: the day is split into 4-hour time slots (taken as a cycle, so
the last slot is followed by the first), and slot i needs demands[i] buses.
Each bus works 8 successive hours, that is two consecutive slots. Find how many
buses start work in each slot so that every slot's demand is met with the fewest
buses overall.
"""
import pulp


def build(instance):
    demands = instance["demands"]  # buses needed in each 4-hour slot
    slots = len(demands)

    problem = pulp.LpProblem("bus_scheduling", pulp.LpMinimize)

    # x[i] = number of buses that start working in slot i (declared output). The
    # reference bounds it by the total demand.
    x = [pulp.LpVariable(f"x_{i}", 0, sum(demands), cat="Integer") for i in range(slots)]

    # objective: minimise the total number of buses
    problem += pulp.lpSum(x)

    # slot (i + 1) is served by the buses that start in slot i (their second slot)
    # and in slot i + 1 (their first slot); together they meet its demand
    for i in range(slots):
        problem += x[i] + x[(i + 1) % slots] >= demands[(i + 1) % slots]

    return problem, {"x": x}
