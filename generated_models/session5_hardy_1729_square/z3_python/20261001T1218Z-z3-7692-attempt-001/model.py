# Hardy 1729 square: find four different numbers a, b, c, d between 1 and 100 such
# that a^2 + b^2 = c^2 + d^2.
import z3


def build(instance):
    del instance  # the puzzle states its own range

    range_min, range_max = 1, 100

    a, b, c, d = numbers = z3.Ints("a b c d")

    solver = z3.Solver()

    # Each number lies between 1 and 100.
    for v in numbers:
        solver.add(v >= range_min, v <= range_max)

    # The sum of the squares of the first two equals that of the other two.
    solver.add(a * a + b * b == c * c + d * d)

    # The four numbers are all different.
    solver.add(z3.Distinct(numbers))

    return solver, {"a": a, "b": b, "c": c, "d": d}
