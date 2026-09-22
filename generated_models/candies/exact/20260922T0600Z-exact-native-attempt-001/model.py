# One candy per child at least, more than a lower-rated neighbour, fewest overall.
from exact import Exact


def build(instance):
    ratings = instance["ratings"]
    n = len(ratings)

    solver = Exact()
    x = [f"x{i}" for i in range(n)]
    for name in x:
        solver.addVariable(name, 1, n)
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            solver.addConstraint([(1, x[i - 1]), (-1, x[i])], True, 1)
        elif ratings[i - 1] < ratings[i]:
            solver.addConstraint([(1, x[i - 1]), (-1, x[i])], False, 0, True, -1)

    solver.addVariable("z", n, n * n)
    solver.addConstraint([(1, name) for name in x] + [(-1, "z")], True, 0, True, 0)
    return solver, {"x": x, "z": "z"}, ("minimize", [(1, "z")])
