# KenKen: fill an n x n grid with the digits 1..n so that every row and column has each
# digit once, and every cage (a group of cells) achieves its target with +, -, x or /.
from functools import reduce

import cpmpy as cp


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # each cage is [target, [[row, col], ...]] with 1-based cells

    # x[i, j] = digit in the cell at row i, column j (0-based here)
    x = cp.intvar(1, n, shape=(n, n), name="x")

    model = cp.Model()

    # Each row contains each digit exactly once.
    model += [cp.AllDifferent(row) for row in x]

    # Each column contains each digit exactly once.
    model += [cp.AllDifferent(col) for col in x.T]

    # Each cage achieves its target with its operation. The operation is not given, so
    # the cage may use any operation that is valid for its size.
    for target, cells in cages:
        cell_vars = [x[r - 1, c - 1] for (r, c) in cells]
        if len(cells) == 2:
            # Two cells: sum, product, difference (either order) or exact quotient
            # (either order) of the two digits equals the target.
            a, b = cell_vars
            model += (
                (a + b == target)
                | (a * b == target)
                | (a - b == target)
                | (b - a == target)
                | (a * target == b)
                | (b * target == a)
            )
        else:
            # Three or more cells: the sum or the product of the digits equals the target
            # (subtraction and division are only defined for two cells).
            product = reduce(lambda p, q: p * q, cell_vars)
            model += (cp.sum(cell_vars) == target) | (product == target)

    return model, {"x": x}
