# KenKen: fill an n x n grid with 1..n so that each row and column holds every
# digit once, and each cage of cells achieves its target. A cage of two cells
# reaches it by a sum, product, difference or quotient; a larger cage by its sum
# or its product. Digits may repeat inside a cage.
import z3


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # [target, [[row, column], ...]] with cells counted from 1

    solver = z3.Solver()

    # x[r][c] = the digit in cell (r, c)
    x = [[z3.Int(f"x_{r}_{c}") for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            solver.add(x[r][c] >= 1, x[r][c] <= n)

    # each row and each column holds different digits
    for r in range(n):
        solver.add(z3.Distinct(x[r]))
    for c in range(n):
        solver.add(z3.Distinct([x[r][c] for r in range(n)]))

    for target, cells in cages:
        cage = [x[r - 1][c - 1] for r, c in cells]
        if len(cage) == 2:
            a, b = cage
            # the cage reaches its target in at least one of these ways
            solver.add(z3.Or(
                a + b == target,  # sum
                a * b == target,  # product
                a * target == b,  # quotient: b divided by a is the target
                b * target == a,  # quotient the other way round
                a - b == target,  # difference
                b - a == target,  # difference the other way round
            ))
        else:
            product = cage[0]
            for cell in cage[1:]:
                product = product * cell
            # a larger cage adds up to the target or multiplies to it
            solver.add(z3.Or(z3.Sum(cage) == target, product == target))

    return solver, {"x": x}
