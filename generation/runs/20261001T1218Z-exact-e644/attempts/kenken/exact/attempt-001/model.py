# KenKen: fill an n x n grid with the digits 1..n so that every row and every column holds each
# digit once, and the digits in each cage (a group of cells) reach the cage's number. A cage of
# two cells reaches it by sum, product, difference or quotient; a larger cage (or a single
# cell) by sum or product. Digits may repeat inside a cage.
from itertools import product

from exact import Exact


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # each cage is [result, [[row, column], ...]], cells numbered from 1
    digits = range(1, n + 1)

    solver = Exact()

    # holds[i][j][v-1] = 1 when cell (i, j) holds the digit v. Exact has no all-different
    # constraint, so rows and columns use these indicators.
    holds = [[[f"cell_{i}_{j}_holds_{v}" for v in digits] for j in range(n)] for i in range(n)]
    # x[i][j] is the digit in cell (i, j)
    x = [[f"x_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(x[i][j], 1, n)
            for name in holds[i][j]:
                solver.addVariable(name, 0, 1)
            # every cell holds exactly one digit, and x is that digit
            solver.addConstraint([(1, name) for name in holds[i][j]], True, 1, True, 1)
            solver.addConstraint([(v, holds[i][j][v - 1]) for v in digits] + [(-1, x[i][j])],
                                 True, 0, True, 0)

    for v in range(n):
        for k in range(n):
            # each row has every digit exactly once
            solver.addConstraint([(1, holds[k][j][v]) for j in range(n)], True, 1, True, 1)
            # each column has every digit exactly once
            solver.addConstraint([(1, holds[i][k][v]) for i in range(n)], True, 1, True, 1)

    # Cages. The arithmetic of a cage is not linear (products, differences in either direction,
    # quotients), so the digit combinations that reach the cage's number are listed and the cage
    # picks exactly one of them: combo[t] = 1 when the cage uses combination t, and a cell holds
    # digit v exactly when the chosen combination has v in that cell's place.
    for c, (result, segment) in enumerate(cages):
        cells = [(r - 1, col - 1) for r, col in segment]  # 0-based

        def reaches(values):
            if len(values) == 2:
                a, b = values
                return (a + b == result or a * b == result or a * result == b
                        or b * result == a or a - b == result or b - a == result)
            product_of_values = 1
            for value in values:
                product_of_values *= value
            return sum(values) == result or product_of_values == result

        combinations = [values for values in product(digits, repeat=len(cells)) if reaches(values)]
        if not combinations:
            # no digits can reach this cage's number: the puzzle has no solution
            solver.addVariable(f"cage_{c}_unreachable", 0, 0)
            solver.addConstraint([(1, f"cage_{c}_unreachable")], True, 1)
            continue
        combo = [f"cage_{c}_combination_{t}" for t in range(len(combinations))]
        for name in combo:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in combo], True, 1, True, 1)
        for place, (i, j) in enumerate(cells):
            for v in digits:
                supporting = [(1, combo[t]) for t, values in enumerate(combinations) if values[place] == v]
                solver.addConstraint(supporting + [(-1, holds[i][j][v - 1])], True, 0, True, 0)

    return solver, {"x": x}
