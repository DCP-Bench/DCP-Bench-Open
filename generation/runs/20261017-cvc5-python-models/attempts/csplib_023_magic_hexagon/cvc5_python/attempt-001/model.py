# Magic hexagon (CSPLib 023): place the numbers 1 to NUM_CELLS in the 19 cells
# A..S of a hexagon so that each of the 15 lines sums to MAGIC_SUM.
# LD lists the values of A, B, ..., S in that order.

import cvc5.pythonic as cz


def build(instance):
    n = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]

    names = "A B C D E F G H I J K L M N O P Q R S".split()
    cells = cz.Ints(names)
    A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S = cells

    constraints = []

    # Each cell takes a value from 1 to NUM_CELLS, and all values are different.
    for c in cells:
        constraints.append(c >= 1)
        constraints.append(c <= n)
    constraints.append(cz.Distinct(cells))

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

    return constraints, {"LD": cells}
