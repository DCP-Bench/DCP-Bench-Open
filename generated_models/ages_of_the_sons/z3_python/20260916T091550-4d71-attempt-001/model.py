import z3


def build(instance):
    """Ages of the sons: the product is 36, the sum is ambiguous, and there is
    a unique oldest.

    The puzzle states its own product, so it carries no instance data.  The
    second triple B is what makes the sum ambiguous: another factorisation of
    36 with the same sum and a different eldest.
    """
    del instance

    a1, a2, a3 = z3.Ints("A1 A2 A3")
    b1, b2, b3 = z3.Ints("B1 B2 B3")
    a_sum, b_sum = z3.Ints("AS BS")

    solver = z3.Solver()
    for value in (a1, a2, a3, b1, b2, b3):
        solver.add(value >= 0, value <= 36)
    solver.add(a_sum >= 0, a_sum <= 1000, b_sum >= 0, b_sum <= 1000)

    solver.add(a1 > a2, a2 >= a3, a1 * a2 * a3 == 36)
    solver.add(b1 >= b2, b2 >= b3, a1 != b1, b1 * b2 * b3 == 36)
    solver.add(a_sum == a1 + a2 + a3, b_sum == b1 + b2 + b3, a_sum == b_sum)

    return solver, {"A1": a1, "A2": a2, "A3": a3}
