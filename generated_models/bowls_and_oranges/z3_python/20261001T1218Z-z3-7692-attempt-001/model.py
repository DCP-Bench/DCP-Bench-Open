# Bowls and oranges: put m oranges into n bowls in a line, at most one per bowl,
# so that no three oranges are evenly spaced.
import z3


def build(instance):
    n = instance["n"]  # number of bowls, numbered 1..n
    m = instance["m"]  # number of oranges

    # x[i] is the bowl holding the i-th orange (oranges listed in ascending order).
    x = [z3.Int(f"x_{i}") for i in range(m)]

    solver = z3.Solver()

    # Each orange sits in one of the bowls 1..n.
    for xi in x:
        solver.add(xi >= 1, xi <= n)

    # At most one orange per bowl, and the list is in ascending order (the
    # reference states both: all different and non-decreasing).
    solver.add(z3.Distinct(x))
    for i in range(1, m):
        solver.add(x[i - 1] <= x[i])

    # No three oranges A, B, C (in order) have the distance A-B equal to B-C.
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                solver.add(x[j] - x[i] != x[k] - x[j])

    return solver, {"x": x}
