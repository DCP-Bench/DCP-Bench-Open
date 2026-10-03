"""Magic square: fill an n-by-n grid with the different integers 1..n^2 so that every row, every
column and both diagonals add up to the magic sum n(n^2 + 1)/2.

The model reports the square.
"""
from docplex.mp.model import Model

# The Community Edition refuses more than 1000 variables.
VARIABLE_LIMIT = 1000


def build(instance):
    n = instance["n"]  # size of the magic square
    magic_sum = n * (n * n + 1) // 2
    cells = [(i, j) for i in range(n) for j in range(n)]
    values = range(1, n * n + 1)
    parts = range(n)

    model = Model("magic_square")

    if n ** 4 <= VARIABLE_LIMIT - 100:
        # has[c, v] = 1 when cell c holds v: every cell holds one number and every number is
        # used once, so all numbers are different. n^4 binaries (625 at n = 5).
        has = {(c, v): model.binary_var(name=f"has_{c[0]}_{c[1]}_{v}") for c in cells for v in values}
        for c in cells:
            model.add_constraint(model.sum(has[c, v] for v in values) == 1)
        for v in values:
            model.add_constraint(model.sum(has[c, v] for c in cells) == 1)

        def number(i, j):
            return model.sum(v * has[(i, j), v] for v in values)
    else:
        # The one-hot table above would exceed the variable limit (1296 binaries at n = 6). Each
        # number is instead written as n * high + low + 1 with high and low in 0..n-1, each
        # chosen one-hot: 2 * n^3 binaries. Two cells are different when their (high, low)
        # pairs differ, a quadratic constraint over binaries; it is not convex, and CPLEX
        # accepts it only when told to search for a global optimum.
        model.parameters.optimalitytarget = 3
        high = {(c, a): model.binary_var(name=f"high_{c[0]}_{c[1]}_{a}") for c in cells for a in parts}
        low = {(c, b): model.binary_var(name=f"low_{c[0]}_{c[1]}_{b}") for c in cells for b in parts}
        for c in cells:
            model.add_constraint(model.sum(high[c, a] for a in parts) == 1)
            model.add_constraint(model.sum(low[c, b] for b in parts) == 1)

        # All numbers are different: no two cells share a (high, low) pair. With n^2 cells and
        # n^2 pairs, at most one cell per pair makes every pair used once.
        for a in parts:
            for b in parts:
                model.add_constraint(model.sum(high[c, a] * low[c, b] for c in cells) <= 1)

        # Implied by the above: every high part and every low part is used by exactly n cells.
        for a in parts:
            model.add_constraint(model.sum(high[c, a] for c in cells) == n)
        for b in parts:
            model.add_constraint(model.sum(low[c, b] for c in cells) == n)

        def number(i, j):
            return model.sum([n * a * high[(i, j), a] for a in parts]
                             + [b * low[(i, j), b] for b in parts] + [1])

    # The numbers in each row add up to the magic sum.
    for i in range(n):
        model.add_constraint(model.sum(number(i, j) for j in range(n)) == magic_sum)

    # The numbers in each column add up to the magic sum.
    for j in range(n):
        model.add_constraint(model.sum(number(i, j) for i in range(n)) == magic_sum)

    # The numbers on the main diagonal add up to the magic sum.
    model.add_constraint(model.sum(number(i, i) for i in range(n)) == magic_sum)

    # The numbers on the other diagonal add up to the magic sum.
    model.add_constraint(model.sum(number(i, n - 1 - i) for i in range(n)) == magic_sum)

    return model, {"square": [[number(i, j) for j in range(n)] for i in range(n)]}
