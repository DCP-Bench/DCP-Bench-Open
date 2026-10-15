# 0-1 knapsack: choose which items to put in the backpack to maximize their total value without exceeding the weight capacity.
from pyscipopt import Model, quicksum


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    m = Model()
    # x[i] = 1 if item i is taken into the backpack, 0 otherwise
    x = [m.addVar(name=f"x{i}", vtype="B") for i in range(n)]

    # the total weight of the taken items must not exceed the backpack's weight capacity
    m.addCons(quicksum(weights[i] * x[i] for i in range(n)) <= capacity)

    # the objective is the total value of the taken items
    m.setObjective(quicksum(values[i] * x[i] for i in range(n)), "maximize")

    return m, {"x": x}
