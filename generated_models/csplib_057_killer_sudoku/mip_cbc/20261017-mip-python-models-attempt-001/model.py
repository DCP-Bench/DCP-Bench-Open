# Killer sudoku (csplib 057): fill the grid with numbers from 1 to n so that each row,
# column and nonet contains each number exactly once, and the sum of all numbers in a
# cage matches the total printed in its corner. No number appears more than once in a cage.
import math

import mip


def build(instance):
    n = instance["n"]
    block = math.isqrt(n)
    cages = instance["problem"]
    digits = range(1, n + 1)

    model = mip.Model(solver_name="CBC")
    model.verbose = 0
    model.threads = 1
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # p[r, c, v] = 1 when cell (r, c) holds the number v
    p = {}
    for r in range(n):
        for c in range(n):
            for v in digits:
                p[r, c, v] = model.add_var(f"p_{r}_{c}_{v}", var_type=mip.BINARY)

    # x[r][c] is the number in cell (r, c), an integer tied to its digit choice
    x = [[model.add_var(f"x_{r}_{c}", lb=1, ub=n, var_type=mip.INTEGER) for c in range(n)] for r in range(n)]

    # Each cell contains exactly one number.
    for r in range(n):
        for c in range(n):
            model.add_constr(mip.xsum(p[r, c, v] for v in digits) == 1)
            model.add_constr(x[r][c] == mip.xsum(v * p[r, c, v] for v in digits))

    # Each row, column and nonet contains each number exactly once.
    units = []
    for r in range(n):
        units.append([(r, c) for c in range(n)])
    for c in range(n):
        units.append([(r, c) for r in range(n)])
    for br in range(0, n, block):
        for bc in range(0, n, block):
            units.append([(br + i, bc + j) for i in range(block) for j in range(block)])
    for unit in units:
        for v in digits:
            model.add_constr(mip.xsum(p[r, c, v] for (r, c) in unit) == 1)

    # The sum of all numbers in a cage matches the total printed in its corner.
    # Cell coordinates in the data are 1-based.
    # No number appears more than once in a cage.
    for total, cells in cages:
        cell_list = [(r - 1, c - 1) for r, c in cells]
        model.add_constr(mip.xsum(x[r][c] for (r, c) in cell_list) == total)
        for v in digits:
            model.add_constr(mip.xsum(p[r, c, v] for (r, c) in cell_list) <= 1)

    grid = [[x[r][c] for c in range(n)] for r in range(n)]
    return model, {"x": grid}
