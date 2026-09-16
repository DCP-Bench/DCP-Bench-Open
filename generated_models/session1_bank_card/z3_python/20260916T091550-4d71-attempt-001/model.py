import z3


def build(instance):
    """Bank card: a four-digit PIN abcd where cd is three times ab and da is
    twice bc.
    """
    del instance

    a, b, c, d = digits = z3.Ints("a b c d")
    solver = z3.Solver()
    for value in digits:
        solver.add(value >= 0, value <= 9)
    solver.add(z3.Distinct(digits))
    solver.add(10 * c + d == 3 * (10 * a + b))
    solver.add(10 * d + a == 2 * (10 * b + c))

    return solver, {"a": a, "b": b, "c": c, "d": d}
