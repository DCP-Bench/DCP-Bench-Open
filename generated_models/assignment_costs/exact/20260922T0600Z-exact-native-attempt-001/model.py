# Assign every task to a distinct person at least total cost.
from exact import Exact


def build(instance):
    cost = instance["cost"]
    rows, cols = len(cost), len(cost[0])

    solver = Exact()
    x = [[f"x{i}_{j}" for j in range(cols)] for i in range(rows)]
    for row in x:
        for name in row:
            solver.addVariable(name, 0, 1)
    for i in range(rows):
        solver.addConstraint([(1, name) for name in x[i]], True, 1, True, 1)
    for j in range(cols):
        solver.addConstraint([(1, x[i][j]) for i in range(rows)], False, 0, True, 1)

    terms = [(cost[i][j], x[i][j]) for i in range(rows) for j in range(cols)]
    return solver, {"x": x}, ("minimize", terms)
