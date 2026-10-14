"""Killer sudoku: fill an n-by-n grid with 1..n so that every row, column and 3-by-3 box holds
different numbers, and the numbers in each cage are different and add up to the cage's sum.

The model reports the filled grid.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["n"]              # size of the grid
    cages = instance["problem"]    # cages as [sum, [[row, col], ...]], rows and columns 1-based
    # The reference fixes the boxes at 3 by 3 cells (a problem constant, not instance data).
    box = 3

    rows = range(n)
    values = range(1, n + 1)

    model = Model("killer_sudoku")

    # has[r, c, v] is 1 when cell (r, c) holds the number v; every cell holds one number.
    has = {(r, c, v): model.binary_var(name=f"has_{r}_{c}_{v}") for r in rows for c in rows for v in values}
    for r in rows:
        for c in rows:
            model.add_constraint(model.sum(has[r, c, v] for v in values) == 1)

    # x[r][c] is the number in cell (r, c).
    x = [[model.sum(v * has[r, c, v] for v in values) for c in rows] for r in rows]

    # All rows and columns must hold different numbers: each number once per row and column.
    for v in values:
        for r in rows:
            model.add_constraint(model.sum(has[r, c, v] for c in rows) == 1)
        for c in rows:
            model.add_constraint(model.sum(has[r, c, v] for r in rows) == 1)

    # Every 3-by-3 box holds different numbers.
    for i in range(n // box):
        for j in range(n // box):
            cells = [(r, c) for r in range(i * box, i * box + box) for c in range(j * box, j * box + box)]
            for v in values:
                model.add_constraint(model.sum(has[r, c, v] for r, c in cells) <= 1)

    # The numbers in each cage add up to its sum and are all different.
    for total, segment in cages:
        cells = [(r - 1, c - 1) for r, c in segment]
        model.add_constraint(model.sum(x[r][c] for r, c in cells) == total)
        if len(cells) > 1:
            for v in values:
                model.add_constraint(model.sum(has[r, c, v] for r, c in cells) <= 1)

    return model, {"x": x}
