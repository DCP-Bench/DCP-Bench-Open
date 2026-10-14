# Pythagorean triplet (Project Euler 9): find natural numbers a, b, c with
# a^2 + b^2 = c^2 and a + b + c = 1000.
import z3


def build(instance):
    del instance  # the puzzle states its own sum

    total = 1000  # the triplet sums to 1000

    a, b, c = z3.Ints("a b c")

    solver = z3.Solver()

    # Natural numbers; none can exceed half the sum, since each is smaller than
    # the sum of the other two for a triangle.
    for v in (a, b, c):
        solver.add(v >= 1, v <= total // 2)

    # The three numbers add up to 1000.
    solver.add(a + b + c == total)

    # They form a Pythagorean triplet.
    solver.add(a * a + b * b == c * c)

    return solver, {"a": a, "b": b, "c": c}
