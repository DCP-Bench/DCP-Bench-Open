# Magic hexagon (CSPLib 023): place the numbers 1 to NUM_CELLS in the 19 cells
# A..S of a hexagon so that each of the 15 lines sums to MAGIC_SUM.
# LD lists the values of A, B, ..., S in that order.
#
# Encoding: a Boolean one-hot matrix x[c][v] (cell c holds value v), so that
# "all different" becomes an exactly-one per value, and each cell value is a
# linear expression of its one-hot row.

import cvc5.pythonic as cz


def build(instance):
    n = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]

    names = "A B C D E F G H I J K L M N O P Q R S".split()
    num_cells = len(names)
    values = list(range(1, n + 1))

    x = [[cz.Bool(f"x_{c}_{v}") for v in values] for c in range(num_cells)]
    cells = cz.Ints([f"val_{c}" for c in range(num_cells)])

    constraints = []

    # Each cell takes exactly one value from 1 to NUM_CELLS.
    for c in range(num_cells):
        constraints.append(cz.Or([x[c][k] for k in range(n)]))
        for k1 in range(n):
            for k2 in range(k1 + 1, n):
                constraints.append(cz.Or(cz.Not(x[c][k1]), cz.Not(x[c][k2])))
        constraints.append(cells[c] == cz.Sum([If_val(x[c][k], values[k]) for k in range(n)]))

    # All different: each value is used by exactly one cell.
    for k in range(n):
        constraints.append(cz.Or([x[c][k] for c in range(num_cells)]))
        for c1 in range(num_cells):
            for c2 in range(c1 + 1, num_cells):
                constraints.append(cz.Or(cz.Not(x[c1][k]), cz.Not(x[c2][k])))

    A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S = cells

    # The hexagon rows (3, 4, 5, 4 and 3 cells) each sum to the magic constant.
    rows = [
        [A, B, C],
        [D, E, F, G],
        [H, I, J, K, L],
        [M, N, O, P],
        [Q, R, S],
    ]
    # The lines running down and to the right each sum to the magic constant.
    down_right = [
        [A, E, J, O, S],
        [B, F, K, P],
        [C, G, L],
        [D, I, N, R],
        [H, M, Q],
    ]
    # The lines running down and to the left each sum to the magic constant.
    down_left = [
        [C, F, J, N, Q],
        [B, E, I, M],
        [A, D, H],
        [G, K, O, R],
        [L, P, S],
    ]
    # Each of the 15 lines (rows and diagonals) sums to the magic constant.
    for line in rows + down_right + down_left:
        constraints.append(cz.Sum(line) == magic)

    return constraints, {"LD": list(cells)}


def If_val(b, v):
    return cz.If(b, v, 0)
