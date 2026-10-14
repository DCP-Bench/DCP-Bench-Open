"""Magic square: fill an n-by-n grid with the different integers 1..n^2 so that every row, every
column and both diagonals add up to the magic sum n(n^2 + 1)/2.

The model reports the square.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]  # size of the magic square
    magic_sum = n * (n * n + 1) // 2
    cells = [(i, j) for i in range(n) for j in range(n)]
    parts = range(n)

    model = Model("magic_square")
    # The all-different rule below is a quadratic constraint over binaries, which is not
    # convex; CPLEX accepts it only when told to search for a global optimum.
    model.parameters.optimalitytarget = 3

    # A cell holding one of n^2 values as a one-hot choice needs n^4 binaries, 1296 at n = 6,
    # over the Community Edition's 1000-variable limit. Instead each value 1..n^2 is written
    # as n * high + low + 1 with high and low in 0..n-1, each chosen one-hot: 2 * n^3 binaries.
    high = {(c, a): model.binary_var(name=f"high_{c[0]}_{c[1]}_{a}") for c in cells for a in parts}
    low = {(c, b): model.binary_var(name=f"low_{c[0]}_{c[1]}_{b}") for c in cells for b in parts}
    for c in cells:
        model.add_constraint(model.sum(high[c, a] for a in parts) == 1)
        model.add_constraint(model.sum(low[c, b] for b in parts) == 1)

    # square[i][j] is the number in cell (i, j).
    square =[[model.sum(n * a * high[(i, j), a] for a in parts)
               + model.sum(b * low[(i, j), b] for b in parts) + 1
               for j in range(n)] for i in range(n)]

    # All numbers in the square are different: no two cells share the same (high, low) pair.
    # With n^2 cells and n^2 pairs, at most one cell per pair makes every pair used once.
    for a in parts:
        for b in parts:
            model.add_constraint(model.sum(high[c, a] * low[c, b] for c in cells) <= 1)

    # Implied by the above: every high part and every low part is used by exactly n cells.
    # Linear, so it gives the solver the counting the quadratic rule hides.
    for a in parts:
        model.add_constraint(model.sum(high[c, a] for c in cells) == n)
    for b in parts:
        model.add_constraint(model.sum(low[c, b] for c in cells) == n)

    # The numbers in each row add up to the magic sum.
    for i in range(n):
        model.add_constraint(model.sum(square[i][j] for j in range(n)) == magic_sum)

    # The numbers in each column add up to the magic sum.
    for j in range(n):
        model.add_constraint(model.sum(square[i][j] for i in range(n)) == magic_sum)

    # The numbers on the main diagonal add up to the magic sum.
    model.add_constraint(model.sum(square[i][i] for i in range(n)) == magic_sum)

    # The numbers on the other diagonal add up to the magic sum.
    model.add_constraint(model.sum(square[i][n - 1 - i] for i in range(n)) == magic_sum)

    return model, {"square": square}
