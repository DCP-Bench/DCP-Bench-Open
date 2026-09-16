import z3


def build(instance):
    """Five brigands: 200 doubloons shared so that the reweighted shares also
    come to 200.

    The reweighting is 12A + 3B + C + D/2 + E/3; multiplying through by six
    clears both fractions, which is what the reference does.
    """
    del instance

    a, b, c, d, e = z3.Ints("A B C D E")
    solver = z3.Solver()
    for value in (a, b, c, d, e):
        solver.add(value >= 1, value <= 200)

    solver.add(a + b + c + d + e == 200)
    solver.add(6 * (a * 12 + b * 3 + c) + 3 * d + 2 * e == 6 * 200)

    return solver, {"A": a, "B": b, "C": c, "D": d, "E": e}
