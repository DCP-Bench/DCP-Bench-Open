"""Magic hexagon (CSPLib 23): place the numbers 1..19 in a hexagon of 19 cells, each once,
so that each of the 15 lines (rows and both diagonal directions) sums to the magic constant.

The model reports the cells A..S row by row (LD).
"""
import pulp


def build(instance):
    num_cells = instance["NUM_CELLS"]
    magic_sum = instance["MAGIC_SUM"]

    # The 15 lines of the 3-4-5-4-3 hexagon, mirrored from the reference, with the cells
    # A..S numbered 0..18 row by row.
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s = range(19)
    lines = [
        # rows
        [a, b, c], [d, e, f, g], [h, i, j, k, l], [m, n, o, p], [q, r, s],
        # diagonals, top left to bottom right
        [a, d, h], [b, e, i, m], [c, f, j, n, q], [g, k, o, r], [l, p, s],
        # diagonals, top right to bottom left
        [c, g, l], [b, f, k, p], [a, e, j, o, s], [d, i, n, r], [h, m, q],
    ]
    cells = range(num_cells)
    values = range(1, num_cells + 1)

    problem = pulp.LpProblem("magic_hexagon", pulp.LpMinimize)  # satisfaction

    # holds[x][v] = 1 if cell x holds the number v
    holds = [[pulp.LpVariable(f"holds_{x}_{v}", cat="Binary") for v in values] for x in cells]
    LD = [pulp.lpSum(v * holds[x][v - 1] for v in values) for x in cells]

    # every cell holds one number, and all numbers from 1 to NUM_CELLS are used exactly once
    for x in cells:
        problem += pulp.lpSum(holds[x]) == 1
    for v in values:
        problem += pulp.lpSum(holds[x][v - 1] for x in cells) == 1

    # the sum of each of the 15 lines equals the magic constant
    for line in lines:
        problem += pulp.lpSum(LD[x] for x in line) == magic_sum

    return problem, {"LD": LD}
