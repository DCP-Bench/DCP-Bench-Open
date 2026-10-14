# Bus scheduling: minimise the number of buses so that every 4-hour slot of the
# day (cyclic over the day) has enough buses, where each bus works 8 successive
# hours (two slots).
from pyscipopt import Model, quicksum


def build(instance):
    demands = instance["demands"]
    n = len(demands)
    total = sum(demands)

    m = Model()

    # x[i] = number of buses that start their 8-hour shift in slot i.
    # Upper bound: the total demand, since no slot needs more buses than that.
    x = [m.addVar(name=f"x_{i}", vtype="I", lb=0, ub=total) for i in range(n)]

    # Each bus covers its start slot and the next slot, so slot i is covered by
    # the buses starting in slot i and in slot i-1 (wrapping around the day).
    for i in range(n):
        # the buses in each time slot must meet the demand of that slot
        m.addCons(x[i] + x[(i - 1) % n] >= demands[i])

    # minimise the total number of buses
    m.setObjective(quicksum(x), "minimize")

    return m, {"x": x}
