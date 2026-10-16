# Car sequencing: arrange the cars of each type in one sequence so that no station's capacity
# (at most at_most[o] of every per_slots[o] consecutive cars may require option o) is exceeded.
from pyscipopt import Model, quicksum


def build(instance):
    at_most = instance["at_most"]
    per_slots = instance["per_slots"]
    demand = instance["demand"]
    requires = instance["requires"]

    n_types = len(demand)
    n_opts = len(at_most)
    # the number of cars is the total demand, one position in the line per car
    n_cars = sum(demand)

    m = Model()
    # x[p, t] = 1 if the car in position p is of type t
    x = {(p, t): m.addVar(name=f"x_{p}_{t}", vtype="B") for p in range(n_cars) for t in range(n_types)}
    # y[p, o] = 1 if the car in position p requires option o
    y = {(p, o): m.addVar(name=f"y_{p}_{o}", vtype="B") for p in range(n_cars) for o in range(n_opts)}

    # each position in the assembly line holds exactly one car
    for p in range(n_cars):
        m.addCons(quicksum(x[p, t] for t in range(n_types)) == 1)

    # each car type is produced as many times as its demand
    for t in range(n_types):
        m.addCons(quicksum(x[p, t] for p in range(n_cars)) == demand[t])

    # a car requires an option exactly when its type requires that option
    for p in range(n_cars):
        for o in range(n_opts):
            m.addCons(y[p, o] == quicksum(requires[t][o] * x[p, t] for t in range(n_types) if requires[t][o]))

    # the stations cannot handle cars requiring their option bunched together:
    # in every window of per_slots[o] consecutive positions, at most at_most[o] cars require option o
    for o in range(n_opts):
        w = per_slots[o]
        for start in range(n_cars - w + 1):
            m.addCons(quicksum(y[p, o] for p in range(start, start + w)) <= at_most[o])

    # the output gives the car type at each position of the assembly line, numbered from 0
    sequence = [quicksum(t * x[p, t] for t in range(n_types)) for p in range(n_cars)]
    return m, {"sequence": sequence}
