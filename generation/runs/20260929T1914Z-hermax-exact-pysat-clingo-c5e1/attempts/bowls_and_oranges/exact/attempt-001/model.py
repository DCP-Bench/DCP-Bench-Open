# Bowls and oranges: put oranges in bowls placed in a line, at most one per bowl,
# so that no three oranges are at equal distances from each other.
from exact import Exact


def build(instance):
    bowls = instance["n"]
    oranges = instance["m"]

    solver = Exact()
    # in_bowl[i][p] = 1 when the i-th orange (in ascending order) is in bowl p + 1
    in_bowl = [[f"orange_{i}_in_{p + 1}" for p in range(bowls)] for i in range(oranges)]
    for i in range(oranges):
        for name in in_bowl[i]:
            solver.addVariable(name, 0, 1)
        # an orange is in exactly one bowl
        solver.addConstraint([(1, name) for name in in_bowl[i]], True, 1, True, 1)

    # x[i] = the bowl, 1 to n, of the i-th orange, oranges in ascending order; this
    # also puts every orange in a different bowl
    x = [f"x_{i}" for i in range(oranges)]
    for i in range(oranges):
        solver.addVariable(x[i], 1, bowls)
        solver.addConstraint([(p + 1, in_bowl[i][p]) for p in range(bowls)] + [(-1, x[i])], True, 0, True, 0)
    for i in range(oranges - 1):
        solver.addConstraint([(1, x[i + 1]), (-1, x[i])], True, 1)

    # No three oranges A, B, C with B in the middle: of the bowls p, p + d and p + 2d
    # at most two hold an orange.
    for p in range(1, bowls + 1):
        for d in range(1, (bowls - p) // 2 + 1):
            terms = [(1, in_bowl[i][q - 1]) for i in range(oranges) for q in (p, p + d, p + 2 * d)]
            solver.addConstraint(terms, False, 0, True, 2)

    return solver, {"x": x}
