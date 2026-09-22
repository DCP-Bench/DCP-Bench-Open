# Maximise the value carried without exceeding the knapsack capacity.
from exact import Exact


def build(instance):
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]
    n = len(values)

    solver = Exact()
    x = [f"x{j}" for j in range(n)]
    for name in x:
        solver.addVariable(name, 0, 1)
    solver.addConstraint(list(zip(weights, x)), False, 0, True, capacity)
    return solver, {"x": x}, ("maximize", list(zip(values, x)))
